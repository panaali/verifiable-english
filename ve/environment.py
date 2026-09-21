"""Immutable local vocabulary; descriptions contribute to artifact identity."""
from dataclasses import dataclass
import re
from types import MappingProxyType

from .errors import DuplicateDeclaration, ResourceLimit, UnknownSymbol, UnsupportedProfile, VEError
from .limits import MAX_IDENTIFIER_BYTES, MAX_PREDICATES, MAX_SORTS
from .wire import canonical_json, digest, loads_json, require_fields

LANGUAGE = "ve.core@0"
PROFILE = "relational-fol@0"
SPEC_REVISION = "ve-v0-draft-2026-09-20"
RESERVED = frozenset("true false is equals not and or if then for every there exists believes must eventually".split())
_IDENTIFIER = re.compile(r"[a-z][a-z0-9_]*\Z", re.ASCII)


def valid_identifier(name) -> bool:
    return type(name) is str and len(name) <= MAX_IDENTIFIER_BYTES and _IDENTIFIER.fullmatch(name) is not None


def validate_identifier(name) -> str:
    if type(name) is str and len(name) > MAX_IDENTIFIER_BYTES:
        raise ResourceLimit("Identifier exceeds 64 ASCII bytes")
    if not valid_identifier(name):
        raise VEError(f"Invalid ASCII identifier: {name!r}")
    return name


def _description(value):
    if type(value) is not str or not value:
        raise VEError("Descriptions must be nonempty Unicode strings")
    return value


@dataclass(frozen=True, slots=True)
class SortDecl:
    description: str


@dataclass(frozen=True, slots=True)
class PredicateDecl:
    arguments: tuple[str, ...]
    description: str


@dataclass(frozen=True, slots=True)
class ConstantDecl:
    sort: str
    description: str


@dataclass(frozen=True, slots=True, init=False)
class Environment:
    language: str
    profile: str
    spec_revision: str
    sorts: object
    predicates: object
    constants: object

    def __init__(self, data):
        canonical_json(data)  # Check size, Unicode, and the restricted wire subset.
        require_fields(data, {"language", "profile", "spec_revision", "vocabulary"})
        if (data["language"], data["profile"], data["spec_revision"]) != (LANGUAGE, PROFILE, SPEC_REVISION):
            raise UnsupportedProfile("Unsupported language, semantic profile, or specification revision")
        vocab = data["vocabulary"]
        require_fields(vocab, {"sorts", "predicates", "constants"}, path="/vocabulary")
        for kind in ("sorts", "predicates", "constants"):
            if type(vocab[kind]) is not dict:
                raise VEError(f"{kind} must be an object")
        if len(vocab["sorts"]) > MAX_SORTS or len(vocab["predicates"]) > MAX_PREDICATES:
            raise ResourceLimit("Vocabulary exceeds sort or predicate limit")
        names = set()
        for kind in ("sorts", "predicates", "constants"):
            for name in vocab[kind]:
                validate_identifier(name)
                if name in names:
                    raise DuplicateDeclaration(f"Symbol {name!r} is declared in multiple categories")
                if name in RESERVED or re.fullmatch(r"x[0-9]+", name):
                    raise DuplicateDeclaration(f"Schema identifier {name!r} is reserved")
                names.add(name)
        sorts, predicates, constants = {}, {}, {}
        for name, entry in vocab["sorts"].items():
            require_fields(entry, {"description"}, path=f"/vocabulary/sorts/{name}")
            sorts[name] = SortDecl(_description(entry["description"]))
        for name, entry in vocab["predicates"].items():
            require_fields(entry, {"arguments", "description"}, path=f"/vocabulary/predicates/{name}")
            args = entry["arguments"]
            if type(args) is not list or len(args) not in (1, 2):
                raise VEError("Predicate arguments must be an array of one or two sort identifiers")
            for sort in args:
                if type(sort) is not str or sort not in sorts:
                    raise UnknownSymbol(f"Undeclared predicate argument sort: {sort!r}")
            predicates[name] = PredicateDecl(tuple(args), _description(entry["description"]))
        for name, entry in vocab["constants"].items():
            require_fields(entry, {"sort", "description"}, path=f"/vocabulary/constants/{name}")
            sort = entry["sort"]
            if type(sort) is not str or sort not in sorts:
                raise UnknownSymbol(f"Undeclared constant sort: {sort!r}")
            constants[name] = ConstantDecl(sort, _description(entry["description"]))
        for field, value in (("language", LANGUAGE), ("profile", PROFILE), ("spec_revision", SPEC_REVISION),
                             ("sorts", MappingProxyType(sorts)), ("predicates", MappingProxyType(predicates)),
                             ("constants", MappingProxyType(constants))):
            object.__setattr__(self, field, value)

    @classmethod
    def from_dict(cls, data):
        return cls(data)

    @classmethod
    def from_json(cls, data: str | bytes):
        return cls(loads_json(data))

    def to_dict(self):
        return {"language": self.language, "profile": self.profile, "spec_revision": self.spec_revision,
                "vocabulary": {"sorts": {k: {"description": v.description} for k, v in self.sorts.items()},
                               "predicates": {k: {"arguments": list(v.arguments), "description": v.description}
                                              for k, v in self.predicates.items()},
                               "constants": {k: {"sort": v.sort, "description": v.description}
                                             for k, v in self.constants.items()}}}

    @property
    def environment_id(self):
        return digest("ve-environment-v0\n", self.to_dict())
