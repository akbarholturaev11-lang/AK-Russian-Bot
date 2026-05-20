from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
import json

from app.repositories.user_repo import UserRepository
from app.services.course_engine_service import CourseEngineService
from app.services.course_progress_summary_service import CourseProgressSummaryService
from app.bot.utils.i18n import t
from app.bot.keyboards.course import (
    lesson_selection_keyboard, review_choice_keyboard,
    course_intro_keyboard, course_vocab_keyboard, course_dialogue_keyboard,
    course_grammar_keyboard, course_homework_keyboard,
    course_next_step_keyboard, course_vocab_v2_keyboard, course_dialogue_n_keyboard,
    next_study_time_inline_keyboard,
    hsk4_part_selection_keyboard, filter_hsk4_lessons_by_part, normalize_hsk4_part,
)
from app.bot.keyboards.subscription import payment_method_keyboard
from app.bot.keyboards.course_context import (
    course_understood_keyboard,
    course_review_offer_keyboard,
    course_satisfaction_keyboard,
    course_homework_keyboard as _ctx_homework_keyboard,
    course_next_lesson_keyboard,
)

from app.config import COURSE_MODE_ENABLED
from app.bot.utils.course_formatter import (
    format_intro, format_vocab, format_dialogue,
    format_grammar, format_exercise, format_step,
)
from app.bot.keyboards.main_menu import course_menu_keyboard, main_menu_keyboard
from app.bot.keyboards.course import course_reminder_timezone_keyboard
import json
from datetime import datetime, timezone



async def _block_if_course_disabled(callback, session):
    if not COURSE_MODE_ENABLED:
        lang = "ru"
        try:
            user_repo = UserRepository(session)
            user = await user_repo.get_by_telegram_id(callback.from_user.id)
            if user and user.language:
                lang = user.language
        except:
            pass

        msg_map = {
            "uz": "🚧 Kurs rejimi hozircha o‘chirilgan. Rus tili bo‘yicha savolingizni oddiy xabar qilib yuboring.",
            "ru": "🚧 Режим курса сейчас отключён. Напишите вопрос по русскому обычным сообщением.",
            "tj": "🚧 Реҷаи курс ҳоло хомӯш аст. Саволи худро оид ба русӣ ҳамчун паёми оддӣ фиристед.",
        }

        await callback.answer()
        await callback.message.answer(msg_map.get(lang, msg_map["ru"]))
        return True
    return False


router = Router()


def _course_level_candidates(level: str | None) -> tuple[str, ...]:
    normalized = (level or "").strip().lower()
    fallback_map = {
        "beginner": ("hsk1",),
        "hsk1": ("hsk1",),
        "hsk2": ("hsk2", "hsk1"),
        "hsk3": ("hsk3", "hsk2", "hsk1"),
        "hsk4": ("hsk4", "hsk3", "hsk2", "hsk1"),
    }
    return fallback_map.get(normalized, ("hsk1",))


async def _resolve_lessons_for_user_level(engine: CourseEngineService, level: str | None):
    candidates = _course_level_candidates(level)
    for candidate in candidates:
        lessons = await engine.lesson_repo.list_by_level(candidate)
        if lessons:
            return lessons, candidate
    return [], candidates[0]


def filter_unlocked_lessons(lessons: list, progress) -> list:
    unlocked_order = max(1, (getattr(progress, "completed_lessons_count", 0) or 0) + 1)
    return [lesson for lesson in lessons if lesson.lesson_order <= unlocked_order]


def _hsk4_part_label(part: str | None) -> str:
    return "下" if part == "lower" else "上"


def _lesson_selection_markup(lessons: list, resolved_level: str, lang: str):
    if resolved_level == "hsk4":
        return hsk4_part_selection_keyboard()
    return lesson_selection_keyboard(lessons, page=0, lang=lang)


async def send_course_completion_prompt(*, respond, engine: CourseEngineService, lesson, lang: str) -> None:
    next_lesson = await engine.lesson_repo.get_next_lesson(
        level=lesson.level,
        lesson_order=lesson.lesson_order,
    )
    if next_lesson:
        await respond(
            t("course_next_lesson_unlocked", lang),
            reply_markup=course_next_lesson_keyboard(lang),
        )
    else:
        await respond(t("course_completed_title", lang))


def _format_homework_text(lang: str, homework_raw) -> str:
    title = t("course_homework_title", lang)

    if not homework_raw:
        return title

    try:
        data = json.loads(homework_raw) if isinstance(homework_raw, str) else homework_raw
    except Exception:
        return f"{title}\n\n{homework_raw}"

    if not isinstance(data, list):
        return f"{title}\n\n{data}"

    lines = [title, ""]
    for i, item in enumerate(data, 1):
        if not isinstance(item, dict):
            lines.append(f"{i}. {item}")
            continue

        instruction = (
            item.get(f"instruction_{lang}")
            or item.get("instruction_uz")
            or item.get("instruction", "")
        )
        direct_text = item.get(lang) or item.get("uz") or ""
        words = item.get("words", [])
        example = item.get("example", "")
        topic = (
            item.get(f"topic_{lang}")
            or item.get("topic_uz")
            or item.get("topic", "")
        )

        if direct_text and not instruction:
            lines.append(f"{i}. {direct_text}")
            lines.append("")
            continue

        lines.append(f"{i}. {instruction}")
        if words:
            lines.append(f"   📌 {' · '.join(words)}")
        if example:
            lines.append(f"   💬 {example}")
        if topic:
            lines.append(f"   🎯 {topic}")
        lines.append("")

    return "\n".join(lines).rstrip()





