from pathlib import Path
from datetime import datetime, timezone

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

from app.config import settings
from app.repositories.payment_repo import PaymentRepository
from app.repositories.bot_feedback_repo import BotFeedbackRepository
from app.repositories.user_repo import UserRepository
from app.services.discount_service import DiscountService
from app.services.payment_service import PaymentService
from app.services.subscription_price_service import SubscriptionPriceService
from app.bot.utils.discount_formatter import build_admin_discount_block, build_discount_plan_line
from app.bot.utils.i18n import t
from app.bot.keyboards.subscription import (
    admin_discount_entry_keyboard,
    admin_discount_plan_keyboard,
    discount_payment_method_keyboard,
    feedback_discount_payment_method_keyboard,
    feedback_discount_plan_keyboard,
    subscription_discount_progress_keyboard,
    subscription_discount_ready_keyboard,
    payment_method_keyboard,
)
from app.bot.keyboards.checkout import checkout_keyboard


router = Router()
PAYMENT_METHODS = ("visa", "alipay", "wechat")
PLANS = ("10_days", "1_month")

# subscription.py → bot/handlers/ → bot/ → app/ → project root → app/static/payments/
_STATIC_PAYMENTS = Path(__file__).parent.parent.parent / "static" / "payments"

QR_PHOTO_PATHS = {
    "alipay_10_days":          str(_STATIC_PAYMENTS / "alipay_10_days.jpg"),
    "alipay_10_days_discount": str(_STATIC_PAYMENTS / "alipay_10_days_discount.jpg"),
    "alipay_1_month":          str(_STATIC_PAYMENTS / "alipay_1_month.jpg"),
    "alipay_1_month_discount": str(_STATIC_PAYMENTS / "alipay_1_month_discount.jpg"),
    "wechat_10_days":          str(_STATIC_PAYMENTS / "wechat_10_days.jpg"),
    "wechat_10_days_discount": str(_STATIC_PAYMENTS / "wechat_10_days_discount.jpg"),
    "wechat_1_month":          str(_STATIC_PAYMENTS / "wechat_1_month.jpg"),
    "wechat_1_month_discount": str(_STATIC_PAYMENTS / "wechat_1_month_discount.jpg"),
    "alipay_admin_discount":    str(_STATIC_PAYMENTS / "alipay_admin_discount.jpg"),
    "wechat_admin_discount":    str(_STATIC_PAYMENTS / "wechat_admin_discount.jpg"),
}


def _parse_campaign_id(value: str | None) -> int | None:
    if not value:
        return None
    try:
        campaign_id = int(value)
    except (TypeError, ValueError):
        return None
    return campaign_id if campaign_id > 0 else None


def _campaign_back_callback(name: str, campaign_id: int | None) -> str:
    return f"discount_offer:{name}:{campaign_id}" if campaign_id else f"discount_offer:{name}"


async def _plan_price(session, plan_type: str, payment_method: str | None) -> tuple[int, str]:
    price = await SubscriptionPriceService(session).get_price(payment_method, plan_type)
    if price:
        return price.amount, price.currency
    if payment_method in ("alipay", "wechat"):
        return (66 if plan_type == "1_month" else 29), "¥"
    return (89 if plan_type == "1_month" else 29), "somoni"


async def _admin_discount_choices(session, user):
    service = DiscountService(session)
    plan_choices = {}
    for plan in ("10_days", "1_month"):
        choice = await service.get_best_admin_discount(
            user=user,
            plan_type=plan,
            payment_method=user.payment_method,
        )
        if choice.source == "admin_campaign" and choice.ends_at and choice.starts_at:
            plan_choices[plan] = choice
    return plan_choices


