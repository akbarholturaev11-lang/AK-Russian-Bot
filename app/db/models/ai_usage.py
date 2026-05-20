from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AIUsageBudget(Base):
    __tablename__ = "ai_usage_budgets"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_telegram_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    payment_id: Mapped[Optional[int]] = mapped_column(Integer, index=True, nullable=True)
    plan_type: Mapped[str] = mapped_column(String(32), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(16), nullable=False)

    total_budget_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    segment_1_budget_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    segment_2_budget_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    segment_1_spent_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    segment_2_spent_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    current_window_spent_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    window_started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    cooldown_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True, nullable=True)

    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="active", index=True, nullable=False)

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


class AIUsageEvent(Base):
    __tablename__ = "ai_usage_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    budget_id: Mapped[Optional[int]] = mapped_column(Integer, index=True, nullable=True)
    user_telegram_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    model: Mapped[str] = mapped_column(String(80), nullable=False)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
