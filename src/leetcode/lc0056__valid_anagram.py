from collections import Counter

import hypothesis.strategies as st
import pytest
from hypothesis import assume, given

_LC_ENTRYPOINT_ = 'isAnagram'
_LC_EXPORT_ = 'is_anagram_counter'
_LC_DESCRIPTION_ = '''
Given two strings s and t, write a function to determine if t is an anagram of s.
'''


def is_anagram_counter(left: str, right: str) -> bool:
    return Counter(left) == Counter(right)


@st.composite
def anagram(draw, src=None):
    if not src:
        src = st.text()
    left = draw(src)

    if not left:
        return ''

    right = ''.join(
        draw(st.randoms(use_true_random=False)).sample(left, k=len(left))
    )
    return right


@st.composite
def not_anagram(draw, src=None):
    if not src:
        src = st.text()
    left = draw(src)
    right = draw(st.text(min_size=len(left), max_size=len(left)) | st.text())
    assume(left != right)
    return right


@given(
    st.shared(st.text(), key='anagram'),
    anagram(st.shared(st.text(), key='anagram')),
)
def test_is_anagram_works_on_anagrams(left: str, right: str) -> None:
    assert is_anagram(left, right)


@given(
    st.shared(st.text(), key='anagram'),
    not_anagram(st.shared(st.text(), key='anagram')),
)
def test_is_anagram_works_on_non_anagrams(left: str, right: str) -> None:
    assert not is_anagram(left, right)
