import pytest

from indirect import cookbook


@pytest.mark.parametrize(
    "args,kwargs,expected",
    [
        ((), {"regex": "^[0-9]"}, []),
        ((), {
            "path": "tests/test_cookbook",
            "regex": "d[0-9]*$"
            }, ["d1", "d2", "d3"]),
        ((), {
            "path": "tests/test_cookbook",
            "regex": "d[0-9]*$",
            "exclude": {"d2"},
            }, ["d1", "d3"])
    ]
)
def test_get_dirs(args, kwargs, expected):
    found = cookbook.get_dirs(*args, **kwargs)

    assert expected == list(found)
