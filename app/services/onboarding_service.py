from typing import Optional, Tuple

from sqlalchemy.exc import IntegrityError

from app.repositories.user_repo import UserRepository
from app.db.models.user import User
from app.services.referral_service import ReferralService


class OnboardingService:
    def __init__(self, session):
        self.session = session
        self.user_repo = UserRepository(session)
        self.referral_service = ReferralService(session)

    async def get_or_create_user(
        self,
        telegram_id: int,
        full_name: Optional[str] = None,
        username: Optional[str] = None,
        referral_code: Optional[str] = None,
    ) -> Tuple[User, bool]:
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if user:
            changed = False
            if full_name and user.full_name != full_name:
                user.full_name = full_name
                changed = True
            if username and user.username != username:
                user.username = username
                changed = True
            if changed:
                await self.session.flush()
            return user, False

        try:
            user = await self.user_repo.create(
                telegram_id=telegram_id,
                full_name=full_name,
                username=username,
                language="tj",
                level="beginner",
            )
        except IntegrityError:
            await self.session.rollback()
            user = await self.user_repo.get_by_telegram_id(telegram_id)
            return user, False

        await self.referral_service.attach_referral_if_needed(
            invited_user_telegram_id=telegram_id,
            referral_code=referral_code,
        )

        user = await self.user_repo.get_by_telegram_id(telegram_id)
        return user, True
