from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.course_lessons import CourseLesson


class CourseLessonRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, lesson_id: int) -> Optional[CourseLesson]:
        result = await self.session.execute(
            select(CourseLesson).where(CourseLesson.id == lesson_id)
        )
        return result.scalar_one_or_none()

    async def get_first_by_level(self, level: str) -> Optional[CourseLesson]:
        result = await self.session.execute(
            select(CourseLesson)
            .where(CourseLesson.level == level)
            .where(CourseLesson.is_active.is_(True))
            .order_by(CourseLesson.lesson_order.asc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_next_lesson(self, level: str, lesson_order: int) -> Optional[CourseLesson]:
        result = await self.session.execute(
            select(CourseLesson)
            .where(CourseLesson.level == level)
            .where(CourseLesson.is_active.is_(True))
            .where(CourseLesson.lesson_order > lesson_order)
            .order_by(CourseLesson.lesson_order.asc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def list_by_level(self, level: str) -> List[CourseLesson]:
        result = await self.session.execute(
            select(CourseLesson)
            .where(CourseLesson.level == level)
            .where(CourseLesson.is_active.is_(True))
            .order_by(CourseLesson.lesson_order.asc())
        )
        return list(result.scalars().all())
