from pathlib import Path
import shutil
import sys

from .plugin import Plugin

class ConfigManager:
    def __init__(self, *, project_root: Path, configs_dir: Path):
        self.project_root = project_root
        self.configs_root = project_root / configs_dir
        self.configs_root.mkdir(parents=True, exist_ok=True)

        self.configs_root.mkdir(exist_ok=True)

    def ensure_plugin_configs(self, plugin: Plugin):
        """
        Гарантирует, что у плагина есть конфиги
        """
        plugin_name = plugin.name
        target_dir = self.get_plugin_config_path(plugin_name)

        default_dir = self._get_plugin_default_config_dir(plugin)

        if not target_dir.exists():
            if default_dir:
                shutil.copytree(default_dir, target_dir)
            else:
                target_dir.mkdir()
            return

        if default_dir:
            self._merge_default_configs(default_dir, target_dir)

    def get_plugin_config_path(self, plugin_name: str) -> Path:
        return self.configs_root / plugin_name
    
    def _get_plugin_default_config_dir(self, plugin: Plugin) -> Path | None:
        if plugin.default_config_dir is None:
            return None

        module = sys.modules[plugin.__class__.__module__]
        plugin_root = Path(module.__file__).parent

        default_dir = plugin_root / plugin.default_config_dir

        if not default_dir.exists():
            raise RuntimeError(
                f"Default config dir not found for plugin {plugin.name}"
            )

        return default_dir
    
    def _merge_default_configs(self, default_dir: Path, target_dir: Path):
        for item in default_dir.iterdir():
            target_item = target_dir / item.name

            if item.is_dir():
                if not target_item.exists():
                    shutil.copytree(item, target_item)
                else:
                    self._merge_default_configs(item, target_item)

            else:
                if not target_item.exists():
                    shutil.copy2(item, target_item)

