import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from .processing import process
from .resources import ResourcesManager

PLUGIN_DIR = Path(__file__).parents[1] / "plugins"


def _parse_args(args: Sequence[str]) -> tuple[Path, Path]:
    parser = argparse.ArgumentParser(description="Writes .env file based on the .env.template")
    parser.add_argument("--src-path", type=Path, help="Path to the template file", default=Path(".env.template"))
    parser.add_argument("--dst-path", type=Path, help="Path to the resulting .env file", default=None)
    parsed_args = parser.parse_args(args)
    dst_path = parsed_args.src_path.parent / ".env" if parsed_args.dst_path is None else parsed_args.dst_path
    return parsed_args.src_path, dst_path


def run() -> None:
    resource_manager = ResourcesManager.from_plugin_dir(plugin_dir=PLUGIN_DIR)
    src_path, dst_path = _parse_args(sys.argv[1:])
    process(src_path=src_path, dst_path=dst_path, resource_manager=resource_manager)
