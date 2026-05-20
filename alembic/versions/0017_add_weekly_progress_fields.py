"""add weekly progress fields

Revision ID: 0017_add_weekly_progress_fields
Revises: 0016_add_course_promo_sent
Create Date: 2026-05-13
"""

from alembic import op
import sqlalchemy as sa


revision = "0017_add_weekly_progress_fields"
down_revision = "0016_add_course_promo_sent"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "course_progress",
        sa.Column("last_weekly_progress_sent_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "course_progress",
        sa.Column(
            "weekly_progress_baseline_lessons_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.alter_column("course_progress", "weekly_progress_baseline_lessons_count", server_default=None)


def downgrade() -> None:
    op.drop_column("course_progress", "weekly_progress_baseline_lessons_count")
    op.drop_column("course_progress", "last_weekly_progress_sent_at")
