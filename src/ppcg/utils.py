from os import PathLike
from pathlib import Path
from typing import Any, Dict

import black
import toml

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
PYPROJECT = PROJECT_ROOT / 'pyproject.toml'


def load_pyproject(path: PathLike = PYPROJECT) -> Dict[str, Any]:
    return dict(toml.load(path))


def get_black_mode(config: Dict[str, Any]) -> black.Mode:
    black_config = config.get('tool', {}).get('black')

    if not black_config:
        return black.Mode()

    black_config = {k.replace('-', '_'): v for k, v in black_config.items()}
    if 'skip_string_normalization' in black_config:
        black_config['string_normalization'] = not black_config.pop(
            'skip_string_normalization'
        )

    return black.Mode(**black_config)


BLACK_MODE = get_black_mode(load_pyproject())


def format_contents(s: str) -> str:
    mode = get_black_mode(load_pyproject(PYPROJECT))
    try:
        return black.format_file_contents(s, fast=False, mode=mode)
    except black.NothingChanged:
        return s


def check_keys(data: Dict[str, Any], keys):
    missing = []
    for key in keys:
        if data.get(key) is None:
            missing.append(key)
    return missing
