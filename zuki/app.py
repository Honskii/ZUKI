from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.base import BaseStorage

from .middleware import OuterMiddleware


class App:
    def __init__(
        self,
        *,
        bot_token: str,
        bot_storage: Optional[BaseStorage],
    ):
        self.bot = Bot(token=bot_token)
        if bot_storage is None:
            self.dp = Dispatcher(storage=bot_storage)
        else:
            self.dp = Dispatcher()

        self._services = {}
        self.plugins = {}

        self.add_dispatcher_middleware(OuterMiddleware(self))

    def register_service(self, name, service):
        self._services[name] = service

    def get_service(self, name):
        return self._services[name]

    def include_router(self, router):
        self.dp.include_router(router)

    def add_dispatcher_middleware(self, middleware):
        self.dp.update.middleware(middleware)

    def add_router_middleware(self, router, middleware, *, update_type=None):
        if update_type is None:
            router.middleware(middleware)
        else:
            getattr(router, update_type).middleware(middleware)

    async def run(self):
        await self.dp.start_polling(self.bot)