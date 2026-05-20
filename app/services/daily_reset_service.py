from datetime import datetime, timezone

from aiogram import Bot
from sqlalchemy import select

from app.db.models.user import User
from app.bot.utils.i18n import t


class DailyResetService:
    def __init__(self, session):
        self.session = session

    async def send_daily_reset_notifications(self, bot: Bot) -> int:
        today = datetime.now(timezone.utc).date()
        now = datetime.now(timezone.utc)

        result = await self.session.execute(
            select(User).where(User.status == "trial")
        )
        users = list(result.scalars().all())

        sent_count = 0

        for user in users:
            needs_reset = (
                user.last_limit_reset_at is None
                or user.last_limit_reset_at.date() < today
            )
            if not needs_reset:
                continue

            should_notify = user.questions_used > 0

            user.questions_used = 0
            user.bonus_questions_used = 0
            user.last_limit_reset_at = now

            if should_notify:
                lang = user.language if user.language else "ru"
                try:
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=t("daily_limit_renewed", lang),
                    )
                    sent_count += 1
                except Exception:
                    pass

        await self.session.commit()
        return sent_count
