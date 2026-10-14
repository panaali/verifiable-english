"""Every field of every RD-9 relayed answer is classified, and every bound field is fuzzed (DRI ruling R8).

The class behind F11 to F23 and `reviews/rd-9-binding-audit.md`: a field of a Lean answer that Python
reads, shows or sends back to Lean without tying it to the request. F22 (`conflict_targets[].sorts`)
and F23 (`lines[].holder_slot`) were missed because they were listed as unused. Here the field list is
walked from the generated response schemas (`ve/backends/lean_service_schema/`), so a field that a Lean
shape adds cannot go unclassified. Each field is either

* BOUND: every one-fault mutant of a genuine answer that still fits the schema is `CheckerUnavailable`
  at the public relay (UNORDERED: the same, except that Lean's order of the list is not an identity;
  COUNTED: a list with one item per request item, each item Lean's value), or
* LEAN: a value Lean derives and its encoder theorem covers (a formula, a hash, a verdict, Lean's
  English), with the reason.

The mutants rename a value to an undeclared one, shift a number, flip a flag, drop, duplicate or extend
a list or map, and reverse an ordered list, at every position the field takes in a genuine answer.
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import pytest

from ve import rights_route, soft_route
from ve.backends.service_schema import Invalid, check_row, same_json
from ve.errors import CheckerUnavailable

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "ve/backends/lean_service_schema"

# Each relayed RD-9 answer: its service mode and the schema definition of its row.
ROUTES = {
    "soft-elaborate": ("soft-norms", "soft-norms.json", "elaborate"),
    "soft-pairs": ("soft-norms", "soft-norms.json", "pairs"),
    "soft-conflict": ("soft-norms", "soft-norms.json", "packages"),
    "soft-conflict-witness": ("soft-norms", "soft-norms.json", "witness"),
    "soft-admission": ("soft-norms", "soft-norms.json", "admission"),
    "rights-elaborate": ("rights", "rights.json", "elaborate"),
    "rights-scope": ("rights", "rights.json", "scope"),
    "rights-bar": ("rights", "rights.json", "bar"),
    "rights-conflict": ("rights", "rights.json", "packages"),
    "rights-conflict-witness": ("rights", "soft-norms.json", "witness"),
    "rights-admission": ("rights", "rights.json", "admission"),
}


# ---------------------------------------------------------------------------------------------------
# The field list, walked from the generated schemas.

def _load(name, cache={}):
    if name not in cache:
        cache[name] = json.loads((SCHEMAS / name).read_text())
    return cache[name]


def _resolve(ref, base):
    name, _, pointer = ref.partition("#")
    name = name or base
    node = _load(name)
    for part in pointer.strip("/").split("/"):
        if part:
            node = node[part.replace("~1", "/").replace("~0", "~")]
    return node, name


def _walk(node, base, path, out, stack=()):
    if not isinstance(node, dict):
        return
    if "x-tagged" in node:
        out.setdefault(path, set()).add("formula")
        return
    if "$ref" in node:
        ref = node["$ref"] if node["$ref"].split("#")[0] else base + node["$ref"]
        if ref in stack:
            out.setdefault(path, set()).add("formula")
        else:
            target, name = _resolve(ref, base)
            _walk(target, name, path, out, stack + (ref,))
    for key in ("anyOf", "allOf", "oneOf", "prefixItems"):
        for sub in node.get(key, ()):
            _walk(sub, base, path + "[]" if key == "prefixItems" else path, out, stack)
    for selected in node.get("x-select", ()):
        _walk(selected["then"], base, path, out, stack)
    for key in ("then", "else"):
        _walk(node.get(key), base, path, out, stack)
    if "properties" in node:
        out.setdefault(path, set()).add("object")
        for name, sub in node["properties"].items():
            _walk(sub, base, f"{path}.{name}" if path else name, out, stack)
    elif node.get("type") == "object" and not isinstance(node.get("additionalProperties"), dict):
        out.setdefault(path, set()).add("record")
    if isinstance(node.get("additionalProperties"), dict):
        out.setdefault(path, set()).add("map")
        _walk(node["additionalProperties"], base, path + "{}", out, stack)
    if "items" in node or "prefixItems" in node:
        out.setdefault(path, set()).add("array")
        _walk(node.get("items"), base, path + "[]", out, stack)
    if node.get("type") in ("string", "integer", "boolean") or "const" in node or "enum" in node:
        out.setdefault(path, set()).add("scalar")


def schema_fields(route):
    """Every field path of the route's row (`a.b`, `a[]` an item, `a{}` a map value) with its kinds."""
    _, name, definition = ROUTES[route]
    out = {}
    _walk(_load(name)["$defs"][definition], name, "", out)
    return {path: kinds for path, kinds in out.items() if path and kinds != {"object"}}


