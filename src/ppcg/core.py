import ast
from dataclasses import dataclass
from itertools import compress
from pathlib import Path
from typing import List, Tuple

from .constants import LC_PRAGMAS, LC_SKIP_IMPORTS, LC_TEMPLATE, SpanType
from .utils import check_keys, format_contents


@dataclass
class LeetcodeSolution:
    content: str
    export: str
    entrypoint: str
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
                entrypoints: List[ast.Name] = assign_node.targets  # type: ignore[assignment]
                lhs = ', '.join(entrypoint.id for entrypoint in entrypoints)
                if lhs.startswith('_LC_') and lhs.endswith('_'):
                    spans.append(
                        (
                            SpanType.PRAGMA,
                            node.lineno,
                            node.end_lineno or node.lineno,
                        )
                    )
                    try:
                        rhs = ast.literal_eval(assign_node.value)
                        data[lhs] = rhs
                    except ValueError:
                        pass

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

            # Generalize skip logic
            elif isinstance(node, ast.Import):
                i_node: ast.Import = node
                for alias in i_node.names:
                    if alias.name in LC_SKIP_IMPORTS:
                        break
                else:
                    continue

                spans.append(
                    (
                        SpanType.IMPORT,
                        node.lineno,
                        node.end_lineno or node.lineno,
                    )
                )

            elif isinstance(node, ast.ImportFrom):
                if_node: ast.ImportFrom = node
                if not if_node.module:
                    continue
                first_part = if_node.module.split('.')[0]
                if first_part not in LC_SKIP_IMPORTS:
                    continue

                spans.append(
                    (
                        SpanType.IMPORT,
                        node.lineno,
                        node.end_lineno or node.lineno,
                    )
                )

        # END BODY LOOP

        missing = check_keys(
            data,
            (key for key, pragma in LC_PRAGMAS.items() if pragma.required),
        )
        if missing:
            raise ValueError(
                'Missing required pragma: {}'.format(', '.join(missing))
            )

        return cls(
            content=content,
            export=data['_LC_EXPORT_'],
            entrypoint=data['_LC_ENTRYPOINT_'],
            specs=data.get('_LC_SPEC_', []),
            spans=spans,
        )

    def _adapter(self):
        return LC_TEMPLATE.format(
            entrypoint=self.entrypoint, export=self.export
        )

    def serialize(
        self, imports=True, pragmas=True, tests=True, adapter=False
    ) -> str:
        # List[Tuple[SpanType, int, int]]: (type, start, end)
        # Non-overlapping spans of lines to remove, inclusive
        # 1-based numbering
        cats = set()
        if not imports:
            cats.add(SpanType.IMPORT)
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
