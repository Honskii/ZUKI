from typing import Callable, Awaitable, Any

from aiogram import BaseMiddleware

class OuterMiddleware(BaseMiddleware):
    def __init__(self, sessionmaker):
        self.sessionmaker = sessionmaker
    
    async def __call__(
        self,
        handler: Callable[[Any, dict], Awaitable[Any]],
        event: Any,
        data: dict,
    ) -> Any:
        data["db_manager:sessionmaker"] = self.sessionmaker
        result = await handler(event, data)
        return result