def get_course_keyboard_for_step(lang: str, step: str):
    if step == "satisfaction_check":
        return course_satisfaction_keyboard(lang)
    if step == "homework":
        return _ctx_homework_keyboard(lang)
    if step == "completed":
        return course_next_lesson_keyboard(lang)
    return course_understood_keyboard(lang, step)

@router.callback_query(F.data.startswith("course:lessons_page:"))
async def course_lessons_page_handler(callback: CallbackQuery, session):
    if await _block_if_course_disabled(callback, session):
        return

    user_repo = UserRepository(session)
    engine = CourseEngineService(session)

    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer()
        return

    lang = user.language if user.language else "ru"

    if user.status != "active":
        await callback.answer()
        await callback.message.answer(
            t("course_only_active_users", lang),
            reply_markup=payment_method_keyboard(lang),
            parse_mode="HTML",
        )
        return

    parts = callback.data.split(":")
    try:
        page = int(parts[2])
    except Exception:
        page = 0
    hsk4_part = normalize_hsk4_part(parts[3] if len(parts) > 3 else None)

    lessons, resolved_level = await _resolve_lessons_for_user_level(engine, user.level)
    if resolved_level == "hsk4":
        if not hsk4_part:
            await callback.answer()
            await callback.message.edit_reply_markup(reply_markup=hsk4_part_selection_keyboard())
            return
        part_lessons = filter_hsk4_lessons_by_part(lessons, hsk4_part)
        if not part_lessons:
            await callback.answer(t("course_no_lessons_available", lang), show_alert=True)
            return

    await callback.answer()
    await callback.message.edit_reply_markup(
        reply_markup=lesson_selection_keyboard(
            lessons,
            page=page,
            lang=lang,
            hsk4_part=hsk4_part,
        )
    )


@router.callback_query(F.data.startswith("course:hsk4_part:"))
async def course_hsk4_part_handler(callback: CallbackQuery, session):
    if await _block_if_course_disabled(callback, session):
        return

    user_repo = UserRepository(session)
    engine = CourseEngineService(session)

    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer()
        return

    lang = user.language if user.language else "ru"

    if user.status != "active":
        await callback.answer()
        await callback.message.answer(
            t("course_only_active_users", lang),
            reply_markup=payment_method_keyboard(lang),
            parse_mode="HTML",
        )
        return

    hsk4_part = normalize_hsk4_part(callback.data.split(":")[-1])
    if not hsk4_part:
        await callback.answer()
        return

    lessons, resolved_level = await _resolve_lessons_for_user_level(engine, user.level)
    if resolved_level != "hsk4":
        await callback.answer()
        await callback.message.edit_reply_markup(
            reply_markup=lesson_selection_keyboard(lessons, page=0, lang=lang)
        )
        return

    part_lessons = filter_hsk4_lessons_by_part(lessons, hsk4_part)
    if not part_lessons:
        await callback.answer(t("course_no_lessons_available", lang), show_alert=True)
        return

    text = f"HSK4 {_hsk4_part_label(hsk4_part)}. {t('course_choose_lesson', lang)}"

    await callback.answer()
    await callback.message.edit_text(
        text,
        reply_markup=lesson_selection_keyboard(
            lessons,
            page=0,
            lang=lang,
            hsk4_part=hsk4_part,
        ),
    )


@router.callback_query(F.data.startswith("course:pick_lesson:"))
async def course_pick_lesson_handler(callback: CallbackQuery, session):
    if await _block_if_course_disabled(callback, session):
        return

    engine = CourseEngineService(session)

    lang = callback.from_user.language_code if callback.from_user.language_code in ["ru", "uz", "tj"] else "ru"

    try:
        lesson_id = int(callback.data.split(":")[-1])
    except Exception:
        await callback.answer()
        return

    _, _, _, error_key = await engine.pick_lesson(callback.from_user.id, lesson_id)
    if error_key:
        if error_key == "course_lesson_not_unlocked":
            await callback.answer(t(error_key, lang), show_alert=True)
        else:
            await callback.answer()
            await callback.message.answer(t(error_key, lang))
        return

    await callback.answer()
    try:
        await callback.message.delete()
    except Exception:
        pass
    await run_course_entry_flow(
        session=session,
        telegram_id=callback.from_user.id,
        respond=callback.message.answer,
        show_menu=True,
    )



