from datetime import datetime, timezone, timedelta

from aiogram import Bot

from app.repositories.user_repo import UserRepository
from app.bot.utils.i18n import t


class ExpiryReminderService:
    def __init__(self, session):
        self.session = session
        self.user_repo = UserRepository(session)

    async def send_expiry_reminders(self, bot: Bot) -> int:
        tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).date()
        users = await self.user_repo.list_active_users_expiring_on(tomorrow)

        sent_count = 0

        for user in users:
            if user.expiry_reminder_sent_at is not None:
                continue

            lang = user.language if user.language else "ru"
            text = t("subscription_expires_tomorrow", lang)

            try:
                await bot.send_message(
                    chat_id=user.telegram_id,
                    text=text,
                )
                user.expiry_reminder_sent_at = datetime.now(timezone.utc)
                sent_count += 1
            except Exception:
                pass

        await self.session.commit()
        return sent_count
