"""norm-defaults@0: Python, Lean and Rust agree on the spec fixtures (docs/spec/norm-defaults.md 8, 9).

Rust's leg is `rust/ve-core/tests/norm_defaults.rs` over `conformance/norm_defaults_rust.json`
(tests/test_norm_defaults.py checks that file is Python's regeneration); this file runs the
Python/Lean legs through `ve_norm_defaults_route`.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from copy import deepcopy

import pytest

from conformance.norm_defaults_three_way import (admission_document, certificate_case, conflict_case,
                                                 fixtures, run)
from ve import norm_defaults as nd
from ve import norm_defaults_route as route
from ve.admission import admit_document
from ve.environment import Environment
from ve.errors import VEError
from ve.norms import NormDocument

LEAN = route.LEAN_ROUTE


@pytest.fixture(scope="module")
def lean_executable():
    if os.environ.get("VE_LEAN_PREBUILT"):
        assert LEAN.is_file(), f"gate Lean build missing: {LEAN}"
        return LEAN
    if not LEAN.exists():
        lake = shutil.which("lake")
        if lake is None:
            pytest.skip("lake is required for the norm-defaults route")
        built = subprocess.run([lake, "build", "ve_norm_defaults_route"], cwd=LEAN.parents[3],
                               capture_output=True, text=True, timeout=1800)
        assert built.returncode == 0, built.stdout + built.stderr
    return LEAN


def _document(name):
    for fixture, env, units, _ in fixtures():
        if fixture == name:
            return nd.UnspecifiedDocument(Environment(env), [NormDocument._decode(u) for u in units])
    raise KeyError(name)


def test_three_way_fixtures(lean_executable):
    result = run(lean_executable)
    rows = {row["fixture"]: row for row in result["fixtures"]}
    assert [r for r in result["fixtures"] if r["mismatches"]] == []
    assert result["passed"] == len(rows) == 12
    assert all(set(r["kinds"]) >= {"elaborate", "status", "conflict", "gaps", "certificate", "admission"}
               for r in rows.values())
    # The spec 9 expectations, as both engines report them.
    assert rows["u1"]["statuses"] == ["SETTLED no", "UNDECIDED"] and rows["u1"]["gaps"] == ["reachable"]
    assert rows["u1-allow"]["statuses"] == ["SETTLED no", "SETTLED yes"]
    assert rows["u1-deny"]["statuses"] == ["SETTLED no", "SETTLED no"]
    assert rows["u5a"]["conflict"] == ["CONFLICT-FREE"] and set(rows["u5a"]["statuses"]) == {"SETTLED no"}
    assert set(rows["u5b"]["statuses"]) == {"SETTLED yes"}
    assert set(rows["u5c"]["statuses"]) == {"UNDECIDED"}
    assert rows["u6"]["conflict"] == ["CONFLICT"] and rows["u6-deny"]["conflict"] == ["CONFLICT-FREE"]
    assert "UNDECIDED" in rows["u6"]["statuses"]
    assert set(rows["u7"]["statuses"]) == {"UNDECIDED"}
    assert rows["u12"]["statuses"] == ["UNDECIDED", "UNDECIDED", "SETTLED yes", "SETTLED yes"]
    assert rows["u15-deny"]["gaps"] == rows["u15-unspecified"]["gaps"] == ["none"]
    assert rows["u15-deny"]["statuses"] == rows["u15-unspecified"]["statuses"]


def test_python_enumeration_is_replayed_by_lean_enumeration(lean_executable):
    """u12: `table3` is unknown and enumeration settles; Lean's `enumerate` agrees."""
    doc = _document("u12")
    situation = doc.situation(fixtures_situation("u12"))
    status = doc.status(situation, "x_permitted", ("a",))
    assert (status.status, status.value, status.evidence) == ("SETTLED", True, "enumeration")
    base = route.source_case(doc, "norm-defaults-status", model=situation.to_dict(),
                             predicate="x_permitted", tuple=["a"])
    rows = route.run_cases([{**base, "method": "enumerate"}, {**base, "method": "table3"}], lean_executable)
    assert [r["point_status"] for r in rows] == ["SETTLED yes", "UNKNOWN"]


