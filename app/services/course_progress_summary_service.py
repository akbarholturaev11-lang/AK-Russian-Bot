import json
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.course_lessons import CourseLesson
from app.db.models.course_progress import CourseProgress


class CourseProgressSummaryService:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _level_candidates(level: str | None) -> tuple[str, ...]:
        normalized = (level or "").strip().lower()
        fallback_map = {
            "beginner": ("hsk1",),
            "hsk1": ("hsk1",),
            "hsk2": ("hsk2", "hsk1"),
            "hsk3": ("hsk3", "hsk2", "hsk1"),
            "hsk4": ("hsk4", "hsk3", "hsk2", "hsk1"),
        }
        return fallback_map.get(normalized, ("hsk1",))

    @staticmethod
    def _count_json_items(raw) -> int:
        if not raw:
            return 0
        try:
            data = json.loads(raw) if isinstance(raw, str) else raw
        except Exception:
            return 0

        if isinstance(data, list):
            return len(data)
        if isinstance(data, dict):
            return 1
        return 0

    async def summarize_completed_range(
        self,
        progress: CourseProgress,
        *,
        start_after: int = 0,
        end_at: Optional[int] = None,
    ) -> dict:
        completed_count = getattr(progress, "completed_lessons_count", 0) or 0
        end_order = completed_count if end_at is None else min(end_at, completed_count)
        start_order = max(0, start_after or 0)

        if end_order <= start_order:
            return {"lessons": 0, "vocab": 0, "dialogues": 0}

        lessons = []
        for level in self._level_candidates(progress.level):
            result = await self.session.execute(
                select(CourseLesson)
                .where(CourseLesson.level == level)
                .where(CourseLesson.is_active.is_(True))
                .where(CourseLesson.lesson_order > start_order)
                .where(CourseLesson.lesson_order <= end_order)
                .order_by(CourseLesson.lesson_order.asc())
            )
            lessons = list(result.scalars().all())
            if lessons:
                break

        return {
            "lessons": len(lessons),
            "vocab": sum(self._count_json_items(lesson.vocabulary_json) for lesson in lessons),
            "dialogues": sum(self._count_json_items(lesson.dialogue_json) for lesson in lessons),
        }

    async def summarize_last_completed_lesson(self, progress: CourseProgress) -> dict:
        lesson = None
        last_lesson_id = getattr(progress, "last_completed_lesson_id", None)

        if last_lesson_id:
            lesson = await self.session.get(CourseLesson, last_lesson_id)

        if lesson is None:
            completed_count = getattr(progress, "completed_lessons_count", 0) or 0
            if completed_count > 0:
                for level in self._level_candidates(progress.level):
                    result = await self.session.execute(
                        select(CourseLesson)
                        .where(CourseLesson.level == level)
                        .where(CourseLesson.is_active.is_(True))
                        .where(CourseLesson.lesson_order == completed_count)
                        .limit(1)
                    )
                    lesson = result.scalar_one_or_none()
                    if lesson:
                        break

        if lesson is None:
            return {"vocab": 0, "dialogues": 0}

        return {
            "vocab": self._count_json_items(lesson.vocabulary_json),
            "dialogues": self._count_json_items(lesson.dialogue_json),
        }
