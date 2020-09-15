import dataclasses
from dataclasses import *

__all__ = dataclasses.__all__  # type: ignore[attr-defined]

del dataclasses
