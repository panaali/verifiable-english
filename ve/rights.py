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
from .errors import DuplicateDeclaration, ResourceLimit, UnsupportedProfile, VEError
from .norms import Norm, _bind, _instantiate
from .search import _used_predicates
from .softnorms import SoftEnvironment, SoftNormDocument, decode_rule

_RULE = re.compile(r"[a-z][a-z0-9-]*\Z", re.ASCII)
_KINDS = frozenset(("claim", "liberty", "immunity", "power"))


def _name(value):
    if type(value) is not str or len(value) > 64 or not _RULE.fullmatch(value):
        raise VEError(f"InvalidInput: invalid rights name {value!r}")
    if value.startswith("rights-"):
        raise VEError(f"InvalidInput: name {value} begins with rights-")
    return value


def _unique(values, kind):
    if type(values) is not list or not values:
        raise VEError(f"InvalidInput: {kind} must be a nonempty list")
    seen = set()
    for value in values:
        if value in seen:
            raise DuplicateDeclaration(f"{kind} {value}")
        seen.add(value)
    return tuple(values)


class RightsEnvironment(SoftEnvironment):
    """Validate and bind the rights block without changing older identities."""

    def __init__(self, data):
        if type(data) is not dict or "rights@0" not in data.get("profiles", []):
            raise UnsupportedProfile("rights@0 is required")
        if "soft-norms@0" not in data["profiles"]:
            raise UnsupportedProfile("rights@0 requires soft-norms@0")
        raw = deepcopy(data)
        rights = raw.get("vocabulary", {}).pop("rights", None)
        if type(rights) is not dict or set(rights) != {"holders", "bearers", "protected", "alters"}:
            raise VEError("InvalidInput: rights block")
        for predicate in raw["vocabulary"].get("predicates", ()):
            if predicate.startswith("rights__"):
                raise VEError(f"InvalidInput: author predicate {predicate} begins with rights__")
        object.__setattr__(self, "rights", rights)
        super().__init__(raw)
        holders = _unique(rights["holders"], "holder")
        bearers = _unique(rights["bearers"], "bearer")
        for sort in (*holders, *bearers):
            if sort not in self.sorts:
                raise VEError(f"UnknownSymbol: sort {sort}")
        object.__setattr__(self, "holders", holders)
        object.__setattr__(self, "bearers", bearers)
        protected = rights["protected"]
        if type(protected) is not list or len(set(protected)) != len(protected):
            raise VEError("InvalidInput: protected")
        for name in protected:
            decl = self.predicates.get(name)
            if (decl is None or decl.regulated is not None or decl.defined is not None
                    or not set(decl.arguments) & set(holders)):
                raise VEError(f"InvalidInput: protected {name}")
        alters = rights["alters"]
        if type(alters) is not dict:
            raise VEError("InvalidInput: alters")
        for act, entry in alters.items():
            declaration = self.predicates.get(act)
            if (type(entry) is not dict or set(entry) != {"holder_slot", "status", "recognition"}
                    or declaration is None or declaration.regulated is None
                    or declaration.regulated.role != "permission"):
                raise VEError(f"InvalidInput: alters {act}")
            slot = entry["holder_slot"]
            if type(slot) is not int or not 0 <= slot < len(declaration.arguments):
                raise VEError(f"InvalidInput: alters {act}")
            holder = declaration.arguments[slot]
            status = self.predicates.get(entry["status"])
            recognition = self.predicates.get(entry["recognition"]) if entry["recognition"] else None
            if (holder not in holders or status is None or status.regulated is not None
                    or status.defined is not None or holder not in status.arguments
                    or (entry["recognition"] is not None and
                        (recognition is None or recognition.regulated is None
                         or recognition.regulated.role != "obligation"
                         or recognition.arguments[0] not in bearers
                         or holder not in recognition.arguments))):
                raise VEError(f"InvalidInput: alters {act}")

    def to_dict(self):
        result = super().to_dict()
        result["vocabulary"]["rights"] = deepcopy(self.rights)
        return result


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
                      core.predicate in env.rights["alters"] and
                      env.rights["alters"][core.predicate]["holder_slot"] == slot)
    if not valid:
        raise VEError(f"IncidentShape: {core.name} on right {right['name']}")


