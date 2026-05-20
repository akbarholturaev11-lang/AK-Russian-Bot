from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.config import COURSE_MODE_ENABLED, settings
from app.repositories.user_repo import UserRepository
from app.services.course_engine_service import CourseEngineService
from app.bot.keyboards.subscription import payment_method_keyboard
from app.bot.keyboards.course import reminder_time_keyboard
from app.bot.utils.i18n import t


router = Router()


async def _clear_voice_mode(user, session, state: FSMContext | None = None) -> None:
    if state:
        await state.update_data(pending_voice_transcript=None, pending_voice_message_id=None)
    if user and (getattr(user, "voice_mode", "none") or "none") != "none":
        user.voice_mode = "none"
        await session.commit()

# ──────────────────────────────────────────────
# QA rejim menyusi — barcha tugmalar handleri
# ──────────────────────────────────────────────

@router.message(F.text.in_([
    "💳 Обуна",
    "💳 Подписка",
    "💳 Obuna",
]))
async def handle_subscription_button(message: Message, state: FSMContext, session):
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)

    if not user:
        return

    lang = user.language if user.language else "ru"
    await _clear_voice_mode(user, session, state)

    await message.answer(
        t("payment_method_choose", lang),
        reply_markup=payment_method_keyboard(lang),
        parse_mode="HTML",
    )


@router.message(F.text.in_([
    "👤 Профил",
    "👤 Профиль",
    "👤 Profil",
]))
async def handle_profile_button(message: Message, state: FSMContext, session):
    from app.bot.handlers.commands import _profile_text, profile_menu_keyboard
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user:
        return
    lang = user.language if user.language else "ru"
    await _clear_voice_mode(user, session, state)
    await message.answer(
        _profile_text(user, lang),
        parse_mode="HTML",
        reply_markup=profile_menu_keyboard(lang),
    )


@router.message(F.text.in_([
    "👥 Дӯст даъват кардан",
    "👥 Пригласить друга",
    "👥 Do'st chaqirish",
]))
async def handle_invite_button(message: Message, state: FSMContext, session):
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user:
        return
    lang = user.language if user.language else "ru"
    await _clear_voice_mode(user, session, state)
    await user_repo.ensure_referral_code(user)
    await session.commit()

    referral_link = f"https://t.me/{settings.BOT_USERNAME}?start={user.referral_code}"

    if lang == "tj":
        text = (
            "<b>🎁 Даъватномаи шумо</b>\n\n"
            f"<blockquote>🔗 {referral_link}</blockquote>\n\n"
            "👥 Агар дӯсти шумо бо ин силка ворид шавад,\n"
            "✨ шумо <b>+5 саволи бонусӣ</b> мегиред."
        )
    elif lang == "uz":
        text = (
            "<b>🎁 Taklif havolangiz</b>\n\n"
            f"<blockquote>🔗 {referral_link}</blockquote>\n\n"
            "👥 Do'stingiz shu havola orqali kirib, botga 2 ta xabar yuborsa,\n"
            "✨ siz <b>+5 bonus savol</b> olasiz."
        )
    else:
        text = (
            "<b>🎁 Ваше приглашение</b>\n\n"
            f"<blockquote>🔗 {referral_link}</blockquote>\n\n"
            "👥 Если друг войдёт по этой ссылке и напишет боту 2 сообщения,\n"
            "✨ вы получите <b>+5 бонусных вопросов</b>."
        )

    await message.answer(text, parse_mode="HTML", disable_web_page_preview=True)


@router.message(F.text.in_([
    "❓ Ёрдам",
    "❓ Помощь",
    "❓ Yordam",
]))
async def handle_help_button(message: Message, state: FSMContext, session):
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    lang = user.language if user and user.language else "ru"
    await _clear_voice_mode(user, session, state)
    await message.answer(
        t("help_section_text", lang),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


@router.message(F.text.in_([
    "⏰ Вақти ёдраскунак",
    "⏰ Напоминание",
    "⏰ Eslatma vaqti",
]))
async def handle_reminder_time_button(message: Message, state: FSMContext, session):
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user:
        return

    lang = user.language if user.language else "ru"
    await _clear_voice_mode(user, session, state)

    if not COURSE_MODE_ENABLED:
        await message.answer(
            {
                "uz": "🚧 Kurs eslatmalari hozir o‘chirilgan.",
                "ru": "🚧 Напоминания курса сейчас отключены.",
                "tj": "🚧 Ёдраскунакҳои курс ҳоло хомӯшанд.",
            }.get(lang, "🚧 Напоминания курса сейчас отключены."),
            parse_mode="HTML",
        )
        return

    engine = CourseEngineService(session)
    _, progress, error_key = await engine.get_or_create_progress(message.from_user.id)
    if error_key or not progress:
        await message.answer(t(error_key or "course_no_lesson_found", lang))
        return

    await engine.progress_repo.set_waiting_for(progress, "reminder_setup")
    await session.commit()
    await message.answer(
        t("course_reminder_setup_msg", lang),
        reply_markup=reminder_time_keyboard(lang),
        parse_mode="HTML",
    )


@router.message(F.text.in_([
    "📚 Режими курс",
    "📚 Режим курса",
    "📚 Kurs rejimi",
]))
async def handle_course_mode_button(message: Message, state: FSMContext, session):
    from app.bot.handlers.course import run_course_entry_flow
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    lang = user.language if user and user.language else "ru"
    await _clear_voice_mode(user, session, state)

    if not COURSE_MODE_ENABLED:
        msg_map = {
            "uz": "🚧 Kurs rejimi hozircha o‘chirilgan. Rus tili bo‘yicha savolingizni oddiy xabar qilib yuboring.",
            "ru": "🚧 Режим курса сейчас отключён. Напишите вопрос по русскому обычным сообщением.",
            "tj": "🚧 Реҷаи курс ҳоло хомӯш аст. Саволи худро оид ба русӣ ҳамчун паёми оддӣ фиристед.",
        }
        await message.answer(msg_map.get(lang, msg_map["ru"]))
        return

    await run_course_entry_flow(
        session=session,
        telegram_id=message.from_user.id,
        respond=message.answer,
        show_menu=True,
    )
