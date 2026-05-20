from typing import Optional

from aiogram import Bot

from app.repositories.user_repo import UserRepository
from app.repositories.referral_repo import ReferralRepository
from app.services.referral_notify_service import ReferralNotifyService
from app.services.subscription_progress_service import SubscriptionProgressService


class ReferralService:
    def __init__(self, session):
        self.session = session
        self.user_repo = UserRepository(session)
        self.referral_repo = ReferralRepository(session)
        self.referral_notify_service = ReferralNotifyService()
        self.subscription_progress_service = SubscriptionProgressService(session)

    async def attach_referral_if_needed(
        self,
        invited_user_telegram_id: int,
        referral_code: Optional[str],
    ) -> None:
        if not referral_code:
            return

        invited_user = await self.user_repo.get_by_telegram_id(invited_user_telegram_id)
        if not invited_user:
            return

        if invited_user.referred_by_telegram_id:
            return

        referrer = await self.user_repo.get_by_referral_code(referral_code)
        if not referrer:
            return

        if referrer.telegram_id == invited_user_telegram_id:
            return

        existing_referral = await self.referral_repo.get_by_pair(
            referrer_telegram_id=referrer.telegram_id,
            invited_user_telegram_id=invited_user_telegram_id,
        )
        if existing_referral:
            return

        await self.user_repo.set_referred_by(invited_user, referrer.telegram_id)
        await self.referral_repo.create(
            referrer_telegram_id=referrer.telegram_id,
            invited_user_telegram_id=invited_user_telegram_id,
        )
        await self.session.commit()

    async def activate_referral_if_eligible(
        self,
        bot: Bot,
        invited_user_telegram_id: int,
    ) -> None:
        referral = await self.referral_repo.get_by_invited_user_telegram_id(
            invited_user_telegram_id
        )
        if not referral:
            return

        if referral.status == "active":
            return

        invited_user = await self.user_repo.get_by_telegram_id(invited_user_telegram_id)
        if not invited_user:
            return

        if invited_user.questions_used < 2:
            return

        await self.referral_repo.activate(referral)

        referrer = await self.user_repo.get_by_telegram_id(referral.referrer_telegram_id)
        if not referrer:
            await self.session.commit()
            return

        bonus_given_now = False

        if not referral.bonus_granted:
            await self.user_repo.add_bonus_questions(referrer, 5)
            referral.bonus_granted = True
            bonus_given_now = True

        if (
            referrer.discount_offer_started_at
            and referral.activated_at
            and referral.activated_at >= referrer.discount_offer_started_at
            and not referral.counts_for_discount
        ):
            await self.user_repo.increment_discount_referral_count(referrer, 1)
            referral.counts_for_discount = True

        await self.session.commit()

        if bonus_given_now and not referrer.discount_progress_message_id:
            await self.referral_notify_service.notify_bonus_received(
                bot=bot,
                referrer_user=referrer,
            )

        await self.subscription_progress_service.update_discount_progress_message(
            bot=bot,
            referrer_user=referrer,
        )
