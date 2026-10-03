"""Stage S5 item 1, the Lean side (docs/spec/wire-contract-s5.md 2.5, 5.2 and the fixtures of 8.1, 8.2, 8.6).

`ve_diagnose norms@0` and `ve_diagnose norm-defaults@0` run the generated tables with the hand-written hooks of
`lean/VE/WireContract/Hooks/Norms.lean` and `Hooks/NormDefaults.lean`. These tests check, on the spec's
fixtures:

- the record of each of N1 to N40 (N14 struck) and D1 to D13: `check`, `path`, `class`, and `text` where the
  check is not inherited (an inherited record's text is each language's own);
- that `ve_diagnose` reports a fault exactly when Python's legacy validator of the unit rejects (2.2), and
  that the record's class is the legacy code except on the exempt cases N32, N36 and N40 (2.12);
- the verdict of the Lean route of 2.2 on the same source, where it is known to agree; the candidates of
  S5-pre (2.12) are listed apart and reported, not asserted;
- L1 to L3 (whole records) and L5 (the domain).

The records' `revision` is read from the generated table modules, so the tests hold at every revision.
"""
from __future__ import annotations

import copy
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from ve.environment import Environment
from ve.errors import VEError
from ve.norm_defaults import UnspecifiedDocument
from ve.norms import NormDocument

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "lean/.lake/build/bin"
EXAMPLE = ROOT / "ve/wire_contract/examples/soft-norms@0/empty.json"


def revision(module):
    text = (ROOT / f"lean/VE/WireContract/Tables/{module}.lean").read_text()
    return int(re.search(r"revision := (\d+)", text)[1])


def binary(name):
    if not (BIN / name).exists():
        lake = shutil.which("lake")
        if lake is None:
            pytest.skip(f"lake is required for {name}")
        result = subprocess.run([lake, "build", name], cwd=ROOT / "lean", capture_output=True, text=True,
                                timeout=3000)
        assert result.returncode == 0, result.stdout + result.stderr
    return BIN / name


@pytest.fixture(scope="module")
def diagnose():
    return binary("ve_diagnose")


def run(executable, args, cases):
    result = subprocess.run([str(executable), *args, "-"], input=json.dumps(cases), text=True,
                            capture_output=True, timeout=1200)
    assert result.returncode in (0, 1), result.stderr
    rows = json.loads(result.stdout)
    assert len(rows) == len(cases)
    return rows


# ---------------------------------------------------------------------------------------------------------------
# The bases B and U and the formulas of section 8

ATOM = ["unary", "c", ["var", 0]]


def balanced(n):
    """The balanced conjunction of `n` atoms: `3n - 1` nodes."""
    if n == 1:
        return copy.deepcopy(ATOM)
    left = (n + 1) // 2
    return ["and", balanced(left), balanced(n - left)]


def nots(k, inner):
    for _ in range(k):
        inner = ["not", inner]
    return inner


def base_b():
    environment = json.loads(EXAMPLE.read_text())["environment"]
    environment["profiles"] = ["norms@0", "relational-fol@0"]
    environment["vocabulary"]["predicates"]["c"] = {"arguments": ["assistant"], "description": "c"}
    norms = [
        {"norm": {"name": "a0", "predicate": "x_required", "sign": True, "guard": copy.deepcopy(ATOM),
                  "unless": [], "over": []}},
        {"norm": {"name": "b1", "predicate": "x_permitted", "sign": False, "guard": ["top"],
                  "unless": [copy.deepcopy(ATOM)], "over": []}},
        {"norm": {"name": "c2", "predicate": "x_required", "sign": False, "guard": ["top"], "unless": [],
                  "over": ["a0"]}},
    ]
    return environment, norms


def base_u():
    environment, norms = base_b()
    environment["profiles"] = ["norm-defaults@0", "norms@0", "relational-fol@0"]
    environment["vocabulary"]["predicates"]["x_permitted"]["regulated"]["default"] = "unspecified"
    return environment, norms


def rule(name, predicate, guard=None, over=()):
    return {"norm": {"name": name, "predicate": predicate, "sign": True, "guard": guard or ["top"],
                     "unless": [], "over": list(over)}}


