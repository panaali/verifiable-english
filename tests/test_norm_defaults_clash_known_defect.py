"""norm-defaults@0 status at clashing duty rules: refused through the commands, two points still recorded (docs/spec/norm-defaults.md 2.5).

Where duty rules clash at a point, the duty status check (`norm-defaults-status`) counts every
admissible filling (2.5) and does not consult the conflict check (3.1), so on its own it reports one
side as SETTLED. Row duties-clash-known-defect recorded main's answers at the eight fixtures under
tests/data/norm-defaults-clash/*.json; row duties-clash-refuse-gate added the refusal gate
(`ve/clash_gate.py`), so the commands that print those answers now refuse at a clash, naming the two
rules (2.5, "Refusal at a clash"). Here:

- Six fixtures are refused through the gated commands, both rule names in the refusal: A1 (a 'must'
  and a 'need not' rule on file_required), B1 (a 'must' rule and a 'may not' rule on its permission
  pair; asked both ways) and u6 (main's own fixture: the pair is broken under the filling
  y_permitted(a) = yes) at `ve norms completions --audit --situation`; the two unstated-fact points
  (a1-unstated, b1-unstated: the same A1 and B1 texts with contractor(omar) not stated, where each
  completion of that fact gave a different definite answer) at `ve document readings --conclusion`,
  since the text allows the situation where the two rules clash.
- Two fixtures stay a known defect (marked below): the ask-both text writes "should file" and "should
  not file" as two request predicates with '+' rules only; nothing declares one the refrain of the
  other, so they are no clash under the gate's rule (same predicate, opposite outcomes) and the
  conflict check does not see them either. Main's answer is recorded exactly, through the entry it
  was measured with: `ve.backends.relay.rows("norm-defaults", ...)`. They are not xfail and not skip:
  they pass today and fail when the behaviour changes, so a fix has to edit them on purpose.

The files under tests/data/norm-defaults-clash/controls/ are ordinary tests: four points beside the
clash whose answer is right today (A1 and B1 book_permitted) or that main already leaves UNDECIDED
(u6 y_permitted, x_required), and one record, askboth-onepred: the ask-both text written as one
predicate with a '+' and a '-' rule, a clash, refused through `ve norms completions --situation`.

Each fixture carries its case, main's row and the command it was measured with (main b47dd5a505);
the files are the measurement's own, with local paths removed from that command.
"""
from __future__ import annotations

import itertools
import json
import os
from pathlib import Path

import pytest

from tests import lean_routes
from tests.test_clash_gate import _completions, _document, _readings, _refused_points
from ve.backends.relay import rows

KNOWN_DEFECT = "duties-clash-known-defect"

DATA = Path(__file__).resolve().parent / "data" / "norm-defaults-clash"

# Refused through `ve norms completions --audit --situation`: fixture -> run id -> main's point status
# (recorded, b47dd5a505) and the two rules the refusal names.
REFUSED_AT_SITUATION = {
    "a1-stated--file_required--clash-in-cone": (
        {"s1-a1-stated:file_required": "SETTLED yes"}, ("contractors-need-not", "members-file")),
    "b1-stated--file_required--clash-in-cone": (
        {"s1-b1-stated:file_required": "SETTLED yes"}, ("contractors-may-not", "members-file")),
    "b1-stated--file_permitted--clash-in-cone": (
        {"s1-b1-stated:file_permitted": "SETTLED no"}, ("contractors-may-not", "members-file")),
    "u6--x_permitted--clash-in-cone": ({"s1-u6:x_permitted": "SETTLED no"}, ("must-x", "not-x")),
}
# Refused through `ve document readings --conclusion` (contractor(omar) unstated): main gave a
# definite answer on each completion of the fact.
REFUSED_AT_DOCUMENT = {
    "a1-unstated--book_permitted--unstated-cone-fact": (
        {"s1-a1-unstated:book_permitted[contractor=F]": "SETTLED no",
         "s1-a1-unstated:book_permitted[contractor=T]": "SETTLED yes"},
        ("contractors-need-not", "members-file")),
    "b1-unstated--book_permitted--unstated-cone-fact": (
        {"s1-b1-unstated:book_permitted[contractor=F]": "SETTLED no",
         "s1-b1-unstated:book_permitted[contractor=T]": "SETTLED yes"},
        ("contractors-may-not", "members-file")),
}

