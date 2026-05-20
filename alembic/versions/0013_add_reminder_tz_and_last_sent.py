"""add reminder_tz_offset and last_reminder_sent_at to course_progress

Revision ID: 0013_add_reminder_tz_and_last_sent
Revises: 0012_add_payment_msg_ids
Create Date: 2026-05-09
"""

from alembic import op
import sqlalchemy as sa


revision = "0013_add_reminder_tz_and_last_sent"
down_revision = "0012_add_payment_msg_ids"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "course_progress",
        sa.Column(
            "reminder_tz_offset",
            sa.Integer(),
            nullable=False,
            server_default="5",
        ),
    )
    op.add_column(
        "course_progress",
        sa.Column("last_reminder_sent_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.alter_column("course_progress", "reminder_tz_offset", server_default=None)


def downgrade() -> None:
    op.drop_column("course_progress", "last_reminder_sent_at")
    op.drop_column("course_progress", "reminder_tz_offset")
