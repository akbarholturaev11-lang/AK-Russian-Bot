from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.bot.utils.i18n import t


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇹🇯 Тоҷикӣ", callback_data="lang:tj"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
                InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang:uz"),
            ]
        ]
    )


def level_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("level_beginner", lang), callback_data="level:beginner")],
            [
                InlineKeyboardButton(text="HSK 1", callback_data="level:hsk1"),
                InlineKeyboardButton(text="HSK 2", callback_data="level:hsk2"),
            ],
            [
                InlineKeyboardButton(text="HSK 3", callback_data="level:hsk3"),
                InlineKeyboardButton(text="HSK 4", callback_data="level:hsk4"),
            ],
        ]
    )
