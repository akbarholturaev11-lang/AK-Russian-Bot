import json
import re
from typing import Optional

from app.repositories.user_repo import UserRepository
from app.repositories.course_lesson_repo import CourseLessonRepository
from app.repositories.course_progress_repo import CourseProgressRepository
from app.repositories.course_attempt_repo import CourseAttemptRepository
from app.services.course_tutor_service import CourseTutorService


# ─── V1: eski format (HSK1 va grammar_notes si yo'q darslar) ───────────────
COURSE_STEP_ORDER_V1 = [
    "intro",
    "vocab",
    "dialogue",
    "grammar",
    "exercise",
    "satisfaction_check",
    "homework",
    "completed",
]

# ─── V2: yangi format (grammar_notes inline, vocab/dialog bo'lingan) ─────────
COURSE_STEP_ORDER_V2_BASE = [
    "intro",
    "vocab_1",
    "vocab_2",          # bo'sh bo'lsa o'tkazib yuboriladi
    "dialogue_1",
    "dialogue_2",       # bo'sh bo'lsa o'tkazib yuboriladi
    "dialogue_3",       # bo'sh bo'lsa o'tkazib yuboriladi
    "dialogue_4",       # bo'sh bo'lsa o'tkazib yuboriladi
    "grammar",          # bo'sh bo'lsa o'tkazib yuboriladi
    "exercise",
    "satisfaction_check",
    "homework",
    "completed",
]

# Backward compat alias
COURSE_STEP_ORDER = COURSE_STEP_ORDER_V1


def _parse_json(value, default):
    if value is None or value == "":
        return default
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except Exception:
        return default


def _normalize_answer_text(value: str) -> str:
    text = (value or "").lower()
    return re.sub(r"[\s,.;:，。；：、!！?？'\"`]+", "", text)


def _answer_options(answer, lang: str) -> list[str]:
    if isinstance(answer, dict):
        values = [
            answer.get(lang),
            answer.get("answer"),
            answer.get("zh"),
            answer.get("uz") if lang == "uz" else None,
            answer.get("ru") if lang == "ru" else None,
            answer.get("tj") if lang == "tj" else None,
        ]
    else:
        values = [str(answer)]

    options = []
    for value in values:
        if not value:
            continue
        text = str(value)
        options.append(text)
        options.extend(part.strip() for part in text.split("/") if part.strip())
    return list(dict.fromkeys(options))


def _flatten_expected_answers(answers_json, lang: str) -> list[list[str]]:
    answers = _parse_json(answers_json, [])
    expected = []
    if not isinstance(answers, list):
        return expected

    for group in answers:
        if not isinstance(group, dict):
            continue
        for answer in group.get("answers", []):
            options = _answer_options(answer, lang)
            if options:
                expected.append(options)
    return expected


def is_v2_lesson(lesson) -> bool:
    """V2 formatmi? dialogue_json ichida block_no bo'lsa V2 (barcha mavjud darslar)."""
    if lesson is None:
        return False
    dialogues = _parse_json(getattr(lesson, "dialogue_json", None), [])
    if not isinstance(dialogues, list) or not dialogues:
        return False
    return any(isinstance(d, dict) and d.get("block_no") for d in dialogues)


def get_step_order(lesson) -> list:
    """Darsga mos step tartibini qaytaradi."""
    if not is_v2_lesson(lesson):
        return COURSE_STEP_ORDER_V1

    vocab = _parse_json(getattr(lesson, "vocabulary_json", None), [])
    dialogues = _parse_json(getattr(lesson, "dialogue_json", None), [])

    steps = ["intro", "vocab_1"]
    if len(vocab) > 8:
        steps.append("vocab_2")

    for i in range(1, min(len(dialogues) + 1, 5)):
        steps.append(f"dialogue_{i}")

    # grammar_json bo'sh bo'lmasa — grammar stepini qo'shamiz
    grammar = _parse_json(getattr(lesson, "grammar_json", None), [])
    if grammar:
        steps.append("grammar")

    exercise = _parse_json(getattr(lesson, "exercise_json", None), [])
    if exercise:
        steps.append("exercise")

    steps += ["satisfaction_check", "homework", "completed"]
    return steps


