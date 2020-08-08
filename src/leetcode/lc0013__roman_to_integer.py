"""
Convert Roman numerals to integers.

>>> s = Solution()
>>> s.romanToInt('I')
1
>>> s.romanToInt('II')
2
>>> s.romanToInt('IV')
4
>>> s.romanToInt('V')
5
>>> s.romanToInt('VI')
6
>>> s.romanToInt('IX')
9
>>> s.romanToInt('XVI')
16
>>> s.romanToInt('XCIX')
99

"""


class Solution:
    VALUES = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    TRANSITIONS = {
        'I': 'VX',
        'V': 'X',
        'X': 'LC',
        'L': 'CD',
        'C': 'DM',
        'D': 'M',
        'M': '',
    }

    def romanToInt(self, s):
        """
        :type s: str
        :rtype: int
        """
        vals = [self.VALUES[c] for c in s]

        prev = 0
        total = 0
        idx = 0

        while idx < len(vals):
            current = vals[idx]
            if prev < current:
                total -= prev
            else:
                total += prev
            prev = current
            idx += 1
        total += prev or 0
        return total
