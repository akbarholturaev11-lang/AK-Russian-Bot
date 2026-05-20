"""initial migration

Revision ID: 0001
Revises:
Create Date: 2026-03-24
"""

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("language", sa.String(length=8), nullable=False, server_default="tj"),
        sa.Column("level", sa.String(length=32), nullable=False, server_default="beginner"),
        sa.Column("learning_mode", sa.String(length=16), nullable=False, server_default="qa"),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="free"),
        sa.Column("payment_status", sa.String(length=16), nullable=False, server_default="none"),
        sa.Column("question_limit", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("questions_used", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("bonus_questions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("referrer_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_active_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"], unique=True)


def downgrade():
    op.drop_index("ix_users_telegram_id", table_name="users")
    op.drop_table("users")
