import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.session import async_session_maker
from app.services.course_seed_service import CourseSeedService


async def main():
    async with async_session_maker() as session:
        total = await CourseSeedService(session).sync_all_lessons()
        print(f"Synced {total} course lessons.")


if __name__ == "__main__":
    asyncio.run(main())
