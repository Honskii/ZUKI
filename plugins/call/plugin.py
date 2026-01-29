import tomllib
from pathlib import Path

from zuki.plugin import Plugin
from plugins.db_manager import UnitOfWork

from .middlewares.message import CallMiddleware
from .router import router

class CallPlugin(Plugin):
    name = "call"
    requires = ["db_manager", "skip_updates", "telegram_adapters", "telegram_info_collect"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config: str
        self.config_path: Path

    async def on_load(self):
        self.config_manager.ensure_plugin_configs(self)
        self.config_path = self.config_manager.get_plugin_config_path(self.name)
        self.config = await self.load_call_settings_from_config()

        self.app.include_router(router)
        self.app.add_router_middleware(
            router,
            CallMiddleware(
                message_skipper=self.app.get_service("skip_updates:messages_update_skipper"),
                **self.config
            ),
            update_types=["message"]
        )

    async def load_config(self, conf_file_path: str):
        with open(self.config_path / conf_file_path, "rb") as file:
            return tomllib.load(file)

    async def load_call_settings_from_config(self):
        config = await self.load_config("config.toml")
        result = {}

        result["users_tag_per_line"] = config.get("users_tag_per_line", 5)
        result["emojies"] = config.get("emojies")
        result["default_call_message"] = config.get("default_call_message", "Калл!")
        result["call_footer"] = config.get("call_footer", "")

        return result