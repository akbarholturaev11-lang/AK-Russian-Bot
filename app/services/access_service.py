from datetime import datetime, timedelta, timezone
from typing import Tuple

from sqlalchemy import select

from app.db.models.user import User
from app.repositories.user_repo import UserRepository
from app.repositories.message_repo import MessageRepository
from app.repositories.payment_repo import PaymentRepository
from app.services.ai_usage_budget_service import AIUsageBudgetService

class AccessService:
    def __init__(self, session):
        self.session = session
        self.user_repo = UserRepository(session)
        self.message_repo = MessageRepository(session)
        self.payment_repo = PaymentRepository(session)

    def _as_utc(self, dt: datetime) -> datetime:
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    def _is_date_expired(self, dt) -> bool:
        if not dt:
            return False
        now = datetime.now(timezone.utc)
        if isinstance(dt, datetime):
            return self._as_utc(dt) <= now
        return dt < now.date()

    async def _downgrade_expired_user(self, user) -> None:
        user.status = "trial"
        user.end_date = None
        await self.session.flush()

    def _is_paid_user(self, user) -> bool:
        return user.payment_status == "approved"

    async def _can_use_daily_image_limit(self, user) -> Tuple[bool, str]:
        now = datetime.now(timezone.utc)

        if not user.last_limit_reset_at:
            user.last_limit_reset_at = now
            user.questions_used = 0
        elif now - user.last_limit_reset_at >= timedelta(days=1):
            user.last_limit_reset_at = now
            user.questions_used = 0

        today_image_count = await self.message_repo.count_user_messages_today(
            user_id=user.id,
            content_type="image",
        )
        if today_image_count >= 2:
            return False, "access_daily_image_limit_reached"

        return True, ""

    async def downgrade_expired_active_users(self) -> int:
        result = await self.session.execute(
            select(User).where(
                User.status == "active",
                User.end_date.is_not(None),
            )
        )
        users = list(result.scalars().all())
        changed = 0

        for user in users:
            if not self._is_date_expired(user.end_date):
                continue
            await self._downgrade_expired_user(user)
            changed += 1

        if changed:
            await self.session.commit()

        return changed

    async def can_use_text_ai(self, telegram_id: int) -> Tuple[bool, str]:
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            return False, "access_start_first"

        if user.status == "blocked":
            return False, "access_blocked"

        if user.status != "active":
            has_pending_payment = await self.payment_repo.has_pending_by_user(telegram_id)
            if has_pending_payment:
                return False, "access_payment_pending_review"

        if user.status == "active":
            if self._is_date_expired(user.end_date):
                await self._downgrade_expired_user(user)
                # falls through to trial logic below
            else:
                budget_access = await AIUsageBudgetService(self.session).can_use_ai(telegram_id)
                if not budget_access.allowed:
                    return False, budget_access.message_key
                return True, ""

        if user.status == "expired":
            await self._downgrade_expired_user(user)
            # falls through to trial logic below

        if user.status == "trial":
            now = datetime.now(timezone.utc)

            if user.last_limit_reset_at is None or now - user.last_limit_reset_at >= timedelta(days=1):
                user.questions_used = 0
                user.bonus_questions_used = 0
                user.last_limit_reset_at = now
                await self.user_repo.session.commit()

            if user.questions_used >= user.question_limit:
                bonus_balance = self.user_repo.get_bonus_balance(user)
                if bonus_balance <= 0:
                    return False, "access_daily_limit_reached"

            return True, ""

        return False, "access_start_first"

    async def can_use_image_ai(self, telegram_id: int) -> Tuple[bool, str]:
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            return False, "access_start_first"

        if user.status == "blocked":
            return False, "access_blocked"

        if user.status != "active":
            has_pending_payment = await self.payment_repo.has_pending_by_user(telegram_id)
            if has_pending_payment:
                return False, "access_payment_pending_review"

        if user.status == "active":
            if self._is_date_expired(user.end_date):
                await self._downgrade_expired_user(user)
                # falls through to trial logic below
            else:
                if not self._is_paid_user(user):
                    return await self._can_use_daily_image_limit(user)

                budget_access = await AIUsageBudgetService(self.session).can_use_ai(telegram_id)
                if not budget_access.allowed:
                    return False, budget_access.message_key
                return True, ""

        if user.status == "expired":
            await self._downgrade_expired_user(user)
            # falls through to trial logic below

        if user.status == "trial":
            return await self._can_use_daily_image_limit(user)

        return False, "access_start_first"

    async def consume_one_question(self, telegram_id: int) -> None:
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            return

        if user.status == "trial":

            now = datetime.now(timezone.utc)

            if not user.last_limit_reset_at:
                user.last_limit_reset_at = now
                user.questions_used = 0
            elif now - user.last_limit_reset_at >= timedelta(days=1):
                user.last_limit_reset_at = now
                user.questions_used = 0

            if user.questions_used >= user.question_limit:
                bonus = self.user_repo.get_bonus_balance(user)
                if bonus > 0:
                    await self.user_repo.consume_bonus_question(user)
                else:
                    return
 
        user.questions_used += 1
        await self.session.flush()
