import argparse
import logging
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
    log_level: str


def _parse_args(args: Sequence[str]) -> ParsedArgs:
    parser = argparse.ArgumentParser(description="Writes .env file based on the .env.template")
    parser.add_argument(
        "--src-path",
        type=Path,
        help="path to the template env file (default .env.template)",
        default=Path(".env.template"),
    )
    parser.add_argument(
        "--dst-path",
        type=Path,
        help="path to the resulting env file (default .env in the same directory as src-path)",
        default=None,
    )
    parser.add_argument(
        "--plugin-dir", type=Path, help=f"path to the directory of plugins (default={PLUGIN_DIR})", default=PLUGIN_DIR
    )
    parser.add_argument("--log-level", type=str, help="logging level (default INFO)", default="INFO")
    parsed_args = parser.parse_args(args)
    dst_path = parsed_args.src_path.parent / ".env" if parsed_args.dst_path is None else parsed_args.dst_path
    return ParsedArgs(
        src_path=parsed_args.src_path,
        dst_path=dst_path,
        plugin_dir=parsed_args.plugin_dir,
        log_level=parsed_args.log_level,
    )


def _create_logger(log_level: str) -> logging.Logger:
    logger = logging.getLogger("tenvplate")
    logger.setLevel(log_level)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def run() -> None:
    args = _parse_args(sys.argv[1:])
    logger = _create_logger(args.log_level)
    resource_manager = ResourcesManager.from_plugin_dir(plugin_dir=args.plugin_dir, logger=logger)
    process(src_path=args.src_path, dst_path=args.dst_path, resource_manager=resource_manager)
