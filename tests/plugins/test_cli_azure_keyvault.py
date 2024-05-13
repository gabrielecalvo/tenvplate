from unittest.mock import Mock

import pytest
from plugins.cli_azure_keyvault import AzureKeyVaultResource, AzureKeyVaultSourceSpec, register


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
        run_func.assert_called_once_with(
            "az keyvault secret show -n sample-secret --vault-name sample-vault --query value"
        )


def test_register():
    mock_resource_manager = Mock()
    register_func = mock_resource_manager.register_resource

    register(mock_resource_manager)
    register_func.assert_called_once()
    assert register_func.call_args.kwargs["resource_id"] == AzureKeyVaultResource.resource_id
    assert isinstance(register_func.call_args.kwargs["resource"], AzureKeyVaultResource)