# ---------------------------------------------------------------------------------------------------
# The classification. One entry per schema field; the test below fails on a missing or extra entry.

BOUND, UNORDERED = "bound", "bound, unordered"
COUNTED = "bound count, each item Lean's"  # rows are bound one per request item; their values are Lean's
FUZZED = (BOUND, UNORDERED, COUNTED)


def lean(reason):
    return "lean: " + reason


FORMULA = lean("a formula Lean generates; its encoder theorem covers it")

_SOFT_CORE = {
    "id": BOUND, "status": BOUND,
    "background": lean("Background' is Lean's regeneration; its soft rows are request identities, bound by label"),
    "background[].ast": FORMULA, "background[].generator": BOUND, "background[].label": BOUND,
    "colliding_pairs": UNORDERED, "colliding_pairs[].act": BOUND, "colliding_pairs[].ast": FORMULA,
    "colliding_pairs[].comparable": BOUND, "colliding_pairs[].label": BOUND,
    "colliding_pairs[].outweighs": BOUND, "colliding_pairs[].pair": BOUND, "colliding_pairs[].pair[]": BOUND,
    "conditional_on": UNORDERED, "conditional_on[]": BOUND,
    "conflict_targets": UNORDERED, "conflict_targets[].ast": FORMULA, "conflict_targets[].sorts": BOUND,
    "conflict_targets[].sorts[]": BOUND, "conflict_targets[].target": BOUND,
    "decisions": UNORDERED, "decisions[].arguments": BOUND, "decisions[].arguments[]": BOUND,
    "decisions[].key.excepted": BOUND, "decisions[].key.higher": BOUND,
    "decisions[].key.lower": BOUND, "decisions[].key.off": BOUND, "decisions[].key.outweighs": BOUND,
    "decisions[].key.party": BOUND, "decisions[].name": BOUND,
    "derived": UNORDERED, "derived[].ast": lean("a rule's derived carve-out, or null"), "derived[].rule": BOUND,
    "environment_prime.language": BOUND, "environment_prime.profiles": BOUND,
    "environment_prime.profiles[]": BOUND, "environment_prime.spec_revision": BOUND,
    "environment_prime.vocabulary.constants": BOUND, "environment_prime.vocabulary.predicates": BOUND,
    "environment_prime.vocabulary.predicates{}.arguments": BOUND,
    "environment_prime.vocabulary.predicates{}.arguments[]": BOUND,
    "environment_prime.vocabulary.rights": BOUND, "environment_prime.vocabulary.soft": BOUND,
    "environment_prime.vocabulary.sorts": BOUND,
    "fragment": lean("whether the document is in Lean's decided fragment"),
    "order": UNORDERED, "order[]": BOUND,
    "premises": UNORDERED, "premises[].ast": FORMULA, "premises[].label": BOUND,
    "warnings": lean("Lean's diagnostics"), "warnings[]": lean("Lean's diagnostics"),
}

_WITNESS = {  # Rows that answer submitted witnesses; no Python relay submits one, so any row is extra.
    f"{field}{rest}": BOUND for field in ("overlaps", "override_cycles")
    for rest in ("", "[].line", "[].model.complete", "[].model.constants",
                 "[].model.constants{}", "[].model.domains", "[].model.domains{}", "[].model.domains{}[]",
                 "[].model.relations", "[].model.relations{}", "[].model.relations{}[]",
                 "[].model.relations{}[][]", "[].tuple", "[].tuple[]")
} | {"overlaps[].pair": BOUND, "overlaps[].pair[]": BOUND,
     "override_cycles[].cycle": BOUND, "override_cycles[].cycle[]": BOUND}

_NARROWINGS = {
    "narrowings": UNORDERED, "narrowings[].right": BOUND, "narrowings[].rule": BOUND,
    "narrowings[].in_scope": BOUND, "narrowings[].mechanisms": BOUND,
    "narrowings[].mechanisms[].conclusion": FORMULA, "narrowings[].mechanisms[].licence": BOUND,
    "narrowings[].mechanisms[].mechanism": BOUND, "narrowings[].mechanisms[].target": BOUND,
}

