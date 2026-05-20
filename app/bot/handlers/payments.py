from aiogram import Router, F
from aiogram.dispatcher.event.bases import SkipHandler
from aiogram.types import Message
from datetime import datetime, timezone, timedelta
from app.repositories.user_repo import UserRepository
from app.repositories.payment_repo import PaymentRepository
from app.services.payment_service import PaymentService
from app.services.admin_notify_service import AdminNotifyService
from app.services.payment_screenshot_ai_service import PaymentScreenshotAIService
from app.bot.utils.i18n import t

router = Router()


_TJT = timezone(timedelta(hours=5))  # Tajikistan Time = UTC+5, server-independent

def _is_night() -> bool:
    tj_hour = datetime.now(_TJT).hour
    return tj_hour >= 23 or tj_hour < 8


def _waiting_message(lang: str, is_night: bool) -> str:
    if is_night:
        return {
            "uz": "📸 Skrinshot qabul qilindi.\n\nAdmin ish vaqti: 08:00–23:00. To'lovingiz ertalab tasdiqlanadi.",
            "tj": "📸 Скриншот қабул шуд.\n\nВақти корӣ: 08:00–23:00. Пардохт субҳ тасдиқ карда мешавад.",
            "ru": "📸 Скриншот получен.\n\nЧасы работы: 08:00–23:00. Платёж будет проверен утром.",
        }.get(lang, "📸 Screenshot received.")
    return {
        "uz": "📸 Skrinshot qabul qilindi.\n\nO'rtacha tekshiruv vaqti: 5–15 daqiqa.",
        "tj": "📸 Скриншот қабул шуд.\n\nВақти тафтиш: 5–15 дақиқа.",
        "ru": "📸 Скриншот получен.\n\nСреднее время проверки: 5–15 минут.",
    }.get(lang, "📸 Screenshot received.")


@router.message(F.photo)
async def payment_screenshot_handler(message: Message, session):
    user_repo = UserRepository(session)
    payment_service = PaymentService(session)
    admin_notify_service = AdminNotifyService()

    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user:
        raise SkipHandler()

    if not user.selected_plan_type:
        raise SkipHandler()

    lang = user.language if user.language else "ru"
    photo = message.photo[-1]
    screenshot_file_id = photo.file_id

    plan_type = user.selected_plan_type
    if not plan_type:
        latest_pending = await payment_service.get_latest_pending_payment(message.from_user.id)
        if latest_pending:
            plan_type = latest_pending.plan_type

    if not plan_type:
        await message.answer(t("payment_plan_not_selected", lang))
        return

    payment, status_or_error = await payment_service.attach_or_create_payment_screenshot(
        telegram_id=message.from_user.id,
        plan_type=plan_type,
        screenshot_file_id=screenshot_file_id,
    )

    if not payment:
        await message.answer(t(status_or_error, lang))
        return

    checkout_msg_id = user.pending_checkout_msg_id
    await user_repo.set_selected_plan_type(user, None)
    await user_repo.set_pending_checkout_msg_id(user, None)
    await session.commit()

    waiting_msg = await message.answer(_waiting_message(lang, _is_night()))

    payment.checkout_msg_id = checkout_msg_id
    payment.screenshot_msg_id = message.message_id
    payment.waiting_msg_id = waiting_msg.message_id
    await session.commit()

    payment_repo = PaymentRepository(session)
    pending_count = await payment_repo.count_pending()

    ai_result = None
    try:
        ai_svc = PaymentScreenshotAIService()
        file = await message.bot.get_file(photo.file_id)
        file_bytes = await message.bot.download_file(file.file_path)
        file_bytes.seek(0)
        image_bytes = file_bytes.read()
        ai_result = await ai_svc.verify_screenshot(
            image_bytes=image_bytes,
            mime_type="image/jpeg",
            expected_amount=payment.amount,
            currency=payment.currency,
        )
    except Exception:
        ai_result = None

    await admin_notify_service.notify_payment_review(
        bot=message.bot,
        payment=payment,
        user=user,
        ai_result=ai_result,
        pending_count=pending_count,
    )
