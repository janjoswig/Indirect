from dataclasses import dataclass
import json
import os.path
import pathlib
from typing import ClassVar, List, Type, Union
from weakref import proxy, ProxyType


class ProjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Content):
            serialisable = {
                "alias": obj.alias,
                "filename": obj.filename,
                "cpath": obj.cpath,
                "keyp": obj.keyp,
                "source": obj.source,
                "exists": obj.exists,
                "desc": obj.desc,
                "kind": obj.kind,
                "tags": obj.tags,
                "_type": "indirect.Content"
                }
            return serialisable
        return super().default(self, obj)


class KeyPath(list):
    def __init__(self, iterable=(), /):
        if isinstance(iterable, str):
            return self.from_string(iterable)

        super().__init__(str(k) for k in iterable)

    @classmethod
    def from_string(cls, s):
        as_list = s.split(".")
        if len(as_list) == 1 and as_list[0] == "":
            as_list = []
        return cls(as_list)


class ProjectDecoder:

    def __init__(self, project=None):
        self._project = project

    def __call__(self, dct):
        try:
            _type = dct.pop("_type")
        except KeyError:
            _type = None

        if _type is None:
            return dct

        if _type == "indirect.Content":
            decoded = Content(
                dct["alias"],
                dct["filename"],
                dct["cpath"],
                dct["keyp"],
                dct["source"],
                dct["exists"],
                dct["desc"],
                dct["kind"],
                dct["tags"],
                self._project
                )
            return decoded

        return dct


class Abstraction:
    __slots__ = ["alias", "path", "previous", "next", "content", '__weakref__']

    def __init__(self, alias, path):
        self.alias = alias
        self.path = path
        self.previous = None
        self.next = None
        self.content = None


class View(list):

    def __init__(self, iterable=(), /):
        super().__init__(KeyPath(x) for x in iterable)


class Project:
    def __init__(self, alias=None, file=None):
        self.alias = alias
        self.file = file

        self.abstractions = Abstraction("", "")
        self.abstractions.next = {"": proxy(self.abstractions)}
        self.a = self.abstractions

        self.views = {}
        self.v = self.views

        self.source = {
            "home": pathlib.Path().absolute(),
            "default": pathlib.Path(),
        }

        if file is not None:
            self.load(file)

    def load(self, file=None, reinit=False):
        """Load project from file"""
        if reinit:
            self.__init__()

        self._set_project_file(file)

        with open(file) as file_:
            details = json.load(file_, object_hook=ProjectDecoder())
            self.abstractions.update(details["abstractions"])
            self.source.update(details["source"])
            self.views.update(details["views"])

    def _set_project_file(self, file):
        """Manage project file path"""
        if file is None:
            if self.file is not None:
                file = self.file
            else:
                file = pathlib.Path(
                    os.path.expandvars(self.source["home"])
                    ) / 'project.json'
        else:
            file = pathlib.Path(os.path.expandvars(file))

        file = file.absolute()

        self.file = file
        self.source = {
            "home": f"{file.parent}"
            }

    def add_abstraction(self, alias, path=None, *, view=None):
        """Add abstraction to abstractions

        Args:
            alias: Short identifier for the new abstraction.

        Keyword args:
            path: Actual path fragment represented by this abstraction.
                If `None`, will use ``alias``.
            view: List of KeyPath instances (or equivalents) under which
                the new abstraction should be added.
        """

        if path is None:
            path = alias

        if view is None:
            view = [[]]

        for keyp in view:
            if isinstance(keyp, str):
                keyp = KeyPath.from_string(keyp)

            last_a = self.decent_keyp(keyp)
            assert isinstance(last_a, Abstraction)

            a = Abstraction(alias, path)
            a.previous = proxy(last_a)

            if last_a.next is None:
                last_a.next = {}
            last_a.next[alias] = a

    def rm_abstraction(self, alias, view):

        if view is None:
            view = [[]]

        for keyp in view:
            if isinstance(keyp, str):
                keyp = KeyPath.from_string(keyp)

            last_a = self.decent_keyp(keyp)
            assert isinstance(last_a, Abstraction)

            _ = last_a.next.pop(alias)

    def add_content(
            self, alias, filename, *, cpath='',
            source="home", check=False, desc=None, kind=None, hash=None,
            tags=None, view=None):

        if view is None:
            view = [[]]

        for keyp in view:
            if isinstance(keyp, str):
                keyp = KeyPath.from_string(keyp)

            last_a = self.decent_keyp(keyp)
            assert isinstance(last_a, Abstraction)

            c = Content(
                alias,
                filename,
                cpath,
                keyp,
                source,
                None,      # Implement existence check
                desc,
                kind,
                tags,
                proxy(self)
                )

            if last_a.content is None:
                last_a.content = {}
            last_a.content[alias] = c

    def rm_content(self, alias, view=None):

        if view is None:
            view = [[]]

        for keyp in view:
            if isinstance(keyp, str):
                keyp = KeyPath.from_string(keyp)

            last_a = self.decent_keyp(keyp)
            assert isinstance(last_a, Abstraction)

            _ = last_a.content.pop(alias)

    def decent_keyp(
            self, keyp: Type[KeyPath]) -> Union[Type["Abstraction"], Type["Content"]]:
        a = self.abstractions
        for key in keyp:
            try:
                a = a.next[key]
            except (KeyError, TypeError):
                try:
                    return a.content[key]
                except (KeyError, TypeError):
                    raise LookupError("Invalid KeyPath")
        return a

    def __getitem__(self, keyp):
        if isinstance(keyp, str):
            keyp = KeyPath.from_string(keyp)
        return self.decent_keyp(keyp)

    def __setitem__(self, keyp, item):
        if isinstance(keyp, str):
            keyp = KeyPath.from_string(keyp)

        a = self.decent_keyp(keyp)
        assert isinstance(a, Abstraction)

        if isinstance(item, Content):
            if a.content is None:
                a.content = {}
            a.content[item.alias] = item

        elif isinstance(item, Abstraction):
            if a.next is None:
                a.next = {}
            a.next[item.alias] = item

        else:
            raise TypeError("Item must be of type Content or Abstraction")

@dataclass
class Content:
    alias: str         # Name as stored in project
    filename: str      # Actual name of the file
    cpath: str         # Path snippet inserted between keyp and filename
    keyp: list         # Key trajectory through Abstractions dict
    source: str        # Root of the tree in which this file lies
    exists: bool       # Existence indicator
    desc: str          # String, description
    kind: str          # Binary, txt? Used if filename has no extension
    # _hash:           # Hash to track file modification
    tags: list         # List of keyword identifiers
    project: Type["Project"]    # Associated project

    @property
    def fullpath(self):
        return
