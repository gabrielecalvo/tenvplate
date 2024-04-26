import logging
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from src.resources import ResourcesManager
from src.sources.protocols import Resource, SourceSpec

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
        resolved_value = resource.get_value(source_spec)
        if resolved_value is None:
            raise ValueError(f"Failed to fetch value: {source_spec}")
        resolved_values[key] = resolved_value

    return resolved_values


def build_default_resources_manager() -> ResourcesManager:
    resources: list[Resource] = []

    try:
        from src.sources import azure_keyvault

        resources.append(azure_keyvault.AzureKeyVaultResource())
    except ImportError:
        logger.warning("Azure KeyVault resource is not available")

    try:
        from src.sources import k8s

        resources.append(k8s.KubernetesResource())
    except ImportError:
        logger.warning("Azure KeyVault resource is not available")

    return ResourcesManager(*resources)


def process(
    src_path: str | Path = ".env.template",
    dst_path: str | Path | None = None,
    resource_manager: ResourcesManager | None = None,
) -> Path:
    src_path = Path(src_path)
    dst_path = Path(src_path).parent / ".env" if dst_path is None else Path(dst_path)

    if resource_manager is None:
        resource_manager = build_default_resources_manager()

    parsed_data = _load_template(src_path)
    values_to_request = _extract_values_to_request(resource_manager, parsed_data)
    resolved_values = _request_values(resource_manager, values_to_request)

    with Path.open(dst_path, "w") as f:
        for key, value in parsed_data.items():
            if key in resolved_values:
                value = resolved_values[key]
            f.write(f"{key}={value}\n")

    return dst_path


if __name__ == "__main__":
    process()
