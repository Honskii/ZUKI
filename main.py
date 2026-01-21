import asyncio
from pathlib import Path

from aiogram.fsm.storage.memory import MemoryStorage

from zuki.app import App
from zuki.plugin_manager import PluginManager
from zuki.config_manager import ConfigManager
from settings import settings

async def main():
    config_manager = ConfigManager(
        project_root=Path("."),
        configs_dir="configs"
    )

    app = App(
        bot_token=settings.bot_token,
        bot_storage=MemoryStorage(),
        timezone=settings.timezone,
    )

    pm = PluginManager(
        app=app,
        config_manager=config_manager
    )
    
    pm.register_all_from_package("plugins")

    await pm.resolve_order()
    await pm.load_all()
    await pm.startup_all()

    try:
        print("Start bot polling")
        await app.run()
    except KeyboardInterrupt:
        print("Bot was stopped")

asyncio.run(main())
