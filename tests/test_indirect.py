import json
import pytest

from indirect import indirect


CONTENT_CASES = [
    (None, None, None, None, None, None, None, None, None, None),
]


class TestProject:
    def test_create(self):
        p = indirect.Project()

class TestContent:

    @pytest.mark.skip(reason="Superseeded")
    @pytest.mark.parametrize("args", CONTENT_CASES)
    def test_create(self, args):
        content = indirect.Content(*args)

    @pytest.mark.parametrize("args", CONTENT_CASES)
    def test_encode(self, args):
        content = indirect.Content(*args)
        json.dumps(content, cls=indirect.ProjectEncoder)

    @pytest.mark.skip(reason="No cases generated")
    # @pytest.mark.parametrize("dumped", DUMPED_CASES)
    def test_decode(self, dumped):
        json.loads(dumped, object_hook=indirect.ProjectDecoder())


class TestAbstraction:
    def test_add_abstraction(self):
        p = indirect.Project()
        p.add_abstraction("x")