"""add course_promo_sent to users

Revision ID: 0016_add_course_promo_sent
Revises: 0015_add_course_audio
Create Date: 2026-05-11
"""

from alembic import op
import sqlalchemy as sa


revision = "0016_add_course_promo_sent"
down_revision = "0015_add_course_audio"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("course_promo_sent", sa.Boolean(), nullable=False, server_default="false"),
    )


def downgrade() -> None:
    op.drop_column("users", "course_promo_sent")
