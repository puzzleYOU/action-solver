import unittest
from dataclasses import dataclass

from action_solver import Action, ActionSolverFactory
from action_solver.solver import SequentialExecutionActionSolver


class ProcessInputs(Action):
    @dataclass(frozen=True)
    class Result(Action.Result):
        a: int
        b: int

    def _production_impl(self) -> Result:
        return self.Result(
            a=self._state.globals["num_a"] * 2,
            b=self._state.globals["num_b"] ** 2,
        )


class Add(Action):
    @dataclass(frozen=True)
    class Result(Action.Result):
        sum: int

    def _production_impl(self) -> Result:
        processed_nums = self.get_result(ProcessInputs.Result)
        return self.Result(processed_nums.a + processed_nums.b)


class Multiply(Action):
    @dataclass(frozen=True)
    class Result(Action.Result):
        product: int

    def _production_impl(self) -> Result:
        processed_nums = self.get_result(Add.Result)
        return self.Result(processed_nums.sum * 10)


class ReverseDigits(Action):
    @dataclass(frozen=True)
    class Result(Action.Result):
        reversed_number: str

    def _production_impl(self) -> Result:
        product = self.get_result(Multiply.Result).product
        reversed_number = str(reversed(str(product)))
        return self.Result(reversed_number)


class SequentialSolverTests(unittest.TestCase):
    def test_full_run(self):
        solver = (
            ActionSolverFactory()
            .bind_globals(a=4, b=2)
            .add_dependencies_from(ReverseDigits)
            .into_solver(solver_class=SequentialExecutionActionSolver)
        )
        self.assertEqual(
            ReverseDigits.Result(reversed_number="042"),
            solver.solve(ReverseDigits.Result),
        )
