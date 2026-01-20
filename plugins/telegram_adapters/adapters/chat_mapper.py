from aiogram.types import Chat

class TelegramChatMapper:
    @staticmethod
    def to_internal_type(chat: Chat) -> str:
        if chat.is_forum:
            return "forum"
        if chat.type in ("private", "group", "supergroup", "channel"):
            return chat.type
        return "other"
