import json
import os
from html import escape
from datetime import datetime, timezone, time

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile,
)

from app.bot.fsm.admin_audio import AdminAudioStates
from app.bot.fsm.admin_broadcast import BroadcastStates
from app.bot.fsm.admin_discount import DiscountStates
from app.bot.fsm.admin_management import AdminPriceStates, AdminRequiredChannelStates
from app.bot.fsm.admin_portfolio import AdminPortfolioStates
from app.bot.utils.response_effect import ResponseEffect
from app.bot.handlers.course import (
    get_course_keyboard_for_step,
    _keyboard_for_step,
    run_course_entry_flow,
    _resolve_lessons_for_user_level,
    filter_unlocked_lessons,
    send_course_completion_prompt,
)
from app.bot.keyboards.course import (
    lesson_selection_keyboard,
    review_choice_keyboard,
    course_reminder_timezone_keyboard,
    reminder_time_keyboard,
    hsk4_part_selection_keyboard,
    homework_retry_keyboard,
)
from app.bot.keyboards.course import course_intro_keyboard
from app.bot.keyboards.checkout import checkout_keyboard
from app.bot.keyboards.main_menu import main_menu_keyboard, course_menu_keyboard
from app.bot.keyboards.referral import photo_limit_subscription_keyboard
from app.bot.keyboards.referral import referral_daily_limit_keyboard
from app.bot.keyboards.mode import course_promo_keyboard
from app.bot.keyboards.subscription import payment_method_keyboard
from app.bot.utils.course_formatter import format_intro, format_step
from app.repositories.message_repo import MessageRepository
from app.repositories.user_repo import UserRepository
from app.services.access_service import AccessService
from app.services.ai_service import AIService
from app.services.ai_usage_budget_service import AIUsageBudgetService
from app.services.course_engine_service import CourseEngineService
from app.services.course_tutor_service import CourseTutorService
from app.services.course_progress_summary_service import CourseProgressSummaryService
from app.services.image_input_service import ImageInputService
from app.services.image_qa_service import ImageQAService
from app.services.qa_service import QAService
from app.bot.utils.i18n import t
from app.config import COURSE_MODE_ENABLED


router = Router()

MAX_VOICE_DURATION_SECONDS = 60
VOICE_MODE_NONE = "none"
VOICE_MODE_QA = "qa"
VOICE_MODE_TRANSLATOR = "translator"

_COURSE_TUTOR_STEPS = {
    "intro",
    "vocab",
    "vocabulary",
    "vocab_1",
    "vocab_2",
    "dialogue",
    "grammar",
}

_ADMIN_FSM_STATES = {
    AdminAudioStates.waiting_for_audio.state,
    BroadcastStates.waiting_for_target.state,
    BroadcastStates.waiting_for_text.state,
    DiscountStates.waiting_target_identifier.state,
    DiscountStates.waiting_title.state,
    DiscountStates.waiting_percent.state,
    DiscountStates.waiting_custom_duration.state,
    DiscountStates.waiting_start_at.state,
    DiscountStates.waiting_repeat_days.state,
    DiscountStates.waiting_quota.state,
    DiscountStates.waiting_notify_media.state,
    AdminPortfolioStates.waiting_amount.state,
    AdminPortfolioStates.waiting_reason.state,
    AdminPriceStates.waiting_amount.state,
    AdminRequiredChannelStates.waiting_channel.state,
}


async def _is_admin_flow_message(state: FSMContext) -> bool:
    return await state.get_state() in _ADMIN_FSM_STATES


def _parse_reminder_time(text: str):
    text = (text or "").strip()
    try:
        parts = text.split(":")
        if len(parts) == 2:
            h, m = int(parts[0].strip()), int(parts[1].strip())
            if 0 <= h < 24 and 0 <= m < 60:
                return time(h, m)
    except (ValueError, AttributeError):
        pass
    return None


def _format_static_exercise_result(result: dict, lang: str) -> str:
    correct = result.get("correct", 0)
    total = result.get("total", 0)
    expected = result.get("expected", [])
    passed = result.get("passed", False)

    status = {
        "uz": "✅ Test tekshirildi" if passed else "❌ Testda xatolar bor",
        "ru": "✅ Тест проверен" if passed else "❌ В тесте есть ошибки",
        "tj": "✅ Санҷиш тафтиш шуд" if passed else "❌ Дар санҷиш хато ҳаст",
    }
    answer_title = {
        "uz": "To'g'ri javoblar:",
        "ru": "Правильные ответы:",
        "tj": "Ҷавобҳои дуруст:",
    }
    lines = [
        status.get(lang, status["ru"]),
        f"{correct}/{total}",
    ]
    if expected:
        lines.append("")
        lines.append(answer_title.get(lang, answer_title["ru"]))
        for index, answer in enumerate(expected, 1):
            lines.append(f"{index}. {answer}")
    return "\n".join(lines)


