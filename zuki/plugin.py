from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .app import App
    from .config_manager import ConfigManager


class Plugin:
    name: str = ""
    requires = []
    default_config_dir = f"default_configs"
    title = name

    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)
        if not cls.name:
            cls.name = cls.__name__.lower()

    def __init__(self, app: "App", config_manager: "ConfigManager"):
        self.app = app
        self.config_manager = config_manager

    async def on_load(self):
        pass

    async def on_startup(self):
        pass

    async def on_shutdown(self):
        pass

    def __str__(self):
        return self.title or self.name
