"""
Merge two sorted singly-linked lists.

>>> s = Solution()
>>> test(s, [1, 2, 4], [1, 3, 4])
"""

# Definition for singly-linked list.
class ListNode:
    def __init__(self, x):
        self.val = x
        self.next = None

    def __repr__(self):
        return "%s %s" % (self.val, str(self.next))

    @classmethod
    def from_list(cls, l):
        start = current = ListNode(l[0])
        for val in l[1:]:
            current.next = ListNode(val)
            current = current.next
        return start


class Solution:
    def mergeTwoLists(self, l1, l2):
        """
        :type l1: ListNode
        :type l2: ListNode
        :rtype: ListNode
        """
        if l1 is None:
            return l2
        if l2 is None:
            return l1

        if l1.val < l2.val:
            current = l1
            l1 = l1.next
        else:
            current = l2
            l2 = l2.next

        start = current

        while l1 is not None and l2 is not None:
            # print(l1.val, l2.val, id(l1.next), id(l2.next))
            if l1.val < l2.val:
                current.next = l1
                current = l1
                l1 = l1.next
            else:
                current.next = l2
                current = l2
                l2 = l2.next
        if l1 is None:
            current.next = l2
        else:
            current.next = l1
        return start


def test(s, l1, l2):
    left, right = ListNode.from_list(l1), ListNode.from_list(l2)
    print(str(left), str(right))
    result = s.mergeTwoLists(left, right)
    while result is not None:
        print(result.val, end=" ")
        result = result.next
    print()


if __name__ == "__main__":
    test(Solution(), [1, 2, 4], [1, 3, 4])
