from __future__ import annotations

from itertools import accumulate, chain, islice
from operator import mul
from typing import List

import hypothesis.strategies as st
from hypothesis import given

from ppcg import omit
from ppcg.functools import reduce

_LC_ENTRYPOINT_ = 'productExceptSelf'
_LC_EXPORT_ = 'product_except_self'
_LC_DESCRIPTION_ = '''
Given an array nums of n integers where n > 1, return an array output such that output[i] is equal to the product of all the elements of nums except nums[i].
'''


def product_except_self(lst: List[int]) -> List[int]:
    pad = (1,)
    n = len(lst)

    lr_pass = accumulate(islice(chain(pad, lst), n), mul)
    rl_pass = accumulate(islice(chain(pad, reversed(lst)), n), mul)

    out = list(lr_pass)
    for i, r in zip(reversed(range(n)), rl_pass):
        out[i] *= r

    return out


@omit
def reference_product_except_self(lst: List[int]) -> List[int]:
    n = len(lst)
    out = [1] * n

    for i, e in enumerate(lst):
        for j in range(n):
            if i != j:
                out[j] *= e

    return out


@given(st.lists(st.integers(), min_size=1, max_size=10),)
def test_product_except_self(lst: List[int]) -> None:
    expected = reference_product_except_self(lst)

    result = product_except_self(lst)

    assert result == expected
