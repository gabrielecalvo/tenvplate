import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from typing import Any, Literal

from tenvplate.protocols import ResourcesManagerProtocol

DEFAULT_RUN_FUNC = partial(subprocess.check_output, shell=True, text=True)


@dataclass
class AzureKeyVaultSourceSpec:
    keyvault_name: str
    object_type: Literal["secrets"]
    secret_name: str
    resource_id: str

    def __post_init__(self) -> None:
        if self.object_type not in ("secrets",):
            raise ValueError(f"Invalid object type: {self.object_type}")


class AzureKeyVaultResource:
    resource_id: str = "azure-keyvault"

    def __init__(self, run_func: Callable = DEFAULT_RUN_FUNC):
        self.run_func = run_func

    def build_spec(self, *source_args: Any) -> AzureKeyVaultSourceSpec:
        if len(source_args) != 3:
            raise ValueError(f"Invalid number of arguments: {source_args}")

        return AzureKeyVaultSourceSpec(
            resource_id=self.resource_id,
            keyvault_name=source_args[0],
            object_type=source_args[1],
            secret_name=source_args[2],
        )

    def get_value(self, source_spec: AzureKeyVaultSourceSpec) -> str:
        cmd = (
            f"az keyvault secret show -n {source_spec.secret_name}"
            f" --vault-name {source_spec.keyvault_name} --query value"
        )
        return self.run_func(cmd).strip('"\n')


def register(resource_manager: ResourcesManagerProtocol) -> None:
    resource_manager.register_resource(resource_id=AzureKeyVaultResource.resource_id, resource=AzureKeyVaultResource())
