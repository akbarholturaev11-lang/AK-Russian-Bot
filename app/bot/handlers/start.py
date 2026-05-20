from datetime import datetime, timezone, timedelta

from aiogram import Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.services.onboarding_service import OnboardingService
from app.bot.utils.i18n import t
from app.bot.keyboards.onboarding import language_keyboard, level_keyboard
from app.bot.keyboards.main_menu import main_menu_keyboard
from app.bot.fsm.onboarding import OnboardingStates


router = Router()


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    state: FSMContext,
    session,
    command: CommandObject,
):
    service = OnboardingService(session)
    first_name = message.from_user.first_name if message.from_user and message.from_user.first_name else "Friend"

    referral_code = command.args if command and command.args else None

    user, created = await service.get_or_create_user(
        telegram_id=message.from_user.id,
        full_name=message.from_user.full_name if message.from_user else None,
        username=message.from_user.username if message.from_user else None,
        referral_code=referral_code,
    )

    await state.clear()

    if not created and user.language and user.level:
        user.learning_mode = "qa"
        user.voice_mode = "none"
        await session.commit()
        await message.answer(
            t("welcome_back", user.language, name=first_name),
            reply_markup=main_menu_keyboard(user.language),
        )
        return

    onboarding_msg = await message.answer(
        f"{t('welcome', user.language, name=first_name)}\n\n{t('choose_language', user.language)}",
        reply_markup=language_keyboard(),
    )

    await state.update_data(
        onboarding_message_id=onboarding_msg.message_id,
        first_name=first_name,
    )
    await state.set_state(OnboardingStates.choosing_language)


@router.callback_query(OnboardingStates.choosing_language)
async def process_language(callback: CallbackQuery, state: FSMContext, session):
    lang = callback.data.split(":")[1]

    service = OnboardingService(session)

    user, _ = await service.get_or_create_user(
        telegram_id=callback.from_user.id,
        full_name=callback.from_user.full_name if callback.from_user else None,
        username=callback.from_user.username if callback.from_user else None,
    )
    user.language = lang
    await session.commit()

    await callback.answer()

    data = await state.get_data()
    onboarding_message_id = data.get("onboarding_message_id")
    first_name = data.get("first_name", "Friend")

    try:
        if onboarding_message_id:
            await callback.bot.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=onboarding_message_id,
                text=f"{t('welcome', lang, name=first_name)}\n\n{t('choose_level', lang)}",
                reply_markup=level_keyboard(lang),
            )
    except Exception:
        pass

    await state.update_data(lang=lang)
    await state.set_state(OnboardingStates.choosing_level)


