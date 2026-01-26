from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import Message
from plugins.skip_updates import MessagesUpdateSkipper

from .service import QuoteService

class QuoteMiddleware(BaseMiddleware):
    def __init__(self, quote_service: QuoteService, message_skipper: MessagesUpdateSkipper):
        self.quote_service = quote_service
        self.message_skipper = message_skipper

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        message: Message,
        data: Dict[str, Any]
    ) -> Any:
        data["quote_service"] = self.quote_service

        if self.message_skipper.should_skip(message):
            return

        # Обработка сообщения
        result = await handler(message, data)

        return result