"""Immutable local vocabulary; descriptions contribute to artifact identity."""
from collections.abc import Mapping
from dataclasses import dataclass, field
import re
from types import MappingProxyType

from .assurance import semantic_entry
from .errors import ResourceLimit, VEError
from .limits import MAX_IDENTIFIER_BYTES
from .wire import canonical_json, digest, loads_json
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


def listed_profiles(data) -> tuple[str, ...]:
    """The profiles named by environment JSON that may not be valid yet: `()`
    unless `profiles` is an array of strings. Routing that reads the profiles
    before the decoder runs uses this; the decoder rejects any other value
    (Lean's `profilesOf`)."""
    profiles = data.get("profiles") if type(data) is dict else None
    return tuple(profiles) if _string_array(profiles) else ()


def _string_array(value) -> bool:
    return type(value) is list and all(type(item) is str for item in value)


def valid_identifier(name) -> bool:
    return type(name) is str and len(name) <= MAX_IDENTIFIER_BYTES and _IDENTIFIER.fullmatch(name) is not None


def validate_identifier(name) -> str:
    if type(name) is str and len(name) > MAX_IDENTIFIER_BYTES:
        raise ResourceLimit("Identifier exceeds 64 ASCII bytes")
    if not valid_identifier(name):
        raise VEError(f"Invalid ASCII identifier: {name!r}")
    return name


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


class _ProfilePredicates(Mapping):
    """Lookup profile words without turning them into declared base tables.

    Enumeration deliberately exposes only declarations. This keeps source
    identity, models, and generated base vocabularies unchanged.
    """

    def __init__(self, declared, profile):
        self.declared = MappingProxyType(declared)
        self.profile = MappingProxyType(profile)

    def __getitem__(self, name):
        if name in self.profile:
            return self.profile[name]
        return self.declared[name]

    def __iter__(self):
        return iter(self.declared)

    def __len__(self):
        return len(self.declared)


