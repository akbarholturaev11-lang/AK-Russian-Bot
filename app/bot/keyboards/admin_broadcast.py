from typing import Optional

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def _mark(active: bool) -> str:
    return "✅ " if active else ""


def broadcast_panel_keyboard(
    lang_filter: Optional[str],
    status_filter: Optional[str],
    level_filter: Optional[str],
    mode_filter: Optional[str] = None,
    payment_status_filter: Optional[str] = None,
    payment_method_filter: Optional[str] = None,
    plan_filter: Optional[str] = None,
    discount_filter: Optional[str] = None,
    course_promo_filter: Optional[str] = None,
    activity_filter: Optional[str] = None,
    section: str = "main",
) -> InlineKeyboardMarkup:
    def section_btn(key: str, label: str) -> InlineKeyboardButton:
        return InlineKeyboardButton(text=label, callback_data=f"bc:section:{key}")

    def back_btn() -> InlineKeyboardButton:
        return InlineKeyboardButton(text="⬅️ Panelga qaytish", callback_data="bc:section:main")

    def lang_btn(val: Optional[str], label: str) -> InlineKeyboardButton:
        return InlineKeyboardButton(
            text=f"{_mark(lang_filter == val)}{label}",
            callback_data=f"bc:lang:{val or 'all'}",
        )

    def status_btn(val: Optional[str], label: str) -> InlineKeyboardButton:
        return InlineKeyboardButton(
            text=f"{_mark(status_filter == val)}{label}",
            callback_data=f"bc:status:{val or 'all'}",
        )

    def level_btn(val: Optional[str], label: str) -> InlineKeyboardButton:
        return InlineKeyboardButton(
            text=f"{_mark(level_filter == val)}{label}",
            callback_data=f"bc:level:{val or 'all'}",
        )

    def mode_btn(val: Optional[str], label: str) -> InlineKeyboardButton:
        return InlineKeyboardButton(
            text=f"{_mark(mode_filter == val)}{label}",
            callback_data=f"bc:mode:{val or 'all'}",
        )

    def pay_status_btn(val: Optional[str], label: str) -> InlineKeyboardButton:
        return InlineKeyboardButton(
            text=f"{_mark(payment_status_filter == val)}{label}",
            callback_data=f"bc:paystatus:{val or 'all'}",
        )

    def pay_method_btn(val: Optional[str], label: str) -> InlineKeyboardButton:
        return InlineKeyboardButton(
            text=f"{_mark(payment_method_filter == val)}{label}",
            callback_data=f"bc:paymethod:{val or 'all'}",
        )

    def plan_btn(val: Optional[str], label: str) -> InlineKeyboardButton:
        return InlineKeyboardButton(
            text=f"{_mark(plan_filter == val)}{label}",
            callback_data=f"bc:plan:{val or 'all'}",
        )

    def discount_btn(val: Optional[str], label: str) -> InlineKeyboardButton:
        return InlineKeyboardButton(
            text=f"{_mark(discount_filter == val)}{label}",
            callback_data=f"bc:discount:{val or 'all'}",
        )

    def promo_btn(val: Optional[str], label: str) -> InlineKeyboardButton:
        return InlineKeyboardButton(
            text=f"{_mark(course_promo_filter == val)}{label}",
            callback_data=f"bc:promo:{val or 'all'}",
        )

    def activity_btn(val: Optional[str], label: str) -> InlineKeyboardButton:
        return InlineKeyboardButton(
            text=f"{_mark(activity_filter == val)}{label}",
            callback_data=f"bc:activity:{val or 'all'}",
        )

    if section == "lang":
        rows = [[lang_btn(None, "Hammasi"), lang_btn("uz", "UZ"), lang_btn("ru", "RU"), lang_btn("tj", "TJ")]]
    elif section == "status":
        rows = [
            [status_btn(None, "Hammasi"), status_btn("active", "Faol"), status_btn("trial", "Sinov")],
            [status_btn("free", "Bepul"), status_btn("expired", "Tugagan"), status_btn("blocked", "Blok")],
        ]
    elif section == "level":
        rows = [
            [level_btn(None, "Hammasi"), level_btn("beginner", "Boshlang'ich"), level_btn("hsk1", "A1")],
            [level_btn("hsk2", "A2"), level_btn("hsk3", "B1"), level_btn("hsk4", "B2")],
        ]
    elif section == "mode":
        rows = [[mode_btn(None, "Hammasi"), mode_btn("qa", "Savol-javob"), mode_btn("course", "Kurs")]]
    elif section == "payment":
        rows = [
            [pay_status_btn(None, "Status: Hammasi"), pay_status_btn("none", "Yo'q"), pay_status_btn("pending", "Kutilmoqda")],
            [pay_status_btn("approved", "Tasdiqlangan"), pay_status_btn("rejected", "Rad etilgan")],
            [pay_method_btn(None, "Usul: Hammasi"), pay_method_btn("visa", "Visa")],
            [pay_method_btn("alipay", "Alipay"), pay_method_btn("wechat", "WeChat")],
            [plan_btn(None, "Tarif: Hammasi"), plan_btn("10_days", "10 kun"), plan_btn("1_month", "1 oy")],
        ]
    elif section == "discount":
        rows = [
            [discount_btn(None, "Hammasi"), discount_btn("eligible", "Chegirma bor"), discount_btn("used", "Ishlatilgan")],
            [discount_btn("none", "Chegirma yo'q")],
            [promo_btn(None, "Promo: Hammasi"), promo_btn("sent", "Yuborilgan"), promo_btn("not_sent", "Yuborilmagan")],
        ]
    elif section == "activity":
        rows = [
            [activity_btn(None, "Hammasi"), activity_btn("active_7d", "7 kun faol")],
            [activity_btn("inactive_7d", "7 kun sovuq"), activity_btn("new_7d", "7 kun yangi")],
        ]
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [section_btn("lang", "🌐 Til"), section_btn("status", "👤 Status")],
            [section_btn("level", "📚 Daraja"), section_btn("mode", "🎯 Rejim")],
            [section_btn("payment", "💳 To'lov"), section_btn("discount", "🎁 Chegirma")],
            [section_btn("activity", "⚡ Aktivlik")],
            [InlineKeyboardButton(text="✏️ Xabar tayyorlash", callback_data="bc:enter_text")],
            [InlineKeyboardButton(text="🎯 Bitta userga xabar", callback_data="bc:target_user")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="bc:cancel")],
        ])

    rows.append([back_btn(), InlineKeyboardButton(text="✏️ Xabar tayyorlash", callback_data="bc:enter_text")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def broadcast_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yuborish", callback_data="bc:confirm"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="bc:cancel"),
        ],
    ])
