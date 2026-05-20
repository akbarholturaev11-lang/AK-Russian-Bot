from typing import Optional

from app.repositories.payment_repo import PaymentRepository
from app.repositories.user_repo import UserRepository
from app.services.discount_service import DiscountService
from app.services.subscription_price_service import SubscriptionPriceService


PLAN_PRICES = {
    "10_days": 29,
    "1_month": 89,
}

DISCOUNT_PERCENT = 20


class PaymentService:
    def __init__(self, session):
        self.session = session
        self.payment_repo = PaymentRepository(session)
        self.user_repo = UserRepository(session)

    def get_plan_price(self, plan_type: str) -> Optional[int]:
        return PLAN_PRICES.get(plan_type)

    async def get_plan_price_value(self, payment_method: str | None, plan_type: str):
        return await SubscriptionPriceService(self.session).get_price(payment_method, plan_type)

    def calculate_discounted_price(self, amount: int) -> int:
        discounted = amount * (100 - DISCOUNT_PERCENT) / 100
        return int(round(discounted))

    def calculate_percent_discounted_price(self, amount: int, percent: int) -> int:
        discounted = amount * (100 - percent) / 100
        return int(round(discounted))

    async def get_checkout_info(
        self,
        user,
        plan_type: str,
        force_admin_discount: bool = False,
        admin_discount_campaign_id: Optional[int] = None,
        force_feedback_discount: bool = False,
        feedback_id: Optional[int] = None,
    ):
        price = await self.get_plan_price_value(user.payment_method, plan_type)
        if price is None:
            return None

        base_amount = price.amount
        currency = price.currency

        discount_service = DiscountService(self.session)
        if force_feedback_discount:
            discount = await discount_service.get_feedback_price_discount(
                user=user,
                feedback_id=feedback_id,
            )
        elif force_admin_discount:
            if admin_discount_campaign_id:
                discount = await discount_service.get_campaign_discount(
                    campaign_id=admin_discount_campaign_id,
                    user=user,
                    plan_type=plan_type,
                    payment_method=user.payment_method,
                )
            else:
                discount = await discount_service.get_best_admin_discount(
                    user=user,
                    plan_type=plan_type,
                    payment_method=user.payment_method,
                )
        else:
            discount = await discount_service.get_best_discount(
                user=user,
                plan_type=plan_type,
                payment_method=user.payment_method,
            )

        if force_feedback_discount and discount.source != "feedback_price_offer":
            return None
        if force_admin_discount and discount.source != "admin_campaign":
            return None

        discount_applied = discount.percent > 0
        final_amount = self.calculate_percent_discounted_price(base_amount, discount.percent) if discount_applied else base_amount

        return {
            "plan_type": plan_type,
            "base_amount": base_amount,
            "final_amount": final_amount,
            "currency": currency,
            "discount_applied": discount_applied,
            "discount_percent": discount.percent,
            "discount_source": discount.source,
            "discount_campaign_id": discount.campaign_id,
            "discount_title": discount.title,
            "discount_details": discount.details,
        }

    async def create_checkout_draft(
        self,
        telegram_id: int,
        plan_type: str,
        force_admin_discount: bool = False,
        admin_discount_campaign_id: Optional[int] = None,
        force_feedback_discount: bool = False,
        feedback_id: Optional[int] = None,
    ):
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            return None, None, "access_start_first"

        checkout_info = await self.get_checkout_info(
            user=user,
            plan_type=plan_type,
            force_admin_discount=force_admin_discount,
            admin_discount_campaign_id=admin_discount_campaign_id,
            force_feedback_discount=force_feedback_discount,
            feedback_id=feedback_id,
        )
        if not checkout_info:
            return None, None, "payment_invalid_plan"

        draft = await self.payment_repo.get_latest_draft_by_user(telegram_id)
        if draft:
            await self.payment_repo.update_checkout(
                draft,
                plan_type=plan_type,
                amount=checkout_info["final_amount"],
                currency=checkout_info["currency"],
                payment_method=user.payment_method,
                base_amount=checkout_info["base_amount"],
                payment_status="draft",
                discount_source=checkout_info["discount_source"],
                discount_percent=checkout_info["discount_percent"],
                discount_campaign_id=checkout_info["discount_campaign_id"],
                discount_title=checkout_info["discount_title"],
                discount_details=checkout_info["discount_details"],
            )
            await self.session.commit()
            return draft, checkout_info, ""

        payment = await self.payment_repo.create(
            user_telegram_id=telegram_id,
            plan_type=plan_type,
            amount=checkout_info["final_amount"],
            currency=checkout_info["currency"],
            payment_status="draft",
            payment_method=user.payment_method,
            base_amount=checkout_info["base_amount"],
            discount_source=checkout_info["discount_source"],
            discount_percent=checkout_info["discount_percent"],
            discount_campaign_id=checkout_info["discount_campaign_id"],
            discount_title=checkout_info["discount_title"],
            discount_details=checkout_info["discount_details"],
        )
        await self.session.commit()
        return payment, checkout_info, ""

    async def create_pending_payment(
        self,
        telegram_id: int,
        plan_type: str,
        screenshot_file_id: Optional[str] = None,
        force_admin_discount: bool = False,
        admin_discount_campaign_id: Optional[int] = None,
    ):
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            return None, "access_start_first"

        checkout_info = await self.get_checkout_info(
            user=user,
            plan_type=plan_type,
            force_admin_discount=force_admin_discount,
            admin_discount_campaign_id=admin_discount_campaign_id,
        )
        if not checkout_info:
            return None, "payment_invalid_plan"

        payment = await self.payment_repo.create(
            user_telegram_id=telegram_id,
            plan_type=plan_type,
            amount=checkout_info["final_amount"],
            currency=checkout_info["currency"],
            screenshot_file_id=screenshot_file_id,
            payment_status="pending",
            payment_method=user.payment_method,
            base_amount=checkout_info["base_amount"],
            discount_source=checkout_info["discount_source"],
            discount_percent=checkout_info["discount_percent"],
            discount_campaign_id=checkout_info["discount_campaign_id"],
            discount_title=checkout_info["discount_title"],
            discount_details=checkout_info["discount_details"],
        )
        await self.session.commit()
        return payment, ""

    async def get_latest_pending_payment(
        self,
        telegram_id: int,
    ):
        return await self.payment_repo.get_latest_pending_by_user(telegram_id)

    async def attach_or_create_payment_screenshot(
        self,
        telegram_id: int,
        plan_type: str,
        screenshot_file_id: str,
    ):
        draft_payment = await self.payment_repo.get_latest_draft_by_user(telegram_id)

        if draft_payment:
            if draft_payment.plan_type != plan_type:
                user = await self.user_repo.get_by_telegram_id(telegram_id)
                checkout_info = await self.get_checkout_info(
                    user=user,
                    plan_type=plan_type,
                    force_admin_discount=draft_payment.discount_source == "admin_campaign",
                    admin_discount_campaign_id=draft_payment.discount_campaign_id,
                    force_feedback_discount=draft_payment.discount_source == "feedback_price_offer",
                )
                if not checkout_info:
                    return None, "payment_invalid_plan"
                await self.payment_repo.update_checkout(
                    draft_payment,
                    plan_type=plan_type,
                    amount=checkout_info["final_amount"],
                    currency=checkout_info["currency"],
                    payment_method=user.payment_method,
                    base_amount=checkout_info["base_amount"],
                    payment_status="pending",
                    screenshot_file_id=screenshot_file_id,
                    discount_source=checkout_info["discount_source"],
                    discount_percent=checkout_info["discount_percent"],
                    discount_campaign_id=checkout_info["discount_campaign_id"],
                    discount_title=checkout_info["discount_title"],
                    discount_details=checkout_info["discount_details"],
                )
            else:
                await self.payment_repo.update_screenshot(draft_payment, screenshot_file_id)
            await self.session.commit()
            return draft_payment, "updated"

        pending_payment = await self.payment_repo.get_latest_pending_by_user(telegram_id)
        if pending_payment:
            await self.payment_repo.update_screenshot(pending_payment, screenshot_file_id)
            await self.session.commit()
            return pending_payment, "updated"

        payment, error_key = await self.create_pending_payment(
            telegram_id=telegram_id,
            plan_type=plan_type,
            screenshot_file_id=screenshot_file_id,
        )
        if error_key:
            return None, error_key

        return payment, "created"
