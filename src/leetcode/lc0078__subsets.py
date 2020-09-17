from typing import List, Tuple

import hypothesis.strategies as st
import pytest
from hypothesis import given

from ppcg import case
from ppcg.typing import Callable

_LC_ENTRYPOINT_ = 'subsets'
_LC_EXPORT_ = 'power_set'
_LC_DESCRIPTION_ = '''
Given a set of distinct integers, nums, return all possible subsets
(the power set).

Note: The solution set must not contain duplicate subsets.
'''


def power_set(lst: List[int]) -> List[Tuple[int, ...]]:
    alphabet = lst
    result = []

    for i in range(2 ** len(alphabet)):
        tmp = tuple(e for j, e in enumerate(alphabet) if i & (1 << j))
        result.append(tmp)

    return result


def power_set_with_backtracking(lst: List[int]) -> List[Tuple[int, ...]]:
    alphabet = lst
    result: List[Tuple[int, ...]] = [()]

    for e in alphabet:
        length = len(result)

        # Can't iterate and mutate
        for j in range(length):
            result.append(result[j] + (e,))

    return result


def reference_power_set(lst: List[int]):
    from itertools import chain, combinations

    size = len(lst)

    return sorted(
        chain.from_iterable(combinations(lst, n) for n in range(size + 1))
    )


@pytest.mark.parametrize(  # type: ignore[misc]
    'fn',
    [
        power_set,
        power_set_with_backtracking,
        #
    ],
)
@given(st.builds(sorted, st.sets(st.integers(), max_size=10)))
def test_power_set(
    fn: Callable[[List[int]], List[Tuple[int, ...]]],
    lst: List[int],
    #
):
    result = sorted(tuple(s) for s in fn(lst))

    assert result == reference_power_set(lst)
