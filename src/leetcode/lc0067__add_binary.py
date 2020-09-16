from hypothesis import assume, given
from hypothesis.strategies import from_regex

_LC_ENTRYPOINT_ = 'addBinary'
_LC_EXPORT_ = 'add_binary'

_LC_DESCRIPTION_ = '''
Add two numbers, encoded as binary strings.
'''


def add_binary(left: str, right: str) -> str:
    diff = len(left) - len(right)

    if diff < 0:
        left, right = right, left
        diff = -diff

    result = []
    carry = False

    for (l, r) in zip(reversed(left), reversed(right)):
        if l == r:
            result.append(carry)
            carry = l == '1'
        elif l == '1' or r == '1':
            if carry:
                result.append(False)
                carry = True
            else:
                result.append(True)
                carry = False
        else:
            result.append(carry)
            carry = False

    if diff:
        for c in left[diff - 1 :: -1]:
            if carry and c == '1':
                result.append(False)
                carry = True
            elif carry or c == '1':
                result.append(True)
                carry = False
            else:
                result.append(False)
                carry = False

    if carry:
        result.append(True)

    return ''.join(map(str, map(int, reversed(result))))


def reference_add_binary(left: str, right: str) -> str:
    return bin(int(left, 2) + int(right, 2))[2:]


@given(
    from_regex(f'1[01]*|0', fullmatch=True),
    from_regex(f'1[01]*|0', fullmatch=True),
)
def test_add_binary(left: str, right: str) -> None:
    assert (left, right) and add_binary(left, right) == reference_add_binary(
        left, right
    )
