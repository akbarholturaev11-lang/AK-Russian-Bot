from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.referral import Referral


class ReferralRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_invited_user_telegram_id(
        self,
        invited_user_telegram_id: int,
    ) -> Optional[Referral]:
        result = await self.session.execute(
            select(Referral).where(
                Referral.invited_user_telegram_id == invited_user_telegram_id
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        referrer_telegram_id: int,
        invited_user_telegram_id: int,
    ) -> Referral:
        referral = Referral(
            referrer_telegram_id=referrer_telegram_id,
            invited_user_telegram_id=invited_user_telegram_id,
            status="pending",
            bonus_granted=False,
            counts_for_discount=False,
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(referral)
        await self.session.flush()
        return referral

    async def activate(
        self,
        referral: Referral,
    ) -> Referral:
        referral.status = "active"
        referral.activated_at = datetime.now(timezone.utc)
        await self.session.flush()
        return referral

    async def list_active_after_datetime(
        self,
        referrer_telegram_id: int,
        started_at: datetime,
    ) -> List[Referral]:
        result = await self.session.execute(
            select(Referral)
            .where(Referral.referrer_telegram_id == referrer_telegram_id)
            .where(Referral.status == "active")
            .where(Referral.activated_at.is_not(None))
            .where(Referral.activated_at >= started_at)
            .order_by(Referral.activated_at.asc())
        )
        return list(result.scalars().all())
    
    from sqlalchemy import select

    async def get_by_pair(self, referrer_telegram_id: int, invited_user_telegram_id: int):
        result = await self.session.execute(
            select(Referral).where(
                Referral.referrer_telegram_id == referrer_telegram_id,
                Referral.invited_user_telegram_id == invited_user_telegram_id,
            )
        )
        return result.scalar_one_or_none()     
