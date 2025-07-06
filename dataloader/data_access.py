from typing import Iterable

from .base import BaseModel
from .loader import BaseLoader


class PersistentModel(BaseModel):
    pass


class PersistentModelLoader[
    TKey: PersistentModel.Key,
    TModel: PersistentModel,
](BaseLoader[TKey, TModel]):
    pass


class PersistentModelsLoader[
    TKey: PersistentModel.Key,
    TModel: PersistentModel,
](BaseLoader[TKey, Iterable[TModel]]):
    pass
