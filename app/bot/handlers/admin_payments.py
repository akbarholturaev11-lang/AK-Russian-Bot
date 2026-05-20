from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.repositories.payment_repo import PaymentRepository
from app.repositories.user_repo import UserRepository
from app.services.subscription_service import SubscriptionService
from app.services.payment_notify_service import PaymentNotifyService
from app.bot.keyboards.admin_review import admin_reject_reason_keyboard


router = Router()

REJECT_REASON_LABELS = {
    "wrong_amount": "Summa noto'g'ri",
    "unclear_screenshot": "Screenshot noaniq edi",
    "fake_suspected": "Shubhali ko'rindi",
    "old_payment": "Eski to'lov",
    "other": "Boshqa sabab",
}


@router.callback_query(F.data.startswith("admin_payment:approve:"))
async def admin_payment_approve_handler(callback: CallbackQuery, session):
    payment_repo = PaymentRepository(session)
    user_repo = UserRepository(session)
    subscription_service = SubscriptionService(session)
    payment_notify_service = PaymentNotifyService()

    payment_id = int(callback.data.split(":")[2])
    payment = await payment_repo.get_by_id(payment_id)
    if not payment:
        await callback.answer("To'lov topilmadi", show_alert=True)
        return

    if payment.payment_status != "pending":
        await callback.answer("Bu to'lov allaqachon ko'rib chiqilgan", show_alert=True)
        return

    await payment_repo.approve(payment, admin_comment="approved by admin")
    await subscription_service.activate_plan(
        telegram_id=payment.user_telegram_id,
        plan_type=payment.plan_type,
        discount_source=payment.discount_source,
        payment=payment,
    )

    user = await user_repo.get_by_telegram_id(payment.user_telegram_id)
    await session.commit()

    await callback.answer("✅ Tasdiqlandi!", show_alert=True)
    await callback.message.edit_reply_markup(reply_markup=None)

    chat_id = payment.user_telegram_id
    for msg_id in [payment.checkout_msg_id, payment.screenshot_msg_id, payment.waiting_msg_id]:
        if msg_id:
            try:
                await callback.bot.delete_message(chat_id=chat_id, message_id=msg_id)
            except Exception:
                pass

    await payment_notify_service.notify_payment_approved(
        bot=callback.bot,
        user=user,
    )


@router.callback_query(F.data.startswith("admin_payment:reject:"))
async def admin_payment_reject_handler(callback: CallbackQuery, session):
    payment_repo = PaymentRepository(session)
    user_repo = UserRepository(session)
    payment_notify_service = PaymentNotifyService()

    parts = callback.data.split(":")
    payment_id = int(parts[2])
    payment = await payment_repo.get_by_id(payment_id)
    if not payment:
        await callback.answer("To'lov topilmadi", show_alert=True)
        return

    if payment.payment_status != "pending":
        await callback.answer("Bu to'lov allaqachon ko'rib chiqilgan", show_alert=True)
        return

    await payment_repo.reject(payment, admin_comment="rejected by admin")
    user = await user_repo.get_by_telegram_id(payment.user_telegram_id)
    if user:
        await user_repo.set_selected_plan_type(user, payment.plan_type)
    await session.commit()

    await callback.answer("❌ Rad etildi", show_alert=True)
    await callback.message.edit_reply_markup(reply_markup=None)

    await payment_notify_service.notify_payment_rejected(
        bot=callback.bot,
        user=user,
        reason=None,
        plan_type=payment.plan_type,
    )


@router.callback_query(F.data.startswith("admin_payment:reject_reason:"))
async def admin_payment_reject_reason_select_handler(callback: CallbackQuery, session):
    payment_id = int(callback.data.split(":")[2])
    await callback.answer()
    await callback.message.answer(
        f"To'lov #{payment_id} uchun rad sababini tanlang:",
        reply_markup=admin_reject_reason_keyboard(payment_id),
    )


@router.callback_query(F.data.startswith("admin_payment:reject_with:"))
async def admin_payment_reject_with_reason_handler(callback: CallbackQuery, session):
    payment_repo = PaymentRepository(session)
    user_repo = UserRepository(session)
    payment_notify_service = PaymentNotifyService()

    parts = callback.data.split(":")
    payment_id = int(parts[2])
    reason_code = parts[3]

    payment = await payment_repo.get_by_id(payment_id)
    if not payment:
        await callback.answer("To'lov topilmadi", show_alert=True)
        return

    if payment.payment_status != "pending":
        await callback.answer("Bu to'lov allaqachon ko'rib chiqilgan", show_alert=True)
        return

    reason_label = REJECT_REASON_LABELS.get(reason_code, "Boshqa sabab")
    await payment_repo.reject(payment, admin_comment=reason_label)

    user = await user_repo.get_by_telegram_id(payment.user_telegram_id)
    if user:
        await user_repo.set_selected_plan_type(user, payment.plan_type)
    await session.commit()

    await callback.answer(f"❌ Rad etildi: {reason_label}", show_alert=True)
    await callback.message.edit_reply_markup(reply_markup=None)

    await payment_notify_service.notify_payment_rejected(
        bot=callback.bot,
        user=user,
        reason=reason_code,
        plan_type=payment.plan_type,
    )
