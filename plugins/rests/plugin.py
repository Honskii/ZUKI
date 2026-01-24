from zuki.plugin import Plugin

from .router import router
from .middlewares.middleware import RestMiddleware

class RestsPlugin(Plugin):
    name = "rests"
    title = "Rest Plugin"
    requires = ["db_manager", "telegram_info_collect"]

    async def on_load(self):
        uow_factory = self.app.get_service("db_manager:uow_factory")

        self.app.include_router(router)
        self.app.add_router_middleware(
            router,
            RestMiddleware(
                uow_factory=uow_factory,
                app_tzinfo=self.app.timezone
            ),
            update_types=["message", "callback_query"]
        )
