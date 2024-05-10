from typing import Any, Protocol


class SourceSpec(Protocol):
    resource_id: str


class Resource(Protocol):
    resource_id: str

    def build_spec(self, *source_args: Any) -> SourceSpec: ...

    def get_value(self, source_spec: Any) -> str: ...


class ResourcesManagerProtocol(Protocol):
    resource_register: dict[str, Resource] = {}

    def register_resource(self, resource_id: str, resource: Resource) -> None: ...

    def get_resource(self, resource_id: str) -> Resource: ...


class PlugIn(Protocol):
    def register(self, resource_manager: ResourcesManagerProtocol) -> None: ...
