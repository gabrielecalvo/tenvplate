from pathlib import Path

from tenvplate.cli import _parse_args


class TestParseArgs:
    def test_default(self):
        actual_src_path, actual_dst_path = _parse_args([])
        assert actual_src_path == Path(".env.template")
        assert actual_dst_path == Path(".env")

    def test_custom_paths(self):
        actual_src_path, actual_dst_path = _parse_args(["--src-path", "mysrc", "--dst-path", "mydst"])
        assert actual_src_path == Path("mysrc")
        assert actual_dst_path == Path("mydst")
