"""Identity-bound rights declarations and holder-side elaboration.

The output is a soft document. Rights add no deontic primitive: a claim and
the corresponding bearer duty are the same selected rule.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import re

from .ast import And, Atom, Binary, Bottom, Implies, Or, Top, Unary, Var, _Checker, _Decoder, _to_data
from .environment import valid_identifier
from .errors import DuplicateDeclaration, ResourceLimit, UnknownSymbol, UnsupportedProfile, VEError
from .norms import Norm, _bind, _instantiate
from .search import _used_predicates
from .softnorms import SoftEnvironment, SoftNormDocument, decode_rule

_RULE = re.compile(r"[a-z][a-z0-9-]*\Z", re.ASCII)
# Every line kind with its rule-bearing fields, in the order the line states its rules: a power line states a
# liberty and a recognition rule, every other kind one norm. Whatever names or owns a line's rules reads this table
# (compose-s2 fix4 A2), so a new kind cannot be added without saying which fields carry its rules.
LINE_RULE_FIELDS = {"claim": ("norm",), "liberty": ("norm",), "immunity": ("norm",), "power": ("liberty", "recognition")}
RULE_FIELDS = tuple(dict.fromkeys(field for fields in LINE_RULE_FIELDS.values() for field in fields))
_KINDS = frozenset(LINE_RULE_FIELDS)


def _name(value):
    if type(value) is not str or len(value) > 64 or not _RULE.fullmatch(value):
        raise VEError(f"InvalidInput: invalid rights name {value!r}")
    if value.startswith("rights-"):
        raise VEError(f"InvalidInput: name {value} begins with rights-")
    return value


def _strings(value):
    return type(value) is list and all(type(item) is str for item in value)


def _decode_block(rights):
    """The types `decodeRightsBlock` reads before the soft environment is
    decoded: `holders`, `bearers` and `protected` arrays of strings, `alters` an
    object whose entries have their fields, a natural `holder_slot` and a string
    `status` and `recognition`."""
    if (not all(_strings(rights.get(key, [])) for key in ("holders", "bearers", "protected"))
            or type(rights.get("alters", {})) is not dict):
        raise VEError("InvalidInput: invalid rights block")
    for act, entry in rights.get("alters", {}).items():
        if (type(entry) is not dict or not {"holder_slot", "status"} <= set(entry)
                or set(entry) - {"holder_slot", "status", "recognition"}
                or type(entry["holder_slot"]) is not int or entry["holder_slot"] < 0
                or type(entry["status"]) is not str or type(entry.get("recognition", "")) is not str):
            raise VEError(f"InvalidInput: alters {act}")


def _duplicate(values, kind):
    seen = set()
    for value in values:
        if value in seen:
            raise DuplicateDeclaration(f"{kind} {value}")
        seen.add(value)


class RightsEnvironment(SoftEnvironment):
    """Validate and bind the rights block without changing older identities."""

    LAYERS = frozenset({"rights@0"})

    def __init__(self, data):
        profiles = data.get("profiles") if type(data) is dict else None
        if type(profiles) is not list or any(type(p) is not str for p in profiles):
            # VE.Rights.Wire.decodeRightsEnvironment reads the profiles first.
            raise UnsupportedProfile("profiles must be a sorted unique array")
        if "rights@0" not in profiles:
            raise UnsupportedProfile("rights@0 is required")
        if "soft-norms@0" not in profiles:
            raise UnsupportedProfile("rights@0 requires soft-norms@0")
        raw = deepcopy(data)
        vocabulary = raw.get("vocabulary", {})
        rights = vocabulary.pop("rights", None) if type(vocabulary) is dict else None
        # As Lean's `decodeRightsBlock` reads the block: `holders` and `bearers` are required, `protected` and
        # `alters` optional (an absent one is empty). The block is kept as written, so its identity is Lean's.
        if (type(rights) is not dict or not {"holders", "bearers"} <= set(rights)
                or not set(rights) <= {"holders", "bearers", "protected", "alters"}):
            raise VEError("InvalidInput: invalid rights block")
        for entry in (rights["alters"].values() if type(rights.get("alters")) is dict else ()):
            if type(entry) is dict and "recognition" in entry and entry["recognition"] is None:
                # 3.1's null recognition is the absent key: canonical JSON has no null,
                # and the Lean wire sends the field absent.
                del entry["recognition"]
        _decode_block(rights)
        predicates = vocabulary.get("predicates")
        for predicate in (predicates if type(predicates) is dict else ()):
            if predicate.startswith("rights__"):
                raise VEError(f"InvalidInput: author predicate {predicate} begins with rights__")
        object.__setattr__(self, "rights", rights)
        super().__init__(raw)
        # VE.Rights.Correlate.checkBlock's order: nonempty, declared, distinct.
        holders, bearers = tuple(rights["holders"]), tuple(rights["bearers"])
        if not holders or not bearers:
            raise VEError("InvalidInput: invalid rights block")
        for sort in (*holders, *bearers):
            if sort not in self.sorts:
                raise UnknownSymbol(f"UnknownSymbol: sort {sort}")
        _duplicate(holders, "holder")
        _duplicate(bearers, "bearer")
        object.__setattr__(self, "holders", holders)
        object.__setattr__(self, "bearers", bearers)
        protected = rights.get("protected", [])
        if len(set(protected)) != len(protected):
            raise VEError("InvalidInput: protected")
        for name in protected:
            decl = self.predicates.get(name)
            if (decl is None or decl.regulated is not None or decl.defined is not None
                    or not set(decl.arguments) & set(holders)):
                raise VEError(f"InvalidInput: protected {name}")
        for act, entry in rights.get("alters", {}).items():
            declaration = self.predicates.get(act)
            if (declaration is None or declaration.regulated is None
                    or declaration.regulated.role != "permission"):
                raise VEError(f"InvalidInput: alters {act}")
            slot = entry["holder_slot"]
            if slot >= len(declaration.arguments):
                raise VEError(f"InvalidInput: alters {act}")
            holder = declaration.arguments[slot]
            status = self.predicates.get(entry["status"])
            recognition = self.predicates.get(entry["recognition"]) if entry.get("recognition") else None
            if (holder not in holders or status is None or status.regulated is not None
                    or status.defined is not None or holder not in status.arguments
                    or ("recognition" in entry and
                        (recognition is None or recognition.regulated is None
                         or recognition.regulated.role != "obligation"
                         or recognition.arguments[0] not in bearers
                         or holder not in recognition.arguments))):
                raise VEError(f"InvalidInput: alters {act}")

    def to_dict(self):
        result = super().to_dict()
        result["vocabulary"]["rights"] = deepcopy(self.rights)
        return result


def conjugated(act):
    """The act phrase with its verb in the third person singular, for the
    generated wordings' "where that state arrests that person" (2.1)."""
    if not act.startswith("{0} "):
        return act
    verb, _, rest = act[4:].partition(" ")
    irregular = {"be": "is", "have": "has", "do": "does", "go": "goes"}
    if verb in irregular:
        verb = irregular[verb]
    elif verb.endswith(("s", "x", "z", "ch", "sh", "o")):
        verb += "es"
    elif verb.endswith("y") and len(verb) > 1 and verb[-2] not in "aeiou":
        verb = verb[:-1] + "ies"
    else:
        verb += "s"
    return "{0} " + verb + (" " + rest if rest else "")