async def _admin_discount_matrix(session, user, campaign_id: int | None = None):
    service = DiscountService(session)
    choices = {}
    for method in PAYMENT_METHODS:
        for plan in PLANS:
            if campaign_id:
                choice = await service.get_campaign_discount(
                    campaign_id=campaign_id,
                    user=user,
                    plan_type=plan,
                    payment_method=method,
                )
            else:
                choice = await service.get_best_admin_discount(
                    user=user,
                    plan_type=plan,
                    payment_method=method,
                )
            if choice.source == "admin_campaign" and choice.ends_at and choice.starts_at:
                choices[(method, plan)] = choice
    return choices


def _available_methods(choices: dict[tuple[str, str], object]) -> list[str]:
    return [method for method in PAYMENT_METHODS if any(key[0] == method for key in choices)]


def _available_plans(choices: dict[tuple[str, str], object], payment_method: str) -> list[str]:
    return [plan for plan in PLANS if (payment_method, plan) in choices]


async def _admin_discount_offer(session, user, lang: str, *, as_window: bool = False) -> str | None:
    plan_choices = await _admin_discount_choices(session, user)
    if not plan_choices:
        return None

    main_choice = max(plan_choices.values(), key=lambda item: item.percent)
    lines = []
    for plan in ("10_days", "1_month"):
        base, currency = await _plan_price(session, plan, user.payment_method)
        choice = plan_choices.get(plan)
        percent = choice.percent if choice else 0
        lines.append(
            build_discount_plan_line(
                lang=lang,
                plan=plan,
                base=base,
                currency=currency,
                percent=percent,
            )
        )

    return build_admin_discount_block(
        lang=lang,
        discount=main_choice,
        percent=main_choice.percent,
        starts_at=main_choice.starts_at,
        ends_at=main_choice.ends_at,
        quota_total=main_choice.quota_total,
        repeat_interval_days=main_choice.repeat_interval_days,
        plan_lines="\n".join(lines),
        discount_button_hint=not as_window,
        now=datetime.now(timezone.utc),
    )


def _plan_label(plan_type: str, lang: str) -> str:
    labels = {
        "tj": {"10_days": "10 рӯз", "1_month": "1 моҳ"},
        "ru": {"10_days": "10 дней", "1_month": "1 месяц"},
        "uz": {"10_days": "10 kunlik", "1_month": "1 oylik"},
    }
    return labels.get(lang, labels["ru"]).get(plan_type, plan_type)


async def build_subscription_main_text_for_user(session, user, lang: str) -> str:
    price_10 = await _plan_price(session, "10_days", getattr(user, "payment_method", None))
    price_1m = await _plan_price(session, "1_month", getattr(user, "payment_method", None))

    base = (
        f"{t('subscription_main_title', lang)}\n\n"
        f"{_plan_label('10_days', lang)} — {price_10[0]} {price_10[1]}\n"
        f"{_plan_label('1_month', lang)} — {price_1m[0]} {price_1m[1]}"
    )

    # Show discount hint only if user hasn't used it yet
    if not user.discount_used:
        base += f"\n\n{t('subscription_referral_hint', lang)}"

    return base


async def build_subscription_discount_progress_text(
    session,
    lang: str,
    referral_link: str,
    count: int,
    discount_eligible: bool = False,
    discount_used: bool = False,
    payment_method: str = None,
) -> str:
    base = (
        f"{t('subscription_discount_title', lang)}\n\n"
        f"{t('subscription_discount_link_label', lang)}\n"
        f"{referral_link}\n\n"
        f"{t('subscription_discount_progress', lang, count=count)}"
    )

    if discount_eligible and not discount_used:
        price_10 = await _plan_price(session, "10_days", payment_method)
        price_1m = await _plan_price(session, "1_month", payment_method)
        discount_10 = int(round(price_10[0] * 0.8))
        discount_1m = int(round(price_1m[0] * 0.8))

        base += (
            f"\n\n{t('subscription_discount_ready', lang)}\n\n"
            f"{_plan_label('10_days', lang)} — {discount_10} {price_10[1]}\n"
            f"{_plan_label('1_month', lang)} — {discount_1m} {price_1m[1]}"
        )

    return base


