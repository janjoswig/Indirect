import json
import pytest

from indirect import indirect

CONTENT_CASES = [
    {},
    {"alias": "alias",
     "filename": "file.ext"},
]


class TestProject:
    def test_create(self):
        p = indirect.Project()


class TestContent:

    @pytest.mark.skip(reason="Superseeded")
    @pytest.mark.parametrize("kwargs", CONTENT_CASES)
    def test_create(self, kwargs):
        _ = indirect.Content(**kwargs)

    @pytest.mark.parametrize("kwargs", CONTENT_CASES)
    def test_encode(self, kwargs, data_regression):
        content = indirect.Content(**kwargs)
        data_regression.check(
            json.dumps(
                content,
                cls=indirect.ProjectEncoder,
                indent=4,
                )
            )

    @pytest.mark.skip(reason="No cases generated")
    # @pytest.mark.parametrize("dumped", DUMPED_CASES)
    def test_decode(self, dumped):
        json.loads(dumped, object_hook=indirect.ProjectDecoder())

    def test_fullpath(self):
        pass


class TestAbstraction:
    def test_add_abstraction(self):
        p = indirect.Project()
        p.add_abstraction("x")