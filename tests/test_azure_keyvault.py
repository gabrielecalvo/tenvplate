from unittest.mock import Mock, patch

import pytest

from src.sources.azure_keyvault import AzureKeyVaultResource, AzureKeyVaultSourceSpec


class TestAzureKeyVaultResource:
    def test_correct_resource_id(self):
        assert AzureKeyVaultResource.resource_id == "azure-keyvault"

    @pytest.mark.parametrize(
        "args",
        [("a", "b"), ("a", "b", "c", "d")],
    )
    def test_build_spec_raises_for_invalid_number_of_args(self, args):
        with pytest.raises(ValueError):
            AzureKeyVaultResource.build_spec(*args)

    def test_build_spec(self):
        actual = AzureKeyVaultResource.build_spec("sample-vault-1", "secrets", "sample-secret-1")
        assert actual == AzureKeyVaultSourceSpec(
            keyvault_name="sample-vault-1", object_type="secrets", secret_name="sample-secret-1"
        )

    def test_get_value(self):
        with patch("azure.keyvault.secrets.SecretClient") as mock_secret_client:
            mock_secret_client.return_value.get_secret.return_value = Mock(value="sample-secret-value")
            spec = AzureKeyVaultSourceSpec(
                keyvault_name="sample-vault-1", object_type="secrets", secret_name="sample-secret-1"
            )
            actual = AzureKeyVaultResource().get_value(spec)
        assert actual == "sample-secret-value"