def build_subscription_main_keyboard_for_user(user, lang: str, show_referral: bool = True) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text=t("subscription_button_10_days", lang),
                callback_data="subscription:plan:10_days",
            ),
            InlineKeyboardButton(
                text=t("subscription_button_1_month", lang),
                callback_data="subscription:plan:1_month",
            ),
        ],
    ]
    if show_referral and not user.discount_used:
        rows.append([
            InlineKeyboardButton(
                text=t("subscription_referral_discount_button", lang),
                callback_data="subscription:referral_discount",
            )
        ])
    rows.append([
        InlineKeyboardButton(
            text=t("payment_back", lang),
            callback_data="subscription:change_payment_method",
        ),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def build_subscription_main_view(session, user, lang: str) -> tuple[str, InlineKeyboardMarkup]:
    return (
        await build_subscription_main_text_for_user(session, user, lang),
        build_subscription_main_keyboard_for_user(user, lang),
    )


async def build_admin_discount_entry_view(
    session,
    user,
    lang: str,
    campaign_id: int | None = None,
) -> tuple[str, InlineKeyboardMarkup] | None:
    choices = await _admin_discount_matrix(session, user, campaign_id=campaign_id)
    if not choices:
        return None
    return (
        t("subscription_admin_discount_entry_text", lang),
        admin_discount_entry_keyboard(lang, campaign_id=campaign_id),
    )


async def build_admin_discount_payment_view(
    session,
    user,
    lang: str,
    campaign_id: int | None = None,
) -> tuple[str, InlineKeyboardMarkup] | None:
    choices = await _admin_discount_matrix(session, user, campaign_id=campaign_id)
    methods = _available_methods(choices)
    if not methods:
        return None
    if len(methods) == 1:
        return await build_admin_discount_plan_view(
            session,
            user,
            lang,
            methods[0],
            choices=choices,
            campaign_id=campaign_id,
        )
    return (
        t("subscription_admin_discount_payment_choose", lang),
        discount_payment_method_keyboard(lang, methods, campaign_id=campaign_id),
    )


async def build_admin_discount_plan_view(
    session,
    user,
    lang: str,
    payment_method: str,
    *,
    choices: dict[tuple[str, str], object] | None = None,
    campaign_id: int | None = None,
) -> tuple[str, InlineKeyboardMarkup] | None:
    choices = choices or await _admin_discount_matrix(session, user, campaign_id=campaign_id)
    plans = _available_plans(choices, payment_method)
    if not plans:
        return None

    lines = []
    for plan in plans:
        choice = choices[(payment_method, plan)]
        base, currency = await _plan_price(session, plan, payment_method)
        lines.append(
            build_discount_plan_line(
                lang=lang,
                plan=plan,
                base=base,
                currency=currency,
                percent=choice.percent,
            )
        )

    back_callback = (
        _campaign_back_callback("back_payment", campaign_id)
        if len(_available_methods(choices)) > 1
        else _campaign_back_callback("back_entry", campaign_id)
    )
    return (
        t("subscription_admin_discount_plan_choose", lang, lines="\n".join(lines)),
        admin_discount_plan_keyboard(
            lang,
            plans=plans,
            payment_method=payment_method,
            campaign_id=campaign_id,
            back_callback=back_callback,
        ),
    )


async def _get_available_feedback_offer(session, user, feedback_id: int):
    return await BotFeedbackRepository(session).get_available_price_offer(
        feedback_id=feedback_id,
        telegram_id=user.telegram_id,
    )


async def build_feedback_discount_payment_view(
    session,
    user,
    lang: str,
    feedback_id: int,
) -> tuple[str, InlineKeyboardMarkup] | None:
    feedback = await _get_available_feedback_offer(session, user, feedback_id)
    if not feedback:
        return None
    return (
        t("feedback_price_offer_payment_choose", lang),
        feedback_discount_payment_method_keyboard(feedback.id, lang),
    )


async def build_feedback_discount_plan_view(
    session,
    user,
    lang: str,
    feedback_id: int,
    payment_method: str,
) -> tuple[str, InlineKeyboardMarkup] | None:
    feedback = await _get_available_feedback_offer(session, user, feedback_id)
    if not feedback:
        return None

    lines = []
    for plan in PLANS:
        base, currency = await _plan_price(session, plan, payment_method)
        lines.append(
            build_discount_plan_line(
                lang=lang,
                plan=plan,
                base=base,
                currency=currency,
                percent=20,
            )
        )

    return (
        t("feedback_price_offer_plan_choose", lang, lines="\n".join(lines)),
        feedback_discount_plan_keyboard(feedback.id, lang, payment_method),
    )


async def _replace_with_text(
    callback: CallbackQuery,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
    *,
    parse_mode: str | None = "HTML",
    disable_web_page_preview: bool = True,
) -> None:
    try:
        await callback.message.edit_text(
            text,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
        )
        return
    except Exception:
        pass

    try:
        await callback.message.delete()
    except Exception:
        pass

    await callback.message.answer(
        text,
        reply_markup=reply_markup,
        parse_mode=parse_mode,
        disable_web_page_preview=disable_web_page_preview,
    )


def build_checkout_text(lang: str, checkout_info: dict) -> str:
    plan_type = checkout_info["plan_type"]
    base_amount = checkout_info["base_amount"]
    final_amount = checkout_info["final_amount"]
    discount_applied = checkout_info["discount_applied"]
    currency = checkout_info["currency"]
    is_qr = (currency == "¥")

    if lang == "tj":
        plan_label = "10 рӯз" if plan_type == "10_days" else "1 моҳ"
        plan_line = f"Тариф: {plan_label}"
    elif lang == "uz":
        plan_label = "10 kunlik" if plan_type == "10_days" else "1 oylik"
        plan_line = f"Tarif: {plan_label}"
    else:
        plan_label = "10 дней" if plan_type == "10_days" else "1 месяц"
        plan_line = f"Тариф: {plan_label}"

    title_key = "checkout_title_qr" if is_qr else "checkout_title_visa"

    lines = [
        t(title_key, lang),
        plan_line,
        "",
    ]

    if discount_applied:
        lines.append(f"{t('subscription_original_price_label', lang)}: {base_amount} {currency}")
        percent = checkout_info.get("discount_percent", 20)
        lines.append(f"💎 {t('subscription_discounted_price_label', lang)}: {final_amount} {currency} (-{percent}%)")
    else:
        lines.append(f"{t('subscription_price_label', lang)}: {final_amount} {currency}")

    lines.append("")

    if is_qr:
        lines.append(t("checkout_qr_scan", lang))
    else:
        lines.append(f"{t('payment_details_label', lang)}: {settings.PAYMENT_DETAILS}")

    lines.extend([
        "",
        t("payment_send_screenshot", lang),
    ])

    return "\n".join(lines)


@router.callback_query(F.data == "subscription:open")
async def subscription_open_handler(callback: CallbackQuery, session):
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)

    if not user:
        await callback.answer()
        return

    lang = user.language if user.language else "ru"

    await callback.answer()
    await callback.message.edit_text(
        t("payment_method_choose", lang),
        reply_markup=payment_method_keyboard(lang),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("discount_offer:open"))
async def discount_offer_open_handler(callback: CallbackQuery, session):
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)

    if not user:
        await callback.answer()
        return

    lang = user.language or "ru"
    parts = callback.data.split(":")
    campaign_id = _parse_campaign_id(parts[2] if len(parts) > 2 else None)
    await callback.answer()

    view = await build_admin_discount_payment_view(session, user, lang, campaign_id=campaign_id)
    if not view:
        await callback.answer(t("subscription_admin_discount_expired", lang), show_alert=True)
        return

    text, keyboard = view
    await _replace_with_text(
        callback,
        text,
        reply_markup=keyboard,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


@router.callback_query(F.data.startswith("feedback_discount:open:"))
async def feedback_discount_open_handler(callback: CallbackQuery, session):
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer()
        return

    lang = user.language or "ru"
    feedback_id = int(callback.data.split(":")[2])
    view = await build_feedback_discount_payment_view(session, user, lang, feedback_id)
    if not view:
        await callback.answer(t("feedback_price_offer_expired", lang), show_alert=True)
        return

    await callback.answer()
    text, keyboard = view
    await _replace_with_text(
        callback,
        text,
        reply_markup=keyboard,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


@router.callback_query(F.data.startswith("feedback_discount:method:"))
async def feedback_discount_method_handler(callback: CallbackQuery, session):
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer()
        return

    parts = callback.data.split(":")
    feedback_id = int(parts[2])
    payment_method = parts[3]
    lang = user.language or "ru"

    if payment_method not in PAYMENT_METHODS:
        await callback.answer(t("feedback_price_offer_expired", lang), show_alert=True)
        return

    user.payment_method = payment_method
    await session.flush()

    view = await build_feedback_discount_plan_view(
        session,
        user,
        lang,
        feedback_id,
        payment_method,
    )
    if not view:
        await callback.answer(t("feedback_price_offer_expired", lang), show_alert=True)
        return

    await callback.answer()
    text, keyboard = view
    await _replace_with_text(
        callback,
        text,
        reply_markup=keyboard,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


@router.callback_query(F.data.startswith("feedback_discount:plan:"))
async def feedback_discount_plan_handler(callback: CallbackQuery, session):
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer()
        return

    parts = callback.data.split(":")
    feedback_id = int(parts[2])
    payment_method = parts[3]
    plan = parts[4]
    lang = user.language or "ru"

    if payment_method not in PAYMENT_METHODS or plan not in PLANS:
        await callback.answer(t("feedback_price_offer_expired", lang), show_alert=True)
        return

    feedback = await _get_available_feedback_offer(session, user, feedback_id)
    if not feedback:
        await callback.answer(t("feedback_price_offer_expired", lang), show_alert=True)
        return

    user.payment_method = payment_method
    await session.flush()

    payment_service = PaymentService(session)
    payment, checkout_info, error_key = await payment_service.create_checkout_draft(
        telegram_id=callback.from_user.id,
        plan_type=plan,
        force_feedback_discount=True,
        feedback_id=feedback.id,
    )

    if not payment or not checkout_info or checkout_info.get("discount_source") != "feedback_price_offer":
        await callback.answer(t("feedback_price_offer_expired", lang), show_alert=True)
        return

    await user_repo.set_selected_plan_type(user, plan)
    await _show_checkout(callback, user_repo, user, lang, plan, checkout_info)
    await session.commit()
    await callback.answer()


@router.callback_query(F.data.startswith("discount_offer:method:"))
async def discount_offer_method_handler(callback: CallbackQuery, session):
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer()
        return

    parts = callback.data.split(":")
    campaign_id = None
    payment_method = None
    if len(parts) >= 4:
        campaign_id = _parse_campaign_id(parts[2])
        payment_method = parts[3] if campaign_id else parts[2]
    elif len(parts) >= 3:
        payment_method = parts[2]

    if payment_method not in PAYMENT_METHODS:
        await callback.answer(t("subscription_admin_discount_expired", user.language or "ru"), show_alert=True)
        return

    user.payment_method = payment_method
    await session.commit()

    lang = user.language or "ru"
    view = await build_admin_discount_plan_view(
        session,
        user,
        lang,
        user.payment_method,
        campaign_id=campaign_id,
    )
    await callback.answer()
    if not view:
        await _replace_with_text(
            callback,
            t("subscription_admin_discount_expired", lang),
            parse_mode="HTML",
        )
        return

    text, keyboard = view
    await _replace_with_text(
        callback,
        text,
        reply_markup=keyboard,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


@router.callback_query(F.data.startswith("discount_offer:change_payment"))
async def discount_offer_change_payment_handler(callback: CallbackQuery, session):
    user = await UserRepository(session).get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer()
        return
    lang = user.language or "ru"
    parts = callback.data.split(":")
    campaign_id = _parse_campaign_id(parts[2] if len(parts) > 2 else None)
    await callback.answer()
    view = await build_admin_discount_payment_view(session, user, lang, campaign_id=campaign_id)
    if not view:
        await callback.answer(t("subscription_admin_discount_expired", lang), show_alert=True)
        return
    text, keyboard = view
    await _replace_with_text(
        callback,
        text,
        reply_markup=keyboard,
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("discount_offer:back_entry"))
async def discount_offer_back_entry_handler(callback: CallbackQuery, session):
    user = await UserRepository(session).get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer()
        return
    lang = user.language or "ru"
    parts = callback.data.split(":")
    campaign_id = _parse_campaign_id(parts[2] if len(parts) > 2 else None)
    view = await build_admin_discount_entry_view(session, user, lang, campaign_id=campaign_id)
    await callback.answer()
    if not view:
        await callback.answer(t("subscription_admin_discount_expired", lang), show_alert=True)
        return
    text, keyboard = view
    await _replace_with_text(
        callback,
        text,
        reply_markup=keyboard,
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("discount_offer:back_payment"))
async def discount_offer_back_payment_handler(callback: CallbackQuery, session):
    user = await UserRepository(session).get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer()
        return
    lang = user.language or "ru"
    parts = callback.data.split(":")
    campaign_id = _parse_campaign_id(parts[2] if len(parts) > 2 else None)
    view = await build_admin_discount_payment_view(session, user, lang, campaign_id=campaign_id)
    await callback.answer()
    if not view:
        await callback.answer(t("subscription_admin_discount_expired", lang), show_alert=True)
        return
    text, keyboard = view
    await _replace_with_text(
        callback,
        text,
        reply_markup=keyboard,
        parse_mode="HTML",
    )


@router.callback_query(F.data == "subscription:referral_discount")
async def subscription_referral_discount_handler(callback: CallbackQuery, session):
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)

    if not user:
        await callback.answer()
        return

    # Guard: if user already used discount — ignore silently
    if user.discount_used:
        await callback.answer()
        return

    await user_repo.ensure_referral_code(user)

    # Only start the offer once — do NOT reset count on repeated clicks
    if not user.discount_offer_started_at:
        await user_repo.start_discount_offer(user)

    await session.flush()

    lang = user.language if user.language else "ru"
    referral_link = f"https://t.me/{settings.BOT_USERNAME}?start={user.referral_code}"
    count = user.discount_referral_count

    text = await build_subscription_discount_progress_text(
        session,
        lang,
        referral_link,
        count,
        discount_eligible=user.discount_eligible,
        discount_used=user.discount_used,
        payment_method=user.payment_method,
    )
    keyboard = (
        subscription_discount_ready_keyboard(lang)
        if user.discount_eligible and not user.discount_used
        else subscription_discount_progress_keyboard(lang)
    )

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )

    await user_repo.set_discount_progress_message(
        user=user,
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
    )
    await session.commit()
    await callback.answer()


@router.callback_query(F.data == "subscription:back_to_main")
async def subscription_back_to_main_handler(callback: CallbackQuery, session):
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)

    if not user:
        await callback.answer()
        return

    lang = user.language if user.language else "ru"
    text, keyboard = await build_subscription_main_view(session, user, lang)

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )

    await user_repo.clear_discount_progress_message(user)
    await session.commit()


