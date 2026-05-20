"""add discount progress fields to users

Revision ID: 0007
Revises: 0006
Create Date: 2026-03-26
"""

from alembic import op
import sqlalchemy as sa

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("discount_progress_chat_id", sa.BigInteger(), nullable=True))
    op.add_column("users", sa.Column("discount_progress_message_id", sa.BigInteger(), nullable=True))


def downgrade():
    op.drop_column("users", "discount_progress_message_id")
    op.drop_column("users", "discount_progress_chat_id")
