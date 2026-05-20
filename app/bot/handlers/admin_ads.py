from datetime import datetime, timedelta, timezone
from html import escape
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.fsm.admin_ads import AdCampaignStates
from app.bot.keyboards.admin_ads import (
    ad_active_policy_keyboard,
    ad_cancel_keyboard,
    ad_confirm_keyboard,
    ad_duration_keyboard,
    ad_language_keyboard,
    ad_list_keyboard,
    ad_panel_keyboard,
    ad_send_count_keyboard,
    ad_start_keyboard,
)
from app.config import settings
from app.repositories.ad_campaign_repo import AdCampaignRepository, decode_languages
from app.repositories.user_repo import UserRepository
from app.services.ad_campaign_service import send_ad_payload

router = Router()

ADMIN_TZ = ZoneInfo("Asia/Shanghai")
MIN_SEND_INTERVAL_SECONDS = 10 * 60
MAX_SENDS_PER_CAMPAIGN = 24
_PANEL_CHAT_ID = "ad_panel_chat_id"
_PANEL_MSG_ID = "ad_panel_msg_id"

_LANG_LABELS = {"uz": "UZ", "ru": "RU", "tj": "TJ"}
_MEDIA_LABELS = {"text": "Matn", "photo": "Foto", "video": "Video"}


def _is_admin(user_id: int) -> bool:
    return user_id in settings.admin_id_list


def _admin_ids() -> set[int]:
    return set(settings.admin_id_list)


def _selected_languages(data: dict) -> list[str]:
    values = data.get("target_languages") or []
    return [item for item in values if item in _LANG_LABELS]


def _fmt_languages(languages: list[str]) -> str:
    if not languages:
        return "Hammasi"
    return ", ".join(_LANG_LABELS[item] for item in languages)


def _fmt_time(value) -> str:
    if not value:
        return "—"
    return value.astimezone(ADMIN_TZ).strftime("%Y-%m-%d %H:%M")


def _fmt_duration(hours: int | None) -> str:
    if not hours:
        return "—"
    if hours % 24 == 0:
        return f"{hours // 24} kun"
    return f"{hours} soat"


def _fmt_interval(duration_hours: int | None, send_count: int | None) -> str:
    if not duration_hours or not send_count:
        return "—"
    if send_count <= 1:
        return "Bir marta"
    seconds = int(duration_hours * 3600 / max(send_count, 1))
    if seconds % 3600 == 0:
        return f"Har {seconds // 3600} soatda"
    if seconds >= 3600:
        return f"Har {seconds / 3600:.1f} soatda"
    return f"Har {max(seconds // 60, 1)} daqiqada"


def _fmt_active_policy(include_active: bool | None) -> str:
    if include_active:
        return "Ruxsat berilgan"
    return "Yuborilmaydi"


def _content_preview(data: dict, limit: int = 180) -> str:
    content_type = data.get("content_type") or "text"
    text = data.get("message_text") or ""
    if not text:
        return f"[{_MEDIA_LABELS.get(content_type, content_type)}]"
    return text[:limit] + ("..." if len(text) > limit else "")


def _validate_send_count(duration_hours: int, send_count: int) -> str | None:
    if send_count < 1:
        return "Kamida 1 marta bo'lishi kerak."
    if send_count > MAX_SENDS_PER_CAMPAIGN:
        return f"Maksimum {MAX_SENDS_PER_CAMPAIGN} marta. Bu anti-spam limit."
    if send_count > 1:
        interval = duration_hours * 3600 / send_count
        if interval < MIN_SEND_INTERVAL_SECONDS:
            return "Bu muddat uchun yuborish soni ko'p. Kamida 10 daqiqa oralig' qoldiring."
    return None


