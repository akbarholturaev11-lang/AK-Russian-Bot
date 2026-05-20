import base64
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional

from openai import AsyncOpenAI

from app.config import settings


@dataclass(frozen=True)
class AIUsageResult:
    content: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.prompt_path = Path("app/prompts/qa_system.txt")

    def _build_system_prompt(self, user_language: str, user_level: str) -> str:
        template = self.prompt_path.read_text(encoding="utf-8")
        return template.format(
            user_language=user_language,
            user_level=self._russian_level_label(user_level),
        )

    def _russian_level_label(self, user_level: str) -> str:
        level = (user_level or "").strip().lower()
        return {
            "beginner": "beginner",
            "az0": "beginner",
            "hsk1": "A1",
            "hsk2": "A2",
            "hsk3": "B1",
            "hsk4": "B2",
        }.get(level, user_level or "beginner")

    def _usage_value(self, usage, *names: str) -> int:
        if not usage:
            return 0
        for name in names:
            value = getattr(usage, name, None)
            if value is None and isinstance(usage, dict):
                value = usage.get(name)
            if value is not None:
                try:
                    return int(value)
                except (TypeError, ValueError):
                    return 0
        return 0

    def _result_from_response(self, response, model: str, content: str) -> AIUsageResult:
        usage = getattr(response, "usage", None)
        prompt_tokens = self._usage_value(usage, "prompt_tokens", "input_tokens")
        completion_tokens = self._usage_value(usage, "completion_tokens", "output_tokens")
        total_tokens = self._usage_value(usage, "total_tokens")
        if not total_tokens:
            total_tokens = prompt_tokens + completion_tokens
        return AIUsageResult(
            content=content or "",
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )

    async def generate_reply_with_usage(
        self,
        text: str,
        user_language: str,
        user_level: str,
        history: Optional[List[Dict[str, str]]] = None,
        model_override: str = None,
        max_completion_tokens: int | None = None,
    ) -> AIUsageResult:
        system_prompt = self._build_system_prompt(
            user_language=user_language,
            user_level=user_level,
        )

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            }
        ]

        if history:
            for msg in history:
                if msg.get("role") in ("user", "assistant"):
                    messages.append(msg)

        messages.append(
            {
                "role": "user",
                "content": text,
            }
        )

        model = model_override or "o4-mini"
        request = {
            "model": model,
            "messages": messages,
        }
        if max_completion_tokens is not None:
            request["max_completion_tokens"] = max_completion_tokens

        response = await self.client.chat.completions.create(**request)

        return self._result_from_response(
            response=response,
            model=model,
            content=response.choices[0].message.content or "",
        )

    async def generate_reply(
        self,
        text: str,
        user_language: str,
        user_level: str,
        history: Optional[List[Dict[str, str]]] = None,
        model_override: str = None,
        max_completion_tokens: int | None = None,
    ) -> str:
        result = await self.generate_reply_with_usage(
            text=text,
            user_language=user_language,
            user_level=user_level,
            history=history,
            model_override=model_override,
            max_completion_tokens=max_completion_tokens,
        )
        return result.content

    async def generate_vision_reply_with_usage(
        self,
        image_bytes: bytes,
        mime_type: str,
        prompt: str,
        model: str = "o4-mini",
    ) -> AIUsageResult:
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:{mime_type};base64,{image_b64}"

        response = await self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": data_url,
                            },
                        },
                    ],
                }
            ],
        )

        return self._result_from_response(
            response=response,
            model=model,
            content=response.choices[0].message.content or "",
        )

    async def generate_vision_reply(
        self,
        image_bytes: bytes,
        mime_type: str,
        prompt: str,
    ) -> str:
        result = await self.generate_vision_reply_with_usage(
            image_bytes=image_bytes,
            mime_type=mime_type,
            prompt=prompt,
        )
        return result.content

    async def transcribe_voice_with_usage(
        self,
        audio_bytes: bytes,
        filename: str,
        user_language: str,
        user_level: str,
    ) -> AIUsageResult:
        lang_labels = {
            "tj": "Tajik",
            "uz": "Uzbek",
            "ru": "Russian",
        }
        primary_lang = lang_labels.get(user_language, "Russian")
        prompt = (
            "Transcribe this Telegram voice message. Do not translate it. "
            f"The user's interface language is {primary_lang}, and their Russian level is {self._russian_level_label(user_level)}. "
            "The audio is likely in the user's interface language or Russian. "
            "Preserve Russian words, names, numbers, and short mixed-language phrases carefully. "
            "If speech is unclear, transcribe only what you can hear."
        )

        model = "gpt-4o-mini-transcribe"
        response = await self.client.audio.transcriptions.create(
            model=model,
            chunking_strategy="auto",
            file=(filename, audio_bytes, "audio/ogg"),
            prompt=prompt,
            temperature=0,
        )

        if isinstance(response, str):
            return AIUsageResult(content=response.strip(), model=model)
        return self._result_from_response(
            response=response,
            model=model,
            content=(getattr(response, "text", "") or "").strip(),
        )

    async def transcribe_voice(
        self,
        audio_bytes: bytes,
        filename: str,
        user_language: str,
        user_level: str,
    ) -> str:
        result = await self.transcribe_voice_with_usage(
            audio_bytes=audio_bytes,
            filename=filename,
            user_language=user_language,
            user_level=user_level,
        )
        return result.content

    async def translate_voice_with_usage(
        self,
        transcript: str,
        user_language: str,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> AIUsageResult:
        lang_labels = {
            "tj": "Tajik",
            "uz": "Uzbek",
            "ru": "Russian",
        }
        target_lang = lang_labels.get(user_language, "Russian")
        model = "gpt-4o-mini"

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a context-aware Russian conversation interpreter for real-life dialogue. "
                    f"The user's interface language is {target_lang}. "
                    "If the latest transcript is Russian, translate only the latest transcript into the user's interface language. "
                    "If the latest transcript is not Russian, translate or interpret only the latest transcript into natural Russian. "
                    "Use recent context only to resolve pronouns, tone, missing objects, and situation. "
                    "Never answer the speaker's question, never continue the chat, and never translate older messages. "
                    "Return only the translation text. Do not add labels, markdown, alternatives, explanations, or quotes. "
                    "If a word is unclear, keep the closest natural meaning and preserve uncertainty briefly."
                ),
            }
        ]

        if history:
            context_lines = []
            for msg in history[-6:]:
                role = msg.get("role")
                content = (msg.get("content") or "").strip()
                if role in ("user", "assistant") and content:
                    context_lines.append(f"{role}: {content}")
            if context_lines:
                messages.append(
                    {
                        "role": "system",
                        "content": (
                            "Recent context for disambiguation only. "
                            "Do not translate these lines unless they are repeated in the latest transcript.\n"
                            + "\n".join(context_lines)
                        ),
                    }
                )

        messages.append(
            {
                "role": "user",
                "content": transcript,
            }
        )

        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_completion_tokens=300,
        )

        return self._result_from_response(
            response=response,
            model=model,
            content=response.choices[0].message.content or "",
        )
