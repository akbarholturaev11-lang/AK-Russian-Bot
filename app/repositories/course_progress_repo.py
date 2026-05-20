from datetime import datetime, timezone, time
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.course_progress import CourseProgress


class CourseProgressRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: int) -> Optional[CourseProgress]:
        result = await self.session.execute(
            select(CourseProgress).where(CourseProgress.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        user_id: int,
        level: str,
        current_lesson_id: Optional[int],
        current_step: str = "intro",
        waiting_for: str = "none",
    ) -> CourseProgress:
        progress = CourseProgress(
            user_id=user_id,
            level=level,
            current_lesson_id=current_lesson_id,
            current_step=current_step,
            waiting_for=waiting_for,
            completed_lessons_count=0,
            homework_status="none",
            needs_review_prompt=False,
            last_opened_at=datetime.now(timezone.utc),
        )
        self.session.add(progress)
        await self.session.flush()
        return progress

    async def set_current_lesson_and_step(
        self,
        progress: CourseProgress,
        lesson_id: Optional[int],
        step: str,
        waiting_for: str = "none",
    ) -> None:
        progress.current_lesson_id = lesson_id
        progress.current_step = step
        progress.waiting_for = waiting_for
        progress.last_opened_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def set_waiting_for(
        self,
        progress: CourseProgress,
        waiting_for: str,
    ) -> None:
        progress.waiting_for = waiting_for
        progress.last_opened_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def set_homework_status(
        self,
        progress: CourseProgress,
        homework_status: str,
    ) -> None:
        progress.homework_status = homework_status
        progress.last_opened_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def set_review_prompt(
        self,
        progress: CourseProgress,
        needs_review_prompt: bool,
        last_completed_lesson_id: Optional[int] = None,
    ) -> None:
        progress.needs_review_prompt = needs_review_prompt
        if last_completed_lesson_id is not None:
            progress.last_completed_lesson_id = last_completed_lesson_id
        progress.last_opened_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def set_next_study_at(
        self,
        progress: CourseProgress,
        next_study_at: Optional[datetime],
    ) -> None:
        progress.next_study_at = next_study_at
        progress.last_opened_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def mark_lesson_completed(
        self,
        progress: CourseProgress,
    ) -> None:
        progress.completed_lessons_count += 1
        progress.current_step = "completed"
        progress.waiting_for = "none"
        progress.homework_status = "completed"
        progress.last_completed_at = datetime.now(timezone.utc)
        progress.last_completed_lesson_id = progress.current_lesson_id
        progress.needs_review_prompt = True
        await self.session.flush()

    async def set_reminder(
        self,
        progress: CourseProgress,
        enabled: bool,
        reminder_time: Optional[time],
    ) -> None:
        progress.reminder_enabled = enabled
        progress.reminder_time = reminder_time
        progress.last_opened_at = datetime.now(timezone.utc)
        await self.session.flush()
