from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .app import App
    from .config_manager import ConfigManager


class Plugin:
    name = None
    requires = []
    default_config_dir = f"config/{name}"

    def __init__(self, app: "App", config_manager: "ConfigManager"):
        self.app = app
        self.config_manager = config_manager


    async def on_load(self):
        pass

    async def on_startup(self):
        pass

    async def on_shutdown(self):
        pass
