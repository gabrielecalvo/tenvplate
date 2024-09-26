import dataclasses
import textwrap
from unittest.mock import Mock

import pytest

from tenvplate.processing import _extract_values_to_request, _load_template, _request_values, process
from tenvplate.resources import ResourcesManager


@dataclasses.dataclass
class MockSourceSpec:
    resource_id: str
    field_id: str


@dataclasses.dataclass
class MockResource:
    resource_id: str
    mock_store: dict

    def build_spec(self, field_id: str) -> MockSourceSpec:
        return MockSourceSpec(resource_id=self.resource_id, field_id=field_id)

    def get_value(self, source_spec: MockSourceSpec) -> str | None:
        return self.mock_store.get(source_spec.field_id)


class TestProcessing:
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

    expected_spec11 = MockSourceSpec(resource_id="r1", field_id="v1")
    expected_spec12 = MockSourceSpec(resource_id="r1", field_id="v2")
    expected_spec21 = MockSourceSpec(resource_id="r2", field_id="v1")

    @pytest.fixture
    def sample_filepath(self, tmp_path):
        file_path = tmp_path / ".env.template"
        with open(file_path, "w") as f:
            f.write(self.TEMPLATE_CONTENT)
        yield file_path

    def test_parses_valid(self, sample_filepath):
        actual = _load_template(sample_filepath)
        assert actual == self.EXPECTED_MAPPING

    def test_invalid_template_raises_error(self, tmp_path):
        file_path = tmp_path / ".env.template"
        with open(file_path, "w") as f:
            f.write("""row without # or equal sign""")

        with pytest.raises(ValueError):
            _load_template(file_path)

    @pytest.fixture
    def mock_resource_manager(self):
        resource1 = MockResource(resource_id="r1", mock_store={"v1": "r11_value", "v2": "r12_value"})
        resource2 = MockResource(resource_id="r2", mock_store={"v1": "r21_value"})
        rm = ResourcesManager(logger=Mock())
        rm.register_resource("r1", resource1)
        rm.register_resource("r2", resource2)
        return rm

    def test_extract_values_to_request(self, mock_resource_manager):
        actual = _extract_values_to_request(resource_manager=mock_resource_manager, parsed_data=self.EXPECTED_MAPPING)
        assert actual == {"KEY11": self.expected_spec11, "KEY12": self.expected_spec12, "KEY21": self.expected_spec21}

    def test_request_values(self, mock_resource_manager):
        values_to_request = {
            "KEY11": self.expected_spec11,
            "KEY12": self.expected_spec12,
            "KEY21": self.expected_spec21,
        }
        actual = _request_values(resource_manager=mock_resource_manager, values_to_request=values_to_request)
        assert actual == {"KEY11": "r11_value", "KEY12": "r12_value", "KEY21": "r21_value"}

    def test_integration(self, sample_filepath, mock_resource_manager, tmp_path):
        dst_path = tmp_path / ".env"
        actual_fpath = process(src_path=sample_filepath, dst_path=dst_path, resource_manager=mock_resource_manager)

        with open(actual_fpath) as f:
            actual = f.read()

        assert actual == self.EXPECTED_ENV_FILE_CONTENT
