from datetime import datetime, timezone
from html import escape
from typing import Any, Optional
from zoneinfo import ZoneInfo

from app.bot.utils.i18n import t


ADMIN_TZ = ZoneInfo("Asia/Shanghai")


def discount_title_for_lang(discount: Any, lang: str) -> str:
    if isinstance(discount, dict):
        title = discount.get(f"title_{lang}") or discount.get("title")
    else:
        title = getattr(discount, f"title_{lang}", None) or getattr(discount, "title", None)
    return escape(str(title or "Chegirma"))


def discount_reason_for_lang(discount: Any, lang: str) -> str:
    if isinstance(discount, dict):
        reason = discount.get(f"reason_{lang}") or discount.get("reason")
    else:
        reason = getattr(discount, f"reason_{lang}", None) or getattr(discount, "reason", None)
    return escape(str(reason or ""))


def plan_label(plan_type: str, lang: str) -> str:
    if plan_type == "10_days":
        return t("subscription_button_10_days", lang)
    if plan_type == "1_month":
        return t("subscription_button_1_month", lang)
    return plan_type


def format_discount_duration(seconds: int, lang: str) -> str:
    if seconds <= 0:
        return t("subscription_admin_discount_remaining_done", lang)

    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60

    if lang == "tj":
        if days:
            return f"{days} рӯз {hours} соат"
        if hours:
            return f"{hours} соат {minutes} дақиқа"
        return f"{max(minutes, 1)} дақиқа"

    if lang == "ru":
        if days:
            return f"{days} дн. {hours} ч."
        if hours:
            return f"{hours} ч. {minutes} мин."
        return f"{max(minutes, 1)} мин."

    if days:
        return f"{days} kun {hours} soat"
    if hours:
        return f"{hours} soat {minutes} daqiqa"
    return f"{max(minutes, 1)} daqiqa"


def format_discount_time(value: Optional[datetime]) -> str:
    if not value:
        return "-"
    return value.astimezone(ADMIN_TZ).strftime("%Y-%m-%d %H:%M")


def format_discount_quota(value: Optional[int], lang: str) -> str:
    return str(value) if value else t("subscription_admin_discount_quota_unlimited", lang)


def format_discount_rule(days: Optional[int], lang: str) -> str:
    if days:
        return t("subscription_admin_discount_rule_repeat", lang, days=days)
    return t("subscription_admin_discount_rule_once", lang)


def build_discount_plan_line(
    *,
    lang: str,
    plan: str,
    base: int,
    currency: str,
    percent: int = 0,
) -> str:
    if percent > 0:
        final = int(round(base * (100 - percent) / 100))
        return t(
            "subscription_admin_discount_plan_discounted",
            lang,
            plan=plan_label(plan, lang),
            base=base,
            final=final,
            currency=currency,
        )

    return t(
        "subscription_admin_discount_plan_regular",
        lang,
        plan=plan_label(plan, lang),
        base=base,
        currency=currency,
    )


def build_admin_discount_block(
    *,
    lang: str,
    discount: Any,
    percent: int,
    starts_at: datetime,
    ends_at: datetime,
    quota_total: Optional[int],
    repeat_interval_days: Optional[int],
    plan_lines: str,
    discount_button_hint: bool = True,
    now: Optional[datetime] = None,
) -> str:
    now = now or datetime.now(timezone.utc)
    duration_seconds = max(int((ends_at - starts_at).total_seconds()), 0)
    remaining_seconds = max(int((ends_at - now).total_seconds()), 0)

    return t(
        "subscription_admin_discount_block",
        lang,
        title=discount_title_for_lang(discount, lang),
        reason=discount_reason_for_lang(discount, lang),
        percent=percent,
        duration=format_discount_duration(duration_seconds, lang),
        remaining=format_discount_duration(remaining_seconds, lang),
        ends_at=format_discount_time(ends_at),
        plan_lines=plan_lines,
        quota=format_discount_quota(quota_total, lang),
        rule=format_discount_rule(repeat_interval_days, lang),
        button_hint=t("subscription_admin_discount_button_hint", lang) if discount_button_hint else "",
    )
