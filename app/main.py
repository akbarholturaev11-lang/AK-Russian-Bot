import asyncio
import contextlib
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

from aiogram import Bot
from fastapi import FastAPI

from app.config import COURSE_MODE_ENABLED, settings
from app.bot.create_bot import create_bot
from app.db.session import async_session_maker, init_db
from app.services.course_seed_service import CourseSeedService
from app.services.access_service import AccessService
from app.services.daily_reset_service import DailyResetService
from app.services.expiry_reminder_service import ExpiryReminderService
from app.services.course_reminder_service import CourseReminderService
from app.services.bot_feedback_service import BotFeedbackService
from app.services.ad_campaign_service import AdCampaignService

logger = logging.getLogger(__name__)

bot, dp = create_bot(settings)
_last_feedback_check_at = None


async def _seed_lessons() -> None:
    """Run all lesson seed scripts in the background after startup."""
    if not COURSE_MODE_ENABLED:
        logger.info("=== SEEDING SKIPPED: course mode disabled ===")
        return

    logger.info("=== SEEDING START: loading all lesson scripts ===")
    try:
        async with async_session_maker() as session:
            count = await CourseSeedService(session).sync_all_lessons()
        logger.info(f"=== SEEDING COMPLETE: {count} lessons in DB ===")
    except Exception as e:
        logger.error(f"=== SEEDING ERROR: {e} ===", exc_info=True)


async def _background_scheduler(bot: Bot) -> None:
    global _last_feedback_check_at

    while True:
        await asyncio.sleep(60)
        try:
            async with async_session_maker() as session:
                await AccessService(session).downgrade_expired_active_users()
            async with async_session_maker() as session:
                await DailyResetService(session).send_daily_reset_notifications(bot)
            async with async_session_maker() as session:
                await ExpiryReminderService(session).send_expiry_reminders(bot)
            async with async_session_maker() as session:
                await CourseReminderService(session).send_due_reminders(bot)
            if COURSE_MODE_ENABLED:
                async with async_session_maker() as session:
                    await CourseReminderService(session).send_weekly_progress_reports(bot)
            async with async_session_maker() as session:
                await BotFeedbackService(session).send_due_price_discount_offers(bot)
            async with async_session_maker() as session:
                await AdCampaignService(session).send_due_ads(bot)
            now = datetime.now(timezone.utc)
            if (
                _last_feedback_check_at is None
                or now - _last_feedback_check_at >= timedelta(hours=24)
            ):
                async with async_session_maker() as session:
                    await BotFeedbackService(session).send_due_feedback_requests(bot)
                _last_feedback_check_at = now
        except Exception as e:
            print("Scheduler error:", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()                                          # faqat jadval yaratish (tez)
    seed_task = asyncio.create_task(_seed_lessons())        # background seeding
    polling_task = asyncio.create_task(dp.start_polling(bot))
    scheduler_task = asyncio.create_task(_background_scheduler(bot))
    try:
        yield                                                # /health darhol ishlaydi
    finally:
        seed_task.cancel()
        polling_task.cancel()
        scheduler_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await seed_task
        with contextlib.suppress(asyncio.CancelledError):
            await polling_task
        with contextlib.suppress(asyncio.CancelledError):
            await scheduler_task
        await bot.session.close()


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}
