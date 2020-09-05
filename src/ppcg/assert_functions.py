from __future__ import annotations

"""
Dynamic generation of function-wrapped assert statements.
"""

import ast
from enum import IntEnum, auto
from typing import (Any, Callable, Dict, List, NamedTuple, NoReturn, Protocol,
                    Tuple, TypeVar, Union, overload)


class Expected(IntEnum):
    NOT_A_BOOLEAN = auto()
    FALSE = auto()
    TRUE = auto()

    @classmethod
    def get(cls, obj: Any) -> Expected:
        if obj is True:
            return cls.TRUE
        elif obj is False:
            return cls.FALSE
        else:
            return cls.NOT_A_BOOLEAN


class AssertSpec(NamedTuple):
    args: bool
    kwargs: bool
    type: Expected

    def __repr__(self):
        return f'AssertSpec({self.args}, {self.kwargs}, {self.type.name})'

    @classmethod
    def get(cls, args: Tuple[...], kwargs: Dict[str, Any], expected: Any):
        return cls(bool(args), bool(kwargs), Expected.get(expected))


specs: List[AssertSpec] = []

for args in (True, False):
    for kwargs in (True, False):
        for type_ in Expected:
            specs.append(AssertSpec(args, kwargs, type_))


T = TypeVar('T', contravariant=True)


class AssertFunction(Protocol[T]):
    def __call__(
        self, expected: T, function: Callable[..., T], *args: Any, **kwargs: Any
    ) -> Union[NoReturn, None]:
        ...


assert_functions: Dict[AssertSpec, AssertFunction] = {}
_locals: Dict[str, AssertFunction] = {}

for i, spec in enumerate(specs):
    args, kwargs, type_ = spec

    # Arguments
    pos = []
    if type_ == Expected.NOT_A_BOOLEAN:
        pos.append(ast.arg('expected'))
    pos.append(ast.arg('function'))
    var_arg = ast.arg('args')
    var_kwarg = ast.arg('kwargs')
    arguments = ast.arguments(pos, [], var_arg, [], [], var_kwarg, [])

    # Call
    call_func = ast.Name('function', ast.Load())
    call_args = (
        [ast.Starred(ast.Name('args', ast.Load()), ast.Load())] if args else []
    )
    call_keywords = (
        [ast.keyword(None, ast.Name('kwargs', ast.Load()))] if kwargs else []
    )
    call = ast.Call(call_func, call_args, call_keywords)

    # Assert
    assert_test: ast.expr
    if type_ == Expected.NOT_A_BOOLEAN:
        assert_test = ast.Compare(
            call, [ast.Eq()], [ast.Name('expected', ast.Load())]
        )
    else:
        assert_test = call
        if type_ == Expected.FALSE:
            assert_test = ast.UnaryOp(ast.Not(), call)

    assert_stmt = ast.Assert(assert_test)

    function_name = f'__assert'
    function_def = ast.FunctionDef(function_name, arguments, [assert_stmt], [])

    fixed = ast.fix_missing_locations(ast.Module([function_def], []))
    exec(compile(fixed, '<generated>', 'exec'), {}, _locals)
    assert_functions[spec] = _locals[function_name]


@overload
def get_assert(args: Tuple[...], kwargs: Dict[str, Any], expected: Any):
    ...


def get_assert(args: Tuple[...], kwargs: Dict[str, Any], expected: Any):
    pass


assert_functions[AssertSpec(False, False, Expected.TRUE)](lambda: False)