def chain(count, predicate):
    """Rules `r0` to `r<count-1>` on `predicate`, each after the first `over` the one before it."""
    return [rule(f"r{i}", predicate, over=[f"r{i - 1}"] if i else []) for i in range(count)]


def n(i):
    return lambda e, r: r[i]["norm"]


# Each change: (environment, norms) -> None, applied to fresh copies of the base.
def set_rule(i, **fields):
    def change(e, r):
        r[i]["norm"].update(copy.deepcopy(fields))
    return change


def both(*changes):
    def change(e, r):
        for c in changes:
            c(e, r)
    return change


def n2(e, r):
    e["profiles"] = ["relational-fol@0"]
    for decl in e["vocabulary"]["predicates"].values():
        decl.pop("regulated", None)


def n3(e, r):
    r.extend(rule(f"r{i}", "x_required", guard=copy.deepcopy(ATOM)) for i in range(3, 257))
    for x in r[3:]:
        x["norm"]["sign"] = True


def n4(e, r):
    r[1]["extra"] = 1


def n6(e, r):
    del r[2]["norm"]["over"]


def n17(e, r):
    r[1]["norm"]["unless"] = [copy.deepcopy(ATOM) for _ in range(9)]


def n21(e, r):
    r[0]["norm"]["guard"] = balanced(1667)
    r[1]["norm"]["guard"] = balanced(1667)
    r[1]["norm"]["unless"] = []


REACH = ["reach", "plus", ["named", "c"], ["var", 0], ["var", 0]]
K = nots(65, ["top"])


def n25(e, r):
    r[:] = chain(17, "x_required")


def n38(e, r):
    e["profiles"] = ["data@0", "norms@0", "relational-fol@0"]
    r[0]["norm"]["guard"] = ["forall", "$string", ["top"]]


def n40(e, r):
    e["vocabulary"]["predicates"]["c"]["defined"] = {"arguments": ["assistant"], "body": ["top"]}


