from dataclasses import dataclass
import json
from typing import ClassVar, List
from weakref import proxy, ProxyType


@dataclass
class Content:
    alias: str          # Name as stored in project
    filename: str       # Actual name of the file
    cpath: str          # Path snippet inserted between keyp and filename
    keyp: list          # Key trajectory through Abstractions dict
    source: str         # Root of the tree in which this file lies
    exists: bool        # Existence indicator
    desc: str           # String, description
    kind: str           # Binary, txt? Used if filename has no extension
    # _hash:            # Hash to track file modification
    tags: list          # List of keyword identifiers
    project: ProxyType  # Associated project


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
