from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import BigInteger, String, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_telegram_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    plan_type: Mapped[str] = mapped_column(String(32), nullable=False)
    payment_method: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    base_amount: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(16), default="somoni", nullable=False)

    payment_status: Mapped[str] = mapped_column(String(16), default="pending", nullable=False)
    screenshot_file_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    admin_comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    discount_source: Mapped[str] = mapped_column(String(32), default="none", nullable=False)
    discount_percent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    discount_campaign_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    discount_title: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    discount_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    checkout_msg_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    screenshot_msg_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    waiting_msg_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
