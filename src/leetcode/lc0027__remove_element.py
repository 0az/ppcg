"""
Remove element from array, in-place.
>>> s = Solution()
>>> case = [3, 2, 2, 3]
>>> s.removeElement(case, 3)
2
>>> sorted(case[:2])
[2, 2]
>>> case = [0, 1, 2, 2, 3, 0, 4, 2]
>>> s.removeElement(case, 2)
5
>>> sorted(case[:5])
[0, 0, 1, 3, 4]
"""


class Solution:
    def removeElement(self, nums, val):
        """
        :type nums: List[int]
        :type val: int
        :rtype: int
        """
        if not nums:
            return 0

        idx = 0

        while idx < len(nums):
            if nums[idx] == val:
                del nums[idx]
            else:
                idx += 1
        return len(nums)
