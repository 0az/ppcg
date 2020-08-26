from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Dict, List, Tuple, TypeVar

import pytest

from .case import Case

if TYPE_CHECKING:
    from _pytest.python import Metafunc

T = TypeVar('T')


class LcModule(pytest.Collector):
    def __init__(self, name: str, parent: pytest.Collector = None, **kwargs):
        super().__init__(name=name, parent=parent, **kwargs)
        self.module = parent

    def collect(self):
        obj = self.module.obj

        export = getattr(obj, obj._LC_EXPORT_)
        cases = obj._LC_CASES_

        collected = [
            SolutionCaseItem.from_parent(
                name=f'{self.name}_{i}',
                parent=self,
                solution=export,
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
        args: Tuple[Any, ...],
        kwargs: Dict[str, Any],
        expected: T,
    ):
        super().__init__(name, parent)

        self.solution = solution
        self.args = args
        self.kwargs = kwargs
        self.expected = expected

    def runtest(self):
        assert self.solution(*self.args, **self.kwargs) == self.expected


@pytest.hookimpl(hookwrapper=True)
def pytest_pycollect_makemodule(path, parent):
    outcome = yield
    result = outcome.get_result()
    if (
        isinstance(result, pytest.Module)
        and hasattr(result.obj, '_LC_EXPORT_')
        and hasattr(result.obj, '_LC_CASES_')
    ):
        outcome.force_result(
            LcModule.from_parent(name=result.name, parent=result)
        )
