import logging
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .protocols import SourceSpec
from .resources import ResourcesManager

EnvPairs = Mapping[str, str]

logger = logging.getLogger(__name__)


def _load_template(file_path: Path) -> EnvPairs:
    parsed_data = {}

    with Path.open(file_path) as f:
        for line in f.readlines():
            _line = line.strip()
            if not _line or _line.startswith("#"):
                continue
            if "=" not in _line:
                raise ValueError(f"Invalid line, does not contain `=`: {line}")

            env_name, env_value = _line.split("=", 1)
            env_name = env_name.strip()
            env_value = env_value.strip().strip("'\"")
            parsed_data[env_name] = env_value

    return parsed_data


def _extract_values_to_request(resource_manager: ResourcesManager, parsed_data: EnvPairs) -> Mapping[str, Any]:
    values_to_request = {}

    for key, value in parsed_data.items():
        if not (value.startswith("{{") and value.endswith("}}")):
            continue
        spec_str = value[2:-2].strip()
        source_type, *source_args = spec_str.split("/")

        resource = resource_manager.get_resource(source_type)
        values_to_request[key] = resource.build_spec(*source_args)

    return values_to_request


def _request_values(resource_manager: ResourcesManager, values_to_request: Mapping[str, SourceSpec]) -> EnvPairs:
    resolved_values = {}

    for key, source_spec in values_to_request.items():
        resource = resource_manager.get_resource(source_spec.resource_id)
        resolved_values[key] = resource.get_value(source_spec)

    return resolved_values


def process(
    src_path: Path,
    dst_path: Path,
    resource_manager: ResourcesManager,
) -> Path:
    parsed_data = _load_template(src_path)
    values_to_request = _extract_values_to_request(resource_manager, parsed_data)
    resolved_values = _request_values(resource_manager, values_to_request)

    with Path.open(dst_path, "w") as f:
        for key, value in parsed_data.items():
            if key in resolved_values:
                value = resolved_values[key]
            f.write(f"{key}={value}\n")

    return dst_path
