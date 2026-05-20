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
    labels = {
        "tj": ("A1", "A2", "B1", "B2"),
        "ru": ("A1", "A2", "B1", "B2"),
        "uz": ("A1", "A2", "B1", "B2"),
    }
    a1, a2, b1, b2 = labels.get(lang, labels["ru"])
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("level_beginner", lang), callback_data="level:beginner")],
            [
                InlineKeyboardButton(text=a1, callback_data="level:hsk1"),
                InlineKeyboardButton(text=a2, callback_data="level:hsk2"),
            ],
            [
                InlineKeyboardButton(text=b1, callback_data="level:hsk3"),
                InlineKeyboardButton(text=b2, callback_data="level:hsk4"),
            ],
        ]
    )
