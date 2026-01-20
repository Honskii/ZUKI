from typing import Dict, Optional
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
        config_manager=Optional[ConfigManager]
    ):
        self.app: App = app
        self.plugins: Dict[Plugin] = {}
        self.config_manager = config_manager

    def register(self, plugin_cls: Plugin):
        if not issubclass(plugin_cls, Plugin):
            raise ValueError(f"Argument 'plugin_cls' must be Plugin type, not {type(plugin_cls)}")
        
        if not plugin_cls.name:
            raise ValueError("Plugin must have name")
        
        if self.plugins.get(plugin_cls.name) is not None:
            raise ValueError("Plugin with this name has already been registered")

        self.plugins[plugin_cls.name] = plugin_cls
    

    def register_all_from_package(self, package_name: str):
        package = importlib.import_module(package_name)

        for _, subpkg_name, is_pkg in pkgutil.iter_modules(package.__path__):
            if not is_pkg:
                continue

            plugin_module_name = f"{package.__name__}.{subpkg_name}.plugin"

            try:
                module = importlib.import_module(plugin_module_name)
            except ModuleNotFoundError:
                continue

            for obj in module.__dict__.values():
                if (
                    isinstance(obj, type)
                    and issubclass(obj, Plugin)
                    and obj is not Plugin
                ):
                    self.register(obj)

    def resolve_order(self):
        resolved = []
        unresolved = []

        def resolve(name):
            if name in resolved:
                return
            if name in unresolved:
                raise RuntimeError(f"Circular dependency: {name}")

            unresolved.append(name)
            plugin = self.plugins[name]

            for dep in plugin.requires:
                if dep not in self.plugins:
                    raise RuntimeError(f"Missing dependency: {dep}")
                resolve(dep)

            unresolved.remove(name)
            resolved.append(name)

        for name in self.plugins:
            resolve(name)

        return resolved

    async def load_all(self):
        order = self.resolve_order()

        for name in order:
            plugin_cls = self.plugins[name]
            instance = plugin_cls(self.app, self.config_manager)
            # self.config_manager.ensure_plugin_configs(instance)
            self.app.plugins[name] = instance
            await instance.on_load()

    async def startup_all(self):
        for plugin in self.app.plugins.values():
            await plugin.on_startup()
