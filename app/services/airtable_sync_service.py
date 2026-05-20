import httpx

from app.config import settings


class AirtableSyncService:
    def __init__(self):
        self.api_key = settings.AIRTABLE_API_KEY
        self.base_id = settings.AIRTABLE_BASE_ID
        self.users_table = settings.AIRTABLE_USERS_TABLE
        self.payments_table = settings.AIRTABLE_PAYMENTS_TABLE
        self.referrals_table = settings.AIRTABLE_REFERRALS_TABLE
        self.chat_summary_table = settings.AIRTABLE_CHAT_SUMMARY_TABLE
        self.chat_archive_table = settings.AIRTABLE_CHAT_ARCHIVE_TABLE
        self.base_url = f"https://api.airtable.com/v0/{self.base_id}"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def _upsert_by_field(self, table_name: str, key_field: str, key_value: str, fields: dict):
        if not self.api_key or not self.base_id:
            return

        async with httpx.AsyncClient(timeout=8) as client:
            safe_value = str(key_value).replace("'", "\\'")
            formula = f"{{{key_field}}}='{safe_value}'"

            resp = await client.get(
                f"{self.base_url}/{table_name}",
                headers=self.headers,
                params={"filterByFormula": formula, "maxRecords": 1},
            )
            resp.raise_for_status()
            data = resp.json()
            records = data.get("records", [])

            if records:
                record_id = records[0]["id"]
                patch_resp = await client.patch(
                    f"{self.base_url}/{table_name}/{record_id}",
                    headers=self.headers,
                    json={"fields": fields},
                )
                patch_resp.raise_for_status()
            else:
                post_resp = await client.post(
                    f"{self.base_url}/{table_name}",
                    headers=self.headers,
                    json={"fields": fields},
                )
                post_resp.raise_for_status()

    async def _append(self, table_name: str, fields: dict):
        if not self.api_key or not self.base_id:
            return

        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.post(
                f"{self.base_url}/{table_name}",
                headers=self.headers,
                json={"fields": fields},
            )
            resp.raise_for_status()

    async def sync_user(self, user):
        await self._upsert_by_field(
            self.users_table,
            "telegram_id",
            str(user.telegram_id),
            {
                "telegram_id": str(user.telegram_id),
                "full_name": user.full_name or "",
                "language": user.language or "",
                "level": user.level or "",
                "learning_mode": user.learning_mode or "",
                "status": user.status or "",
                "payment_status": user.payment_status or "",
                "question_limit": user.question_limit or 0,
                "questions_used": user.questions_used or 0,
                "bonus_questions": user.bonus_questions or 0,
                "bonus_questions_used": user.bonus_questions_used or 0,
                "referral_code": user.referral_code or "",
                "referred_by_telegram_id": str(user.referred_by_telegram_id or ""),
                "discount_referral_count": user.discount_referral_count or 0,
                "discount_eligible": bool(user.discount_eligible),
                "discount_used": bool(user.discount_used),
                "selected_plan_type": user.selected_plan_type or "",
                "start_date": user.start_date.isoformat() if user.start_date else None,
                "end_date": user.end_date.isoformat() if user.end_date else None,
                "last_active_at": user.last_active_at.isoformat() if user.last_active_at else None,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            },
        )

    async def sync_payment(self, payment, full_name: str = ""):
        await self._upsert_by_field(
            self.payments_table,
            "payment_id",
            str(payment.id),
            {
                "payment_id": str(payment.id),
                "user_telegram_id": str(payment.user_telegram_id),
                "full_name": full_name,
                "plan_type": payment.plan_type or "",
                "amount": payment.amount or 0,
                "currency": payment.currency or "",
                "payment_status": payment.payment_status or "",
                "screenshot_file_id": payment.screenshot_file_id or "",
                "submitted_at": payment.submitted_at.isoformat() if payment.submitted_at else None,
                "reviewed_at": payment.reviewed_at.isoformat() if payment.reviewed_at else None,
                "admin_comment": payment.admin_comment or "",
            },
        )

    async def sync_referral(self, referral):
        await self._append(
            self.referrals_table,
            {
                "referrer_telegram_id": str(referral.referrer_telegram_id),
                "invited_user_telegram_id": str(referral.invited_user_telegram_id),
                "status": referral.status or "",
                "bonus_granted": bool(referral.bonus_granted),
                "counts_for_discount": bool(referral.counts_for_discount),
                "created_at": referral.created_at.isoformat() if referral.created_at else None,
                "activated_at": referral.activated_at.isoformat() if referral.activated_at else None,
            },
        )

    async def sync_chat_summary(
        self,
        user_telegram_id: int,
        full_name: str,
        last_user_message: str,
        last_bot_reply: str,
        last_content_type: str,
        last_image_context: str,
        message_count: int,
        updated_at,
    ):
        await self._upsert_by_field(
            self.chat_summary_table,
            "user_telegram_id",
            str(user_telegram_id),
            {
                "user_telegram_id": str(user_telegram_id),
                "full_name": full_name or "",
                "last_user_message": last_user_message or "",
                "last_bot_reply": last_bot_reply or "",
                "last_content_type": last_content_type or "",
                "last_image_context": last_image_context or "",
                "message_count": message_count or 0,
                "updated_at": updated_at.isoformat() if updated_at else None,
            },
        )

    async def append_chat_archive(
        self,
        message_id: int,
        user_telegram_id: int,
        role: str,
        content: str,
        content_type: str,
        telegram_message_id,
        created_at,
    ):
        await self._append(
            self.chat_archive_table,
            {
                "message_id": str(message_id),
                "user_telegram_id": str(user_telegram_id),
                "role": role or "",
                "content": content or "",
                "content_type": content_type or "",
                "telegram_message_id": str(telegram_message_id or ""),
                "created_at": created_at.isoformat() if created_at else None,
            },
        )
