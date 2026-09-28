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
RESERVED = frozenset("true false is equals not and or if then for every there exists believes must eventually no".split())
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


def _entry_fields(entry, required, *, path, negative=False, regulated=False):
    # Optional display metadata is identity-bound, but never executable syntax.
    fields = set(required)
    if type(entry) is dict and "verbalisation" in entry:
        fields.add("verbalisation")
    if negative and type(entry) is dict and "negative_verbalisation" in entry:
        fields.add("negative_verbalisation")
    if regulated and type(entry) is dict and "regulated" in entry:
        fields.add("regulated")
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
    regulated: "RegulatedDecl | None" = None
    functional: bool | None = None
    total: bool | None = None
    defined: bytes | None = None
    argument_units: object = None


@dataclass(frozen=True, slots=True)
class RegulatedDecl:
    role: str
    default: str
    act: str | None = None
    permission: str | None = None


def _regulated(raw, args, name):
    if type(raw) is not dict or "role" not in raw or "default" not in raw:
        raise VEError(f"InvalidInput: regulated declaration {name} needs role and default")
    role, default = raw["role"], raw["default"]
    if role not in ("permission", "obligation", "plain") or default not in ("deny", "allow"):
        raise VEError(f"InvalidInput: invalid regulated role or default for {name}")
    required = {"role", "default"} | ({"act"} if role != "plain" else set())
    allowed = required | ({"permission"} if role == "obligation" else set())
    if set(raw) - allowed or not required <= set(raw):
        raise VEError(f"InvalidInput: invalid regulated fields for {name}")
    act = None
    if role != "plain":
        act = " ".join(raw["act"].split()) if type(raw["act"]) is str else ""
        slots = re.findall(r"\{([0-9]+)\}", act)
        words = re.sub(r"\{[0-9]+\}", "slot", act).split()
        if (len(act) > 80 or not act.startswith("{0} ")
                or slots != [str(i) for i in range(len(args))]
                or len(words) < 2 or not all(re.fullmatch(r"[A-Za-z][A-Za-z'-]*", w) for w in words)
                or any(w.lower() in RESERVED for w in words if w != "slot")):
            raise VEError(f"InvalidInput: invalid act phrase for {name}")
    permission = raw.get("permission")
    if permission is not None and type(permission) is not str:
        raise VEError(f"InvalidInput: invalid permission dual for {name}")
    return RegulatedDecl(role, default, act, permission)


@dataclass(frozen=True, slots=True)
class ConstantDecl:
    sort: str
    description: str | None
    unit: str | None = None
    verbalisation: str | None = None


