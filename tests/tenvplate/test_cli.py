import shutil
import sys
from pathlib import Path
from unittest.mock import patch

from tenvplate.cli import PLUGIN_DIR, _parse_args, run

from tests.conftest import TEST_DATA_DIR


class TestParseArgs:
    def test_default(self):
        actual_args = _parse_args([])
        assert actual_args.src_path == Path(".env.template")
        assert actual_args.dst_path == Path(".env")
        assert actual_args.plugin_dir == PLUGIN_DIR

    def test_default_dst_follows_src(self):
        actual_args = _parse_args(["--src-path", "somepath/.env.template"])
        assert actual_args.src_path == Path("somepath/.env.template")
        assert actual_args.dst_path == Path("somepath/.env")

    def test_custom_paths(self):
        actual_args = _parse_args(["--src-path", "mysrc", "--dst-path", "mydst", "--plugin-dir", "myplugins"])
        assert actual_args.src_path == Path("mysrc")
        assert actual_args.dst_path == Path("mydst")
        assert actual_args.plugin_dir == Path("myplugins")


def test_cli_run(tmp_path):
    sample_src_path = tmp_path / ".env.template"
    shutil.copyfile(TEST_DATA_DIR / ".sample.env.template", sample_src_path)

    plugin_fld = tmp_path / "plugins"
    plugin_fld.mkdir()
    shutil.copyfile(TEST_DATA_DIR / "sample_plugin.py", plugin_fld / "sample_plugin.py")

    test_args = f"tenvplate --src-path {sample_src_path.as_posix()} --plugin-dir {plugin_fld.as_posix()}".split(" ")
    with patch.object(sys, "argv", test_args):
        run()

    with open(sample_src_path.parent / ".env") as f:
        actual_content = f.read()
    assert actual_content == "FIXED=will-be-left-untouched\nENV_VAR=sample-existing-value\n"
