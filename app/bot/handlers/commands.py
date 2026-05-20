from app.bot.keyboards.onboarding import level_keyboard
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from sqlalchemy import select, func
from app.db.models.user import User

from app.config import settings
from app.repositories.user_repo import UserRepository
from app.bot.handlers.subscription import build_subscription_main_text_for_user
from app.bot.keyboards.subscription import subscription_main_keyboard, payment_method_keyboard
from app.bot.keyboards.referral import photo_limit_subscription_keyboard
from app.bot.utils.i18n import t


router = Router()


def _lang(user) -> str:
    return user.language if user and user.language else "ru"


async def _clear_voice_mode(user, session, state: FSMContext | None = None) -> None:
    if state:
        await state.update_data(pending_voice_transcript=None, pending_voice_message_id=None)
    if user and (getattr(user, "voice_mode", "none") or "none") != "none":
        user.voice_mode = "none"
        await session.commit()


def _fmt_date(dt) -> str:
    if not dt:
        return "-"
    try:
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return str(dt)


def _status_label(status: str, lang: str) -> str:
    if lang == "tj":
        return {
            "trial": "Санҷишӣ",
            "active": "Фаъол",
            "expired": "Ба анҷом расида",
            "blocked": "Баста",
        }.get(status, status)
    if lang == "uz":
        return {
            "trial": "Sinov",
            "active": "Faol",
            "expired": "Tugagan",
            "blocked": "Bloklangan",
        }.get(status, status)
    return {
        "trial": "Пробный",
        "active": "Активный",
        "expired": "Закончен",
        "blocked": "Заблокирован",
    }.get(status, status)


def _level_label(level: str | None) -> str:
    return {
        "beginner": "0",
        "az0": "0",
        "hsk1": "A1",
        "hsk2": "A2",
        "hsk3": "B1",
        "hsk4": "B2",
    }.get(str(level or "").lower(), str(level or "—"))


