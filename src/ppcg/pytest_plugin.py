from __future__ import annotations

from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Tuple,
    TypeVar,
)

import attr
import pytest
from _pytest._code.code import FormattedExcinfo

from ._public import Case

if TYPE_CHECKING:
    from _pytest._code import ExceptionInfo
    from _pytest._code.code import ExceptionChainRepr
    from _pytest.python import Metafunc

T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., T])


def expect_call(
    f: F,
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
    #
    expected: T,
):
    """
    Assert that a call returns an expected value.
    """
    # Yank, Put, and Substitute...
    if args and kwargs:
        if expected is True:
            assert f(*args, **kwargs)
        elif expected is False:
            assert not f(*args, **kwargs)
        elif expected is None:
            assert f(*args, **kwargs) is None
        else:
            assert f(*args, **kwargs) == expected
    elif args:
        if expected is True:
            assert f(*args)
        elif expected is False:
            assert not f(*args)
        elif expected is None:
            assert f(*args) is None
        else:
            assert f(*args) == expected
    elif kwargs:
        if expected is True:
            assert f(**kwargs)
        elif expected is False:
            assert not f(**kwargs)
        elif expected is None:
            assert f(**kwargs) is None
        else:
            assert f(**kwargs) == expected
    else:
        if expected is True:
            assert f()
        elif expected is False:
            assert not f()
        elif expected is None:
            assert f() is None
        else:
            assert f() == expected


@dataclass
class ReprWrapper(Generic[F]):
    wrapped: F
    repr: str

    def __call__(self, *args, **kwargs) -> T:
        return self.wrapped(*args, **kwargs)

    def __repr__(self):
        return self.repr


class TrimmedExceptionInfo(FormattedExcinfo):
    def repr_excinfo(self, excinfo):
        repr_: ExceptionChainRepr = super().repr_excinfo(excinfo)
        return attr.evolve(repr_, chain=repr_.chain[0])


class LcModule(pytest.Collector):
    def __init__(
        self, name: str = 'cases', parent: pytest.Collector = None, **kwargs
    ):
        super().__init__(name='cases', parent=parent, **kwargs)
        self.module = parent

    def collect(self):
        obj = self.module.obj
        solution_name = obj._LC_EXPORT_
        export = getattr(obj, solution_name)
        cases = obj._LC_CASES_

        collected = [
            SolutionCaseItem.from_parent(
                name=str(i),
                parent=self,
                solution=export,
                solution_name=solution_name,
                args=case.args,
                kwargs=case.kwargs,
                expected=case.expected,
            )
            for i, case in enumerate(cases)
        ]
        return collected


class SolutionCaseItem(pytest.Item):
    def __init__(
        self,
        name,
        parent,
        #
        solution: Callable[..., T],
        solution_name: str,
        args: Tuple[Any, ...],
        kwargs: Dict[str, Any],
        expected: T,
    ):
        super().__init__(name, parent)

        self.solution = ReprWrapper(solution, solution_name)

        self.solution_name = solution_name
        self.args = args
        self.kwargs = kwargs
        self.expected = expected

    def runtest(self):
        expect_call(
            self.solution,
            self.args,
            self.kwargs,
            #
            self.expected,
        )

    def repr_failure(self, excinfo: ExceptionInfo, style=None):
        if excinfo.errisinstance(AssertionError):
            return excinfo.exconly(True)

        if style == 'native' or not excinfo.errisinstance(AssertionError):
            return super().repr_failure(excinfo, style=style)

        # HACK
        fmt = TrimmedExceptionInfo(
            showlocals=self.config.getoption('showlocals', False),
            style=style,
            tbfilter=not self.config.getoption('fulltrace', False),
            # chain=False,
        )
        return fmt.repr_excinfo(excinfo)


@pytest.hookimpl(hookwrapper=True)
def pytest_pycollect_makemodule(path, parent):
    outcome = yield
    result = outcome.get_result()
    if (
        isinstance(result, pytest.Module)
        and hasattr(result.obj, '_LC_EXPORT_')
        and hasattr(result.obj, '_LC_CASES_')
    ):
        outcome.force_result(LcModule.from_parent(parent=result))
