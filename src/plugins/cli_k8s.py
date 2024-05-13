import base64
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from functools import partial
from typing import Any

from tenvplate.protocols import ResourcesManagerProtocol

DEFAULT_RUN_FUNC = partial(subprocess.check_output, text=True)


class SourceType(str, Enum):
    SECRETS = "secrets"
    CONFIGMAPS = "configmaps"


@dataclass
class KubernetesSourceSpec:
    namespace: str
    object_type: SourceType
    object_name: str
    field: str
    resource_id: str


class KubernetesResource:
    resource_id: str = "kubernetes"

    def __init__(self, run_func: Callable = DEFAULT_RUN_FUNC):
        self.run_func = run_func

    def build_spec(self, *source_args: Any) -> KubernetesSourceSpec:
        if len(source_args) != 4:
            raise ValueError(f"Invalid number of arguments: {source_args}")

        if source_args[1] not in SourceType.__members__.values():
            raise ValueError(f"Invalid object type: {source_args[1]}")

        return KubernetesSourceSpec(
            resource_id=self.resource_id,
            namespace=source_args[0],
            object_type=source_args[1],
            object_name=source_args[2],
            field=source_args[3],
        )

    def get_value(self, source_spec: KubernetesSourceSpec) -> str:
        cmd_prefix = f"kubectl get {source_spec.object_type} {source_spec.object_name} -n {source_spec.namespace}"
        json_path = f".data.{source_spec.field}"
        cmd = f"{cmd_prefix} -o jsonpath='{{{json_path}}}'".split(" ")
        value = self.run_func(cmd)

        if source_spec.object_type == SourceType.SECRETS:
            return base64.b64decode(value).decode("utf-8")

        return value.strip("'\n")


def register(resource_manager: ResourcesManagerProtocol) -> None:
    resource_manager.register_resource(resource_id=KubernetesResource.resource_id, resource=KubernetesResource())
