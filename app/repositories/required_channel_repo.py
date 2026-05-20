from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.required_channel import RequiredChannel


class RequiredChannelRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(
        self,
        *,
        chat_id: str,
        title: str,
        invite_link: Optional[str],
        created_by_telegram_id: Optional[int],
    ) -> RequiredChannel:
        existing = await self.get_by_chat_id(chat_id)
        if existing:
            existing.title = title
            existing.invite_link = invite_link
            existing.is_active = True
            await self.session.flush()
            return existing

        channel = RequiredChannel(
            chat_id=chat_id,
            title=title,
            invite_link=invite_link,
            created_by_telegram_id=created_by_telegram_id,
        )
        self.session.add(channel)
        await self.session.flush()
        return channel

    async def get_by_id(self, channel_id: int) -> Optional[RequiredChannel]:
        result = await self.session.execute(
            select(RequiredChannel).where(RequiredChannel.id == channel_id)
        )
        return result.scalar_one_or_none()

    async def get_by_chat_id(self, chat_id: str) -> Optional[RequiredChannel]:
        result = await self.session.execute(
            select(RequiredChannel).where(RequiredChannel.chat_id == chat_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[RequiredChannel]:
        result = await self.session.execute(
            select(RequiredChannel).order_by(RequiredChannel.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_active(self) -> list[RequiredChannel]:
        result = await self.session.execute(
            select(RequiredChannel)
            .where(RequiredChannel.is_active.is_(True))
            .order_by(RequiredChannel.created_at.asc())
        )
        return list(result.scalars().all())

    async def set_active(self, channel: RequiredChannel, is_active: bool) -> None:
        channel.is_active = is_active
        await self.session.flush()

    async def delete(self, channel: RequiredChannel) -> None:
        await self.session.delete(channel)
        await self.session.flush()
