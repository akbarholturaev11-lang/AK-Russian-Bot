from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.bot_feedback import BotFeedback
from app.db.models.user import User


class BotFeedbackRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, feedback_id: int) -> Optional[BotFeedback]:
        result = await self.session.execute(
            select(BotFeedback).where(BotFeedback.id == feedback_id)
        )
        return result.scalar_one_or_none()

    async def get_latest_pending_by_user(self, user_id: int) -> Optional[BotFeedback]:
        result = await self.session.execute(
            select(BotFeedback)
            .where(BotFeedback.user_id == user_id)
            .where(BotFeedback.status == "pending")
            .order_by(BotFeedback.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def has_completed_since(self, user_id: int, since: datetime) -> bool:
        result = await self.session.execute(
            select(BotFeedback.id)
            .where(BotFeedback.user_id == user_id)
            .where(BotFeedback.status == "completed")
            .where(BotFeedback.completed_at >= since)
            .limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def create_pending(self, user: User) -> BotFeedback:
        now = datetime.now(timezone.utc)
        feedback = BotFeedback(
            user_id=user.id,
            telegram_id=user.telegram_id,
            language=user.language or "ru",
            status="pending",
            created_at=now,
            updated_at=now,
        )
        self.session.add(feedback)
        await self.session.flush()
        return feedback

    async def mark_prompt_sent(
        self,
        feedback: BotFeedback,
        message_id: Optional[int],
    ) -> None:
        now = datetime.now(timezone.utc)
        feedback.prompt_message_id = message_id
        feedback.prompted_at = now
        feedback.updated_at = now
        await self.session.flush()

    async def save_liked(
        self,
        feedback: BotFeedback,
        code: str,
        text: str,
    ) -> None:
        feedback.liked_code = code
        feedback.liked_text = text
        feedback.updated_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def save_disliked(
        self,
        feedback: BotFeedback,
        code: str,
        text: str,
        attachment_file_id: Optional[str] = None,
        attachment_type: Optional[str] = None,
    ) -> None:
        feedback.disliked_code = code
        feedback.disliked_text = text
        feedback.disliked_attachment_file_id = attachment_file_id
        feedback.disliked_attachment_type = attachment_type
        feedback.updated_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def complete(self, feedback: BotFeedback) -> None:
        now = datetime.now(timezone.utc)
        feedback.status = "completed"
        feedback.completed_at = now
        feedback.updated_at = now
        await self.session.flush()

    async def mark_reward_granted(self, feedback: BotFeedback) -> None:
        now = datetime.now(timezone.utc)
        feedback.reward_granted_at = now
        feedback.updated_at = now
        await self.session.flush()

    async def schedule_price_offer(
        self,
        feedback: BotFeedback,
        due_at: datetime,
    ) -> None:
        feedback.price_offer_due_at = due_at
        feedback.updated_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def list_due_price_offers(self, now: datetime) -> list[BotFeedback]:
        result = await self.session.execute(
            select(BotFeedback)
            .where(BotFeedback.status == "completed")
            .where(BotFeedback.disliked_code == "price")
            .where(BotFeedback.price_offer_due_at.is_not(None))
            .where(BotFeedback.price_offer_due_at <= now)
            .where(BotFeedback.price_offer_sent_at.is_(None))
            .order_by(BotFeedback.price_offer_due_at.asc())
        )
        return list(result.scalars().all())

    async def mark_price_offer_sent(self, feedback: BotFeedback) -> None:
        now = datetime.now(timezone.utc)
        feedback.price_offer_sent_at = now
        feedback.updated_at = now
        await self.session.flush()

    async def get_available_price_offer(
        self,
        *,
        feedback_id: int,
        telegram_id: int,
    ) -> Optional[BotFeedback]:
        result = await self.session.execute(
            select(BotFeedback)
            .where(BotFeedback.id == feedback_id)
            .where(BotFeedback.telegram_id == telegram_id)
            .where(BotFeedback.status == "completed")
            .where(BotFeedback.disliked_code == "price")
            .where(BotFeedback.price_offer_sent_at.is_not(None))
            .where(BotFeedback.price_offer_used_at.is_(None))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_latest_available_price_offer(self, telegram_id: int) -> Optional[BotFeedback]:
        result = await self.session.execute(
            select(BotFeedback)
            .where(BotFeedback.telegram_id == telegram_id)
            .where(BotFeedback.status == "completed")
            .where(BotFeedback.disliked_code == "price")
            .where(BotFeedback.price_offer_sent_at.is_not(None))
            .where(BotFeedback.price_offer_used_at.is_(None))
            .order_by(BotFeedback.price_offer_sent_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def mark_latest_price_offer_used(self, telegram_id: int) -> None:
        feedback = await self.get_latest_available_price_offer(telegram_id)
        if not feedback:
            return
        now = datetime.now(timezone.utc)
        feedback.price_offer_used_at = now
        feedback.updated_at = now
        await self.session.flush()

    async def mark_admin_reply(
        self,
        feedback: BotFeedback,
        *,
        admin_telegram_id: int,
        reply_text: str,
    ) -> None:
        now = datetime.now(timezone.utc)
        feedback.admin_reply_text = reply_text
        feedback.admin_replied_by = admin_telegram_id
        feedback.admin_replied_at = now
        feedback.updated_at = now
        await self.session.flush()
