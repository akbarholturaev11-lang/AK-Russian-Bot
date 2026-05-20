"""add ai usage budgets

Revision ID: 0022_add_ai_usage_budgets
Revises: 0021_add_bot_feedbacks
Create Date: 2026-05-14
"""

from alembic import op
import sqlalchemy as sa


revision = "0022_add_ai_usage_budgets"
down_revision = "0021_add_bot_feedbacks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_usage_budgets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("payment_id", sa.Integer(), nullable=True),
        sa.Column("plan_type", sa.String(length=32), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=16), nullable=False),
        sa.Column("total_budget_usd", sa.Float(), nullable=False, server_default="0"),
        sa.Column("segment_1_budget_usd", sa.Float(), nullable=False, server_default="0"),
        sa.Column("segment_2_budget_usd", sa.Float(), nullable=False, server_default="0"),
        sa.Column("segment_1_spent_usd", sa.Float(), nullable=False, server_default="0"),
        sa.Column("segment_2_spent_usd", sa.Float(), nullable=False, server_default="0"),
        sa.Column("current_window_spent_usd", sa.Float(), nullable=False, server_default="0"),
        sa.Column("window_started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("cooldown_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ai_usage_budgets")),
    )
    op.create_index(op.f("ix_ai_usage_budgets_user_telegram_id"), "ai_usage_budgets", ["user_telegram_id"], unique=False)
    op.create_index(op.f("ix_ai_usage_budgets_payment_id"), "ai_usage_budgets", ["payment_id"], unique=False)
    op.create_index(op.f("ix_ai_usage_budgets_cooldown_until"), "ai_usage_budgets", ["cooldown_until"], unique=False)
    op.create_index(op.f("ix_ai_usage_budgets_status"), "ai_usage_budgets", ["status"], unique=False)

    op.create_table(
        "ai_usage_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("budget_id", sa.Integer(), nullable=True),
        sa.Column("user_telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("model", sa.String(length=80), nullable=False),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completion_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cost_usd", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ai_usage_events")),
    )
    op.create_index(op.f("ix_ai_usage_events_budget_id"), "ai_usage_events", ["budget_id"], unique=False)
    op.create_index(op.f("ix_ai_usage_events_user_telegram_id"), "ai_usage_events", ["user_telegram_id"], unique=False)

    op.alter_column("ai_usage_budgets", "total_budget_usd", server_default=None)
    op.alter_column("ai_usage_budgets", "segment_1_budget_usd", server_default=None)
    op.alter_column("ai_usage_budgets", "segment_2_budget_usd", server_default=None)
    op.alter_column("ai_usage_budgets", "segment_1_spent_usd", server_default=None)
    op.alter_column("ai_usage_budgets", "segment_2_spent_usd", server_default=None)
    op.alter_column("ai_usage_budgets", "current_window_spent_usd", server_default=None)
    op.alter_column("ai_usage_budgets", "status", server_default=None)
    op.alter_column("ai_usage_events", "prompt_tokens", server_default=None)
    op.alter_column("ai_usage_events", "completion_tokens", server_default=None)
    op.alter_column("ai_usage_events", "total_tokens", server_default=None)
    op.alter_column("ai_usage_events", "cost_usd", server_default=None)


def downgrade() -> None:
    op.drop_index(op.f("ix_ai_usage_events_user_telegram_id"), table_name="ai_usage_events")
    op.drop_index(op.f("ix_ai_usage_events_budget_id"), table_name="ai_usage_events")
    op.drop_table("ai_usage_events")
    op.drop_index(op.f("ix_ai_usage_budgets_status"), table_name="ai_usage_budgets")
    op.drop_index(op.f("ix_ai_usage_budgets_cooldown_until"), table_name="ai_usage_budgets")
    op.drop_index(op.f("ix_ai_usage_budgets_payment_id"), table_name="ai_usage_budgets")
    op.drop_index(op.f("ix_ai_usage_budgets_user_telegram_id"), table_name="ai_usage_budgets")
    op.drop_table("ai_usage_budgets")