def _wizard_text(data: dict, prompt: str, error: str | None = None) -> str:
    starts_at = data.get("starts_at")
    duration_hours = data.get("duration_hours")
    ends_at = starts_at + timedelta(hours=duration_hours) if starts_at and duration_hours else None
    content_type = data.get("content_type")
    send_count = data.get("send_count_total")
    languages = _selected_languages(data)

    lines = [
        "📣 <b>Yangi reklama kampaniyasi</b>",
        "",
        "<blockquote>",
        f"Nomi: <b>{escape(str(data.get('title') or '—'))}</b>",
        f"Xabar: <b>{_MEDIA_LABELS.get(content_type, '—')}</b>",
        f"Muddat: <b>{_fmt_duration(duration_hours)}</b>",
        f"Yuborish: <b>{send_count or '—'} marta</b>",
        f"Interval: <b>{_fmt_interval(duration_hours, send_count)}</b>",
        f"Til: <b>{_fmt_languages(languages)}</b>",
        f"Faol obuna: <b>{_fmt_active_policy(data.get('include_active_subscribers'))}</b>",
        f"Boshlanish: <b>{_fmt_time(starts_at)}</b>",
        f"Tugash: <b>{_fmt_time(ends_at)}</b>",
        "</blockquote>",
        "",
        f"➡️ <b>{prompt}</b>",
    ]
    if error:
        lines.extend(["", f"⚠️ {escape(error)}"])
    return "\n".join(lines)


async def _remember_panel(state: FSMContext, callback: CallbackQuery) -> None:
    if not callback.message:
        return
    await state.update_data(
        **{
            _PANEL_CHAT_ID: callback.message.chat.id,
            _PANEL_MSG_ID: callback.message.message_id,
        }
    )


async def _edit_callback_panel(
    callback: CallbackQuery,
    state: FSMContext,
    text: str,
    reply_markup=None,
) -> None:
    await _remember_panel(state, callback)
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
    except Exception:
        pass


async def _edit_stored_panel(
    message: Message,
    state: FSMContext,
    text: str,
    reply_markup=None,
) -> None:
    data = await state.get_data()
    chat_id = data.get(_PANEL_CHAT_ID)
    message_id = data.get(_PANEL_MSG_ID)
    if chat_id and message_id:
        try:
            await message.bot.edit_message_text(
                text=text,
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=reply_markup,
                parse_mode="HTML",
            )
            return
        except Exception:
            pass

    sent = await message.answer(text, reply_markup=reply_markup, parse_mode="HTML")
    await state.update_data(**{_PANEL_CHAT_ID: sent.chat.id, _PANEL_MSG_ID: sent.message_id})


async def _delete_admin_input(message: Message) -> None:
    try:
        await message.delete()
    except Exception:
        pass


async def _target_count(session, data: dict) -> int:
    users = await UserRepository(session).get_ad_target_users(
        languages=_selected_languages(data),
        include_active_subscribers=bool(data.get("include_active_subscribers")),
    )
    admin_ids = _admin_ids()
    return len([user for user in users if user.telegram_id not in admin_ids])


async def _confirm_text(session, data: dict) -> str:
    starts_at = data["starts_at"]
    ends_at = starts_at + timedelta(hours=data["duration_hours"])
    target_count = await _target_count(session, data)
    preview = escape(_content_preview(data))
    return (
        "📣 <b>Reklama tasdiqlash</b>\n\n"
        f"Nomi: <b>{escape(str(data['title']))}</b>\n"
        f"Tur: <b>{_MEDIA_LABELS.get(data.get('content_type'), '—')}</b>\n"
        f"<blockquote>{preview}</blockquote>\n\n"
        f"Muddat: <b>{_fmt_time(starts_at)}</b> dan <b>{_fmt_time(ends_at)}</b> gacha\n"
        f"Yuborish: <b>{data['send_count_total']} marta</b> · {_fmt_interval(data['duration_hours'], data['send_count_total'])}\n"
        f"Til: <b>{_fmt_languages(_selected_languages(data))}</b>\n"
        f"Faol obuna: <b>{_fmt_active_policy(data.get('include_active_subscribers'))}</b>\n"
        f"Target: <b>{target_count} ta user</b>\n\n"
        "Ishga tushirilsa scheduler 1 daqiqa ichida due bo'lgan xabarlarni yuboradi."
    )


async def _show_confirm_from_callback(callback: CallbackQuery, state: FSMContext, session) -> None:
    data = await state.get_data()
    await _edit_callback_panel(callback, state, await _confirm_text(session, data), ad_confirm_keyboard())


async def _show_confirm_from_message(message: Message, state: FSMContext, session) -> None:
    data = await state.get_data()
    await _edit_stored_panel(message, state, await _confirm_text(session, data), ad_confirm_keyboard())


