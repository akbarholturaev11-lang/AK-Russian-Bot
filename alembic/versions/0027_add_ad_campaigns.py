"""add ad campaigns

Revision ID: 0027_add_ad_campaigns
Revises: 0026_admin_target_prices_required_channels
Create Date: 2026-05-20
"""

from alembic import op
import sqlalchemy as sa


revision = "0027_add_ad_campaigns"
down_revision = "0026_admin_target_prices_required_channels"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ad_campaigns",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("message_text", sa.Text(), nullable=True),
        sa.Column("content_type", sa.String(length=16), nullable=False),
        sa.Column("media_file_id", sa.String(length=512), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("next_send_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("send_count_total", sa.Integer(), nullable=False),
        sa.Column("rounds_sent", sa.Integer(), nullable=False),
        sa.Column("target_languages", sa.String(length=40), nullable=True),
        sa.Column("include_active_subscribers", sa.Boolean(), nullable=False),
        sa.Column("created_by_telegram_id", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ad_campaigns")),
    )
    op.create_index(op.f("ix_ad_campaigns_next_send_at"), "ad_campaigns", ["next_send_at"], unique=False)

    op.create_table(
        "ad_campaign_deliveries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("campaign_id", sa.Integer(), nullable=False),
        sa.Column("user_telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("round_no", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("error", sa.String(length=300), nullable=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["campaign_id"],
            ["ad_campaigns.id"],
            name=op.f("fk_ad_campaign_deliveries_campaign_id_ad_campaigns"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ad_campaign_deliveries")),
        sa.UniqueConstraint(
            "campaign_id",
            "user_telegram_id",
            "round_no",
            name="uq_ad_campaign_deliveries_campaign_user_round",
        ),
    )
    op.create_index(
        op.f("ix_ad_campaign_deliveries_campaign_id"),
        "ad_campaign_deliveries",
        ["campaign_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ad_campaign_deliveries_user_telegram_id"),
        "ad_campaign_deliveries",
        ["user_telegram_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_ad_campaign_deliveries_user_telegram_id"), table_name="ad_campaign_deliveries")
    op.drop_index(op.f("ix_ad_campaign_deliveries_campaign_id"), table_name="ad_campaign_deliveries")
    op.drop_table("ad_campaign_deliveries")
    op.drop_index(op.f("ix_ad_campaigns_next_send_at"), table_name="ad_campaigns")
    op.drop_table("ad_campaigns")
