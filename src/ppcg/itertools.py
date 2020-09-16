import itertools
from itertools import *

__all__ = [attr for attr in dir(itertools) if not attr.startswith('_')]  # type: ignore[attr-defined]

del itertools