@router.callback_query(F.data == "mode:qa")
async def mode_qa_handler(callback: CallbackQuery, state: FSMContext, session):

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)

    lang = callback.from_user.language_code if callback.from_user.language_code in ["ru", "uz", "tj"] else "ru"

    if not user:
        await callback.answer()
        await callback.message.answer(t("user_not_found", lang))
        return

    lang = user.language if user.language else "ru"
    user.learning_mode = "qa"
    user.voice_mode = "none"
    await state.update_data(pending_voice_transcript=None, pending_voice_message_id=None)
    await session.commit()

    await callback.answer()
    await callback.message.answer(t("trial_started_info", lang))
    await callback.message.answer(t("send_first_message", lang), reply_markup=main_menu_keyboard(lang))

@router.callback_query(F.data == "mode:course")
async def course_mode_open_handler(callback: CallbackQuery, state: FSMContext, session):
    if await _block_if_course_disabled(callback, session):
        return

    await state.update_data(pending_voice_transcript=None, pending_voice_message_id=None)
    await callback.answer()
    await run_course_entry_flow(
        session=session,
        telegram_id=callback.from_user.id,
        respond=callback.message.answer,
        show_menu=True,
    )




async def run_course_entry_flow(
    *,
    session,
    telegram_id: int,
    respond,
    show_menu: bool = True,
):
    user_repo = UserRepository(session)
    engine = CourseEngineService(session)

    user = await user_repo.get_by_telegram_id(telegram_id)
    if not user:
        await respond(t("access_start_first", "ru"))
        return

    lang = user.language if user.language else "ru"

    if not COURSE_MODE_ENABLED:
        user.learning_mode = "qa"
        user.voice_mode = "none"
        await session.commit()
        msg_map = {
            "uz": "🚧 Kurs rejimi hozircha o‘chirilgan. Rus tili bo‘yicha savolingizni oddiy xabar qilib yuboring.",
            "ru": "🚧 Режим курса сейчас отключён. Напишите вопрос по русскому обычным сообщением.",
            "tj": "🚧 Реҷаи курс ҳоло хомӯш аст. Саволи худро оид ба русӣ ҳамчун паёми оддӣ фиристед.",
        }
        await respond(msg_map.get(lang, msg_map["ru"]))
        return

    if user.status != "active":
        await respond(
            t("course_only_active_users", lang),
            reply_markup=payment_method_keyboard(lang),
            parse_mode="HTML",
        )
        return

    user.learning_mode = "course"
    user.voice_mode = "none"
    await session.commit()

    progress = await engine.progress_repo.get_by_user_id(user.id)
    if not progress:
        progress = await engine.progress_repo.create(
            user_id=user.id,
            level=user.level,
            current_lesson_id=None,
            current_step="intro",
            waiting_for="none",
        )

    # Kurs rejimiga kirish bilanoq menyuni ko'rsat
    await respond(t("course_menu_title", lang), reply_markup=course_menu_keyboard(lang))

    if not progress.current_lesson_id:
        lessons, resolved_level = await _resolve_lessons_for_user_level(engine, user.level)

        if not lessons:
            await respond(t("course_no_lessons_available", lang))
            return

        level_label = resolved_level.upper() if resolved_level else "HSK"
        await respond(
            f"{level_label}. {t('course_choose_lesson', lang)}",
            reply_markup=_lesson_selection_markup(lessons, resolved_level, lang),
        )
        return

    if getattr(progress, "waiting_for", None) == "next_study_time":
        # Avtomatik o'tkazib yuboramiz — foydalanuvchi xohlasa menyu orqali eslatma qo'yadi
        await engine.set_next_study_at(telegram_id, None)
        _, p2, l2, e2 = await engine.get_current_lesson(telegram_id)
        if not e2:
            if getattr(p2, "waiting_for", None) == "review_choice":
                await respond(
                    t("course_review_choice", lang),
                    reply_markup=review_choice_keyboard(lang),
                )
            else:
                await send_course_completion_prompt(
                    respond=respond,
                    engine=engine,
                    lesson=l2,
                    lang=lang,
                )
        return

    if (
        getattr(progress, "current_step", None) == "completed"
        and getattr(progress, "homework_status", None) == "completed"
        and getattr(progress, "waiting_for", None) == "review_choice"
    ):
        await respond(
            t("course_review_choice", lang),
            reply_markup=review_choice_keyboard(lang),
        )
        return

    if getattr(progress, "current_step", None) == "completed" and getattr(progress, "homework_status", None) == "completed":
        lesson = await engine.lesson_repo.get_by_id(progress.current_lesson_id)
        if lesson:
            await send_course_completion_prompt(
                respond=respond,
                engine=engine,
                lesson=lesson,
                lang=lang,
            )
        else:
            await respond(t("course_completed_title", lang))
        return

    user, progress, lesson, error_key = await engine.continue_course(telegram_id)
    if error_key:
        await respond(t(error_key, lang))
        return

    step = progress.current_step

    # V1 → V2 migratsiya: eski "vocab"/"dialogue" stepida qolgan foydalanuvchilarni
    # V2 ekvivalentiga ko'chiramiz (V2 darslar uchun)
    from app.services.course_engine_service import is_v2_lesson
    if is_v2_lesson(lesson):
        if step == "vocab":
            step = "vocab_1"
            await engine.progress_repo.set_current_lesson_and_step(
                progress=progress, lesson_id=lesson.id, step=step, waiting_for="none"
            )
            await session.commit()
        elif step == "dialogue":
            step = "dialogue_1"
            await engine.progress_repo.set_current_lesson_and_step(
                progress=progress, lesson_id=lesson.id, step=step, waiting_for="none"
            )
            await session.commit()

    if step == "exercise" and getattr(progress, "waiting_for", "none") != "exercise_answer":
        await engine.progress_repo.set_waiting_for(progress, "exercise_answer")
        await session.commit()

    if step == "homework":
        text = _format_homework_text(lang, lesson.homework_json)
        keyboard = get_course_keyboard_for_step(lang, step)
        await respond(text, reply_markup=keyboard, parse_mode="HTML")
    else:
        await _send_step(respond, user, lesson, step, lang, session)

