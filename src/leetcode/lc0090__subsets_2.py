from __future__ import annotations

from collections import Counter
from typing import List, Set, Tuple

import hypothesis.strategies as st
import pytest
from hypothesis import given

from ppcg.itertools import chain, combinations
from ppcg.typing import Callable

_LC_ENTRYPOINT_ = 'subsetsWithDup'
_LC_EXPORT_ = 'power_set_no_sets'

_LC_DESCRIPTION_ = '''
Given a set of distinct integers, nums, return all possible subsets
(the power set).

Note: The solution set must not contain duplicate subsets.
'''


def power_set_with_sets(lst: List[int]) -> Set[Tuple[int, ...]]:
    alphabet = lst
    result = set()

    for i in range(2 ** len(alphabet)):
        tmp = tuple(e for j, e in enumerate(alphabet) if i & (1 << j))
        result.add(tmp)
    return result


def power_set_backtracking(lst: List[int]) -> List[Tuple[int, ...]]:
    result: List[Tuple[int, ...]] = [()]
    alphabet = sorted(lst)

    length = len(result)

    for i, e in enumerate(alphabet):
        if e != alphabet[i - 1]:
            length = len(result)

        for j in range(len(result) - length, len(result)):
            result.append(result[j] + (e,))

    return result


def reference_power_set(lst: List[int]) -> List[Tuple[int, ...]]:

    size = len(lst)
    alphabet = sorted(lst)

    return sorted(
        set(
            chain.from_iterable(
                combinations(alphabet, n) for n in range(size + 1)
            )
        )
    )


@pytest.mark.parametrize(  # type: ignore[misc]
    'fn',
    [
        power_set_with_sets,
        power_set_backtracking,
        #
    ],
)
@given(st.builds(sorted, st.lists(st.integers(), max_size=10)))
def test_power_set_v2(
    fn: Callable[[List[int]], List[Tuple[int, ...]]],
    lst: List[int],
    #
):
    l = sorted(tuple(s) for s in fn(lst))
    assert l == reference_power_set(lst)