async def _set_send_count_from_value(
    *,
    value: int,
    state: FSMContext,
    message: Message | None = None,
    callback: CallbackQuery | None = None,
) -> bool:
    data = await state.get_data()
    duration_hours = int(data.get("duration_hours") or 0)
    error = _validate_send_count(duration_hours, value)
    if error:
        text = _wizard_text(data, "Necha marta yuborilsin?", error)
        if callback:
            await _edit_callback_panel(callback, state, text, ad_send_count_keyboard())
        elif message:
            await _edit_stored_panel(message, state, text, ad_send_count_keyboard())
        return False

    await state.update_data(send_count_total=value)
    await state.set_state(None)
    data = await state.get_data()
    text = _wizard_text(data, "Qaysi til egalariga chiqsin? Tanlamasangiz hammasiga chiqadi.")
    keyboard = ad_language_keyboard(_selected_languages(data))
    if callback:
        await _edit_callback_panel(callback, state, text, keyboard)
    elif message:
        await _edit_stored_panel(message, state, text, keyboard)
    return True


@router.message(Command("ads"))
async def ads_command(message: Message, state: FSMContext):
    if not _is_admin(message.from_user.id):
        return
    await state.clear()
    await message.answer(
        "📣 <b>Reklama boshqaruvi</b>\n\n"
        "Kampaniya matn/foto/video oladi, muddat ichida belgilangan marta target userlarga yuboradi.",
        reply_markup=ad_panel_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "adm:ads_panel")
async def admin_ads_panel(callback: CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user.id):
        await callback.answer()
        return
    await state.clear()
    await callback.answer()
    await _edit_callback_panel(
        callback,
        state,
        "📣 <b>Reklama boshqaruvi</b>\n\n"
        "Broadcastdan farqi: reklama kampaniyasi vaqt oralig'ida bir necha marta avtomatik yuboriladi.",
        ad_panel_keyboard(),
    )


@router.callback_query(F.data == "ads:new")
async def ads_new(callback: CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user.id):
        await callback.answer()
        return
    await state.clear()
    await state.set_state(AdCampaignStates.waiting_title)
    await callback.answer()
    await _edit_callback_panel(
        callback,
        state,
        _wizard_text({}, "Kampaniya nomini yozing. Masalan: May reklama"),
        ad_cancel_keyboard(),
    )


@router.message(StateFilter(AdCampaignStates.waiting_title))
async def ads_title(message: Message, state: FSMContext):
    if not _is_admin(message.from_user.id):
        return
    title = (message.text or "").strip()
    if len(title) < 2:
        data = await state.get_data()
        await _delete_admin_input(message)
        await _edit_stored_panel(
            message,
            state,
            _wizard_text(data, "Kampaniya nomini yozing. Masalan: May reklama", "Nom juda qisqa."),
            ad_cancel_keyboard(),
        )
        return

    await state.update_data(title=title[:120])
    await state.set_state(AdCampaignStates.waiting_content)
    data = await state.get_data()
    await _delete_admin_input(message)
    await _edit_stored_panel(
        message,
        state,
        _wizard_text(data, "Reklama xabarini yuboring: matn, foto + caption yoki video + caption."),
        ad_cancel_keyboard(),
    )


@router.message(StateFilter(AdCampaignStates.waiting_content))
async def ads_content(message: Message, state: FSMContext):
    if not _is_admin(message.from_user.id):
        return

    text = message.text or message.caption or ""
    content_type = "text"
    media_file_id = None
    if message.photo:
        content_type = "photo"
        media_file_id = message.photo[-1].file_id
    elif message.video:
        content_type = "video"
        media_file_id = message.video.file_id

    if not text and not media_file_id:
        data = await state.get_data()
        await _delete_admin_input(message)
        await _edit_stored_panel(
            message,
            state,
            _wizard_text(data, "Matn, foto yoki video yuboring.", "Xabar bo'sh bo'lmasin."),
            ad_cancel_keyboard(),
        )
        return
    if content_type == "text" and len(text) > 4096:
        data = await state.get_data()
        await _edit_stored_panel(message, state, _wizard_text(data, "Qisqaroq matn yuboring.", "Matn 4096 belgidan oshmasin."), ad_cancel_keyboard())
        return
    if content_type in {"photo", "video"} and len(text) > 1024:
        data = await state.get_data()
        await _edit_stored_panel(message, state, _wizard_text(data, "Captionni qisqartiring.", "Foto/video caption 1024 belgidan oshmasin."), ad_cancel_keyboard())
        return

    await state.update_data(
        message_text=text,
        content_type=content_type,
        media_file_id=media_file_id,
    )
    await state.set_state(None)
    data = await state.get_data()
    await _delete_admin_input(message)
    await _edit_stored_panel(
        message,
        state,
        _wizard_text(data, "Reklama qancha muddat aktiv bo'lsin?"),
        ad_duration_keyboard(),
    )