_ADMISSION = {
    "id": BOUND, "status": BOUND, "admitted": BOUND, "conditional_on": BOUND, "conditional_on[]": BOUND,
    "report.assumptions": BOUND, "report.assumptions[].ast": FORMULA,
    "report.assumptions[].label": BOUND, "report.assumptions[].name": BOUND,
    "report.root.ast": FORMULA, "report.root.label": BOUND, "report.root.name": BOUND,
    "report_id": lean("the report's identity hash"),
}

INVENTORY = {
    "soft-elaborate": {
        **_SOFT_CORE, **_WITNESS,
        "default_exceptions_by_decider": BOUND, "default_exceptions_by_decider{}": BOUND,
        "document_hash": lean("the document's identity hash"),
        "incompatible_pairs": UNORDERED, "incompatible_pairs[]": BOUND, "incompatible_pairs[][]": BOUND,
        "ranks_above": BOUND, "ranks_above{}": UNORDERED, "ranks_above{}[]": BOUND,
        "rule_acts": BOUND, "rule_acts{}": BOUND,
        "soft_residual.default_exceptions": BOUND, "soft_residual.holistic_overrides": BOUND,
        "soft_residual.instruction_switches": BOUND, "soft_residual.weighing_points": BOUND,
        "soft_status": lean("the soft status Lean decides"),
    },
    "rights-elaborate": {
        **_SOFT_CORE, **_NARROWINGS,
        "bars": UNORDERED, "bars[].guard": FORMULA, "bars[].hard": BOUND, "bars[].mode": BOUND,
        "bars[].name": BOUND, "bars[].over": BOUND, "bars[].over[]": BOUND, "bars[].predicate": BOUND,
        "bars[].sign": BOUND, "bars[].unless": BOUND, "bars[].unless[]": FORMULA,
        "distinction": UNORDERED, "distinction[].predicate": BOUND,
        "distinction[].independent": lean("whether the predicate's cone is protected-free"),
        "distinction[].hits": lean("which lines in the cone mention a protected predicate; each hit is bound"),
        "distinction[].hits[].cited": BOUND, "distinction[].hits[].protected": BOUND,
        "distinction[].hits[].right": BOUND, "distinction[].hits[].rule": BOUND,
        "findings": BOUND, "findings[]": BOUND,
        "generated": UNORDERED, "generated[].act": BOUND, "generated[].condition": BOUND,
        "generated[].kind": BOUND, "generated[].limitation": BOUND, "generated[].name": BOUND,
        "generated[].predicate": BOUND,
        "limitations": UNORDERED, "limitations[].ast": FORMULA, "limitations[].label": BOUND,
        "lines": BOUND, "lines[].bearer": BOUND, "lines[].holder_slot": BOUND, "lines[].instance": BOUND,
        "lines[].kind": BOUND, "lines[].node.guard": FORMULA, "lines[].node.hard": BOUND,
        "lines[].node.mode": BOUND, "lines[].node.name": BOUND, "lines[].node.over": BOUND,
        "lines[].node.over[]": BOUND, "lines[].node.predicate": BOUND, "lines[].node.sign": BOUND,
        "lines[].node.unless": BOUND, "lines[].node.unless[]": lean(
            "an authored carve-out as Lean re-encodes it, or the limitation pack Lean generates"),
        "lines[].predicate": BOUND, "lines[].right": BOUND, "lines[].rule": BOUND,
        "lines[].source_line": BOUND,
        "rights_background": BOUND, "rights_background[].ast": BOUND, "rights_background[].generator": BOUND,
        "rights_background[].label": BOUND,
        "unit_open": COUNTED, "unit_open[]": lean("whether Lean finds an open term in the unit"),
        "wordings": BOUND, "wordings{}": lean("Lean's English for a generated predicate; its placeholders are bound"),
    },
    "rights-scope": {
        **_NARROWINGS, "id": BOUND, "status": BOUND, "findings": BOUND, "findings[]": BOUND, "licensed": BOUND,
    },
    "rights-bar": {
        "id": BOUND, "status": BOUND, "bars": BOUND, "bars[].aimed": BOUND, "bars[].barred": BOUND,
        "bars[].barred[]": BOUND, "bars[].blocked_defaults": BOUND, "bars[].blocked_defaults[]": BOUND,
        "bars[].composition_candidates": BOUND, "bars[].composition_candidates[]": BOUND,
        "bars[].entailed": lean("whether Lean proves the bar's target"), "bars[].predicate": BOUND,
        "bars[].reading": BOUND, "bars[].target": FORMULA,
    },
    "rights-conflict": {
        "id": BOUND, "status": BOUND, "targets": BOUND, "targets[]": BOUND,
        "conditional_on": lean("which premises Lean's conflict check used; each label is bound"),
        "conditional_on[]": BOUND, "detail": lean("Lean's detail line"), "verdict": lean("Lean's verdict"),
        "status_text": lean("Lean's verdict line; its counts are bound for CONFLICT-FREE"),
    },
    "soft-pairs": {
        "id": BOUND, "status": BOUND, "pairs": BOUND, "pairs[].pair": BOUND, "pairs[].pair[]": BOUND,
        "pairs[].label": BOUND, "pairs[].status": lean("each pair's classification"),
        "pairs[].detail": lean("Lean's detail line"), "discharged": BOUND, "discharged[]": BOUND,
        "weighing_points": BOUND, "weighing_points[]": BOUND,
    },
    "soft-conflict": {
        "id": BOUND, "status": BOUND, "targets": BOUND, "targets[]": BOUND, "budget": BOUND,
        "conditional_on": lean("which open premises Lean's conflict check used; each label is bound"),
        "conditional_on[]": BOUND, "coherent_exhibit": lean("whether Lean checked the coherent model"),
        "detail": lean("Lean's detail line"), "status_text": lean("Lean's verdict line"),
        "verdict": lean("Lean's verdict"),
    },
    "soft-conflict-witness": {
        "id": BOUND, "status": BOUND, "targets": BOUND, "targets[]": BOUND, "target": BOUND,
        "status_text": lean("Lean's verdict line"), "verdict": lean("Lean's verdict"),
        "witness_kind": lean("the witness kind Lean replayed"),
    },
    "rights-conflict-witness": {
        "id": BOUND, "status": BOUND, "targets": BOUND, "targets[]": BOUND, "target": BOUND,
        "status_text": lean("Lean's verdict line"), "verdict": lean("Lean's verdict"),
        "witness_kind": lean("the witness kind Lean replayed"),
    },
    "soft-admission": {**_ADMISSION, "kinds": BOUND, "kinds[]": BOUND},
    "rights-admission": _ADMISSION,
}


