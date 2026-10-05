"""Python's environment check and the Lean risk route give one diagnostic (risk.md 4.1, 6).

Review B1/A6: the Python block check must follow `decodeRiskBlock` and
`checkRiskBlock` in order and text. Each mutation below is decided by both,
single faults and pairs of faults alike, and the answers must agree; the route
answer through Python's dispatch is Lean's own.
"""
from __future__ import annotations

import itertools
import json
import subprocess
from copy import deepcopy
from pathlib import Path

import pytest

from conformance.risk import agent_ops
from subprocesses import HANG_TIMEOUT
from ve.environment import Environment
from ve.errors import VEError
from ve.risk import run_case

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "lean/.lake/build/bin/ve_risk_route"

pytestmark = pytest.mark.skipif(not BIN.exists(), reason="ve_risk_route is not built")


def _set(path, value):
    def edit(raw):
        *head, last = path
        target = raw
        for key in head:
            target = target[key]
        target[last] = value
    return edit


def _del(path):
    def edit(raw):
        *head, last = path
        target = raw
        for key in head:
            target = target[key]
        del target[last]
    return edit


def _pred(name, arguments=("action",), wording=None):
    return _set(("vocabulary", "predicates", name),
                {"arguments": list(arguments), "description": name,
                 **({"verbalisation": wording} if wording else {})})


def _const(name, sort):
    return _set(("vocabulary", "constants", name), {"sort": sort, "description": name})


R = ("risk",)
S = ("risk", "severity")

