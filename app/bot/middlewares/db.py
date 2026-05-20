from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable

from app.repositories.user_repo import UserRepository


class DBSessionMiddleware(BaseMiddleware):
    def __init__(self, sessionmaker):
        self.sessionmaker = sessionmaker

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any]
    ):
        async with self.sessionmaker() as session:
            data["session"] = session
            tg_user = getattr(event, "from_user", None)
            if tg_user:
                user = await UserRepository(session).get_by_telegram_id(tg_user.id)
                if user:
                    changed = False
                    if tg_user.full_name and user.full_name != tg_user.full_name:
                        user.full_name = tg_user.full_name
                        changed = True
                    if tg_user.username and user.username != tg_user.username:
                        user.username = tg_user.username
                        changed = True
                    if changed:
                        await session.commit()
            return await handler(event, data)
