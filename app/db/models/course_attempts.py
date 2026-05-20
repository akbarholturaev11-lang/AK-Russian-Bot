from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CourseAttempt(Base):
    __tablename__ = "course_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    lesson_id: Mapped[int] = mapped_column(
        ForeignKey("course_lessons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    attempt_no: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    attempt_type: Mapped[str] = mapped_column(String(30), nullable=False, default="quiz")
    step_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    answers_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    ai_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