@router.callback_query(F.data.startswith("ads:duration:"))
async def ads_duration(callback: CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user.id):
        await callback.answer()
        return
    value = callback.data.split(":")[2]
    await callback.answer()
    if value == "custom":
        await state.set_state(AdCampaignStates.waiting_custom_duration)
        data = await state.get_data()
        await _edit_callback_panel(
            callback,
            state,
            _wizard_text(data, "Muddatni soatda yozing. Masalan: 48"),
            ad_cancel_keyboard(),
        )
        return

    await state.update_data(duration_hours=int(value))
    data = await state.get_data()
    await _edit_callback_panel(
        callback,
        state,
        _wizard_text(data, "Belgilangan muddat ichida necha marta yuborilsin?"),
        ad_send_count_keyboard(),
    )


@router.message(StateFilter(AdCampaignStates.waiting_custom_duration))
async def ads_custom_duration(message: Message, state: FSMContext):
    if not _is_admin(message.from_user.id):
        return
    try:
        hours = int((message.text or "").strip())
    except ValueError:
        data = await state.get_data()
        await _delete_admin_input(message)
        await _edit_stored_panel(message, state, _wizard_text(data, "Muddatni soatda yozing. Masalan: 48", "Soat raqam bo'lishi kerak."), ad_cancel_keyboard())
        return
    if hours < 1 or hours > 24 * 365:
        data = await state.get_data()
        await _delete_admin_input(message)
        await _edit_stored_panel(message, state, _wizard_text(data, "Muddatni soatda yozing. Masalan: 48", "Muddat 1 soatdan 365 kungacha bo'lsin."), ad_cancel_keyboard())
        return

    await state.update_data(duration_hours=hours)
    await state.set_state(None)
    data = await state.get_data()
    await _delete_admin_input(message)
    await _edit_stored_panel(
        message,
        state,
        _wizard_text(data, "Belgilangan muddat ichida necha marta yuborilsin?"),
        ad_send_count_keyboard(),
    )


@router.callback_query(F.data.startswith("ads:count:"))
async def ads_count_callback(callback: CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user.id):
        await callback.answer()
        return
    value = callback.data.split(":")[2]
    await callback.answer()
    if value == "custom":
        await state.set_state(AdCampaignStates.waiting_send_count)
        data = await state.get_data()
        await _edit_callback_panel(
            callback,
            state,
            _wizard_text(data, "Necha marta yuborilsin? Masalan: 4"),
            ad_cancel_keyboard(),
        )
        return
    await _set_send_count_from_value(value=int(value), state=state, callback=callback)


@router.message(StateFilter(AdCampaignStates.waiting_send_count))
async def ads_send_count_message(message: Message, state: FSMContext):
    if not _is_admin(message.from_user.id):
        return
    try:
        count = int((message.text or "").strip())
    except ValueError:
        data = await state.get_data()
        await _delete_admin_input(message)
        await _edit_stored_panel(message, state, _wizard_text(data, "Necha marta yuborilsin? Masalan: 4", "Son raqam bo'lishi kerak."), ad_cancel_keyboard())
        return
    await _delete_admin_input(message)
    await _set_send_count_from_value(value=count, state=state, message=message)


