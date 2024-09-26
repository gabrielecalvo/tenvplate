import shutil
from unittest.mock import Mock

import pytest

from tenvplate.resources import ResourcesManager
from tests.conftest import TEST_DATA_DIR


class TestResourceManager:
    def test_unregistered_raises_error(self):
        resource_manager = ResourcesManager(logger=Mock())
        with pytest.raises(KeyError):
            resource_manager.get_resource("nope")

    def test_can_register_and_get_resource(self):
        mock_resource = Mock()
        resource_manager = ResourcesManager(logger=Mock())
        resource_manager.register_resource("test_resource", mock_resource)
        assert resource_manager.get_resource("test_resource") == mock_resource

    def test_can_init_from_plugin_dir(self, tmp_path):
        shutil.copyfile(TEST_DATA_DIR / "sample_plugin.py", tmp_path / "plugin1.py")
        resource_manager = ResourcesManager.from_plugin_dir(tmp_path, logger=Mock())
        actual_resource = resource_manager.get_resource("sample-resource")
        assert actual_resource is not None
        assert str(actual_resource.__class__) == "<class 'plugin1.SampleResource'>"

    def test_from_plugin_dir_skips_init_files(self, tmp_path):
        shutil.copyfile(TEST_DATA_DIR / "sample_plugin.py", tmp_path / "__init__.py")
        resource_manager = ResourcesManager.from_plugin_dir(tmp_path, logger=Mock())
        assert not resource_manager.resource_register
