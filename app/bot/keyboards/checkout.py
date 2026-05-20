from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.bot.utils.i18n import t


def checkout_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("checkout_change_plan_button", lang),
                    callback_data="checkout:change_plan",
                ),
            ]
        ]
    )