# (case, change, check, path, class, text or None for an inherited check)
NORMS = [
    ("N1", lambda e, r: None, None, None, None, None),
    ("N1b", lambda e, r: r.clear(), None, None, None, None),
    ("N2", n2, "2.1", "/environment/profiles", "InvalidInput", "UnsupportedProfile: norms@0 is required"),
    ("N3", n3, "2.2", "/norms", "ResourceLimit", "ResourceLimit: rules"),
    ("N4", n4, "3.1", "/norms/1", "InvalidInput", "InvalidInput: expected norm object"),
    ("N5", set_rule(0), None, None, None, None),  # replaced below: `norm` is `[]`
    ("N6", n6, "3.3", "/norms/2/norm", "InvalidInput", "InvalidInput: invalid norm fields"),
    ("N7", set_rule(1, unless={}), "3.4", "/norms/1/norm/unless", "InvalidInput",
     "InvalidInput: unless and over must be arrays"),
    ("N8", set_rule(2, over=["a0", 7]), "3.7", "/norms/2/norm/over/1", "InvalidInput",
     "InvalidInput: rule predicate and precedence edges must be strings"),
    ("N9", set_rule(0, guard=nots(65, ["top"])), "3.8a", "/norms/0/norm/guard", "ResourceLimit", None),
    ("N10", set_rule(0, guard=5), "3.8b", "/norms/0/norm/guard", "SyntaxError", None),
    ("N11", set_rule(1, unless=[ATOM, 5]), "3.9b", "/norms/1/norm/unless/1", "SyntaxError", None),
    ("N12", set_rule(0, name="A0"), "4.1", "/norms/0/norm/name", "InvalidInput",
     "InvalidInput: invalid rule name 'A0'"),
    ("N13", set_rule(2, name="a0"), "4.2", "/norms/2/norm/name", "DuplicateDeclaration",
     "DuplicateDeclaration: rule a0"),
    ("N15", set_rule(0, predicate="c"), "4.4", "/norms/0/norm/predicate", "InvalidInput",
     "UnknownSymbol: regulated predicate c"),
    ("N16", set_rule(1, sign="no"), "4.5", "/norms/1/norm/sign", "InvalidInput",
     "InvalidInput: invalid sign or too many carve-outs"),
    ("N17", n17, "4.6", "/norms/1/norm/unless", "InvalidInput", "InvalidInput: invalid sign or too many carve-outs"),
    ("N18", set_rule(0, guard=["binary", "c", ["var", 0], ["var", 0]]), "4.7a", "/norms/0", "TypeMismatch", None),
    ("N19", set_rule(0, guard=["unary", "d", ["var", 0]]), "4.7b", "/norms/0", "UnknownSymbol", None),
    ("N20", set_rule(0, guard=["unary", "c", ["var", 1]]), "4.7c", "/norms/0", "UnboundVariable", None),
    ("N21", n21, "4.7d", "/norms/2", "ResourceLimit", None),
    ("N22", set_rule(2, over=["zz"]), "5.1", "/norms/2/norm/over/0", "InvalidInput", "UnknownRule: rule zz"),
    ("N23", set_rule(2, over=["b1"]), "5.2", "/norms/2/norm/over/0", "InvalidInput",
     "PrecedenceAcrossPredicates: rule c2 on x_required, rule b1 on x_permitted"),
    ("N24", set_rule(0, over=["c2"]), "6.1", "/norms", "InvalidInput", "DependencyCycle: a0, c2"),
    ("N25", n25, "6.2", "/norms", "ResourceLimit", "ResourceLimit: precedence depth"),
    ("N26", both(set_rule(0, guard=["unary", "x_permitted", ["var", 0]]),
                 set_rule(1, guard=["unary", "x_required", ["var", 0]])),
     "6.3", "/norms", "InvalidInput", "DependencyCycle: x_permitted, x_required"),
    ("N27", both(n4, set_rule(2, name="a0")), "3.1", "/norms/1", "InvalidInput", "InvalidInput: expected norm object"),
    ("N28", both(set_rule(0, predicate="c"), set_rule(1, name="B1")), "4.4", "/norms/0/norm/predicate",
     "InvalidInput", "UnknownSymbol: regulated predicate c"),
    ("N29", both(set_rule(0, name="A0"), set_rule(0, predicate="c")), "4.1", "/norms/0/norm/name", "InvalidInput",
     "InvalidInput: invalid rule name 'A0'"),
    ("N30", both(set_rule(1, unless={}), set_rule(1, sign="no")), "3.4", "/norms/1/norm/unless", "InvalidInput",
     "InvalidInput: unless and over must be arrays"),
    ("N31", set_rule(1, unless=[ATOM, ["unary", "d", ["var", 0]]]), "4.7b", "/norms/1", "UnknownSymbol", None),
    ("N32", set_rule(0, guard=["unary", "c", ["var", True]]), "3.8b", "/norms/0/norm/guard", "SyntaxError", None),
    ("N33", set_rule(0, guard=["unary", 7, ["var", 0]]), "4.7b", "/norms/0", "UnknownSymbol", None),
    ("N34", set_rule(0, guard=["eq", ["const", 5], ["var", 0]]), "4.7b", "/norms/0", "UnknownSymbol", None),
    ("N35", set_rule(0, guard=["forall", 5, ["top"]]), "4.7b", "/norms/0", "UnknownSymbol", None),
    ("N36", set_rule(0, guard=["and", REACH, K]), "3.8b", "/norms/0/norm/guard", "SyntaxError", None),
    ("N37", set_rule(0, guard=["and", K, REACH]), "3.8a", "/norms/0/norm/guard", "ResourceLimit", None),
    ("N38", n38, "4.7e", "/norms/0", "UnsupportedProfile", None),
    ("N39", both(n21, set_rule(2, guard=["unary", "d", ["var", 0]])), "4.7d", "/norms/2", "ResourceLimit", None),
    ("N40", n40, "1.1", "/environment", "InvalidInput", None),
]
NORMS[5] = ("N5", lambda e, r: r[0].update({"norm": []}), "3.2", "/norms/0/norm", "InvalidInput",
            "InvalidInput: expected norm object")
# 2.12: the record's class is not Python's legacy code on these, by the listed exemptions.
EXEMPT = {"N32", "N36", "N40"}
# Every fixture is a case that Lean reads: N32's index is the Boolean of the spec (4098ed1c), not the negative
# integer the restricted JSON reader refuses (`lean/VE/Json.lean`).
LEAN_UNREADABLE = set()


def d6(e, r):
    for i in range(253):
        e["vocabulary"]["predicates"][f"b{i}"] = {"arguments": ["assistant"], "description": "b"}


