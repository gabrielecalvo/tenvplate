from dataclasses import dataclass
from typing import Any, Literal

RESOURCE_ID = "azure-keyvault"


@dataclass
class AzureKeyVaultSourceSpec:
    keyvault_name: str
    object_type: Literal["secrets"]
    secret_name: str
    resource_id: str = RESOURCE_ID


class AzureKeyVaultResource:
    resource_id: str = RESOURCE_ID

    def __init__(self, credential: Any | None = None) -> None:
        from azure.identity import DefaultAzureCredential

        self.credential = credential or DefaultAzureCredential()

    @staticmethod
    def build_spec(*source_args: Any) -> AzureKeyVaultSourceSpec:
        if len(source_args) != 3:
            raise ValueError(f"Invalid number of arguments: {source_args}")
        return AzureKeyVaultSourceSpec(
            keyvault_name=source_args[0], object_type=source_args[1], secret_name=source_args[2]
        )

    def get_value(self, source_spec: AzureKeyVaultSourceSpec) -> str | None:
        from azure.keyvault.secrets import SecretClient

        client = SecretClient(
            vault_url=f"https://{source_spec.keyvault_name}.vault.azure.net", credential=self.credential
        )
        return client.get_secret(source_spec.secret_name).value
