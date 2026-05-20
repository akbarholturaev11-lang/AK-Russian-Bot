import asyncio
from sqlalchemy import text
from app.db.session import async_session_maker

TABLES = [
    "course_attempts",
    "course_progress",
    "referrals",
    "messages",
    "payments",
    "users"
]

async def clean():
    async with async_session_maker() as session:
        for table in TABLES:
            await session.execute(text(f"DELETE FROM {table}"))
            print(f"cleared: {table}")

        await session.commit()
        print("🔥 FULL CLEAN DONE")

if __name__ == "__main__":
    asyncio.run(clean())
