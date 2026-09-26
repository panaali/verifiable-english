"""Immutable local vocabulary; descriptions contribute to artifact identity."""
from dataclasses import dataclass
import re
from types import MappingProxyType

from .errors import DuplicateDeclaration, ResourceLimit, UnknownSymbol, UnsupportedProfile, VEError
from .limits import MAX_IDENTIFIER_BYTES, MAX_PREDICATES, MAX_SORTS
from .wire import canonical_json, digest, loads_json, require_fields
from . import profiles as profile_registry

LANGUAGE = "ve.core@0"
PROFILE = "relational-fol@0"
SPEC_REVISION = "ve-v0-draft-2026-09-20"
CLOSURE_LANGUAGE = "ve.core@0.1"
CLOSURE_PROFILES = ("closure@0", PROFILE)
CLOSURE_REVISION = "ve-v0.1-closure-2026-09-21"
# order@0: linear integer comparisons. `$int` is the reserved built-in integer
# sort. It is not an identifier, so no vocabulary can declare, enumerate or
# quantify over it; it may appear only as a predicate argument or constant sort
# in an order environment. Combined closure@0 x order@0 is rejected.
ORDER_LANGUAGE = CLOSURE_LANGUAGE
ORDER_PROFILES = ("order@0", PROFILE)
ORDER_REVISION = "ve-v0.1-order-2026-09-22"
INT_SORT = "$int"
STRING_SORT = "$string"
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


def _verbalisation(value):
    if type(value) is not str or not value:
        raise VEError("Verbalisations must be nonempty strings")
    if len(value) > 256:
        raise ResourceLimit("Verbalisation exceeds 256 characters")
    return value


def _entry_fields(entry, required, *, path, negative=False):
    # Optional display metadata is identity-bound, but never executable syntax.
    fields = set(required)
    if type(entry) is dict and "verbalisation" in entry:
        fields.add("verbalisation")
    if negative and type(entry) is dict and "negative_verbalisation" in entry:
        fields.add("negative_verbalisation")
    require_fields(entry, fields, path=path)


@dataclass(frozen=True, slots=True)
class SortVerbalisation:
    singular: str
    plural: str


@dataclass(frozen=True, slots=True)
class SortDecl:
    description: str
    verbalisation: SortVerbalisation | None = None


@dataclass(frozen=True, slots=True)
class PredicateDecl:
    arguments: tuple[str, ...]
    description: str
    verbalisation: str | None = None
    negative_verbalisation: str | None = None


@dataclass(frozen=True, slots=True)
class ConstantDecl:
    sort: str
    description: str | None