def _get_demo_lesson(level: str, lang: str) -> tuple:
    """Returns (display_text, ai_context) tuple."""

    level_key = (level or "").lower().replace(" ", "").replace("_", "")
    lang_key = lang if lang in ("tj", "uz", "ru") else "ru"
    level_label = {
        "beginner": "beginner",
        "az0": "beginner",
        "hsk1": "A1",
        "hsk2": "A2",
        "hsk3": "B1",
        "hsk4": "B2",
    }.get(level_key, "beginner")

    challenges = {
        "beginner": {
            "tj": (
                "🎮 <b>Омода-ед? Бозӣ мекунем!</b>\n\n"
                "Ман ба шумо 3 калима медиҳам:\n\n"
                "✨ <b>привет</b> · <b>спасибо</b> · <b>пока</b>\n\n"
                "Аз ин калимаҳо як ҷумла созед — хато ҳам бошад, бот тасҳеҳ мекунад 😄",
                "The user just started learning Russian (beginner level). "
                "You gave them a challenge: make a sentence using привет, спасибо, пока. "
                "Their next message is their attempt. Encourage them, correct gently, explain the words."
            ),
            "uz": (
                "🎮 <b>Tayyor bo'ldingizmi? O'yin boshlanadi!</b>\n\n"
                "Sizga 3 ta so'z beraman:\n\n"
                "✨ <b>привет</b> · <b>спасибо</b> · <b>пока</b>\n\n"
                "Shu so'zlardan bitta gap tuzing — xato bo'lsa ham, bot tuzatadi 😄",
                "The user just started learning Russian (beginner level). "
                "You gave them a challenge: make a sentence using привет, спасибо, пока. "
                "Their next message is their attempt. Encourage them, correct gently, explain the words."
            ),
            "ru": (
                "🎮 <b>Готовы? Начинаем игру!</b>\n\n"
                "Даю вам 3 слова:\n\n"
                "✨ <b>привет</b> · <b>спасибо</b> · <b>пока</b>\n\n"
                "Составьте из них предложение — ошибки не страшны, бот поправит 😄",
                "The user just started learning Russian (beginner level). "
                "You gave them a challenge: make a sentence using привет, спасибо, пока. "
                "Their next message is their attempt. Encourage them, correct gently, explain the words."
            ),
        },
        "hsk1": {
            "tj": (
                "🎯 <b>A1 — Осон сар мекунем!</b>\n\n"
                "Ин 3 калимаро истифода баред:\n\n"
                "🔢 <b>один</b> · <b>два</b> · <b>три</b>\n\n"
                "Бо онҳо як ҷумлаи содда созед — масалан дар бораи синну сол ё шумора.",
                "The user is at Russian A1 level. You gave them a challenge: "
                "make a sentence using один, два, три. "
                "Their next message is their attempt. Correct and encourage."
            ),
            "uz": (
                "🎯 <b>A1 — Oson boshlaymiz!</b>\n\n"
                "Bu 3 so'zni ishlating:\n\n"
                "🔢 <b>один</b> · <b>два</b> · <b>три</b>\n\n"
                "Ular bilan oddiy gap tuzing — masalan yoshingiz yoki biror narsa soni.",
                "The user is at Russian A1 level. You gave them a challenge: "
                "make a sentence using один, два, три. "
                "Their next message is their attempt. Correct and encourage."
            ),
            "ru": (
                "🎯 <b>A1 — Начинаем просто!</b>\n\n"
                "Используйте эти 3 слова:\n\n"
                "🔢 <b>один</b> · <b>два</b> · <b>три</b>\n\n"
                "Составьте простое предложение — например про возраст или количество.",
                "The user is at Russian A1 level. You gave them a challenge: "
                "make a sentence using один, два, три. "
                "Their next message is their attempt. Correct and encourage."
            ),
        },
        "hsk2": {
            "tj": (
                "🕵️ <b>A2 — Ибораи муфид!</b>\n\n"
                "Ин калимаҳоро дар як ҷумла ҷамъ кунед:\n\n"
                "🇷🇺 <b>рад</b> · <b>познакомиться</b> · <b>с вами</b>\n\n"
                "Ибораи табиӣ ҳосил кунед.",
                "The user is at Russian A2 level. You gave them a challenge: "
                "combine рад, познакомиться, с вами into a natural Russian sentence. "
                "The expected phrase is Рад познакомиться с вами. Correct and explain warmly."
            ),
            "uz": (
                "🕵️ <b>A2 — Foydali ibora!</b>\n\n"
                "Bu so'zlardan bitta tabiiy gap tuzing:\n\n"
                "🇷🇺 <b>рад</b> · <b>познакомиться</b> · <b>с вами</b>\n\n"
                "Nima hosil bo'lishini ko'ramiz.",
                "The user is at Russian A2 level. You gave them a challenge: "
                "combine рад, познакомиться, с вами into a natural Russian sentence. "
                "The expected phrase is Рад познакомиться с вами. Correct and explain warmly."
            ),
            "ru": (
                "🕵️ <b>A2 — Полезная фраза!</b>\n\n"
                "Соберите естественное предложение из слов:\n\n"
                "🇷🇺 <b>рад</b> · <b>познакомиться</b> · <b>с вами</b>",
                "The user is at Russian A2 level. You gave them a challenge: "
                "combine рад, познакомиться, с вами into a natural Russian sentence. "
                "The expected phrase is Рад познакомиться с вами. Correct and explain warmly."
            ),
        },
        "hsk3": {
            "tj": (
                "🔥 <b>B1 — Санҷиши зуд!</b>\n\n"
                "Ба русӣ ҷавоб диҳед:\n\n"
                "🇷🇺 <b>Как у вас сегодня настроение?</b>\n\n"
                "Ҷавобро табиӣ нависед.",
                "The user is at Russian B1 level. You gave them a challenge: "
                "answer Как у вас сегодня настроение? in Russian. "
                "Their next message is their attempt. Evaluate their Russian, correct errors, praise effort."
            ),
            "uz": (
                "🔥 <b>B1 — Tezkor tekshiruv!</b>\n\n"
                "Ruscha javob bering:\n\n"
                "🇷🇺 <b>Как у вас сегодня настроение?</b>\n\n"
                "Javobni tabiiy yozing.",
                "The user is at Russian B1 level. You gave them a challenge: "
                "answer Как у вас сегодня настроение? in Russian. "
                "Their next message is their attempt. Evaluate their Russian, correct errors, praise effort."
            ),
            "ru": (
                "🔥 <b>B1 — Быстрая проверка!</b>\n\n"
                "Ответьте по-русски:\n\n"
                "🇷🇺 <b>Как у вас сегодня настроение?</b>\n\n"
                "Напишите естественный ответ.",
                "The user is at Russian B1 level. You gave them a challenge: "
                "answer Как у вас сегодня настроение? in Russian. "
                "Their next message is their attempt. Evaluate their Russian, correct errors, praise effort."
            ),
        },
        "hsk4": {
            "tj": (
                "⚡ <b>B2 — Устодро санҷем!</b>\n\n"
                "Ин сохтро дар як ҷумлаи мураккаб истифода баред:\n\n"
                "🇷🇺 <b>Хотя ..., но ...</b>\n\n"
                "Мавзуъ озод — аз зиндагии худ мисол биёред.",
                "The user is at Russian B2 level. You gave them a challenge: "
                "use the grammar pattern Хотя ..., но ... in a complex sentence about their life. "
                "Their next message is their attempt. Analyze grammar deeply, suggest improvements."
            ),
            "uz": (
                "⚡ <b>B2 — Ustani sinaylik!</b>\n\n"
                "Bu grammatik konstruksiyani murakkab gapda ishlating:\n\n"
                "🇷🇺 <b>Хотя ..., но ...</b>\n\n"
                "Mavzu istalgan — o'z hayotingizdan misol keltiring.",
                "The user is at Russian B2 level. You gave them a challenge: "
                "use the grammar pattern Хотя ..., но ... in a complex sentence about their life. "
                "Their next message is their attempt. Analyze grammar deeply, suggest improvements."
            ),
            "ru": (
                "⚡ <b>B2 — Проверим уровень!</b>\n\n"
                "Используйте эту конструкцию в сложном предложении:\n\n"
                "🇷🇺 <b>Хотя ..., но ...</b>\n\n"
                "Тема любая — возьмите пример из своей жизни.",
                "The user is at Russian B2 level. You gave them a challenge: "
                "use the grammar pattern Хотя ..., но ... in a complex sentence about their life. "
                "Their next message is their attempt. Analyze grammar deeply, suggest improvements."
            ),
        },
    }

    level_map = {
        "beginner": "beginner", "az0": "beginner",
        "hsk1": "hsk1", "hsk2": "hsk2", "hsk3": "hsk3", "hsk4": "hsk4",
    }
    mapped = level_map.get(level_key, "beginner")
    result = challenges.get(mapped, {}).get(lang_key)
    if result:
        return result
    return (
        "🇷🇺 <b>Начинаем русский.</b>\n\nНапишите простое предложение по-русски — я проверю и помогу улучшить.",
        f"The user is at Russian {level_label} level. Ask them to write a simple Russian sentence, then correct gently."
    )


