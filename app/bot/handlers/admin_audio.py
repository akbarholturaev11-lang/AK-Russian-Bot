"""Admin audio boshqaruv paneli.

Flow:
  /admin_audio
    → Level tanlash
      → Darslar ro'yxati (✅ audio bor / ❌ yo'q)
        → Dars tanlash → Audio turi tanlash (vocab / dialogue_1 / dialogue_2 …)
          → "Faylni yuboring" → Fayl → Saqlandi ✅ → Keyingi tur yoki keyingi dars
"""

import json
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from app.config import settings
from app.repositories.course_lesson_repo import CourseLessonRepository
from app.repositories.course_audio_repo import CourseAudioRepository
from app.bot.fsm.admin_audio import AdminAudioStates

router = Router()

LEVELS = ["hsk1", "hsk2", "hsk3", "hsk4"]


# ─── helpers ────────────────────────────────────────────────────────────────

def _is_admin(user_id: int) -> bool:
    admin_ids = [int(x.strip()) for x in settings.ADMIN_IDS.split(",") if x.strip()]
    return user_id in admin_ids


def _parse(value, default=None):
    if value is None or value == "":
        return default or []
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except Exception:
        return default or []


def _audio_types_for_lesson(lesson) -> list[str]:
    """Darsning barcha audio turlarini qaytaradi."""
    types = ["vocab"]
    dialogues = _parse(lesson.dialogue_json, [])
    for i in range(1, min(len(dialogues) + 1, 5)):
        types.append(f"dialogue_{i}")
    return types


# ─── keyboards ───────────────────────────────────────────────────────────────