def _profile_text(user, lang: str) -> str:
    from html import escape

    full_name = escape(str(getattr(user, "full_name", "—") or "—"))
    language = escape(str(getattr(user, "language", "—") or "—"))
    level = escape(_level_label(getattr(user, "level", None)))
    status_raw = str(getattr(user, "status", "—") or "—")
    learning_mode = escape(str(getattr(user, "learning_mode", "—") or "—"))

    started = (
        getattr(user, "start_date", None)
        or getattr(user, "trial_start_date", None)
        or getattr(user, "trial_started_at", None)
        or getattr(user, "created_at", None)
    )
    ends = (
        getattr(user, "end_date", None)
        or getattr(user, "trial_end_date", None)
        or getattr(user, "trial_ends_at", None)
        or getattr(user, "subscription_end_date", None)
        or getattr(user, "expires_at", None)
    )

    plan_raw = getattr(user, "selected_plan_type", None)

    duration_days = None
    try:
        start_dt = getattr(user, "start_date", None)
        end_dt = getattr(user, "end_date", None)
        if start_dt and end_dt:
            duration_days = (end_dt.date() - start_dt.date()).days
    except Exception:
        duration_days = None

    if plan_raw:
        plan_key = str(plan_raw)
        if lang == "tj":
            plan_map = {
                "trial_3_days": "trial 3-рӯза",
                "free_trial": "trial 3-рӯза",
                "10_days": "10 рӯз",
                "1_month": "1 моҳ",
                "monthly": "1 моҳ",
            }
        elif lang == "uz":
            plan_map = {
                "trial_3_days": "3 kunlik trial",
                "free_trial": "3 kunlik trial",
                "10_days": "10 kun",
                "1_month": "1 oy",
                "monthly": "1 oy",
            }
        else:
            plan_map = {
                "trial_3_days": "3 дня trial",
                "free_trial": "3 дня trial",
                "10_days": "10 дней",
                "1_month": "1 месяц",
                "monthly": "1 месяц",
            }
        plan_label = plan_map.get(plan_key, plan_key)
    else:
        if status_raw == "trial":
            plan_label = "trial 3-рӯза" if lang == "tj" else ("3 kunlik trial" if lang == "uz" else "3 дня trial")
        elif status_raw == "active":
            if duration_days is not None and 9 <= duration_days <= 11:
                plan_label = "10 рӯз" if lang == "tj" else ("10 kun" if lang == "uz" else "10 дней")
            elif duration_days is not None and 28 <= duration_days <= 31:
                plan_label = "1 моҳ" if lang == "tj" else ("1 oy" if lang == "uz" else "1 месяц")
            else:
                plan_label = "Обунаи фаъол" if lang == "tj" else ("Faol obuna" if lang == "uz" else "Активная подписка")
        else:
            plan_label = "—"

    status = escape(status_raw)
    plan = escape(str(plan_label))

    def fmt_date(value):
        if not value:
            return "—"
        try:
            return str(value)[:10]
        except Exception:
            return "—"

    started_str = escape(fmt_date(started))
    ends_str = escape(fmt_date(ends))

    if lang == "tj":
        text = (
            f"<b>👤 Профили шумо</b>\n\n"
            f"<blockquote>"
            f"🙍 <b>Ном:</b> {full_name}\n"
            f"🈯 <b>Забон:</b> {language}\n"
            f"📖 <b>Дараҷа:</b> {level}\n"
            f"🎯 <b>Режими ҷорӣ:</b> {learning_mode}\n"
            f"⭐ <b>Ҳолат:</b> {status}\n"
            f"💳 <b>Тариф:</b> {plan}\n\n"
            f"🗓 <b>Оғоз:</b> {started_str}\n"
            f"⌛ <b>Анҷом:</b> {ends_str}"
            f"</blockquote>"
        )
        if getattr(user, "status", "") != "active":
            text += "\n\n🔓 <b>Агар обунаро фаъол кунед</b>, метавонед аз бот бе ягон лимит истифода баред."
        else:
            text += "\n\n✅ <b>Шумо обунаи фаъол доред.</b> Шумо метавонед аз ҳамаи функсияҳои бот истифода баред."
        return text

    if lang == "uz":
        text = (
            f"<b>👤 Profilingiz</b>\n\n"
            f"<blockquote>"
            f"🙍 <b>Ism:</b> {full_name}\n"
            f"🈯 <b>Til:</b> {language}\n"
            f"📖 <b>Daraja:</b> {level}\n"
            f"🎯 <b>Joriy rejim:</b> {learning_mode}\n"
            f"⭐ <b>Holat:</b> {status}\n"
            f"💳 <b>Tarif:</b> {plan}\n\n"
            f"🗓 <b>Boshlanish:</b> {started_str}\n"
            f"⌛ <b>Tugash:</b> {ends_str}"
            f"</blockquote>"
        )
        if getattr(user, "status", "") != "active":
            text += "\n\n🔓 <b>Obuna faollashtirsangiz</b>, botdan hech qanday limitsiz foydalanasiz."
        else:
            text += "\n\n✅ <b>Sizda faol obuna bor.</b> Botning barcha funksiyalaridan foydalanishingiz mumkin."
        return text

    text = (
        f"<b>👤 Ваш профиль</b>\n\n"
        f"<blockquote>"
        f"🙍 <b>Имя:</b> {full_name}\n"
        f"🈯 <b>Язык:</b> {language}\n"
        f"📖 <b>Уровень:</b> {level}\n"
        f"🎯 <b>Текущий режим:</b> {learning_mode}\n"
        f"⭐ <b>Статус:</b> {status}\n"
        f"💳 <b>Тариф:</b> {plan}\n\n"
        f"🗓 <b>Начало:</b> {started_str}\n"
        f"⌛ <b>Окончание:</b> {ends_str}"
        f"</blockquote>"
    )
    if getattr(user, "status", "") != "active":
        text += "\n\n🔓 <b>Если активируете подписку</b>, сможете пользоваться ботом без каких-либо лимитов."
    else:
        text += "\n\n✅ <b>У вас активная подписка.</b> Вы можете пользоваться всеми функциями бота."
    return text

def profile_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    labels = {
        "tj": {
            "subscription": "💎 Обуна",
            "language": "🌐 Забон",
            "level": "📊 Дараҷа",
            "qa": "💬 Саволу ҷавоб",
        },
        "uz": {
            "subscription": "💎 Obuna",
            "language": "🌐 Til",
            "level": "📊 Daraja",
            "qa": "💬 Savol-javob",
        },
        "ru": {
            "subscription": "💎 Подписка",
            "language": "🌐 Язык",
            "level": "📊 Уровень",
            "qa": "💬 Вопрос-ответ",
        },
    }
    l = labels.get(lang, labels["ru"])
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=l["subscription"], callback_data="subscription:open"),
                InlineKeyboardButton(text=l["language"], callback_data="profile_menu:language"),
            ],
            [
                InlineKeyboardButton(text=l["level"], callback_data="profile_menu:level"),
            ],
            [
                InlineKeyboardButton(text=l["qa"], callback_data="profile_menu:qa"),
            ],
        ]
    )


@router.message(Command("profile"))
async def profile_command(message: Message, state: FSMContext, session):
    user = await UserRepository(session).get_by_telegram_id(message.from_user.id)
    lang = _lang(user)

    if not user:
        await message.answer(t("user_not_found", lang))
        return

    await _clear_voice_mode(user, session, state)
    text = _profile_text(user, lang)
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=profile_menu_keyboard(lang),
    )