@dataclass(frozen=True, slots=True, init=False)
class Environment:
    language: str
    profile: str | None
    profiles: tuple[str, ...]
    spec_revision: str
    sorts: object
    predicates: object
    constants: object
    unit_schema: str | None
    units: object

    def __init__(self, data):
        canonical_json(data)  # Check size, Unicode, and the restricted wire subset.
        language = data.get("language") if type(data) is dict else None
        modern = language in (CLOSURE_LANGUAGE, profile_registry.LANGUAGE)
        closure = language == CLOSURE_LANGUAGE
        route = language == profile_registry.LANGUAGE
        extended = type(data) is dict and ("unit_schema" in data or "units" in data)
        if extended and (not route or "unit_schema" not in data or "units" not in data):
            raise UnsupportedProfile("unit_schema and units require the ve.core@0.2 quantity route together")
        require_fields(data, {"language", "profiles" if modern else "profile", "spec_revision", "vocabulary"}
                       | ({"unit_schema", "units"} if extended else set()))
        order = False
        if route:
            family = profile_registry.checker_family(data["profiles"])
            if data["spec_revision"] != profile_registry.SPEC_REVISION:
                raise UnsupportedProfile(f"Unsupported specification revision {data['spec_revision']}")
            order = family == "order"
            if extended and not {"order@0", "time@0"} <= set(data["profiles"]):
                raise UnsupportedProfile("ve-units@1 requires order@0 and time@0")
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
        if extended:
            from .units import validate_units
            units = validate_units(data["unit_schema"], data["units"])
        else:
            units = None
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
            flagged = type(entry) is dict and ("functional" in entry or "total" in entry)
            if flagged and "defined" in entry:
                raise UnsupportedProfile("Defined predicates cannot carry functional or total flags")
            defined = route and "definitions@0" in data["profiles"] and type(entry) is dict and "defined" in entry
            fields = {"arguments", "description"}
            if extended and type(entry) is dict and "argument_units" in entry:
                fields.add("argument_units")
            if defined:
                fields.add("defined")
            if flagged:
                if not route or "data@0" not in data["profiles"]:
                    raise UnsupportedProfile("Predicate flags require data@0")
                fields |= {key for key in ("functional", "total") if key in entry}
            _entry_fields(entry, fields, path=f"/vocabulary/predicates/{name}",
                          negative=True, regulated=route and "norms@0" in data["profiles"])
            if "regulated" in entry and defined:
                raise VEError(f"RegulatedDefinedPredicate: {name}")
            if "regulated" in entry and flagged:
                raise VEError(f"RegulatedFlag: {name}")
            args = entry["arguments"]
            maximum_arity = 6 if route and "nary@0" in data["profiles"] else 2
            if type(args) is not list or not 1 <= len(args) <= maximum_arity:
                raise VEError(f"Predicate arguments must be an array of one to {maximum_arity} sort identifiers")
            for sort in args:
                if type(sort) is not str or (sort not in sorts and not (order and sort == INT_SORT)
                                             and not (route and "data@0" in data["profiles"] and sort == STRING_SORT)):
                    raise UnknownSymbol(f"Undeclared predicate argument sort: {sort!r}")
            argument_units = {}
            if "argument_units" in entry:
                from .units import validate_slot_units
                argument_units = validate_slot_units(entry["argument_units"], args, units)
            if flagged and len(args) != 2:
                raise VEError("Functional and total flags require a binary predicate")
            if flagged and INT_SORT in args:
                raise UnsupportedProfile("Data flags on $int slots are not supported")
            if order and route and "data@0" in data["profiles"] and (flagged or STRING_SORT in args):
                raise UnsupportedProfile("Data attributes on the order family are not enabled")
            for flag in ("functional", "total"):
                if flag in entry and type(entry[flag]) is not bool:
                    raise VEError(f"{flag} must be a Boolean")
            verbalisation = _verbalisation(entry["verbalisation"]) if "verbalisation" in entry else None
            negative = (_verbalisation(entry["negative_verbalisation"])
                        if "negative_verbalisation" in entry else None)
            regulated = _regulated(entry["regulated"], args, name) if "regulated" in entry else None
            if defined:
                payload = entry["defined"]
                require_fields(payload, {"arguments", "body"}, path=f"/vocabulary/predicates/{name}/defined")
                if payload["arguments"] != args:
                    raise VEError(f"Definition {name!r} arguments differ from its declaration")
            predicates[name] = PredicateDecl(tuple(args), _description(entry["description"]),
                                             verbalisation, negative, regulated,
                                             entry.get("functional"), entry.get("total"),
                                             canonical_json(entry["defined"]) if defined else None,
                                             MappingProxyType(argument_units))
        regulated_names = [n for n, p in predicates.items() if p.regulated is not None]
        if len(regulated_names) > 64:
            raise ResourceLimit("regulated predicates")
        acts = {}
        for name in regulated_names:
            decl = predicates[name]
            reg = decl.regulated
            if reg.role == "plain":
                continue
            key = (decl.arguments, reg.act, reg.role)
            if key in acts:
                raise VEError(f"DuplicateActRole: {reg.role}, {reg.act}")
            acts[key] = name
        linked = set()
        for name in regulated_names:
            decl = predicates[name]
            reg = decl.regulated
            if reg.role != "obligation":
                continue
            expected = acts.get((decl.arguments, reg.act, "permission"))
            if reg.permission is None:
                if expected is not None:
                    raise VEError(f"MissingPermissionDual: {name}, {expected}")
                continue
            target = predicates.get(reg.permission)
            if target is None or target.regulated is None or target.regulated.role != "permission":
                raise VEError(f"MissingPermissionDual: {name}, {reg.permission}")
            if decl.arguments != target.arguments:
                raise VEError(f"DualSortMismatch: {name}, {reg.permission}")
            if reg.act != target.regulated.act:
                raise VEError(f"DualActMismatch: {name}, {reg.permission}")
            if reg.permission in linked:
                raise VEError(f"DuplicateActRole: obligation, {reg.act}")
            linked.add(reg.permission)
        for name, entry in vocab["constants"].items():
            literal = (route and type(entry) is dict and entry.get("sort") == STRING_SORT)
            has_unit = extended and type(entry) is dict and "unit" in entry
            has_words = extended and type(entry) is dict and "verbalisation" in entry
            require_fields(entry, {"sort"} | ({"description"} if not literal or "description" in entry else set())
                           | ({"unit"} if has_unit else set()) | ({"verbalisation"} if has_words else set()),
                           path=f"/vocabulary/constants/{name}")
            sort = entry["sort"]
            if type(sort) is not str or (sort not in sorts and not (order and sort == INT_SORT)
                                          and not (route and sort == STRING_SORT)):
                raise UnknownSymbol(f"Undeclared constant sort: {sort!r}")
            if has_unit:
                from .units import validate_tag
                if sort != INT_SORT:
                    raise VEError(f"Unit on non-integer constant {name}")
                validate_tag(entry["unit"], units)
            constants[name] = ConstantDecl(sort, _description(entry["description"])
                                           if "description" in entry else None,
                                           entry.get("unit") if has_unit else None,
                                           _verbalisation(entry["verbalisation"]) if has_words else None)
        if route and sum(decl.sort == STRING_SORT for decl in constants.values()) > 64:
            raise ResourceLimit("At most 64 declared $string literals")
        for field, value in (("language", data["language"]), ("profile", None if modern else PROFILE),
                             ("profiles", tuple(data["profiles"]) if route else
                              (ORDER_PROFILES if order else CLOSURE_PROFILES) if closure else (PROFILE,)),
                             ("spec_revision", data["spec_revision"]),
                             ("sorts", MappingProxyType(sorts)), ("predicates", MappingProxyType(predicates)),
                             ("constants", MappingProxyType(constants)),
                             ("unit_schema", data["unit_schema"] if extended else None),
                             ("units", MappingProxyType(units) if extended else None)):
            object.__setattr__(self, field, value)
        if any(decl.defined is not None for decl in predicates.values()):
            from .definitions import compile_definitions
            compile_definitions(self, self.definition_entries, version=self.environment_id)

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
            if declaration.regulated is not None:
                reg = declaration.regulated
                entry["regulated"] = {"role": reg.role, "default": reg.default,
                                      **({"act": reg.act} if reg.act is not None else {}),
                                      **({"permission": reg.permission} if reg.permission is not None else {})}
            if declaration.functional is not None:
                entry["functional"] = declaration.functional
            if declaration.total is not None:
                entry["total"] = declaration.total
            if declaration.defined is not None:
                entry["defined"] = loads_json(declaration.defined)
            if declaration.argument_units:
                entry["argument_units"] = dict(declaration.argument_units)
            return entry

        return {"language": self.language, **({"profiles": list(self.profiles)} if self.profile is None else {"profile": self.profile}), "spec_revision": self.spec_revision,
                "vocabulary": {"sorts": {k: sort_entry(v) for k, v in self.sorts.items()},
                               "predicates": {k: predicate_entry(v) for k, v in self.predicates.items()},
                               "constants": {k: {"sort": v.sort, **({"description": v.description}
                                                                      if v.description is not None else {}),
                                                 **({"unit": v.unit} if v.unit is not None else {}),
                                                 **({"verbalisation": v.verbalisation}
                                                    if v.verbalisation is not None else {})}
                                             for k, v in self.constants.items()}},
                **({"unit_schema": self.unit_schema, "units": dict(self.units)}
                   if self.unit_schema is not None else {})}

    @property
    def closure(self):
        return "closure@0" in self.profiles

    @property
    def definition_entries(self):
        return {name: loads_json(decl.defined) for name, decl in self.predicates.items()
                if decl.defined is not None}

    @property
    def order(self):
        return "order@0" in self.profiles

    @property
    def model_sorts(self):
        return (*self.sorts, *((STRING_SORT,) if any(d.sort == STRING_SORT for d in self.constants.values())
                or any(STRING_SORT in d.arguments for d in self.predicates.values()) else ()))

    @property
    def identity_version(self):
        # Domain-separated before any order meaning_id was minted.
        if self.language == profile_registry.LANGUAGE:
            return "v0.2:" + ",".join(self.profiles)
        return "v0.1-order" if self.order else "v0.1" if self.closure else "v0"

    @property
    def environment_id(self):
        return digest(f"ve-environment-{self.identity_version}\n", self.to_dict())
