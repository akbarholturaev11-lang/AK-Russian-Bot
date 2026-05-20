"""add admin target discounts prices and required channels

Revision ID: 0026_admin_target_prices_required_channels
Revises: 0025_add_feedback_reply_and_attachment
Create Date: 2026-05-19
"""

from alembic import op
import sqlalchemy as sa


revision = "0026_admin_target_prices_required_channels"
down_revision = "0025_add_feedback_reply_and_attachment"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("username", sa.String(length=64), nullable=True))
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=False)

    op.add_column("discount_campaigns", sa.Column("target_telegram_id", sa.BigInteger(), nullable=True))
    op.create_index(
        op.f("ix_discount_campaigns_target_telegram_id"),
        "discount_campaigns",
        ["target_telegram_id"],
        unique=False,
    )

    op.create_table(
        "bot_settings",
        sa.Column("key", sa.String(length=120), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("key", name=op.f("pk_bot_settings")),
    )
    op.create_table(
        "required_channels",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("chat_id", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("invite_link", sa.String(length=300), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_by_telegram_id", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_required_channels")),
    )
    op.create_index(op.f("ix_required_channels_chat_id"), "required_channels", ["chat_id"], unique=True)
    op.alter_column("required_channels", "is_active", server_default=None)

    op.create_table(
        "subscription_prices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("payment_method", sa.String(length=16), nullable=False),
        sa.Column("plan_type", sa.String(length=32), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=16), nullable=False),
        sa.Column("updated_by_telegram_id", sa.BigInteger(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_subscription_prices")),
        sa.UniqueConstraint("payment_method", "plan_type", name="uq_subscription_prices_method_plan"),
    )
    op.create_index(op.f("ix_subscription_prices_payment_method"), "subscription_prices", ["payment_method"], unique=False)
    op.create_index(op.f("ix_subscription_prices_plan_type"), "subscription_prices", ["plan_type"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_subscription_prices_plan_type"), table_name="subscription_prices")
    op.drop_index(op.f("ix_subscription_prices_payment_method"), table_name="subscription_prices")
    op.drop_table("subscription_prices")
    op.drop_index(op.f("ix_required_channels_chat_id"), table_name="required_channels")
    op.drop_table("required_channels")
    op.drop_table("bot_settings")
    op.drop_index(op.f("ix_discount_campaigns_target_telegram_id"), table_name="discount_campaigns")
    op.drop_column("discount_campaigns", "target_telegram_id")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_column("users", "username")
