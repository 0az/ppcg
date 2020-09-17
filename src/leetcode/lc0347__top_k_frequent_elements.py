from collections import Counter
from heapq import heapify, heappush, heapreplace
from typing import List

import hypothesis.strategies as st
import pytest
from hypothesis import assume, given

_LC_ENTRYPOINT_ = 'topKFrequent'
_LC_EXPORT_ = 'heapq_top_k'

_LC_DESCRIPTION_ = '''
Given a non-empty array of integers, return the k most frequent elements.
'''


def heapq_top_k(lst: List[int], k: int) -> List[int]:
    counts = Counter(lst)
    heap = []

    for i in range(k):
        k, v = counts.popitem()
        heap.append((v, k))

    heapify(heap)

    while counts:
        k, v = counts.popitem()

        if v > heap[0][0]:
            heapreplace(heap, (v, k))

    return [t[1] for t in heap]


def reference_top_k(lst: List[int], k: int) -> List[int]:
    counts = Counter(lst)
    return [t[0] for t in counts.most_common(k)]


@st.composite
def k_unique_list(draw, elements=st.integers()):
    xs = draw(st.lists(st.integers(), max_size=100))
    n_unique = len(set(xs))
    assume(n_unique > 0)
    k = draw(st.integers(min_value=1, max_value=n_unique))
    return xs, k


@given(k_unique_list())
def test_top_k(tup):
    lst, k = tup

    if len(lst) > k:
        tmp = sorted(v for k, v in Counter(lst).most_common(k + 1))
        assume(len(tmp) > 1 and tmp[0] != tmp[1])

    result = sorted(heapq_top_k(lst, k))
    expected = sorted(reference_top_k(lst, k))
    assert result == expected
