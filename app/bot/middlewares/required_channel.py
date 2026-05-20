from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from app.bot.utils.i18n import t
from app.bot.fsm.onboarding import OnboardingStates
from app.repositories.user_repo import UserRepository
from app.services.required_channel_service import RequiredChannelService, is_admin_user


ONBOARDING_STATES = {
    OnboardingStates.choosing_language.state,
    OnboardingStates.choosing_level.state,
}
PENDING_FORCE_SUB_TEXT = "force_sub_pending_text"
PENDING_FORCE_SUB_MESSAGE_ID = "force_sub_pending_message_id"


class RequiredChannelMiddleware(BaseMiddleware):
    def __init__(self, sessionmaker):
        self.sessionmaker = sessionmaker

    async def __call__(
        self,
        handler: Callable[[Any, dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: dict[str, Any],
    ):
        tg_user = getattr(event, "from_user", None)
        if not tg_user:
            return await handler(event, data)

        if is_admin_user(tg_user.id):
            return await handler(event, data)

        if isinstance(event, CallbackQuery) and (event.data or "") == "force_sub:check":
            return await handler(event, data)

        if isinstance(event, Message) and (event.text or "").strip().startswith("/start"):
            return await handler(event, data)

        state = data.get("state")
        if state and await state.get_state() in ONBOARDING_STATES:
            return await handler(event, data)

        session = data.get("session")
        owns_session = False
        if session is None:
            session = self.sessionmaker()
            owns_session = True

        try:
            user = await UserRepository(session).get_by_telegram_id(tg_user.id)
            if not user:
                return await handler(event, data)

            if user and user.status == "active" and user.payment_status == "approved":
                return await handler(event, data)

            service = RequiredChannelService(session)
            bot = data.get("bot") or event.bot
            missing = await service.missing_channels(bot, tg_user.id)
            if not missing:
                return await handler(event, data)

            lang = user.language if user and user.language else "ru"
            text = service.build_required_text(missing, lang)
            keyboard = service.build_required_keyboard(missing, lang)

            if isinstance(event, CallbackQuery):
                await event.answer(t("force_sub_required_alert", lang), show_alert=True)
                if event.message:
                    await event.message.answer(text, reply_markup=keyboard, parse_mode="HTML")
                return None

            if isinstance(event, Message):
                if state and event.text and not event.text.strip().startswith("/"):
                    await state.update_data(
                        **{
                            PENDING_FORCE_SUB_TEXT: event.text,
                            PENDING_FORCE_SUB_MESSAGE_ID: event.message_id,
                        }
                    )
                await event.answer(text, reply_markup=keyboard, parse_mode="HTML", disable_web_page_preview=True)
                return None

            return await handler(event, data)
        finally:
            if owns_session:
                await session.close()
