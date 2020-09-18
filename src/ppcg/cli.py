import os
import sys
from pathlib import Path
from tempfile import mkstemp
from typing import Any, Dict, Tuple

import pyperclip

from ._core import LeetcodeSolution
from .utils import format_contents

HELP = '''
Usage:
    {program} print <solution>
    {program} copy <solution>
    {program} help
'''

TEMPLATE_PATH = Path(__file__).parent.resolve() / '_template.py'


def print_help() -> int:
    print(HELP.format(program='ppcg', file=sys.stderr))
    return 0


def _command_print(*argv) -> str:
    if len(argv) != 1:
        print_help()
        raise SystemExit(1)

    solution = Path(argv[0])

    if not solution.exists():
        print(f'Solution {solution} not found', file=sys.stderr)
        raise SystemExit(1)

    result = LeetcodeSolution.parse(solution).serialize(
        imports=False,
        pragmas=False,
        tests=False,
        adapter=True,
        #
    )

    return result


def command_print(*argv) -> int:
    result = _command_print(*argv)

    print(result, end='')
    return 0


def command_copy(*argv: str) -> int:
    result = _command_print(*argv)

    pyperclip.copy(result)
    lines = sum(1 for c in result if c == '\n')
    print(f'Copied {lines} lines!', file=sys.stderr)
    return 0


def _command_generate(ctx: Dict['str', Any] = None) -> str:
    template = TEMPLATE_PATH.read_text()
    if ctx:
        return template.format_map(ctx)
    return template


def command_generate(*argv: str) -> int:
    if len(argv) > 1:
        return 1

    text = format_contents(_command_generate())
    if not len(argv):
        print(text, end='')
        return 0

    out = Path(argv[0]).resolve()

    fd, name = mkstemp(prefix='ppcg', text=True)
    try:
        with os.fdopen(fd, 'w+') as f:
            print(text, end='', file=f)
        os.replace(name, out)
    finally:
        try:
            os.close(fd)
        except OSError as e:
            pass

        if os.path.exists(name):
            os.unlink(name)

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

    if cmd == 'generate':
        return command_generate(*rest)

    print_help()
    return 0
