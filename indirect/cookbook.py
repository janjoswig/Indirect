import pathlib
import re
from typing import Container, Iterator, Optional, Union


def get_dirs(
        path: Union[str, pathlib.Path] = '', *,
        prefix: str = '',
        regex: str = '*',
        suffix: str = '',
        exclude: Optional[Container[str]] = None) -> Iterator[str]:
    """Find all directories matching a pattern
    
    Args:
        path: Look for directories under this location.
        prefix: Directory names must start with this prefix.
        regex: Directory names (without prefix and suffix) must
            match this regular expression.
        suffix: Directory names must end with this suffix.
        exclude: List of directory names to ignore.
    """

    if exclude is None:
        exclude = set()

    pattern = f"{prefix}{regex}{suffix}"
    path_to_search = pathlib.Path(path)

    for match in path_to_search.iterdir():
        if not match.is_dir():
            continue

        if not re.search(pattern, match.stem):
            continue

        a = match.stem.lstrip(prefix).rstrip(suffix)

        if a in exclude:
            continue

        yield a
