from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.bot_setting import BotSetting


class BotSettingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, key: str) -> Optional[str]:
        result = await self.session.execute(
            select(BotSetting.value).where(BotSetting.key == key)
        )
        return result.scalar_one_or_none()

    async def set(self, key: str, value: str) -> BotSetting:
        result = await self.session.execute(
            select(BotSetting).where(BotSetting.key == key)
        )
        setting = result.scalar_one_or_none()
        if setting:
            setting.value = value
        else:
            setting = BotSetting(key=key, value=value)
            self.session.add(setting)
        await self.session.flush()
        return setting

    async def get_bool(self, key: str, default: bool = False) -> bool:
        value = await self.get(key)
        if value is None:
            return default
        return value.strip().lower() in {"1", "true", "yes", "on"}

    async def set_bool(self, key: str, value: bool) -> BotSetting:
        return await self.set(key, "1" if value else "0")