@router.callback_query(OnboardingStates.choosing_level)
async def process_level(callback: CallbackQuery, state: FSMContext, session):
    level = callback.data.split(":")[1]

    service = OnboardingService(session)

    user, _ = await service.get_or_create_user(
        telegram_id=callback.from_user.id,
        full_name=callback.from_user.full_name if callback.from_user else None,
        username=callback.from_user.username if callback.from_user else None,
    )
    now = datetime.now(timezone.utc)
    user.level = level
    user.learning_mode = "qa"
    user.voice_mode = "none"
    user.status = "active"
    user.start_date = now
    user.end_date = now + timedelta(hours=24)
    user.expiry_reminder_sent_at = None
    await session.commit()

    await callback.answer()

    data = await state.get_data()
    onboarding_message_id = data.get("onboarding_message_id")

    user_num = str(user.id)

    try:
        if onboarding_message_id:
            await callback.bot.delete_message(
                chat_id=callback.message.chat.id,
                message_id=onboarding_message_id,
            )
    except Exception:
        pass

    await callback.message.answer(
        t("onboarding_special_welcome", user.language, user_num=user_num),
        parse_mode="HTML",
    )

    display_text, ai_context = _get_demo_lesson(level, user.language)

    if display_text:
        await callback.bot.send_message(
            chat_id=callback.from_user.id,
            text=display_text,
            reply_markup=main_menu_keyboard(user.language),
            parse_mode="HTML",
        )

    if ai_context:
        from app.repositories.message_repo import MessageRepository
        msg_repo = MessageRepository(session)
        await msg_repo.create(
            user_id=user.id,
            role="system",
            content=ai_context,
            content_type="onboarding_challenge",
        )
        await session.commit()

    await state.clear()