def d7(e, r):
    r.extend(rule(f"r{i}", "x_required") for i in range(3, 256))


LONG = "x" * 50 + "_permit"  # 57 bytes


def d8(e, r):
    predicates = e["vocabulary"]["predicates"]
    predicates[LONG] = predicates.pop("x_permitted")
    predicates["x_required"]["regulated"]["permission"] = LONG
    r[1]["norm"]["predicate"] = LONG


def d10(e, r):
    r[:] = chain(16, "x_permitted")


def d13(e, r):
    """D10 with D8: D10's rules are on `x_permitted`, so D8's rename reaches each of them."""
    d10(e, r)
    d8(e, [None, {"norm": {}}])
    for x in r:
        x["norm"]["predicate"] = LONG


NORM_DEFAULTS = [
    ("D1", lambda e, r: None, None, None, None, None),
    ("D1b", lambda e, r: r.clear(), None, None, None, None),
    ("D2", set_rule(1, unless={}), "w1-shape/3.4", "/norms/1/norm/unless", "InvalidInput",
     "InvalidInput: unless and over must be arrays"),
    ("D3", set_rule(2, name="a0"), "w1/4.2", "/norms/2/norm/name", "DuplicateDeclaration",
     "DuplicateDeclaration: rule a0"),
    ("D4", set_rule(1, name="unsaid--x"), "w1/4.3", "/norms/1/norm/name", "InvalidInput",
     "InvalidInput: reserved name unsaid--x"),
    ("D5", set_rule(0, over=["c2"]), "w1/6.1", "/norms", "InvalidInput", "DependencyCycle: a0, c2"),
    ("D6", d6, "5.1", "", "ResourceLimit", "ResourceLimit: vocabulary size"),
    ("D7", d7, "5.2", "", "ResourceLimit", "ResourceLimit: rules"),
    ("D8", d8, "5.3", "", "ResourceLimit", "ResourceLimit: unspecified name length"),
    ("D9", set_rule(0, guard=balanced(3332)), "6.1", "", "ResourceLimit", "ResourceLimit: AST exceeds 10,000 nodes"),
    ("D10", d10, "6.2", "", "ResourceLimit", "ResourceLimit: precedence depth"),
    ("D11", set_rule(0, guard=balanced(3320)), "6.3", "", "ResourceLimit",
     "ResourceLimit: fill premise unsaid:pair:x_required,x_permitted"),
    ("D12", both(d8, set_rule(2, over=["b1"])), "w1/5.2", "/norms/2/norm/over/0", "InvalidInput",
     f"PrecedenceAcrossPredicates: rule c2 on x_required, rule b1 on {LONG}"),
    ("D13", d13, "5.3", "", "ResourceLimit", "ResourceLimit: unspecified name length"),
]


def source(base, change):
    environment, norms = base()
    change(environment, norms)
    return environment, norms


def legacy_norms(environment, norms):
    NormDocument(Environment(copy.deepcopy(environment)), copy.deepcopy(norms))


def legacy_norm_defaults(environment, norms):
    UnspecifiedDocument(Environment(copy.deepcopy(environment)),
                        [NormDocument._decode(c) for c in copy.deepcopy(norms)])


def legacy_error(validate, environment, norms):
    try:
        validate(environment, norms)
    except VEError as error:
        return error
    return None


UNITS = {
    "norms@0": (base_b, NORMS, "norms-elaborate", "Norms", legacy_norms),
    "norm-defaults@0": (base_u, NORM_DEFAULTS, "norm-defaults-elaborate", "NormDefaults", legacy_norm_defaults),
}


