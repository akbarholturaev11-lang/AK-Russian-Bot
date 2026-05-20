from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.message import Message


class MessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: int,
        role: str,
        content: str,
        content_type: str = "text",
        telegram_message_id: Optional[int] = None,
    ) -> Message:
        message = Message(
            user_id=user_id,
            role=role,
            content=content,
            content_type=content_type,
            telegram_message_id=telegram_message_id,
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(message)
        await self.session.flush()
        return message

    async def get_recent_by_user(
        self,
        user_id: int,
        limit: int = 10,
    ) -> List[Message]:
        result = await self.session.execute(
            select(Message)
            .where(Message.user_id == user_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = list(result.scalars().all())
        messages.reverse()
        return messages

    async def count_user_messages_today(
        self,
        user_id: int,
        content_type: str = "text",
    ) -> int:
        today = datetime.now(timezone.utc).date()

        result = await self.session.execute(
            select(func.count(Message.id))
            .where(Message.user_id == user_id)
            .where(Message.role == "user")
            .where(Message.content_type == content_type)
            .where(func.date(Message.created_at) == today)
        )
        return int(result.scalar() or 0)

    async def count_user_messages(self, user_id: int) -> int:
        result = await self.session.execute(
            select(func.count(Message.id))
            .where(Message.user_id == user_id)
            .where(Message.role == "user")
        )
        return int(result.scalar() or 0)

    async def get_latest_image_context_by_user(
        self,
        user_id: int,
    ) -> Optional[Message]:
        result = await self.session.execute(
            select(Message)
            .where(Message.user_id == user_id)
            .where(Message.role == "assistant")
            .where(Message.content_type == "image_context")
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_latest_by_content_type(
        self,
        user_id: int,
        content_type: str,
    ):
        from sqlalchemy import select, desc
        result = await self.session.execute(
            select(Message)
            .where(Message.user_id == user_id)
            .where(Message.content_type == content_type)
            .order_by(desc(Message.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()
