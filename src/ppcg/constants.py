from dataclasses import dataclass
from enum import Enum, auto


class SpanType(Enum):
    PRAGMA = auto()
    TEST = auto()
    IMPORT = auto()


@dataclass
class Pragma:
    name: str
    required: bool = True


_pragmas = (
    Pragma('export'),
    Pragma('entrypoint'),
    Pragma('spec', required=False),
)
LC_PRAGMAS = {f'_LC_{pragma.name.upper()}_': pragma for pragma in _pragmas}

LC_TEMPLATE = '''
class Solution:
    {entrypoint} = staticmethod({export})
'''

LC_SKIP_IMPORTS = frozenset(('pytest', 'ppcg'))