@pytest.mark.parametrize("unit", sorted(UNITS))
def test_fixtures_records_and_legacy_agreement(diagnose, unit):
    base, fixtures, kind, module, validate = UNITS[unit]
    cases, expected = [], {}
    for name, change, check, path, cls, text in fixtures:
        if name in LEAN_UNREADABLE:
            continue
        environment, norms = source(base, change)
        cases.append({"id": name, "kind": kind, "environment": environment, "norms": norms})
        expected[name] = (check, path, cls, text, legacy_error(validate, environment, norms))
    rows = run(diagnose, [unit], cases)
    problems = []
    for row in rows:
        check, path, cls, text, error = expected[row["id"]]
        if check is None:
            if row != {"id": row["id"], "status": "ok", "outcome": "clean"} or error is not None:
                problems.append((row["id"], "clean expected", row, error))
            continue
        record = row.get("diagnostic", {})
        got = (record.get("check"), record.get("path"), record.get("class"))
        if row.get("outcome") != "fault" or got != (check, path, cls):
            problems.append((row["id"], (check, path, cls), row))
            continue
        if record["contract"] != unit or record["revision"] != revision(module):
            problems.append((row["id"], "contract or revision", record))
        if text is not None and record["text"] != text:
            problems.append((row["id"], text, record["text"]))
        if error is None:
            problems.append((row["id"], "Python's legacy validator accepts"))
        elif row["id"] not in EXEMPT and record["class"] != error.code:
            problems.append((row["id"], "class rule", record["class"], error.code))
    assert not problems, problems


def test_exempt_cases_differ_from_python_class_as_listed():
    """N32, N36 and N40: the record's class against Python's legacy code (2.12, section 10)."""
    legacy = {name: legacy_error(legacy_norms, *source(base_b, change)).code
              for name, change, *_ in NORMS if name in EXEMPT}
    assert legacy == {"N32": "UnboundVariable", "N36": "ResourceLimit", "N40": legacy["N40"]}


# S5-pre's candidates (2.12): sources on which the Lean route's verdict is not asserted here.
LEAN_ROUTE_OPEN = {"D11"}


@pytest.mark.parametrize("unit", sorted(UNITS))
def test_lean_route_rejects_where_the_engine_faults(diagnose, unit):
    """The Lean legacy validator of 2.2 on the same fixtures: it rejects exactly where `ve_diagnose` reports a
    fault, except on the listed S5-pre candidates, which are reported, not asserted."""
    base, fixtures, kind, _, _ = UNITS[unit]
    route = binary("ve_norms_route" if unit == "norms@0" else "ve_norm_defaults_route")
    cases = [{"id": name, "kind": kind, **dict(zip(("environment", "norms"), source(base, change)))}
             for name, change, *_ in fixtures if name not in LEAN_UNREADABLE]
    diagnosed = {row["id"]: row.get("outcome") for row in run(diagnose, [unit], cases)}
    routed = {row["id"]: row.get("status") for row in run(route, [], cases)}
    differ = sorted(i for i in diagnosed if (diagnosed[i] == "fault") != (routed[i] == "error"))
    assert set(differ) <= LEAN_ROUTE_OPEN, differ


# ---------------------------------------------------------------------------------------------------------------
# 8.6: L1 to L3 and L5

def s1():
    return source(base_b, set_rule(2, name="a0"))


def s16():
    return source(base_u, set_rule(2, name="a0"))


def record(unit, module, check, phase):
    return {"contract": unit, "revision": revision(module), "check": check, "phase": phase,
            "code": "NORMS_DUPLICATE_DECLARATION", "class": "DuplicateDeclaration", "path": "/norms/2/norm/name",
            "text": "DuplicateDeclaration: rule a0", "args": {"value": "a0"}}


def document(norms):
    return {"units": [{"id": f"u{i}", "span": [i, i + 1], "kind": "norm", "content": c} for i, c in enumerate(norms)],
            "graph": {"root": "r", "nodes": []}}


def test_l1_and_l3_norms_records(diagnose):
    environment, norms = s1()
    cases = [{"id": "l1", "kind": "norms-elaborate", "environment": environment, "norms": norms},
             {"id": "l3", "kind": "admission", "environment": environment, "document": document(norms)}]
    expected = record("norms@0", "Norms", "4.2", "rules")
    assert run(diagnose, ["norms@0"], cases) == [
        {"id": "l1", "status": "ok", "outcome": "fault", "diagnostic": expected},
        {"id": "l3", "status": "ok", "outcome": "fault", "diagnostic": expected}]


def test_l2_norm_defaults_record(diagnose):
    environment, norms = s16()
    case = {"id": "l2", "kind": "norm-defaults-elaborate", "environment": environment, "norms": norms}
    assert run(diagnose, ["norm-defaults@0"], [case]) == [
        {"id": "l2", "status": "ok", "outcome": "fault",
         "diagnostic": record("norm-defaults@0", "NormDefaults", "w1/4.2", "norms")}]


