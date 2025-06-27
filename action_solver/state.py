from dataclasses import dataclass
from typing import Any, Self

from .action import Action


@dataclass(frozen=True)
class SolverState:
    """
    State wrapper for the lifetime of a :class:`ActionSolver`.

    Attributes:
    - `globals`: Global variables which are relevant for some actions
      and which are all known before any action has been started.
    - `results`: This is where the :class:`ActionSolver` stores a result
      if a :class:`Action` implementation returned one.
    """

    globals: dict[str, Any]
    results: dict[type[Action.Result], Action.Result]

    @classmethod
    def construct_empty(cls) -> Self:
        return cls(globals={}, results={})

    def get_result[TResult: Action.Result](
        self, result_type: type[TResult]
    ) -> TResult:
        result_candidate = self.results[result_type]
        if not isinstance(result_candidate, result_type):
            raise TypeError(
                f"lookup on result type '{result_type.__name__}' "
                f"revealed {result_candidate.__class__}: {result_candidate}"
            )
        return result_candidate
