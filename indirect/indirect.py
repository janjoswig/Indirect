from dataclasses import dataclass
import json
import os.path
import pathlib
from typing import Type, Union
from weakref import proxy


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
                "ignore_keyp": obj.ignore_keyp,
                "_type": "indirect.Content"
                }
            return serialisable

        if isinstance(obj, Abstraction):
            serialisable = {
                "alias": obj.alias,
                "path": obj.path,
                "_type": "indirect.Abstraction"
                }
            return serialisable

        return super().default(self, obj)


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
                self._project,
                dct["ingore_keyp"]
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

    def __str__(self):
        n_next = len(self.next) if self.next is not None else None
        n_content = len(self.content) if self.content is not None else None
        str_repr = (
            f"{type(self).__name__}\n"
            f"    alias:    {self.alias}\n"
            f"    path:     {self.path}\n"
            f"    next:     {n_next}\n"
            f"    content:  {n_content}"
        )
        return str_repr

    def __repr__(self):
        next_str_reprs = (
            [str(x) for x in self.next]
            if self.next is not None else None
            )
        content_str_reprs = (
            [str(x) for x in self.content]
            if self.content is not None else None
            )
        obj_repr = {
            "alias": self.alias,
            "path":  self.path,
            "next": next_str_reprs,
            "content": content_str_reprs
            }
        return str(obj_repr)


class KeyPath(list):
    def __init__(self, iterable=(), /):
        if isinstance(iterable, str):
            super().__init__(self.from_string(iterable))
        else:
            super().__init__(str(k) for k in iterable)

    @classmethod
    def from_string(cls, s):
        as_list = s.split(".")
        if len(as_list) == 1 and as_list[0] == "":
            as_list = []
        return cls(as_list)

    def to_string(self):
        return ".".join(self)


class View(list):

    def __init__(self, iterable=(), /):
        if isinstance(iterable, dict):
            super().__init__(self.from_dict(iterable))
        elif isinstance(iterable, str):
            super().__init__([iterable])
        else:
            super().__init__(KeyPath(x) for x in iterable)

    @classmethod
    def from_dict(cls, dct):

        def decent(d, keyp=None):
            if keyp is None:
                keyp = []

            for key in d:
                keyp_ = keyp + [key]
                if (d[key] is None) or (len(d[key]) == 0):
                    yield keyp_
                else:
                    yield from decent(d[key], keyp=keyp_)

        return cls(decent(dct))

    def to_dict(self):
        dct = {}
        for keyp in self:
            d_ = dct
            for key in keyp:
                if key not in d_:
                    d_[key] = {}
                d_ = d_[key]

        return dct


class Project:
    def __init__(self, alias=None, file=None):
        self.alias = alias
        self.file = file

        self.abstractions = Abstraction("", "")
        # self.abstractions.next = {"": proxy(self.abstractions)}
        self.a = self.abstractions

        self.views = {}
        self.v = self.views

        self.source = {
            "home": str(pathlib.Path().absolute()),
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

    def save(self):
        pass

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

    def add_abstraction(self, alias, *, path=None, view=None):
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

        view = self.check_view(view)

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

    def check_view(self, view):
        if view is None:
            view = View([[]])
        elif isinstance(view, str):
            try:
                view = self.views[view]
            except KeyError:
                raise LookupError("Could not find view")
        elif not isinstance(view, View):
            view = View(view)

        return view

    def rm_abstraction(self, alias, view):

        view = self.check_view(view)

        for keyp in view:
            if isinstance(keyp, str):
                keyp = KeyPath.from_string(keyp)

            last_a = self.decent_keyp(keyp)
            assert isinstance(last_a, Abstraction)

            _ = last_a.next.pop(alias)

    def add_content(
            self, alias, filename, *, cpath='',
            source="home", check=False, desc=None, kind=None, hash=None,
            tags=None, ignore_keyp=False, view=None):

        view = self.check_view(view)

        for keyp in view:
            if isinstance(keyp, str):
                keyp = KeyPath.from_string(keyp)

            last_a = self.decent_keyp(keyp)
            assert isinstance(last_a, Abstraction)

            c = Content(
                alias,
                filename.format(*keyp),
                cpath,
                keyp,
                source,
                None,      # Implement existence check
                desc,
                kind,
                tags,
                proxy(self),
                ignore_keyp
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
            self, keyp: Type[KeyPath]
            ) -> Union[Type["Abstraction"], Type["Content"]]:
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

    def eval_keyp(self, keyp: Type[KeyPath]) -> Type[pathlib.Path]:
        a = self.abstractions
        keyp_eval = pathlib.Path()
        for key in keyp:
            try:
                a = a.next[key]
            except (KeyError, TypeError):
                try:
                    a = a.content[key]
                except (KeyError, TypeError):
                    raise LookupError("Invalid KeyPath")
            finally:
                if isinstance(a, Abstraction):
                    keyp_eval = keyp_eval / os.path.expandvars(a.path)
                elif isinstance(a, Content):
                    keyp_eval = keyp_eval / (
                        f"{os.path.expandvars(a.cpath)}/"
                        f"{a.filename}"
                        )

        return keyp_eval

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

    def __repr__(self):
        obj_repr = (
            f"{type(self).__name__}"
            f"(alias={self.alias!r}, file={self.file!r})"
            )

        return obj_repr

    def __str__(self):
        str_repr = (
            f"{type(self).__name__}\n"
            f"    alias:  {self.alias!r}\n"
            f"    file:   {self.file!r}"
            )
        return str_repr


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
    ignore_keyp: bool = False  # Do not consider keyp for fullpath

    @property
    def fullpath(self):
        if self.project is None:
            fullpath_ = pathlib.Path(
                f"{os.path.expandvars(self.cpath)}/"
                f"{self.filename}"
                )
        else:
            if not self.ignore_keyp:
                keyp_eval = self.project.eval_keyp(self.keyp)
            else:
                keyp_eval = ""

            fullpath_ = pathlib.Path(
                f"{os.path.expandvars(self.project.source[self.source])}/"
                f"{keyp_eval}/"
                f"{os.path.expandvars(self.cpath)}/"
                f"{self.filename}"
                )

        return fullpath_

    def __repr__(self):
        obj_repr = (
            f"{type(self).__name__}("
            f"alias={self.alias!r}, "
            f"filename={self.filename!r}, "
            f"cpath={self.cpath!r}, "
            f"keyp={self.keyp!r}, "
            f"source={self.source!r}, "
            f"exists={self.exists!r}, "
            f"desc={self.desc!r}, "
            f"kind={self.kind!r}', "
            f"tags={self.tags!r}, "
            f"project={self.project.__repr__()}, "
            f"ignore_keyp={self.ignore_keyp!r})"
            )

        return obj_repr

    def __str__(self):
        str_repr = (
            f"{type(self).__name__}\n"
            f"    alias:        {self.alias!r}\n"
            f"    filename:     {self.filename!r}\n"
            f"    cpath:        {self.cpath!r}\n"
            f"    keyp:         {self.keyp!r}\n"
            f"    source:       {self.source!r}\n"
            f"    exists:       {self.exists!r}\n"
            f"    desc:         {self.desc!r}\n"
            f"    kind:         {self.kind!r}\n"
            f"    tags:         {self.tags!r}\n"
            f"    project:      {self.project!s}\n"
            f"    ignore keyp:  {self.ignore_keyp!r}"
            )

        return str_repr
