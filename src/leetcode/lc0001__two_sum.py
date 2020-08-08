"""
Find the indices of the two numbers adding up to target.

>>> Solution().twoSum([2, 7, 11, 15], 9)
[0, 1]
"""


class Solution:
    def twoSum(self, nums, target):
        """
        :type nums: List[int]
        :type target: int
        :rtype: List[int]
        """
        complements = {}
        for i, n in enumerate(nums):
            complement = target - n
            if complement in complements:
                return [i, complements[complement]]
            complements[n] = i
