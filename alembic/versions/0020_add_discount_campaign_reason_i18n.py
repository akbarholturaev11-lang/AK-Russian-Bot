"""add discount campaign reason i18n

Revision ID: 0020_add_discount_campaign_reason_i18n
Revises: 0019_add_discount_campaign_title_i18n
Create Date: 2026-05-13
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0020_add_discount_campaign_reason_i18n"
down_revision = "0019_add_discount_campaign_title_i18n"
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
    _add_column_if_missing("discount_campaigns", sa.Column("reason", sa.String(length=500), nullable=True))
    _add_column_if_missing("discount_campaigns", sa.Column("reason_tj", sa.String(length=700), nullable=True))
    _add_column_if_missing("discount_campaigns", sa.Column("reason_ru", sa.String(length=700), nullable=True))
    _add_column_if_missing("discount_campaigns", sa.Column("reason_uz", sa.String(length=700), nullable=True))


def downgrade() -> None:
    _drop_column_if_exists("discount_campaigns", "reason_uz")
    _drop_column_if_exists("discount_campaigns", "reason_ru")
    _drop_column_if_exists("discount_campaigns", "reason_tj")
    _drop_column_if_exists("discount_campaigns", "reason")