@router.callback_query(F.data == "payment:visa")
async def payment_visa_handler(callback: CallbackQuery, session):

    await callback.answer()

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        return

    user.payment_method = "visa"
    await session.commit()

    lang = user.language if user.language else "ru"
    text, keyboard = await build_subscription_main_view(session, user, lang)

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML",
    )


@router.callback_query(F.data == "payment:alipay")
async def payment_alipay_handler(callback: CallbackQuery, session):

    await callback.answer()

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        return

    user.payment_method = "alipay"
    await session.commit()

    lang = user.language if user.language else "ru"
    text, keyboard = await build_subscription_main_view(session, user, lang)

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML",
    )


@router.callback_query(F.data == "payment:wechat")
async def payment_wechat_handler(callback: CallbackQuery, session):

    await callback.answer()

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        return

    user.payment_method = "wechat"
    await session.commit()

    lang = user.language if user.language else "ru"
    text, keyboard = await build_subscription_main_view(session, user, lang)

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML",
    )


@router.callback_query(F.data == "checkout:change_plan")
async def checkout_change_plan_handler(callback: CallbackQuery, session):
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)

    if not user:
        await callback.answer()
        return

    lang = user.language if user.language else "ru"

    draft = await PaymentRepository(session).get_latest_draft_by_user(callback.from_user.id)
    await user_repo.set_selected_plan_type(user, None)
    await session.commit()

    if draft and draft.discount_source == "admin_campaign":
        view = await build_admin_discount_plan_view(
            session,
            user,
            lang,
            draft.payment_method or user.payment_method or "visa",
            campaign_id=draft.discount_campaign_id,
        )
        if not view:
            await callback.answer(t("subscription_admin_discount_expired", lang), show_alert=True)
            return
        text, keyboard = view
        await _replace_with_text(
            callback,
            text,
            reply_markup=keyboard,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
        await callback.answer()
        return

    if draft and draft.discount_source == "feedback_price_offer":
        feedback = await BotFeedbackRepository(session).get_latest_available_price_offer(callback.from_user.id)
        if not feedback:
            await callback.answer(t("feedback_price_offer_expired", lang), show_alert=True)
            return
        view = await build_feedback_discount_plan_view(
            session,
            user,
            lang,
            feedback.id,
            draft.payment_method or user.payment_method or "visa",
        )
        if not view:
            await callback.answer(t("feedback_price_offer_expired", lang), show_alert=True)
            return
        text, keyboard = view
        await _replace_with_text(
            callback,
            text,
            reply_markup=keyboard,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
        await callback.answer()
        return

    text, keyboard = await build_subscription_main_view(session, user, lang)

    try:
        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except Exception:
        # message is a photo (QR checkout) — delete and send new text message
        await callback.message.delete()
        await callback.message.answer(
            text,
            reply_markup=keyboard,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )

    await callback.answer()


async def _show_checkout(callback: CallbackQuery, user_repo: UserRepository, user, lang: str, plan: str, checkout_info: dict):
    text = build_checkout_text(lang, checkout_info)
    keyboard = checkout_keyboard(lang)

    checkout_msg_id: int | None = None

    if checkout_info["currency"] == "¥":
        if checkout_info.get("discount_source") == "admin_campaign":
            qr_key = f"{user.payment_method}_admin_discount"
        else:
            qr_key = f"{user.payment_method}_{plan}"
            if checkout_info.get("discount_applied"):
                qr_key += "_discount"
        photo_path = QR_PHOTO_PATHS.get(qr_key)
        if photo_path:
            photo = FSInputFile(photo_path)
            try:
                await callback.message.delete()
            except Exception:
                pass
            sent = await callback.message.answer_photo(
                photo,
                caption=text,
                reply_markup=keyboard,
            )
            checkout_msg_id = sent.message_id
        else:
            sent = await callback.message.edit_text(
                text,
                reply_markup=keyboard,
                disable_web_page_preview=True,
            )
            checkout_msg_id = callback.message.message_id
    else:
        try:
            await callback.message.edit_text(
                text,
                reply_markup=keyboard,
                disable_web_page_preview=True,
            )
            checkout_msg_id = callback.message.message_id
        except Exception:
            await callback.message.delete()
            sent = await callback.message.answer(
                text,
                reply_markup=keyboard,
                disable_web_page_preview=True,
            )
            checkout_msg_id = sent.message_id

    await user_repo.set_pending_checkout_msg_id(user, checkout_msg_id)


@router.callback_query(F.data.startswith("discount_offer:plan:"))
async def discount_offer_plan_handler(callback: CallbackQuery, session):
    await callback.answer()

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        return

    lang = user.language or "ru"
    parts = callback.data.split(":")
    campaign_id = None
    if len(parts) >= 5:
        campaign_id = _parse_campaign_id(parts[2])
        if campaign_id:
            payment_method = parts[3]
            plan = parts[4]
        else:
            payment_method = parts[2]
            plan = parts[3]
    elif len(parts) >= 4:
        payment_method = parts[2]
        plan = parts[3]
    else:
        payment_method = user.payment_method
        plan = parts[-1]

    if payment_method not in PAYMENT_METHODS:
        payment_method = None

    if plan not in PLANS:
        await callback.answer(t("subscription_admin_discount_expired", lang), show_alert=True)
        return

    if not payment_method:
        view = await build_admin_discount_payment_view(session, user, lang, campaign_id=campaign_id)
        if not view:
            await callback.answer(t("subscription_admin_discount_expired", lang), show_alert=True)
            return
        text, keyboard = view
        await _replace_with_text(
            callback,
            text,
            reply_markup=keyboard,
            parse_mode="HTML",
        )
        return

    user.payment_method = payment_method
    await session.flush()

    payment_service = PaymentService(session)
    payment, checkout_info, error_key = await payment_service.create_checkout_draft(
        telegram_id=callback.from_user.id,
        plan_type=plan,
        force_admin_discount=True,
        admin_discount_campaign_id=campaign_id,
    )

    if (
        not payment
        or not checkout_info
        or checkout_info.get("discount_source") != "admin_campaign"
        or (campaign_id and checkout_info.get("discount_campaign_id") != campaign_id)
    ):
        await callback.answer(t("subscription_admin_discount_expired", lang), show_alert=True)
        return

    await user_repo.set_selected_plan_type(user, plan)
    await _show_checkout(callback, user_repo, user, lang, plan, checkout_info)
    await session.commit()


@router.callback_query(F.data.startswith("subscription:plan:"))
async def subscription_plan_handler(callback: CallbackQuery, session):
    await callback.answer()

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)

    if not user:
        return

    lang = user.language or "ru"

    if not user.payment_method:
        await callback.message.edit_text(
            t("payment_method_choose", lang),
            reply_markup=payment_method_keyboard(lang),
            parse_mode="HTML",
        )
        return

    plan = callback.data.split(":")[-1]

    payment_service = PaymentService(session)
    payment, checkout_info, error_key = await payment_service.create_checkout_draft(
        telegram_id=callback.from_user.id,
        plan_type=plan,
    )

    if not payment or not checkout_info:
        if error_key:
            await callback.message.answer(t(error_key, lang))
        return

    await user_repo.set_selected_plan_type(user, plan)
    await _show_checkout(callback, user_repo, user, lang, plan, checkout_info)
    await session.commit()


@router.callback_query(F.data == "payment:back")
async def payment_back_handler(callback: CallbackQuery, session):
    await callback.answer()
    try:
        await callback.message.delete()
    except Exception:
        pass


@router.callback_query(F.data == "payment:retry")
async def payment_retry_handler(callback: CallbackQuery, session):
    from app.repositories.user_repo import UserRepository

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer()
        return

    lang = user.language if user.language else "ru"
    text, keyboard = await build_subscription_main_view(session, user, lang)
    await callback.answer()
    await callback.message.answer(
        text,
        reply_markup=keyboard,
        parse_mode="HTML",
    )


@router.callback_query(F.data == "subscription:change_payment_method")
async def subscription_change_payment_method_handler(callback: CallbackQuery, session):
    await callback.answer()

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)

    if not user:
        return

    lang = user.language if user.language else "ru"

    await callback.message.edit_text(
        t("payment_method_choose", lang),
        reply_markup=payment_method_keyboard(lang),
        parse_mode="HTML",
    )
