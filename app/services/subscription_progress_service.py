from aiogram import Bot

from app.config import settings
from app.bot.handlers.subscription import build_subscription_discount_progress_text
from app.bot.keyboards.subscription import (
    subscription_discount_progress_keyboard,
    subscription_discount_ready_keyboard,
)


class SubscriptionProgressService:
    def __init__(self, session):
        self.session = session

    async def update_discount_progress_message(
        self,
        bot: Bot,
        referrer_user,
    ) -> None:
        if not referrer_user:
            return

        if not referrer_user.discount_progress_chat_id or not referrer_user.discount_progress_message_id:
            return

        lang = referrer_user.language if referrer_user.language else "ru"
        referral_link = f"https://t.me/{settings.BOT_USERNAME}?start={referrer_user.referral_code}"
        count = referrer_user.discount_referral_count

        try:
            text = await build_subscription_discount_progress_text(
                self.session,
                lang,
                referral_link,
                count,
                discount_eligible=referrer_user.discount_eligible,
                discount_used=referrer_user.discount_used,
                payment_method=referrer_user.payment_method,
            )
            keyboard = (
                subscription_discount_ready_keyboard(lang)
                if referrer_user.discount_eligible and not referrer_user.discount_used
                else subscription_discount_progress_keyboard(lang)
            )
            await bot.edit_message_text(
                chat_id=referrer_user.discount_progress_chat_id,
                message_id=referrer_user.discount_progress_message_id,
                text=text,
                reply_markup=keyboard,
                disable_web_page_preview=True,
            )
        except Exception:
            pass
