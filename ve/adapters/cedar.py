"""Cedar's no-attribute fragment as a finite request norm document.

The parser is shared with the pinned reference interpreter; expression
evaluation below is independent.  Values are represented as finite tagged
cases guarded by FOL formulas. An ill-typed path has no case and therefore
cannot activate a rule. This preserves Cedar short-circuit behavior and lets
the adapter report erroring policies separately from excluded policies.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import importlib.util
from pathlib import Path
import re

from ..ast import And, Binary, Bottom, Const, Eq, Not, Or, Reach, Named, Top, Unary, Var
from ..environment import Environment
from ..errors import ResourceLimit, VEError
from ..evaluate import _Evaluator
from ..model import FiniteModel
from ..norms import Norm, NormDocument


def _any(items):
    """Keep finite case splits within the formula depth budget."""
    row = list(items)
    if not row:
        return Bottom()
    while len(row) > 1:
        row = [Or(row[i], row[i + 1]) if i + 1 < len(row) else row[i]
               for i in range(0, len(row), 2)]
    return row[0]
from ..profiles import LANGUAGE, SPEC_REVISION


def _parser_module():
    path = Path(__file__).resolve().parents[2] / "experiments/P3-formalisation-tax/reference_cedar.py"
    spec = importlib.util.spec_from_file_location("ve_cedar_reference_parser", path)
    module = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _entity(value):
    return ("entity", value.type, value.id)


def _literal(value):
    if hasattr(value, "type") and hasattr(value, "id"):
        return _entity(value)
    if type(value) is bool:
        return ("bool", value)
    if type(value) is str:
        return ("string", value)
    if type(value) is int:
        return ("long", value)
    raise _Excluded("value-representation")


def _and(a, b):
    return And(a, b)


def _or(a, b):
    return Or(a, b)


class _Excluded(Exception):
    pass


@dataclass(frozen=True)
class _Case:
    guard: object
    value: tuple


def _bool(cases):
    return tuple(c for c in cases if c.value[0] == "bool")


def _select(cases, truth):
    return _any(c.guard for c in cases if c.value == ("bool", truth))


class _Compiler:
    def __init__(self, entity_symbols, slots, possible):
        self.symbols = entity_symbols
        self.slots = slots
        self.entities = tuple(entity_symbols)
        self.possible = possible

    def _limit(self, cases):
        if len(cases) > 4096:
            raise ResourceLimit("Cedar value cases")
        return tuple(cases)

    def _var(self, name):
        if name == "context":
            raise _Excluded("context")
        if name not in ("principal", "action", "resource"):
            raise _Excluded("value-representation")
        return tuple(_Case(Binary(name, Var(0), Const(self.symbols[e])), e)
                     for e in self.possible[name])

    def _reach(self, a, b):
        return Reach("star", Named("parent"), Const(self.symbols[a]), Const(self.symbols[b]))

    def _membership(self, a, b):
        if a[0] != "entity":
            return None
        if b[0] == "entity":
            return self._reach(a, b)
        if b[0] == "set":
            if any(x[0] != "entity" for x in b[1]):
                return None
            return _any(self._reach(a, x) for x in sorted(b[1]))
        return None

    def _logical(self, op, left, right):
        a = _bool(self.compile(left))
        cases = []
        for c in a:
            short = (op == "&&" and c.value[1] is False) or (op == "||" and c.value[1] is True)
            if short:
                cases.append(c)
                continue
            for d in _bool(self.compile(right)):
                cases.append(_Case(_and(c.guard, d.guard), d.value))
        return self._limit(cases)

    def compile(self, node):
        tag = node[0]
        if tag == "lit":
            return (_Case(Top(), _literal(node[1])),)
        if tag == "var":
            return self._var(node[1])
        if tag == "slot":
            if node[1] not in self.slots:
                return ()
            return (_Case(Top(), _entity(self.slots[node[1]])),)
        if tag in ("&&", "||"):
            return self._logical(tag, node[1], node[2])
        if tag == "!":
            return tuple(_Case(c.guard, ("bool", not c.value[1])) for c in _bool(self.compile(node[1])))
        if tag == "if":
            cases = []
            for c in _bool(self.compile(node[1])):
                branch = node[2] if c.value[1] else node[3]
                for d in self.compile(branch):
                    cases.append(_Case(_and(c.guard, d.guard), d.value))
            return self._limit(cases)
        if tag == "setlit":
            members = [self.compile(x) for x in node[1]]
            cases = []
            for combo in product(*members):
                values = frozenset(c.value for c in combo)
                guard = Top()
                for c in combo:
                    guard = _and(guard, c.guard)
                cases.append(_Case(guard, ("set", values)))
            return self._limit(cases)
        if tag == "rel":
            op = node[1]
            if op not in ("==", "!=", "in"):
                raise _Excluded("comparison")
            cases = []
            for a, b in product(self.compile(node[2]), self.compile(node[3])):
                guard = _and(a.guard, b.guard)
                if op == "in":
                    member = self._membership(a.value, b.value)
                    if member is None:
                        continue
                    cases.extend((_Case(_and(guard, member), ("bool", True)),
                                  _Case(_and(guard, Not(member)), ("bool", False))))
                else:
                    equal = a.value == b.value
                    cases.append(_Case(guard, ("bool", equal if op == "==" else not equal)))
            return self._limit(cases)
        if tag == "is":
            cases = []
            for a in self.compile(node[1]):
                if a.value[0] != "entity":
                    continue
                matches = a.value[1] == node[2]
                if not matches or node[3] is None:
                    cases.append(_Case(a.guard, ("bool", matches)))
                else:
                    for b in self.compile(("rel", "in", ("lit", _Entity(*a.value[1:])), node[3])):
                        cases.append(_Case(_and(a.guard, b.guard), b.value))
            return self._limit(cases)
        if tag in ("has", "attr"):
            raise _Excluded("attribute")
        if tag == "like":
            raise _Excluded("like")
        if tag == "arith" or tag == "neg":
            raise _Excluded("arithmetic")
        if tag == "method":
            raise _Excluded("set-op")
        if tag == "call":
            raise _Excluded("extension-function")
        raise _Excluded("value-representation")

    def scope(self, variable, item):
        kind = item[0]
        if kind == "any":
            return (_Case(Top(), ("bool", True)),)
        left = ("var", variable)
        if kind in ("==", "in"):
            reference = item[1]
            right = (("slot", reference[1]) if reference[0] == "slot" else
                     ("setlit", [("lit", x) for x in reference[1]]) if reference[0] == "set" else
                     ("lit", reference[1]))
            return self.compile(("rel", kind, left, right))
        if kind == "is":
            return self.compile(("is", left, item[1], None))
        if kind == "is_in":
            reference = item[2]
            right = (("slot", reference[1]) if reference[0] == "slot" else
                     ("setlit", [("lit", x) for x in reference[1]]) if reference[0] == "set" else
                     ("lit", reference[1]))
            return self.compile(("is", left, item[1], right))
        raise _Excluded("value-representation")

    def policy(self, policy):
        cases = (_Case(Top(), ("bool", True)),)
        for variable, item in zip(("principal", "action", "resource"), policy["scope"]):
            cases = self._logical_cases(cases, self.scope(variable, item))
        for kind, condition in policy["conds"]:
            values = _bool(self.compile(condition))
            if kind == "unless":
                values = tuple(_Case(c.guard, ("bool", not c.value[1])) for c in values)
            cases = self._logical_cases(cases, values)
        return cases

    def _logical_cases(self, left, right):
        out = []
        for a in _bool(left):
            if not a.value[1]:
                out.append(a)
            else:
                out.extend(_Case(_and(a.guard, b.guard), b.value) for b in _bool(right))
        return self._limit(out)


@dataclass(frozen=True)
class _Entity:
    type: str
    id: str


@dataclass(frozen=True)
class CedarTranslation:
    environment: Environment
    document: NormDocument
    model: FiniteModel
    request_ids: tuple[str, ...]
    policy_defined: tuple[tuple[str, object], ...]
    exclusions: tuple[tuple[str, str], ...]

    def decisions(self):
        active_exclusions = tuple(item for item in self.exclusions if item[1] != "template-unlinked")
        if active_exclusions:
            return tuple({"decision": None, "errors": (), "excluded": active_exclusions}
                         for _ in self.request_ids)
        evaluator = _Evaluator(self.environment, self.model, 1_000_000, trace=False)
        outcome = self.document.outcome("permitted")
        reports = []
        for request_id in self.request_ids:
            binding = (("request", request_id),)
            permitted = evaluator.formula(outcome, binding)[0]
            errors = tuple(name for name, defined in self.policy_defined
                           if not evaluator.formula(defined, binding)[0])
            reports.append({"decision": "allow" if permitted else "deny", "errors": errors})
        return tuple(reports)


def _walk(value):
    if hasattr(value, "type") and hasattr(value, "id"):
        yield _entity(value)
    elif isinstance(value, (tuple, list)):
        for item in value:
            yield from _walk(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from _walk(item)


def translate(policy_text, linked, entities, requests):
    """Translate the listed requests; unsupported policies are reported explicitly."""
    parser = _parser_module()
    instances = parser.instantiate(policy_text, linked)
    all_policies = parser.parse_policies(policy_text)
    linked_ids = {x["template_id"] for x in linked or []}
    unlinked = tuple((p["annotations"].get("id") or f"policy{i}", "template-unlinked")
                     for i, p in enumerate(all_policies)
                     if parser._has_slot(p) and (p["annotations"].get("id") or f"policy{i}") not in linked_ids)
    entity_values = set(_walk(instances))
    for item in entities:
        entity_values.add(_entity(parser.parse_uid(item["uid"])))
        entity_values.update(_entity(parser.parse_uid(x)) for x in item.get("parents", []))
    for request in requests:
        entity_values.update(_entity(parser.parse_uid(request[key]))
                             for key in ("principal", "action", "resource"))
    ordered_entities = tuple(sorted(entity_values))
    symbols = {e: f"entity{i}" for i, e in enumerate(ordered_entities)}
    possible = {key: tuple(sorted({_entity(parser.parse_uid(request[key])) for request in requests}))
                for key in ("principal", "action", "resource")}
    compiler_base = lambda slots: _Compiler(symbols, slots, possible)
    rules, defined, exclusions = [], [], list(unlinked)
    used_names = set()
    for index, (policy, slots) in enumerate(instances):
        pid = policy["id"]
        name = re.sub(r"[^a-z0-9-]", "-", pid.lower()).strip("-")
        name = (name if name and name[0].isalpha() else f"policy-{index}")[:48]
        while name in used_names:
            name += "-copy"
        used_names.add(name)
        try:
            cases = compiler_base(slots).policy(policy)
        except _Excluded as exc:
            exclusions.append((pid, str(exc)))
            continue
        guard = _select(cases, True)
        defined.append((pid, _any(c.guard for c in cases)))
        rules.append((name, pid, policy["effect"], guard))
    permits = tuple(name for name, _, effect, _ in rules if effect == "permit")
    norm_rules = [Norm(name, "permitted", effect == "permit", guard, (),
                       permits if effect == "forbid" else ())
                  for name, _, effect, guard in rules]
    predicates = {
        name: {"arguments": ["request", "entity"], "description": f"Cedar {name} relation"}
        for name in ("principal", "action", "resource")}
    predicates["parent"] = {"arguments": ["entity", "entity"], "description": "Cedar parent edge"}
    predicates["permitted"] = {"arguments": ["request"], "description": "Cedar permission",
                               "regulated": {"role": "permission", "default": "deny",
                                             "act": "{0} be allowed"}}
    env = Environment({"language": LANGUAGE,
                       "profiles": ["closure@0", "norms@0", "relational-fol@0"],
                       "spec_revision": SPEC_REVISION,
                       "vocabulary": {"sorts": {"request": {"description": "request"},
                                                "entity": {"description": "entity"}},
                                      "predicates": predicates,
                                      "constants": {**{symbol: {"sort": "entity", "description": str(e)}
                                                       for e, symbol in symbols.items()}}}})
    document = NormDocument(env, norm_rules)
    request_ids = tuple(f"request{i}" for i in range(len(requests)))
    relations = {name: [] for name in predicates}
    for request_id, request in zip(request_ids, requests):
        for key in ("principal", "action", "resource"):
            relations[key].append([request_id, symbols[_entity(parser.parse_uid(request[key]))]])
    for item in entities:
        child = symbols[_entity(parser.parse_uid(item["uid"]))]
        for parent in item.get("parents", []):
            relations["parent"].append([child, symbols[_entity(parser.parse_uid(parent))]])
    model = FiniteModel.from_dict(env, {"complete": True,
                                        "domains": {"request": list(request_ids),
                                                    "entity": list(symbols.values())},
                                        "constants": {symbol: symbol for symbol in symbols.values()},
                                        "relations": relations})
    return CedarTranslation(env, document, model, request_ids,
                            tuple(defined), tuple(exclusions))
