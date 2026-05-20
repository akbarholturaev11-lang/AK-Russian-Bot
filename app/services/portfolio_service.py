from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import delete, func, or_, select

from app.db.models.payment import Payment
from app.db.models.portfolio import PortfolioTransaction
from app.services.ai_usage_budget_service import (
    USD_TO_SOMONI,
    USD_TO_YUAN,
)


@dataclass(frozen=True)
class PortfolioSummary:
    approved_payments: int
    gross_revenue_usd: float
    subscription_profit_usd: float
    manual_profit_usd: float
    total_profit_usd: float
    manual_expense_usd: float
    total_expense_usd: float
    net_usd: float


class PortfolioService:
    def __init__(self, session):
        self.session = session

    def amount_to_usd(self, amount: float, currency: str) -> Optional[float]:
        currency_key = (currency or "").strip().lower()
        if currency_key in {"somoni", "tjs", "сомони"}:
            return float(amount) / USD_TO_SOMONI
        if currency_key in {"usd", "$"}:
            return float(amount)
        if currency_key in {"¥", "cny", "yuan", "юань"}:
            return float(amount) / USD_TO_YUAN
        return None

    async def _get_transaction(self, payment_id: int, source: str) -> Optional[PortfolioTransaction]:
        result = await self.session.execute(
            select(PortfolioTransaction)
            .where(PortfolioTransaction.payment_id == payment_id)
            .where(PortfolioTransaction.source == source)
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def _delete_stale_subscription_profits(self) -> None:
        approved_payment_ids = select(Payment.id).where(Payment.payment_status == "approved")
        await self.session.execute(
            delete(PortfolioTransaction)
            .where(PortfolioTransaction.source == "subscription_profit")
            .where(
                or_(
                    PortfolioTransaction.payment_id.is_(None),
                    ~PortfolioTransaction.payment_id.in_(approved_payment_ids),
                )
            )
        )

    async def record_subscription_profit(self, payment: Payment) -> None:
        revenue_usd = self.amount_to_usd(payment.amount, payment.currency)
        if revenue_usd is None:
            return

        transaction = await self._get_transaction(payment.id, "subscription_profit")
        if transaction:
            transaction.amount_usd = revenue_usd
            transaction.original_amount = payment.amount
            transaction.original_currency = payment.currency
            transaction.user_telegram_id = payment.user_telegram_id
            transaction.note = "100% revenue from subscription"
        else:
            self.session.add(
                PortfolioTransaction(
                    transaction_type="profit",
                    source="subscription_profit",
                    amount_usd=revenue_usd,
                    original_amount=payment.amount,
                    original_currency=payment.currency,
                    payment_id=payment.id,
                    user_telegram_id=payment.user_telegram_id,
                    note="100% revenue from subscription",
                    created_at=payment.reviewed_at or datetime.now(timezone.utc),
                )
            )

        await self.session.flush()

    async def sync_approved_payments(self) -> None:
        await self._delete_stale_subscription_profits()
        result = await self.session.execute(
            select(Payment).where(Payment.payment_status == "approved")
        )
        for payment in result.scalars().all():
            await self.record_subscription_profit(payment)
        await self.session.flush()

    async def add_manual_transaction(
        self,
        *,
        transaction_type: str,
        admin_telegram_id: int,
        amount: float,
        currency: str,
        note: str,
    ) -> Optional[PortfolioTransaction]:
        if transaction_type not in {"profit", "expense"}:
            return None

        amount_usd = self.amount_to_usd(amount, currency)
        if amount_usd is None:
            return None

        transaction = PortfolioTransaction(
            transaction_type=transaction_type,
            source=f"manual_{transaction_type}",
            amount_usd=amount_usd,
            original_amount=amount,
            original_currency=currency,
            admin_telegram_id=admin_telegram_id,
            note=note,
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(transaction)
        await self.session.flush()
        return transaction

    async def get_summary(self) -> PortfolioSummary:
        await self.sync_approved_payments()

        subscription_profit_usd = await self._sum_transactions("profit", source="subscription_profit")
        manual_profit_usd = await self._sum_transactions("profit", source="manual_profit")
        total_profit_usd = subscription_profit_usd + manual_profit_usd
        manual_expense_usd = await self._sum_transactions("expense", source="manual_expense")
        gross_revenue_usd, approved_payments = await self._approved_payment_totals()
        total_expense_usd = manual_expense_usd

        return PortfolioSummary(
            approved_payments=approved_payments,
            gross_revenue_usd=gross_revenue_usd,
            subscription_profit_usd=subscription_profit_usd,
            manual_profit_usd=manual_profit_usd,
            total_profit_usd=total_profit_usd,
            manual_expense_usd=manual_expense_usd,
            total_expense_usd=total_expense_usd,
            net_usd=total_profit_usd - total_expense_usd,
        )

    async def list_history(self, limit: int = 20) -> list[PortfolioTransaction]:
        await self.sync_approved_payments()
        result = await self.session.execute(
            select(PortfolioTransaction)
            .order_by(PortfolioTransaction.created_at.desc(), PortfolioTransaction.id.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def _sum_transactions(self, transaction_type: str, source: Optional[str] = None) -> float:
        query = select(func.sum(PortfolioTransaction.amount_usd)).where(
            PortfolioTransaction.transaction_type == transaction_type
        )
        if source:
            query = query.where(PortfolioTransaction.source == source)
        result = await self.session.execute(query)
        return float(result.scalar() or 0.0)

    async def _approved_payment_totals(self) -> tuple[float, int]:
        result = await self.session.execute(
            select(Payment).where(Payment.payment_status == "approved")
        )
        total_usd = 0.0
        count = 0
        for payment in result.scalars().all():
            amount_usd = self.amount_to_usd(payment.amount, payment.currency)
            if amount_usd is None:
                continue
            total_usd += amount_usd
            count += 1
        return total_usd, count
