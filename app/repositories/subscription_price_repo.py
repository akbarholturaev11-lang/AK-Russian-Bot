from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.subscription_price import SubscriptionPrice


class SubscriptionPriceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, payment_method: str, plan_type: str) -> Optional[SubscriptionPrice]:
        result = await self.session.execute(
            select(SubscriptionPrice).where(
                SubscriptionPrice.payment_method == payment_method,
                SubscriptionPrice.plan_type == plan_type,
            )
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[SubscriptionPrice]:
        result = await self.session.execute(
            select(SubscriptionPrice).order_by(
                SubscriptionPrice.payment_method.asc(),
                SubscriptionPrice.plan_type.asc(),
            )
        )
        return list(result.scalars().all())

    async def set_price(
        self,
        *,
        payment_method: str,
        plan_type: str,
        amount: int,
        currency: str,
        updated_by_telegram_id: int | None = None,
    ) -> SubscriptionPrice:
        price = await self.get(payment_method, plan_type)
        if price:
            price.amount = amount
            price.currency = currency
            price.updated_by_telegram_id = updated_by_telegram_id
        else:
            price = SubscriptionPrice(
                payment_method=payment_method,
                plan_type=plan_type,
                amount=amount,
                currency=currency,
                updated_by_telegram_id=updated_by_telegram_id,
            )
            self.session.add(price)
        await self.session.flush()
        return price
