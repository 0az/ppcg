"""
Determine if a number is a palindrome.

>>> s = Solution()
>>> s.isPalindrome(121)
True
>>> s.isPalindrome(-121)
False
>>> s.isPalindrome(10)
True
"""


class Solution:
    def isPalindrome(self, x):
        """
        :type x: int
        :rtype: bool
        """
        if x < 0:
            return False
        digits = []
        while x > 0:
            digits.append(x % 10)
            x //= 10
        for i, digit in enumerate(digits[: len(digits) // 2 + 1], 1):
            if digit != digits[-i]:
                return False
        return True
