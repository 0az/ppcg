"""
Longest common prefix.

>>> s = Solution()
>>> s.longestCommonPrefix(['a', 'b'])
''
>>> s.longestCommonPrefix(['a', 'a', 'b'])
''
>>> s.longestCommonPrefix(['a', 'aa'])
'a'
>>> s.longestCommonPrefix(['a', 'aa', 'aaa'])
'a'
"""

from itertools import groupby


def all_equal(iterable):
    grouped = groupby(iterable)
    return next(grouped, True) and not next(grouped, False)


class Solution:
    def longestCommonPrefix(self, strs):
        """
        :type strs: List[str]
        :rtype: str
        """
        if not strs:
            return ''
        idx = 0
        try:
            while all_equal(s[idx] for s in strs):
                idx += 1
        except IndexError:
            pass
        return strs[0][:idx]