def _format_homework_evaluation_result(result: dict, lang: str) -> str:
    feedback_text = str(result.get("feedback_text") or t("course_homework_received", lang)).strip()
    text = escape(feedback_text)
    if not result.get("passed"):
        text = f"{text}\n\n{t('course_homework_retry_recommendation', lang)}"
    return text


class _TextMessageProxy:
    def __init__(self, message: Message, text: str):
        self._message = message
        self.text = text
        self._from_voice = True

    def __getattr__(self, name):
        return getattr(self._message, name)


def _is_paid_voice_user(user) -> bool:
    return (
        user is not None
        and user.status == "active"
        and user.payment_status == "approved"
    )


def _is_i18n_access_key(value: str) -> bool:
    return value.startswith("access_") or value.startswith("ai_budget_")


def _is_course_tutor_step(step: str) -> bool:
    step = (step or "").strip()
    return step in _COURSE_TUTOR_STEPS or step.startswith("dialogue_")


async def _ensure_ai_available(access_service: AccessService, telegram_id: int, respond, lang: str) -> bool:
    can_use, message_key = await access_service.can_use_text_ai(telegram_id)
    if can_use:
        return True
    await respond(t(message_key, lang), parse_mode="HTML")
    return False


async def _record_ai_usage(session, telegram_id: int, ai_result, source: str):
    return await AIUsageBudgetService(session).record_usage(
        telegram_id=telegram_id,
        result=ai_result,
        source=source,
    )


async def _send_budget_notice(respond, record, lang: str) -> None:
    if not record or not getattr(record, "cooldown_started", False):
        return
    message_key = getattr(record, "message_key", "")
    if message_key:
        await respond(t(message_key, lang), parse_mode="HTML")


async def _answer_course_tutor_question(
    *,
    message: Message,
    session,
    access_service: AccessService,
    user,
    progress,
    lesson,
    text: str,
    lang: str,
) -> bool:
    if not _is_course_tutor_step(getattr(progress, "current_step", "")):
        return False

    text = (text or "").strip()
    if not text:
        return False

    if not await _ensure_ai_available(access_service, message.from_user.id, message.answer, lang):
        return True

    effect = ResponseEffect(message)
    await effect.start()
    try:
        tutor = CourseTutorService()
        reply = await tutor.generate_step_response(
            user_language=user.language,
            user_level=user.level,
            lesson=lesson,
            step=progress.current_step,
            user_message=text,
        )
        budget_record = await _record_ai_usage(
            session=session,
            telegram_id=message.from_user.id,
            ai_result=tutor.last_ai_result,
            source="course_tutor",
        )
        await session.commit()
    finally:
        await effect.stop()

    await message.answer(
        reply,
        reply_markup=_keyboard_for_step(lang, progress.current_step, lesson),
        parse_mode="HTML",
    )
    await _send_budget_notice(message.answer, budget_record, lang)
    return True


def _voice_mode_choice_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("voice_mode_translator_button", lang),
                    callback_data="voice_mode:translator",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=t("voice_mode_qa_button", lang),
                    callback_data="voice_mode:qa",
                ),
            ],
        ]
    )


def _voice_mode_cancel_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t("voice_mode_cancel_button", lang))]],
        resize_keyboard=True,
        input_field_placeholder="...",
    )


async def _transcribe_voice_message(message: Message, user, lang: str):
    effect = ResponseEffect(
        message,
        step_delay=1.8,
        states=(
            t("voice_status_received", lang),
            t("voice_status_transcribing", lang),
            t("voice_status_understanding", lang),
            t("voice_status_answering", lang),
        ),
        delete_on_stop=False,
    )
    await effect.start()

    try:
        telegram_file = await message.bot.get_file(message.voice.file_id)
        downloaded = await message.bot.download_file(telegram_file.file_path)
        downloaded.seek(0)
        audio_bytes = downloaded.read()
        transcript_result = await AIService().transcribe_voice_with_usage(
            audio_bytes=audio_bytes,
            filename="telegram_voice.ogg",
            user_language=user.language,
            user_level=user.level,
        )
        transcript = transcript_result.content
    except Exception:
        await effect.stop()
        await effect.set_text(t("voice_transcription_failed", lang))
        return None, None, effect

    await effect.stop()

    transcript = (transcript or "").strip()
    if not transcript:
        await effect.set_text(t("voice_transcript_empty", lang))
        return None, None, effect

    return transcript, transcript_result, effect


async def _store_voice_transcript(
    session,
    user,
    transcript: str,
    content_type: str,
    telegram_message_id: int | None = None,
) -> None:
    await MessageRepository(session).create(
        user_id=user.id,
        role="user",
        content=transcript,
        content_type=content_type,
        telegram_message_id=telegram_message_id,
    )


