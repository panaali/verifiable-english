"""Immutable local vocabulary; descriptions contribute to artifact identity."""
from collections.abc import Mapping
from dataclasses import dataclass, field
import re
from types import MappingProxyType

from .assurance import semantic_entry
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
_ASCII_LOWER = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")


def listed_profiles(data) -> tuple[str, ...]:
    """The profiles named by environment JSON that may not be valid yet: `()`
    unless `profiles` is an array of strings. Routing that reads the profiles
    before the decoder runs uses this; the decoder rejects any other value
    (Lean's `profilesOf`)."""
    profiles = data.get("profiles") if type(data) is dict else None
    return tuple(profiles) if _string_array(profiles) else ()


def _string_array(value) -> bool:
    return type(value) is list and all(type(item) is str for item in value)


def route_kind(data) -> str:
    """The Lean route that decodes a route envelope: by its profiles when they
    are an array of strings, else by the blocks it carries. "speech", "alternatives" and "risk"
    read the profiles before the envelope; "reports", "quantity" and "envelope"
    (`VE.Route.Gate.decodeEnvelope`) read the field set first."""
    if _string_array(data.get("profiles")):
        named = [kind for profile, kind in (("risk@0", "risk"), ("alternatives@0", "alternatives"),
                                            ("speech-acts@0", "speech"), ("reports@0", "reports"))
                 if profile in data["profiles"]]
    else:
        named = [kind for block, kind in (("risk", "risk"), ("alternatives", "alternatives"),
                                          ("speech_acts", "speech")) if block in data]
    if named:
        return named[0]
    return "quantity" if "unit_schema" in data or "units" in data else "envelope"


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


