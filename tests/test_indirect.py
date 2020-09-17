import json
import pytest

from indirect import indirect


CONTENT_CASES = [
    (None, None, None, None, None, None, None, None, None, None),
]


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
