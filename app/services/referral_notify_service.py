from aiogram import Bot

from app.bot.utils.i18n import t


class ReferralNotifyService:
    async def notify_bonus_received(
        self,
        bot: Bot,
        referrer_user,
    ) -> None:
        if not referrer_user:
            return

        lang = referrer_user.language if referrer_user.language else "ru"
        text = t("referral_bonus_received", lang)

        try:
            await bot.send_message(
                chat_id=referrer_user.telegram_id,
                text=text,
            )
        except Exception:
            pass
