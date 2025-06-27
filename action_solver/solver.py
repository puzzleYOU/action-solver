from abc import ABC, abstractmethod
from dataclasses import dataclass

from igraph import Graph

from .action import Action, VoidResult
from .state import SolverState


@dataclass(frozen=True)
class ActionSolver[TFinalResult: Action.Result](ABC):
    """
    Base class for solving actions in the right order.

    Notes:
    - The vertices of `graph` are action class ordinals. To reconstruct the
      action class from any vertex value (e.g. 0), look into `actions[0]`.
    - `state` may only exactly cover the lifetime of one solver.
    - Always pass `dry_run` to :meth:`Action.invoke` when writing custom
      solver implementations.
    """

    graph: Graph
    actions: list[type[Action]]
    dry_run: bool
    state: SolverState

    def __post_init__(self):
        if not self.graph.is_dag():
            raise ValueError("graph must not have any cycle")
        if self._graph_has_leaf_nodes():
            raise ValueError("graph must be connected")

    def _graph_has_leaf_nodes(self):
        return any(
            map(
                lambda vertex: len(vertex.all_edges()) == 0,
                self.graph.vs,
            )
        )

    @abstractmethod
    def solve(
        self,
        final_result_type: type[TFinalResult] = VoidResult,
    ) -> TFinalResult:
        pass

    def _apply_step(self, ordinal: int) -> Action.Result:
        action_class = self.actions[ordinal]
        action = action_class(self.state)
        result = action.invoke(self.dry_run)
        self.state.results[result.__class__] = result
        return result


class SequentialExecutionActionSolver[TFinalResult: Action.Result](
    ActionSolver[TFinalResult]
):
    """
    A simple solver implementation invoking actions step by step
    according to how the actions' dependencies amongst each other
    are defined.
    """

    def solve(
        self,
        final_result_type: type[TFinalResult] = VoidResult,
    ) -> TFinalResult:
        final_result = VoidResult()
        for ordinal in self.graph.topological_sorting():
            final_result = self._apply_step(ordinal)
        if not isinstance(final_result, final_result_type):
            raise TypeError(
                f"expected to finalize to {final_result_type.__name__}, got "
                f"{final_result.__class__}: {final_result}"
            )
        return final_result