class RightsDocument:
    """Validate source units and regenerate E'', T'', and limitation premises."""

    def __init__(self, env: RightsEnvironment, units):
        if not isinstance(env, RightsEnvironment):
            raise UnsupportedProfile("rights@0 is required")
        self.env = env
        if type(units) is not list or len(units) > 256:
            raise ResourceLimit("rights")
        rights = {}
        entries = []
        limitations = []
        bars = []
        outside = []
        names = set()
        for unit in units:
            if type(unit) is not dict or len(unit) != 1:
                raise VEError("InvalidInput: rights unit")
            kind, body = next(iter(unit.items()))
            if kind == "right":
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
        for name, right in rights.items():
            if not right["count"]:
                raise VEError(f"RightWithoutIncident: {name}")
        self.rights = rights
        self.limitations = tuple(limitations)
        self.bar = bars[0] if bars else None
        self.instances = tuple(self._instances(entries, names))
        self.outside = tuple(outside)
        self._validate_limitations(names)
        self._correlate()

    def _instances(self, entries, names):
        fan = 0
        for right_name, line in entries:
            right = self.rights[right_name]
            if type(line) is not dict or line.get("kind") not in _KINDS:
                raise VEError("InvalidInput: incident line")
            kind = line["kind"]
            if type(line.get("cites")) is not dict:
                raise VEError("InvalidInput: line citations")
            allowed = ({"kind", "cites", "liberty", "recognition", "holder_slot"} if kind == "power"
                       else {"kind", "cites", "norm", "holder_slot", "fan_out"})
            if set(line) - allowed or (kind == "power" and not {"liberty", "recognition"} <= set(line)):
                raise VEError("InvalidInput: incident line fields")
            norms = (("powerLiberty", line.get("liberty")),
                     ("powerRecognition", line.get("recognition"))) if kind == "power" else ((kind, line.get("norm")),)
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
                    rule = decode_rule(self.env, {"norm": norm})
                    slot = _slot(self.env, right, rule, line.get("holder_slot"),
                                 subject=instance_kind in ("liberty", "powerLiberty"))
                    _line_shape(self.env, right, instance_kind, rule, slot)
                    if instance_kind == "powerLiberty":
                        alter = self.env.rights["alters"].get(predicate)
                        if alter is None or alter["holder_slot"] != 0 or alter["recognition"] is None:
                            raise VEError(f"IncidentShape: {rule.core.name} on right {right_name}")
                    if instance_kind == "powerRecognition":
                        liberty = line["liberty"]["predicate"]
                        alter = self.env.rights["alters"].get(liberty)
                        if alter is None or predicate != alter["recognition"]:
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
                           "rule": rule, "holder_slot": slot, "cites": line["cites"],
                           "bearer": bearer}

    def _validate_limitations(self, names):
        for limit in self.limitations:
            if (set(limit) != {"name", "scope", "kinds", "decided_by", "conditions", "factors"}
                    or type(limit["conditions"]) is not list or type(limit["factors"]) is not list):
                raise VEError("InvalidInput: limitation")
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
        return reg.permission if reg.role == "obligation" and reg.permission else predicate

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
        bar_names = {p: f"rights__bar__{i}" for i, p in enumerate(permissions, 1)}
        for (name, act), generated in lim_names.items():
            limit = next(item for item in self.limitations if item["name"] == name)
            args = list(self.env.predicates[act].arguments)
            predicates[generated] = {"arguments": args, "description": f"limitation {name} of {act}",
                                     "verbalisation": f"limitation {name} holds where " +
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
            unless = core.unless + ((_or(_atom(name, arity) for name in covering),) if covering else ())
            if len(core.unless) > 6 and covering:
                raise ResourceLimit(f"carve-outs of rule {core.name}")
            rules.append(replace(rule, core=replace(core, guard=guard, unless=unless)))
        for unit in self.outside:
            raw = unit["norm"]
            _name(raw.get("name"))
            if any(type(parent) is str and parent.startswith("rights-")
                   for parent in raw.get("over", ())):
                raise VEError("InvalidInput: authored precedence cites a generated rule")
            rules.append(decode_rule(env, unit))
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


def correlate(environment, units):
    """Return the validated holder-side document and its soft elaboration."""
    env = environment if isinstance(environment, RightsEnvironment) else RightsEnvironment(environment)
    return RightsDocument(env, units)
