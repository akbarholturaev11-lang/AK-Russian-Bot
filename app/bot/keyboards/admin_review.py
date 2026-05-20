from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def admin_payment_review_keyboard(payment_id: int, lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash",
                    callback_data=f"admin_payment:approve:{payment_id}",
                ),
                InlineKeyboardButton(
                    text="❌ Rad etish",
                    callback_data=f"admin_payment:reject:{payment_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="💬 Sabab bilan rad",
                    callback_data=f"admin_payment:reject_reason:{payment_id}",
                ),
            ],
        ]
    )


def admin_reject_reason_keyboard(payment_id: int) -> InlineKeyboardMarkup:
    reasons = [
        ("Summa noto'g'ri", "wrong_amount"),
        ("Screenshot noaniq", "unclear_screenshot"),
        ("Soxta ko'rinadi", "fake_suspected"),
        ("Eski to'lov", "old_payment"),
        ("Boshqa sabab", "other"),
    ]
    buttons = [
        [InlineKeyboardButton(
            text=label,
            callback_data=f"admin_payment:reject_with:{payment_id}:{code}",
        )]
        for label, code in reasons
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
