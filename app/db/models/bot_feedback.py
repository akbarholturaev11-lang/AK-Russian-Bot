from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class BotFeedback(Base):
    __tablename__ = "bot_feedbacks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    telegram_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    language: Mapped[str] = mapped_column(String(8), default="ru", nullable=False)

    status: Mapped[str] = mapped_column(String(16), default="pending", index=True, nullable=False)
    liked_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    liked_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    disliked_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    disliked_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    disliked_attachment_file_id: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    disliked_attachment_type: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    admin_reply_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    admin_replied_by: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    admin_replied_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    prompt_message_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    prompted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    reward_granted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    price_offer_due_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    price_offer_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    price_offer_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
