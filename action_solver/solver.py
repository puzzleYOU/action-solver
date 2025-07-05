# NOTE this code is full of 'type: ignore' as igraph stubs are just
# broken. as we will rewrite this part in C(++) or Rust using CPython/Swig
# or PyO3 this should not bother much.

from abc import ABC, abstractmethod

from igraph import Graph

from .action import Action, VoidResult
from .state import SolverState


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

    def __init__(
        self,
        graph: Graph,
        actions: list[type[Action]],
        dry_run: bool,
        state: SolverState,
    ):
        self._graph = graph
        self._actions = actions
        self._dry_run = dry_run
        self._state = state

        # NOTE returns bool. just trust it exists. type stub doesn't know.
        if not self._graph.is_dag():  # type: ignore
            raise ValueError("graph must not have any cycle")
        if self._graph_has_leaf_nodes():
            raise ValueError("graph must be connected")

    def _graph_has_leaf_nodes(self):
        # NOTE just trust this code. same rant as above regarding type stub
        return any(
            map(
                lambda vertex: len(vertex.all_edges()) == 0,  # type: ignore
                self._graph.vs,  # type: ignore
            )
        )

    @abstractmethod
    def solve(
        self,
        final_result_type: type[TFinalResult] = VoidResult,
    ) -> TFinalResult:
        pass

    def _apply_step(self, ordinal: int) -> Action.Result:
        action_class = self._actions[ordinal]
        action = action_class(self._state)
        result = action.invoke(self._dry_run)
        self._state.results[result.__class__] = result
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
        # TODO this per-step assert is hopefully optimized away in production
        # or after cleanly rewriting solver interface in idk whatever lang
        # we should not need anymore
        for ordinal in self._graph.topological_sorting():  # type: ignore
            assert isinstance(ordinal, int)
            final_result = self._apply_step(ordinal)
        if not isinstance(final_result, final_result_type):
            raise TypeError(
                f"expected to finalize to {final_result_type.__name__}, got "
                f"{final_result.__class__}: {final_result}"
            )
        return final_result
