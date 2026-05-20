from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DiscountCampaign(Base):
    __tablename__ = "discount_campaigns"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    title_tj: Mapped[Optional[str]] = mapped_column(String(180), nullable=True)
    title_ru: Mapped[Optional[str]] = mapped_column(String(180), nullable=True)
    title_uz: Mapped[Optional[str]] = mapped_column(String(180), nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    reason_tj: Mapped[Optional[str]] = mapped_column(String(700), nullable=True)
    reason_ru: Mapped[Optional[str]] = mapped_column(String(700), nullable=True)
    reason_uz: Mapped[Optional[str]] = mapped_column(String(700), nullable=True)
    percent: Mapped[int] = mapped_column(Integer, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    audience_status: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    audience_language: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)
    audience_level: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    target_telegram_id: Mapped[Optional[int]] = mapped_column(BigInteger, index=True, nullable=True)
    payment_method: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    plan_type: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    quota_total: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    repeat_interval_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    created_by_telegram_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
