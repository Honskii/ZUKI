import tomllib

from zuki.plugin import Plugin

from .updates.skip_messages import MessagesUpdateSkipper

class SkipUpdatesPlugin(Plugin):
    name = "skip_updates"
    title = "Skip Updates"
    requires = []

    async def on_load(self):
        self.config_manager.ensure_plugin_configs(self)
        self.config_path = self.config_manager.get_plugin_config_path(self.name)
        self.config = await self.skippers_settings_from_config()

        message_skipper = MessagesUpdateSkipper(skip_interval_seconds=self.config["message"])
        self.app.register_service(f"{self.name}:messages_update_skipper", message_skipper)

    async def load_config(self, conf_file_path: str):
        with open(self.config_path / conf_file_path, "rb") as file:
            return tomllib.load(file)

    async def skippers_settings_from_config(self):
        config = await self.load_config("config.toml")

        message_skip_interval_seconds = config.get("message", 30)

        return {
            "message": message_skip_interval_seconds
        }
