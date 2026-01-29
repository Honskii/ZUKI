from typing import Callable, Awaitable, Any

from aiogram import BaseMiddleware

class OuterMiddleware(BaseMiddleware):
    def __init__(self, uow_factory):
        self.uow_factory = uow_factory

    async def __call__(
        self,
        handler: Callable[[Any, dict], Awaitable[Any]],
        event: Any,
        data: dict,
    ) -> Any:
        data["db_manager:uow_factory"] = self.uow_factory
        result = await handler(event, data)
        return result