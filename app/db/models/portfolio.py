from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PortfolioTransaction(Base):
    __tablename__ = "portfolio_transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    transaction_type: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    source: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    amount_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    original_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    original_currency: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)

    payment_id: Mapped[Optional[int]] = mapped_column(Integer, index=True, nullable=True)
    user_telegram_id: Mapped[Optional[int]] = mapped_column(BigInteger, index=True, nullable=True)
    admin_telegram_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False,
    )
