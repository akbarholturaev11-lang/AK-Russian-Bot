"""add discount campaign title i18n

Revision ID: 0019_add_discount_campaign_title_i18n
Revises: 0018_add_discount_campaigns
Create Date: 2026-05-13
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0019_add_discount_campaign_title_i18n"
down_revision = "0018_add_discount_campaigns"
branch_labels = None
depends_on = None


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    return column_name in {column["name"] for column in inspect(bind).get_columns(table_name)}


def _add_column_if_missing(table_name: str, column: sa.Column) -> None:
    if not _has_column(table_name, column.name):
        op.add_column(table_name, column)


def _drop_column_if_exists(table_name: str, column_name: str) -> None:
    if _has_column(table_name, column_name):
        op.drop_column(table_name, column_name)


def upgrade() -> None:
    _add_column_if_missing("discount_campaigns", sa.Column("title_tj", sa.String(length=180), nullable=True))
    _add_column_if_missing("discount_campaigns", sa.Column("title_ru", sa.String(length=180), nullable=True))
    _add_column_if_missing("discount_campaigns", sa.Column("title_uz", sa.String(length=180), nullable=True))


def downgrade() -> None:
    _drop_column_if_exists("discount_campaigns", "title_uz")
    _drop_column_if_exists("discount_campaigns", "title_ru")
    _drop_column_if_exists("discount_campaigns", "title_tj")
