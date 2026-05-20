from datetime import datetime, timezone
from html import escape

from aiogram import Bot

from app.config import settings
from app.bot.keyboards.admin_review import admin_payment_review_keyboard
from app.bot.keyboards.feedback import admin_bot_feedback_keyboard
from app.bot.utils.i18n import t


class AdminNotifyService:
    def __init__(self):
        self.admin_ids = self._parse_admin_ids(settings.ADMIN_IDS)

    def _parse_admin_ids(self, raw_value: str):
        if not raw_value:
            return []
        result = []
        for item in raw_value.split(","):
            item = item.strip()
            if item:
                try:
                    result.append(int(item))
                except ValueError:
                    continue
        return result

    def build_payment_review_text(
        self,
        lang: str,
        telegram_id: int,
        full_name: str,
        plan_type: str,
        amount: int,
        currency: str,
        payment_id: int,
        payment_method: str = None,
        base_amount: int = None,
        discount_source: str = "none",
        discount_percent: int = 0,
        discount_title: str = None,
        discount_details: str = None,
        ai_result: dict = None,
        pending_count: int = 0,
    ) -> str:
        plan_label = "10 kunlik" if plan_type == "10_days" else "1 oylik"
        method_labels = {
            "visa": "Visa",
            "alipay": "Alipay",
            "wechat": "WeChat",
        }

        lines = [
            f"💳 Yangi to'lov so'rovi",
            f"",
            f"👤 {full_name} ({telegram_id})",
            f"📦 Tarif: {plan_label} — {amount} {currency}",
            f"🏦 To'lov turi: {method_labels.get(payment_method, payment_method or '-')}",
            f"🆔 To'lov ID: #{payment_id}",
        ]

        if discount_percent > 0:
            source_label = {
                "referral": "Referral chegirma",
                "admin_campaign": "Admin kampaniya",
                "feedback_price_offer": "Feedback maxsus chegirma",
            }.get(discount_source, "Chegirma")
            title = f" — {discount_title}" if discount_title else ""
            lines.append("")
            lines.append(f"🎁 Chegirma: {discount_percent}% ({source_label}{title})")
            if base_amount:
                lines.append(f"  Narx: {base_amount} → {amount} {currency}")
            if discount_details:
                lines.append(f"  Qanday olindi: {discount_details}")
        else:
            lines.append("🎁 Chegirma: yo'q")

        if pending_count > 1:
            lines.append(f"⏳ Navbatda: {pending_count} ta to'lov")

        if ai_result:
            verdict = ai_result.get("verdict", "unknown")
            ai_amount = ai_result.get("amount")
            ai_currency = ai_result.get("currency", "")
            date_str = ai_result.get("date", "unknown")
            pay_sys = ai_result.get("payment_system", "unknown")
            amount_match = ai_result.get("amount_match", False)
            reason = ai_result.get("reason", "")

            if verdict == "trusted":
                verdict_icon = "✅"
            elif verdict == "suspicious":
                verdict_icon = "⚠️"
            else:
                verdict_icon = "❌"

            lines.append(f"")
            lines.append(f"🤖 AI tekshiruvi: {verdict_icon} {verdict.upper()}")

            if ai_amount is not None:
                match_icon = "✅" if amount_match else "❌"
                lines.append(f"  Summa: {ai_amount} {ai_currency} {match_icon}")
            else:
                lines.append(f"  Summa: aniqlanmadi ❌")

            lines.append(f"  Sana: {date_str}")
            lines.append(f"  To'lov tizimi: {pay_sys}")

            if reason and verdict != "trusted":
                lines.append(f"  Sabab: {reason}")

        return "\n".join(lines)

    async def notify_payment_review(
        self,
        bot: Bot,
        payment,
        user,
        ai_result: dict = None,
        pending_count: int = 1,
    ) -> None:
        if not self.admin_ids:
            return

        text = self.build_payment_review_text(
            lang="uz",
            telegram_id=user.telegram_id,
            full_name=user.full_name or "-",
            plan_type=payment.plan_type,
            amount=payment.amount,
            currency=payment.currency,
            payment_id=payment.id,
            payment_method=payment.payment_method or getattr(user, "payment_method", None),
            base_amount=payment.base_amount,
            discount_source=payment.discount_source,
            discount_percent=payment.discount_percent,
            discount_title=payment.discount_title,
            discount_details=payment.discount_details,
            ai_result=ai_result,
            pending_count=pending_count,
        )

        keyboard = admin_payment_review_keyboard(payment.id, "uz")

        for admin_id in self.admin_ids:
            try:
                if payment.screenshot_file_id:
                    if len(text) <= 1000:
                        await bot.send_photo(
                            chat_id=admin_id,
                            photo=payment.screenshot_file_id,
                            caption=text,
                            reply_markup=keyboard,
                        )
                    else:
                        await bot.send_photo(
                            chat_id=admin_id,
                            photo=payment.screenshot_file_id,
                        )
                        await bot.send_message(
                            chat_id=admin_id,
                            text=text,
                            reply_markup=keyboard,
                        )
                else:
                    await bot.send_message(
                        chat_id=admin_id,
                        text=text,
                        reply_markup=keyboard,
                    )
            except Exception:
                pass

    def _feedback_user_age(self, user) -> str:
        created_at = getattr(user, "created_at", None)
        if not created_at:
            return "-"
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        days = max(0, (datetime.now(timezone.utc) - created_at).days)
        if days == 0:
            return "1 kundan kam"
        return f"{days} kun"

    def _feedback_level_label(self, user) -> str:
        level = str(getattr(user, "level", None) or "-")
        return {
            "beginner": "0 dan",
            "hsk1": "A1",
            "hsk2": "A2",
            "hsk3": "B1",
            "hsk4": "B2",
        }.get(level, level)

    def _feedback_mode_label(self, user) -> str:
        mode = str(getattr(user, "learning_mode", None) or "-")
        return {
            "qa": "Savol-javob",
            "course": "Kurs",
        }.get(mode, mode)

    def build_bot_feedback_text(self, feedback, user) -> str:
        liked = escape(str(getattr(feedback, "liked_text", None) or "-"))
        disliked = escape(str(getattr(feedback, "disliked_text", None) or "-"))
        full_name = escape(str(getattr(user, "full_name", None) or "-"))
        language = escape(str(getattr(user, "language", None) or "-"))
        level = escape(self._feedback_level_label(user))
        mode = escape(self._feedback_mode_label(user))
        reward = "berildi" if getattr(feedback, "reward_granted_at", None) else "berilmadi"

        return "\n".join(
            [
                "📝 <b>Yangi bot otzivi</b>",
                "",
                f"🧾 Otziv ID: <b>#{feedback.id}</b>",
                f"👤 User: <b>{full_name}</b>",
                f"🆔 Telegram ID: <code>{user.telegram_id}</code>",
                f"🌐 Til: <b>{language}</b>",
                f"📚 Urven: <b>{level}</b>",
                f"🎛 Rejim: <b>{mode}</b>",
                f"⏱ Botda: <b>{self._feedback_user_age(user)}</b>",
                "",
                f"👍 <b>Yoqdi:</b>\n{liked}",
                "",
                f"👎 <b>Yoqmadi:</b>\n{disliked}",
                "",
                f"🎁 1 kunlik bonus: <b>{reward}</b>",
            ]
        )

    async def notify_bot_feedback(
        self,
        bot: Bot,
        feedback,
        user,
    ) -> None:
        if not self.admin_ids:
            return

        text = self.build_bot_feedback_text(feedback, user)
        keyboard = admin_bot_feedback_keyboard(feedback.id)
        attachment_file_id = getattr(feedback, "disliked_attachment_file_id", None)
        attachment_type = getattr(feedback, "disliked_attachment_type", None)

        for admin_id in self.admin_ids:
            try:
                if attachment_file_id and attachment_type == "photo" and len(text) <= 1000:
                    await bot.send_photo(
                        chat_id=admin_id,
                        photo=attachment_file_id,
                        caption=text,
                        reply_markup=keyboard,
                        parse_mode="HTML",
                    )
                    continue

                if attachment_file_id and attachment_type == "document" and len(text) <= 1000:
                    await bot.send_document(
                        chat_id=admin_id,
                        document=attachment_file_id,
                        caption=text,
                        reply_markup=keyboard,
                        parse_mode="HTML",
                    )
                    continue

                if attachment_file_id:
                    if attachment_type == "photo":
                        await bot.send_photo(chat_id=admin_id, photo=attachment_file_id)
                    elif attachment_type == "document":
                        await bot.send_document(chat_id=admin_id, document=attachment_file_id)

                await bot.send_message(
                    chat_id=admin_id,
                    text=text,
                    reply_markup=keyboard,
                    parse_mode="HTML",
                )
            except Exception:
                pass