def _regulated(raw, args, name, *, unspecified=False):
    if type(raw) is not dict or "role" not in raw or "default" not in raw:
        raise VEError(f"InvalidInput: regulated declaration {name} needs role and default")
    role, default = raw["role"], raw["default"]
    if default == "unspecified" and role in ("permission", "obligation", "plain") and not unspecified:
        # norm-defaults 2.1: a statement of silence, accepted only under its profile.
        raise UnsupportedProfile("UnsupportedProfile: unspecified completion requires norm-defaults@0")
    if (role not in ("permission", "obligation", "plain")
            or default not in ("deny", "allow", *(("unspecified",) if unspecified else ()))):
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
    speech_acts: object
    unit_schema: str | None
    units: object
    reports: object
    alternatives: bytes | None
    risk: bytes | None
    _environment_id: str = field(repr=False, compare=False)

    @semantic_entry("environment")
    def __init__(self, data, *, _generated_reports=False):
        """Decode and validate an environment under the selected authority."""
        from .backends.dispatch import authority_for, execute

        def python():
            self._decode(data, _generated_reports=_generated_reports)
            return self

        # rust-experimental covers evaluation and search only; environments
        # keep the Python decoder there, as before any adapter existed.
        if _generated_reports or authority_for("environment_validation") in ("python", "rust-experimental"):
            python()
            return
        from .backends.validation import environment_in_scope, validated_environment
        if not environment_in_scope(data):
            # Statement-layer and legacy envelopes are validated by their own
            # routes; Lean's environment mode does not take them.
            python()
            return
        execute("environment_validation", {"kind": "environment"}, python,
                lean=lambda: validated_environment(self, data, python))

    def _decode(self, data, *, _generated_reports=False):
        canonical_json(data)  # Check size, Unicode, and the restricted wire subset.
        # The two block routes own acceptance and its first diagnostic. The
        # remainder of this constructor only materialises an accepted source.
        block_kind = route_kind(data) if type(data) is dict else None
        if block_kind in ("alternatives", "risk") and data.get("language") not in (LANGUAGE, CLOSURE_LANGUAGE):
            from .backends.validation import validated_statement_block
            validated_statement_block(data, block_kind)
        language = data.get("language") if type(data) is dict else None
        # Lean's decoders read a language that is not a string, or absent, as
        # the route's (VE.Service.Standalone.isLegacy): the route's fields, in
        # the order of the route that decodes the envelope (`route_kind`). So is
        # any other language on an envelope a block route decodes, as those read
        # the profiles and the block before the language; elsewhere an unknown
        # language is the frozen v0 decoder's (conformance/validation.json).
        closure = language == CLOSURE_LANGUAGE
        route = type(data) is dict and (
            type(language) is not str or language == profile_registry.LANGUAGE
            or (language not in (LANGUAGE, CLOSURE_LANGUAGE)
                and route_kind(data) in ("speech", "alternatives", "risk")))
        modern = route or closure
        kind = route_kind(data) if route else None
        extended = type(data) is dict and ("unit_schema" in data or "units" in data)
        units_together = UnsupportedProfile("unit_schema and units require the ve.core@0.2 quantity route together")
        if kind == "risk" and ("unit_schema" in data) != ("units" in data):
            raise units_together  # VE.Risk.Wire.extended, before the profiles
        if kind in ("speech", "alternatives", "risk"):
            # The block routes read the profiles, their gate and their block
            # before the envelope's field set and language: VE.SpeechActs.Wire.
            # decodeSpeechEnvironmentFull, VE.Alternatives.Wire.decodeAltSource,
            # VE.Risk.Wire.decodeRiskSource.
            profile_registry.route_gate(kind, data.get("profiles"))
            if kind == "speech":
                vocabulary = data.get("vocabulary")
                if type(vocabulary) is not dict or type(vocabulary.get("predicates")) is not dict:
                    raise VEError("InvalidInput: environment vocabulary")  # predicatesOf
                from .speech_acts import parse_scope
                parse_scope(data.get("speech_acts"))
            elif "alternatives" not in data:
                raise VEError("InvalidInput: alternatives.block")
            elif kind == "risk" and "risk" not in data:
                raise VEError("InvalidInput: risk.block")
        if extended and (not route or "unit_schema" not in data or "units" not in data):
            raise units_together
        fields = {"language", "profiles" if modern else "profile", "spec_revision", "vocabulary"}
        require_fields(data, fields | ({"speech_acts"} if kind == "speech" else set())
                       | ({"alternatives"} if kind in ("alternatives", "risk") else set())
                       | ({"risk"} if kind == "risk" else set())
                       | ({"unit_schema", "units"} if extended else set()))
        if route and type(language) is not str:
            raise VEError("String expected")
        if route and language != profile_registry.LANGUAGE:
            raise UnsupportedProfile("Unsupported language")  # VE.Route.Gate.decodeEnvelope
        order = False
        if route:
            if kind == "quantity":
                # The quantity route (VE.Time.Wire.decodeEnvironment) reads the
                # profiles with `strings`; the risk route as the gate does.
                if type(data["profiles"]) is not list:
                    raise VEError("array expected")
                if not _string_array(data["profiles"]):
                    raise VEError("String expected")
            family = profile_registry.checker_family(data["profiles"])
            # Every top-level field's type is checked before its value is used,
            # with the diagnostics of Lean's decoders (VE.Route.Gate.decodeEnvelope).
            if type(data["spec_revision"]) is not str:
                raise VEError("String expected")
            if data["spec_revision"] != profile_registry.SPEC_REVISION:
                raise UnsupportedProfile(f"Unsupported specification revision {data['spec_revision']}")
            order = family == "order"
            if extended:
                from .units import RISK_UNIT_PROFILES, W6_PROFILE_TEXT, W6_PROFILES
                if tuple(data["profiles"]) not in W6_PROFILES + RISK_UNIT_PROFILES:
                    raise UnsupportedProfile(W6_PROFILE_TEXT)
        elif closure:
            # VE.Closure.Bridge and VE.Order.Wire read the profiles as an array
            # of strings and the revision as a string before comparing them.
            if type(data["profiles"]) is not list:
                raise VEError("array expected")
            if any(type(p) is not str for p in data["profiles"]) or type(data["spec_revision"]) is not str:
                raise VEError("String expected")
            if (data["profiles"], data["spec_revision"]) == (list(ORDER_PROFILES), ORDER_REVISION):
                order = True
            elif data["profiles"] != list(CLOSURE_PROFILES) or data["spec_revision"] != CLOSURE_REVISION:
                raise UnsupportedProfile("Unsupported profiles or specification revision"
                                         + (" (closure@0 x order@0 is not supported)"
                                            if {"closure@0", "order@0"} <= set(data["profiles"]) else ""))
        else:
            if language == LANGUAGE and any(type(data[key]) is not str for key in ("profile", "spec_revision")):
                # VE.Bridge.decodeEnvironment reads all three as strings before comparing them.
                raise VEError("String expected")
            if (data["language"], data["profile"], data["spec_revision"]) != (LANGUAGE, PROFILE, SPEC_REVISION):
                raise UnsupportedProfile("Unsupported language, semantic profile, or specification revision")
        vocab = data["vocabulary"]
        if extended:
            from .units import validate_units
            if type(data["unit_schema"]) is not str and "risk@0" not in data["profiles"]:
                # VE.Time.Wire.decodeEnvironment; the risk route compares the
                # value (VE.Risk.Wire), which validate_units does.
                raise VEError("String expected")
            checked_units = validate_units(data["unit_schema"], data["units"])
            units = {tag: MappingProxyType({"scale": record["scale"],
                                          "display": MappingProxyType(dict(record["display"]))})
                     for tag, record in checked_units.items()}
        else:
            units = None
        if route and "reports@0" in data["profiles"] and (type(vocab) is not dict or "reports" not in vocab):
            # VE.Attribution.Wire.decodeEnvironment reads the block from the
            # vocabulary (`getObjVal?`, which fails on any other value) first.
            raise UnsupportedProfile("reports@0 needs a reports block")
        if type(vocab) is not dict:
            raise VEError("object expected")
        require_fields(vocab, {"sorts", "predicates", "constants"} |
                       ({"reports"} if route and "reports@0" in data["profiles"] else set()),
                       path="/vocabulary")
        if route and "reports@0" in data["profiles"]:
            # VE.Attribution.Wire reads the block's fields and types before the vocabulary.
            require_fields(vocab["reports"], {"holders", "evidence"}, path="/vocabulary/reports")
            if type(vocab["reports"]["holders"]) is not list:
                raise VEError("array expected")
            if not _string_array(vocab["reports"]["holders"]) or type(vocab["reports"]["evidence"]) is not str:
                raise VEError("String expected")
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
            # An explicit map, even an empty one, is part of the submitted identity.
            argument_units = None
            if "argument_units" in entry:
                from .units import validate_slot_units
                argument_units = MappingProxyType(
                    validate_slot_units(entry["argument_units"], args, units))
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
            regulated = (_regulated(entry["regulated"], args, name,
                                    unspecified=route and "norm-defaults@0" in data["profiles"])
                         if "regulated" in entry else None)
            if defined:
                payload = entry["defined"]
                require_fields(payload, {"arguments", "body"}, path=f"/vocabulary/predicates/{name}/defined")
                if payload["arguments"] != args:
                    raise VEError(f"Definition {name!r} arguments differ from its declaration")
            predicates[name] = PredicateDecl(tuple(args), _description(entry["description"]),
                                             verbalisation, negative, regulated,
                                             entry.get("functional"), entry.get("total"),
                                             canonical_json(entry["defined"]) if defined else None,
                                             argument_units)
        if route and "norm-defaults@0" in data["profiles"]:
            # norm-defaults 2.1: `unsaid__` names the fillings `fill` adds.
            for name in predicates:
                if name.startswith("unsaid__"):
                    raise VEError(f"InvalidInput: reserved name {name}")
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
            has_words = route and type(entry) is dict and "verbalisation" in entry
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
                if type(entry["unit"]) is not str:
                    raise VEError("String expected")
                validate_tag(entry["unit"], units)
            constants[name] = ConstantDecl(sort, _description(entry["description"])
                                           if "description" in entry else None,
                                           entry.get("unit") if has_unit else None,
                                           _verbalisation(entry["verbalisation"]) if has_words else None)
        if route and "risk@0" in data["profiles"]:
            # The Lean risk route's checks after the vocabulary, at its point and in its order
            # (VE.Risk.Wire.decodeRiskSource): W6's route conditions, then what the route refuses.
            if extended:
                from .units import validate_extension
                validate_extension(data["profiles"], units, sorts, constants)
        speech_acts = None
        if route and "speech-acts@0" in data["profiles"]:
            from .speech_acts import validate_scope
            speech_acts = validate_scope(data["speech_acts"], sorts, constants, predicates)
            speech_acts = MappingProxyType({
                **speech_acts,
                **({"addressee": MappingProxyType(speech_acts["addressee"])}
                   if "addressee" in speech_acts else {}),
                **({"definites": MappingProxyType(speech_acts["definites"])}
                   if "definites" in speech_acts else {}),
            })
        reports = None
        if route and "reports@0" in data["profiles"]:
            holders, evidence = vocab["reports"]["holders"], vocab["reports"]["evidence"]
            if not 1 <= len(holders) <= 8 or len(set(holders)) != len(holders):
                raise VEError("InvalidInput: holders must be 1 to 8 distinct sorts")
            for holder in holders:
                if holder not in sorts:
                    raise UnknownSymbol(f"holder sort {holder}")
            if type(evidence) is not str or evidence not in sorts:
                raise UnknownSymbol("evidence sort")
            if any(c.get("sort") in holders and type(c.get("verbalisation")) is str and
                   # ASCII case folding only, as Lean's String.toLower: no
                   # Unicode fold may reach the reserved words by another path.
                   c["verbalisation"].translate(_ASCII_LOWER) == "the stated assessment"
                   for c in vocab["constants"].values()):
                raise VEError("InvalidInput: holder verbalisation reserved")
            if not _generated_reports and any(name.startswith("reports__") for name in predicates):
                raise VEError("InvalidInput: author predicate begins with reports__")
            reports = {"holders": tuple(holders), "evidence": evidence}
        if route and sum(decl.sort == STRING_SORT for decl in constants.values()) > 64:
            raise ResourceLimit("At most 64 declared $string literals")
        alternatives = None
        if route and "alternatives@0" in data["profiles"]:
            alternatives = canonical_json(data["alternatives"])
        risk = None
        if route and "risk@0" in data["profiles"]:
            risk = canonical_json(data["risk"])
        profile_predicates = {}
        profile_sorts = {}
        profile_constants = {}
        if alternatives is not None:
            block = loads_json(alternatives)
            for name, arguments in (("avoidable", (block["harm"], block["chooser"])),
                                    ("unavoidable", (block["harm"], block["chooser"])),
                                    ("allows", (block["action"], block["harm"])),
                                    ("prevents", (block["action"], block["harm"]))):
                profile_predicates[name] = PredicateDecl(arguments, "alternatives@0 profile word")
        if risk is not None:
            block = loads_json(risk)
            severity_sort = block["severity"]["sort"]
            profile_sorts[severity_sort] = SortDecl("risk severity")
            for klass in block["severity"]["classes"]:
                profile_constants[klass] = ConstantDecl(severity_sort, "risk severity class")
            alt_block = loads_json(alternatives)
            for name, arguments in (
                ("risk__might_lead_to", (alt_block["action"], alt_block["harm"])),
                ("risk__class", (alt_block["harm"], severity_sort)),
                ("risk__more_severe", (severity_sort, severity_sort)),
                ("risk__or_worse", (alt_block["harm"], severity_sort)),
                ("risk__less_worst", (alt_block["action"], alt_block["action"])),
            ):
                profile_predicates[name] = PredicateDecl(arguments, "risk@0 generated word")
        for field, value in (("language", data["language"]), ("profile", None if modern else PROFILE),
                             ("profiles", tuple(data["profiles"]) if route else
                              (ORDER_PROFILES if order else CLOSURE_PROFILES) if closure else (PROFILE,)),
                             ("spec_revision", data["spec_revision"]),
                             ("sorts", _ProfilePredicates(sorts, profile_sorts) if risk is not None
                              else MappingProxyType(sorts)), ("predicates", _ProfilePredicates(predicates, profile_predicates)
                              if alternatives is not None else MappingProxyType(predicates)),
                             ("constants", _ProfilePredicates(constants, profile_constants) if risk is not None
                              else MappingProxyType(constants)),
                             ("unit_schema", data["unit_schema"] if extended else None),
                             ("units", MappingProxyType(units) if extended else None),
                             ("alternatives", alternatives),
                             ("speech_acts", speech_acts)):
            object.__setattr__(self, field, value)
        object.__setattr__(self, "risk", risk)
        object.__setattr__(self, "reports", reports)
        if extended and risk is None:  # a risk environment was checked after its vocabulary
            from .units import validate_extension
            validate_extension(self.profiles, units, sorts, constants)
        if extended and risk is None:
            # Rust and Lean digest the submitted environment; Python digests
            # to_dict(). Any spelling that does not survive the round trip would
            # give the same input two identities, so it is rejected.
            if canonical_json(self.to_dict()) != canonical_json(data):
                raise VEError("W6 environment does not round-trip to its canonical declaration")
        # All identity-bearing declarations are now immutable. Model search
        # constructs many candidates against this same environment.
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
                                  if self.reports is not None else {})},
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
