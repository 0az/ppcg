from dataclasses import dataclass
from typing import Any, Dict, Generic, Tuple, TypeVar, overload

T = TypeVar('T')
U = TypeVar('U')


@dataclass
class Case(Generic[T]):
    """
    A pure function test case.
    """

    expected: T
    args: Tuple
    kwargs: Dict[str, Any]


@overload
def case(expected: U = None, /, **kwargs: Any) -> Case[U]:
    ...


@overload
def case(expected: U, /, *args: Any, **kwargs: Any) -> Case[U]:
    ...


def case(expected=None, /, *args, **kwargs):
    """
    Create a test case.
    """
    return Case(expected, args, kwargs)
