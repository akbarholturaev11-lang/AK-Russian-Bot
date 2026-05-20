from datetime import datetime, timezone, timedelta

from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.course_progress import CourseProgress
from app.db.models.user import User
from app.bot.utils.i18n import t
from app.services.course_progress_summary_service import CourseProgressSummaryService


def _reminder_keyboard(lang: str):
    labels = {
        "uz": "📖 Darsni davom ettirish",
        "ru": "📖 Продолжить урок",
        "tj": "📖 Идома додани дарс",
    }
    builder = InlineKeyboardBuilder()
    builder.button(text=labels.get(lang, labels["ru"]), callback_data="course:continue")
    return builder.as_markup()


class CourseReminderService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _build_reminder_text(self, progress: CourseProgress, lang: str) -> str:
        summary = await CourseProgressSummaryService(self.session).summarize_last_completed_lesson(progress)
        return t(
            "course_reminder_text",
            lang,
            vocab=summary["vocab"],
            dialogues=summary["dialogues"],
        )

    async def send_due_reminders(self, bot: Bot) -> None:
        now_utc = datetime.now(timezone.utc)

        result = await self.session.execute(
            select(CourseProgress, User)
            .join(User, CourseProgress.user_id == User.id)
            .where(CourseProgress.reminder_enabled.is_(True))
            .where(CourseProgress.reminder_time.isnot(None))
        )
        rows = result.all()

        for progress, user in rows:
            if not progress.reminder_time:
                continue

            tz_offset = getattr(progress, "reminder_tz_offset", 5) or 5
            local_now = now_utc + timedelta(hours=tz_offset)

            # Vaqtni moslashtirish (soat va daqiqa, ±2 daqiqa oynasi)
            rt = progress.reminder_time
            now_mins = local_now.hour * 60 + local_now.minute
            rem_mins = rt.hour * 60 + rt.minute
            if not (0 <= now_mins - rem_mins <= 2):
                continue

            # Bugun allaqachon yuborilganmi?
            if progress.last_reminder_sent_at:
                last_local = progress.last_reminder_sent_at + timedelta(hours=tz_offset)
                if last_local.date() == local_now.date():
                    continue

            lang = user.language if user.language else "ru"
            try:
                await bot.send_message(
                    chat_id=user.telegram_id,
                    text=await self._build_reminder_text(progress, lang),
                    reply_markup=_reminder_keyboard(lang),
                    parse_mode="HTML",
                )
                progress.last_reminder_sent_at = now_utc
                print(f"CourseReminderService: sent reminder to {user.telegram_id}")
            except Exception as e:
                print(f"CourseReminderService: failed to notify {user.telegram_id}: {e}")

        await self.session.commit()

    async def send_weekly_progress_reports(self, bot: Bot) -> None:
        now_utc = datetime.now(timezone.utc)

        result = await self.session.execute(
            select(CourseProgress, User)
            .join(User, CourseProgress.user_id == User.id)
            .where(CourseProgress.completed_lessons_count > 0)
            .where(User.status.in_(("trial", "active")))
        )
        rows = result.all()
        summary_service = CourseProgressSummaryService(self.session)

        for progress, user in rows:
            tz_offset = getattr(progress, "reminder_tz_offset", 5) or 5
            local_now = now_utc + timedelta(hours=tz_offset)

            if local_now.weekday() != 0:
                continue
            if not (9 * 60 <= local_now.hour * 60 + local_now.minute <= 9 * 60 + 2):
                continue

            if progress.last_weekly_progress_sent_at:
                last_local = progress.last_weekly_progress_sent_at + timedelta(hours=tz_offset)
                if last_local.isocalendar()[:2] == local_now.isocalendar()[:2]:
                    continue

            baseline = getattr(progress, "weekly_progress_baseline_lessons_count", 0) or 0
            summary = await summary_service.summarize_completed_range(
                progress,
                start_after=baseline,
            )

            if summary["lessons"] <= 0 and baseline > 0:
                continue

            lang = user.language if user.language else "ru"
            total_lessons = getattr(progress, "completed_lessons_count", 0) or 0

            try:
                await bot.send_message(
                    chat_id=user.telegram_id,
                    text=t(
                        "course_weekly_progress_text",
                        lang,
                        lessons=summary["lessons"],
                        vocab=summary["vocab"],
                        dialogues=summary["dialogues"],
                        total_lessons=total_lessons,
                    ),
                    reply_markup=_reminder_keyboard(lang),
                    parse_mode="HTML",
                )
                progress.last_weekly_progress_sent_at = now_utc
                progress.weekly_progress_baseline_lessons_count = total_lessons
                print(f"CourseReminderService: sent weekly progress to {user.telegram_id}")
            except Exception as e:
                print(f"CourseReminderService: failed weekly progress for {user.telegram_id}: {e}")

        await self.session.commit()
