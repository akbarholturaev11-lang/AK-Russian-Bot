from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def ad_panel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Yangi reklama", callback_data="ads:new")],
            [InlineKeyboardButton(text="📋 Reklamalar", callback_data="ads:list")],
            [InlineKeyboardButton(text="⬅️ Admin panel", callback_data="adm:menu")],
        ]
    )


def ad_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="ads:cancel")],
        ]
    )


def ad_duration_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="1 kun", callback_data="ads:duration:24"),
                InlineKeyboardButton(text="3 kun", callback_data="ads:duration:72"),
                InlineKeyboardButton(text="7 kun", callback_data="ads:duration:168"),
            ],
            [InlineKeyboardButton(text="✍️ Boshqa muddat", callback_data="ads:duration:custom")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="ads:cancel")],
        ]
    )


def ad_send_count_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="1 marta", callback_data="ads:count:1"),
                InlineKeyboardButton(text="2 marta", callback_data="ads:count:2"),
                InlineKeyboardButton(text="3 marta", callback_data="ads:count:3"),
            ],
            [
                InlineKeyboardButton(text="5 marta", callback_data="ads:count:5"),
                InlineKeyboardButton(text="✍️ Boshqa", callback_data="ads:count:custom"),
            ],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="ads:cancel")],
        ]
    )


def ad_language_keyboard(selected: list[str]) -> InlineKeyboardMarkup:
    selected_set = set(selected)

    def label(code: str, text: str) -> str:
        return f"✅ {text}" if code in selected_set else text

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=label("uz", "UZ"), callback_data="ads:lang:uz"),
                InlineKeyboardButton(text=label("ru", "RU"), callback_data="ads:lang:ru"),
                InlineKeyboardButton(text=label("tj", "TJ"), callback_data="ads:lang:tj"),
            ],
            [InlineKeyboardButton(text="🌐 Hammasi", callback_data="ads:lang:all")],
            [InlineKeyboardButton(text="✅ Davom etish", callback_data="ads:lang_done")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="ads:cancel")],
        ]
    )


def ad_active_policy_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚫 Faol obunachilarga yubormaslik", callback_data="ads:active:no")],
            [InlineKeyboardButton(text="✅ Faol obunachilarga ham yuborish", callback_data="ads:active:yes")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="ads:cancel")],
        ]
    )


def ad_start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Hozir", callback_data="ads:start:now"),
                InlineKeyboardButton(text="Belgilangan vaqt", callback_data="ads:start:scheduled"),
            ],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="ads:cancel")],
        ]
    )


def ad_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👁 Admin test", callback_data="ads:test")],
            [
                InlineKeyboardButton(text="✅ Ishga tushirish", callback_data="ads:confirm"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="ads:cancel"),
            ],
        ]
    )


def ad_list_keyboard(campaigns) -> InlineKeyboardMarkup:
    rows = []
    for campaign in campaigns:
        if campaign.is_active:
            rows.append([
                InlineKeyboardButton(
                    text=f"⛔ #{campaign.id} to'xtatish",
                    callback_data=f"ads:disable:{campaign.id}",
                )
            ])
    rows.extend([
        [InlineKeyboardButton(text="➕ Yangi reklama", callback_data="ads:new")],
        [InlineKeyboardButton(text="⬅️ Admin panel", callback_data="adm:menu")],
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)