@router.message(Command("subscription"))
async def subscription_command_handler(message: Message, state: FSMContext, session):
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)

    if not user:
        return

    lang = user.language if user.language else "ru"
    await _clear_voice_mode(user, session, state)

    await message.answer(
        t("payment_method_choose", lang),
        reply_markup=payment_method_keyboard(lang),
        parse_mode="HTML",
    )



def command_language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇹🇯 Тоҷикӣ", callback_data="cmdlang:tj"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="cmdlang:ru"),
                InlineKeyboardButton(text="🇺🇿 O‘zbek", callback_data="cmdlang:uz"),
            ]
        ]
    )


@router.message(Command("language"))
async def language_command_handler(message: Message, state: FSMContext, session):
    user = await UserRepository(session).get_by_telegram_id(message.from_user.id)
    lang = getattr(user, "language", None) or "ru"
    await _clear_voice_mode(user, session, state)

    await message.answer(
        t("choose_language", lang),
        reply_markup=command_language_keyboard(),
    )


@router.callback_query(F.data.startswith("cmdlang:"))
async def command_language_callback_handler(callback: CallbackQuery, session):
    lang = callback.data.split(":")[1]

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer()
        return

    user.language = lang
    await session.commit()

    await callback.answer()
    try:
        await callback.message.delete()
    except Exception:
        pass

    await callback.message.answer(t("language_selected", lang))



def command_level_keyboard(lang: str):
    kb = level_keyboard(lang)
    for row in kb.inline_keyboard:
        for btn in row:
            if btn.callback_data and btn.callback_data.startswith("level:"):
                btn.callback_data = btn.callback_data.replace("level:", "cmdlevel:", 1)
    return kb


@router.message(Command("level"))
async def level_command_handler(message: Message, state: FSMContext, session):
    user = await UserRepository(session).get_by_telegram_id(message.from_user.id)
    lang = getattr(user, "language", None) or "ru"
    await _clear_voice_mode(user, session, state)

    await message.answer(
        t("choose_level", lang),
        reply_markup=command_level_keyboard(lang),
    )


@router.callback_query(F.data.startswith("cmdlevel:"))
async def command_level_callback_handler(callback: CallbackQuery, session):
    level = callback.data.split(":", 1)[1]

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer()
        return

    user.level = level
    await session.commit()

    lang = getattr(user, "language", None) or "ru"

    await callback.answer()
    try:
        await callback.message.delete()
    except Exception:
        pass

    level_label = _level_label(level)

    if lang == "tj":
        msg = f"✅ Дараҷа нав шуд: {level_label}"
    elif lang == "uz":
        msg = f"✅ Daraja yangilandi: {level_label}"
    else:
        msg = f"✅ Уровень обновлён: {level_label}"

    await callback.message.answer(msg)



@router.message(Command("invite"))
async def invite_command_handler(message: Message, state: FSMContext, session):
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user:
        return

    await _clear_voice_mode(user, session, state)
    await user_repo.ensure_referral_code(user)
    await session.commit()

    referral_link = f"https://t.me/{settings.BOT_USERNAME}?start={user.referral_code}"
    lang = user.language if user.language else "ru"

    if lang == "tj":
        text = (
            "<b>🎁 Даъватномаи шумо</b>\n\n"
            "<blockquote>"
            f"🔗 {referral_link}"
            "</blockquote>\n\n"
            "👥 Агар дӯсти шумо бо ин силка ворид шавад ва ба бот 2 хабар фиристад,\n"
            "✨ шумо +5 саволи бонусӣ мегиред."
        )
    elif lang == "ru":
        text = (
            "<b>🎁 Ваше приглашение</b>\n\n"
            "<blockquote>"
            f"🔗 {referral_link}"
            "</blockquote>\n\n"
            "👥 Если ваш друг войдёт по этой ссылке и отправит боту 2 сообщения,\n"
            "✨ вы получите +5 бонусных вопросов."
        )
    else:
        text = (
            "<b>🎁 Taklif havolangiz</b>\n\n"
            "<blockquote>"
            f"🔗 {referral_link}"
            "</blockquote>\n\n"
            "👥 Agar do‘stingiz shu silka orqali kirib, botga 2 ta xabar yuborsa,\n"
            "✨ siz +5 bonus savol olasiz."
        )

    await message.answer(
        text,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )



