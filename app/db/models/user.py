from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import BigInteger, String, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Column

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    username: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)

    payment_method = Column(String, nullable=True)

    language: Mapped[str] = mapped_column(String(8), default="tj", nullable=False)
    level: Mapped[str] = mapped_column(String(32), default="beginner", nullable=False)
    learning_mode: Mapped[str] = mapped_column(String(16), default="qa", nullable=False)
    voice_mode: Mapped[str] = mapped_column(String(20), default="none", nullable=False)

    status: Mapped[str] = mapped_column(String(16), default="free", nullable=False)
    payment_status: Mapped[str] = mapped_column(String(16), default="none", nullable=False)

    question_limit: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    questions_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    bonus_questions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    bonus_questions_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    referral_code: Mapped[Optional[str]] = mapped_column(String(64), unique=True, nullable=True)
    referred_by_telegram_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    start_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    end_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    discount_offer_started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    discount_referral_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    discount_eligible: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    discount_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
      
    last_limit_reset_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    daily_limit_offer_sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    discount_progress_chat_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    discount_progress_message_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    selected_plan_type: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    pending_checkout_msg_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    expiry_reminder_sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    referrer_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    course_promo_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_active_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
