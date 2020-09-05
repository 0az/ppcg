"""
Solution for LC0055: Jump Game (Medium).
"""

from typing import List

from ppcg import case

_LC_ENTRYPOINT_ = 'canJump'
_LC_EXPORT_ = 'jump_game_reverse'
_LC_CASES_ = [
    case(True, [2, 3, 1, 1, 4]),
    case(False, [3, 2, 1, 0, 4]),
]
_LC_DESCRIPTION_ = '''
Given an array of non-negative integers, you are initially positioned
at the first index of the array. Each element in the array represents
your maximum jump length at that position. Determine if you are able
to reach the last index.
'''


def jump_game_reverse(board: List[int]) -> bool:
    target = len(board) - 1

    if target <= 0:
        return True

    i = target - 1
    while i >= 0:
        elem = board[i]
        if i + elem >= target:
            target = i
        i -= 1

    return not target
