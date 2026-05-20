from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.config import settings
from app.repositories.user_repo import UserRepository


router = Router()


@router.callback_query(F.data == "referral:invite")
async def referral_invite_handler(callback: CallbackQuery, session):
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)

    if not user:
        await callback.answer()
        return

    await user_repo.ensure_referral_code(user)
    await session.commit()

    referral_link = f"https://t.me/{settings.BOT_USERNAME}?start={user.referral_code}"

    lang = user.language if user.language else "ru"

    if lang == "tj":
        text = (
            "Ин силкаи даъвати шумост:\n"
            f"{referral_link}\n\n"
            "Агар дӯсти шумо бо ин силка ворид шуда, ба бот 2 хабар фиристад, "
            "шумо +5 саволи бонусӣ мегиред."
        )
    elif lang == "ru":
        text = (
            "Это ваша силка для приглашения:\n"
            f"{referral_link}\n\n"
            "Если ваш друг войдёт по этой силке и отправит боту 2 сообщения, "
            "вы получите +5 бонусных вопросов."
        )
    else:
        text = (
            "Bu sizning taklif silka-ngiz:\n"
            f"{referral_link}\n\n"
            "Agar do‘stingiz shu silka orqali kirib, botga 2 ta xabar yuborsa, "
            "siz +5 bonus savol olasiz."
        )

    await callback.answer()
    await callback.message.answer(text, disable_web_page_preview=True)
