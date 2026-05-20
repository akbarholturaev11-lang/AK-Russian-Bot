from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from app.db.models.discount_campaign import DiscountCampaign
from app.repositories.bot_feedback_repo import BotFeedbackRepository
from app.repositories.discount_campaign_repo import DiscountCampaignRepository


@dataclass
class DiscountChoice:
    source: str = "none"
    percent: int = 0
    campaign_id: Optional[int] = None
    title: Optional[str] = None
    title_tj: Optional[str] = None
    title_ru: Optional[str] = None
    title_uz: Optional[str] = None
    reason: Optional[str] = None
    reason_tj: Optional[str] = None
    reason_ru: Optional[str] = None
    reason_uz: Optional[str] = None
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    plan_type: Optional[str] = None
    payment_method: Optional[str] = None
    quota_total: Optional[int] = None
    repeat_interval_days: Optional[int] = None
    details: Optional[str] = None


class DiscountService:
    def __init__(self, session):
        self.session = session
        self.repo = DiscountCampaignRepository(session)
        self.feedback_repo = BotFeedbackRepository(session)

    async def get_best_discount(
        self,
        *,
        user,
        plan_type: str,
        payment_method: Optional[str],
        include_admin_campaigns: bool = False,
    ) -> DiscountChoice:
        choices: list[DiscountChoice] = []

        if user.discount_eligible and not user.discount_used:
            choices.append(
                DiscountChoice(
                    source="referral",
                    percent=20,
                    title="Referral 3/3",
                    details="3 ta do'st taklif qilgani uchun referral chegirma.",
                )
            )

        if include_admin_campaigns:
            now = datetime.now(timezone.utc)
            for campaign in await self.repo.list_current(now):
                if not self._matches_campaign(campaign, user, plan_type, payment_method):
                    continue
                choice = await self._campaign_choice(campaign, user, now)
                if choice:
                    choices.append(choice)

        if not choices:
            return DiscountChoice()

        return max(
            choices,
            key=lambda item: (item.percent, 1 if item.source == "admin_campaign" else 0),
        )

    async def get_best_admin_discount(
        self,
        *,
        user,
        plan_type: str,
        payment_method: Optional[str],
    ) -> DiscountChoice:
        choices: list[DiscountChoice] = []
        now = datetime.now(timezone.utc)

        for campaign in await self.repo.list_current(now):
            if not self._matches_campaign(campaign, user, plan_type, payment_method):
                continue
            choice = await self._campaign_choice(campaign, user, now)
            if choice:
                choices.append(choice)

        if not choices:
            return DiscountChoice()

        return max(choices, key=lambda item: item.percent)

    async def get_campaign_discount(
        self,
        *,
        campaign_id: int,
        user,
        plan_type: str,
        payment_method: Optional[str],
    ) -> DiscountChoice:
        campaign = await self.repo.get_by_id(campaign_id)
        now = datetime.now(timezone.utc)

        if not campaign or not campaign.is_active:
            return DiscountChoice()
        if campaign.starts_at > now or campaign.ends_at <= now:
            return DiscountChoice()
        if not self._matches_campaign(campaign, user, plan_type, payment_method):
            return DiscountChoice()

        choice = await self._campaign_choice(campaign, user, now)
        return choice or DiscountChoice()

    async def get_feedback_price_discount(
        self,
        *,
        user,
        feedback_id: Optional[int] = None,
    ) -> DiscountChoice:
        if feedback_id is not None:
            feedback = await self.feedback_repo.get_available_price_offer(
                feedback_id=feedback_id,
                telegram_id=user.telegram_id,
            )
        else:
            feedback = await self.feedback_repo.get_latest_available_price_offer(user.telegram_id)

        if not feedback:
            return DiscountChoice()

        return DiscountChoice(
            source="feedback_price_offer",
            percent=20,
            title="Feedback 20%",
            details=f"Bot feedback #{feedback.id}: user obuna narxini qimmat deb belgilagan.",
        )

    def _matches_campaign(
        self,
        campaign: DiscountCampaign,
        user,
        plan_type: str,
        payment_method: Optional[str],
    ) -> bool:
        if campaign.target_telegram_id and campaign.target_telegram_id != user.telegram_id:
            return False

        checks = [
            (campaign.audience_status, getattr(user, "status", None)),
            (campaign.audience_language, getattr(user, "language", None)),
            (campaign.audience_level, getattr(user, "level", None)),
            (campaign.payment_method, payment_method),
            (campaign.plan_type, plan_type),
        ]
        return all(expected is None or expected == actual for expected, actual in checks)

    async def _campaign_choice(
        self,
        campaign: DiscountCampaign,
        user,
        now: datetime,
    ) -> Optional[DiscountChoice]:
        last_usage = await self.repo.get_user_last_usage(campaign.id, user.telegram_id)
        if campaign.repeat_interval_days:
            if last_usage and last_usage.submitted_at:
                next_allowed = last_usage.submitted_at.timestamp() + campaign.repeat_interval_days * 86400
                if now.timestamp() < next_allowed:
                    return None
            usage_rule = f"har {campaign.repeat_interval_days} kunda qayta olish mumkin"
        else:
            if last_usage:
                return None
            usage_rule = "bir userga 1 marta"

        used = await self.repo.count_used(
            campaign.id,
            now=now,
            exclude_user_telegram_id=user.telegram_id,
        )
        if campaign.quota_total and used >= campaign.quota_total:
            return None

        quota_text = "limitsiz"
        if campaign.quota_total:
            quota_text = f"{used + 1}/{campaign.quota_total}"

        details = (
            f"Admin kampaniya #{campaign.id}: {campaign.title}; "
            f"limit: {quota_text}; qoida: {usage_rule}; "
            f"amal qiladi: {campaign.starts_at:%Y-%m-%d %H:%M} - {campaign.ends_at:%Y-%m-%d %H:%M} UTC."
        )
        return DiscountChoice(
            source="admin_campaign",
            percent=campaign.percent,
            campaign_id=campaign.id,
            title=campaign.title,
            title_tj=campaign.title_tj,
            title_ru=campaign.title_ru,
            title_uz=campaign.title_uz,
            reason=campaign.reason,
            reason_tj=campaign.reason_tj,
            reason_ru=campaign.reason_ru,
            reason_uz=campaign.reason_uz,
            starts_at=campaign.starts_at,
            ends_at=campaign.ends_at,
            plan_type=campaign.plan_type,
            payment_method=campaign.payment_method,
            quota_total=campaign.quota_total,
            repeat_interval_days=campaign.repeat_interval_days,
            details=details,
        )