def test_l5_outside_the_domain(diagnose):
    environment, norms = base_b()
    closure = copy.deepcopy(environment)
    closure["profiles"] = ["closure@0", "norms@0", "relational-fol@0"]
    defaults, _ = base_u()
    cases = [{"id": "string", "kind": "norms-elaborate", "environment": environment, "norms": "x"},
             {"id": "closure", "kind": "norms-elaborate", "environment": closure, "norms": norms},
             {"id": "defaults", "kind": "norms-elaborate", "environment": defaults, "norms": norms}]
    result = subprocess.run([str(diagnose), "norms@0", "-"], input=json.dumps(cases), text=True,
                            capture_output=True, timeout=600)
    assert result.returncode == 1, result.stderr
    error = "UnsupportedProfile: the case is outside the unit's domain"
    assert json.loads(result.stdout) == [{"id": c["id"], "status": "error", "error": error} for c in cases]
    # The same refusals under `norm-defaults@0`: without the profile, or with a unit that is not an object.
    cases = [{"id": "plain", "kind": "norm-defaults-elaborate", "environment": environment, "norms": norms},
             {"id": "unit", "kind": "norm-defaults-elaborate", "environment": defaults, "norms": [7]},
             {"id": "kind", "kind": "norms-elaborate", "environment": defaults, "norms": norms}]
    rows = run(diagnose, ["norm-defaults@0"], cases)
    assert rows[:2] == [{"id": c["id"], "status": "error", "error": error} for c in cases[:2]]
    assert rows[2] == {"id": "kind", "status": "error",
                       "error": "UnsupportedProfile: case kind norms-elaborate has no wire contract input"}


# ---------------------------------------------------------------------------------------------------------------
# 8.6, L8 over the corpus (Astra review B: the `#guard`s of `Hooks/Norms.lean` check 17 samples at three
# counts; L8 asks for every eligible guard and carve-out of the corpus, from its running count).

# The name position of each tag that has one: the syntax walk reads a value there that is not a string as
# `sentinel`, where `budgetFormula` refuses the node, so such a formula is not L8's.
NAME_AT = frozenset({"unary", "binary", "forall", "exists", "const"})


def names_are_strings(node):
    if type(node) is not list:
        return True
    if node and node[0] in NAME_AT and len(node) > 1 and type(node[1]) is not str:
        return False
    return all(names_are_strings(child) for child in node[1:])


def l8_rules(cases):
    """Each rule of the corpus cases that Lean reads, as its guard and then its carve-outs, up to the first
    formula with a name that is not a string; once each."""
    rules = set()
    for case in cases:
        if not case[6] or type(case[3]) is not list:
            continue
        for unit in case[3]:
            rule = unit.get("norm") if type(unit) is dict else None
            if type(rule) is not dict or "guard" not in rule:
                continue
            formulas = [rule["guard"]] + (rule["unless"] if type(rule.get("unless")) is list else [])
            prefix = []
            for formula in formulas:
                if not names_are_strings(formula):
                    break
                prefix.append(formula)
            if prefix:
                rules.add(json.dumps(prefix, separators=(",", ":")))
    return sorted(rules)


def l8(lines):
    lake = shutil.which("lake")
    if lake is None:
        pytest.skip("lake is required for L8")
    binary("ve_diagnose")  # the hooks module is built
    result = subprocess.run([lake, "env", "lean", "--run", str(ROOT / "tests/wire_contract_l8.lean")],
                            cwd=ROOT / "lean", input="\n".join(lines) + "\n", text=True, capture_output=True,
                            timeout=3000)
    assert result.returncode == 0, result.stdout[-4000:] + result.stderr[-4000:]
    rows = [json.loads(line) for line in result.stdout.splitlines()]
    assert len(rows) == len(lines)
    return rows


def test_l8_harness_reports_a_difference():
    """The comparison is not vacuous: a name that is not a string is read by the walk and refused by
    `budgetFormula`, and a later carve-out is read from the count the earlier formulas leave."""
    rows = l8([json.dumps([["unary", 7, ["var", 0]]]), json.dumps([["top"], nots(64, ["top"])]),
               json.dumps([balanced(1667), balanced(1667), balanced(1)])])
    assert rows[0]["differ"] is not None and rows[0]["compared"] == 1
    assert rows[1] == {"compared": 2, "failed": True, "differ": None}  # 1 + 65 nodes: depth over 64
    assert rows[2] == {"compared": 3, "failed": True, "differ": None}  # 5,000 + 5,000 + 2 nodes: over the budget


