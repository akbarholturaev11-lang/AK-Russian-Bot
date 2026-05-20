from io import BytesIO
from typing import Optional

from aiogram import Bot

from app.repositories.user_repo import UserRepository
from app.repositories.message_repo import MessageRepository
from app.services.access_service import AccessService
from app.services.ai_usage_budget_service import AIUsageBudgetService
from app.services.image_analyzer_service import ImageAnalyzerService
from app.services.image_explainer_service import ImageExplainerService


class ImageQAService:
    def __init__(self, session):
        self.session = session
        self.user_repo = UserRepository(session)
        self.message_repo = MessageRepository(session)
        self.access_service = AccessService(session)
        self.image_analyzer_service = ImageAnalyzerService()
        self.image_explainer_service = ImageExplainerService()
        self.last_budget_record = None

    async def _download_image_bytes(
        self,
        bot: Bot,
        file_id: str,
    ) -> bytes:
        telegram_file = await bot.get_file(file_id)
        buffer = BytesIO()
        await bot.download(telegram_file, destination=buffer)
        return buffer.getvalue()

    async def handle_user_image(
        self,
        bot: Bot,
        telegram_id: int,
        file_id: str,
        mime_type: str,
        telegram_message_id: Optional[int] = None,
    ) -> str:
        can_use, message_key = await self.access_service.can_use_image_ai(telegram_id)
        if not can_use:
            return message_key

        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            return "access_start_first"

        await self.message_repo.create(
            user_id=user.id,
            role="user",
            content=file_id,
            content_type="image",
            telegram_message_id=telegram_message_id,
        )

        image_bytes = await self._download_image_bytes(
            bot=bot,
            file_id=file_id,
        )

        analyzer_result = await self.image_analyzer_service.analyze_image(
            image_bytes=image_bytes,
            mime_type=mime_type,
        )

        assistant_reply = await self.image_explainer_service.explain_analysis(
            analyzer_result=analyzer_result,
            user_language=user.language,
            user_level=user.level,
        )
        budget_service = AIUsageBudgetService(self.session)
        analyzer_record = await budget_service.record_usage(
            telegram_id=telegram_id,
            result=self.image_analyzer_service.last_ai_result,
            source="image_analyze",
        )
        explainer_record = await budget_service.record_usage(
            telegram_id=telegram_id,
            result=self.image_explainer_service.last_ai_result,
            source="image_explain",
        )
        self.last_budget_record = (
            explainer_record
            if explainer_record.cooldown_started
            else analyzer_record
            if analyzer_record.cooldown_started
            else explainer_record
        )

        await self.message_repo.create(
            user_id=user.id,
            role="assistant",
            content=assistant_reply,
            content_type="text",
        )

        image_context = (
            "LAST_IMAGE_LESSON_CONTEXT\n"
            f"Analyzer result:\n{analyzer_result}\n\n"
            f"Final lesson reply:\n{assistant_reply}\n\n"
            "User may ask follow-up questions about this image lesson."
        )

        await self.message_repo.create(
            user_id=user.id,
            role="assistant",
            content=image_context,
            content_type="image_context",
        )

        await self.access_service.consume_one_question(telegram_id)
        await self.session.commit()
        return assistant_reply
