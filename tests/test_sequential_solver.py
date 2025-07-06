import unittest
from dataclasses import dataclass

from action_solver import Action, ActionSolverBuilder
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

    @classmethod
    def get_dependent_actions(cls) -> list[type[Action]]:
        return [ProcessInputs]

    def _production_impl(self) -> Result:
        processed_nums = self.get_result(ProcessInputs.Result)
        return self.Result(processed_nums.a + processed_nums.b)


class Multiply(Action):
    @dataclass(frozen=True)
    class Result(Action.Result):
        product: int

    @classmethod
    def get_dependent_actions(cls) -> list[type[Action]]:
        return [Add]

    def _production_impl(self) -> Result:
        processed_nums = self.get_result(Add.Result)
        return self.Result(processed_nums.sum * 10)


class ReverseDigits(Action):
    @dataclass(frozen=True)
    class Result(Action.Result):
        reversed_number: str

    @classmethod
    def get_dependent_actions(cls) -> list[type[Action]]:
        return [Multiply]

    def _production_impl(self) -> Result:
        product = self.get_result(Multiply.Result).product
        reversed_number = str(product)[::-1]
        return self.Result(reversed_number)


class SequentialSolverTests(unittest.TestCase):
    def test_full_run_with_transitively_added_dependencies(self):
        builder = (
            ActionSolverBuilder(ReverseDigits.Result)
            .bind_globals(num_a=4, num_b=2)
            .add_dependencies_from(ReverseDigits)
        )
        solver = (
            SequentialExecutionActionSolver[ReverseDigits.Result]
            .from_builder(builder)
        )
        self.assertEqual("021", solver.solve().reversed_number)
