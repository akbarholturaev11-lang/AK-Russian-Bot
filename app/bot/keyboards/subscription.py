from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.bot.utils.i18n import t


def subscription_main_keyboard(lang: str, show_discount: bool = True) -> InlineKeyboardMarkup:
    rows = []

    # Invite button shown FIRST — only if user hasn't used discount yet
    if show_discount:
        rows.append([
            InlineKeyboardButton(
                text=t("subscription_referral_discount_button", lang),
                callback_data="subscription:referral_discount",
            )
        ])

    rows.append([
        InlineKeyboardButton(
            text=t("subscription_button_10_days", lang),
            callback_data="subscription:plan:10_days",
        ),
        InlineKeyboardButton(
            text=t("subscription_button_1_month", lang),
            callback_data="subscription:plan:1_month",
        ),
    ])
    rows.append([
        InlineKeyboardButton(
            text=t("payment_back", lang),
            callback_data="subscription:change_payment_method",
        ),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def subscription_discount_progress_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Shown while waiting for 3 referrals — only back button."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("subscription_back_to_main", lang),
                    callback_data="subscription:back_to_main",
                )
            ]
        ]
    )


def subscription_discount_ready_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Shown when 3/3 referrals reached — plan buttons + back."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
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
            [
                InlineKeyboardButton(
                    text=t("subscription_back_to_main", lang),
                    callback_data="subscription:back_to_main",
                ),
            ],
        ]
    )


def payment_method_keyboard(lang: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💳 VISA card", callback_data="payment:visa"),
        ],
        [
            InlineKeyboardButton(text="Alipay", callback_data="payment:alipay"),
        ],
        [
            InlineKeyboardButton(text="WeChat Pay", callback_data="payment:wechat"),
        ],
        [
            InlineKeyboardButton(text=t("payment_back", lang), callback_data="payment:back"),
        ]
    ])


def discount_payment_method_keyboard(
    lang: str,
    methods: list[str] | tuple[str, ...] | None = None,
    campaign_id: int | None = None,
):
    labels = {
        "visa": "💳 VISA card",
        "alipay": "Alipay",
        "wechat": "WeChat Pay",
    }
    methods = list(methods or ("visa", "alipay", "wechat"))
    rows = []
    for method in methods:
        if method not in labels:
            continue
        callback_data = (
            f"discount_offer:method:{campaign_id}:{method}"
            if campaign_id
            else f"discount_offer:method:{method}"
        )
        rows.append([InlineKeyboardButton(text=labels[method], callback_data=callback_data)])

    back_callback = f"discount_offer:back_entry:{campaign_id}" if campaign_id else "discount_offer:back_entry"
    rows.append([InlineKeyboardButton(text=t("payment_back", lang), callback_data=back_callback)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def admin_discount_entry_keyboard(lang: str, campaign_id: int | None = None) -> InlineKeyboardMarkup:
    callback_data = f"discount_offer:open:{campaign_id}" if campaign_id else "discount_offer:open"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("subscription_admin_discount_button", lang),
                    callback_data=callback_data,
                )
            ]
        ]
    )


def admin_discount_plan_keyboard(
    lang: str,
    plans: list[str] | tuple[str, ...] | None = None,
    payment_method: str | None = None,
    campaign_id: int | None = None,
    back_callback: str = "discount_offer:back_entry",
) -> InlineKeyboardMarkup:
    plans = list(plans or ("10_days", "1_month"))
    plan_buttons = []
    for plan in plans:
        if campaign_id and payment_method:
            callback_data = f"discount_offer:plan:{campaign_id}:{payment_method}:{plan}"
        elif payment_method:
            callback_data = f"discount_offer:plan:{payment_method}:{plan}"
        else:
            callback_data = f"discount_offer:plan:{plan}"
        plan_buttons.append(
            InlineKeyboardButton(
                text=t("subscription_button_10_days" if plan == "10_days" else "subscription_button_1_month", lang),
                callback_data=callback_data,
            )
        )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            plan_buttons,
            [
                InlineKeyboardButton(
                    text=t("payment_back", lang),
                    callback_data=back_callback,
                )
            ],
        ]
    )


def feedback_discount_payment_method_keyboard(feedback_id: int, lang: str):
    labels = {
        "visa": "💳 VISA card",
        "alipay": "Alipay",
        "wechat": "WeChat Pay",
    }
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=label,
                callback_data=f"feedback_discount:method:{feedback_id}:{method}",
            )
        ]
        for method, label in labels.items()
    ] + [
        [
            InlineKeyboardButton(text=t("payment_back", lang), callback_data="payment:back"),
        ],
    ])


def feedback_discount_plan_keyboard(
    feedback_id: int,
    lang: str,
    payment_method: str,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("subscription_button_10_days", lang),
                    callback_data=f"feedback_discount:plan:{feedback_id}:{payment_method}:10_days",
                ),
                InlineKeyboardButton(
                    text=t("subscription_button_1_month", lang),
                    callback_data=f"feedback_discount:plan:{feedback_id}:{payment_method}:1_month",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=t("payment_back", lang),
                    callback_data=f"feedback_discount:open:{feedback_id}",
                )
            ],
        ]
    )
