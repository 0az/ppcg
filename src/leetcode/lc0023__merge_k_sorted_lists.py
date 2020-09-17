from __future__ import annotations

from dataclasses import dataclass
from heapq import heapify, heappop, heapreplace
from typing import Iterable, List

import hypothesis.strategies as st
from hypothesis import given

from ppcg import omit
from ppcg.itertools import chain
from ppcg.typing import Optional

_LC_ENTRYPOINT_ = 'mergeKLists'
_LC_EXPORT_ = 'merge_k_lists'

_LC_DESCRIPTION_ = '''
Given an array of non-negative integers `arr`, you are initially
positioned at start index of the array. When you are at index `i`, you
can jump to `i + arr[i]` or `i - arr[i]`, check if you can reach to
any index with value 0.

Notice that you can not jump outside of the array at any time.
'''


@omit
@dataclass
class ListNode:
    val: int = 0
    next: Optional[ListNode] = None

    def items(self):
        yield self.val
        if self.next:
            yield from self.next.items()

    def __iter__(self):
        return self.items()

    @classmethod
    def from_iter(cls, it: Iterable[int]) -> Optional[ListNode]:
        start = curr = cls()

        it = iter(it)
        for i in it:
            curr.next = curr = cls(i)

        return start.next


@dataclass
class QueueItem:
    val: int
    node: ListNode

    @classmethod
    def from_list_node(cls, node: ListNode) -> 'QueueItem':
        return cls(node.val, node)

    def __lt__(self, other):
        if isinstance(other, QueueItem):
            return self.val < other.val
        raise NotImplemented


def merge_k_lists(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    if len(lists) == 1:
        return lists[0]

    heap = [QueueItem.from_list_node(node) for node in lists if node]

    if not heap:
        return None

    heapify(heap)

    start = curr = ListNode()

    while len(heap) > 1:
        curr.next = curr = heap[0].node
        if n := heap[0].node.next:
            heapreplace(heap, QueueItem.from_list_node(n))
        else:
            heappop(heap)

    curr.next = heap[0].node

    return start.next


@given(st.lists(st.integers(), min_size=0, max_size=10))
def test_ListNode_roundtrips(l: List[int]) -> None:
    linked_list = ListNode.from_iter(l)
    if not l:
        assert linked_list is None
    assert linked_list is not None
    assert list(linked_list) == l


@given(
    st.lists(
        st.builds(sorted, st.lists(st.integers(), min_size=0, max_size=5)),
        max_size=3,
    )
)
def test_merge_k_lists(lists: List[List[int]]) -> None:
    linked_lists = [ListNode.from_iter(l) for l in lists]
    expected = sorted(chain.from_iterable(lists))
    print(linked_lists)
    _tmp = merge_k_lists(linked_lists)
    result = list(_tmp) if _tmp else []
    assert result == expected