async def _process_course_voice_transcript(
    message: Message,
    state: FSMContext,
    session,
    user,
    lang: str,
    transcript: str,
    effect: ResponseEffect,
    voice_budget_record,
) -> None:
    preview_text = escape(transcript[:1000])
    await effect.set_text(t("voice_transcript_preview", lang, text=preview_text))

    await _store_voice_transcript(
        session=session,
        user=user,
        transcript=transcript,
        content_type="voice",
        telegram_message_id=message.message_id,
    )
    await session.commit()

    await handle_text_message(_TextMessageProxy(message, transcript), state, session)
    await _send_budget_notice(message.answer, voice_budget_record, lang)


async def _process_qa_voice_transcript(
    source_message: Message,
    session,
    user,
    lang: str,
    transcript: str,
    telegram_message_id: int | None = None,
) -> None:
    await _store_voice_transcript(
        session=session,
        user=user,
        transcript=transcript,
        content_type="voice",
        telegram_message_id=telegram_message_id,
    )
    await session.commit()

    effect = ResponseEffect(
        source_message,
        step_delay=1.6,
        states=(t("voice_status_answering", lang), "✍️", "🧠"),
    )
    await effect.start()
    try:
        qa_service = QAService(session)
        reply = await qa_service.handle_user_message(
            bot=source_message.bot,
            telegram_id=user.telegram_id,
            text=transcript,
            telegram_message_id=telegram_message_id,
        )
    finally:
        await effect.stop()

    if _is_i18n_access_key(reply):
        await source_message.answer(
            t(reply, lang),
            reply_markup=_voice_mode_cancel_keyboard(lang),
            parse_mode="HTML",
        )
        return

    await source_message.answer(
        reply,
        reply_markup=_voice_mode_cancel_keyboard(lang),
    )
    await _send_budget_notice(source_message.answer, qa_service.last_budget_record, lang)


async def _process_translator_voice_transcript(
    source_message: Message,
    session,
    user,
    lang: str,
    transcript: str,
    telegram_message_id: int | None = None,
    cleanup_message: Message | None = None,
) -> None:
    can_use, message_key = await AccessService(session).can_use_text_ai(user.telegram_id)
    if not can_use:
        if cleanup_message:
            try:
                await cleanup_message.delete()
            except Exception:
                pass
        await source_message.answer(
            t(message_key, lang),
            reply_markup=_voice_mode_cancel_keyboard(lang),
            parse_mode="HTML",
        )
        return

    message_repo = MessageRepository(session)
    recent = await message_repo.get_recent_by_user(user_id=user.id, limit=10)
    history = [
        {"role": msg.role, "content": msg.content}
        for msg in recent
        if msg.content_type == "voice_translator" and msg.role in ("user", "assistant")
    ][-6:]

    effect = None
    if cleanup_message:
        try:
            await cleanup_message.edit_text(t("voice_status_answering", lang))
        except Exception:
            pass
    else:
        effect = ResponseEffect(
            source_message,
            step_delay=1.6,
            states=(t("voice_status_answering", lang), "🌐", "🧠"),
        )
        await effect.start()

    try:
        translation_result = await AIService().translate_voice_with_usage(
            transcript=transcript,
            user_language=user.language,
            history=history,
        )
    except Exception:
        if effect:
            await effect.stop()
        if cleanup_message:
            try:
                await cleanup_message.delete()
            except Exception:
                pass
        await source_message.answer(
            t("voice_translation_failed", lang),
            reply_markup=_voice_mode_cancel_keyboard(lang),
        )
        return
    finally:
        if effect:
            try:
                await effect.stop()
            except Exception:
                pass

    translation_text = (translation_result.content or "").strip()
    if not translation_text:
        if cleanup_message:
            try:
                await cleanup_message.delete()
            except Exception:
                pass
        await source_message.answer(
            t("voice_translation_failed", lang),
            reply_markup=_voice_mode_cancel_keyboard(lang),
        )
        return

    await _store_voice_transcript(
        session=session,
        user=user,
        transcript=transcript,
        content_type="voice_translator",
        telegram_message_id=telegram_message_id,
    )
    await message_repo.create(
        user_id=user.id,
        role="assistant",
        content=translation_text,
        content_type="voice_translator",
    )
    budget_record = await _record_ai_usage(
        session=session,
        telegram_id=user.telegram_id,
        ai_result=translation_result,
        source="voice_translator",
    )
    await session.commit()

    if cleanup_message:
        try:
            await cleanup_message.delete()
        except Exception:
            pass

    result_text = (
        f"{t('voice_transcript_preview', lang, text=escape(transcript[:1000]))}\n\n"
        f"{t('voice_translator_result', lang, text=escape(translation_text[:1500]))}"
    )
    await source_message.answer(
        result_text,
        reply_markup=_voice_mode_cancel_keyboard(lang),
        parse_mode="HTML",
    )
    await _send_budget_notice(source_message.answer, budget_record, lang)