# Faults found by the decoder (shape) and by the block check (clauses 2 to 6 of 4.1).
DECODE = {
    "block": _set(R, []),
    "unknown": _set(R + ("zeta",), 1),
    "stage": _set(R + ("bands",), []),
    "missing-unexamined": _del(R + ("unexamined",)),
    "missing-severity": _del(R + ("severity",)),
    "severity-extra": _set(S + ("colour",), "red"),
    "sort-type": _set(S + ("sort",), 3),
    "sort-identifier": _set(S + ("sort",), "Severity"),
    "sort-dunder": _set(S + ("sort",), "sev__erity"),
    "classes-type": _set(S + ("classes",), "severe"),
    "class-identifier": _set(S + ("classes",), ["severe", "serious", "Minor"]),
    "edges-shape": _set(S + ("more_severe",), [["severe", "serious", "minor"]]),
    "unranked-shape": _set(S + ("unranked",), [["severe"]]),
    "decider-empty": _set(S + ("decided_by",), ""),
    "decider-long": _set(S + ("decided_by",), "x" * 65),
    "harm-classes-shape": _set(R + ("harm_classes",), [["data_loss"]]),
    "unexamined-word": _set(R + ("unexamined",), "impossible"),
    "unexamined-empty": _set(R + ("unexamined",), {"ruled_out_by": ""}),
    "unexamined-type": _set(R + ("unexamined",), {"ruled_out_by": 3}),
    "always-shape": _set(R + ("always_possible",), [1]),
    "combination": _set(R + ("combination",), "max"),
    "kinds-type": _set(R + ("alternative_kinds",), []),
    "kind-identifier": _set(R + ("alternative_kinds", "Run"), "running"),
    "kind-empty": _set(R + ("alternative_kinds", "run"), ""),
    "required-shape": _set(R + ("required_alternatives",), [{"when": "run"}]),
    "quantity-kind-identifier": _set(R + ("quantity_kinds", "Peak"), "gb"),
    "quantity-kind-type": _set(R + ("quantity_kinds", "peak_memory"), 1),
    "estimators-shape": _set(R + ("required_estimators",), [{"quantity_kind": "peak_memory"}]),
    "use-all": _set(R + ("use_all_recorded",), "yes"),
}
CHECK = {
    "not-fresh": _set(S + ("sort",), "harm"),
    "sort-profile-word": _set(S + ("sort",), "avoidable"),
    "class-profile-word": _set(S + ("classes",), ["severe", "serious", "minor", "prevents"]),
    "reserved-prefix": _pred("risk__extra"),
    "reserved-class-constant": _const("minor", "harm"),
    "reserved-class-predicate": _pred("serious"),
    "no-classes": _set(S + ("classes",), []),
    "many-classes": _set(S + ("classes",), ["severe", "serious", "minor"] + [f"c{i}" for i in range(14)]),
    "duplicate-class": _set(S + ("classes",), ["severe", "serious", "minor", "serious"]),
    "edge-unknown": _set(S + ("more_severe",), [["severe", "serious"], ["serious", "tiny"]]),
    "unranked-unknown": _set(S + ("unranked",), [["tiny", "minor"]]),
    "self-edge": _set(S + ("more_severe",), [["severe", "serious"], ["serious", "minor"], ["minor", "minor"]]),
    "cycle": _set(S + ("more_severe",), [["severe", "serious"], ["serious", "minor"], ["minor", "severe"]]),
    "unranked-ordered": _set(S + ("unranked",), [["minor", "severe"]]),
    "unranked-self": _set(S + ("unranked",), [["minor", "minor"]]),
    "harm-unknown": _set(R + ("harm_classes",), [["data_loss", "severe"], ["server_outage", "serious"],
                                                ["job_failure", "minor"], ["task_delay", "minor"],
                                                ["task_abandonment", "minor"], ["flood", "minor"]]),
    "harm-class-unknown": _set(R + ("harm_classes",), [["data_loss", "severe"], ["server_outage", "grave"],
                                                      ["job_failure", "minor"], ["task_delay", "minor"],
                                                      ["task_abandonment", "minor"]]),
    "harm-twice": _set(R + ("harm_classes",), [["data_loss", "severe"], ["data_loss", "minor"],
                                              ["server_outage", "serious"], ["job_failure", "minor"],
                                              ["task_delay", "minor"], ["task_abandonment", "minor"]]),
    "harms-unclassified": _set(R + ("harm_classes",), [["data_loss", "severe"], ["job_failure", "minor"],
                                                      ["task_abandonment", "minor"]]),
    "always-unknown": _set(R + ("always_possible",), ["severe", "grave"]),
    "required-when-unknown": _set(R + ("required_alternatives",), [{"when": "fly", "require": ["run"]}]),
    "required-kind-unknown": _set(R + ("required_alternatives",), [{"when": "run", "require": ["ask", "fly"]}]),
    "quantity-tag-unknown": _set(R + ("quantity_kinds", "peak_memory"), "tb"),
    "estimator-kind-unknown": _set(R + ("required_estimators",),
                                   [{"quantity_kind": "latency", "estimators": ["probe"]}]),
    "outcomes": _set(("alternatives", "outcomes"), {"complete_by": "the build agent"}),
}
ALT = {
    "alt-missing-harm": _del(("alternatives", "harm")),
    "excludes-sort": _set(("alternatives", "fulfilments"), [{"obligation": "required", "body": "excludes"}]),
    "profile-word-predicate": _pred("allows"),
    # Not listed: alternatives@0's own Python-only `AlternativesReserved: wording for <p>` (an
    # existing alt diagnostic, unchanged by risk.md 6); Lean's alt route has no such check.
}
ACCEPTED = {
    "dimensionless-kind": _set(R + ("quantity_kinds", "count"), "dimensionless"),
    "ruled-out-by-chooser": _set(R + ("unexamined",), {"ruled_out_by": "chooser"}),
    "estimator-name-long": _set(R + ("required_estimators",),
                                [{"quantity_kind": "peak_memory", "estimators": ["m" * 80]}]),
    "risk-wording-alias": _pred("alias", ("action", "harm"), "{0} might lead to {1}"),
    "class-named-like-sort": _set(S + ("classes",), ["severe", "serious", "minor", "severity"]),
}


