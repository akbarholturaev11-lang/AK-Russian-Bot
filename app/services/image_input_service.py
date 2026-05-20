from typing import Optional

from aiogram.types import Message


class ImageInputService:
    def is_photo_message(self, message: Message) -> bool:
        return bool(message.photo)

    def is_supported_image_message(self, message: Message) -> bool:
        return self.is_photo_message(message)

    def get_image_file_id(self, message: Message) -> Optional[str]:
        if self.is_photo_message(message):
            return message.photo[-1].file_id
        return None

    def get_image_mime_type(self, message: Message) -> str:
        return "image/jpeg"

    def get_image_content_type(self, message: Message) -> Optional[str]:
        if self.is_photo_message(message):
            return "image"
        return None

    def get_invalid_file_reason_key(self, message: Message) -> str:
        return "image_invalid_format"