@pytest.mark.parametrize("route", sorted(ROUTES))
def test_every_schema_field_is_classified(route):
    fields = schema_fields(route)
    assert set(INVENTORY[route]) == set(fields), (
        f"unclassified: {sorted(set(fields) - set(INVENTORY[route]))}; "
        f"not in the schema: {sorted(set(INVENTORY[route]) - set(fields))}")
    for path, kind in INVENTORY[route].items():
        assert kind in FUZZED or kind.startswith("lean: "), path


# ---------------------------------------------------------------------------------------------------
# One-fault mutants of a genuine answer.

_TOKEN = re.compile(r"\[\]|\{\}|[^.\[\]{}]+")


def _locate(value, tokens, parent=None, key=None):
    if not tokens:
        yield parent, key
        return
    head, rest = tokens[0], tokens[1:]
    if head == "[]" and type(value) is list:
        for index, item in enumerate(value):
            yield from _locate(item, rest, value, index)
    elif head == "{}" and type(value) is dict:
        for name, item in value.items():
            yield from _locate(item, rest, value, name)
    elif head not in ("[]", "{}") and type(value) is dict and head in value:
        yield from _locate(value[head], rest, value, head)


def _edits(value, ordered):
    """The one-fault replacements of `value`, with their names."""
    if type(value) is str or value is None:
        yield "renamed", "ghost"
    elif type(value) is bool:
        yield "flipped", not value
    elif type(value) is int:
        yield "shifted", value + 1
        yield "far", 99
    elif type(value) is list:
        if value:
            yield "emptied", []
            yield "last dropped", value[:-1]
            yield "first duplicated", [value[0], *value]
        if all(type(item) is str for item in value):
            yield "extended", [*value, "ghost"]
        if ordered and len(value) > 1 and value != value[::-1]:
            yield "reversed", value[::-1]
    elif type(value) is dict:
        if value:
            first = next(iter(value))
            yield "key dropped", {k: v for k, v in value.items() if k != first}
            yield "key added", {**value, "ghost": copy.deepcopy(value[first])}
        else:
            yield "key added", {"ghost": "ghost"}