def test_l8_syntax_walk_is_budget_formula_on_the_corpus():
    """Every guard and carve-out of both units' corpora whose name positions hold strings, from its running
    count: the same formula and count, or a failure with the same text."""
    from conformance.wire_contract_gate import gate_cases
    from ve.wire_contract.engine import load
    rules = sorted(set(l8_rules(gate_cases(load("norms@0")))) | set(l8_rules(gate_cases(load("norm-defaults@0")))))
    rows = l8(rules)
    differ = [(rule[:200], row["differ"]) for rule, row in zip(rules, rows) if row.get("differ") is not None]
    assert differ == []
    compared = sum(row["compared"] for row in rows)
    failed = sum(row["failed"] for row in rows)
    # On the corpus of this commit: 2,218 rules, 3,115 formulas, 21 of them refused by both with one text.
    assert len(rules) > 2000 and compared > len(rules) and failed > 10, (len(rules), compared, failed)


# ---------------------------------------------------------------------------------------------------------------
# 2.2: one domain, and one root, for both adapters (Astra and Fable reviews, B: a missing admission document
# was an empty source in Python and outside the domain in Lean; a profile that is not a string was outside
# the domain in Python and inside it in Lean; a `profiles` that is not an array was inside `norm-defaults@0`'s
# domain in Python and outside it in Lean; `units` that is not an array was `[]` or a `TypeError` in Python).

OUTSIDE = "UnsupportedProfile: the case is outside the unit's domain"


def _with(base, change, kind):
    environment, norms = base()
    case = {"id": "", "kind": kind, "environment": environment, "norms": norms}
    change(case)
    return case


def _admission(base, document_value):
    environment, _ = base()
    case = {"id": "", "kind": "admission", "environment": environment}
    if document_value is not None:
        case["document"] = document_value
    return case


def _profiles(value):
    def change(case):
        case["environment"]["profiles"] = value(case["environment"]["profiles"])
    return change


def adapter_cases(unit):
    """(id, case, expected): `outside` for the domain's refusal, `kind` for a kind without input, `in` for a
    case whose root both engines diagnose, and `crash` for one inside the domain on which Python's environment
    decoder raises `TypeError`, not a `VEError` (`profiles` a number or a Boolean; `ve/environment.py:327`, frozen
    in item 1), where Lean's 1.1 rejects: an S5-pre candidate (s5-pre.md)."""
    base, kind = (base_b, "norms-elaborate") if unit == "norms@0" else (base_u, "norm-defaults-elaborate")
    environment, norms = base()
    mixed = {"units": [7, "x", {"kind": "norm", "content": norms[0]}, {"kind": "quoted", "content": norms[1]},
                       {"kind": "norm", "content": {"text": "t"}}], "graph": {"root": "r", "nodes": []}}
    other = "norm-defaults@0" if unit == "norms@0" else "norms@0"
    rows = [
        ("profile-not-a-string", _with(base, _profiles(lambda p: p + [7]), kind), "outside"),
        ("profile-object", _with(base, _profiles(lambda p: [{"p": "norms@0"}] + p), kind), "outside"),
        ("profiles-string", _with(base, _profiles(lambda p: " ".join(p)), kind),
         "in" if unit == "norms@0" else "outside"),
        ("profiles-number", _with(base, _profiles(lambda p: 7), kind), "crash" if unit == "norms@0" else "outside"),
        ("profiles-boolean", _with(base, _profiles(lambda p: True), kind),
         "crash" if unit == "norms@0" else "outside"),
        ("profiles-missing", _with(base, lambda c: c["environment"].pop("profiles"), kind),
         "in" if unit == "norms@0" else "outside"),
        ("environment-number", _with(base, lambda c: c.update(environment=7), kind),
         "in" if unit == "norms@0" else "outside"),
        ("environment-array", _with(base, lambda c: c.update(environment=[environment]), kind),
         "in" if unit == "norms@0" else "outside"),
        ("environment-missing", _with(base, lambda c: c.pop("environment"), kind),
         "in" if unit == "norms@0" else "outside"),
        ("other-unit", _with(base, _profiles(lambda p: sorted(set(p) ^ {"norm-defaults@0"})), kind), "outside"),
        ("quantity", _with(base, lambda c: c["environment"].update(unit_schema={}), kind), "outside"),
        ("norms-string", _with(base, lambda c: c.update(norms="x"), kind), "outside"),
        ("norms-member", _with(base, lambda c: c["norms"].append(7), kind), "outside"),
        ("norms-missing", _with(base, lambda c: c.pop("norms"), kind), "outside"),
        ("admission-no-document", _admission(base, None), "outside"),
        ("admission-document-string", _admission(base, "x"), "outside"),
        ("admission-no-units", _admission(base, {"graph": {"root": "r", "nodes": []}}), "outside"),
        ("admission-units-string", _admission(base, {"units": "xy"}), "outside"),
        ("admission-units-number", _admission(base, {"units": 7}), "outside"),
        ("admission-units-object", _admission(base, {"units": {"kind": "norm", "content": norms[0]}}), "outside"),
        ("admission-mixed-units", _admission(base, mixed), "in"),
        ("admission-s1", _admission(base, document(norms)), "in"),
        ("kind-number", _with(base, lambda c: c.update(kind=7), kind), "kind"),
        ("kind-object", _with(base, lambda c: c.update(kind={"a": [1]}), kind), "kind"),
        ("kind-missing", _with(base, lambda c: c.pop("kind"), kind), "kind"),
        ("kind-other-unit", _with(base, lambda c: c.update(
            kind="norm-defaults-elaborate" if unit == "norms@0" else "norms-elaborate"), kind), "kind"),
        ("kind-soft", _with(base, lambda c: c.update(kind="soft-elaborate"), kind), "kind"),
    ]
    assert other  # both units are listed above by their kinds and profiles
    return [(name, {**case, "id": name}, expected) for name, case, expected in rows]


