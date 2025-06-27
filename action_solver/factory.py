from typing import Self

from igraph import Graph

from .action import Action
from .solver import ActionSolver
from .state import SolverState


class ActionSolverFactory:
    def __init__(self, dry_run: bool):
        """
        Creates a new factory instance for constructing an :`ActionSolver`.

        Parameters:
        - dry_run (bool): Whether the dry-run ("simulation") or actual logic
          should be executed when calling the actual solver.
        """
        self._graph = Graph(directed=True)
        self._actions = []
        self._dry_run = dry_run
        self._parameters = {}
        self._state = SolverState.construct_empty()

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

    def bind_globals(self, **kwargs) -> Self:
        """
        Binds :class:`SolverState` globals (variables visible to all actions).
        """
        self._state.globals.update(kwargs)
        return self

    def _add_to_known_actions_and_graph(self, action: type[Action]):
        if action not in self._actions:
            self._graph.add_vertex(action)
            self._actions.append(action)

    def _add_edge(
        self,
        from_action: type[Action],
        to_action: type[Action],
    ):
        self._graph.add_edge(
            self._actions.index(from_action),
            self._actions.index(to_action),
        )

    def into_solver(self, solver_class: type[ActionSolver]) -> ActionSolver:
        """
        Constructs a new :class:`ActionSolver`.
        """
        return solver_class(
            self._graph,
            self._actions,
            self._dry_run,
            self._state,
        )