def mutants(row, route):
    """Every one-fault mutant of `row` at a bound field, as (path, edit, mutant)."""
    for path, kind in sorted(INVENTORY[route].items()):
        if kind not in FUZZED:
            continue
        tokens = _TOKEN.findall(path)
        for index, (parent, key) in enumerate(_locate(row, tokens)):
            for edit, replacement in _edits(parent[key], ordered=kind == BOUND):
                mutant = copy.deepcopy(row)
                target_parent, target_key = list(_locate(mutant, tokens))[index]
                target_parent[target_key] = replacement
                if not same_json(mutant, row):
                    yield path, f"{edit} at {index}", mutant


def located(row, route):
    """The bound paths that occur in `row`."""
    return {path for path, kind in INVENTORY[route].items()
            if kind in FUZZED and any(True for _ in _locate(row, _TOKEN.findall(path)))}


# ---------------------------------------------------------------------------------------------------
# Genuine answers and their public relays.

def _soft_sources():
    from tests.test_soft_norms_lean import env, ranks, should
    return {
        "holistic": (env(ranks(["a", "b"], "holistic", parties=("user",))),
                     [should("h", "x_required", True, rank="a", alterable=["user"]),
                      should("l", "x_required", False, rank="b")]),
        "open pair": (env(), [should("a", "x_required", True), should("b", "x_permitted", False)]),
        "witness": (env(perm="deny"), [should("s", "x_required", True)]),
    }


def _soft_calls(name, document, raw, norms):
    from tests.test_soft_norms_lean import model, packages
    from ve.soft_route import admit_soft_document, check_soft_conflict, classify_soft_pairs, \
        elaborate_soft_document
    elaborated = elaborate_soft_document(document)
    leaf = next((entry for entry in elaborated["background"] if entry.get("label", "").startswith("soft:coherence:")),
                elaborated["premises"][0])
    admission = {"units": [{"id": f"u{i}", "span": [10 * i, 10 * i + 5], "kind": "norm", "content": n}
                           for i, n in enumerate(norms)],
                 "graph": {"root": "leaf", "nodes": [{"name": "leaf", "ast": leaf["ast"], "label": leaf["label"]}]}}
    certified = packages(raw, norms, elaborated)
    witness = {"target": "x_required->x_permitted", "model": model({"soft__excepted__s": []}), "tuple": ["a"]}
    return {
        "soft-elaborate": lambda: elaborate_soft_document(document),
        "soft-pairs": lambda: classify_soft_pairs(document),
        "soft-conflict": lambda: check_soft_conflict(document, packages=certified, budget=7),
        "soft-admission": lambda: admit_soft_document(document.env, admission, soft_document=document),
        **({"soft-conflict-witness": lambda: check_soft_conflict(document, witness=witness)}
           if name == "witness" else {}),
    }


def _soft_route_of(case):
    kind = case["kind"]
    return ("soft-admission" if kind == "admission" else
            "soft-conflict-witness" if kind == "soft-conflict" and "witness" in case else kind)