class CourseEngineService:
    def __init__(self, session):
        self.session = session
        self.user_repo = UserRepository(session)
        self.lesson_repo = CourseLessonRepository(session)
        self.progress_repo = CourseProgressRepository(session)
        self.attempt_repo = CourseAttemptRepository(session)

    def _allowed_level_candidates(self, level: str | None) -> tuple[str, ...]:
        normalized = (level or "").strip().lower()
        fallback_map = {
            "beginner": ("hsk1",),
            "hsk1": ("hsk1",),
            "hsk2": ("hsk2", "hsk1"),
            "hsk3": ("hsk3", "hsk2", "hsk1"),
            "hsk4": ("hsk4", "hsk3", "hsk2", "hsk1"),
        }
        return fallback_map.get(normalized, ("hsk1",))

    async def get_or_create_progress(self, telegram_id: int):
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            return None, None, "access_start_first"

        progress = await self.progress_repo.get_by_user_id(user.id)
        if progress:
            return user, progress, ""

        progress = await self.progress_repo.create(
            user_id=user.id,
            level=user.level,
            current_lesson_id=None,
            current_step="intro",
            waiting_for="none",
        )
        await self.session.commit()
        return user, progress, ""

    async def get_current_lesson(self, telegram_id: int):
        user, progress, error_key = await self.get_or_create_progress(telegram_id)
        if error_key:
            return None, None, None, error_key

        if not progress or not progress.current_lesson_id:
            return user, progress, None, "course_no_lesson_found"

        lesson = await self.lesson_repo.get_by_id(progress.current_lesson_id)
        if not lesson:
            return user, progress, None, "course_no_lesson_found"

        return user, progress, lesson, ""

    async def continue_course(self, telegram_id: int):
        user, progress, lesson, error_key = await self.get_current_lesson(telegram_id)
        if error_key:
            return user, progress, lesson, error_key

        if not progress or not lesson:
            return user, progress, lesson, "course_no_lesson_selected"

        waiting_for = getattr(progress, "waiting_for", None) or "none"
        homework_status = getattr(progress, "homework_status", None) or "none"
        current_step = getattr(progress, "current_step", None) or "intro"

        if waiting_for in {
            "satisfaction_answer",
            "satisfaction_reason",
            "homework_submission",
            "next_study_time",
            "review_choice",
        }:
            return user, progress, lesson, ""

        if current_step == "completed" and homework_status == "completed":
            return user, progress, lesson, ""

        return user, progress, lesson, ""

    async def pick_lesson(self, telegram_id: int, lesson_id: int):
        user, progress, error_key = await self.get_or_create_progress(telegram_id)
        if error_key:
            return None, None, None, error_key

        lesson = await self.lesson_repo.get_by_id(lesson_id)
        if not lesson:
            return user, progress, None, "course_no_lesson_found"

        if lesson.level not in self._allowed_level_candidates(user.level):
            return user, progress, None, "course_lesson_not_unlocked"

        await self.progress_repo.set_current_lesson_and_step(
            progress=progress,
            lesson_id=lesson.id,
            step="intro",
            waiting_for="none",
        )
        await self.session.commit()

        return user, progress, lesson, ""

    def get_next_step_name(self, current_step: str, lesson=None) -> str:
        """Lesson berilsa, unga mos step tartibidan keyingisini qaytaradi."""
        order = get_step_order(lesson) if lesson is not None else COURSE_STEP_ORDER_V1

        if current_step not in order:
            for candidate in COURSE_STEP_ORDER_V2_BASE[
                COURSE_STEP_ORDER_V2_BASE.index(current_step) + 1:
            ] if current_step in COURSE_STEP_ORDER_V2_BASE else []:
                if candidate in order:
                    return candidate
            return "intro"

        idx = order.index(current_step)
        if idx >= len(order) - 1:
            return "completed"

        return order[idx + 1]

    def get_prev_step_name(self, current_step: str, lesson=None) -> str:
        order = get_step_order(lesson) if lesson is not None else COURSE_STEP_ORDER_V1

        if current_step not in order:
            return "intro"

        idx = order.index(current_step)
        if idx <= 0:
            return "intro"

        return order[idx - 1]

    async def go_to_next_step(self, telegram_id: int):
        user, progress, lesson, error_key = await self.get_current_lesson(telegram_id)
        if error_key:
            return None, None, None, error_key

        next_step = self.get_next_step_name(progress.current_step, lesson)
        await self.progress_repo.set_current_lesson_and_step(
            progress=progress,
            lesson_id=progress.current_lesson_id,
            step=next_step,
            waiting_for="none",
        )
        await self.session.commit()

        return user, progress, lesson, ""

    async def go_to_prev_step(self, telegram_id: int):
        user, progress, lesson, error_key = await self.get_current_lesson(telegram_id)
        if error_key:
            return None, None, None, error_key

        prev_step = self.get_prev_step_name(progress.current_step, lesson)
        await self.progress_repo.set_current_lesson_and_step(
            progress=progress,
            lesson_id=progress.current_lesson_id,
            step=prev_step,
            waiting_for="none",
        )
        await self.session.commit()

        return user, progress, lesson, ""

    async def mark_quiz_passed_and_go_to_satisfaction(self, telegram_id: int):
        user, progress, lesson, error_key = await self.get_current_lesson(telegram_id)
        if error_key:
            return None, None, None, error_key

        await self.progress_repo.set_current_lesson_and_step(
            progress=progress,
            lesson_id=progress.current_lesson_id,
            step="satisfaction_check",
            waiting_for="satisfaction_answer",
        )
        await self.session.commit()

        return user, progress, lesson, ""

    async def mark_satisfied_and_go_to_homework(self, telegram_id: int):
        user, progress, lesson, error_key = await self.get_current_lesson(telegram_id)
        if error_key:
            return None, None, None, error_key

        await self.progress_repo.set_current_lesson_and_step(
            progress=progress,
            lesson_id=lesson.id,
            step="homework",
            waiting_for="homework_submission",
        )
        await self.progress_repo.set_homework_status(progress, "assigned")
        await self.session.commit()

        return user, progress, lesson, ""

    async def mark_not_satisfied_and_stay(self, telegram_id: int):
        user, progress, lesson, error_key = await self.get_current_lesson(telegram_id)
        if error_key:
            return None, None, None, error_key

        await self.progress_repo.set_current_lesson_and_step(
            progress=progress,
            lesson_id=progress.current_lesson_id,
            step="satisfaction_check",
            waiting_for="satisfaction_reason",
        )
        await self.session.commit()

        return user, progress, lesson, ""

    async def mark_exercise_submitted(self, telegram_id: int, submission_text: str):
        user, progress, lesson, error_key = await self.get_current_lesson(telegram_id)
        if error_key:
            return {"error_key": error_key}

        submission_text = (submission_text or "").strip()
        if not submission_text:
            return {"error_key": "course_homework_empty"}

        lang = user.language if getattr(user, "language", None) else "ru"
        expected = _flatten_expected_answers(getattr(lesson, "answers_json", None), lang)
        normalized_submission = _normalize_answer_text(submission_text)

        correct = 0
        expected_labels = []
        for options in expected:
            expected_labels.append(options[0])
            normalized_options = [_normalize_answer_text(option) for option in options]
            if any(option and option in normalized_submission for option in normalized_options):
                correct += 1

        total = len(expected)
        score = int((correct / total) * 100) if total else 100
        passed = correct >= max(1, (total + 1) // 2) if total else True

        await self.attempt_repo.create(
            user_id=user.id,
            lesson_id=lesson.id,
            attempt_type="exercise",
            step_name="exercise",
            score=score,
            passed=passed,
            answers_json=json.dumps(
                {
                    "submission_text": submission_text,
                    "correct": correct,
                    "total": total,
                    "expected": expected_labels,
                },
                ensure_ascii=False,
            ),
            ai_feedback=None,
        )

        await self.progress_repo.set_current_lesson_and_step(
            progress=progress,
            lesson_id=progress.current_lesson_id,
            step="satisfaction_check",
            waiting_for="satisfaction_answer",
        )
        await self.session.commit()

        return {
            "error_key": None,
            "correct": correct,
            "total": total,
            "score": score,
            "passed": passed,
            "expected": expected_labels,
        }

    async def mark_homework_submitted(self, telegram_id: int, submission_text: str):
        user, progress, lesson, error_key = await self.get_current_lesson(telegram_id)
        if error_key:
            return {"error_key": error_key}

        submission_text = (submission_text or "").strip()
        if not submission_text:
            return {"error_key": "course_homework_empty"}

        user_lang = user.language if getattr(user, "language", None) else "ru"
        user_level = user.level if getattr(user, "level", None) else "hsk1"

        tutor = CourseTutorService()
        evaluation = await tutor.evaluate_homework(
            user_language=user_lang,
            user_level=user_level,
            lesson=lesson,
            submission_text=submission_text,
        )

        score = evaluation.get("score", 0)
        passed = evaluation.get("passed", False)
        feedback_text = evaluation.get("feedback_text", "")

        await self.attempt_repo.create(
            user_id=user.id,
            lesson_id=lesson.id,
            attempt_type="homework",
            step_name="homework",
            score=score,
            passed=passed,
            answers_json=json.dumps({"submission_text": submission_text}, ensure_ascii=False),
            ai_feedback=feedback_text,
        )

        if passed:
            await self.progress_repo.set_homework_status(progress, "completed")
            await self.progress_repo.set_waiting_for(progress, "next_study_time")
        else:
            await self.progress_repo.set_homework_status(progress, "assigned")
            await self.progress_repo.set_current_lesson_and_step(
                progress=progress,
                lesson_id=lesson.id,
                step="homework",
                waiting_for="homework_decision",
            )
        await self.session.commit()

        return {
            "error_key": None,
            "feedback_text": feedback_text,
            "ask_next_study_time": passed,
            "score": score,
            "passed": passed,
            "ai_result": tutor.last_ai_result,
            "budget_cooldown_started": False,
            "budget_message_key": "",
        }

    async def set_next_study_at(self, telegram_id: int, next_study_at):
        user, progress, lesson, error_key = await self.get_current_lesson(telegram_id)
        if error_key:
            return None, None, None, error_key

        next_lesson = await self.lesson_repo.get_next_lesson(
            level=lesson.level,
            lesson_order=lesson.lesson_order,
        )

        await self.progress_repo.set_next_study_at(progress, next_study_at)
        await self.progress_repo.set_current_lesson_and_step(
            progress=progress,
            lesson_id=lesson.id,
            step="completed",
            waiting_for="review_choice" if next_lesson else "none",
        )
        await self.session.commit()

        return user, progress, lesson, ""

    async def activate_next_lesson(self, telegram_id: int):
        user, progress, lesson, error_key = await self.get_current_lesson(telegram_id)
        if error_key:
            return None, None, None, error_key

        next_lesson = await self.lesson_repo.get_next_lesson(
            level=lesson.level,
            lesson_order=lesson.lesson_order,
        )
        if not next_lesson:
            return user, progress, None, "course_no_next_lesson"

        await self.progress_repo.mark_lesson_completed(progress)
        await self.progress_repo.set_current_lesson_and_step(
            progress=progress,
            lesson_id=next_lesson.id,
            step="intro",
            waiting_for="none",
        )
        await self.progress_repo.set_homework_status(progress, "none")
        await self.session.commit()

        return user, progress, next_lesson, ""

    async def clear_review_prompt(self, telegram_id: int):
        user, progress, lesson, error_key = await self.get_current_lesson(telegram_id)
        if error_key:
            return None, None, None, error_key

        await self.progress_repo.set_review_prompt(
            progress=progress,
            needs_review_prompt=False,
        )
        await self.session.commit()

        return user, progress, lesson, ""

    async def complete_lesson_and_unlock_next(self, telegram_id: int):
        user, progress, lesson, error_key = await self.get_current_lesson(telegram_id)
        if error_key:
            return None, None, None, None, error_key

        current_order = lesson.lesson_order
        next_lesson = await self.lesson_repo.get_next_lesson(
            level=lesson.level,
            lesson_order=current_order,
        )

        await self.progress_repo.mark_lesson_completed(progress)

        await self.progress_repo.set_current_lesson_and_step(
            progress=progress,
            lesson_id=next_lesson.id if next_lesson else progress.current_lesson_id,
            step="intro" if next_lesson else "completed",
            waiting_for="none",
        )

        if next_lesson:
            await self.progress_repo.set_homework_status(progress, "none")

        await self.session.commit()

        return user, progress, lesson, next_lesson, ""