def python_adapter_row(unit, case):
    """The Python adapter, then the Python engine, as one `ve_diagnose` row without its record's text."""
    from ve.errors import UnsupportedProfile
    from ve.norm_defaults_contract import REGISTRY as DEFAULTS
    from ve.norms_contract import REGISTRY as NORMS
    from ve.wire_contract.engine import Fault, load
    from ve.wire_contract.engine import run as engine_run
    registry = NORMS if unit == "norms@0" else DEFAULTS
    contract = load(unit)
    try:
        root = registry.adapters[contract["adapter"]](copy.deepcopy(case))
    except UnsupportedProfile as error:
        return {"id": case["id"], "status": "error", "error": str(error)}
    try:
        outcome = engine_run(contract, root, registry=registry)
    except TypeError:
        return {"id": case["id"], "status": "crash"}
    if isinstance(outcome, Fault):
        return {"id": case["id"], "status": "ok", "outcome": "fault",
                "at": [outcome.record["check"], outcome.record["path"]]}
    return {"id": case["id"], "status": "ok", "outcome": "clean"}


def lean_adapter_row(row):
    if row.get("outcome") == "fault":
        record = row.pop("diagnostic")
        row["at"] = [record["check"], record["path"]]
    return row


@pytest.mark.parametrize("unit", sorted(UNITS))
def test_both_adapters_share_one_domain(diagnose, unit):
    cases = adapter_cases(unit)
    lean = [lean_adapter_row(row) for row in run(diagnose, [unit], [case for _, case, _ in cases])]
    python = [python_adapter_row(unit, case) for _, case, _ in cases]
    crashes = {name for name, _, expected in cases if expected == "crash"}
    assert [row for row in python if row["id"] not in crashes] == [row for row in lean if row["id"] not in crashes]
    for (name, case, expected), row, lean_row in zip(cases, python, lean):
        if expected == "crash":
            assert row == {"id": name, "status": "crash"}
            assert lean_row == {"id": name, "status": "ok", "outcome": "fault", "at": ["1.1", "/environment"]}
            with pytest.raises(TypeError):
                legacy_norms(case["environment"], case["norms"])
        elif expected == "outside":
            assert row == {"id": name, "status": "error", "error": OUTSIDE}
        elif expected == "kind":
            assert row["status"] == "error" and row["error"].endswith("has no wire contract input"), row
        else:
            assert row["status"] == "ok", row
