import logging
from abc import ABC, abstractmethod


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

    def __init__(self, state):
        from action_solver import SolverState

        self._state: SolverState = state

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

    def _log(self, msg: str, level=logging.INFO):
        logger: logging.Logger | None = self._state.globals.get("logger")
        if logger:
            logger.log(level, msg)


class VoidResult(Action.Result):
    def __init__(self):
        pass
