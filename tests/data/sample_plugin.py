from dataclasses import dataclass
from typing import Any

from tenvplate.protocols import ResourcesManagerProtocol

RESOURCE_ID = "sample-resource"


@dataclass
class SampleSourceSpec:
    secret_key: str
    resource_id: str = RESOURCE_ID


class SampleResource:
    resource_id: str = RESOURCE_ID
    mock_store: dict = {}

    @staticmethod
    def build_spec(*source_args: Any) -> SampleSourceSpec:
        return SampleSourceSpec(*source_args)

    def get_value(self, source_spec: SampleSourceSpec) -> str:
        return self.mock_store[source_spec.secret_key]


def register(resource_manager: ResourcesManagerProtocol) -> None:
    resource_manager.register_resource(resource_id=RESOURCE_ID, resource=SampleResource())
