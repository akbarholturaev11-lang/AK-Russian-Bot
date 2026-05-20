"""add bonus questions used to users

Revision ID: 0009
Revises: 0008
Create Date: 2026-03-26
"""

from alembic import op
import sqlalchemy as sa

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column("bonus_questions_used", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade():
    op.drop_column("users", "bonus_questions_used")
