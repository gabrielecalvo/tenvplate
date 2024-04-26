from typing import Any, Protocol


class SourceSpec(Protocol):
    resource_id: str


class Resource(Protocol):
    resource_id: str

    def build_spec(self, *source_args: Any) -> SourceSpec: ...

    def get_value(self, source_spec: Any) -> str | None: ...
