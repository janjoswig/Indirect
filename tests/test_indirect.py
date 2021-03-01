import inspect
import json
import pytest

from indirect import indirect


CONTENT_CASES = [
    ("no", {}),
    ("a", {
        "alias": "alias", "filename": "file.ext"
    }),
]

ABSTRACTION_CASES = [
    ("no", {}),
    ("a", {
        "alias": "system", "path": "system/setup"
    })
]


class TestProject:

    @pytest.mark.parametrize("caseid,kwargs", ABSTRACTION_CASES)
    def test_add_abstraction(self, caseid, kwargs):
        try:
            alias = kwargs.pop("alias")
        except KeyError:
            alias = None

        p = indirect.Project()
        p.add_abstraction("x")


class TestContent:

    @pytest.mark.skip(reason="Superseeded")
    @pytest.mark.parametrize("caseid,kwargs", CONTENT_CASES)
    def test_create(self, caseid, kwargs):
        _ = indirect.Content(**kwargs)

    @pytest.mark.parametrize("caseid,kwargs", CONTENT_CASES)
    def test_encode(self, caseid, kwargs, data_regression):
        try:
            alias = kwargs.pop("alias")
        except KeyError:
            alias = None

        content = indirect.Content(alias, **kwargs)

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

    @pytest.mark.parametrize("caseid,kwargs", ABSTRACTION_CASES)
    def test_create_abstraction(self, caseid, kwargs, file_regression):
        try:
            alias = kwargs.pop("alias")
        except KeyError:
            alias = None

        abstraction = indirect.Abstraction(alias, **kwargs)

        basename = f"{inspect.stack()[0][3]}_{caseid}"

        file_regression.check(
            f"{abstraction!s}", basename=f"{basename}_str"
            )
        file_regression.check(
            f"{abstraction!r}", basename=f"{basename}_repr"
            )
