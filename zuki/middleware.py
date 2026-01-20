from typing import Callable, Awaitable, Any

from aiogram import BaseMiddleware


class OuterMiddleware(BaseMiddleware):
    def __init__(self, app):
        self.app = app
    
    async def __call__(
        self,
        handler: Callable[[Any, dict], Awaitable[Any]],
        event: Any,
        data: dict,
    ) -> Any:
        data["app"] = self.app
        result = await handler(event, data)
        return result