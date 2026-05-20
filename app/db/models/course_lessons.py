from datetime import datetime, timezone

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CourseLesson(Base):
    __tablename__ = "course_lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    level: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    lesson_order: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    lesson_code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    goal: Mapped[str] = mapped_column(Text, nullable=False, default="")
    intro_text: Mapped[str] = mapped_column(Text, nullable=False, default="")

    vocabulary_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    dialogue_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    grammar_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    exercise_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    answers_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    homework_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    review_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