# KNOWN DEFECT duties-clash-known-defect: fixture -> run id -> main's point status today. Two request
# predicates nothing links: outside the refusal gate's rule, answered SETTLED yes both ways.
KNOWN_DEFECT_STATUS = {
    "askboth--file_requested--clash-in-cone": {"s1-askboth:file_requested": "SETTLED yes"},
    "askboth--refrain_file_requested--clash-in-cone": {"s1-askboth:refrain_file_requested": "SETTLED yes"},
}

# Controls: fixture -> run id -> main's point status today (ordinary tests; right today, or UNDECIDED).
CONTROL_STATUS = {
    "a1-stated--book_permitted--control-answer": {"s1-a1-stated:book_permitted": "SETTLED yes"},
    "b1-stated--book_permitted--control-answer": {"s1-b1-stated:book_permitted": "SETTLED yes"},
    "u6--y_permitted--control-main-undecided": {"s1-u6:y_permitted": "UNDECIDED"},
    "u6--x_required--control-main-undecided": {"s1-u6:x_required": "UNDECIDED"},
}

# The fifth control file, a record: a '+' and a '-' rule on file_requested both fire (main answered
# SETTLED yes); refused through `ve norms completions --situation`.
RECORD = "askboth-onepred--file_requested--record"
RECORD_STATUS = {"s1-askboth-onepred:file_requested": "SETTLED yes"}
RECORD_RULES = ("should-file", "should-not-file")


@pytest.fixture(scope="module")
def lean_executable():
    """The Lean norm-defaults route is the service mode `norm-defaults`; this fixture needs the service."""
    if not lean_routes.SERVICE.exists():
        if os.environ.get("VE_LEAN_PREBUILT"):
            raise AssertionError(f"gate Lean build missing: {lean_routes.SERVICE}")
        pytest.skip("the Lean service has not been built")


def _fixture(path):
    return json.loads(path.read_text())


def _split(case):
    """The empty vs full unsaid filling of every `unspecified` regulated predicate, as the fixtures'
    measuring run used it after an UNKNOWN from `enumerate` (yes = full, no = empty)."""
    predicates = case["environment"]["vocabulary"]["predicates"]
    domains = case["model"]["domains"]
    full = {}
    for name, declared in predicates.items():
        regulated = declared.get("regulated")
        if regulated and regulated["default"] == "unspecified":
            full["unsaid__" + name] = [list(row) for row in
                                       itertools.product(*(domains[s] for s in declared["arguments"]))]
    return full, {table: [] for table in full}


def _main_rows(fixture):
    """Main's row for each run of `fixture`, measured the way the fixture records it."""
    cases = [run["case"] for run in fixture["runs"]]
    got = rows("norm-defaults", cases)
    for i, run in enumerate(fixture["runs"]):
        if run["method"] == "enumerate":
            continue
        assert run["method"] == "undecided (empty vs full filling)", run["method"]
        assert got[i]["status"] == "ok" and got[i]["point_status"] == "UNKNOWN", got[i]
        yes, no = _split(run["case"])
        got[i] = rows("norm-defaults", [{**run["case"], "method": "undecided", "yes": yes, "no": no}])[0]
    return got


def _recorded(fixture, expected):
    """The fixture's recorded main answers (b47dd5a505) are the ones listed here."""
    assert {run["case"]["id"]: run["main_row"]["point_status"] for run in fixture["runs"]} == expected


def _check(path, expected):
    fixture = _fixture(path)
    assert fixture["name"] == path.stem
    _recorded(fixture, expected)
    got = _main_rows(fixture)
    assert {row["id"]: row["point_status"] for row in got} == expected
    assert got == [run["main_row"] for run in fixture["runs"]]


def _situation_refusal(tmp_path, capsys, path, expected, rules):
    """`ve norms completions --audit --situation` on the fixture's one run: the asked point is refused, naming
    both rules."""
    fixture = _fixture(path)
    assert fixture["name"] == path.stem
    _recorded(fixture, expected)
    (run,) = fixture["runs"]
    case = run["case"]
    row = _refused_points(_completions(tmp_path, capsys, case))[(case["predicate"], tuple(case["tuple"]))]
    assert tuple(sorted(row["rules"])) == rules
    assert row["text"].startswith("VE could not decide this. The document's rules conflict in this situation")
    for rule in rules:
        assert f'rule "{rule}"' in row["text"]
    return case, row


