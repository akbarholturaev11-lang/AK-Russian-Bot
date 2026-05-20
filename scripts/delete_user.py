import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.session import engine


async def delete_user(telegram_id: int):
    async with engine.begin() as conn:
        result = await conn.execute(
            text("SELECT id, full_name FROM users WHERE telegram_id = :tid"),
            {"tid": telegram_id}
        )
        user = result.fetchone()

        if not user:
            print(f"User {telegram_id} not found.")
            return

        print(f"Found: id={user.id}, name={user.full_name}")

        await conn.execute(
            text("DELETE FROM users WHERE telegram_id = :tid"),
            {"tid": telegram_id}
        )
        print(f"Deleted user {telegram_id} (all related data removed via CASCADE).")


if __name__ == "__main__":
    tid = int(sys.argv[1]) if len(sys.argv) > 1 else 6935199446
    asyncio.run(delete_user(tid))
