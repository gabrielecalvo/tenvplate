from unittest.mock import Mock

import pytest
from plugins.cli_azure_keyvault import AzureKeyVaultResource, AzureKeyVaultSourceSpec


class TestAzureKeyVaultResource:
    sample_spec = AzureKeyVaultSourceSpec("sample-vault", "secrets", "sample-secret", "azure-keyvault")

    @pytest.mark.parametrize("args", [("a", "b"), ("a", "b", "c", "d")])
    def test_build_invalid_spec_raises(self, args):
        resource = AzureKeyVaultResource()
        with pytest.raises(ValueError, match="Invalid number of arguments:"):
            resource.build_spec(*args)

    def test_build_valid_spec(self):
        resource = AzureKeyVaultResource()
        actual = resource.build_spec("sample-vault", "secrets", "sample-secret")
        assert isinstance(actual, AzureKeyVaultSourceSpec)
        assert actual == self.sample_spec

    def test_object_type_must_be_secret(self):
        # only azure-keyvault secrets are supported at the moment
        resource = AzureKeyVaultResource()
        with pytest.raises(ValueError, match="Invalid object type:"):
            resource.build_spec("a", "not-secret", "c")

    def test_get_value(self):
        run_func = Mock(return_value="value\n")
        resource = AzureKeyVaultResource(run_func=run_func)
        actual = resource.get_value(self.sample_spec)
        assert actual == "value"