def fixtures_situation(name):
    return next(situations[0] for fixture, _, _, situations in fixtures() if fixture == name)


def test_mutations_are_rejected_by_both(lean_executable):
    """u14: a flipped completion makes the stale packages and certificates fail; a
    dropped `Fill_T` premise is not the bound premise list."""
    doc = _document("u5a")
    report, case = conflict_case(doc, fixtures_situation("u5a"))
    assert report.status == "CONFLICT-FREE"
    flipped = deepcopy(case)
    flipped["environment"]["vocabulary"]["predicates"]["x_required"]["regulated"]["default"] = "deny"
    stale = nd.check_conflict(nd.UnspecifiedDocument(Environment(flipped["environment"]), []),
                              certificates=report.certificates)
    assert stale.status == "UNKNOWN"
    rows = route.run_cases([case, flipped], lean_executable)
    assert [r["verdict"] for r in rows] == ["CONFLICT-FREE", "UNKNOWN"]

    certified = certificate_case(doc)
    dropped = deepcopy(certified)
    dropped["certificate"]["premise_meaning_ids"] = [
        pid for i, pid in enumerate(dropped["certificate"]["premise_meaning_ids"]) if i != 1]
    rows = route.run_cases([certified, dropped], lean_executable)
    assert rows[0]["valid"] is True
    assert rows[1].get("valid") is not True


def test_admission_tampering_is_rejected_by_both(lean_executable):
    """Leaves under the profile are W2 provenance or exactly a regenerated premise of
    `fill U`; certificates bind `E‴`, and the report id binds the source."""
    doc = _document("u5a")
    raw = doc.env.to_dict()
    good = admission_document(doc)
    labels = [n.get("label") for n in good["graph"]["nodes"]]
    assert "unsaid:pair:x_required,x_permitted" in labels and "background:profile" in labels
    fill = labels.index("unsaid:pair:x_required,x_permitted")
    layer = labels.index("layer:norms:x_required")

    def mutant(edit):
        document = deepcopy(good)
        edit(document["graph"]["nodes"])
        return document
    mutants = {
        "fill label": mutant(lambda ns: ns[fill].update(label="unsaid:pair:x_permitted,x_required")),
        "fill formula": mutant(lambda ns: ns[fill].update(ast=ns[layer]["ast"])),
        "fill with a unit": mutant(lambda ns: ns[fill].update(unit="n0")),
        "layer swapped": mutant(lambda ns: ns[layer].update(ast=ns[fill]["ast"])),
        "certificate on the source": mutant(lambda ns: ns[-1]["certificate"].update(
            environment_id=doc.env.environment_id)),
    }
    python = admit_document(raw, good)
    rows = route.run_cases([{"id": "good", "kind": "admission", "environment": raw, "document": good}] +
                           [{"id": k, "kind": "admission", "environment": raw, "document": d}
                            for k, d in mutants.items()], lean_executable)
    assert {k: v for k, v in rows[0].items() if k not in ("id", "status")} == python
    for (label, document), row in zip(mutants.items(), rows[1:]):
        with pytest.raises(VEError) as error:
            admit_document(raw, document)
        assert row["status"] == "error", (label, row)
        assert row["error"] == str(error.value), label


def test_profiled_admission_without_unspecified_is_w1_admission(lean_executable):
    """Conservativity (spec 6): with no `unspecified` predicate `fill U` is the author tree,
    and the profiled admission report equals W1's on the same graph."""
    doc = _document("u6-deny")
    raw = doc.env.to_dict()
    document = admission_document(doc)
    profiled = admit_document(raw, document)
    plain = deepcopy(raw)
    plain["profiles"] = [p for p in raw["profiles"] if p != nd.PROFILE]
    # E‴ is E without the profile, so the certificates already bind the W1 environment.
    w1 = admit_document(plain, document)
    assert profiled["report"] == w1["report"] and profiled["kinds"] == w1["kinds"]
    row = route.run_cases([{"id": "p", "kind": "admission", "environment": raw, "document": document}],
                          lean_executable)[0]
    assert {k: v for k, v in row.items() if k not in ("id", "status")} == profiled