def _level_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="A1", callback_data="adm_audio:level:hsk1"),
            InlineKeyboardButton(text="A2", callback_data="adm_audio:level:hsk2"),
        ],
        [
            InlineKeyboardButton(text="B1", callback_data="adm_audio:level:hsk3"),
            InlineKeyboardButton(text="B2", callback_data="adm_audio:level:hsk4"),
        ],
        [InlineKeyboardButton(text="📊 Statistika", callback_data="adm_audio:stats")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def _lessons_keyboard(lessons, uploaded_set: set, page: int = 0) -> InlineKeyboardMarkup:
    """Darslar ro'yxati. uploaded_set — kamida bitta audio yuklangan darslar lesson_order lari."""
    page_size = 8
    start = page * page_size
    end = start + page_size
    page_lessons = lessons[start:end]
    level = lessons[0].level if lessons else "hsk1"

    buttons = []
    for lesson in page_lessons:
        icon = "✅" if lesson.lesson_order in uploaded_set else "❌"
        buttons.append([InlineKeyboardButton(
            text=f"{icon} {lesson.lesson_order}. {lesson.title}",
            callback_data=f"adm_audio:lesson:{lesson.id}",
        )])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"adm_audio:page:{level}:{page-1}"))
    if end < len(lessons):
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"adm_audio:page:{level}:{page+1}"))
    if nav:
        buttons.append(nav)

    buttons.append([InlineKeyboardButton(text="◀️ Orqaga", callback_data="adm_audio:back_levels")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def _audio_types_keyboard(lesson, uploaded_types: set) -> InlineKeyboardMarkup:
    """Audio turi tanlash. Yuklanganlari ✅, yo'qlari ❌."""
    types = _audio_types_for_lesson(lesson)
    buttons = []
    row = []
    for i, atype in enumerate(types):
        icon = "✅" if atype in uploaded_types else "❌"
        label = "🔉 vocab" if atype == "vocab" else f"🔉 {atype}"
        row.append(InlineKeyboardButton(
            text=f"{icon} {label}",
            callback_data=f"adm_audio:upload:{lesson.id}:{atype}",
        ))
        if len(row) == 2 or i == len(types) - 1:
            buttons.append(row)
            row = []

    buttons.append([
        InlineKeyboardButton(text="◀️ Darslar", callback_data=f"adm_audio:level:{lesson.level}"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def _after_upload_keyboard(lesson, next_type: str | None) -> InlineKeyboardMarkup:
    """Yuklangandan keyin: keyingi tur yoki keyingi dars."""
    buttons = []
    if next_type:
        buttons.append([InlineKeyboardButton(
            text=f"➡️ Keyingi: {next_type}",
            callback_data=f"adm_audio:upload:{lesson.id}:{next_type}",
        )])
    buttons.append([
        InlineKeyboardButton(text="📋 Dars turlari", callback_data=f"adm_audio:lesson:{lesson.id}"),
        InlineKeyboardButton(text="📚 Darslar", callback_data=f"adm_audio:level:{lesson.level}"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ─── /admin_audio entry ──────────────────────────────────────────────────────

@router.message(Command("admin_audio"))
async def admin_audio_entry(message: Message, state: FSMContext):
    if not _is_admin(message.from_user.id):
        return
    await state.clear()
    await message.answer(
        "🎵 <b>Audio boshqaruv paneli</b>\n\nQaysi daraja?",
        reply_markup=_level_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "adm:audio_panel")
async def admin_audio_from_panel(callback: CallbackQuery, state: FSMContext):
    """Admin paneldagi '🎵 Audio boshqaruv' tugmasi."""
    if not _is_admin(callback.from_user.id):
        await callback.answer()
        return
    await state.clear()
    await callback.answer()
    await callback.message.edit_text(
        "🎵 <b>Audio boshqaruv paneli</b>\n\nQaysi daraja?",
        reply_markup=_level_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "adm_audio:back_levels")
async def back_to_levels(callback: CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user.id):
        await callback.answer()
        return
    await state.clear()
    await callback.message.edit_text(
        "🎵 <b>Audio boshqaruv paneli</b>\n\nQaysi daraja?",
        reply_markup=_level_keyboard(),
        parse_mode="HTML",
    )


# ─── statistika ─────────────────────────────────────────────────────────────

@router.callback_query(F.data == "adm_audio:stats")
async def audio_stats(callback: CallbackQuery, session):
    if not _is_admin(callback.from_user.id):
        await callback.answer()
        return

    lesson_repo = CourseLessonRepository(session)
    audio_repo = CourseAudioRepository(session)

    lines = ["📊 <b>Audio holati</b>\n"]
    for level in LEVELS:
        lessons = await lesson_repo.list_by_level(level)
        if not lessons:
            continue
        uploaded = await audio_repo.count_uploaded_lessons(level)
        total = len(lessons)
        bar = "▓" * uploaded + "░" * (total - uploaded)
        lines.append(f"<b>{level.upper()}</b>: {uploaded}/{total}  {bar}")

    await callback.answer()
    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Orqaga", callback_data="adm_audio:back_levels")]
        ]),
        parse_mode="HTML",
    )


# ─── level → darslar ro'yxati ────────────────────────────────────────────────

async def _show_lessons(callback: CallbackQuery, session, level: str, page: int = 0):
    lesson_repo = CourseLessonRepository(session)
    audio_repo = CourseAudioRepository(session)

    lessons = await lesson_repo.list_by_level(level)
    if not lessons:
        await callback.answer("Bu darajada dars yo'q", show_alert=True)
        return

    uploaded_orders = await audio_repo.get_uploaded_lesson_orders(level)
    total = len(lessons)
    uploaded = len(uploaded_orders)

    await callback.message.edit_text(
        f"📚 <b>{level.upper()}</b> — {total} dars\n"
        f"✅ Audio yuklangan: <b>{uploaded}</b> / {total}\n\n"
        f"Darsni tanlang:",
        reply_markup=_lessons_keyboard(lessons, uploaded_orders, page),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("adm_audio:level:"))
async def show_lessons_for_level(callback: CallbackQuery, session):
    if not _is_admin(callback.from_user.id):
        await callback.answer()
        return
    level = callback.data.split(":")[-1]
    await callback.answer()
    await _show_lessons(callback, session, level, page=0)


@router.callback_query(F.data.startswith("adm_audio:page:"))
async def paginate_lessons(callback: CallbackQuery, session):
    if not _is_admin(callback.from_user.id):
        await callback.answer()
        return
    parts = callback.data.split(":")
    level = parts[2]
    page = int(parts[3])
    await callback.answer()
    await _show_lessons(callback, session, level, page=page)


# ─── dars → audio turi tanlash ───────────────────────────────────────────────

@router.callback_query(F.data.startswith("adm_audio:lesson:"))
async def show_audio_types(callback: CallbackQuery, session):
    if not _is_admin(callback.from_user.id):
        await callback.answer()
        return

    lesson_id = int(callback.data.split(":")[-1])
    lesson_repo = CourseLessonRepository(session)
    audio_repo = CourseAudioRepository(session)

    lesson = await lesson_repo.get_by_id(lesson_id)
    if not lesson:
        await callback.answer("Dars topilmadi", show_alert=True)
        return

    uploaded_rows = await audio_repo.list_for_lesson(lesson.level, lesson.lesson_order)
    uploaded_types = {r.audio_type for r in uploaded_rows}
    all_types = _audio_types_for_lesson(lesson)
    missing = [t for t in all_types if t not in uploaded_types]

    status = "✅ Hammasi yuklangan!" if not missing else f"❌ Kerak: {', '.join(missing)}"

    await callback.answer()
    await callback.message.edit_text(
        f"🎵 <b>{lesson.level.upper()} · Dars {lesson.lesson_order}</b>\n"
        f"📖 {lesson.title}\n\n"
        f"{status}\n\n"
        f"Qaysi audio turini yuklaysiz?",
        reply_markup=_audio_types_keyboard(lesson, uploaded_types),
        parse_mode="HTML",
    )


# ─── audio turi tanlandi → fayl kutish ───────────────────────────────────────

@router.callback_query(F.data.startswith("adm_audio:upload:"))
async def ask_for_audio_file(callback: CallbackQuery, session, state: FSMContext):
    if not _is_admin(callback.from_user.id):
        await callback.answer()
        return

    parts = callback.data.split(":")
    lesson_id = int(parts[2])
    audio_type = parts[3]

    lesson_repo = CourseLessonRepository(session)
    lesson = await lesson_repo.get_by_id(lesson_id)
    if not lesson:
        await callback.answer("Dars topilmadi", show_alert=True)
        return

    await state.set_state(AdminAudioStates.waiting_for_audio)
    await state.update_data(
        lesson_id=lesson_id,
        audio_type=audio_type,
        level=lesson.level,
        lesson_order=lesson.lesson_order,
    )

    type_label = "so'zlar (vocab)" if audio_type == "vocab" else audio_type
    await callback.answer()
    await callback.message.edit_text(
        f"🎙 <b>{lesson.level.upper()} · Dars {lesson.lesson_order} · {audio_type}</b>\n"
        f"📖 {lesson.title}\n\n"
        f"⬇️ <b>{type_label}</b> uchun audio faylni yuboring\n"
        f"(voice yoki mp3/ogg fayl)",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"adm_audio:lesson:{lesson_id}")]
        ]),
        parse_mode="HTML",
    )


# ─── fayl qabul qilish ───────────────────────────────────────────────────────

@router.message(StateFilter(AdminAudioStates.waiting_for_audio), F.voice | F.audio | F.document)
async def receive_audio_file(message: Message, session, state: FSMContext):
    if not _is_admin(message.from_user.id):
        return

    data = await state.get_data()
    lesson_id = data.get("lesson_id")
    audio_type = data.get("audio_type")
    level = data.get("level")
    lesson_order = data.get("lesson_order")

    # file_id olish
    if message.voice:
        file_id = message.voice.file_id
    elif message.audio:
        file_id = message.audio.file_id
    elif message.document:
        file_id = message.document.file_id
    else:
        await message.answer("❌ Audio, voice yoki fayl yuboring")
        return

    audio_repo = CourseAudioRepository(session)
    lesson_repo = CourseLessonRepository(session)

    await audio_repo.upsert(level=level, lesson_order=lesson_order, audio_type=audio_type, file_id=file_id)
    await state.clear()

    lesson = await lesson_repo.get_by_id(lesson_id)
    if not lesson:
        await message.answer("✅ Saqlandi!")
        return

    # Keyingi yuklanmagan audio turini topamiz
    all_types = _audio_types_for_lesson(lesson)
    uploaded_rows = await audio_repo.list_for_lesson(level, lesson_order)
    uploaded_types = {r.audio_type for r in uploaded_rows}
    missing = [t for t in all_types if t not in uploaded_types]
    next_type = missing[0] if missing else None

    remaining = f"\n⏳ Qolgan: {', '.join(missing)}" if missing else "\n🎉 Bu darsning barcha audiolari yuklandi!"

    await message.answer(
        f"✅ <b>Saqlandi!</b>\n"
        f"📍 {level.upper()} · Dars {lesson_order} · <code>{audio_type}</code>"
        f"{remaining}",
        reply_markup=_after_upload_keyboard(lesson, next_type),
        parse_mode="HTML",
    )


@router.message(StateFilter(AdminAudioStates.waiting_for_audio))
async def wrong_file_type(message: Message):
    if not _is_admin(message.from_user.id):
        return
    await message.answer("⚠️ Voice yoki audio fayl yuboring (matn emas)")