def _atom(name, arity):
    terms = tuple(Var(arity - index - 1) for index in range(arity))
    return (Unary(name, terms[0]) if arity == 1 else
            Binary(name, *terms) if arity == 2 else Atom(name, terms))


def _or(items):
    result = Bottom()
    for item in items:
        result = Or(result, item)
    return result


def _slot(env, right, rule, specified, *, subject=False):
    arguments = env.predicates[rule.core.predicate].arguments
    if subject:
        if arguments[0] != right["holder"]:
            raise VEError(f"IncidentShape: {rule.core.name} on right {right['name']}")
        return 0
    choices = [index for index, sort in enumerate(arguments) if index and sort == right["holder"]]
    if specified is None and len(choices) > 1:
        raise VEError(f"HolderSlotAmbiguous: {rule.core.name}")
    slot = specified if specified is not None else choices[0] if len(choices) == 1 else None
    if slot not in choices:
        raise VEError(f"IncidentShape: {rule.core.name} on right {right['name']}")
    return slot


def _line_shape(env, right, kind, rule, slot):
    core = rule.core
    decl = env.predicates.get(core.predicate)
    reg = decl.regulated if decl else None
    subject = decl.arguments[0] if decl else None
    valid = (
        kind in ("claim", "powerRecognition") and subject in env.bearers and
        ((reg.role == "obligation" and core.sign) or (reg.role == "permission" and not core.sign))
        if reg is not None else False)
    valid = valid or (kind in ("liberty", "powerLiberty") and subject == right["holder"]
                      and reg is not None and reg.role == "permission" and core.sign)
    valid = valid or (kind == "immunity" and subject in env.bearers and reg is not None
                      and reg.role == "permission" and not core.sign and
                      core.predicate in env.rights.get("alters", {}) and
                      env.rights["alters"][core.predicate]["holder_slot"] == slot)
    if not valid:
        raise VEError(f"IncidentShape: {core.name} on right {right['name']}")


