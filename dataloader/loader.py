from abc import abstractmethod
from dataclasses import dataclass
from typing import Iterable

from action_solver import Action, SolverState

from .base import BaseModel
from .registry import LoaderRegistry


class LoaderState[TKey: BaseModel.Key](SolverState):
    def __init__(
        self,
        registry: LoaderRegistry,  # TODO brauch ich den?
        pending_keys: dict[type[TKey], Iterable[TKey]],
    ):
        self._registry = registry
        self._pending_keys = pending_keys


class BaseLoader[TKey: BaseModel.Key, TResult](Action):
    def __init__(
        self,
        keys: Iterable[TKey],
        state: LoaderState[TKey],
    ):
        super().__init__(state)
        self._keys = keys

    @dataclass(frozen=True)
    class Result(Action.Result):
        results: dict[TKey, TResult]

    def _production_impl(self) -> Result:
        return self.Result(results=self._fetch_many(self._keys))

    @abstractmethod
    def _fetch_many(self, keys: Iterable[TKey]) -> dict[TKey, TResult]:
        pass