@dataclass(frozen=True, slots=True, init=False)
class Environment:
    language: str
    profile: str | None
    profiles: tuple[str, ...]
    spec_revision: str
    sorts: object
    predicates: object
    constants: object

    def __init__(self, data):
        canonical_json(data)  # Check size, Unicode, and the restricted wire subset.
        language = data.get("language") if type(data) is dict else None
        modern = language in (CLOSURE_LANGUAGE, profile_registry.LANGUAGE)
        closure = language == CLOSURE_LANGUAGE
        route = language == profile_registry.LANGUAGE
        require_fields(data, {"language", "profiles" if modern else "profile", "spec_revision", "vocabulary"})
        order = False
        if route:
            family = profile_registry.checker_family(data["profiles"])
            if data["spec_revision"] != profile_registry.SPEC_REVISION:
                raise UnsupportedProfile(f"Unsupported specification revision {data['spec_revision']}")
            order = family == "order"
        elif closure:
            if (data["profiles"], data["spec_revision"]) == (list(ORDER_PROFILES), ORDER_REVISION):
                order = True
            elif data["profiles"] != list(CLOSURE_PROFILES) or data["spec_revision"] != CLOSURE_REVISION:
                raise UnsupportedProfile("Unsupported profiles or specification revision"
                                         + (" (closure@0 x order@0 is not supported)"
                                            if type(data["profiles"]) is list
                                            and {"closure@0", "order@0"} <= set(data["profiles"]) else ""))
        elif (data["language"], data["profile"], data["spec_revision"]) != (LANGUAGE, PROFILE, SPEC_REVISION):
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
            path = f"/vocabulary/sorts/{name}"
            _entry_fields(entry, {"description"}, path=path)
            verbalisation = None
            if "verbalisation" in entry:
                raw = entry["verbalisation"]
                require_fields(raw, {"singular", "plural"}, path=path + "/verbalisation")
                verbalisation = SortVerbalisation(_verbalisation(raw["singular"]),
                                                  _verbalisation(raw["plural"]))
            sorts[name] = SortDecl(_description(entry["description"]), verbalisation)
        for name, entry in vocab["predicates"].items():
            _entry_fields(entry, {"arguments", "description"}, path=f"/vocabulary/predicates/{name}",
                          negative=True)
            args = entry["arguments"]
            maximum_arity = 6 if route and "nary@0" in data["profiles"] else 2
            if type(args) is not list or not 1 <= len(args) <= maximum_arity:
                raise VEError(f"Predicate arguments must be an array of one to {maximum_arity} sort identifiers")
            for sort in args:
                if type(sort) is not str or (sort not in sorts and not (order and sort == INT_SORT)):
                    raise UnknownSymbol(f"Undeclared predicate argument sort: {sort!r}")
            verbalisation = _verbalisation(entry["verbalisation"]) if "verbalisation" in entry else None
            negative = (_verbalisation(entry["negative_verbalisation"])
                        if "negative_verbalisation" in entry else None)
            predicates[name] = PredicateDecl(tuple(args), _description(entry["description"]),
                                             verbalisation, negative)
        for name, entry in vocab["constants"].items():
            literal = (route and type(entry) is dict and entry.get("sort") == STRING_SORT)
            require_fields(entry, {"sort"} | ({"description"} if not literal or "description" in entry else set()),
                           path=f"/vocabulary/constants/{name}")
            sort = entry["sort"]
            if type(sort) is not str or (sort not in sorts and not (order and sort == INT_SORT)
                                          and not (route and sort == STRING_SORT)):
                raise UnknownSymbol(f"Undeclared constant sort: {sort!r}")
            constants[name] = ConstantDecl(sort, _description(entry["description"])
                                           if "description" in entry else None)
        if route and sum(decl.sort == STRING_SORT for decl in constants.values()) > 64:
            raise ResourceLimit("At most 64 declared $string literals")
        for field, value in (("language", data["language"]), ("profile", None if modern else PROFILE),
                             ("profiles", tuple(data["profiles"]) if route else
                              (ORDER_PROFILES if order else CLOSURE_PROFILES) if closure else (PROFILE,)),
                             ("spec_revision", data["spec_revision"]),
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
        def sort_entry(declaration):
            entry = {"description": declaration.description}
            if declaration.verbalisation is not None:
                entry["verbalisation"] = {"singular": declaration.verbalisation.singular,
                                           "plural": declaration.verbalisation.plural}
            return entry

        def predicate_entry(declaration):
            entry = {"arguments": list(declaration.arguments), "description": declaration.description}
            if declaration.verbalisation is not None:
                entry["verbalisation"] = declaration.verbalisation
            if declaration.negative_verbalisation is not None:
                entry["negative_verbalisation"] = declaration.negative_verbalisation
            return entry

        return {"language": self.language, **({"profiles": list(self.profiles)} if self.profile is None else {"profile": self.profile}), "spec_revision": self.spec_revision,
                "vocabulary": {"sorts": {k: sort_entry(v) for k, v in self.sorts.items()},
                               "predicates": {k: predicate_entry(v) for k, v in self.predicates.items()},
                               "constants": {k: {"sort": v.sort, **({"description": v.description}
                                                                      if v.description is not None else {})}
                                             for k, v in self.constants.items()}}}

    @property
    def closure(self):
        return "closure@0" in self.profiles

    @property
    def order(self):
        return "order@0" in self.profiles

    @property
    def model_sorts(self):
        return (*self.sorts, *((STRING_SORT,) if any(d.sort == STRING_SORT for d in self.constants.values()) else ()))

    @property
    def identity_version(self):
        # Domain-separated before any order meaning_id was minted.
        if self.language == profile_registry.LANGUAGE:
            return "v0.2:" + ",".join(self.profiles)
        return "v0.1-order" if self.order else "v0.1" if self.closure else "v0"

    @property
    def environment_id(self):
        return digest(f"ve-environment-{self.identity_version}\n", self.to_dict())
