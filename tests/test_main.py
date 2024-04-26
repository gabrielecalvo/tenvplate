import dataclasses
import textwrap
from unittest.mock import Mock

import pytest

from src.main import _extract_values_to_request, _load_template, build_default_resources_manager, process
from src.resources import ResourcesManager
from src.sources.azure_keyvault import AzureKeyVaultResource
from src.sources.k8s import KubernetesResource
from src.sources.protocols import Resource


@dataclasses.dataclass
class MockSourceSpec:
    resource_id: str
    field_id: str


class TestAzureKeyvault:
    TEMPLATE_CONTENT = textwrap.dedent(
        "# some comment\nKEY11={{r1/v1}}\nKEY12= {{ r1/v2 }}\nKEY21={{ r2/v1 }} \nFIXED=FIXED"
    )

    EXPECTED_MAPPING = {
        "KEY11": "{{r1/v1}}",
        "KEY12": "{{ r1/v2 }}",
        "KEY21": "{{ r2/v1 }}",
        "FIXED": "FIXED",
    }

    EXPECTED_ENV_FILE_CONTENT = textwrap.dedent("""\
    KEY11=r11_value
    KEY12=r12_value
    KEY21=r21_value
    FIXED=FIXED
    """)

    expected_spec11 = MockSourceSpec(resource_id="r1", field_id="1")
    expected_spec12 = MockSourceSpec(resource_id="r1", field_id="2")
    expected_spec21 = MockSourceSpec(resource_id="r2", field_id="1")

    @pytest.fixture
    def sample_filepath(self, tmp_path):
        file_path = tmp_path / ".env.template"
        with open(file_path, "w") as f:
            f.write(self.TEMPLATE_CONTENT)
        yield file_path

    @pytest.fixture
    def mock_resource_manager(self):
        resource1 = Mock(spec=Resource)
        resource1.resource_id = "r1"
        resource2 = Mock(spec=Resource)
        resource2.resource_id = "r2"
        resource1.build_spec.side_effect = [self.expected_spec11, self.expected_spec12]
        resource2.build_spec.side_effect = [self.expected_spec21]

        def mock_get_value(x):
            return f"{x.resource_id}{x.field_id}_value"

        resource1.get_value = mock_get_value
        resource2.get_value = mock_get_value
        rm = ResourcesManager(resource1, resource2)
        return rm

    def test_raises_if_no_registered_resources(self):
        rm = ResourcesManager()
        with pytest.raises(ValueError):
            rm.get_resource("nope")

    def test_load_template(self, sample_filepath):
        actual = _load_template(sample_filepath)
        assert actual == self.EXPECTED_MAPPING

    def test_load_invalid_template_raises_error(self, tmp_path):
        file_path = tmp_path / ".env.template"
        with open(file_path, "w") as f:
            f.write("""row without # or equal sign""")

        with pytest.raises(ValueError):
            _load_template(file_path)

    def test_extract_values_to_request(self, mock_resource_manager):
        actual = _extract_values_to_request(resource_manager=mock_resource_manager, parsed_data=self.EXPECTED_MAPPING)
        assert actual == {"KEY11": self.expected_spec11, "KEY12": self.expected_spec12, "KEY21": self.expected_spec21}

    def test_process(self, sample_filepath, mock_resource_manager):
        dst_filepath = process(sample_filepath, resource_manager=mock_resource_manager)
        expected_fpath = sample_filepath.parent / ".env"

        assert dst_filepath == expected_fpath

        with open(dst_filepath) as f:
            content = f.read()
        assert content == self.EXPECTED_ENV_FILE_CONTENT

    def test_build_default_resources_manager(self):
        rm = build_default_resources_manager()
        assert len(rm._resources) == 2
        assert isinstance(rm.get_resource("azure-keyvault"), AzureKeyVaultResource)
        assert isinstance(rm.get_resource("kubernetes"), KubernetesResource)
