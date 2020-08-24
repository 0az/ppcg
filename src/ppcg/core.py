import ast
from dataclasses import dataclass
from enum import Enum, auto
from itertools import compress
from pathlib import Path
from typing import List, Tuple

from .utils import check_keys, format_contents


class SpanType(Enum):
    PRAGMA = auto()
    TEST = auto()


LC_PRAGMAS = '_LC_ENTRYPOINT_', '_LC_TARGET_', '_LC_SPEC_'

LC_TEMPLATE = '''
class Solution:
    {target} = staticmethod({entrypoint})
'''


@dataclass
class LeetcodeSolution:
    content: str
    entrypoint: str
    target: str
    specs: List[str]
    spans: List[Tuple[SpanType, int, int]]

    @classmethod
    def parse(cls, solution: Path):
        content = solution.read_text()
        tree = ast.parse(content)
        data = {}
        spans: List[Tuple[SpanType, int, int]] = []

        for node in tree.body:
            # FIXME: Generalize the ast parsing
            # if isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
            #     assign_node: Union[ast.Assign, ast.AugAssign, ast.AnnAssign]
            if isinstance(node, ast.Assign):
                assign_node: ast.Assign = node
                targets: List[ast.Name] = assign_node.targets  # type: ignore[assignment]
                lhs = ', '.join(target.id for target in targets)
                if lhs in LC_PRAGMAS:
                    rhs = ast.literal_eval(assign_node.value)
                    data[lhs] = rhs
                    spans.append(
                        (
                            SpanType.PRAGMA,
                            node.lineno,
                            node.end_lineno or node.lineno,
                        )
                    )

            elif isinstance(node, ast.FunctionDef):
                f_node: ast.FunctionDef = node

                if not f_node.name.startswith('test'):
                    continue

                span_start = f_node.lineno

                for deco in f_node.decorator_list:
                    if deco.lineno < span_start:
                        span_start = deco.lineno
                spans.append(
                    (SpanType.TEST, span_start, node.end_lineno or node.lineno)
                )
        # END BODY LOOP

        missing = check_keys(data, LC_PRAGMAS)
        if missing:
            raise ValueError(
                'Missing required pragma: {}'.format(', '.join(missing))
            )

        return cls(
            content=content,
            entrypoint=data['_LC_ENTRYPOINT_'],
            target=data['_LC_TARGET_'],
            specs=data['_LC_SPEC_'],
            spans=spans,
        )

    def _adapter(self):
        return LC_TEMPLATE.format(
            target=self.target, entrypoint=self.entrypoint
        )

    def serialize(self, pragmas=True, tests=True, adapter=False) -> str:
        # List[Tuple[SpanType, int, int]]: (type, start, end)
        # Non-overlapping spans of lines to remove, inclusive
        # 1-based numbering
        cats = set()
        if not pragmas:
            cats.add(SpanType.PRAGMA)
        if not tests:
            cats.add(SpanType.TEST)

        if not cats:
            return format_contents(self.content)

        lines = self.content.splitlines(True)
        spans = self.spans
        spans.sort(key=lambda t: t[1:])

        mask = [True] * len(lines)

        cat: SpanType
        for cat, start, end in spans:
            if cat in cats:
                mask[start - 1 : end] = [False] * (end - start + 1)

        if adapter:
            lines.append(self._adapter())
            mask.append(True)

        content = ''.join(compress(lines, mask))
        return format_contents(content)
