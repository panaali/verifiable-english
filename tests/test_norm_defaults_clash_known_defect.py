"""norm-defaults@0 status at clashing duty rules: today's answers, recorded (docs/spec/norm-defaults.md 2.5).

KNOWN DEFECT duties-clash-known-defect: records a wrong definite answer at a must/need-not clash; do not build on it; the fix (duties-clash-refuse-design) flips these to REFUSED

Where duty rules clash at a point, the duty status check (`norm-defaults-status`) reports one side
as SETTLED instead of refusing: it counts every admissible filling (2.5) and does not consult the
conflict check (3.1). The eight fixtures under tests/data/norm-defaults-clash/*.json are the points
the refusal design (duties-clash-refuse-design) must refuse; they pin main's answer exactly, through
the entry they were measured with: `ve.backends.relay.rows("norm-defaults", ...)`.

- Six clash points: A1 (a 'must' and a 'need not' rule on file_required), B1 (a 'must' rule and a
  'may not' rule on its permission pair; asked both ways), u6 (main's own fixture: the pair is broken
  under the filling y_permitted(a) = yes), and the ask-both text ("should file" and "should not file"
  as two request predicates), which is answered both ways. The conflict check reports A1, B1 and u6
  as CONFLICT; it does not see the ask-both pair, two predicates to it.
- Two unstated-fact points (a1-unstated, b1-unstated): round 3 of the same A1 and B1 texts, where
  contractor(omar) is not stated. Main's status needs a complete situation, so each completion of
  that fact is recorded; each gives a definite answer, and the two differ. The refusal design refuses
  the point because the fact is unstated; there is no clash at the asked point itself.

They are not xfail and not skip: they pass today and fail when the behaviour changes, so the fix has
to edit them on purpose (to REFUSED). Each compares main's whole row, so an unrelated change to the
row's fields fails them too; that is the price of recording the answer exactly.

The files under tests/data/norm-defaults-clash/controls/ are ordinary tests: four points beside the
clash whose answer is right today (A1 and B1 book_permitted) or that main already leaves UNDECIDED
(u6 y_permitted, x_required), and one record, askboth-onepred: the ask-both text written as one
predicate with a '+' and a '-' rule, a clash main also answers SETTLED yes (marked below).

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
from ve.backends.relay import rows

KNOWN_DEFECT = "duties-clash-known-defect"
FIX_ROW = "duties-clash-refuse-design"

DATA = Path(__file__).resolve().parent / "data" / "norm-defaults-clash"

# KNOWN DEFECT duties-clash-known-defect: fixture -> run id -> main's point status today. A clash
# point should be refused; an unstated-fact point gives a definite answer on each completion of the fact.
KNOWN_DEFECT_STATUS = {
    "a1-stated--file_required--clash-in-cone": {"s1-a1-stated:file_required": "SETTLED yes"},
    "a1-unstated--book_permitted--unstated-cone-fact": {
        "s1-a1-unstated:book_permitted[contractor=F]": "SETTLED no",
        "s1-a1-unstated:book_permitted[contractor=T]": "SETTLED yes"},
    "b1-stated--file_required--clash-in-cone": {"s1-b1-stated:file_required": "SETTLED yes"},
    "b1-stated--file_permitted--clash-in-cone": {"s1-b1-stated:file_permitted": "SETTLED no"},
    "b1-unstated--book_permitted--unstated-cone-fact": {
        "s1-b1-unstated:book_permitted[contractor=F]": "SETTLED no",
        "s1-b1-unstated:book_permitted[contractor=T]": "SETTLED yes"},
    "askboth--file_requested--clash-in-cone": {"s1-askboth:file_requested": "SETTLED yes"},
    "askboth--refrain_file_requested--clash-in-cone": {"s1-askboth:refrain_file_requested": "SETTLED yes"},
    "u6--x_permitted--clash-in-cone": {"s1-u6:x_permitted": "SETTLED no"},
}

# Controls: fixture -> run id -> main's point status today (ordinary tests; right today, or UNDECIDED).
CONTROL_STATUS = {
    "a1-stated--book_permitted--control-answer": {"s1-a1-stated:book_permitted": "SETTLED yes"},
    "b1-stated--book_permitted--control-answer": {"s1-b1-stated:book_permitted": "SETTLED yes"},
    "u6--y_permitted--control-main-undecided": {"s1-u6:y_permitted": "UNDECIDED"},
    "u6--x_required--control-main-undecided": {"s1-u6:x_required": "UNDECIDED"},
}

# The fifth control file, a record: KNOWN DEFECT duties-clash-known-defect (a '+' and a '-' rule on
# file_requested both fire; main answers SETTLED yes; the refusal design refuses it).
RECORD = "askboth-onepred--file_requested--record"
RECORD_STATUS = {"s1-askboth-onepred:file_requested": "SETTLED yes"}


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


def _check(path, expected):
    fixture = _fixture(path)
    assert fixture["name"] == path.stem
    assert {run["case"]["id"]: run["main_row"]["point_status"] for run in fixture["runs"]} == expected
    got = _main_rows(fixture)
    assert {row["id"]: row["point_status"] for row in got} == expected
    assert got == [run["main_row"] for run in fixture["runs"]]


def test_fixture_sets_are_exactly_the_recorded_ones():
    assert sorted(p.stem for p in DATA.glob("*.json")) == sorted(KNOWN_DEFECT_STATUS)
    assert sorted(p.stem for p in (DATA / "controls").glob("*.json")) == sorted([*CONTROL_STATUS, RECORD])
    assert len(KNOWN_DEFECT_STATUS) == 8 and len(CONTROL_STATUS) + 1 == 5
    for name in KNOWN_DEFECT_STATUS:
        fixture = _fixture(DATA / f"{name}.json")
        assert (fixture["expect_design_A"], fixture["refusal_reason"]) == ("REFUSE", name.rsplit("--", 1)[1])


@pytest.mark.parametrize("name", sorted(KNOWN_DEFECT_STATUS))
def test_known_defect_clash_status_is_recorded(name, lean_executable):
    """KNOWN DEFECT duties-clash-known-defect: records a wrong definite answer at a must/need-not clash; do not build on it; the fix (duties-clash-refuse-design) flips these to REFUSED

    (a1-unstated and b1-unstated: a definite answer on each completion of an unstated fact; see the module docstring.)"""
    _check(DATA / f"{name}.json", KNOWN_DEFECT_STATUS[name])


@pytest.mark.parametrize("name", sorted(CONTROL_STATUS))
def test_clash_control_status(name, lean_executable):
    """A point beside a clash fixture: main's answer today (right, or already UNDECIDED)."""
    _check(DATA / "controls" / f"{name}.json", CONTROL_STATUS[name])


