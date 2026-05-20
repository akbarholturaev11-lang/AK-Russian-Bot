from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.bot.utils.i18n import t


def referral_daily_limit_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("referral_invite_button", lang),
                    callback_data="referral:invite",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("menu_subscription", lang),
                    callback_data="subscription:open",
                )
            ],
        ]
    )


def photo_limit_subscription_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("menu_subscription", lang),
                    callback_data="subscription:open",
                )
            ],
        ]
    )
