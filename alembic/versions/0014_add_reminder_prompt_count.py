"""add reminder_prompt_count to course_progress

Revision ID: 0014_add_reminder_prompt_count
Revises: 0013_add_reminder_tz_and_last_sent
Create Date: 2026-05-10
"""

from alembic import op
import sqlalchemy as sa


revision = "0014_add_reminder_prompt_count"
down_revision = "0013_add_reminder_tz_and_last_sent"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "course_progress",
        sa.Column(
            "reminder_prompt_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.alter_column("course_progress", "reminder_prompt_count", server_default=None)


def downgrade() -> None:
    op.drop_column("course_progress", "reminder_prompt_count")
