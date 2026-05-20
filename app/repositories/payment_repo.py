from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.payment import Payment


class PaymentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_telegram_id: int,
        plan_type: str,
        amount: int,
        currency: str = "somoni",
        screenshot_file_id: Optional[str] = None,
        payment_status: str = "pending",
        payment_method: Optional[str] = None,
        base_amount: Optional[int] = None,
        discount_source: str = "none",
        discount_percent: int = 0,
        discount_campaign_id: Optional[int] = None,
        discount_title: Optional[str] = None,
        discount_details: Optional[str] = None,
    ) -> Payment:
        payment = Payment(
            user_telegram_id=user_telegram_id,
            plan_type=plan_type,
            payment_method=payment_method,
            base_amount=base_amount,
            amount=amount,
            currency=currency,
            payment_status=payment_status,
            screenshot_file_id=screenshot_file_id,
            discount_source=discount_source,
            discount_percent=discount_percent,
            discount_campaign_id=discount_campaign_id,
            discount_title=discount_title,
            discount_details=discount_details,
            submitted_at=datetime.now(timezone.utc),
        )
        self.session.add(payment)
        await self.session.flush()
        return payment

    async def get_by_id(self, payment_id: int) -> Optional[Payment]:
        result = await self.session.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        return result.scalar_one_or_none()

    async def get_latest_draft_by_user(
        self,
        user_telegram_id: int,
    ) -> Optional[Payment]:
        result = await self.session.execute(
            select(Payment)
            .where(Payment.user_telegram_id == user_telegram_id)
            .where(Payment.payment_status == "draft")
            .order_by(Payment.submitted_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def update_checkout(
        self,
        payment: Payment,
        *,
        plan_type: str,
        amount: int,
        currency: str,
        payment_method: Optional[str],
        base_amount: Optional[int],
        payment_status: Optional[str] = None,
        screenshot_file_id: Optional[str] = None,
        discount_source: str = "none",
        discount_percent: int = 0,
        discount_campaign_id: Optional[int] = None,
        discount_title: Optional[str] = None,
        discount_details: Optional[str] = None,
    ) -> None:
        payment.plan_type = plan_type
        payment.payment_method = payment_method
        payment.base_amount = base_amount
        payment.amount = amount
        payment.currency = currency
        payment.discount_source = discount_source
        payment.discount_percent = discount_percent
        payment.discount_campaign_id = discount_campaign_id
        payment.discount_title = discount_title
        payment.discount_details = discount_details
        if payment_status:
            payment.payment_status = payment_status
        if screenshot_file_id:
            payment.screenshot_file_id = screenshot_file_id
        payment.submitted_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def get_latest_pending_by_user(
        self,
        user_telegram_id: int,
    ) -> Optional[Payment]:
        result = await self.session.execute(
            select(Payment)
            .where(Payment.user_telegram_id == user_telegram_id)
            .where(Payment.payment_status == "pending")
            .order_by(Payment.submitted_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def has_pending_by_user(
        self,
        user_telegram_id: int,
    ) -> bool:
        result = await self.session.execute(
            select(Payment.id)
            .where(Payment.user_telegram_id == user_telegram_id)
            .where(Payment.payment_status == "pending")
            .limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def list_by_user(
        self,
        user_telegram_id: int,
        limit: int = 20,
    ) -> List[Payment]:
        result = await self.session.execute(
            select(Payment)
            .where(Payment.user_telegram_id == user_telegram_id)
            .order_by(Payment.submitted_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update_screenshot(
        self,
        payment: Payment,
        screenshot_file_id: str,
    ) -> None:
        payment.screenshot_file_id = screenshot_file_id
        payment.payment_status = "pending"
        payment.submitted_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def approve(
        self,
        payment: Payment,
        admin_comment: Optional[str] = None,
    ) -> None:
        payment.payment_status = "approved"
        payment.admin_comment = admin_comment
        payment.reviewed_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def reject(
        self,
        payment: Payment,
        admin_comment: Optional[str] = None,
    ) -> None:
        payment.payment_status = "rejected"
        payment.admin_comment = admin_comment
        payment.reviewed_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def count_pending(self) -> int:
        from sqlalchemy import func
        result = await self.session.execute(
            select(func.count()).where(Payment.payment_status == "pending")
        )
        return result.scalar() or 0