def _rights_sources():
    from tests.test_norms import obligation, permission
    from tests.test_rights_lean import ARBITRARY, ARREST, GAMMA, IMPART, BLOCK, base, env, line, norm, right
    from tests.test_soft_decision_keys import _default_gamma, _fan_out_source
    from tests.test_soft_norms_lean import DECIDER, ranks

    def default(name, predicate, sign, **soft):
        return norm(name, predicate, sign, mode="default", exception=dict(DECIDER), **soft)

    holistic = env(ARREST, rights={**BLOCK, "protected": ["arbitrary_arrest"]})
    holistic["vocabulary"]["soft"] = ranks(["a", "b"], "holistic", parties=("person",))
    weighed = [right("r9", [line("claim", default("no-arbitrary-arrest", "arrest_permitted", False, guard=ARBITRARY,
                                                  rank="a", alterable=["person"]))]),
               {"norm": default("may-arrest", "arrest_permitted", True, rank="b")}]
    over = [right("r9", [line("claim", norm("no-arbitrary-arrest", "arrest_permitted", False, guard=ARBITRARY,
                                            over=["may-arrest"]))]),
            {"norm": default("may-arrest", "arrest_permitted", True)}]
    impart = env(IMPART, sorts=("person", "idea"), rights={"holders": ["person"], "bearers": ["person"]})
    carve = copy.deepcopy(GAMMA)
    carve[0]["right"]["lines"][0]["norm"]["unless"] = [["top"]]
    # The wire spells an absent optional field as null too (`rights_route._wire`); a genuine answer
    # to such a source must be accepted (the class of a refused genuine answer, N9).
    nulls = copy.deepcopy(GAMMA)
    nulls[0]["right"]["lines"][0].update(holder_slot=None, cites={})
    slot = copy.deepcopy(GAMMA)
    slot[0]["right"]["guard"] = ["top"]
    slot[0]["right"]["lines"][0]["holder_slot"] = 1
    nationality = {"deprive_of_nationality_permitted": permission(
        "allow", act="{0} deprive {1} of nationality", args=("state", "person")),
        "has_nationality": base("person")}
    marriage = {"marry_permitted": permission("allow", act="{0} marry", args=("person",)),
                "recognise_required": obligation("deny", "recognise_permitted", act="{0} recognise {1}",
                                                 args=("state", "person")),
                "recognise_permitted": permission("allow", act="{0} recognise {1}", args=("state", "person")),
                "married": base("person")}
    power = {"kind": "power", "liberty": norm("may-marry", "marry_permitted", True),
             "recognition": norm("recognise-marriage", "recognise_required", True)}
    return {
        "gamma": (env(ARREST), copy.deepcopy(GAMMA)),
        "default gamma": (env(ARREST), _default_gamma()),
        "carve-out": (env(ARREST), carve),
        "authored holder slot": (env(ARREST), slot),
        "null optional fields": (env(ARREST), nulls),
        "fan-out": _fan_out_source(),
        "bar": (impart, [right("r19", [line("liberty", norm("may-impart", "impart_permitted", True))]),
                         {"bar": {"name": "b30", "reading": "rule"}}]),
        "bar with outside rules": (impart, [
            right("r19", [line("liberty", norm("may-impart", "impart_permitted", True))]),
            {"norm": default("no-impart", "impart_permitted", False)},
            {"norm": norm("must-impart", "impart_required", True)},
            {"bar": {"name": "b30", "reading": "rule"}}]),
        "weighed and protected": (holistic, weighed),
        "over": (env(ARREST), over),
        "open pair": (env(ARREST), [
            right("r9", [line("claim", default("no-arbitrary-arrest", "arrest_permitted", False, guard=ARBITRARY))]),
            {"norm": default("may-arrest", "arrest_permitted", True)}]),
        "immunity": (env(nationality, rights={**BLOCK, "alters": {"deprive_of_nationality_permitted": {
            "holder_slot": 1, "status": "has_nationality"}}}),
                     [right("r15", [line("immunity", norm("no-deprivation", "deprive_of_nationality_permitted",
                                                          False))])]),
        "power": (env(marriage, rights={"holders": ["person"], "bearers": ["state"], "alters": {
            "marry_permitted": {"holder_slot": 0, "status": "married", "recognition": "recognise_required"}}}),
                  [right("r16", [power])]),
    }


def _rights_calls(name, environment, units):
    elaborated = rights_route.run_rights_case(environment, units, "rights-elaborate")
    leaf = (elaborated["limitations"] or elaborated["premises"])[0]
    admission = {"units": [{"id": f"u{i}", "span": [i, i + 1], "kind": next(iter(content)), "content": content}
                           for i, content in enumerate(units)],
                 "graph": {"root": "leaf", "nodes": [{"name": "leaf", "ast": leaf["ast"], "label": leaf["label"]}]}}
    # A base model of GAMMA's environment: every non-regulated predicate of E' is empty.
    relations = {predicate: [] for predicate, declaration in
                 elaborated["environment_prime"]["vocabulary"]["predicates"].items()
                 if "regulated" not in declaration and not predicate.startswith("soft__")}
    witness = {"target": "arrest_permitted", "tuple": ["s", "p"], "model": {
        "complete": True, "domains": {"state": ["s"], "person": ["p"]}, "constants": {}, "relations": relations}}
    return {
        # The elaboration's own binder, so a forgery that only a later answer would expose still fails here.
        "rights-elaborate": lambda: rights_route.run_rights_case(environment, units, "rights-elaborate"),
        **{route: (lambda: rights_route.report_rights(environment, units))
           for route in ("rights-scope", "rights-bar", "rights-conflict")},
        "rights-admission": lambda: rights_route.admit_rights_document(environment, admission),
        **({"rights-conflict-witness": lambda: rights_route.run_rights_case(
            environment, units, "rights-conflict", witness=witness)} if name == "gamma" else {}),
    }


