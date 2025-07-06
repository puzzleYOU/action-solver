from typing import Iterable

from .base import BaseModel
from .loader import BaseLoader


class PresentationModel(BaseModel):
    pass


class PresentationModelLoader[
    TKey: PresentationModel.Key,
    TModel: PresentationModel,
](BaseLoader[TKey, TModel]):
    pass


class PresentationModelsLoader[
    TKey: PresentationModel.Key,
    TModel: PresentationModel,
](BaseLoader[TKey, Iterable[TModel]]):
    pass
