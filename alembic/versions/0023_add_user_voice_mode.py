"""add user voice mode

Revision ID: 0023_add_user_voice_mode
Revises: 0022_add_ai_usage_budgets
Create Date: 2026-05-14
"""

from alembic import op
import sqlalchemy as sa


revision = "0023_add_user_voice_mode"
down_revision = "0022_add_ai_usage_budgets"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("voice_mode", sa.String(length=20), nullable=False, server_default="none"),
    )
    op.alter_column("users", "voice_mode", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "voice_mode")
