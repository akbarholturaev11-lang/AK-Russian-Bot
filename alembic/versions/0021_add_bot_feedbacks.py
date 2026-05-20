"""add bot feedbacks

Revision ID: 0021_add_bot_feedbacks
Revises: 0020_add_discount_campaign_reason_i18n
Create Date: 2026-05-13
"""

from alembic import op
import sqlalchemy as sa


revision = "0021_add_bot_feedbacks"
down_revision = "0020_add_discount_campaign_reason_i18n"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "bot_feedbacks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("language", sa.String(length=8), nullable=False, server_default="ru"),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="pending"),
        sa.Column("liked_code", sa.String(length=64), nullable=True),
        sa.Column("liked_text", sa.Text(), nullable=True),
        sa.Column("disliked_code", sa.String(length=64), nullable=True),
        sa.Column("disliked_text", sa.Text(), nullable=True),
        sa.Column("prompt_message_id", sa.Integer(), nullable=True),
        sa.Column("prompted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reward_granted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("price_offer_due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("price_offer_sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("price_offer_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_bot_feedbacks")),
    )
    op.create_index(op.f("ix_bot_feedbacks_user_id"), "bot_feedbacks", ["user_id"], unique=False)
    op.create_index(op.f("ix_bot_feedbacks_telegram_id"), "bot_feedbacks", ["telegram_id"], unique=False)
    op.create_index(op.f("ix_bot_feedbacks_status"), "bot_feedbacks", ["status"], unique=False)
    op.create_index(op.f("ix_bot_feedbacks_completed_at"), "bot_feedbacks", ["completed_at"], unique=False)
    op.create_index(op.f("ix_bot_feedbacks_price_offer_due_at"), "bot_feedbacks", ["price_offer_due_at"], unique=False)

    op.alter_column("bot_feedbacks", "language", server_default=None)
    op.alter_column("bot_feedbacks", "status", server_default=None)


def downgrade() -> None:
    op.drop_index(op.f("ix_bot_feedbacks_price_offer_due_at"), table_name="bot_feedbacks")
    op.drop_index(op.f("ix_bot_feedbacks_completed_at"), table_name="bot_feedbacks")
    op.drop_index(op.f("ix_bot_feedbacks_status"), table_name="bot_feedbacks")
    op.drop_index(op.f("ix_bot_feedbacks_telegram_id"), table_name="bot_feedbacks")
    op.drop_index(op.f("ix_bot_feedbacks_user_id"), table_name="bot_feedbacks")
    op.drop_table("bot_feedbacks")
