"""add course_audio table for storing telegram file_ids

Revision ID: 0015_add_course_audio
Revises: 0014_add_reminder_prompt_count
Create Date: 2026-05-10
"""

from alembic import op
import sqlalchemy as sa


revision = "0015_add_course_audio"
down_revision = "0014_add_reminder_prompt_count"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "course_audio",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("level", sa.String(32), nullable=False),
        sa.Column("lesson_order", sa.Integer(), nullable=False),
        sa.Column("audio_type", sa.String(32), nullable=False),
        sa.Column("file_id", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("level", "lesson_order", "audio_type", name="uq_course_audio"),
    )
    op.create_index("ix_course_audio_level", "course_audio", ["level"])
    op.create_index("ix_course_audio_lesson_order", "course_audio", ["lesson_order"])


def downgrade() -> None:
    op.drop_index("ix_course_audio_lesson_order", table_name="course_audio")
    op.drop_index("ix_course_audio_level", table_name="course_audio")
    op.drop_table("course_audio")
