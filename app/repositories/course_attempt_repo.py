from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.course_attempts import CourseAttempt


class CourseAttemptRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: int,
        lesson_id: int,
        score: int,
        passed: bool,
        answers_json: str,
        attempt_type: str = "quiz",
        step_name: Optional[str] = None,
        ai_feedback: Optional[str] = None,
    ) -> CourseAttempt:
        attempt_no = await self.get_next_attempt_no(user_id, lesson_id, attempt_type)

        attempt = CourseAttempt(
            user_id=user_id,
            lesson_id=lesson_id,
            attempt_no=attempt_no,
            attempt_type=attempt_type,
            step_name=step_name,
            score=score,
            passed=passed,
            answers_json=answers_json,
            ai_feedback=ai_feedback,
        )
        self.session.add(attempt)
        await self.session.flush()
        return attempt

    async def get_next_attempt_no(
        self,
        user_id: int,
        lesson_id: int,
        attempt_type: str = "quiz",
    ) -> int:
        result = await self.session.execute(
            select(func.max(CourseAttempt.attempt_no))
            .where(CourseAttempt.user_id == user_id)
            .where(CourseAttempt.lesson_id == lesson_id)
            .where(CourseAttempt.attempt_type == attempt_type)
        )
        max_no = result.scalar_one_or_none()
        return (max_no or 0) + 1

    async def get_last_attempt(
        self,
        user_id: int,
        lesson_id: int,
        attempt_type: Optional[str] = None,
    ) -> Optional[CourseAttempt]:
        query = (
            select(CourseAttempt)
            .where(CourseAttempt.user_id == user_id)
            .where(CourseAttempt.lesson_id == lesson_id)
        )

        if attempt_type is not None:
            query = query.where(CourseAttempt.attempt_type == attempt_type)

        result = await self.session.execute(
            query.order_by(CourseAttempt.attempt_no.desc()).limit(1)
        )
        return result.scalar_one_or_none()

    async def list_by_user_and_lesson(
        self,
        user_id: int,
        lesson_id: int,
        attempt_type: Optional[str] = None,
    ) -> List[CourseAttempt]:
        query = (
            select(CourseAttempt)
            .where(CourseAttempt.user_id == user_id)
            .where(CourseAttempt.lesson_id == lesson_id)
        )

        if attempt_type is not None:
            query = query.where(CourseAttempt.attempt_type == attempt_type)

        result = await self.session.execute(
            query.order_by(CourseAttempt.attempt_no.asc())
        )
        return list(result.scalars().all())
