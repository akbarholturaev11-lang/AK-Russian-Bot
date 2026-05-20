"""add feedback reply and attachment fields

Revision ID: 0025_add_feedback_reply_and_attachment
Revises: 0024_add_portfolio_transactions
Create Date: 2026-05-19
"""

from alembic import op
import sqlalchemy as sa


revision = "0025_add_feedback_reply_and_attachment"
down_revision = "0024_add_portfolio_transactions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "bot_feedbacks",
        sa.Column("disliked_attachment_file_id", sa.String(length=256), nullable=True),
    )
    op.add_column(
        "bot_feedbacks",
        sa.Column("disliked_attachment_type", sa.String(length=16), nullable=True),
    )
    op.add_column("bot_feedbacks", sa.Column("admin_reply_text", sa.Text(), nullable=True))
    op.add_column("bot_feedbacks", sa.Column("admin_replied_by", sa.BigInteger(), nullable=True))
    op.add_column(
        "bot_feedbacks",
        sa.Column("admin_replied_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("bot_feedbacks", "admin_replied_at")
    op.drop_column("bot_feedbacks", "admin_replied_by")
    op.drop_column("bot_feedbacks", "admin_reply_text")
    op.drop_column("bot_feedbacks", "disliked_attachment_type")
    op.drop_column("bot_feedbacks", "disliked_attachment_file_id")
