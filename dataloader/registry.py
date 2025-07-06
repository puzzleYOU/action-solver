from typing import Any

#from .data_access import PersistentModel, PersistentModelLoader, PersistentModelsLoader
#from .presentation import PresentationModel, PresentationModelLoader, PresentationModelsLoader


class LoaderRegistry:
    def __init__(self):
        self._registry: dict[Any, Any] = {}

    def register(self, model: Any, loader: Any):
        self._registry[model.Key] = loader

    def enumerate_loaders(self) -> list[type]:
        return list(self._registry.values())
