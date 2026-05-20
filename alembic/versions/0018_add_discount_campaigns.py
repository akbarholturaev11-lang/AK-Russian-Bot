"""add discount campaigns

Revision ID: 0018_add_discount_campaigns
Revises: 0017_add_weekly_progress_fields
Create Date: 2026-05-13
"""

from alembic import op
import sqlalchemy as sa


revision = "0018_add_discount_campaigns"
down_revision = "0017_add_weekly_progress_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "discount_campaigns",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("percent", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("audience_status", sa.String(length=32), nullable=True),
        sa.Column("audience_language", sa.String(length=8), nullable=True),
        sa.Column("audience_level", sa.String(length=32), nullable=True),
        sa.Column("payment_method", sa.String(length=16), nullable=True),
        sa.Column("plan_type", sa.String(length=32), nullable=True),
        sa.Column("quota_total", sa.Integer(), nullable=True),
        sa.Column("repeat_interval_days", sa.Integer(), nullable=True),
        sa.Column("created_by_telegram_id", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_discount_campaigns")),
    )

    op.add_column("payments", sa.Column("payment_method", sa.String(length=16), nullable=True))
    op.add_column("payments", sa.Column("base_amount", sa.Integer(), nullable=True))
    op.add_column(
        "payments",
        sa.Column("discount_source", sa.String(length=32), nullable=False, server_default="none"),
    )
    op.add_column(
        "payments",
        sa.Column("discount_percent", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column("payments", sa.Column("discount_campaign_id", sa.Integer(), nullable=True))
    op.add_column("payments", sa.Column("discount_title", sa.String(length=120), nullable=True))
    op.add_column("payments", sa.Column("discount_details", sa.Text(), nullable=True))
    op.alter_column("payments", "discount_source", server_default=None)
    op.alter_column("payments", "discount_percent", server_default=None)


def downgrade() -> None:
    op.drop_column("payments", "discount_details")
    op.drop_column("payments", "discount_title")
    op.drop_column("payments", "discount_campaign_id")
    op.drop_column("payments", "discount_percent")
    op.drop_column("payments", "discount_source")
    op.drop_column("payments", "base_amount")
    op.drop_column("payments", "payment_method")
    op.drop_table("discount_campaigns")