@router.message(F.text == "/course")
async def course_command_handler(message: Message, state: FSMContext, session):
    await state.update_data(pending_voice_transcript=None, pending_voice_message_id=None)

    if not COURSE_MODE_ENABLED:
        lang = "ru"
        try:
            user_repo = UserRepository(session)
            user = await user_repo.get_by_telegram_id(message.from_user.id)
            if user and user.language:
                lang = user.language
        except:
            pass

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


@router.callback_query(F.data == "course:back_to_qa")
async def course_back_to_qa_handler(callback: CallbackQuery, state: FSMContext, session):
    if await _block_if_course_disabled(callback, session):
        return

    user_repo = UserRepository(session)

    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer()
        await callback.message.answer(t("access_start_first", "ru"))
        return

    user.learning_mode = "qa"
    user.voice_mode = "none"
    await state.update_data(pending_voice_transcript=None, pending_voice_message_id=None)
    await session.commit()

    lang = user.language if user.language else "ru"

    await callback.answer()
    await callback.message.answer(t("send_first_message", lang), reply_markup=main_menu_keyboard(lang))




@router.callback_query(F.data == "course:continue")
async def course_continue_handler(callback: CallbackQuery, state: FSMContext, session):
    if await _block_if_course_disabled(callback, session):
        return

    await state.update_data(pending_voice_transcript=None, pending_voice_message_id=None)
    await callback.answer()
    await run_course_entry_flow(
        session=session,
        telegram_id=callback.from_user.id,
        respond=callback.message.answer,
    )




@router.callback_query(F.data == "course:review_yes")
async def course_review_yes_handler(callback: CallbackQuery, session):
    if await _block_if_course_disabled(callback, session):
        return

    user_repo = UserRepository(session)
    engine = CourseEngineService(session)

    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer()
        return

    lang = user.language if user.language else "ru"
    progress = await engine.progress_repo.get_by_user_id(user.id)
    if not progress or progress.waiting_for != "review_choice":
        await callback.answer()
        return

    user, progress, lesson, error_key = await engine.get_current_lesson(callback.from_user.id)
    if error_key:
        await callback.answer()
        await callback.message.answer(t(error_key, lang))
        return

    review_text = format_step(lesson, lang, "review") or _static_course_missing_text(lang)

    if getattr(progress, "homework_status", None) == "completed":
        await engine.progress_repo.set_waiting_for(progress, "none")
        await session.commit()

        await callback.answer()
        await callback.message.answer(t("course_review", lang))
        await callback.message.answer(review_text)
        await send_course_completion_prompt(
            respond=callback.message.answer,
            engine=engine,
            lesson=lesson,
            lang=lang,
        )
        return

    await engine.progress_repo.set_waiting_for(progress, "homework_submission")
    await session.commit()

    homework_text = _format_homework_text(lang, lesson.homework_json)

    await callback.answer()
    await callback.message.answer(t("course_review_then_homework", lang))
    await callback.message.answer(review_text)
    await callback.message.answer(t("course_lesson_homework_intro", lang))
    await callback.message.answer(homework_text)


@router.callback_query(F.data == "course:review_no")
async def course_review_no_handler(callback: CallbackQuery, session):
    if await _block_if_course_disabled(callback, session):
        return

    user_repo = UserRepository(session)
    engine = CourseEngineService(session)

    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer()
        return

    lang = user.language if user.language else "ru"

    user, progress, lesson, current_error_key = await engine.get_current_lesson(callback.from_user.id)
    if current_error_key:
        await callback.answer()
        await callback.message.answer(t(current_error_key, lang))
        return

    if getattr(progress, "homework_status", None) != "completed":
        await callback.answer()
        await callback.message.answer(t("course_complete_homework_first", lang))
        return

    user, progress, lesson, next_lesson, error_key = await engine.complete_lesson_and_unlock_next(callback.from_user.id)
    if error_key:
        await callback.answer()
        await callback.message.answer(t(error_key, lang))
        return

    if not next_lesson:
        await callback.answer()
        await callback.message.answer(t("course_completed_title", lang))
        return

    text = format_intro(next_lesson, lang)

    await callback.answer()
    await callback.message.answer(t("course_skip_review_next_lesson", lang))
    await callback.message.answer(
        text,
        reply_markup=course_intro_keyboard(lang),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "course:progress")
