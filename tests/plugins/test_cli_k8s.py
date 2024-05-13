from unittest.mock import Mock

import pytest
from plugins.cli_k8s import KubernetesResource, KubernetesSourceSpec, SourceType


class TestAzureKeyVaultResource:
    sample_spec = KubernetesSourceSpec(
        "sample-namespace",
        "secrets",
        "sample-object_name",
        "sample-field",
        "kubernetes",
    )

    @pytest.mark.parametrize("args", [("a", "b", "c"), ("a", "b", "c", "d", "e")])
    def test_build_invalid_spec_raises(self, args):
        resource = KubernetesResource()
        with pytest.raises(ValueError, match="Invalid number of arguments:"):
            resource.build_spec(*args)

    @pytest.mark.parametrize("source_type", SourceType)
    def test_build_valid_spec(self, source_type):
        resource = KubernetesResource()
        actual = resource.build_spec("sample-namespace", source_type, "sample-object_name", "sample-field")
        assert isinstance(actual, KubernetesSourceSpec)
        assert actual.__dict__ == self.sample_spec.__dict__ | {"object_type": source_type}

    def test_object_type_must_be_valid(self):
        resource = KubernetesResource()
        with pytest.raises(ValueError, match="Invalid object type:"):
            resource.build_spec("a", "not-secret", "c", "d")

    @pytest.mark.parametrize("source_type", SourceType)
    def test_get_value(self, source_type):
        run_func = Mock(return_value="value\n" if source_type == SourceType.CONFIGMAPS else "dmFsdWU=")
        resource = KubernetesResource(run_func=run_func)
        source_spec = KubernetesSourceSpec(
            self.sample_spec.namespace,
            source_type,
            self.sample_spec.object_name,
            self.sample_spec.field,
            self.sample_spec.resource_id,
        )
        actual = resource.get_value(source_spec)
        assert actual == "value"
