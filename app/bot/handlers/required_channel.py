from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.utils.i18n import t
from app.bot.middlewares.required_channel import (
    PENDING_FORCE_SUB_MESSAGE_ID,
    PENDING_FORCE_SUB_TEXT,
)
from app.repositories.user_repo import UserRepository
from app.services.required_channel_service import RequiredChannelService


router = Router()


class _ForceSubTextProxy:
    def __init__(self, callback: CallbackQuery, text: str, message_id: int | None):
        self._message = callback.message
        self.text = text
        self.from_user = callback.from_user
        self.message_id = message_id or callback.message.message_id

    def __getattr__(self, name):
        return getattr(self._message, name)


@router.callback_query(F.data == "force_sub:check")
async def force_sub_check(callback: CallbackQuery, state: FSMContext, session):
    user = await UserRepository(session).get_by_telegram_id(callback.from_user.id)
    lang = user.language if user and user.language else "ru"
    service = RequiredChannelService(session)
    missing = await service.missing_channels(callback.bot, callback.from_user.id)
    if missing:
        await callback.answer(t("force_sub_still_missing", lang), show_alert=True)
        if callback.message:
            await callback.message.edit_text(
                service.build_required_text(missing, lang),
                reply_markup=service.build_required_keyboard(missing, lang),
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
        return

    await callback.answer(t("force_sub_unlocked_alert", lang), show_alert=True)
    data = await state.get_data()
    pending_text = (data.get(PENDING_FORCE_SUB_TEXT) or "").strip()
    pending_message_id = data.get(PENDING_FORCE_SUB_MESSAGE_ID)
    await state.update_data(
        **{
            PENDING_FORCE_SUB_TEXT: None,
            PENDING_FORCE_SUB_MESSAGE_ID: None,
        }
    )

    if callback.message:
        try:
            await callback.message.delete()
        except Exception:
            if not pending_text:
                await callback.message.edit_text(t("force_sub_unlocked_text", lang), parse_mode="HTML")

    if pending_text and callback.message:
        from app.bot.handlers.messages import handle_text_message

        await handle_text_message(
            _ForceSubTextProxy(callback, pending_text, pending_message_id),
            state,
            session,
        )
