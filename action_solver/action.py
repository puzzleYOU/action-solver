import logging
from abc import ABC, abstractmethod
from typing import Self, final


class Action(ABC):
    """Base class for a fragment of control flow.

    An action is intended to encapsulate a specific part of implementation of
    your program. For example, one might have a concrete :class:`Action`
    subclass for fetching from a database, one gathering filesystem data,
    another one for archiving them and finally one for sending the archive
    to a backup storage.

    Actions are stateless entities, i.e. they do not have to care themselves
    about which action takes part in which order. This is something the
    :mod:`solver` module takes care of.

    Actions support following concepts:

    - **Dry-run functionality**: One might want to implement a simulation
      of e.g. writing down to console what the actual run would want to do.
      This is what :meth:`_production_impl` and :meth:`_dry_run_impl` are for.
      One **must** implement :meth:`_production_impl` which contains the
      actual logic when running the action. :meth:`_dry_run` is absolutely
      optional and fails with :class:`NotImplementedError` by default. It may
      be overriden to write down "simulation logic".

    - **Returning results**: This is what the inner class :class:`Action.Result`
      is for. If an :class:`Action` returns something, it is necessary to
      derive an inner result subclass:

      .. code-block:: python
        class MySQLFetchAction(Action):
            @dataclass(frozen=True)
            class Result(Action.Result):  # <<<< here
                users: list[Account]
                chats: list[ChatHistory]

    - **Having dependencies to other actions and global state**.
      Note that from the example above, that your "archiving" action depends
      on data from two previous actions (again, the "previous actions"
      constraint is something the solver implementations take care of).

      This is what :attr:`_state` is for. See the following example:

      .. code-block:: python
        class CreateBackupArchiveAction(Action):
            @dataclass(frozen=True)
            class Result(Action.Result)
                location: str

            def _production_impl(self) -> Result:
                # dependencies to global state (here in form of a constant)
                backup_location = self._state.globals["BACKUP_LOCATION"]

                # dependencies to previous results. you must pass the result
                # type of the action you depend on.
                mysql_result = self._state.get_result(MySQLFetchAction.Result)
                fs_result = self._state.get_result(FSFetchAction.Result)

                with BackupArchive(dir=backup_location) as handle:
                    handle.pack_text_file("users.json",
                                          serialize(mysql_result.users))
                    handle.pack_text_file("chats.json",
                                          serialize(mysql_result.chats))
                    handle.merge(fs_result.backup_archive)
                    return self.Result(location=handle.path)

      See :class:`ActionSolver` and :class:`ActionSolverFactory` to see how
      to pass global state.
    """

    class Result(ABC):
        @abstractmethod
        def __init__(self): ...

    def __init__(self, state: object):
        # NOTE due to circular module interdependencies we cannot expose
        # 'SolverState' to signature. therefore we manually check the type
        from action_solver import SolverState

        if not isinstance(state, SolverState):
            self._raise_type_error(
                exp_class=SolverState, act_class=state.__class__
            )
            
        self._state: SolverState = state
        self._logger: logging.Logger | None = self._unwrap_logger()

    def _raise_type_error(self, exp_class: type, act_class: type):
        raise TypeError(f"'state' must be '{exp_class}', got {act_class}")

    def _unwrap_logger(self) -> logging.Logger | None:
        logger = self._state.globals.get("logger")
        if not isinstance(logger, logging.Logger):
            self._raise_type_error(
                exp_class=logging.Logger, act_class=logger.__class__
            )
        return logger

    @property
    def dependent_actions(self) -> list[type[Self]]:
        return []

    @property
    @final
    def dependent_results(self) -> list[type[Result]]:
        return [T.Result for T in self.dependent_actions]

    def get_global(self, key: str) -> object:
        return self._state.globals[key]

    def get_result[TResult: Result](
        self, result_type: type[TResult]
    ) -> TResult:
        if result_type not in self.dependent_results:
            raise MissingDependencyDeclarationException(
                self.__class__, result_type
            )
        return self._state.get_result(result_type)

    def invoke(self, dry_run: bool) -> Result:
        self._log(self._format_heading(dry_run))
        result = self._dry_run_impl() if dry_run else self._production_impl()
        if not dry_run:
            self._log(" - done.")
        return result

    @abstractmethod
    def _production_impl(self) -> Result:
        pass

    def _dry_run_impl(self) -> Result:
        raise NotImplementedError()

    def _format_heading(self, dry_run: bool) -> str:
        heading = f"=== PROCESSING {self.__class__.__name__}"
        if dry_run:
            heading += " (dry run)"
        return heading

    def _log(self, msg: str, level: int = logging.INFO):
        if self._logger:
            self._logger.log(level, msg)


class VoidResult(Action.Result):
    def __init__(self):
        pass


class MissingDependencyDeclarationException(Exception):
    def __init__(self, from_action: type[Action], to_result: type[Action.Result]):
        super().__init__(
            f"could not resolve result: {from_action} depends on {to_result}. "
            "Did you forget to extend 'Action.dependent_actions'?"
        )
