from typing import Optional, List

from aiogram import Bot, Dispatcher, Router, BaseMiddleware
from aiogram.fsm.storage.base import BaseStorage
from zoneinfo import ZoneInfo

from .middleware import OuterMiddleware


class App:
    def __init__(
        self,
        *,
        bot_token: str,
        bot_storage: Optional[BaseStorage],
        timezone: str = "Etc/UTC"
    ):
        self.bot = Bot(token=bot_token)
        if bot_storage is None:
            self.dp = Dispatcher(storage=BaseStorage())
        else:
            self.dp = Dispatcher()

        self._services = {}
        self.plugins = {}

        self.timezone = ZoneInfo(timezone)

        self.add_dispatcher_middleware(OuterMiddleware(self))

    def register_service(self, name, service):
        self._services[name] = service

    def get_service(self, name):
        return self._services[name]

    def include_router(self, router):
        self.dp.include_router(router)

    def add_dispatcher_middleware(self, middleware):
        self.dp.update.middleware(middleware)

    def add_router_middleware(self, router: Router, middleware: BaseMiddleware, update_types: List[str]):
        for update_type in update_types:
            getattr(router, update_type).middleware(middleware)

    async def run(self):
        await self.dp.start_polling(self.bot)