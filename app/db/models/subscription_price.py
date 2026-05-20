from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SubscriptionPrice(Base):
    __tablename__ = "subscription_prices"
    __table_args__ = (
        UniqueConstraint("payment_method", "plan_type", name="uq_subscription_prices_method_plan"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    payment_method: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    plan_type: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(16), nullable=False)
    updated_by_telegram_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