@router.message(Command("help"))
async def help_command_handler(message: Message, state: FSMContext, session):
    user = await UserRepository(session).get_by_telegram_id(message.from_user.id)
    lang = getattr(user, "language", None) or "ru"
    await _clear_voice_mode(user, session, state)

    await message.answer(
        t("help_section_text", lang),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


@router.message(Command("admin_stats"))
async def admin_stats_handler(message: Message, session):
    from app.config import settings

    admin_ids = [int(x.strip()) for x in settings.ADMIN_IDS.split(",") if x.strip()]
    if message.from_user.id not in admin_ids:
        return

    # Count users by status
    result = await session.execute(
        select(User.status, func.count().label("cnt")).group_by(User.status)
    )
    status_counts = {row.status: row.cnt for row in result.fetchall()}

    # Count users by language
    result = await session.execute(
        select(User.language, func.count().label("cnt")).group_by(User.language)
    )
    lang_counts = {row.language: row.cnt for row in result.fetchall()}

    # Total users
    result = await session.execute(select(func.count()).select_from(User))
    total = result.scalar() or 0

    # Users who asked at least 1 question
    result = await session.execute(
        select(func.count()).select_from(User).where(User.questions_used > 0)
    )
    active_users = result.scalar() or 0

    # Users registered in last 7 days
    from datetime import datetime, timezone, timedelta
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    result = await session.execute(
        select(func.count()).select_from(User).where(User.created_at >= week_ago)
    )
    new_this_week = result.scalar() or 0

    # Pending payments
    from app.db.models.payment import Payment
    result = await session.execute(
        select(func.count()).select_from(Payment).where(Payment.payment_status == "pending")
    )
    pending_payments = result.scalar() or 0

    # Approved payments total
    result = await session.execute(
        select(func.count()).select_from(Payment).where(Payment.payment_status == "approved")
    )
    total_paid = result.scalar() or 0

    trial = status_counts.get("trial", 0)
    active = status_counts.get("active", 0)
    expired = status_counts.get("expired", 0)
    blocked = status_counts.get("blocked", 0)

    conversion = round(active / total * 100, 1) if total > 0 else 0
    engagement = round(active_users / total * 100, 1) if total > 0 else 0

    lang_str = " | ".join(f"{k}: {v}" for k, v in sorted(lang_counts.items()))

    text = (
        f"📊 <b>Admin statistika</b>\n\n"
        f"<b>👥 Foydalanuvchilar:</b>\n"
        f"  Jami: {total}\n"
        f"  Trial: {trial}\n"
        f"  Aktiv obuna: {active}\n"
        f"  Tugagan: {expired}\n"
        f"  Bloklangan: {blocked}\n\n"
        f"<b>📈 Konversiya:</b>\n"
        f"  Trial → Obuna: {conversion}%\n"
        f"  Savol berganlar: {active_users} ({engagement}%)\n"
        f"  Bu hafta yangilar: +{new_this_week}\n\n"
        f"<b>💳 To'lovlar:</b>\n"
        f"  Kutilmoqda: {pending_payments}\n"
        f"  Jami tasdiqlangan: {total_paid}\n\n"
        f"<b>🌐 Tillar:</b>\n"
        f"  {lang_str}"
    )

    await message.answer(text, parse_mode="HTML")


@router.callback_query(F.data == "profile_menu:language")
async def profile_menu_language(callback: CallbackQuery, state: FSMContext, session):
    user = await UserRepository(session).get_by_telegram_id(callback.from_user.id)
    lang = user.language if user and user.language else "ru"
    await _clear_voice_mode(user, session, state)
    await callback.answer()
    await callback.message.answer(
        t("choose_language", lang),
        reply_markup=command_language_keyboard(),
    )

@router.callback_query(F.data == "profile_menu:level")
async def profile_menu_level(callback: CallbackQuery, state: FSMContext, session):
    user = await UserRepository(session).get_by_telegram_id(callback.from_user.id)
    lang = user.language if user and user.language else "ru"
    await _clear_voice_mode(user, session, state)
    await callback.answer()
    await callback.message.answer(
        t("choose_level", lang),
        reply_markup=command_level_keyboard(lang),
    )

@router.callback_query(F.data == "profile_menu:course")
async def profile_menu_course(callback: CallbackQuery, state: FSMContext, session):
    from app.bot.handlers.course import run_course_entry_flow
    await state.update_data(pending_voice_transcript=None, pending_voice_message_id=None)
    await callback.answer()
    await run_course_entry_flow(
        session=session,
        telegram_id=callback.from_user.id,
        respond=callback.message.answer,
    )

@router.callback_query(F.data == "profile_menu:qa")
async def profile_menu_qa(callback: CallbackQuery, state: FSMContext, session):
    from app.repositories.user_repo import UserRepository as UR
    user_repo = UR(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer()
        return
    user.learning_mode = "qa"
    user.voice_mode = "none"
    await state.update_data(pending_voice_transcript=None, pending_voice_message_id=None)
    await session.commit()
    lang = user.language if user.language else "ru"
    await callback.answer()
    await callback.message.answer(t("send_first_message", lang))