def test_clash_record_one_predicate_status(lean_executable):
    """KNOWN DEFECT duties-clash-known-defect: records a wrong definite answer at a must/need-not clash; do not build on it; the fix (duties-clash-refuse-design) flips these to REFUSED

    (The fifth control file: the ask-both text as one predicate with a '+' and a '-' rule.)"""
    _check(DATA / "controls" / f"{RECORD}.json", RECORD_STATUS)


def test_clash_points_name_both_signs_of_rule():
    """KNOWN DEFECT duties-clash-known-defect: records a wrong definite answer at a must/need-not clash; do not build on it; the fix (duties-clash-refuse-design) flips these to REFUSED

    Where a '+' and a '-' rule sit on the asked predicate itself (A1, and the one-predicate ask-both
    record), the recorded row names both as firing and still gives one definite answer. (The rows
    themselves are checked against main by the tests above.)"""
    for path in (DATA / "a1-stated--file_required--clash-in-cone.json",
                 DATA / "controls" / f"{RECORD}.json"):
        (run,) = _fixture(path)["runs"]
        assert run["main_row"]["point_status"].startswith("SETTLED ")
        signs = {n["norm"]["name"]: n["norm"]["sign"] for n in run["case"]["norms"]
                 if n["norm"]["predicate"] == run["case"]["predicate"]}
        assert sorted(signs[r] for r in run["main_row"]["rules"]) == [False, True]
