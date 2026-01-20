from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import Message, ChatMemberRestricted

from .service import QuoteService

class QuoteMiddleware(BaseMiddleware):
    def __init__(self, quote_service: QuoteService):
        self.quote_service = quote_service

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        message: Message,
        data: Dict[str, Any]
    ) -> Any:
        data["quote_service"] = self.quote_service

        # Обработка сообщения
        result = await handler(message, data)

        return result