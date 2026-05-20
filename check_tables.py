import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.config import settings


async def main():
    engine = create_async_engine(settings.DATABASE_URL)

    async with engine.begin() as conn:
        result = await conn.run_sync(
            lambda c: c.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
        )
        print(result.fetchall())


asyncio.run(main())
