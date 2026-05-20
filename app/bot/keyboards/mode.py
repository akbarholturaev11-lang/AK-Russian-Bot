from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.bot.utils.i18n import t


def course_promo_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("course_promo_button", lang),
                    callback_data="course_promo:start",
                )
            ]
        ]
    )


def mode_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("qa_mode_title", lang),
                    callback_data="mode:qa",
                )
            ],
        ]
    )
