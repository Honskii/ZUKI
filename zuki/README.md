# Zuki Core

## Overview
**Zuki Core** is a minimal framework for modular bots and applications. Its purpose is to manage the application, load plugins, and provide them with a unified interface. The core itself contains no business logic and imposes no technology choices — all functionality lives in plugins.

---

## Features
- Plugin lifecycle management (`load`, `startup`, `shutdown`). Lifecycle methods are optional — if not defined, nothing happens.
- Configuration handling: the core provides paths to config files, regardless of format (TOML, JSON, YAML, etc.).
- Plugin dependencies and default configs: missing files can be copied from a plugin’s internal defaults to the external configs directory.
- Service registration: plugins can register and retrieve services through the application.
- Integration with **aiogram**: routers and middleware can be attached via the app.

---

## Components
- **`app.py`** — `App` object, controls startup and provides API for plugins.
- **`plugin.py`** — base `Plugin` class, all plugins inherit from it.
- **`config_manager.py`** — configuration manager, copies defaults and provides config paths.
- **`plugin_manager.py`** — handles plugin registration and lifecycle.
- **`middleware.py`** — auxiliary layer required for integration, but not relevant for plugin developers.

---

## Plugins
Each plugin must contain a `plugin.py` file with a class inheriting `Plugin`.

```py
from zuki.plugin import Plugin

class ExamplePlugin(Plugin):
    name = "example"
    requires = []
    default_config_dir = "config/example"
```

### Attributes
- `name` — plugin name.
- `requires` — list of dependencies (other plugin names).
- `default_config_dir` — path to default configs inside the plugin package.

Config manager usage:
```py
self.config_manager.ensure_plugin_configs(self)  # copy missing files
self.config_path = self.config_manager.get_plugin_config_path(self.name)  # get config path
```

---

## Application API
Within a plugin, `self.app` provides:

```py
self.app.register_service(name, service)   # register a service
self.app.get_service(name)                 # retrieve a service
self.app.include_router(router)            # attach an aiogram router
self.app.add_dispatcher_middleware(mw)     # add middleware to dispatcher
self.app.add_router_middleware(router, mw) # add middleware to router
```

Example:
```py
self.app.register_service(f"{self.name}:engine", self.engine)
```

---

## Minimal `main.py`
```py
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
        bot_storage=MemoryStorage()
    )

    pm = PluginManager(app=app, config_manager=config_manager)
    pm.register_all_from_package("plugins")

    await pm.load_all()
    await pm.startup_all()
    await app.run()

asyncio.run(main())
```

---

## License
This project is licensed under the Unlicense.
