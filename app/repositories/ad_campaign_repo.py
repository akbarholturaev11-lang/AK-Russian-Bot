from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.ad_campaign import AdCampaign, AdCampaignDelivery


def encode_languages(languages: Optional[list[str]]) -> Optional[str]:
    if not languages:
        return None
    clean = [item for item in languages if item in {"uz", "ru", "tj"}]
    return ",".join(sorted(set(clean))) or None


def decode_languages(value: Optional[str]) -> list[str]:
    if not value:
        return []
    return [item for item in value.split(",") if item in {"uz", "ru", "tj"}]


class AdCampaignRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        *,
        title: str,
        message_text: Optional[str],
        content_type: str,
        media_file_id: Optional[str],
        starts_at: datetime,
        ends_at: datetime,
        send_count_total: int,
        target_languages: Optional[list[str]] = None,
        include_active_subscribers: bool = False,
        created_by_telegram_id: Optional[int] = None,
    ) -> AdCampaign:
        campaign = AdCampaign(
            title=title,
            message_text=message_text,
            content_type=content_type,
            media_file_id=media_file_id,
            starts_at=starts_at,
            ends_at=ends_at,
            next_send_at=starts_at,
            send_count_total=send_count_total,
            target_languages=encode_languages(target_languages),
            include_active_subscribers=include_active_subscribers,
            created_by_telegram_id=created_by_telegram_id,
        )
        self.session.add(campaign)
        await self.session.flush()
        return campaign

    async def get_by_id(self, campaign_id: int) -> Optional[AdCampaign]:
        result = await self.session.execute(
            select(AdCampaign).where(AdCampaign.id == campaign_id)
        )
        return result.scalar_one_or_none()

    async def list_recent(self, limit: int = 10) -> list[AdCampaign]:
        result = await self.session.execute(
            select(AdCampaign)
            .order_by(AdCampaign.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_due(self, now: Optional[datetime] = None) -> list[AdCampaign]:
        now = now or datetime.now(timezone.utc)
        result = await self.session.execute(
            select(AdCampaign)
            .where(AdCampaign.is_active.is_(True))
            .where(AdCampaign.next_send_at.isnot(None))
            .where(AdCampaign.next_send_at <= now)
            .where(AdCampaign.starts_at <= now)
            .where(AdCampaign.ends_at >= now)
            .where(AdCampaign.rounds_sent < AdCampaign.send_count_total)
            .order_by(AdCampaign.next_send_at.asc(), AdCampaign.id.asc())
        )
        return list(result.scalars().all())

    async def deactivate_expired(self, now: Optional[datetime] = None) -> int:
        now = now or datetime.now(timezone.utc)
        result = await self.session.execute(
            select(AdCampaign)
            .where(AdCampaign.is_active.is_(True))
            .where(
                or_(
                    AdCampaign.ends_at < now,
                    AdCampaign.rounds_sent >= AdCampaign.send_count_total,
                )
            )
        )
        campaigns = list(result.scalars().all())
        for campaign in campaigns:
            campaign.is_active = False
            campaign.next_send_at = None
        if campaigns:
            await self.session.flush()
        return len(campaigns)

    async def list_delivered_user_ids(self, campaign_id: int, round_no: int) -> set[int]:
        result = await self.session.execute(
            select(AdCampaignDelivery.user_telegram_id)
            .where(AdCampaignDelivery.campaign_id == campaign_id)
            .where(AdCampaignDelivery.round_no == round_no)
        )
        return {int(item) for item in result.scalars().all()}

    async def create_delivery(
        self,
        *,
        campaign_id: int,
        user_telegram_id: int,
        round_no: int,
        status: str,
        error: Optional[str] = None,
    ) -> AdCampaignDelivery:
        delivery = AdCampaignDelivery(
            campaign_id=campaign_id,
            user_telegram_id=user_telegram_id,
            round_no=round_no,
            status=status,
            error=(error or "")[:300] or None,
        )
        self.session.add(delivery)
        await self.session.flush()
        return delivery

    async def count_deliveries(self, campaign_id: int, status: Optional[str] = None) -> int:
        query = select(func.count()).select_from(AdCampaignDelivery).where(
            AdCampaignDelivery.campaign_id == campaign_id
        )
        if status:
            query = query.where(AdCampaignDelivery.status == status)
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def mark_round_finished(self, campaign: AdCampaign, now: Optional[datetime] = None) -> None:
        now = now or datetime.now(timezone.utc)
        campaign.rounds_sent += 1

        if campaign.rounds_sent >= campaign.send_count_total:
            campaign.next_send_at = None
            campaign.is_active = False
            await self.session.flush()
            return

        campaign.next_send_at = self._next_send_time(campaign)
        if campaign.next_send_at is None or campaign.next_send_at > campaign.ends_at:
            campaign.next_send_at = None
            campaign.is_active = False
        elif campaign.next_send_at < now:
            campaign.next_send_at = now + timedelta(minutes=1)
        await self.session.flush()

    async def deactivate(self, campaign: AdCampaign) -> None:
        campaign.is_active = False
        campaign.next_send_at = None
        await self.session.flush()

    def _next_send_time(self, campaign: AdCampaign) -> Optional[datetime]:
        if campaign.send_count_total <= 1:
            return None
        duration_seconds = max(int((campaign.ends_at - campaign.starts_at).total_seconds()), 0)
        if duration_seconds <= 0:
            return None
        step_seconds = duration_seconds / max(campaign.send_count_total, 1)
        return campaign.starts_at + timedelta(seconds=int(step_seconds * campaign.rounds_sent))