def _rights_route_of(case):
    return ("rights-admission" if case["kind"] == "admission" else
            "rights-conflict-witness" if case["kind"] == "rights-conflict" and "witness" in case else case["kind"])


class Relay:
    """Genuine answers of one source, recorded once, and their replay with one answer forged."""

    def __init__(self, mode, calls, route_of, patch_points):
        self.mode, self.calls, self.route_of, self.patch_points = mode, calls, route_of, patch_points
        self.answers = {}

    def record(self, monkeypatch):
        for module, name in self.patch_points:
            real = getattr(module, name)

            def recording(*args, real=real, **kwargs):
                result = real(*args, **kwargs)
                for case, row in self._pairs(args, result):
                    self.answers.setdefault(self.route_of(case), (case, copy.deepcopy(row)))
                return result
            monkeypatch.setattr(module, name, recording)
        for call in self.calls.values():
            call()

    @staticmethod
    def _pairs(args, result):
        if len(args) == 2 and isinstance(args[1], list):  # decide(mode, cases)
            return zip(args[1], result)
        return [(args[-1], result)]

    def replay(self, monkeypatch, route, forged):
        for module, name in self.patch_points:
            def answering(*args, **kwargs):
                rows = [copy.deepcopy(forged if self.route_of(case) == route else self.answers[self.route_of(case)][1])
                        for case, _ in self._pairs(args, [None] * (len(args[1]) if len(args) == 2 and
                                                                   isinstance(args[1], list) else 1))]
                return rows if len(args) == 2 and isinstance(args[1], list) else rows[0]
            monkeypatch.setattr(module, name, answering)
        self.calls[route]()


def _soft_relays(monkeypatch):
    from ve.softnorms import SoftEnvironment, SoftNormDocument
    relays = {}
    for name, (raw, norms) in _soft_sources().items():
        document = SoftNormDocument(SoftEnvironment(raw), norms)
        relay = Relay("soft-norms", _soft_calls(name, document, raw, norms), _soft_route_of, [(soft_route, "_run")])
        with monkeypatch.context() as patch:
            relay.record(patch)
        relays[name] = relay
    return relays


def _rights_relays(monkeypatch):
    from ve.rights import RightsEnvironment
    relays = {}
    for name, (raw, units) in _rights_sources().items():
        environment = RightsEnvironment(raw)
        relay = Relay("rights", _rights_calls(name, environment, units), _rights_route_of,
                      [(rights_route, "decide_once"), (rights_route, "decide")])
        with monkeypatch.context() as patch:
            relay.record(patch)
        relays[name] = relay
    return relays


@pytest.fixture(scope="module")
def relays():
    from tests.test_soft_norms_lean import SERVICE
    if not SERVICE.exists():
        pytest.skip("the Lean service has not been built")
    with pytest.MonkeyPatch.context() as monkeypatch:
        return {**{("soft", name): relay for name, relay in _soft_relays(monkeypatch).items()},
                **{("rights", name): relay for name, relay in _rights_relays(monkeypatch).items()}}


def _survivors(relay, route):
    case, genuine = relay.answers[route]
    mode = relay.mode
    survivors = []
    for path, edit, mutant in mutants(genuine, route):
        try:
            check_row(mode, mutant, case, 0)
        except Invalid:
            continue  # the generated schema refuses it
        with pytest.MonkeyPatch.context() as patch:
            try:
                relay.replay(patch, route, mutant)
            except CheckerUnavailable:
                continue
        survivors.append(f"{path}: {edit}")
    return survivors


@pytest.mark.parametrize("route", sorted(ROUTES))
def test_every_bound_field_mutant_is_unavailable(relays, route):
    exercised, survivors = set(), {}
    for (family, name), relay in relays.items():
        if route not in relay.answers:
            continue
        exercised |= located(relay.answers[route][1], route)
        found = _survivors(relay, route)
        if found:
            survivors[name] = found
    assert not survivors, survivors
    missing = {path for path, kind in INVENTORY[route].items() if kind in FUZZED} - exercised
    assert missing <= set(UNEXERCISED.get(route, {})), sorted(missing - set(UNEXERCISED.get(route, {})))


