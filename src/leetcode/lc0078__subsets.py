from typing import List

from hypothesis import example, given
from hypothesis import strategies as st

from ppcg import case

_LC_ENTRYPOINT_ = 'subsets'
_LC_EXPORT_ = 'power_set'
_LC_DESCRIPTION_ = '''
Given a set of distinct integers, nums, return all possible subsets
(the power set).

Note: The solution set must not contain duplicate subsets.
'''


def power_set(lst: List[int]):
    alphabet = lst
    result = []

    for i in range(2 ** len(alphabet)):
        tmp = [e for j, e in enumerate(alphabet) if i & (1 << j)]
        result.append(tmp)
    return result


def reference_power_set(lst: List[int]):
    from itertools import chain, combinations

    size = len(lst)

    return sorted(
        chain.from_iterable(combinations(lst, n) for n in range(size + 1))
    )


@given(st.builds(sorted, st.sets(st.integers(), max_size=10)))
def test_power_set(lst: List[int]):
    l = sorted(tuple(s) for s in power_set(lst))
    assert l == reference_power_set(lst)
