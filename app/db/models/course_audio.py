from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CourseAudio(Base):
    """Telegram file_id orqali saqlangan kurs audio fayllari.

    audio_type qiymatlari: vocab | dialogue_1 | dialogue_2 | dialogue_3 | dialogue_4
    """
    __tablename__ = "course_audio"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    level: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    lesson_order: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    audio_type: Mapped[str] = mapped_column(String(32), nullable=False)
    file_id: Mapped[str] = mapped_column(String(255), nullable=False)

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

    __table_args__ = (
        UniqueConstraint("level", "lesson_order", "audio_type", name="uq_course_audio"),
    )
