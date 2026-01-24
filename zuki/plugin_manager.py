from typing import Dict, Optional, List
import importlib
import pkgutil

from .plugin import Plugin
from .app import App
from .config_manager import ConfigManager


class PluginManager:
    def __init__(
        self,
        *,
        app: App,
        config_manager: Optional[ConfigManager] = None
    ):
        self.app: App = app
        self.config_manager = config_manager
        self.plugins: Dict[str, Plugin] = {}
        self.order: List[str] = []

    def register(self, plugin_cls: Plugin):
        if not issubclass(plugin_cls, Plugin):
            raise ValueError(f"Argument 'plugin_cls' must be Plugin type, not {type(plugin_cls)}")

        if not plugin_cls.name:
            raise ValueError("Plugin must have name")

        if self.plugins.get(plugin_cls.name) is not None:
            raise ValueError(f"Plugin with this name {plugin_cls.name} has already been registered")

        self.plugins[plugin_cls.name] = plugin_cls

    def register_all_from_package(self, package_name: str):
        package = importlib.import_module(package_name)

        for _, subpkg_name, is_pkg in pkgutil.iter_modules(package.__path__):
            if not is_pkg:
                continue

            plugin_module_name = f"{package.__name__}.{subpkg_name}.plugin"

            try:
                module = importlib.import_module(plugin_module_name)
            except ModuleNotFoundError as e:
                print(f"Failed to import {plugin_module_name}: {e}")
                continue

            for obj in module.__dict__.values():
                if (
                    isinstance(obj, type)
                    and issubclass(obj, Plugin)
                    and obj is not Plugin
                ):
                    self.register(obj)

    async def resolve_order(self):
        resolved = []
        unresolved = []

        async def resolve(name):
            if name in resolved:
                return
            if name in unresolved:
                raise RuntimeError(f"Circular dependency: {name}")

            unresolved.append(name)
            plugin = self.plugins[name]

            for dep in plugin.requires:
                if dep not in self.plugins:
                    raise RuntimeError(f"Missing dependency: {dep}")
                await resolve(dep)

            unresolved.remove(name)
            resolved.append(name)

        for name in self.plugins:
            await resolve(name)

        self.order = resolved

    async def load_all(self):
        print(f"Plugin found:", ', '.join(self.order))
        print("Loading plugins...")

        for name in self.order:
            plugin_cls = self.plugins[name]
            instance = plugin_cls(self.app, self.config_manager)
            self.app.plugins[name] = instance
            try:
                await instance.on_load()
                print(f"Plugin loaded: {instance} ({name})")
            except Exception as e:
                print(f"Failed to load plugin {instance} ({name}): {e}")
                raise e
        print("All plugins loaded")

    async def startup_all(self):
        print("Starting plugins...")

        for name in self.order:
            plugin = self.app.plugins[name]
            try:
                await plugin.on_startup()
                print(f"Plugin started: {plugin} ({name})")
            except Exception as e:
                print(f"Failed to start plugin {plugin} ({name}): {e}")
                raise e
        print("All plugins started")

    async def bootstrap(self, package_list: List[str]):
        for package_name in package_list:
            self.register_all_from_package(package_name)

        await self.resolve_order()
        await self.load_all()
        await self.startup_all()