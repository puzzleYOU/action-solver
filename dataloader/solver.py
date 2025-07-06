from action_solver import Action
from action_solver.solver import ActionSolver

from igraph import Graph

from .base import BaseModel, LoaderState
from .registry import LoaderRegistry


class DataLoaderSolver[TResult: Action.Result](ActionSolver[TResult]):
    def __init__(
        self,
        graph: Graph,
        registry: LoaderRegistry,
        result: type[TResult],  # TODO constrain harder
    ):
        super().__init__(
            graph=graph,
            actions=registry.enumerate_loaders(),
            dry_run=False,
            state=LoaderState[BaseModel.Key](
                registry=registry,
                pending_keys={},
            ),
            result=result,
        )

    def _apply_step(self, ordinal: int) -> Action.Result:
        action_class = self._actions[ordinal]
        action = action_class(self._state)
        result = action.invoke(self._dry_run)
        self._state.results[result.__class__] = result
        return result