"""add daily limit offer sent at

Revision ID: 0005
Revises: 0004
Create Date: 2026-03-26
"""

from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column("daily_limit_offer_sent_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade():
    op.drop_column("users", "daily_limit_offer_sent_at")
