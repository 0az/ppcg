"""
Check if a string of parentheses is valid.

>>> s = Solution()
>>> s.isValid('()')
True
>>> s.isValid('()[]{}')
True
>>> s.isValid('(]')
False
>>> s.isValid('([)]')
False
>>> s.isValid('{[]}')
True
>>> s.isValid(']')
False
>>> s.isValid('(')
False
"""


class Solution:
    def isValid(self, s):
        """
        :type s: str
        :rtype: bool
        """
        stack = []
        for char in s:
            if char == '(':
                stack.append(')')
            elif char == '{':
                stack.append('}')
            elif char == '[':
                stack.append(']')
            elif char in ']})':
                if not stack or stack[-1] != char:
                    return False
                stack.pop()
            else:
                return False
        return not stack
