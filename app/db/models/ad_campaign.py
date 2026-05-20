from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AdCampaign(Base):
    __tablename__ = "ad_campaigns"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    message_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_type: Mapped[str] = mapped_column(String(16), default="text", nullable=False)
    media_file_id: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    next_send_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    send_count_total: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    rounds_sent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    target_languages: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    include_active_subscribers: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_by_telegram_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class AdCampaignDelivery(Base):
    __tablename__ = "ad_campaign_deliveries"
    __table_args__ = (
        UniqueConstraint(
            "campaign_id",
            "user_telegram_id",
            "round_no",
            name="uq_ad_campaign_deliveries_campaign_user_round",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("ad_campaigns.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    user_telegram_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    round_no: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    error: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    delivered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
