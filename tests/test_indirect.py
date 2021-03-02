import inspect
import json
import pytest

from indirect import indirect


CONTENT_CASES = [
    ("no", (), {}),
    ("a", ("alias", ), {
        "filename": "file.ext"
    }),
]

ABSTRACTION_CASES = [
    ("no", (), {}),
    ("a", ("system", ), {
        "path": "system/setup"
    })
]


class TestProject:

    def test_add_abstraction(self):

        p = indirect.Project()
        p.add_abstraction("s1")


class TestContent:

    @pytest.mark.parametrize("caseid,args,kwargs", CONTENT_CASES)
    def test_encode(self, caseid, args, kwargs, data_regression):

        content = indirect.Content(*args, **kwargs)

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

    @pytest.mark.parametrize("caseid,args,kwargs", ABSTRACTION_CASES)
    def test_create_abstraction(self, caseid, args, kwargs, file_regression):
        abstraction = indirect.Abstraction(*args, **kwargs)

        basename = f"{inspect.stack()[0][3]}_{caseid}"

        file_regression.check(
            f"{abstraction!s}", basename=f"{basename}_str"
            )
        file_regression.check(
            f"{abstraction!r}", basename=f"{basename}_repr"
            )

    def test_to_dict(self):
        abstraction = indirect.Abstraction("s1")
        print(abstraction.to_dict())