async def course_progress_handler(callback: CallbackQuery, session):
    if await _block_if_course_disabled(callback, session):
        return

    user_repo = UserRepository(session)
    engine = CourseEngineService(session)

    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer()
        await callback.message.answer(t("access_start_first", "ru"))
        return

    lang = user.language if user.language else "ru"

    if user.status != "active":
        await callback.answer()
        await callback.message.answer(
            t("course_only_active_users", lang),
            reply_markup=payment_method_keyboard(lang),
            parse_mode="HTML",
        )
        return

    user, progress, lesson, error_key = await engine.get_current_lesson(callback.from_user.id)
    if error_key:
        await callback.answer()
        await callback.message.answer(t(error_key, lang))
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

    await callback.answer()
    await callback.message.answer(
        t("course_progress_full_text", lang,
          lessons=completed_count,
          vocab=summary["vocab"],
          dialogues=summary["dialogues"],
          days=days_studying,
          current=current_lesson_title),
        parse_mode="HTML",
    )



@router.callback_query(F.data == "course:review_last")
async def course_review_last_handler(callback: CallbackQuery, state: FSMContext, session):
    if await _block_if_course_disabled(callback, session):
        return

    user_repo = UserRepository(session)
    engine = CourseEngineService(session)

    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer()
        await callback.message.answer(t("access_start_first", "ru"))
        return

    lang = user.language if user.language else "ru"

    if user.status != "active":
        await callback.answer()
        await callback.message.answer(
            t("course_only_active_users", lang),
            reply_markup=payment_method_keyboard(lang),
            parse_mode="HTML",
        )
        return

    user.learning_mode = "course"
    user.voice_mode = "none"
    await state.update_data(pending_voice_transcript=None, pending_voice_message_id=None)
    await session.commit()

    user, progress, lesson, error_key = await engine.get_current_lesson(callback.from_user.id)
    if error_key:
        await callback.answer()
        await callback.message.answer(t(error_key, lang))
        return

    step = progress.current_step
    text = format_step(lesson, lang, step) or ""

    await callback.answer()
    await callback.message.answer(text, parse_mode="HTML")





@router.callback_query(F.data == "course:satisfied_yes")
async def course_satisfied_yes_handler(callback: CallbackQuery, session):
    if await _block_if_course_disabled(callback, session):
        return

    user_repo = UserRepository(session)
    engine = CourseEngineService(session)

    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer()
        await callback.message.answer(t("access_start_first", "ru"))
        return

    lang = user.language if user.language else "ru"

    user, progress, lesson, error_key = await engine.mark_satisfied_and_go_to_homework(callback.from_user.id)
    if error_key:
        await callback.answer()
        await callback.message.answer(t(error_key, lang))
        return

    await engine.progress_repo.set_waiting_for(progress, "homework_submission")
    await session.commit()

    homework_text = _format_homework_text(lang, lesson.homework_json)

    await callback.answer()
    await callback.message.answer(t("course_lesson_homework_intro", lang))
    await callback.message.answer(homework_text)


@router.callback_query(F.data == "course:satisfied_no")
async def course_satisfied_no_handler(callback: CallbackQuery, session):
    if await _block_if_course_disabled(callback, session):
        return

    user_repo = UserRepository(session)
    engine = CourseEngineService(session)

    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer()
        await callback.message.answer(t("access_start_first", "ru"))
        return

    lang = user.language if user.language else "ru"

    user, progress, lesson, error_key = await engine.mark_not_satisfied_and_stay(callback.from_user.id)
    if error_key:
        await callback.answer()
        await callback.message.answer(t(error_key, lang))
        return

    await callback.answer()
    await callback.message.answer(
        t("course_lesson_what_unclear", lang)
    )


@router.callback_query(F.data == "course:show_homework")
async def course_show_homework_handler(callback: CallbackQuery, session):
    if await _block_if_course_disabled(callback, session):
        return

    user_repo = UserRepository(session)
    engine = CourseEngineService(session)

    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer()
        await callback.message.answer(t("access_start_first", "ru"))
        return

    lang = user.language if user.language else "ru"

    user, progress, lesson, error_key = await engine.get_current_lesson(callback.from_user.id)
    if error_key:
        await callback.answer()
        await callback.message.answer(t(error_key, lang))
        return

    homework_text = _format_homework_text(lang, lesson.homework_json)

    if progress.current_step == "homework" and progress.homework_status != "completed":
        await engine.progress_repo.set_waiting_for(progress, "homework_submission")
        await session.commit()

    await callback.answer()
    await callback.message.answer(homework_text)