@router.message(F.voice)
async def handle_voice_message(message: Message, state: FSMContext, session):
    if await _is_admin_flow_message(state):
        await message.answer("Admin sozlash jarayoni davom etyapti. Bu voice AI'ga yuborilmadi.")
        return

    user_repo = UserRepository(session)
    access_service = AccessService(session)

    user = await user_repo.get_by_telegram_id(message.from_user.id)
    user_lang = user.language if user and user.language else "ru"

    if user and user.selected_plan_type and user.payment_status != "approved":
        await message.answer(
            t("payment_send_screenshot_only", user_lang),
            reply_markup=checkout_keyboard(user_lang),
        )
        return

    if not user:
        await message.answer(t("access_start_first", user_lang))
        return

    can_use, message_key = await access_service.can_use_text_ai(message.from_user.id)
    if not can_use and message_key in {"access_blocked", "access_payment_pending_review"}:
        await message.answer(t(message_key, user_lang), parse_mode="HTML")
        return

    if not _is_paid_voice_user(user):
        await session.commit()
        await message.answer(
            t("voice_subscription_required", user_lang),
            reply_markup=payment_method_keyboard(user_lang),
            parse_mode="HTML",
        )
        return

    if not can_use:
        await message.answer(t(message_key, user_lang), parse_mode="HTML")
        return

    if message.voice and message.voice.duration > MAX_VOICE_DURATION_SECONDS:
        await message.answer(t("voice_too_long", user_lang, seconds=MAX_VOICE_DURATION_SECONDS))
        return

    transcript, transcript_result, effect = await _transcribe_voice_message(message, user, user_lang)
    if not transcript or not transcript_result or not effect:
        return

    voice_budget_record = await _record_ai_usage(
        session=session,
        telegram_id=message.from_user.id,
        ai_result=transcript_result,
        source="voice_transcribe",
    )
    await session.commit()

    if user.learning_mode == "course" and not COURSE_MODE_ENABLED:
        user.learning_mode = "qa"
        user.voice_mode = "none"
        await session.commit()

    if user.learning_mode == "course":
        await _process_course_voice_transcript(
            message=message,
            state=state,
            session=session,
            user=user,
            lang=user_lang,
            transcript=transcript,
            effect=effect,
            voice_budget_record=voice_budget_record,
        )
        return

    voice_mode = getattr(user, "voice_mode", VOICE_MODE_NONE) or VOICE_MODE_NONE
    if voice_mode == VOICE_MODE_QA:
        await effect.set_text(t("voice_transcript_preview", user_lang, text=escape(transcript[:1000])))
        await _process_qa_voice_transcript(
            source_message=message,
            session=session,
            user=user,
            lang=user_lang,
            transcript=transcript,
            telegram_message_id=message.message_id,
        )
        await _send_budget_notice(message.answer, voice_budget_record, user_lang)
        return

    if voice_mode == VOICE_MODE_TRANSLATOR:
        await effect.set_text(t("voice_transcript_preview", user_lang, text=escape(transcript[:1000])))
        await _process_translator_voice_transcript(
            source_message=message,
            session=session,
            user=user,
            lang=user_lang,
            transcript=transcript,
            telegram_message_id=message.message_id,
            cleanup_message=effect.temp_message,
        )
        await _send_budget_notice(message.answer, voice_budget_record, user_lang)
        return

    await state.update_data(
        pending_voice_transcript=transcript,
        pending_voice_message_id=message.message_id,
    )
    choice_text = (
        f"{t('voice_transcript_preview', user_lang, text=escape(transcript[:1000]))}\n\n"
        f"{t('voice_mode_choose', user_lang)}"
    )
    await effect.set_text(
        choice_text,
        reply_markup=_voice_mode_choice_keyboard(user_lang),
        parse_mode="HTML",
    )
    await _send_budget_notice(message.answer, voice_budget_record, user_lang)


@router.callback_query(F.data.in_(["voice_mode:qa", "voice_mode:translator"]))
async def voice_mode_select_handler(callback: CallbackQuery, state: FSMContext, session):
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer()
        return

    lang = user.language if user.language else "ru"
    data = await state.get_data()
    transcript = (data.get("pending_voice_transcript") or "").strip()
    telegram_message_id = data.get("pending_voice_message_id")
    if not transcript:
        await callback.answer(t("voice_mode_no_pending", lang), show_alert=True)
        return

    mode = VOICE_MODE_TRANSLATOR if callback.data == "voice_mode:translator" else VOICE_MODE_QA
    await user_repo.set_voice_mode(user, mode)
    await session.commit()
    await state.update_data(pending_voice_transcript=None, pending_voice_message_id=None)

    await callback.answer()

    if mode == VOICE_MODE_TRANSLATOR:
        await _process_translator_voice_transcript(
            source_message=callback.message,
            session=session,
            user=user,
            lang=lang,
            transcript=transcript,
            telegram_message_id=telegram_message_id,
            cleanup_message=callback.message,
        )
        return

    try:
        await callback.message.delete()
    except Exception:
        pass
    await _process_qa_voice_transcript(
        source_message=callback.message,
        session=session,
        user=user,
        lang=lang,
        transcript=transcript,
        telegram_message_id=telegram_message_id,
    )



