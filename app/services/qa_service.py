from typing import Optional

from aiogram import Bot

from app.repositories.user_repo import UserRepository
from app.repositories.message_repo import MessageRepository
from app.services.ai_service import AIService
from app.services.ai_usage_budget_service import AIUsageBudgetService
from app.services.referral_service import ReferralService
from app.services.access_service import AccessService


QA_MODEL = "gpt-4o-mini"
QA_MAX_COMPLETION_TOKENS = 900


class QAService:
    def __init__(self, session):
        self.session = session
        self.user_repo = UserRepository(session)
        self.message_repo = MessageRepository(session)
        self.ai_service = AIService()
        self.referral_service = ReferralService(session)
        self.access_service = AccessService(session)
        self.last_budget_record = None

    async def handle_user_message(
        self,
        bot: Bot,
        telegram_id: int,
        text: str,
        telegram_message_id: Optional[int] = None,
    ) -> str:
        can_use, message_key = await self.access_service.can_use_text_ai(telegram_id)
        if not can_use:
            return message_key

        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            return "access_start_first"

        cleaned_text = text.strip()
        if not cleaned_text:
            return "access_start_first"

        recent_messages = await self.message_repo.get_recent_by_user(
            user_id=user.id,
            limit=5,
        )

        history = [
            {
                "role": msg.role,
                "content": msg.content,
            }
            for msg in recent_messages
            if msg.role in ("user", "assistant")
            and msg.content_type not in ("image_context", "voice", "voice_translator")
        ]

        latest_image_context = await self.message_repo.get_latest_image_context_by_user(
            user_id=user.id,
        )
        if latest_image_context:
            history.insert(
                0,
                {
                    "role": "system",
                    "content": latest_image_context.content,
                },
            )

        onboarding_challenge = await self.message_repo.get_latest_by_content_type(
            user_id=user.id,
            content_type="onboarding_challenge",
        )
        if onboarding_challenge:
            history.insert(
                0,
                {
                    "role": "user",
                    "content": f"[Context for this conversation: {onboarding_challenge.content}]",
                },
            )

        await self.message_repo.create(
            user_id=user.id,
            role="user",
            content=cleaned_text,
            content_type="text",
            telegram_message_id=telegram_message_id,
        )

        usage_result = await self.ai_service.generate_reply_with_usage(
            text=cleaned_text,
            user_language=user.language,
            user_level=user.level,
            history=history,
            model_override=QA_MODEL,
            max_completion_tokens=QA_MAX_COMPLETION_TOKENS,
        )
        assistant_reply = usage_result.content

        await self.message_repo.create(
            user_id=user.id,
            role="assistant",
            content=assistant_reply,
            content_type="text",
        )
        self.last_budget_record = await AIUsageBudgetService(self.session).record_usage(
            telegram_id=telegram_id,
            result=usage_result,
            source="qa",
        )

        await self.access_service.consume_one_question(telegram_id)

        await self.referral_service.activate_referral_if_eligible(
            bot=bot,
            invited_user_telegram_id=telegram_id,
        )

        await self.session.commit()
        return assistant_reply
