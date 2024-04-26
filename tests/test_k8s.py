import base64
from unittest.mock import Mock

import pytest
from kubernetes.client import CoreV1Api

from src.sources.k8s import KubernetesResource, KubernetesSourceSpec


class TestKubernetesResource:
    def test_correct_resource_id(self):
        assert KubernetesResource.resource_id == "kubernetes"

    @pytest.mark.parametrize(
        "args",
        [("a", "b", "c"), ("a", "b", "c", "d", "e")],
    )
    def test_build_spec_raises_for_invalid_number_of_args(self, args):
        with pytest.raises(ValueError):
            KubernetesResource.build_spec(*args)

    @pytest.mark.parametrize("object_type", ["secrets", "configmaps"])
    def test_build_spec(self, object_type):
        actual = KubernetesResource.build_spec(
            "sample-namespace", object_type, "sample-secret_name", "sample-secret_field"
        )
        assert actual == KubernetesSourceSpec(
            namespace="sample-namespace",
            object_type=object_type,
            object_name="sample-secret_name",
            field="sample-secret_field",
        )

    @pytest.mark.parametrize("object_type", ["secrets", "configmaps"])
    def test_get_value(self, object_type):
        mock_client = Mock(spec=CoreV1Api)
        secret_val = "a"
        secret_b64_val = base64.b64encode(secret_val.encode("utf-8")).decode("utf-8")
        mock_client.read_namespaced_secret.return_value = Mock(data={"sample-field": secret_b64_val})
        mock_client.read_namespaced_config_map.return_value = Mock(data={"sample-field": secret_val})
        spec = KubernetesSourceSpec(
            namespace="sample-namespace",
            object_type=object_type,
            object_name="sample-name",
            field="sample-field",
        )
        actual = KubernetesResource(client=mock_client).get_value(spec)
        assert actual == secret_val
