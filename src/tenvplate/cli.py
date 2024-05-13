import argparse
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from .processing import process
from .resources import ResourcesManager

PLUGIN_DIR = Path(__file__).parents[1] / "plugins"


@dataclass
class ParsedArgs:
    src_path: Path
    dst_path: Path
    plugin_dir: Path


def _parse_args(args: Sequence[str]) -> ParsedArgs:
    parser = argparse.ArgumentParser(description="Writes .env file based on the .env.template")
    parser.add_argument("--src-path", type=Path, help="Path to the template file", default=Path(".env.template"))
    parser.add_argument("--dst-path", type=Path, help="Path to the resulting .env file", default=None)
    parser.add_argument("--plugin-dir", type=Path, help="Path to the directory of plugins", default=PLUGIN_DIR)
    parsed_args = parser.parse_args(args)
    dst_path = parsed_args.src_path.parent / ".env" if parsed_args.dst_path is None else parsed_args.dst_path
    return ParsedArgs(src_path=parsed_args.src_path, dst_path=dst_path, plugin_dir=parsed_args.plugin_dir)


def run() -> None:
    args = _parse_args(sys.argv[1:])
    resource_manager = ResourcesManager.from_plugin_dir(plugin_dir=args.plugin_dir)
    process(src_path=args.src_path, dst_path=args.dst_path, resource_manager=resource_manager)
