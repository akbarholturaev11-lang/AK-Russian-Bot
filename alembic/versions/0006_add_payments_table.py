"""add payments table

Revision ID: 0006
Revises: 0005
Create Date: 2026-03-26
"""

from alembic import op
import sqlalchemy as sa

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("plan_type", sa.String(length=32), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=16), nullable=False, server_default="somoni"),
        sa.Column("payment_status", sa.String(length=16), nullable=False, server_default="pending"),
        sa.Column("screenshot_file_id", sa.String(length=255), nullable=True),
        sa.Column("admin_comment", sa.Text(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_payments_user_telegram_id", "payments", ["user_telegram_id"], unique=False)


def downgrade():
    op.drop_index("ix_payments_user_telegram_id", table_name="payments")
    op.drop_table("payments")