def test_fixture_sets_are_exactly_the_recorded_ones():
    clash = {**REFUSED_AT_SITUATION, **REFUSED_AT_DOCUMENT, **KNOWN_DEFECT_STATUS}
    assert sorted(p.stem for p in DATA.glob("*.json")) == sorted(clash)
    assert sorted(p.stem for p in (DATA / "controls").glob("*.json")) == sorted([*CONTROL_STATUS, RECORD])
    assert (len(REFUSED_AT_SITUATION) + len(REFUSED_AT_DOCUMENT), len(KNOWN_DEFECT_STATUS)) == (6, 2)
    assert len(CONTROL_STATUS) + 1 == 5
    for name in clash:
        fixture = _fixture(DATA / f"{name}.json")
        assert (fixture["expect_design_A"], fixture["refusal_reason"]) == ("REFUSE", name.rsplit("--", 1)[1])


@pytest.mark.parametrize("name", sorted(REFUSED_AT_SITUATION))
def test_clash_is_refused_at_completions_situation(name, tmp_path, capsys, lean_executable):
    """Main answered the asked point SETTLED; `ve norms completions --audit --situation` now refuses it, naming
    both rules."""
    expected, rules = REFUSED_AT_SITUATION[name]
    _situation_refusal(tmp_path, capsys, DATA / f"{name}.json", expected, rules)


@pytest.mark.parametrize("name", sorted(REFUSED_AT_DOCUMENT))
def test_unstated_fact_clash_is_refused_at_document_readings(name, tmp_path, capsys, lean_executable):
    """contractor(omar) unstated: main answered each completion definitely, and differently; `ve document
    readings --conclusion` on the document without that fact now refuses, naming both rules."""
    expected, rules = REFUSED_AT_DOCUMENT[name]
    fixture = _fixture(DATA / f"{name}.json")
    assert fixture["name"] == name
    _recorded(fixture, expected)
    case = fixture["runs"][0]["case"]
    path = _document(tmp_path, case, drop=("contractor",))
    result = _readings(tmp_path, capsys, path, ["unary", case["predicate"], ["const", case["tuple"][0]]])
    assert result["status"] == "refused" and result["reason"] == "rules-conflict", result
    assert tuple(sorted(result["rules"])) == rules
    for rule in rules:
        assert f'rule "{rule}"' in result["text"]
    assert "the text allows a situation where both apply" in result["text"]


@pytest.mark.parametrize("name", sorted(KNOWN_DEFECT_STATUS))
def test_known_defect_clash_status_is_recorded(name, lean_executable):
    """KNOWN DEFECT duties-clash-known-defect: records a wrong definite answer at a should/should-not clash written as two request predicates; do not build on it; outside the refusal gate's rule (no declared request/refrain link)"""
    _check(DATA / f"{name}.json", KNOWN_DEFECT_STATUS[name])


@pytest.mark.parametrize("name", sorted(CONTROL_STATUS))
def test_clash_control_status(name, lean_executable):
    """A point beside a clash fixture: main's answer today (right, or already UNDECIDED)."""
    _check(DATA / "controls" / f"{name}.json", CONTROL_STATUS[name])


def test_clash_record_one_predicate_is_refused(tmp_path, capsys, lean_executable):
    """The fifth control file: the ask-both text as one predicate with a '+' and a '-' rule. Main answered
    SETTLED yes; `ve norms completions --situation` now refuses it, naming both rules."""
    _situation_refusal(tmp_path, capsys, DATA / "controls" / f"{RECORD}.json", RECORD_STATUS, RECORD_RULES)


def test_clash_refusals_name_both_signs_of_rule(tmp_path, capsys, lean_executable):
    """Where a '+' and a '-' rule sit on the asked predicate itself (A1, and the one-predicate ask-both record),
    the refusal names one rule of each sign (main's row named both as firing and gave one definite answer)."""
    for path, expected, rules in (
            (DATA / "a1-stated--file_required--clash-in-cone.json",
             *REFUSED_AT_SITUATION["a1-stated--file_required--clash-in-cone"]),
            (DATA / "controls" / f"{RECORD}.json", RECORD_STATUS, RECORD_RULES)):
        case, row = _situation_refusal(tmp_path, capsys, path, expected, rules)
        signs = {n["norm"]["name"]: n["norm"]["sign"] for n in case["norms"]
                 if n["norm"]["predicate"] == case["predicate"]}
        assert sorted(signs[r] for r in row["rules"]) == [False, True]