@router.callback_query(F.data == "course:homework_reread")
async def course_homework_reread_handler(callback: CallbackQuery, session):
    if await _block_if_course_disabled(callback, session):
        return

    user_repo = UserRepository(session)
    engine = CourseEngineService(session)

    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer()
        await callback.message.answer(t("access_start_first", "ru"))
        return

    lang = user.language if user.language else "ru"
    user, progress, lesson, error_key = await engine.get_current_lesson(callback.from_user.id)
    if error_key:
        await callback.answer()
        await callback.message.answer(t(error_key, lang))
        return

    await engine.progress_repo.set_current_lesson_and_step(
        progress=progress,
        lesson_id=lesson.id,
        step="intro",
        waiting_for="none",
    )
    await session.commit()

    await callback.answer()
    await callback.message.answer(t("course_reread_start_msg", lang))
    await callback.message.answer(
        format_intro(lesson, lang),
        reply_markup=course_intro_keyboard(lang),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "course:start_next_lesson")
async def course_start_next_lesson_handler(callback: CallbackQuery, session):
    if await _block_if_course_disabled(callback, session):
        return

    user_repo = UserRepository(session)
    engine = CourseEngineService(session)

    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer()
        await callback.message.answer(t("access_start_first", "ru"))
        return

    lang = user.language if user.language else "ru"

    user, progress, lesson, current_error_key = await engine.get_current_lesson(callback.from_user.id)
    if current_error_key:
        await callback.answer()
        await callback.message.answer(t(current_error_key, lang))
        return

    if progress.homework_status != "completed":
        can_skip_after_low_score = (
            getattr(progress, "current_step", None) == "homework"
            and getattr(progress, "waiting_for", None) == "homework_decision"
        )
        if can_skip_after_low_score:
            await engine.progress_repo.set_homework_status(progress, "completed")
        else:
            await callback.answer()
            await callback.message.answer(t("course_complete_homework_first", lang))
            return

    user, progress, lesson, next_lesson, error_key = await engine.complete_lesson_and_unlock_next(callback.from_user.id)
    if error_key:
        await callback.answer()
        await callback.message.answer(t(error_key, lang))
        return

    if not next_lesson:
        await callback.answer()
        await callback.message.answer(t("course_completed_title", lang))
        return

    await callback.answer()
    await run_course_entry_flow(
        session=session,
        telegram_id=callback.from_user.id,
        respond=callback.message.answer,
    )


def _keyboard_for_step(lang: str, step: str, lesson=None):
    """Har qanday step uchun to'g'ri klaviaturani qaytaradi (V1 + V2)."""
    from app.services.course_engine_service import is_v2_lesson as _is_v2
    v2 = lesson is not None and _is_v2(lesson)

    # V2 intro — "Davom etamiz" (vocab_1 ga o'tadi)
    if step == "intro" and v2:
        return course_next_step_keyboard(lang)
    # V2 vocab steps — audio + next
    if step in ("vocab_1", "vocab_2"):
        return course_vocab_v2_keyboard(lang)
    # V2 dialogue_N steps — audio + next
    if step.startswith("dialogue_"):
        try:
            n = int(step.split("_", 1)[1])
        except (ValueError, IndexError):
            n = 1
        return course_dialogue_n_keyboard(lang, n)
    # grammar — V2 da "Davom etamiz", V1 da "Exercisega o'tamiz"
    if step == "grammar" and v2:
        return course_next_step_keyboard(lang)
    # V1 steps
    if step == "intro":
        return course_intro_keyboard(lang)
    if step == "vocab":
        return course_vocab_keyboard(lang)
    if step == "dialogue":
        return course_dialogue_keyboard(lang)
    if step == "grammar":
        return course_grammar_keyboard(lang)
    # exercise, satisfaction_check, homework, completed — handled by get_course_keyboard_for_step
    return get_course_keyboard_for_step(lang, step)


def _static_course_missing_text(lang: str) -> str:
    messages = {
        "uz": "Bu bo'lim uchun tayyor kurs materiali topilmadi. Dars seed faylini tekshirish kerak.",
        "ru": "Для этого раздела не найден готовый материал курса. Нужно проверить seed-файл урока.",
        "tj": "Барои ин қисм маводи тайёри курс ёфт нашуд. Seed-файли дарсро санҷидан лозим.",
    }
    return messages.get(lang, messages["ru"])


def _v2_remap(step: str, lesson) -> str:
    """V2 dars uchun V1 step nomini V2 ekvivalentiga o'zgartiradi."""
    from app.services.course_engine_service import is_v2_lesson as _is_v2
    if not _is_v2(lesson):
        return step
    mapping = {"vocab": "vocab_1", "dialogue": "dialogue_1"}
    return mapping.get(step, step)


async def _send_step(respond, user, lesson, step: str, lang: str, session):
    """Step kontentini format qilib yuboradi (V1 va V2 uchun)."""
    text = format_step(lesson, lang, step)
    if text is not None:
        keyboard = _keyboard_for_step(lang, step, lesson)
        await respond(text, reply_markup=keyboard, parse_mode="HTML")
    else:
        keyboard = _keyboard_for_step(lang, step, lesson)
        await respond(_static_course_missing_text(lang), reply_markup=keyboard, parse_mode="HTML")


