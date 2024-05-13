import base64
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from typing import Any, Literal

from tenvplate.protocols import ResourcesManagerProtocol

DEFAULT_RUN_FUNC = partial(subprocess.check_output, text=True)


@dataclass
class KubernetesSourceSpec:
    namespace: str
    object_type: Literal["secrets", "configmaps"]
    object_name: str
    field: str
    resource_id: str

    def __post_init__(self) -> None:
        if self.object_type not in ("secrets", "configmaps"):
            raise ValueError(f"Invalid object type: {self.object_type}")


class KubernetesResource:
    resource_id: str = "kubernetes"

    def __init__(self, run_func: Callable = DEFAULT_RUN_FUNC):
        self.run_func = run_func

    def build_spec(self, *source_args: Any) -> KubernetesSourceSpec:
        if len(source_args) != 4:
            raise ValueError(f"Invalid number of arguments: {source_args}")

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

        if source_spec.object_type == "secrets":
            return base64.b64decode(value).decode("utf-8")

        return value.strip("'\n")


def register(resource_manager: ResourcesManagerProtocol) -> None:
    resource_manager.register_resource(resource_id=KubernetesResource.resource_id, resource=KubernetesResource())
