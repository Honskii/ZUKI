from zuki.plugin import Plugin

from .middlewares.outer import OuterMiddleware
from . import seeds

class UserInfo(Plugin):
    name = "telegram_info_collect"
    requires = ["db_manager", "telegram_adapters"]

    async def on_load(self):
        print("User info collect plugin loading")

        self.app.add_dispatcher_middleware(OuterMiddleware())
