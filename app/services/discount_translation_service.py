import json
from typing import Dict

from openai import AsyncOpenAI

from app.config import settings


class DiscountTranslationService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def translate_title(self, title: str) -> Dict[str, str]:
        fallback = {"tj": title, "ru": title, "uz": title}
        if not settings.OPENAI_API_KEY or not title.strip():
            return fallback

        try:
            response = await self.client.chat.completions.create(
                model="o4-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Translate a short Telegram discount campaign title into Tajik Cyrillic, "
                            "Russian, and Uzbek Latin. Return only valid JSON with keys tj, ru, uz. "
                            "Keep emojis, numbers, percentages, and brand names unchanged."
                        ),
                    },
                    {"role": "user", "content": title[:120]},
                ],
            )
            raw = response.choices[0].message.content or ""
            start = raw.find("{")
            end = raw.rfind("}")
            payload = json.loads(raw[start : end + 1] if start >= 0 and end >= 0 else raw)
        except Exception:
            return fallback

        return {
            "tj": str(payload.get("tj") or title)[:180],
            "ru": str(payload.get("ru") or title)[:180],
            "uz": str(payload.get("uz") or title)[:180],
        }

    async def translate_campaign_texts(self, title: str, reason: str) -> Dict[str, str]:
        fallback = {
            "title_tj": title,
            "title_ru": title,
            "title_uz": title,
            "reason_tj": reason,
            "reason_ru": reason,
            "reason_uz": reason,
        }
        if not settings.OPENAI_API_KEY:
            return fallback

        try:
            response = await self.client.chat.completions.create(
                model="o4-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Translate Telegram discount campaign text into Tajik Cyrillic, Russian, "
                            "and Uzbek Latin. Return only valid JSON with keys title_tj, title_ru, "
                            "title_uz, reason_tj, reason_ru, reason_uz. Keep emojis, numbers, "
                            "percentages, and brand names unchanged. Keep the copy concise and natural."
                        ),
                    },
                    {
                        "role": "user",
                        "content": json.dumps(
                            {"title": title[:120], "reason": reason[:500]},
                            ensure_ascii=False,
                        ),
                    },
                ],
            )
            raw = response.choices[0].message.content or ""
            start = raw.find("{")
            end = raw.rfind("}")
            payload = json.loads(raw[start : end + 1] if start >= 0 and end >= 0 else raw)
        except Exception:
            return fallback

        return {
            "title_tj": str(payload.get("title_tj") or title)[:180],
            "title_ru": str(payload.get("title_ru") or title)[:180],
            "title_uz": str(payload.get("title_uz") or title)[:180],
            "reason_tj": str(payload.get("reason_tj") or reason)[:700],
            "reason_ru": str(payload.get("reason_ru") or reason)[:700],
            "reason_uz": str(payload.get("reason_uz") or reason)[:700],
        }
