from typing import Callable, Awaitable, Dict, Any, Union
from datetime import tzinfo, datetime

from plugins.db_manager.uow import UnitOfWork

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery


class RestMiddleware(BaseMiddleware):
    def __init__(self, uow_factory: UnitOfWork, app_tzinfo: tzinfo):
        self.uow_factory = uow_factory
        self.app_tzinfo = app_tzinfo

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        message: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:
        data["app_tzinfo"] = self.app_tzinfo
        data["uow_factory"] = self.uow_factory

        if isinstance(message, Message):
            if (datetime.now(tz=message.date.tzinfo) - message.date).seconds > 30:
                return
        # Обработка сообщения
        result = await handler(message, data)

        return result