@router.message(F.text & ~F.text.startswith("/"))
async def handle_text_message(message: Message, state: FSMContext, session):
    if await _is_admin_flow_message(state):
        await message.answer(
            "Admin sozlash jarayoni davom etyapti. "
            "Yuqoridagi savolga mos javob yuboring yoki ❌ Bekor qilish tugmasini bosing."
        )
        return

    user_repo = UserRepository(session)
    access_service = AccessService(session)

    user = await user_repo.get_by_telegram_id(message.from_user.id)
    user_lang = user.language if user and user.language else "ru"

    if message.text and message.text.startswith("/"):
        return

    if user and user.selected_plan_type and user.payment_status != "approved":
        await message.answer(
            t("payment_send_screenshot_only", user_lang),
            reply_markup=checkout_keyboard(user_lang),
        )
        return

    if user and not getattr(message, "_from_voice", False):
        voice_mode = getattr(user, "voice_mode", VOICE_MODE_NONE) or VOICE_MODE_NONE
        state_data = await state.get_data()
        has_pending_voice = bool((state_data.get("pending_voice_transcript") or "").strip())
    else:
        voice_mode = VOICE_MODE_NONE
        has_pending_voice = False

    if user and not getattr(message, "_from_voice", False) and (
        voice_mode != VOICE_MODE_NONE or has_pending_voice
    ):
        msg_text = (message.text or "").strip()
        is_cancel = msg_text == t("voice_mode_cancel_button", user_lang)
        if voice_mode != VOICE_MODE_NONE:
            await user_repo.set_voice_mode(user, VOICE_MODE_NONE)
        await state.update_data(pending_voice_transcript=None, pending_voice_message_id=None)
        await session.commit()
        await message.answer(
            t("voice_mode_cancelled" if is_cancel else "voice_mode_text_exit", user_lang),
            reply_markup=main_menu_keyboard(user_lang),
            parse_mode="HTML",
        )
        if is_cancel:
            return

    if user and not COURSE_MODE_ENABLED:
        reminder_engine = CourseEngineService(session)
        reminder_progress = await reminder_engine.progress_repo.get_by_user_id(user.id)
        if reminder_progress and reminder_progress.waiting_for == "reminder_setup":
            await reminder_engine.progress_repo.set_waiting_for(reminder_progress, "none")
            await session.commit()
            await message.answer(
                {
                    "uz": "🚧 Kurs eslatmalari hozir o‘chirilgan.",
                    "ru": "🚧 Напоминания курса сейчас отключены.",
                    "tj": "🚧 Ёдраскунакҳои курс ҳоло хомӯшанд.",
                }.get(user_lang, "🚧 Напоминания курса сейчас отключены."),
                reply_markup=main_menu_keyboard(user_lang),
            )
            return

    if user:
        reminder_engine = CourseEngineService(session)
        reminder_progress = await reminder_engine.progress_repo.get_by_user_id(user.id)
        if reminder_progress and reminder_progress.waiting_for == "reminder_setup":
            msg_text = (message.text or "").strip()
            cancel_map = {"uz": "❌ Bekor qilish", "ru": "❌ Отмена", "tj": "❌ Бекор кардан"}
            if msg_text == cancel_map.get(user_lang, "❌ Отмена"):
                await reminder_engine.progress_repo.set_waiting_for(reminder_progress, "none")
                await session.commit()
                keyboard = course_menu_keyboard(user_lang) if user.learning_mode == "course" else main_menu_keyboard(user_lang)
                await message.answer(
                    t("course_reminder_cancelled", user_lang),
                    reply_markup=keyboard,
                )
                return

            parsed_reminder = _parse_reminder_time(msg_text)
            if not parsed_reminder:
                await message.answer(
                    t("course_invalid_time_format", user_lang),
                    reply_markup=reminder_time_keyboard(user_lang),
                )
                return

            await reminder_engine.progress_repo.set_reminder(
                reminder_progress,
                enabled=True,
                reminder_time=parsed_reminder,
            )
            await reminder_engine.progress_repo.set_waiting_for(reminder_progress, "none")
            await session.commit()
            await message.answer(
                t("course_reminder_tz_title", user_lang),
                reply_markup=course_reminder_timezone_keyboard(),
            )
            return

    if user and user.learning_mode == "course" and not COURSE_MODE_ENABLED:
        user.learning_mode = "qa"
        user.voice_mode = "none"
        await session.commit()
        await message.answer(
            {
                "uz": "🚧 Kurs rejimi hozircha o‘chirilgan. Xabaringizni savol-javob rejimida ko‘rib chiqaman.",
                "ru": "🚧 Режим курса сейчас отключён. Обработаю сообщение в режиме вопрос-ответ.",
                "tj": "🚧 Реҷаи курс ҳоло хомӯш аст. Паёмро дар режими саволу ҷавоб коркард мекунам.",
            }.get(user_lang, "🚧 Режим курса сейчас отключён. Обработаю сообщение в режиме вопрос-ответ."),
            reply_markup=main_menu_keyboard(user_lang),
        )

    if user and COURSE_MODE_ENABLED and user.learning_mode == "course":
        engine = CourseEngineService(session)

        msg_text = (message.text or "").strip()

        if msg_text == t("course_settings_button", user_lang):
            settings_engine = CourseEngineService(session)
            progress = await settings_engine.progress_repo.get_by_user_id(user.id)
            lessons, resolved_level = await _resolve_lessons_for_user_level(settings_engine, user.level)
            if not lessons:
                await message.answer(t("course_no_lessons_available", user_lang))
                return
            level_label = resolved_level.upper() if resolved_level else "LEVEL"
            reply_markup = (
                hsk4_part_selection_keyboard()
                if resolved_level == "hsk4"
                else lesson_selection_keyboard(lessons, page=0, lang=user_lang)
            )
            await message.answer(
                f"{level_label}. {t('course_settings_choose_lesson', user_lang)}",
                reply_markup=reply_markup,
            )
            return

        if msg_text == t("course_progress", user_lang):
            current_user, progress, lesson, error_key = await engine.get_current_lesson(message.from_user.id)
            if error_key:
                await message.answer(t(error_key, user_lang))
                return
            current_lesson_title = lesson.title if lesson else "—"
            completed_count = getattr(progress, "completed_lessons_count", 0) or 0
            summary = await CourseProgressSummaryService(session).summarize_completed_range(progress)
            days_studying = 1
            if progress.created_at:
                created = progress.created_at
                if not created.tzinfo:
                    created = created.replace(tzinfo=timezone.utc)
                days_studying = max(1, (datetime.now(timezone.utc) - created).days)
            await message.answer(
                t("course_progress_full_text", user_lang,
                  lessons=completed_count,
                  vocab=summary["vocab"],
                  dialogues=summary["dialogues"],
                  days=days_studying,
                  current=current_lesson_title),
                parse_mode="HTML",
            )
            return

        if msg_text == t("course_back_to_qa_button", user_lang):
            user.learning_mode = "qa"
            user.voice_mode = "none"
            await session.commit()
            await message.answer(t("send_first_message", user_lang), reply_markup=main_menu_keyboard(user_lang))
            return

        if msg_text == t("course_reread_button", user_lang):
            _, progress_rr, lesson_rr, err_rr = await engine.get_current_lesson(message.from_user.id)
            if err_rr or not lesson_rr:
                await message.answer(t(err_rr or "course_no_lesson_found", user_lang))
                return
            await engine.progress_repo.set_current_lesson_and_step(
                progress=progress_rr,
                lesson_id=lesson_rr.id,
                step="intro",
                waiting_for="none",
            )
            await session.commit()
            text_rr = format_intro(lesson_rr, user_lang)
            await message.answer(t("course_reread_start_msg", user_lang))
            await message.answer(text_rr, reply_markup=course_intro_keyboard(user_lang), parse_mode="HTML")
            return

        if msg_text == t("course_reminder_set_button", user_lang):
            progress_rm = await engine.progress_repo.get_by_user_id(user.id)
            if not progress_rm:
                return
            await engine.progress_repo.set_waiting_for(progress_rm, "reminder_setup")
            await session.commit()
            await message.answer(
                t("course_reminder_setup_msg", user_lang),
                reply_markup=reminder_time_keyboard(user_lang),
                parse_mode="HTML",
            )
            return

        current_user, progress, lesson, error_key = await engine.get_current_lesson(message.from_user.id)
        if error_key:
            await message.answer(t(error_key, user_lang))
            return

        if progress.waiting_for == "reminder_setup":
            cancel_map = {"uz": "❌ Bekor qilish", "ru": "❌ Отмена", "tj": "❌ Бекор кардан"}
            if msg_text == cancel_map.get(user_lang, "❌ Отмена"):
                await engine.progress_repo.set_waiting_for(progress, "none")
                await session.commit()
                await message.answer(
                    t("course_reminder_cancelled", user_lang),
                    reply_markup=course_menu_keyboard(user_lang),
                )
                return
            parsed_reminder = _parse_reminder_time(msg_text)
            if not parsed_reminder:
                await message.answer(
                    t("course_invalid_time_format", user_lang),
                    reply_markup=reminder_time_keyboard(user_lang),
                )
                return
            await engine.progress_repo.set_reminder(progress, enabled=True, reminder_time=parsed_reminder)
            await engine.progress_repo.set_waiting_for(progress, "none")
            await session.commit()
            # Faqat bitta blok — timezone tanlash (yakuniy xabar timezone tanlanganida yuboriladi)
            await message.answer(
                t("course_reminder_tz_title", user_lang),
                reply_markup=course_reminder_timezone_keyboard(),
            )
            return

        if progress.waiting_for == "satisfaction_answer":
            await message.answer(
                t("course_wait_for_answer", user_lang),
                reply_markup=get_course_keyboard_for_step(user_lang, progress.current_step),
            )
            return

        if progress.current_step == "completed" and progress.homework_status == "completed":
            if progress.waiting_for == "review_choice":
                await message.answer(
                    t("course_review_choice", user_lang),
                    reply_markup=review_choice_keyboard(user_lang),
                )
                return

            await send_course_completion_prompt(
                respond=message.answer,
                engine=engine,
                lesson=lesson,
                lang=user_lang,
            )
            return

        if progress.waiting_for == "satisfaction_reason":
            await engine.mark_not_satisfied_and_stay(message.from_user.id)
            refreshed_user, refreshed_progress, refreshed_lesson, refreshed_error = await engine.get_current_lesson(
                message.from_user.id
            )
            if refreshed_error:
                await message.answer(t(refreshed_error, user_lang))
                return

            await engine.progress_repo.set_waiting_for(refreshed_progress, "satisfaction_answer")
            await session.commit()

            text = format_step(refreshed_lesson, user_lang, "review")
            await message.answer(t("course_lesson_reexplaining", user_lang))
            await message.answer(
                text or t("course_lesson_what_unclear", user_lang),
                reply_markup=_keyboard_for_step(user_lang, refreshed_progress.current_step, refreshed_lesson),
                parse_mode="HTML",
            )
            return

        if progress.waiting_for == "exercise_answer":
            result = await engine.mark_exercise_submitted(
                message.from_user.id,
                message.text or "",
            )
            if isinstance(result, dict) and result.get("error_key"):
                await message.answer(t(result["error_key"], user_lang))
                return

            _, refreshed_progress, refreshed_lesson, refreshed_error = await engine.get_current_lesson(
                message.from_user.id
            )
            if refreshed_error:
                await message.answer(t(refreshed_error, user_lang))
                return

            satisfaction_text = format_step(refreshed_lesson, user_lang, "satisfaction_check")

            await message.answer(_format_static_exercise_result(result, user_lang), parse_mode="HTML")
            await message.answer(
                satisfaction_text or t("course_lesson_satisfaction_question", user_lang),
                reply_markup=get_course_keyboard_for_step(user_lang, "satisfaction_check"),
                parse_mode="HTML",
            )
            return

        if progress.waiting_for == "homework_submission":
            if not msg_text:
                await message.answer(t("course_homework_empty", user_lang))
                return

            if not await _ensure_ai_available(access_service, message.from_user.id, message.answer, user_lang):
                return

            effect = ResponseEffect(message)
            await effect.start()
            try:
                result = await engine.mark_homework_submitted(
                    message.from_user.id,
                    message.text or "",
                )
            finally:
                await effect.stop()

            if isinstance(result, dict) and result.get("error_key"):
                await message.answer(t(result["error_key"], user_lang))
                return

            budget_record = await _record_ai_usage(
                session=session,
                telegram_id=message.from_user.id,
                ai_result=result.get("ai_result") if isinstance(result, dict) else None,
                source="course_homework",
            )
            await session.commit()

            if isinstance(result, dict):
                await message.answer(
                    _format_homework_evaluation_result(result, user_lang),
                    reply_markup=None if result.get("passed") else homework_retry_keyboard(user_lang),
                    parse_mode="HTML",
                )
            else:
                await message.answer(t("course_homework_received", user_lang))

            await _send_budget_notice(message.answer, budget_record, user_lang)

            if isinstance(result, dict) and result.get("passed"):
                _, _, next_lesson, next_error = await engine.activate_next_lesson(message.from_user.id)
                if next_error == "course_no_next_lesson":
                    await message.answer(t("course_completed_title", user_lang))
                    return
                if next_error:
                    await message.answer(t(next_error, user_lang))
                    return

                await message.answer(t("course_homework_auto_next", user_lang))
                await message.answer(
                    format_intro(next_lesson, user_lang),
                    reply_markup=course_intro_keyboard(user_lang),
                    parse_mode="HTML",
                )

            return

        if progress.waiting_for == "homework_decision":
            await message.answer(
                t("course_homework_choose_next_action", user_lang),
                reply_markup=homework_retry_keyboard(user_lang),
                parse_mode="HTML",
            )
            return

        if progress.waiting_for == "next_study_time":
            # Agar kimdir eski holatda qolib ketgan bo’lsa — avtomatik o’tkazib yuborish
            await engine.set_next_study_at(message.from_user.id, None)
            _, rp, rl, re_err = await engine.get_current_lesson(message.from_user.id)
            if not re_err:
                if rp.waiting_for == "review_choice":
                    await message.answer(
                        t("course_review_choice", user_lang),
                        reply_markup=review_choice_keyboard(user_lang),
                    )
                else:
                    await send_course_completion_prompt(
                        respond=message.answer,
                        engine=engine,
                        lesson=rl,
                        lang=user_lang,
                    )
            return

        if await _answer_course_tutor_question(
            message=message,
            session=session,
            access_service=access_service,
            user=current_user,
            progress=progress,
            lesson=lesson,
            text=msg_text,
            lang=user_lang,
        ):
            return

        await message.answer(
            t("course_wait_for_answer", user_lang),
            reply_markup=_keyboard_for_step(user_lang, progress.current_step, lesson),
            parse_mode="HTML",
        )
        return

    can_use, message_key = await access_service.can_use_text_ai(message.from_user.id)

    if not can_use:
        if message_key == "access_daily_limit_reached":
            if user and not await user_repo.was_daily_limit_offer_sent_today(user):
                await user_repo.mark_daily_limit_offer_sent(user)
                await session.commit()
                await message.answer(
                    t("referral_daily_limit_offer", user_lang),
                    reply_markup=referral_daily_limit_keyboard(user_lang),
                )
                return

            await message.answer(t("access_daily_limit_reached", user_lang), parse_mode="HTML")
            return

        await message.answer(t(message_key, user_lang), parse_mode="HTML")
        return

    effect = ResponseEffect(message)
    await effect.start()

    try:
        qa_service = QAService(session)
        reply = await qa_service.handle_user_message(
            bot=message.bot,
            telegram_id=message.from_user.id,
            text=message.text,
            telegram_message_id=message.message_id,
        )
    finally:
        await effect.stop()

    if _is_i18n_access_key(reply):
        await message.answer(t(reply, user_lang), parse_mode="HTML")
        return

    await message.answer(reply)
    await _send_budget_notice(message.answer, qa_service.last_budget_record, user_lang)

    # Show course promo after 3rd QA message (once per user)
    refreshed_user = await user_repo.get_by_telegram_id(message.from_user.id)
    if (
        refreshed_user
        and not refreshed_user.course_promo_sent
        and refreshed_user.questions_used >= 3
        and refreshed_user.learning_mode == "qa"
        and COURSE_MODE_ENABLED
    ):
        refreshed_user.course_promo_sent = True
        await session.commit()

        lang_photo_map = {
            "uz": "app/static/course_promo/uz.jpg",
            "tj": "app/static/course_promo/tj.jpg",
            "ru": "app/static/course_promo/ru.jpg",
        }
        photo_path = lang_photo_map.get(user_lang, "app/static/course_promo/ru.jpg")
        if os.path.exists(photo_path):
            await message.answer_photo(
                FSInputFile(photo_path),
                caption=t("course_promo_caption", user_lang),
                reply_markup=course_promo_keyboard(user_lang),
                parse_mode="HTML",
            )


