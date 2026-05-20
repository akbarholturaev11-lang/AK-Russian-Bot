import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings
from app.db.base import Base


async def init():
    engine = create_async_engine(settings.DATABASE_URL)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(init())