def _mutations():
    rows = [(name, (edit,)) for name, edit in {**DECODE, **CHECK, **ALT, **ACCEPTED}.items()]
    # Every pair of block-check faults, and every decode fault with a check fault:
    # the first failure in Lean's order must be Python's first failure too.
    rows += [(f"{a}+{b}", (CHECK[a], CHECK[b])) for a, b in itertools.combinations(CHECK, 2)]
    rows += [(f"{a}+{b}", (DECODE[a], CHECK[b]))
             for a, b in itertools.product(("unknown", "decider-long", "quantity-kind-identifier"),
                                           ("not-fresh", "outcomes", "harms-unclassified"))]
    return rows


def _python(raw):
    try:
        Environment(raw)
    except VEError as exc:
        # A plain VEError carries its code in the message; a subclass carries it in `code`.
        return str(exc) if type(exc) is VEError or str(exc).startswith(f"{exc.code}: ") else f"{exc.code}: {exc}"
    return "ok"


def _lean(raws):
    cases = [{"id": str(i), "kind": "risk-elaborate", "environment": raw, "document": {"norms": []}}
             for i, raw in enumerate(raws)]
    out = subprocess.run([str(BIN), "-"], input=json.dumps(cases), text=True, capture_output=True, timeout=HANG_TIMEOUT)
    assert out.returncode in (0, 1), out.stderr
    return [row["error"] if row["status"] == "error" else "ok" for row in json.loads(out.stdout)]


def test_python_and_lean_environment_diagnostics_agree():
    names, raws = [], []
    for name, edits in _mutations():
        raw = agent_ops()
        for edit in edits:
            edit(raw)
        names.append(name)
        raws.append(raw)
    lean = _lean(raws)
    python = [_python(raw) for raw in raws]
    disagreements = [(n, p, l) for n, p, l in zip(names, python, lean) if p != l]
    assert disagreements == []
    for name in ACCEPTED:
        assert lean[names.index(name)] == "ok", name
    for name in (*DECODE, *CHECK):
        assert lean[names.index(name)] != "ok", name


@pytest.mark.parametrize("name,expected", [
    # risk.md 6: an undeclared class, harm, kind or tag in the block is UnknownSymbol: risk.<field> <name>
    ("harm-class-unknown", "UnknownSymbol: risk.harm_classes grave"),
    ("required-kind-unknown", "UnknownSymbol: risk.required_alternatives fly"),
    ("required-when-unknown", "UnknownSymbol: risk.required_alternatives fly"),
    ("quantity-tag-unknown", "UnknownSymbol: risk.quantity_kinds tb"),
    ("estimator-kind-unknown", "UnknownSymbol: risk.required_estimators latency"),
    # 4.1(3): the first failure in 4.1's order; RiskOutcomes is clause 6
    ("not-fresh+outcomes", "RiskSeverityNotFresh: harm"),
    ("unranked-self", "RiskUnrankedAgainstOrder: minor, minor"),
    ("self-edge", "DependencyCycle: minor, serious, severe"),
    ("class-profile-word", "AlternativesReserved: prevents"),
    ("harms-unclassified", "HarmUnclassified: server_outage"),
])
def test_spec_texts(name, expected):
    raw = agent_ops()
    for edit in dict(_mutations())[name]:
        edit(raw)
    assert _python(raw) == expected
    assert _lean([raw]) == [expected]


def test_route_answer_is_leans_through_python_dispatch():
    """Python decodes nothing first: the dispatched answer is the route's, byte for byte."""
    for name in ("not-fresh+outcomes", "decider-long", "harm-twice"):
        raw = agent_ops()
        for edit in dict(_mutations())[name]:
            edit(raw)
        case = {"id": name, "kind": "risk-elaborate", "environment": raw, "document": {"norms": []}}
        direct = json.loads(subprocess.run([str(BIN), "-"], input=json.dumps([case]), text=True,
                                           capture_output=True, timeout=HANG_TIMEOUT).stdout)[0]
        assert run_case(deepcopy(case)) == direct