@router.callback_query(F.data == "course_promo:start")
async def handle_course_promo_start(callback: CallbackQuery, state: FSMContext, session):
    await state.update_data(pending_voice_transcript=None, pending_voice_message_id=None)
    await callback.answer()
    await run_course_entry_flow(
        session=session,
        telegram_id=callback.from_user.id,
        respond=callback.message.answer,
    )


@router.message(F.photo)
async def handle_image_message(message: Message, state: FSMContext, session):
    if await _is_admin_flow_message(state):
        await message.answer("Admin sozlash jarayoni davom etyapti. Bu xabar AI'ga yuborilmadi.")
        return

    user_repo = UserRepository(session)
    access_service = AccessService(session)
    image_input_service = ImageInputService()

    user = await user_repo.get_by_telegram_id(message.from_user.id)
    user_lang = user.language if user and user.language else "ru"

    can_use, message_key = await access_service.can_use_image_ai(message.from_user.id)
    if not can_use:
        if message_key == "access_daily_image_limit_reached":
            await message.answer(
                t("access_daily_image_limit_reached", user_lang),
                reply_markup=photo_limit_subscription_keyboard(user_lang),
            )
            return

        await message.answer(t(message_key, user_lang))
        return

    if not user:
        await message.answer(t("access_start_first", user_lang))
        return

    file_id = image_input_service.get_image_file_id(message)
    mime_type = image_input_service.get_image_mime_type(message)

    if not file_id:
        await message.answer(t("image_invalid_format", user_lang))
        return

    effect = ResponseEffect(message)
    await effect.start()

    try:
        image_qa_service = ImageQAService(session)
        reply = await image_qa_service.handle_user_image(
            bot=message.bot,
            telegram_id=message.from_user.id,
            file_id=file_id,
            mime_type=mime_type,
            telegram_message_id=message.message_id,
        )
    finally:
        await effect.stop()

    if _is_i18n_access_key(reply):
        await message.answer(t(reply, user_lang), parse_mode="HTML")
        return

    await message.answer(reply)
    await _send_budget_notice(message.answer, image_qa_service.last_budget_record, user_lang)


@router.message(F.document)
async def handle_unsupported_document(message: Message, state: FSMContext, session):
    if await _is_admin_flow_message(state):
        await message.answer("Admin sozlash jarayoni davom etyapti. Bu fayl AI'ga yuborilmadi.")
        return

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    user_lang = user.language if user and user.language else "ru"

    if user and user.selected_plan_type:
        await message.answer(
            t("payment_send_screenshot_only", user_lang),
            reply_markup=checkout_keyboard(user_lang),
        )
        return

    await message.answer(t("image_invalid_format", user_lang))
