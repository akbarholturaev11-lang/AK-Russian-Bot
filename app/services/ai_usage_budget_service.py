from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select

from app.db.models.ai_usage import AIUsageBudget, AIUsageEvent
from app.services.ai_service import AIUsageResult


USD_TO_SOMONI = 9.37
USD_TO_YUAN = 6.80
PROFIT_MARGIN = 0.40
RAILWAY_SHARE_USD = 1.0
SEGMENT_COUNT = 2
COOLDOWN_HOURS = 6

MODEL_PRICING_USD_PER_1M = {
    "gpt-4o-mini": (0.15, 0.60),
    "o4-mini": (1.10, 4.40),
    "gpt-4o-mini-transcribe": (1.25, 5.00),
}


@dataclass(frozen=True)
class BudgetAccessResult:
    allowed: bool
    message_key: str = ""
    cooldown_hours: int = COOLDOWN_HOURS


@dataclass(frozen=True)
class BudgetRecordResult:
    cost_usd: float
    cooldown_started: bool = False
    message_key: str = ""
    cooldown_hours: int = COOLDOWN_HOURS


class AIUsageBudgetService:
    def __init__(self, session):
        self.session = session

    def _as_utc(self, dt: datetime) -> datetime:
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    def _amount_to_usd(self, amount: int, currency: str) -> Optional[float]:
        currency_key = (currency or "").strip().lower()
        if currency_key in {"somoni", "tjs", "сомони"}:
            return amount / USD_TO_SOMONI
        if currency_key in {"usd", "$"}:
            return float(amount)
        if currency_key in {"¥", "cny", "yuan", "юань"}:
            return amount / USD_TO_YUAN
        return None

    def _ai_budget_usd(self, amount: int, currency: str) -> Optional[float]:
        revenue_usd = self._amount_to_usd(amount, currency)
        if revenue_usd is None:
            return None
        return max((revenue_usd * (1 - PROFIT_MARGIN)) - RAILWAY_SHARE_USD, 0.0)

    async def create_for_payment(self, payment, starts_at: datetime, ends_at: datetime) -> Optional[AIUsageBudget]:
        total_budget = self._ai_budget_usd(payment.amount, payment.currency)
        if total_budget is None:
            return None

        await self.expire_active_budgets(payment.user_telegram_id)

        now = datetime.now(timezone.utc)
        segment_budget = total_budget / SEGMENT_COUNT
        budget = AIUsageBudget(
            user_telegram_id=payment.user_telegram_id,
            payment_id=payment.id,
            plan_type=payment.plan_type,
            amount=payment.amount,
            currency=payment.currency,
            total_budget_usd=total_budget,
            segment_1_budget_usd=segment_budget,
            segment_2_budget_usd=segment_budget,
            segment_1_spent_usd=0.0,
            segment_2_spent_usd=0.0,
            current_window_spent_usd=0.0,
            window_started_at=now,
            cooldown_until=None,
            starts_at=starts_at,
            ends_at=ends_at,
            status="active",
            created_at=now,
            updated_at=now,
        )
        self.session.add(budget)
        await self.session.flush()
        return budget

    async def expire_active_budgets(self, telegram_id: int) -> None:
        budgets = await self._list_active_budgets(telegram_id)
        now = datetime.now(timezone.utc)
        for budget in budgets:
            budget.status = "expired"
            budget.updated_at = now
        if budgets:
            await self.session.flush()

    async def _list_active_budgets(self, telegram_id: int) -> list[AIUsageBudget]:
        result = await self.session.execute(
            select(AIUsageBudget)
            .where(AIUsageBudget.user_telegram_id == telegram_id)
            .where(AIUsageBudget.status == "active")
            .order_by(AIUsageBudget.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_active_budget(self, telegram_id: int) -> Optional[AIUsageBudget]:
        now = datetime.now(timezone.utc)
        budgets = await self._list_active_budgets(telegram_id)
        active = None
        changed = False
        for budget in budgets:
            if self._as_utc(budget.ends_at) <= now:
                budget.status = "expired"
                budget.updated_at = now
                changed = True
                continue
            if active is None:
                active = budget
            else:
                budget.status = "expired"
                budget.updated_at = now
                changed = True
        if changed:
            await self.session.flush()
        return active

    def _segment_bounds(self, budget: AIUsageBudget, now: datetime) -> tuple[int, datetime, datetime]:
        starts_at = self._as_utc(budget.starts_at)
        ends_at = self._as_utc(budget.ends_at)
        midpoint = starts_at + ((ends_at - starts_at) / SEGMENT_COUNT)
        if now < midpoint:
            return 1, starts_at, midpoint
        return 2, midpoint, ends_at

    def _segment_budget(self, budget: AIUsageBudget, segment: int) -> float:
        return budget.segment_1_budget_usd if segment == 1 else budget.segment_2_budget_usd

    def _segment_spent(self, budget: AIUsageBudget, segment: int) -> float:
        return budget.segment_1_spent_usd if segment == 1 else budget.segment_2_spent_usd

    def _set_segment_spent(self, budget: AIUsageBudget, segment: int, value: float) -> None:
        if segment == 1:
            budget.segment_1_spent_usd = value
        else:
            budget.segment_2_spent_usd = value

    def _remaining_segment_budget(self, budget: AIUsageBudget, segment: int) -> float:
        return max(self._segment_budget(budget, segment) - self._segment_spent(budget, segment), 0.0)

    def _remaining_segment_days(self, segment_end: datetime, now: datetime) -> float:
        seconds = max((segment_end - now).total_seconds(), 0.0)
        return max(seconds / 86400, 1.0)

    def _current_threshold_usd(self, budget: AIUsageBudget, segment: int, segment_end: datetime, now: datetime) -> float:
        remaining_budget = self._remaining_segment_budget(budget, segment)
        daily_budget = remaining_budget / self._remaining_segment_days(segment_end, now)
        return daily_budget * 2

    def _should_reset_window(
        self,
        budget: AIUsageBudget,
        segment_start: datetime,
        now: datetime,
    ) -> bool:
        window_started_at = self._as_utc(budget.window_started_at)
        if window_started_at < segment_start:
            return True
        if window_started_at.date() != now.date():
            return True
        if budget.cooldown_until and self._as_utc(budget.cooldown_until) <= now:
            return True
        return False

    async def _refresh_window_if_needed(self, budget: AIUsageBudget, now: datetime) -> None:
        _, segment_start, _ = self._segment_bounds(budget, now)
        if not self._should_reset_window(budget, segment_start, now):
            return
        budget.current_window_spent_usd = 0.0
        budget.window_started_at = now
        budget.cooldown_until = None
        budget.updated_at = now
        await self.session.flush()

    async def can_use_ai(self, telegram_id: int) -> BudgetAccessResult:
        budget = await self.get_active_budget(telegram_id)
        if not budget:
            return BudgetAccessResult(allowed=True)

        now = datetime.now(timezone.utc)
        if budget.cooldown_until and self._as_utc(budget.cooldown_until) > now:
            return BudgetAccessResult(allowed=False, message_key="ai_budget_cooldown")

        await self._refresh_window_if_needed(budget, now)

        segment, _, segment_end = self._segment_bounds(budget, now)
        if self._remaining_segment_budget(budget, segment) <= 0:
            await self._start_cooldown(budget, now)
            return BudgetAccessResult(allowed=False, message_key="ai_budget_cooldown")

        threshold = self._current_threshold_usd(budget, segment, segment_end, now)
        if threshold > 0 and budget.current_window_spent_usd >= threshold:
            await self._start_cooldown(budget, now)
            return BudgetAccessResult(allowed=False, message_key="ai_budget_cooldown")

        return BudgetAccessResult(allowed=True)

    def calculate_cost_usd(self, result: AIUsageResult) -> float:
        pricing = MODEL_PRICING_USD_PER_1M.get(result.model)
        if not pricing:
            return 0.0
        input_price, output_price = pricing
        return (
            (result.prompt_tokens / 1_000_000) * input_price
            + (result.completion_tokens / 1_000_000) * output_price
        )

    async def record_usage(
        self,
        telegram_id: int,
        result: Optional[AIUsageResult],
        source: str,
    ) -> BudgetRecordResult:
        if not result:
            return BudgetRecordResult(cost_usd=0.0)

        cost_usd = self.calculate_cost_usd(result)
        budget = await self.get_active_budget(telegram_id)
        now = datetime.now(timezone.utc)

        event = AIUsageEvent(
            budget_id=budget.id if budget else None,
            user_telegram_id=telegram_id,
            source=source,
            model=result.model,
            prompt_tokens=result.prompt_tokens,
            completion_tokens=result.completion_tokens,
            total_tokens=result.total_tokens,
            cost_usd=cost_usd,
            created_at=now,
        )
        self.session.add(event)

        if not budget or cost_usd <= 0:
            await self.session.flush()
            return BudgetRecordResult(cost_usd=cost_usd)

        await self._refresh_window_if_needed(budget, now)
        segment, _, segment_end = self._segment_bounds(budget, now)
        threshold = self._current_threshold_usd(budget, segment, segment_end, now)

        self._set_segment_spent(
            budget,
            segment,
            self._segment_spent(budget, segment) + cost_usd,
        )
        budget.current_window_spent_usd += cost_usd
        budget.updated_at = now

        cooldown_started = threshold > 0 and budget.current_window_spent_usd >= threshold
        if cooldown_started:
            await self._start_cooldown(budget, now, flush=False)

        await self.session.flush()
        return BudgetRecordResult(
            cost_usd=cost_usd,
            cooldown_started=cooldown_started,
            message_key="ai_budget_cooldown_notice" if cooldown_started else "",
        )

    async def _start_cooldown(self, budget: AIUsageBudget, now: datetime, *, flush: bool = True) -> None:
        budget.cooldown_until = now + timedelta(hours=COOLDOWN_HOURS)
        budget.updated_at = now
        if flush:
            await self.session.flush()
