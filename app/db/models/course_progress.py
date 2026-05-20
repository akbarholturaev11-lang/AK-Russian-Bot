from datetime import datetime, timezone, time
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CourseProgress(Base):
    __tablename__ = "course_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    level: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    current_lesson_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("course_lessons.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    current_step: Mapped[str] = mapped_column(String(32), nullable=False, default="intro")

    waiting_for: Mapped[str] = mapped_column(String(50), nullable=False, default="none")

    completed_lessons_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    last_opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    last_completed_lesson_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("course_lessons.id", ondelete="SET NULL"),
        nullable=True,
    )
    needs_review_prompt: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    homework_status: Mapped[str] = mapped_column(String(30), nullable=False, default="none")

    reminder_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    reminder_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    reminder_tz_offset: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    last_reminder_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reminder_prompt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    next_study_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_weekly_progress_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    weekly_progress_baseline_lessons_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

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
