"""add referrals and user discount fields

Revision ID: 0003
Revises: 0002
Create Date: 2026-03-25
"""

from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("referral_code", sa.String(length=64), nullable=True))
    op.add_column("users", sa.Column("referred_by_telegram_id", sa.BigInteger(), nullable=True))
    op.add_column("users", sa.Column("discount_offer_started_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("discount_referral_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("discount_eligible", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("users", sa.Column("discount_used", sa.Boolean(), nullable=False, server_default=sa.false()))

    op.create_unique_constraint("uq_users_referral_code", "users", ["referral_code"])

    op.create_table(
        "referrals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("referrer_telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("invited_user_telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="pending"),
        sa.Column("bonus_granted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("counts_for_discount", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index("ix_referrals_referrer_telegram_id", "referrals", ["referrer_telegram_id"], unique=False)
    op.create_unique_constraint(
        "uq_referrals_invited_user_telegram_id",
        "referrals",
        ["invited_user_telegram_id"],
    )


def downgrade():
    op.drop_constraint("uq_referrals_invited_user_telegram_id", "referrals", type_="unique")
    op.drop_index("ix_referrals_referrer_telegram_id", table_name="referrals")
    op.drop_table("referrals")

    op.drop_constraint("uq_users_referral_code", "users", type_="unique")
    op.drop_column("users", "discount_used")
    op.drop_column("users", "discount_eligible")
    op.drop_column("users", "discount_referral_count")
    op.drop_column("users", "discount_offer_started_at")
    op.drop_column("users", "referred_by_telegram_id")
    op.drop_column("users", "referral_code")
