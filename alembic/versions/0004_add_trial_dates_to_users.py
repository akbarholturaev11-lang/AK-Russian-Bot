"""add trial dates to users

Revision ID: 0004
Revises: 0003
Create Date: 2026-03-26
"""

from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("start_date", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("end_date", sa.DateTime(timezone=True), nullable=True))


def downgrade():
    op.drop_column("users", "end_date")
    op.drop_column("users", "start_date")
