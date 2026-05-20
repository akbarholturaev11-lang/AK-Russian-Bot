from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.discount_campaign import DiscountCampaign
from app.db.models.payment import Payment


class DiscountCampaignRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        *,
        title: str,
        title_tj: Optional[str] = None,
        title_ru: Optional[str] = None,
        title_uz: Optional[str] = None,
        reason: Optional[str] = None,
        reason_tj: Optional[str] = None,
        reason_ru: Optional[str] = None,
        reason_uz: Optional[str] = None,
        percent: int,
        starts_at: datetime,
        ends_at: datetime,
        audience_status: Optional[str] = None,
        audience_language: Optional[str] = None,
        audience_level: Optional[str] = None,
        target_telegram_id: Optional[int] = None,
        payment_method: Optional[str] = None,
        plan_type: Optional[str] = None,
        quota_total: Optional[int] = None,
        repeat_interval_days: Optional[int] = None,
        created_by_telegram_id: Optional[int] = None,
    ) -> DiscountCampaign:
        campaign = DiscountCampaign(
            title=title,
            title_tj=title_tj,
            title_ru=title_ru,
            title_uz=title_uz,
            reason=reason,
            reason_tj=reason_tj,
            reason_ru=reason_ru,
            reason_uz=reason_uz,
            percent=percent,
            starts_at=starts_at,
            ends_at=ends_at,
            audience_status=audience_status,
            audience_language=audience_language,
            audience_level=audience_level,
            target_telegram_id=target_telegram_id,
            payment_method=payment_method,
            plan_type=plan_type,
            quota_total=quota_total,
            repeat_interval_days=repeat_interval_days,
            created_by_telegram_id=created_by_telegram_id,
        )
        self.session.add(campaign)
        await self.session.flush()
        return campaign

    async def get_by_id(self, campaign_id: int) -> Optional[DiscountCampaign]:
        result = await self.session.execute(
            select(DiscountCampaign).where(DiscountCampaign.id == campaign_id)
        )
        return result.scalar_one_or_none()

    async def list_recent(self, limit: int = 10) -> list[DiscountCampaign]:
        result = await self.session.execute(
            select(DiscountCampaign)
            .order_by(DiscountCampaign.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_current(self, now: Optional[datetime] = None) -> list[DiscountCampaign]:
        now = now or datetime.now(timezone.utc)
        result = await self.session.execute(
            select(DiscountCampaign)
            .where(DiscountCampaign.is_active.is_(True))
            .where(DiscountCampaign.starts_at <= now)
            .where(DiscountCampaign.ends_at > now)
            .order_by(DiscountCampaign.percent.desc(), DiscountCampaign.created_at.desc())
        )
        return list(result.scalars().all())

    async def deactivate(self, campaign: DiscountCampaign) -> None:
        campaign.is_active = False
        await self.session.flush()

    async def count_used(
        self,
        campaign_id: int,
        *,
        now: Optional[datetime] = None,
        exclude_user_telegram_id: Optional[int] = None,
    ) -> int:
        now = now or datetime.now(timezone.utc)
        fresh_draft_after = now - timedelta(minutes=30)
        query = select(func.count()).select_from(Payment).where(
            Payment.discount_campaign_id == campaign_id,
            or_(
                Payment.payment_status.in_(("pending", "approved")),
                and_(
                    Payment.payment_status == "draft",
                    Payment.submitted_at >= fresh_draft_after,
                ),
            ),
        )
        if exclude_user_telegram_id:
            query = query.where(Payment.user_telegram_id != exclude_user_telegram_id)
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_user_last_usage(
        self,
        campaign_id: int,
        user_telegram_id: int,
    ) -> Optional[Payment]:
        result = await self.session.execute(
            select(Payment)
            .where(Payment.discount_campaign_id == campaign_id)
            .where(Payment.user_telegram_id == user_telegram_id)
            .where(Payment.payment_status.in_(("pending", "approved")))
            .order_by(Payment.submitted_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