@router.callback_query(F.data.startswith("ads:lang:"))
async def ads_language_toggle(callback: CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user.id):
        await callback.answer()
        return
    value = callback.data.split(":")[2]
    data = await state.get_data()
    selected = set(_selected_languages(data))
    if value == "all":
        selected.clear()
    elif value in _LANG_LABELS:
        if value in selected:
            selected.remove(value)
        else:
            selected.add(value)
    await state.update_data(target_languages=sorted(selected))
    data = await state.get_data()
    await callback.answer()
    await _edit_callback_panel(
        callback,
        state,
        _wizard_text(data, "Qaysi til egalariga chiqsin? Tanlamasangiz hammasiga chiqadi."),
        ad_language_keyboard(_selected_languages(data)),
    )


@router.callback_query(F.data == "ads:lang_done")
async def ads_language_done(callback: CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user.id):
        await callback.answer()
        return
    await callback.answer()
    data = await state.get_data()
    await _edit_callback_panel(
        callback,
        state,
        _wizard_text(data, "Faol obunachilarga reklama borishiga ruxsat berasizmi?"),
        ad_active_policy_keyboard(),
    )


@router.callback_query(F.data.startswith("ads:active:"))
async def ads_active_policy(callback: CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user.id):
        await callback.answer()
        return
    include_active = callback.data.split(":")[2] == "yes"
    await state.update_data(include_active_subscribers=include_active)
    data = await state.get_data()
    await callback.answer()
    await _edit_callback_panel(
        callback,
        state,
        _wizard_text(data, "Qachon ishga tushsin?"),
        ad_start_keyboard(),
    )


@router.callback_query(F.data.startswith("ads:start:"))
async def ads_start(callback: CallbackQuery, state: FSMContext, session):
    if not _is_admin(callback.from_user.id):
        await callback.answer()
        return
    mode = callback.data.split(":")[2]
    await callback.answer()
    if mode == "scheduled":
        await state.set_state(AdCampaignStates.waiting_start_at)
        data = await state.get_data()
        await _edit_callback_panel(
            callback,
            state,
            _wizard_text(data, "Boshlanish vaqtini yozing: YYYY-MM-DD HH:MM. Vaqt zonasi: Asia/Shanghai"),
            ad_cancel_keyboard(),
        )
        return

    await state.update_data(starts_at=datetime.now(timezone.utc))
    await _show_confirm_from_callback(callback, state, session)


@router.message(StateFilter(AdCampaignStates.waiting_start_at))
async def ads_start_at_message(message: Message, state: FSMContext, session):
    if not _is_admin(message.from_user.id):
        return
    raw = (message.text or "").strip()
    try:
        local_dt = datetime.strptime(raw, "%Y-%m-%d %H:%M").replace(tzinfo=ADMIN_TZ)
    except ValueError:
        data = await state.get_data()
        await _delete_admin_input(message)
        await _edit_stored_panel(
            message,
            state,
            _wizard_text(
                data,
                "Boshlanish vaqtini yozing: YYYY-MM-DD HH:MM. Vaqt zonasi: Asia/Shanghai",
                "Format noto'g'ri. Masalan: 2026-05-20 21:30",
            ),
            ad_cancel_keyboard(),
        )
        return

    starts_at = local_dt.astimezone(timezone.utc)
    if starts_at < datetime.now(timezone.utc) - timedelta(minutes=5):
        data = await state.get_data()
        await _delete_admin_input(message)
        await _edit_stored_panel(message, state, _wizard_text(data, "Kelajakdagi vaqtni yozing.", "Boshlanish vaqti o'tib ketgan."), ad_cancel_keyboard())
        return

    await state.update_data(starts_at=starts_at)
    await state.set_state(None)
    await _delete_admin_input(message)
    await _show_confirm_from_message(message, state, session)


@router.callback_query(F.data == "ads:test")
async def ads_test(callback: CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user.id):
        await callback.answer()
        return
    data = await state.get_data()
    if not data.get("content_type"):
        await callback.answer("Xabar topilmadi", show_alert=True)
        return
    try:
        await send_ad_payload(
            callback.bot,
            chat_id=callback.from_user.id,
            text=data.get("message_text"),
            content_type=data.get("content_type"),
            media_file_id=data.get("media_file_id"),
        )
        await callback.answer("Test yuborildi", show_alert=True)
    except Exception as exc:
        await callback.answer(f"Test xato: {str(exc)[:80]}", show_alert=True)


