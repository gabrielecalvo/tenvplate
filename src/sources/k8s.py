import base64
from dataclasses import dataclass
from typing import Any, Literal

RESOURCE_ID = "kubernetes"


@dataclass
class KubernetesSourceSpec:
    namespace: str
    object_type: Literal["secrets", "configmaps"]
    object_name: str
    field: str
    resource_id: str = RESOURCE_ID


class KubernetesResource:
    resource_id: str = RESOURCE_ID

    def __init__(self, client: Any | None = None) -> None:
        if client is None:
            import kubernetes as k8s

            k8s.config.load_kube_config()
            client = k8s.client.CoreV1Api()
        self.client = client

    @staticmethod
    def build_spec(*source_args: Any) -> KubernetesSourceSpec:
        if len(source_args) != 4:
            raise ValueError(f"Invalid number of arguments: {source_args}")
        return KubernetesSourceSpec(
            namespace=source_args[0],
            object_type=source_args[1],
            object_name=source_args[2],
            field=source_args[3],
        )

    def get_value(self, source_spec: KubernetesSourceSpec) -> str | None:
        if source_spec.object_type == "configmaps":
            configmap = self.client.read_namespaced_config_map(
                name=source_spec.object_name, namespace=source_spec.namespace
            )
            return configmap.data[source_spec.field]
        elif source_spec.object_type == "secrets":
            secret = self.client.read_namespaced_secret(name=source_spec.object_name, namespace=source_spec.namespace)
            return base64.b64decode(secret.data[source_spec.field]).decode("utf-8")
        raise ValueError(f"Invalid object type: {source_spec.object_type}")
