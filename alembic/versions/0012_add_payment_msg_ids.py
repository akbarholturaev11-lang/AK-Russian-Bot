"""add payment message ids for cleanup on approve

Revision ID: 0012_add_payment_msg_ids
Revises: 0011_add_course_workflow_fields
Create Date: 2026-04-28
"""

from alembic import op
import sqlalchemy as sa


revision = "0012_add_payment_msg_ids"
down_revision = "0011_add_course_workflow_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("payments", sa.Column("checkout_msg_id", sa.Integer(), nullable=True))
    op.add_column("payments", sa.Column("screenshot_msg_id", sa.Integer(), nullable=True))
    op.add_column("payments", sa.Column("waiting_msg_id", sa.Integer(), nullable=True))
    op.add_column("users", sa.Column("pending_checkout_msg_id", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("payments", "checkout_msg_id")
    op.drop_column("payments", "screenshot_msg_id")
    op.drop_column("payments", "waiting_msg_id")
    op.drop_column("users", "pending_checkout_msg_id")
