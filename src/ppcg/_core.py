import ast
from dataclasses import dataclass
from itertools import compress
from pathlib import Path
from typing import List, NamedTuple, Tuple, Union

from ._constants import LC_PRAGMAS, LC_SKIP_IMPORTS, LC_TEMPLATE, SpanType
from .utils import check_keys, format_contents


class DecoratorInfo(NamedTuple):
    """
    Decorator information.

    Attrs:
        name: A string identifying the decorator. Not guaranteed to represent
            the entire decorator.
        lineno: The first line of the decorator
        end_lineno: The final line of the decorator
    """

    name: str
    lineno: int
    end_lineno: int


def extract_decorator_info(
    node: Union[ast.ClassDef, ast.FunctionDef]
) -> List[DecoratorInfo]:
    # FIXME: Add support for PEP-614
    names: List[str] = []

    for deco_expr in node.decorator_list:
        if isinstance(deco_expr, ast.Attribute):
            if isinstance(deco_expr.value, ast.Name):
                name: ast.Name = deco_expr.value
                names.append(DecoratorInfo(name.id, name.lineno, name.end_lineno))
        # TODO: Add support for Calls

    return names


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
        imports = {}

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

                skip = f_node.name.startswith('test')
                decos = extract_decorator_info(f_node)

                for deco in decos:
                    package = imports[deco.name].split('.')[0]
                    if package in LC_SKIP_IMPORTS:
                        skip = True
                        break

                if not skip:
                    continue

                span_start = f_node.lineno

                for deco in f_node.decorator_list:
                    if deco.lineno < span_start:
                        span_start = deco.lineno

                spans.append(
                    (SpanType.TEST, span_start, node.end_lineno or node.lineno)
                )

            elif isinstance(node, ast.ClassDef):
                c_node: ast.ClassDef = node
                skip = False

                decos = extract_decorator_info(c_node)
                for deco in decos:
                    package = imports[deco.name].split('.')[0]
                    if package in LC_SKIP_IMPORTS:
                        skip = True
                        break

                if not skip:
                    continue

                span_start = c_node.lineno

                for deco in c_node.decorator_list:
                    if deco.lineno < span_start:
                        span_start = deco.lineno

                spans.append(
                    (SpanType.TEST, span_start, node.end_lineno or node.lineno)
                )
            # Generalize skip logic
            elif isinstance(node, ast.Import):
                i_node: ast.Import = node

                for alias in i_node.names:
                    if alias.asname:
                        imports[alias.asname] = alias.name
                    else:
                        imports[alias.name] = alias.name

                    if alias.name.split('.')[0] in LC_SKIP_IMPORTS:
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

                # HACK: Leetcode doesn't like __future__ imports
                if not if_node.module == '__future__':

                    for alias in if_node.names:
                        if alias.asname:
                            imports[alias.name] = (
                                f'{if_node.module}.{alias.asname}'
                            )
                        else:
                            imports[alias.name] = (
                                f'{if_node.module}.{alias.name}'
                            )

                        if alias.name in LC_SKIP_IMPORTS:
                            break

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
