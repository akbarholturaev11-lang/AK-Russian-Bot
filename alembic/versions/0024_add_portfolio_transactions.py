"""add portfolio transactions

Revision ID: 0024_add_portfolio_transactions
Revises: 0023_add_user_voice_mode
Create Date: 2026-05-15
"""

from alembic import op
import sqlalchemy as sa


revision = "0024_add_portfolio_transactions"
down_revision = "0023_add_user_voice_mode"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "portfolio_transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("transaction_type", sa.String(length=16), nullable=False),
        sa.Column("source", sa.String(length=40), nullable=False),
        sa.Column("amount_usd", sa.Float(), nullable=False, server_default="0"),
        sa.Column("original_amount", sa.Float(), nullable=True),
        sa.Column("original_currency", sa.String(length=16), nullable=True),
        sa.Column("payment_id", sa.Integer(), nullable=True),
        sa.Column("user_telegram_id", sa.BigInteger(), nullable=True),
        sa.Column("admin_telegram_id", sa.BigInteger(), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_portfolio_transactions")),
    )
    op.create_index(
        op.f("ix_portfolio_transactions_transaction_type"),
        "portfolio_transactions",
        ["transaction_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_portfolio_transactions_source"),
        "portfolio_transactions",
        ["source"],
        unique=False,
    )
    op.create_index(
        op.f("ix_portfolio_transactions_payment_id"),
        "portfolio_transactions",
        ["payment_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_portfolio_transactions_user_telegram_id"),
        "portfolio_transactions",
        ["user_telegram_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_portfolio_transactions_created_at"),
        "portfolio_transactions",
        ["created_at"],
        unique=False,
    )
    op.alter_column("portfolio_transactions", "amount_usd", server_default=None)


def downgrade() -> None:
    op.drop_index(op.f("ix_portfolio_transactions_created_at"), table_name="portfolio_transactions")
    op.drop_index(op.f("ix_portfolio_transactions_user_telegram_id"), table_name="portfolio_transactions")
    op.drop_index(op.f("ix_portfolio_transactions_payment_id"), table_name="portfolio_transactions")
    op.drop_index(op.f("ix_portfolio_transactions_source"), table_name="portfolio_transactions")
    op.drop_index(op.f("ix_portfolio_transactions_transaction_type"), table_name="portfolio_transactions")
    op.drop_table("portfolio_transactions")