# Bound fields no genuine answer above carries, each with the regression that covers it.
_WITNESS_ROWS = "test_unrequested_witness_rows_are_unavailable"
UNEXERCISED = {
    "rights-conflict": {"conditional_on[]": "test_f15_rights_conflict_identities_are_bound"},
    "soft-elaborate": {
        # The soft relay never sends a rights block (`check_soft_source` removes it); the same prime
        # binder refuses a changed block on the rights route.
        "environment_prime.vocabulary.rights":
            "test_f19_rights_prime_environment_is_the_request_plus_bound_declarations",
        **{path: _WITNESS_ROWS for path in _WITNESS},
    },
}


def test_unexercised_fields_name_existing_regressions():
    names = set(re.findall(r"^def (test_\w+)", "".join(
        path.read_text() for path in (ROOT / "tests").glob("test_*.py")), re.M))
    for route, fields in UNEXERCISED.items():
        assert set(fields) <= {path for path, kind in INVENTORY[route].items() if kind in FUZZED}, route
        assert set(fields.values()) <= names, route


def test_unrequested_witness_rows_are_unavailable(monkeypatch):
    """`overlaps` and `override_cycles` answer submitted witnesses (SoftNorms/Run.lean `warningRows`); the
    relays submit none, so a genuine row of either kind in an answer to them is extra."""
    from tests.test_soft_norms_lean import SERVICE, env, model, run, should
    from ve.softnorms import SoftEnvironment, SoftNormDocument
    if not SERVICE.exists():
        pytest.skip("the Lean service has not been built")
    same = [should("a", "x_required", True), should("b", "x_required", True)]
    witness = {"pair": ["a", "b"], "model": model({"soft__excepted__a": [], "soft__excepted__b": []}),
               "tuple": ["a"]}
    case = {"id": "soft-elaborate", "kind": "soft-elaborate", "environment": env(), "norms": same}
    [witnessed] = run("ve_soft_norms_route", [{**case, "overlap_witnesses": [witness]}])
    document = SoftNormDocument(SoftEnvironment(env()), same)
    genuine = soft_route.elaborate_soft_document(document)
    for field, rows in (("overlaps", witnessed["overlaps"]),
                        ("override_cycles", [{"cycle": ["a", "b"], "tuple": ["a"], "model": witness["model"],
                                              "line": "override_cycles: a > b > a"}])):
        forged = {**copy.deepcopy(genuine), field: rows}
        check_row("soft-norms", forged, case, 0)
        monkeypatch.setattr(soft_route, "_run", lambda request, forged=forged: copy.deepcopy(forged))
        with pytest.raises(CheckerUnavailable):
            soft_route.elaborate_soft_document(document)


def test_a_report_is_the_ordered_unfolding_of_the_request_graph():
    """ClaimGraph.lean `Unfolds`: a deduction lists its premises' leaves in order, once per use, so a
    dropped, repeated, reordered or foreign assumption, or another root, is refused (all admission relays)."""
    from ve.admission import bind_report

    def node(name, *premises):
        return {"name": name, "ast": ["top"], "label": f"open:{name}"} if not premises else \
            {"name": name, "ast": ["top"], "premises": list(premises), "certificate": {}}

    def claim(name, label=True):
        return {"name": name, "ast": ["top"], **({"label": f"open:{name}"} if label else {})}

    document = {"graph": {"root": "r", "nodes": [node("r", "d", "b"), node("d", "a", "b"), node("a"), node("b")]}}
    report = {"root": claim("r", label=False), "assumptions": [claim("a"), claim("b"), claim("b")]}
    bind_report(document, report)
    for assumptions in ([claim("a"), claim("b")], [claim("b"), claim("a"), claim("b")],
                        [claim("a"), claim("b"), claim("b"), claim("b")], [claim("a"), claim("b"), claim("a")],
                        [claim("a"), claim("b"), claim("d", label=False)], []):
        with pytest.raises(ValueError):
            bind_report(document, {**report, "assumptions": assumptions})
    with pytest.raises(ValueError):
        bind_report(document, {**report, "root": claim("d", label=False)})
    cyclic = {"graph": {"root": "r", "nodes": [node("r", "d"), node("d", "r")]}}
    with pytest.raises(ValueError):
        bind_report(cyclic, {"root": claim("r", label=False), "assumptions": []})
