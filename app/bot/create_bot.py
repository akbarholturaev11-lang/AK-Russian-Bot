from app.db.session import async_session_maker
from app.bot.middlewares.db import DBSessionMiddleware
from app.bot.middlewares.required_channel import RequiredChannelMiddleware
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.db.session import init_db

from app.bot.handlers.start import router as start_router
from app.bot.handlers.required_channel import router as required_channel_router
from app.bot.handlers.commands import router as commands_router
from app.bot.handlers.referral import router as referral_router
from app.bot.handlers.subscription import router as subscription_router
from app.bot.handlers.menu import router as menu_router
from app.bot.handlers.payments import router as payments_router
from app.bot.handlers.admin_payments import router as admin_payments_router
from app.bot.handlers.admin_broadcast import router as admin_broadcast_router
from app.bot.handlers.admin_ads import router as admin_ads_router
from app.bot.handlers.admin_discount import router as admin_discount_router
from app.bot.handlers.feedback import router as feedback_router
from app.bot.handlers.messages import router as messages_router
from app.bot.handlers.course import router as course_router
from app.bot.handlers.admin import router as admin_router
from app.bot.handlers.admin_audio import router as admin_audio_router


def create_bot(settings):
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.middleware(DBSessionMiddleware(async_session_maker))
    dp.callback_query.middleware(DBSessionMiddleware(async_session_maker))
    dp.message.middleware(RequiredChannelMiddleware(async_session_maker))
    dp.callback_query.middleware(RequiredChannelMiddleware(async_session_maker))

    dp.include_router(required_channel_router)
    dp.include_router(start_router)
    dp.include_router(commands_router)
    dp.include_router(admin_discount_router)
    dp.include_router(admin_broadcast_router)
    dp.include_router(admin_ads_router)
    dp.include_router(admin_audio_router)   # admin FSM flows must stay before generic text/photo handlers
    dp.include_router(feedback_router)
    dp.include_router(referral_router)
    dp.include_router(subscription_router)
    dp.include_router(menu_router)
    dp.include_router(payments_router)
    dp.include_router(admin_payments_router)
    dp.include_router(course_router)
    dp.include_router(admin_router)
    dp.include_router(messages_router)

    return bot, dp

import asyncio
from app.config import settings


async def main():
    await init_db()
    bot, dp = create_bot(settings)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
