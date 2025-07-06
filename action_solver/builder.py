from typing import Any, Self

from igraph import Graph

from .action import Action
from .state import SolverState


class ActionSolverBuilder[TFinalResult: Action.Result]:
    def __init__(
        self,
        result: type[TFinalResult],
        dry_run: bool = False,
    ):
        """
        Creates a new factory instance for constructing an :`ActionSolver`.

        Parameters:
        - dry_run (bool): Whether the dry-run ("simulation") or actual logic
          should be executed when calling the actual solver. Defaults to
          `False` (actual logic).
        """
        self.graph = Graph(directed=True)
        self.actions: list[type[Action]] = []
        self.dry_run = dry_run
        self.solver_state = SolverState.construct_empty()
        self.result = result

    def add_dependency(
        self,
        action: type[Action],
        depends_on: type[Action],
    ) -> Self:
        """
        Adds two dependent actions to the solver.

        Parameters:
        - action: The action depending on `depends_on`.
        - depends_on: The action which will be executed before `action`.
        """
        self._add_to_known_actions_and_graph(action)
        self._add_to_known_actions_and_graph(depends_on)
        self._add_edge(depends_on, action)
        return self

    def add_dependencies_from(self, action: type[Action]) -> Self:
        """
        Transitively adds dependencies from `action`'s result dependencies.
        """
        self._add_to_known_actions_and_graph(action)
        for dependency in action.get_dependent_actions():
            self.add_dependency(action, dependency)
            self.add_dependencies_from(dependency)
        return self

    def bind_globals(self, **kwargs: Any) -> Self:
        """
        Binds :class:`SolverState` globals (variables visible to all actions).
        """
        self.solver_state.globals.update(kwargs)
        return self

    def _add_to_known_actions_and_graph(self, action: type[Action]):
        if action not in self.actions:
            self.graph.add_vertex(action)
            self.actions.append(action)

    def _add_edge(
        self,
        from_action: type[Action],
        to_action: type[Action],
    ):
        self.graph.add_edge(
            self.actions.index(from_action),
            self.actions.index(to_action),
        )
