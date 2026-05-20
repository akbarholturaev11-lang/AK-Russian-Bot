from aiogram import Bot

from app.bot.utils.i18n import t

REASON_TRANSLATIONS = {
    "wrong_amount":       {"uz": "Summa noto'g'ri",    "tj": "Маблағ нодуруст",     "ru": "Неверная сумма"},
    "unclear_screenshot": {"uz": "Screenshot noaniq",  "tj": "Скриншот норавшан",   "ru": "Скриншот нечёткий"},
    "fake_suspected":     {"uz": "Shubhali to'lov",    "tj": "Пардохти шубҳанок",   "ru": "Подозрительный платёж"},
    "old_payment":        {"uz": "Eski to'lov",        "tj": "Пардохти кӯҳна",      "ru": "Старый платёж"},
    "other":              {"uz": "Boshqa sabab",        "tj": "Сабаби дигар",        "ru": "Другая причина"},
}


def _translate_reason(reason_code: str, lang: str) -> str:
    return REASON_TRANSLATIONS.get(reason_code, {}).get(lang, reason_code)


class PaymentNotifyService:
    async def notify_payment_approved(self, bot: Bot, user) -> None:
        if not user:
            return
        lang = user.language if user.language else "ru"
        try:
            await bot.send_message(chat_id=user.telegram_id, text=t("user_payment_approved", lang))
        except Exception:
            pass

    async def notify_payment_rejected(self, bot: Bot, user, reason: str = None, plan_type: str = None) -> None:
        if not user:
            return
        lang = user.language if user.language else "ru"
        text = t("user_payment_rejected", lang)
        if reason:
            translated = _translate_reason(reason, lang)
            prefix = {"uz": "Sabab", "tj": "Сабаб", "ru": "Причина"}.get(lang, "Sabab")
            text += f"\n\n{prefix}: {translated}"
        try:
            await bot.send_message(chat_id=user.telegram_id, text=text)
        except Exception:
            pass
