import sys
from pathlib import Path
from typing import Tuple

import pyperclip

from .core import LeetcodeSolution

HELP = '''
Usage:
    {program} print <solution>
    {program} copy <solution>
    {program} help
'''


def print_help() -> int:
    print(HELP.format(program='ppcg', file=sys.stderr))
    return 0


def _command_print(*argv) -> Tuple[str, int]:
    if len(argv) != 3:
        print_help()
        return '', 1

    solution = Path(argv[2])

    if not solution.exists():
        print(f'Solution {solution} not found', file=sys.stderr)
        return '', 1

    result = LeetcodeSolution.parse(solution).serialize(
        pragmas=False, tests=False, adapter=True
    )

    return result, 0


def command_print(*argv) -> int:
    result, err = _command_print(*argv)

    if err:
        return err

    print(result, end='')
    return 0


def command_copy(*argv: str) -> int:
    result, err = _command_print(*argv)

    if err:
        return err

    pyperclip.copy(result)
    lines = sum(1 for c in result if c == '\n')
    print(f'Copied {lines} lines!', file=sys.stderr)
    return 0


def main():
    argv = sys.argv
    if len(argv) == 1:
        print_help()
        return 1

    cmd, *rest = argv[1:]
    cmd = cmd.casefold()

    if cmd == 'help':
        print_help()
        return 0

    if cmd == 'print':
        return command_print(*rest)

    if cmd == 'copy':
        return command_copy(*rest)

    print_help()
    return 0