async def _go_to_step(callback, session, step: str):
    if await _block_if_course_disabled(callback, session):
        return

    user_repo = UserRepository(session)
    engine = CourseEngineService(session)

    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer()
        return

    lang = user.language if user.language else "ru"
    user, progress, lesson, error_key = await engine.get_current_lesson(callback.from_user.id)
    if error_key:
        await callback.answer()
        await callback.message.answer(t(error_key, lang))
        return

    # V2 dars uchun V1 step nomlarini V2 ga remap qilamiz
    step = _v2_remap(step, lesson)

    waiting_for_val = "exercise_answer" if step == "exercise" else "none"
    await engine.progress_repo.set_current_lesson_and_step(
        progress=progress,
        lesson_id=lesson.id,
        step=step,
        waiting_for=waiting_for_val,
    )
    await session.commit()

    await callback.answer()
    await _send_step(callback.message.answer, user, lesson, step, lang, session)


@router.callback_query(F.data == "course:go_vocab")
async def course_go_vocab(callback: CallbackQuery, session):
    await _go_to_step(callback, session, "vocab")

@router.callback_query(F.data == "course:go_dialogue")
async def course_go_dialogue(callback: CallbackQuery, session):
    await _go_to_step(callback, session, "dialogue")

@router.callback_query(F.data == "course:go_grammar")
async def course_go_grammar(callback: CallbackQuery, session):
    await _go_to_step(callback, session, "grammar")

@router.callback_query(F.data == "course:go_exercise")
async def course_go_exercise(callback: CallbackQuery, session):
    await _go_to_step(callback, session, "exercise")


@router.callback_query(F.data == "course:go_next_step")
async def course_go_next_step(callback: CallbackQuery, session):
    """V2 darslar uchun universal 'Davom etamiz' tugmasi."""
    if await _block_if_course_disabled(callback, session):
        return

    user_repo = UserRepository(session)
    engine = CourseEngineService(session)

    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer()
        return

    lang = user.language if user.language else "ru"

    user, progress, lesson, error_key = await engine.go_to_next_step(callback.from_user.id)
    if error_key:
        await callback.answer()
        await callback.message.answer(t(error_key, lang))
        return

    step = progress.current_step

    # Exercise stepiga o'tganda waiting_for ni yangilaymiz
    if step == "exercise":
        await engine.progress_repo.set_waiting_for(progress, "exercise_answer")
        await session.commit()

    await callback.answer()
    await _send_step(callback.message.answer, user, lesson, step, lang, session)

@router.callback_query(F.data == "course:repeat_step")
async def course_repeat_step(callback: CallbackQuery, session):
    if await _block_if_course_disabled(callback, session):
        return

    user_repo = UserRepository(session)
    engine = CourseEngineService(session)

    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer()
        return

    lang = user.language if user.language else "ru"
    user, progress, lesson, error_key = await engine.get_current_lesson(callback.from_user.id)
    if error_key:
        await callback.answer()
        await callback.message.answer(t(error_key, lang))
        return

    step = progress.current_step
    await callback.answer()
    await _send_step(callback.message.answer, user, lesson, step, lang, session)


async def _finish_study_time_flow(callback: CallbackQuery, session, saved_text: str):
    """Vaqt saqlangandan yoki o'tkazib yuborgandan keyin umumiy tugash oqimi."""
    engine = CourseEngineService(session)
    user_repo = UserRepository(session)

    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    lang = (user.language if user and user.language else "ru")

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(saved_text, parse_mode="HTML")

    _, progress, lesson, err = await engine.get_current_lesson(callback.from_user.id)
    if err or not lesson:
        return

    if getattr(progress, "waiting_for", None) == "review_choice":
        await callback.message.answer(
            t("course_review_choice", lang),
            reply_markup=review_choice_keyboard(lang),
        )
    else:
        await send_course_completion_prompt(
            respond=callback.message.answer,
            engine=engine,
            lesson=lesson,
            lang=lang,
        )


@router.callback_query(F.data.startswith("course:study_time:"))
async def course_set_study_time_handler(callback: CallbackQuery, session):
    if await _block_if_course_disabled(callback, session):
        return

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer()
        return

    lang = user.language if user.language else "ru"
    time_str = callback.data.split(":")[-2] + ":" + callback.data.split(":")[-1]  # "09:00"

    # "09:00" → datetime bugun uchun
    try:
        h, m = int(time_str.split(":")[0]), int(time_str.split(":")[1])
        now = datetime.now(timezone.utc)
        next_study_at = now.replace(hour=h, minute=m, second=0, microsecond=0)
        if next_study_at <= now:
            # Agar vaqt o'tib ketgan bo'lsa — ertaga
            from datetime import timedelta
            next_study_at = next_study_at + timedelta(days=1)
    except Exception:
        await callback.answer()
        return

    engine = CourseEngineService(session)
    await engine.set_next_study_at(callback.from_user.id, next_study_at)

    saved_labels = {
        "uz": f"✅ Keyingi dars vaqti saqlandi: <b>{time_str}</b>",
        "ru": f"✅ Время следующего урока сохранено: <b>{time_str}</b>",
        "tj": f"✅ Вақти дарси навбатӣ сабт шуд: <b>{time_str}</b>",
    }
    await callback.answer(f"✅ {time_str}")
    await _finish_study_time_flow(callback, session, saved_labels.get(lang, saved_labels["ru"]))


