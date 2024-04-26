from src.sources.protocols import Resource


class ResourcesManager:
    def __init__(self, *resources: Resource) -> None:
        self._resources = {i.resource_id: i for i in resources}

    def get_resource(self, resource_id: str) -> Resource:
        if resource_id not in self._resources:
            raise ValueError(f"Unsupported resource: {resource_id}")

        return self._resources[resource_id]
