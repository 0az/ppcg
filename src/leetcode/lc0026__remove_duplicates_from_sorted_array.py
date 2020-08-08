"""
Remove duplicates from a sorted array in-place.

>>> s = Solution()
>>> case = [1, 1, 2]
>>> s.removeDuplicates(case)
2
>>> case
[1, 2]
>>> case = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]
>>> s.removeDuplicates(case)
5
>>> case
[0, 1, 2, 3, 4]
"""


class Solution:
    def removeDuplicates(self, nums):
        """
        :type nums: List[int]
        :rtype: int
        """
        if not nums:
            return 0

        idx = 1
        current = nums[0]
        while idx < len(nums):
            if nums[idx] == current:
                del nums[idx]
            else:
                current = nums[idx]
                idx += 1
        return len(nums)