@router.callback_query(F.data == "ads:confirm")
async def ads_confirm(callback: CallbackQuery, state: FSMContext, session):
    if not _is_admin(callback.from_user.id):
        await callback.answer()
        return
    data = await state.get_data()
    required = ["title", "content_type", "duration_hours", "send_count_total", "starts_at"]
    if any(key not in data for key in required):
        await callback.answer("Ma'lumot yetishmayapti", show_alert=True)
        return

    starts_at = data["starts_at"]
    ends_at = starts_at + timedelta(hours=data["duration_hours"])
    target_count = await _target_count(session, data)
    campaign = await AdCampaignRepository(session).create(
        title=data["title"],
        message_text=data.get("message_text") or None,
        content_type=data["content_type"],
        media_file_id=data.get("media_file_id"),
        starts_at=starts_at,
        ends_at=ends_at,
        send_count_total=int(data["send_count_total"]),
        target_languages=_selected_languages(data),
        include_active_subscribers=bool(data.get("include_active_subscribers")),
        created_by_telegram_id=callback.from_user.id,
    )
    campaign_id = campaign.id
    await session.commit()
    await state.clear()
    await callback.answer("Reklama saqlandi", show_alert=True)
    await callback.message.edit_text(
        f"✅ Reklama #{campaign_id} ishga tushirildi.\n"
        f"Target: {target_count} ta user\n"
        f"Boshlanish: {_fmt_time(starts_at)}\n"
        f"Tugash: {_fmt_time(ends_at)}\n\n"
        "Scheduler due bo'lgan xabarlarni 1 daqiqa ichida yuboradi.",
        reply_markup=ad_panel_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "ads:list")
async def ads_list(callback: CallbackQuery, session):
    if not _is_admin(callback.from_user.id):
        await callback.answer()
        return
    repo = AdCampaignRepository(session)
    campaigns = await repo.list_recent(10)
    await callback.answer()
    if not campaigns:
        await callback.message.edit_text(
            "Hozircha reklama kampaniyasi yo'q.",
            reply_markup=ad_panel_keyboard(),
            parse_mode="HTML",
        )
        return

    now = datetime.now(timezone.utc)
    lines = ["📋 <b>Oxirgi reklama kampaniyalari</b>", ""]
    for item in campaigns:
        sent = await repo.count_deliveries(item.id, "sent")
        failed = await repo.count_deliveries(item.id, "failed")
        if item.is_active and item.starts_at > now:
            status = "kutmoqda"
        elif item.is_active and item.ends_at >= now:
            status = "aktiv"
        elif item.rounds_sent >= item.send_count_total:
            status = "tugagan"
        else:
            status = "to'xtatilgan"
        langs = _fmt_languages(decode_languages(item.target_languages))
        active = _fmt_active_policy(item.include_active_subscribers)
        lines.append(
            f"#{item.id} <b>{escape(item.title)}</b> — {status}\n"
            f"  {item.rounds_sent}/{item.send_count_total} raund · sent: {sent}, xato: {failed}\n"
            f"  Til: {langs} · Faol obuna: {active}\n"
            f"  Keyingi: {_fmt_time(item.next_send_at)}"
        )

    await callback.message.edit_text(
        "\n\n".join(lines),
        reply_markup=ad_list_keyboard(campaigns),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("ads:disable:"))
async def ads_disable(callback: CallbackQuery, session):
    if not _is_admin(callback.from_user.id):
        await callback.answer()
        return
    campaign_id = int(callback.data.split(":")[2])
    repo = AdCampaignRepository(session)
    campaign = await repo.get_by_id(campaign_id)
    if not campaign:
        await callback.answer("Topilmadi", show_alert=True)
        return
    await repo.deactivate(campaign)
    await session.commit()
    await callback.answer("To'xtatildi", show_alert=True)
    await callback.message.edit_text(
        f"⛔ Reklama #{campaign_id} to'xtatildi.",
        reply_markup=ad_panel_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "ads:cancel")
async def ads_cancel(callback: CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user.id):
        await callback.answer()
        return
    await state.clear()
    await callback.answer()
    await callback.message.edit_text(
        "❌ Reklama kampaniyasi bekor qilindi.",
        reply_markup=ad_panel_keyboard(),
        parse_mode="HTML",
    )
