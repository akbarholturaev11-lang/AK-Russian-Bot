from datetime import datetime, timezone, timedelta
from typing import Optional

from app.repositories.bot_feedback_repo import BotFeedbackRepository
from app.repositories.user_repo import UserRepository
from app.services.ai_usage_budget_service import AIUsageBudgetService
from app.services.portfolio_service import PortfolioService


PLAN_DURATIONS = {
    "10_days": 10,
    "1_month": 30,
}


class SubscriptionService:
    def __init__(self, session):
        self.session = session
        self.user_repo = UserRepository(session)
        self.feedback_repo = BotFeedbackRepository(session)

    async def activate_plan(
        self,
        telegram_id: int,
        plan_type: str,
        discount_source: Optional[str] = None,
        payment=None,
    ) -> bool:
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            return False

        duration_days = PLAN_DURATIONS.get(plan_type)
        if not duration_days:
            return False

        now = datetime.now(timezone.utc)

        user.status = "active"
        user.payment_status = "approved"
        user.start_date = now
        user.end_date = now + timedelta(days=duration_days)
        user.selected_plan_type = None
        user.expiry_reminder_sent_at = None

        if discount_source == "referral" and user.discount_eligible and not user.discount_used:
            user.discount_used = True
            user.discount_eligible = False

        if discount_source == "feedback_price_offer":
            await self.feedback_repo.mark_latest_price_offer_used(telegram_id)

        if payment is not None:
            await AIUsageBudgetService(self.session).create_for_payment(
                payment=payment,
                starts_at=user.start_date,
                ends_at=user.end_date,
            )
            await PortfolioService(self.session).record_subscription_profit(payment)

        await self.session.flush()
        return True
