import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone

from aiogram import Bot

from app.config import settings
from app.db.models.ad_campaign import AdCampaign
from app.repositories.ad_campaign_repo import AdCampaignRepository, decode_languages
from app.repositories.user_repo import UserRepository


@dataclass
class AdSendResult:
    campaign_id: int
    round_no: int
    total: int
    sent: int
    failed: int


async def send_ad_payload(
    bot: Bot,
    *,
    chat_id: int,
    text: str | None,
    content_type: str,
    media_file_id: str | None,
) -> None:
    if content_type == "photo" and media_file_id:
        await bot.send_photo(chat_id=chat_id, photo=media_file_id, caption=text or None)
    elif content_type == "video" and media_file_id:
        await bot.send_video(chat_id=chat_id, video=media_file_id, caption=text or None)
    else:
        await bot.send_message(chat_id=chat_id, text=text or "")


class AdCampaignService:
    def __init__(self, session):
        self.session = session
        self.repo = AdCampaignRepository(session)
        self.user_repo = UserRepository(session)

    async def send_due_ads(self, bot: Bot) -> list[AdSendResult]:
        now = datetime.now(timezone.utc)
        expired_count = await self.repo.deactivate_expired(now)
        campaigns = await self.repo.list_due(now)
        results = []

        for campaign in campaigns:
            results.append(await self._send_campaign_round(bot, campaign))

        if campaigns or expired_count:
            await self.session.commit()
        return results

    async def _send_campaign_round(self, bot: Bot, campaign: AdCampaign) -> AdSendResult:
        round_no = campaign.rounds_sent + 1
        users = await self.user_repo.get_ad_target_users(
            languages=decode_languages(campaign.target_languages),
            include_active_subscribers=campaign.include_active_subscribers,
        )
        admin_ids = set(settings.admin_id_list)
        already_done = await self.repo.list_delivered_user_ids(campaign.id, round_no)

        target_users = [
            user for user in users
            if user.telegram_id not in admin_ids and user.telegram_id not in already_done
        ]

        sent_count = 0
        failed_count = 0
        delivery_count = 0

        for user in target_users:
            status = "sent"
            error = None
            try:
                await send_ad_payload(
                    bot,
                    chat_id=user.telegram_id,
                    text=campaign.message_text,
                    content_type=campaign.content_type,
                    media_file_id=campaign.media_file_id,
                )
                sent_count += 1
            except Exception as exc:
                status = "failed"
                error = str(exc)
                failed_count += 1

            await self.repo.create_delivery(
                campaign_id=campaign.id,
                user_telegram_id=user.telegram_id,
                round_no=round_no,
                status=status,
                error=error,
            )
            delivery_count += 1
            if delivery_count % 20 == 0:
                await self.session.commit()
            await asyncio.sleep(0.05)

        await self.repo.mark_round_finished(campaign)
        return AdSendResult(
            campaign_id=campaign.id,
            round_no=round_no,
            total=len(target_users),
            sent=sent_count,
            failed=failed_count,
        )