@dataclass(frozen=True, slots=True)
class RegulatedDecl:
    role: str
    default: str
    act: str | None = None
    permission: str | None = None


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
    speech_acts: object
    unit_schema: str | None
    units: object
    reports: object
    rights: bytes | None
    alternatives: bytes | None
    risk: bytes | None
    _environment_id: str = field(repr=False, compare=False)

    @semantic_entry("environment")
    def __init__(self, data, *, _generated_reports=False, _validated_projection=False):
        """Build the container after Lean accepts its source."""

        def python():
            self._decode(data, _generated_reports=_generated_reports)
            return self

        # The reports generator and statement-layer constructors build
        # projections of sources already accepted by their owning routes.
        if _generated_reports or _validated_projection:
            python()
            return
        from .backends.validation import validated_environment
        validated_environment(self, data, python)

    def _decode(self, data, *, _generated_reports=False):
        """Materialise declarations that the Lean environment mode accepted.

        The source's field checks, profile gate, fault order and limits live in
        Lean. An unexpected shape here is an operational construction failure.
        """
        language = data["language"]
        route = language == profile_registry.LANGUAGE
        closure = language == CLOSURE_LANGUAGE
        profiles = (tuple(data["profiles"]) if route else
                    ORDER_PROFILES if closure and "order@0" in data["profiles"] else
                    CLOSURE_PROFILES if closure else (PROFILE,))
        order = "order@0" in profiles
        extended = "unit_schema" in data
        vocabulary = data["vocabulary"]

        units = None
        if extended:
            units = MappingProxyType({tag: MappingProxyType({
                "scale": entry["scale"], "display": MappingProxyType(dict(entry["display"]))})
                for tag, entry in data["units"].items()})

        sorts = {}
        for name, entry in vocabulary["sorts"].items():
            raw_words = entry.get("verbalisation")
            words = (SortVerbalisation(raw_words["singular"], raw_words["plural"])
                     if raw_words is not None else None)
            sorts[name] = SortDecl(entry["description"], words)

        predicates = {}
        for name, entry in vocabulary["predicates"].items():
            raw_reg = entry.get("regulated")
            regulated = None
            if raw_reg is not None:
                act = raw_reg.get("act")
                regulated = RegulatedDecl(raw_reg["role"], raw_reg["default"],
                                          " ".join(act.split()) if act is not None else None,
                                          raw_reg.get("permission"))
            predicates[name] = PredicateDecl(
                tuple(entry["arguments"]), entry["description"],
                entry.get("verbalisation"), entry.get("negative_verbalisation"),
                regulated, entry.get("functional"), entry.get("total"),
                canonical_json(entry["defined"]) if "defined" in entry else None,
                MappingProxyType(dict(entry["argument_units"]))
                if "argument_units" in entry else None)

        constants = {name: ConstantDecl(entry["sort"], entry.get("description"),
                                        entry.get("unit"), entry.get("verbalisation"))
                     for name, entry in vocabulary["constants"].items()}

        speech_acts = None
        if "speech_acts" in data:
            raw_scope = data["speech_acts"]
            scope = {"task": raw_scope["task"]}
            if "addressee" in raw_scope:
                scope["addressee"] = MappingProxyType(dict(raw_scope["addressee"]))
            if raw_scope.get("definites"):
                scope["definites"] = MappingProxyType(dict(raw_scope["definites"]))
            speech_acts = MappingProxyType(scope)

        reports = None
        if "reports" in vocabulary:
            block = vocabulary["reports"]
            reports = {"holders": tuple(block["holders"]), "evidence": block["evidence"]}
        alternatives = canonical_json(data["alternatives"]) if "alternatives" in data else None
        risk = canonical_json(data["risk"]) if "risk" in data else None

        profile_sorts = {}
        profile_predicates = {}
        profile_constants = {}
        if alternatives is not None:
            block = data["alternatives"]
            for name, arguments in (("avoidable", (block["harm"], block["chooser"])),
                                    ("unavoidable", (block["harm"], block["chooser"])),
                                    ("allows", (block["action"], block["harm"])),
                                    ("prevents", (block["action"], block["harm"]))):
                profile_predicates[name] = PredicateDecl(arguments, "alternatives@0 profile word")
        if risk is not None:
            block = data["risk"]
            severity_sort = block["severity"]["sort"]
            profile_sorts[severity_sort] = SortDecl("risk severity")
            for klass in block["severity"]["classes"]:
                profile_constants[klass] = ConstantDecl(severity_sort, "risk severity class")
            alt = data["alternatives"]
            for name, arguments in (
                ("risk__might_lead_to", (alt["action"], alt["harm"])),
                ("risk__class", (alt["harm"], severity_sort)),
                ("risk__more_severe", (severity_sort, severity_sort)),
                ("risk__or_worse", (alt["harm"], severity_sort)),
                ("risk__less_worst", (alt["action"], alt["action"])),
            ):
                profile_predicates[name] = PredicateDecl(arguments, "risk@0 generated word")

        values = (
            ("language", language),
            ("profile", None if route or closure else PROFILE),
            ("profiles", profiles),
            ("spec_revision", data["spec_revision"]),
            ("sorts", _ProfilePredicates(sorts, profile_sorts) if risk is not None
             else MappingProxyType(sorts)),
            ("predicates", _ProfilePredicates(predicates, profile_predicates)
             if alternatives is not None else MappingProxyType(predicates)),
            ("constants", _ProfilePredicates(constants, profile_constants) if risk is not None
             else MappingProxyType(constants)),
            ("speech_acts", speech_acts),
            ("unit_schema", data["unit_schema"] if extended else None),
            ("units", units),
            ("reports", reports),
            ("alternatives", alternatives),
            ("risk", risk),
        )
        for field, value in values:
            object.__setattr__(self, field, value)
        if "rights" in vocabulary:
            object.__setattr__(self, "rights", canonical_json(vocabulary["rights"]))
        elif not hasattr(self, "rights"):
            object.__setattr__(self, "rights", None)
        object.__setattr__(self, "_environment_id",
                           digest(f"ve-environment-{self.identity_version}\n", self.to_dict()))
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
            if declaration.argument_units is not None:
                entry["argument_units"] = dict(declaration.argument_units)
            return entry

        return {"language": self.language, **({"profiles": list(self.profiles)} if self.profile is None else {"profile": self.profile}), "spec_revision": self.spec_revision,
                **({"speech_acts": {**self.speech_acts,
                                    **({"addressee": dict(self.speech_acts["addressee"])}
                                       if "addressee" in self.speech_acts else {}),
                                    **({"definites": dict(self.speech_acts["definites"])}
                                       if "definites" in self.speech_acts else {})}}
                   if self.speech_acts is not None else {}),
                **({"alternatives": loads_json(self.alternatives)} if self.alternatives is not None else {}),
                **({"risk": loads_json(self.risk)} if self.risk is not None else {}),
                "vocabulary": {"sorts": {k: sort_entry(v) for k, v in self.sorts.items()},
                               "predicates": {k: predicate_entry(v) for k, v in self.predicates.items()},
                               "constants": {k: {"sort": v.sort, **({"description": v.description}
                                                                      if v.description is not None else {}),
                                                 **({"unit": v.unit} if v.unit is not None else {}),
                                                 **({"verbalisation": v.verbalisation}
                                                    if v.verbalisation is not None else {})}
                                             for k, v in self.constants.items()},
                               **({"reports": {"holders": list(self.reports["holders"]), "evidence": self.reports["evidence"]}}
                                  if self.reports is not None else {}),
                               **({"rights": loads_json(self.rights)} if type(self.rights) is bytes else {})},
                **({"unit_schema": self.unit_schema,
                    "units": {tag: {"scale": record["scale"], "display": dict(record["display"])}
                              for tag, record in self.units.items()}}
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
        return self._environment_id