@router.callback_query(F.data == "course:skip_next_study_time")
async def course_skip_next_study_time_handler(callback: CallbackQuery, session):
    if await _block_if_course_disabled(callback, session):
        return

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer()
        await callback.message.answer(t("access_start_first", "ru"))
        return

    lang = user.language if user.language else "ru"

    engine = CourseEngineService(session)
    await engine.set_next_study_at(callback.from_user.id, None)

    await callback.answer()
    await _finish_study_time_flow(callback, session, t("course_next_study_time_skipped", lang))


_AUDIO_UNAVAILABLE = {
    "uz": "🔇 Audio hozircha mavjud emas",
    "ru": "🔇 Аудио пока недоступно",
    "tj": "🔇 Аудио ҳоло дастрас нест",
}

# ─── Audio fayl joylash qoidasi ───────────────────────────────────────────────
# Birinchi navbatda dars-spesifik path qidiriladi, keyin level-wide:
#   app/static/audio/{level}/lesson_{NN}/{name}.ogg   ← birinchi
#   app/static/audio/{level}/{name}.ogg               ← fallback
#
# Misol: hsk2/lesson_03/dialogue_1.ogg  yoki  hsk2/dialogue_1.ogg
# ─────────────────────────────────────────────────────────────────────────────
from app.repositories.course_audio_repo import CourseAudioRepository


async def _send_audio_file(callback: CallbackQuery, session, audio_type: str):
    """DB dan file_id topib yuboradi, yo'q bo'lsa foydalanuvchi tilida xabar ko'rsatadi."""
    user_repo = UserRepository(session)
    engine = CourseEngineService(session)

    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    lang = (user.language if user and user.language else "ru")
    unavailable = _AUDIO_UNAVAILABLE.get(lang, _AUDIO_UNAVAILABLE["ru"])

    if not user:
        await callback.answer(unavailable, show_alert=True)
        return

    user, progress, lesson, error_key = await engine.get_current_lesson(callback.from_user.id)
    if error_key or not lesson:
        await callback.answer(unavailable, show_alert=True)
        return

    level = (lesson.level or "hsk1").lower()
    order = lesson.lesson_order or 1

    audio_repo = CourseAudioRepository(session)
    file_id = await audio_repo.get(level=level, lesson_order=order, audio_type=audio_type)

    # Fallback: dialogue_2/3/4 topilmasa — dialogue_1 ni ishlatamiz
    if not file_id and audio_type.startswith("dialogue_") and audio_type != "dialogue_1":
        file_id = await audio_repo.get(level=level, lesson_order=order, audio_type="dialogue_1")

    await callback.answer()
    if file_id:
        await callback.message.answer_voice(file_id)
    else:
        await callback.message.answer(unavailable)


@router.callback_query(F.data == "course:audio_vocab")
async def course_audio_vocab_handler(callback: CallbackQuery, session):
    await _send_audio_file(callback, session, "vocab")


@router.callback_query(F.data.startswith("course:audio_dialogue:"))
async def course_audio_dialogue_n_handler(callback: CallbackQuery, session):
    try:
        n = int(callback.data.split(":")[-1])
    except (ValueError, IndexError):
        n = 1
    await _send_audio_file(callback, session, f"dialogue_{n}")


# V1 eski handler (eski callback_data uchun)
@router.callback_query(F.data == "course:audio_dialogue")
async def course_audio_dialogue_handler(callback: CallbackQuery, session):
    await _send_audio_file(callback, session, "dialogue_1")


@router.callback_query(F.data.startswith("course:set_tz:"))
async def course_set_timezone_handler(callback: CallbackQuery, session):
    user_repo = UserRepository(session)
    engine = CourseEngineService(session)

    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer()
        return

    lang = user.language if user.language else "ru"

    try:
        tz_offset = int(callback.data.split(":")[-1])
    except (ValueError, IndexError):
        await callback.answer()
        return

    progress = await engine.progress_repo.get_by_user_id(user.id)
    if not progress or not progress.reminder_enabled or not progress.reminder_time:
        await callback.answer()
        return

    progress.reminder_tz_offset = tz_offset
    await session.commit()

    tz_labels = {3: "UTC+3 🇷🇺 Москва", 5: "UTC+5 🇺🇿🇹🇯 Тошкент/Душанбе", 8: "UTC+8 🇨🇳 Пекин"}
    tz_label = tz_labels.get(tz_offset, f"UTC+{tz_offset}")
    time_str = progress.reminder_time.strftime("%H:%M")

    await callback.answer()
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(
        t("course_reminder_tz_saved", lang, time=time_str, tz=tz_label),
        reply_markup=course_menu_keyboard(lang) if user.learning_mode == "course" else main_menu_keyboard(lang),
        parse_mode="HTML",
    )
