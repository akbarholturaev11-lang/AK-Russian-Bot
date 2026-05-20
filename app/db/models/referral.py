from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import BigInteger, String, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Referral(Base):
    __tablename__ = "referrals"

    id: Mapped[int] = mapped_column(primary_key=True)

    referrer_telegram_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    invited_user_telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)

    status: Mapped[str] = mapped_column(String(16), default="pending", nullable=False)
    bonus_granted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    counts_for_discount: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    activated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
