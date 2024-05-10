import importlib.util
import sys
from pathlib import Path

from .protocols import PlugIn, Resource


def _import_from_fpath(fpath: Path) -> PlugIn:
    module_name = fpath.stem
    spec = importlib.util.spec_from_file_location(module_name, fpath)
    _module = importlib.util.module_from_spec(spec)  # type: ignore
    sys.modules[module_name] = _module
    spec.loader.exec_module(_module)  # type: ignore
    return _module  # type: ignore


class ResourcesManager:
    resource_register: dict[str, Resource]

    def __init__(self) -> None:
        self.resource_register = {}

    @classmethod
    def from_plugin_dir(cls, plugin_dir: Path) -> "ResourcesManager":
        self = cls()
        for plugin_file in plugin_dir.glob("*.py"):
            if plugin_file.stem == "__init__":
                continue

            plugin: PlugIn = _import_from_fpath(plugin_file)
            plugin.register(resource_manager=self)
        return self

    def register_resource(self, resource_id: str, resource: Resource) -> None:
        self.resource_register[resource_id] = resource

    def get_resource(self, resource_id: str) -> Resource:
        return self.resource_register[resource_id]
