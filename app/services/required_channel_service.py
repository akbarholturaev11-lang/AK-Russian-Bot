from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.utils.i18n import t
from app.config import settings
from app.repositories.bot_setting_repo import BotSettingRepository
from app.repositories.required_channel_repo import RequiredChannelRepository


FORCE_CHANNEL_SETTING_KEY = "force_channel_subscription_enabled"
MEMBER_STATUSES = {"creator", "administrator", "member"}
MAIN_CHANNEL_USERNAME = "aibotsakbar"


def normalize_channel_username(value: str | None) -> str:
    value = (value or "").strip()
    if value.startswith("@"):
        value = value[1:]
    for prefix in ("https://t.me/", "http://t.me/", "t.me/"):
        if value.startswith(prefix):
            value = value[len(prefix):]
            break
    return value.strip("/").split("/")[0].lower()


def is_main_channel(chat_id: str | None, invite_link: str | None = None) -> bool:
    return (
        normalize_channel_username(chat_id) == MAIN_CHANNEL_USERNAME
        or normalize_channel_username(invite_link) == MAIN_CHANNEL_USERNAME
    )


class RequiredChannelService:
    def __init__(self, session):
        self.session = session
        self.repo = RequiredChannelRepository(session)
        self.settings_repo = BotSettingRepository(session)

    async def is_enabled(self) -> bool:
        return await self.settings_repo.get_bool(FORCE_CHANNEL_SETTING_KEY, default=False)

    async def set_enabled(self, enabled: bool) -> None:
        await self.settings_repo.set_bool(FORCE_CHANNEL_SETTING_KEY, enabled)

    async def add_channel(
        self,
        *,
        chat_id: str,
        title: str,
        invite_link: str | None,
        created_by_telegram_id: int | None,
    ):
        return await self.repo.add(
            chat_id=chat_id,
            title=title,
            invite_link=invite_link,
            created_by_telegram_id=created_by_telegram_id,
        )

    async def list_channels(self):
        return await self.repo.list_all()

    async def list_active_channels(self):
        return await self.repo.list_active()

    async def set_channel_active(self, channel_id: int, is_active: bool) -> bool:
        channel = await self.repo.get_by_id(channel_id)
        if not channel:
            return False
        await self.repo.set_active(channel, is_active)
        return True

    async def delete_channel(self, channel_id: int) -> bool:
        channel = await self.repo.get_by_id(channel_id)
        if not channel:
            return False
        await self.repo.delete(channel)
        return True

    async def missing_channels(self, bot: Bot, user_id: int):
        if not await self.is_enabled():
            return []

        missing = []
        for channel in await self.repo.list_active():
            try:
                member = await bot.get_chat_member(channel.chat_id, user_id)
                status = str(member.status).split(".")[-1].lower()
                if status in MEMBER_STATUSES:
                    continue
            except Exception:
                pass
            missing.append(channel)
        return missing

    def build_required_keyboard(self, channels, lang: str) -> InlineKeyboardMarkup:
        rows = []
        for channel in channels:
            url = channel.invite_link
            if not url and str(channel.chat_id).startswith("@"):
                url = f"https://t.me/{str(channel.chat_id).lstrip('@')}"
            if not url:
                continue
            rows.append([InlineKeyboardButton(text=channel.title, url=url)])
        rows.append([
            InlineKeyboardButton(
                text=t("force_sub_check_button", lang),
                callback_data="force_sub:check",
            )
        ])
        return InlineKeyboardMarkup(inline_keyboard=rows)

    def build_required_text(self, channels, lang: str) -> str:
        if len(channels) == 1 and is_main_channel(channels[0].chat_id, channels[0].invite_link):
            return t("force_sub_main_channel_text", lang)
        return t("force_sub_required_text", lang)


def is_admin_user(user_id: int) -> bool:
    return user_id in {int(x.strip()) for x in settings.ADMIN_IDS.split(",") if x.strip()}
