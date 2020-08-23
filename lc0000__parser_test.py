_LC_ENTRYPOINT_ = 'identity'
_LC_TARGET_ = 'targetMethod'
_LC_SPEC_ = [
    '''
    '''
]


def identity(s: str) -> str:
    return s


def test_decorator(maybe_func=None):
    if not maybe_func:
        return lambda func: func
    return maybe_func


@test_decorator()
def test_function(s: str):
    assert s == identity(s)