class RightsDocument:
    """Validate source units and regenerate E'', T'', and limitation premises."""

    def __init__(self, env: RightsEnvironment, units):
        if not isinstance(env, RightsEnvironment):
            raise UnsupportedProfile("rights@0 is required")
        self.env = env
        if type(units) is not list or len(units) > 1024:
            raise ResourceLimit("units")
        rights = {}
        entries = []
        limitations = []
        bars = []
        outside = []
        names = set()
        source_units = None
        for unit in units:
            if type(unit) is dict and set(unit) == {"norm", "cites"}:
                # 3.2: a norm unit outside rights may carry `narrows:<line>` citations.
                outside.append(unit)
                continue
            if type(unit) is not dict or len(unit) != 1:
                raise VEError("InvalidInput: rights unit")
            kind, body = next(iter(unit.items()))
            if kind == "source_units":
                # The ids of the source units a citation may name (the Lean wire's element).
                if source_units is not None:
                    raise VEError("InvalidInput: duplicate source_units")
                if type(body) is not list or any(type(item) is not str for item in body):
                    raise VEError("InvalidInput: source_units must list unit ids")
                source_units = tuple(body)
            elif kind == "right":
                if (type(body) is not dict or
                        set(body) != {"name", "holder", "guard", "lines"}):
                    raise VEError("InvalidInput: right")
                name = _name(body["name"])
                if name in names:
                    raise DuplicateDeclaration(f"right {name}")
                names.add(name)
                if body["holder"] not in env.holders:
                    raise VEError(f"UnknownSymbol: sort {body['holder']}")
                guard = _Decoder().decode(body["guard"])
                _Checker(env).formula(guard, (body["holder"],))
                if any(env.predicates[p].regulated is not None or
                       env.predicates[p].defined is not None or p.startswith("soft__")
                       for p in _used_predicates(guard)):
                    raise VEError(f"InvalidInput: right guard {name} must use base predicates")
                if type(body["lines"]) is not list:
                    raise VEError("InvalidInput: right lines")
                rights[name] = {**body, "guard_formula": guard, "count": 0}
                for line in body["lines"]:
                    entries.append((name, line))
                    rights[name]["count"] += 1
            elif kind == "right_lines":
                if type(body) is not dict or set(body) != {"right", "lines"}:
                    raise VEError("InvalidInput: right_lines")
                if body["right"] not in rights:
                    raise VEError(f"UnknownRight: {body['right']}")
                if type(body["lines"]) is not list:
                    raise VEError("InvalidInput: right lines")
                for line in body["lines"]:
                    entries.append((body["right"], line))
                    rights[body["right"]]["count"] += 1
            elif kind == "limitation":
                if type(body) is not dict or "name" not in body:
                    raise VEError("InvalidInput: limitation")
                name = _name(body["name"])
                if name in names:
                    raise DuplicateDeclaration(f"limitation {name}")
                names.add(name)
                limitations.append(body)
            elif kind == "bar":
                if bars:
                    raise DuplicateDeclaration("bar")
                if type(body) is not dict or set(body) != {"name", "reading", "decided_by"}:
                    raise VEError("InvalidInput: bar")
                name = _name(body["name"])
                if name in names:
                    raise DuplicateDeclaration("bar")
                names.add(name)
                if body["reading"] not in ("rule", "query"):
                    raise VEError("InvalidInput: bar reading")
                if type(body["decided_by"]) is not str or not body["decided_by"]:
                    raise VEError("InvalidInput: bar decider")
                bars.append(body)
            elif kind == "norm":
                outside.append(unit)
            else:
                raise VEError(f"InvalidInput: rights unit {kind}")
        # 11: the same limits as the Lean rights route.
        if len(rights) > 128:
            raise ResourceLimit("rights")
        if len(limitations) > 16:
            raise ResourceLimit("limitations")
        for name, right in rights.items():
            if not right["count"]:
                raise VEError(f"RightWithoutIncident: {name}")
        self.rights = rights
        self.limitations = tuple(limitations)
        self.bar = bars[0] if bars else None
        self.outside = tuple(outside)
        self.source_units = source_units or ()
        self._validate_limitations(names)
        self._validate_citations(entries)
        self.line_env = self._line_environment(entries)
        self.instances = tuple(self._instances(entries, names))
        self._correlate()

    def _line_environment(self, entries):
        """Declare source-key predicates before typing authored line guards."""
        source = self.env.to_dict()
        source["profiles"].remove("rights@0")
        source["vocabulary"].pop("rights")
        predicates = source["vocabulary"]["predicates"]
        pairs = set()
        for right_name, line in entries:
            if type(line) is not dict:
                continue
            kind = line.get("kind")
            for field in (LINE_RULE_FIELDS.get(kind, ("norm",)) if type(kind) is str else ("norm",)):
                raw = line.get(field)
                if type(raw) is not dict:
                    continue
                subjects = (line.get("fan_out") or {}).values() if line.get("fan_out") else (raw.get("predicate"),)
                for predicate in subjects:
                    if predicate not in self.env.predicates:
                        continue
                    act = self._act(predicate)
                    for limit in self.limitations:
                        if ((limit["scope"] == "all" or right_name in limit["scope"]) and
                                (limit["kinds"] == "all" or line.get("kind") in limit["kinds"])):
                            pairs.add((limit["name"], act))
        for index, (name, act) in enumerate(sorted(pairs), 1):
            args = list(self.env.predicates[act].arguments)
            predicates[f"rights__lim__{index}"] = {
                "arguments": args, "description": f"limitation {name} of {act}"}
        triples = sorted((name, act, condition["name"])
                         for name, act in pairs
                         for limit in self.limitations if limit["name"] == name
                         for condition in limit["conditions"])
        for index, (name, act, condition) in enumerate(triples, 1):
            predicates[f"rights__cond__{index}"] = {
                "arguments": list(self.env.predicates[act].arguments),
                "description": f"condition {condition} of limitation {name} on {act}"}
        return SoftEnvironment(source, generated=True)

    def _instances(self, entries, names):
        fan = 0
        for right_name, line in entries:
            right = self.rights[right_name]
            if type(line) is not dict or line.get("kind") not in _KINDS:
                raise VEError("InvalidInput: incident line")
            kind = line["kind"]
            fields = LINE_RULE_FIELDS[kind]
            allowed = {"kind", "cites", "holder_slot", *fields} | (set() if kind == "power" else {"fan_out"})
            if set(line) - allowed or (kind == "power" and not set(fields) <= set(line)):
                raise VEError("InvalidInput: incident line fields")
            norms = (tuple((f"power{field.capitalize()}", line.get(field)) for field in fields) if kind == "power"
                     else ((kind, line.get("norm")),))
            fan_map = line.get("fan_out")
            if fan_map is not None and (kind not in ("claim", "immunity") or
                                        type(fan_map) is not dict):
                raise VEError("InvalidInput: invalid fan-out")
            for instance_kind, raw in norms:
                if type(raw) is not dict:
                    raise VEError("InvalidInput: incident norm")
                if fan_map is not None and raw.get("predicate") is not None:
                    raise VEError(f"InvalidInput: line {raw.get('name')} has predicate and fan_out")
                if any(type(parent) is str and parent.startswith("rights-")
                       for parent in raw.get("over", ())):
                    raise VEError("InvalidInput: authored precedence cites a generated rule")
                if fan_map is not None:
                    # A fan-out line keeps its author name as its source key (1.6): it is
                    # an author rule name, reserved prefix and uniqueness included.
                    _name(raw.get("name"))
                    if raw["name"] in names:
                        raise DuplicateDeclaration(f"rule {raw['name']}")
                    names.add(raw["name"])
                sources = ([(bearer, fan_map.get(bearer)) for bearer in sorted(self.env.bearers)]
                           if fan_map is not None else [(None, raw.get("predicate"))])
                for bearer, predicate in sources:
                    if bearer is not None and predicate is None:
                        raise VEError(f"FanOutUndeclared: {raw.get('name')}, {bearer}")
                    norm = {**raw, "predicate": predicate}
                    if bearer is not None:
                        fan += 1
                        norm["name"] = f"rights-fan-{fan}"
                    else:
                        _name(norm.get("name"))
                        if norm["name"] in names:
                            raise DuplicateDeclaration(f"rule {norm['name']}")
                        names.add(norm["name"])
                    rule = decode_rule(self.line_env, {"norm": norm})
                    slot = _slot(self.env, right, rule, line.get("holder_slot"),
                                 subject=instance_kind in ("liberty", "powerLiberty"))
                    _line_shape(self.env, right, instance_kind, rule, slot)
                    if instance_kind == "powerLiberty":
                        alter = self.env.rights.get("alters", {}).get(predicate)
                        if alter is None or alter["holder_slot"] != 0 or alter.get("recognition") is None:
                            raise VEError(f"IncidentShape: {rule.core.name} on right {right_name}")
                    if instance_kind == "powerRecognition":
                        liberty = line["liberty"]["predicate"]
                        alter = self.env.rights.get("alters", {}).get(liberty)
                        if alter is None or predicate != alter.get("recognition"):
                            raise VEError(f"IncidentShape: {rule.core.name} on right {right_name}")
                    if bearer is not None:
                        example = next((self.env.predicates[p] for p in fan_map.values() if p in self.env.predicates), None)
                        actual = self.env.predicates[predicate]
                        if (example is None or actual.arguments[0] != bearer or
                                actual.arguments[1:] != example.arguments[1:] or
                                actual.regulated.act != example.regulated.act or
                                actual.regulated.role != example.regulated.role):
                            raise VEError(f"FanOutUndeclared: {raw.get('name')}, {bearer}")
                    yield {"right": right_name, "source_kind": kind, "kind": instance_kind,
                           "rule": rule, "holder_slot": slot, "cites": line.get("cites", {}),
                           "bearer": bearer, "source_line": line}

    def _validate_citations(self, entries):
        """4.1 step 3: every citation names a source unit, so a citation to a
        non-existent unit never licenses a mechanism (4.5)."""
        tables = [line.get("cites", {}) for _, line in entries if type(line) is dict]
        tables += [unit["cites"] for unit in self.outside if "cites" in unit]
        for cites in tables:
            if type(cites) is not dict:
                raise VEError("InvalidInput: line citations")
            for key, targets in cites.items():
                if type(targets) is not list or not targets or any(type(t) is not str for t in targets):
                    raise VEError(f"InvalidInput: cites {key} must list unit ids")
                for target in targets:
                    if target not in self.source_units:
                        raise VEError(f"UnknownSymbol: unit {target}")

    def _validate_limitations(self, names):
        for limit in self.limitations:
            if (set(limit) != {"name", "scope", "kinds", "decided_by", "conditions", "factors"}
                    or type(limit["conditions"]) is not list or type(limit["factors"]) is not list):
                raise VEError("InvalidInput: limitation")
            if len(limit["conditions"]) > 8:
                raise ResourceLimit("conditions")
            scope = limit["scope"]
            kinds = limit["kinds"]
            if scope != "all":
                if type(scope) is not list or not scope:
                    raise VEError("InvalidInput: limitation scope")
                for right in scope:
                    if right not in self.rights:
                        raise VEError(f"UnknownRight: {right}")
            if kinds != "all" and (type(kinds) is not list or not kinds or
                                    not set(kinds) <= _KINDS):
                raise VEError("InvalidInput: limitation kinds")
            if not limit["decided_by"] or type(limit["decided_by"]) is not str:
                raise VEError(f"MissingExceptionDecider: limitation {limit['name']}")
            if any(type(factor) is not str or not factor for factor in limit["factors"]):
                raise VEError("InvalidInput: limitation factors")
            condition_names = set()
            for condition in limit["conditions"]:
                if (type(condition) is not dict or
                        not {"name", "role", "verbalisation", "decided_by"} <= set(condition) or
                        set(condition) - {"name", "role", "verbalisation", "decided_by", "purposes"} or
                        not valid_identifier(condition["name"]) or
                        condition["role"] not in ("necessary", "sufficient") or
                        type(condition["verbalisation"]) is not str or not condition["verbalisation"]):
                    raise VEError("InvalidInput: limitation condition")
                if condition["name"] in condition_names:
                    raise DuplicateDeclaration(f"condition {condition['name']}")
                condition_names.add(condition["name"])
                if condition["decided_by"] is None and not limit["decided_by"]:
                    raise VEError(f"MissingExceptionDecider: condition {condition['name']}")
                if (condition["decided_by"] is not None and
                        (type(condition["decided_by"]) is not str or not condition["decided_by"])):
                    raise VEError(f"MissingExceptionDecider: condition {condition['name']}")

    def _act(self, predicate):
        declaration = self.env.predicates[predicate]
        reg = declaration.regulated
        # A base predicate is its own act here; the line's decoder refuses it (`UnknownSymbol`), as Lean's does.
        return reg.permission if reg is not None and reg.role == "obligation" and reg.permission else predicate

    def _in_scope(self, limit, instance):
        return ((limit["scope"] == "all" or instance["right"] in limit["scope"])
                and (limit["kinds"] == "all" or instance["source_kind"] in limit["kinds"]))

    def _correlate(self):
        source = self.env.to_dict()
        source["profiles"].remove("rights@0")
        source["vocabulary"].pop("rights")
        predicates = source["vocabulary"]["predicates"]
        pairs = sorted({(limit["name"], self._act(instance["rule"].core.predicate))
                        for limit in self.limitations for instance in self.instances
                        if self._in_scope(limit, instance)})
        lim_names = {pair: f"rights__lim__{index}" for index, pair in enumerate(pairs, 1)}
        triples = sorted((limit["name"], act, condition["name"])
                         for limit in self.limitations for name, act in pairs if name == limit["name"]
                         for condition in limit["conditions"])
        cond_names = {triple: f"rights__cond__{index}" for index, triple in enumerate(triples, 1)}
        permissions = sorted({instance["rule"].core.predicate for instance in self.instances
                              if instance["kind"] in ("liberty", "powerLiberty")})
        bar_names = ({p: f"rights__bar__{i}" for i, p in enumerate(permissions, 1)}
                     if self.bar is not None else {})
        # 2.1: one fixed wording per generated predicate, by the limitation's display
        # number (document order) and the act phrase; the Lean route emits the same bytes.
        display = {item["name"]: number for number, item in enumerate(self.limitations, 1)}
        for (name, act), generated in lim_names.items():
            limit = next(item for item in self.limitations if item["name"] == name)
            args = list(self.env.predicates[act].arguments)
            predicates[generated] = {"arguments": args, "description": f"limitation {name} of {act}",
                                     "verbalisation": f"limitation {display[name]} holds where " +
                                     self.env.predicates[act].regulated.act}
            for condition in limit["conditions"]:
                generated_condition = cond_names[(name, act, condition["name"])]
                predicates[generated_condition] = {
                    "arguments": args, "description": f"condition {condition['name']} of limitation {name} on {act}",
                    "verbalisation": condition["verbalisation"] + " where " +
                    self.env.predicates[act].regulated.act}
        for predicate, generated in bar_names.items():
            decl = self.env.predicates[predicate]
            predicates[generated] = {"arguments": list(decl.arguments),
                                     "description": "act aimed at destruction of a right",
                                     "verbalisation": decl.regulated.act + " aimed at the destruction of a right"}
        env = SoftEnvironment(source, generated=True)
        # 2.1: the one English wording of each generated predicate, with the act
        # phrase conjugated for the "where" clause the declared template stands for.
        wordings = {}
        for (name, act), generated in lim_names.items():
            wordings[generated] = (f"limitation {display[name]} holds where " +
                                   conjugated(self.env.predicates[act].regulated.act))
        for (name, act, condition_name), generated in cond_names.items():
            limit = next(item for item in self.limitations if item["name"] == name)
            condition = next(item for item in limit["conditions"] if item["name"] == condition_name)
            wordings[generated] = (condition["verbalisation"] + " where " +
                                   conjugated(self.env.predicates[act].regulated.act))
        for predicate, generated in bar_names.items():
            wordings[generated] = (conjugated(self.env.predicates[predicate].regulated.act) +
                                   " aimed at the destruction of a right")
        object.__setattr__(env, "rights_wordings", wordings)
        rules = []
        for instance in self.instances:
            rule = instance["rule"]
            core = rule.core
            arity = len(env.predicates[core.predicate].arguments)
            holder_guard = self.rights[instance["right"]]["guard_formula"]
            guard = core.guard
            if not isinstance(holder_guard, Top):
                term = Var(arity - instance["holder_slot"] - 1)
                guard = And(guard, _instantiate(holder_guard, (term,)))
            covering = [lim_names[(limit["name"], self._act(core.predicate))]
                        for limit in self.limitations if self._in_scope(limit, instance)]
            # 4.1 step 5: six author carve-outs on every right line, covered or not.
            if len(core.unless) > 6:
                raise ResourceLimit(f"carve-outs of rule {core.name}")
            unless = core.unless + ((_or(_atom(name, arity) for name in covering),) if covering else ())
            rules.append(replace(rule, core=replace(core, guard=guard, unless=unless)))
        for unit in self.outside:
            raw = unit["norm"]
            _name(raw.get("name"))
            if any(type(parent) is str and parent.startswith("rights-")
                   for parent in raw.get("over", ())):
                raise VEError("InvalidInput: authored precedence cites a generated rule")
            rules.append(decode_rule(env, {"norm": raw}))
        if self.bar is not None and self.bar["reading"] == "rule":
            for index, predicate in enumerate(permissions, 1):
                parents = tuple(instance["rule"].core.name for instance in self.instances
                                if instance["rule"].core.predicate == predicate
                                and instance["rule"].core.sign)
                bar_rule = Norm(f"rights-bar-{index}", predicate, False,
                                _atom(bar_names[predicate], len(env.predicates[predicate].arguments)),
                                (), parents)
                rules.append(decode_rule(env, {"norm": {**bar_rule.to_dict()["norm"], "hard": True}}))
        self.environment = env
        self.soft_document = SoftNormDocument(env, [rule.to_dict() for rule in rules])
        self.limitation_names = lim_names
        self.condition_names = cond_names
        self.bar_names = bar_names
        premises = []
        for name, act, condition_name in triples:
            limit = next(item for item in self.limitations if item["name"] == name)
            condition = next(item for item in limit["conditions"] if item["name"] == condition_name)
            arity = len(env.predicates[act].arguments)
            lim = _atom(lim_names[(name, act)], arity)
            cond = _atom(cond_names[(name, act, condition_name)], arity)
            implication = Implies(lim, cond) if condition["role"] == "necessary" else Implies(cond, lim)
            label = f"rights:limitation:{name}:{act}:{condition['role']}:{condition_name}"
            premises.append((label, _bind(implication, env.predicates[act].arguments)))
        self.limitation_premises = tuple(premises)
        object.__setattr__(self.soft_document.extended_env, "rights_premises",
                           self.limitation_premises)
        object.__setattr__(self.soft_document.extended_env, "rights_wordings", wordings)
        self.wordings = wordings


def correlate(environment, units):
    """Return the validated holder-side document and its soft elaboration."""
    env = environment if isinstance(environment, RightsEnvironment) else RightsEnvironment(environment)
    return RightsDocument(env, units)
