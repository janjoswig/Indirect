import os
import pathlib
import re
from typing import Container, Iterator, Optional, Union

from . import indirect


def get_dirs(
        path: Union[str, pathlib.Path] = '', *,
        prefix: str = '',
        regex: str = '.*',
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


def list_content_paths(project, view):
    view = project.check_view(view)

    print(f"{'key':<20}path (exists?)")
    print("=" * 100)

    for keyp in view:
        a = project[keyp]
        if isinstance(a, indirect.Abstraction):
            print(keyp.to_string())
            for alias, content in a.content.items():

                if not content.ignore_keyp:
                    keyp_eval = project.eval_keyp(keyp)
                else:
                    keyp_eval = ""

                fullpath_ = pathlib.Path(
                    f"{content.source}:"
                    f"{keyp_eval}/"
                    f"{os.path.expandvars(content.cpath)}/"
                    f"{content.filename}"
                )

                print(
                    f"  .{alias:<18}{fullpath_} "
                    f"({content.fullpath.is_file()})"
                    )
            print()

        elif isinstance(a, indirect.Content):

            if not a.ignore_keyp:
                keyp_eval = project.eval_keyp(keyp)
            else:
                keyp_eval = ""

            fullpath_ = pathlib.Path(
                f"{a.source}:"
                f"{keyp_eval}/"
                f"{os.path.expandvars(a.cpath)}/"
                f"{a.filename}"
            )

            print(
                f"{keyp.to_string():<20}{fullpath_}"
            )
