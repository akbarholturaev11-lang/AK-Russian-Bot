from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from app.bot.utils.i18n import t


def main_menu_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t("menu_profile", lang)),
                KeyboardButton(text=t("menu_subscription", lang)),
            ],
            [
                KeyboardButton(text=t("menu_invite", lang)),
                KeyboardButton(text=t("menu_help", lang)),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder="...",
    )


def course_menu_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t("course_settings_button", lang)),
                KeyboardButton(text=t("course_progress", lang)),
            ],
            [
                KeyboardButton(text=t("course_reread_button", lang)),
                KeyboardButton(text=t("course_reminder_set_button", lang)),
            ],
            [
                KeyboardButton(text=t("menu_profile", lang)),
                KeyboardButton(text=t("course_back_to_qa_button", lang)),
            ],
        ],
        resize_keyboard=True,
    )
