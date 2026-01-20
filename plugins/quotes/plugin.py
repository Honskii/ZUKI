import tomllib

from zuki.plugin import Plugin

from .router import router
from .service import QuoteService
from .middleware import QuoteMiddleware

class QuotesPlugin(Plugin):
    name = "quotes"
    requires = ["telegram_adapters"]
    default_config_dir = "default_configs"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_path = None
        self.config = {}

    async def on_load(self):
        print("Quotes collect plugin loading")
        self.config_manager.ensure_plugin_configs(self)
        self.config_path = self.config_manager.get_plugin_config_path(self.name)
        self.config = await self.load_config("config.toml")

        quote_service = QuoteService(
            **await self.quote_service_kwargs_from_config()
        )
        self.app.register_service(f"{self.name}:quote_service", QuoteService)

        self.app.add_router_middleware(router, QuoteMiddleware(quote_service), update_type="message")
        self.app.include_router(router)

    async def load_config(self, conf_file_path: str):
        with open(self.config_path / conf_file_path, "rb") as file:
            return tomllib.load(file)
    
    async def quote_service_kwargs_from_config(self):
        src_path = self.config_path / "src"

        backgrounds_config = self.config.get("backgrounds")
        if backgrounds_config is None:
            raise ValueError("Backgrounds dir configuration is missing in quotes plugin configuration")
        font_config = self.config.get("font")
        if font_config is None:
            raise ValueError("Font configuration is missing in quotes plugin configuration")

        allowed_backgrounds = backgrounds_config.get("allowed", ['*'])
        ignored_backgrounds = backgrounds_config.get("ignored", [])
        bg_limit = min(backgrounds_config.get("limit", 100), 1000)
        randomized_backgrounds = backgrounds_config.get("randomized", True)
        backgrounds = set()

        quote_font_family = font_config.get("quote_font_family")
        metadata_font_family = font_config.get("metadata_font_family")
        if not quote_font_family or not metadata_font_family:
            raise ValueError("Font family configuration is missing in quotes plugin configuration")

        quote_font_size = font_config.get("quote_font_size", 24)
        metadata_font_size = font_config.get("metadata_font_size", 18)

        for filter in allowed_backgrounds:
            backgrounds = backgrounds.union(set((src_path / "backgrounds").glob(filter)))
        
        for filter in ignored_backgrounds:
            backgrounds = {bg for bg in backgrounds if not bg.match(filter)}

        backgrounds = list(backgrounds)[:bg_limit]

        datetime_config = self.config.get("datetime")
        timezone_name = ""
        strftime = ""
        if datetime_config:
            timezone_name = datetime_config.get("timezone", "Etc/UTC")
            strftime = datetime_config.get("strftime", "%d.%m.%Y")

        return {
            "src_path": src_path,
            "backgrounds": backgrounds,
            "randomized": randomized_backgrounds,
            "quote_font_family": quote_font_family,
            "metadata_font_family": metadata_font_family,
            "quote_font_size": quote_font_size,
            "metadata_font_size": metadata_font_size,
            "timezone": timezone_name,
            "strftime": strftime
        }
