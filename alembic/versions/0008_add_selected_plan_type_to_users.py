"""add selected plan type to users

Revision ID: 0008
Revises: 0007
Create Date: 2026-03-26
"""

from alembic import op
import sqlalchemy as sa

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("selected_plan_type", sa.String(length=32), nullable=True))


def downgrade():
    op.drop_column("users", "selected_plan_type")
