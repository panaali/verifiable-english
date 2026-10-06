"""norm-defaults@0: Python, Lean and Rust agree on the spec fixtures (docs/spec/norm-defaults.md 8, 9).

Rust's leg is `rust/ve-core/tests/norm_defaults.rs` over `conformance/norm_defaults_rust.json`
(tests/test_norm_defaults.py checks that file is Python's regeneration); this file runs the
Python/Lean legs through `ve_norm_defaults_route`.
"""
from __future__ import annotations

import os
from copy import deepcopy

import pytest

from tests import lean_routes

from conformance import norm_defaults_differential as differential
from conformance.norm_defaults_three_way import (admission_document, certificate_case, conflict_case,
                                                 fixtures, run)
from ve import norm_defaults as nd
from ve import norm_defaults_route as route
from ve.admission import admit_document
from ve.environment import Environment
from ve.errors import VEError
from ve.norms import NormDocument

@pytest.fixture(scope="module")
def lean_executable():
    """The Lean norm-defaults route is the service mode `norm-defaults`; this fixture needs the service."""
    if not lean_routes.SERVICE.exists():
        if os.environ.get("VE_LEAN_PREBUILT"):
            raise AssertionError(f"gate Lean build missing: {lean_routes.SERVICE}")
        pytest.skip("the Lean service has not been built")


def _document(name):
    for fixture, env, units, _ in fixtures():
        if fixture == name:
            return nd.UnspecifiedDocument(Environment(env), [NormDocument._decode(u) for u in units])
    raise KeyError(name)


def test_three_way_fixtures(lean_executable):
    result = run()
    rows = {row["fixture"]: row for row in result["fixtures"]}
    assert [r for r in result["fixtures"] if r["mismatches"]] == []
    assert result["passed"] == len(rows) == 18
    assert all(set(r["kinds"]) >= {"elaborate", "table3", "status", "conflict", "gaps", "certificate",
                                   "admission"} for r in rows.values())
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
    # review B1: `a_permitted(a)` sits between the pair's members; `table3` leaves it
    # unknown in both engines and the cone enumeration settles it in both
    between = rows["b1-between"]
    assert between["statuses"][:4] == ["SETTLED yes", "UNDECIDED", "SETTLED yes", "UNDECIDED"]
    assert between["evidence"][:4] == ["table3", "undecided", "enumerate", "undecided"]
    # loop recheck B1: row `b` of `x_required` does not read the close made at row `a`
    # (through ∃ or a constant): unknown in both tables, settled by enumeration in both
    assert rows["b1-rows-exists"]["evidence"] == ["table3", "enumerate"] * 2 + ["enumerate", "table3"] * 2
    assert set(rows["b1-rows-exists"]["statuses"]) == {"SETTLED yes"}
    assert rows["b1-rows-const"]["evidence"][:4] == ["table3", "enumerate"] * 2
    # review B2: 13 unsaid atoms in the situation, one in each point's cone
    assert set(rows["b2-wide"]["statuses"][13:]) == {"SETTLED yes"}  # after y_permitted
    assert set(rows["b2-wide"]["evidence"][13:]) == {"enumerate"}
    # review A1: unreached under U, reachable once switched
    gaps = {name: dict(zip(rows_order(name), rows[name]["gaps"]))
            for name in ("a1-switch-deny", "a1-switch-unspecified")}
    assert gaps["a1-switch-deny"]["p_permitted"] == "none"
    assert gaps["a1-switch-unspecified"]["p_permitted"] == "reachable"


def test_python_enumeration_is_replayed_by_lean_enumeration(lean_executable):
    """u12: `table3` is unknown and enumeration settles; Lean's `enumerate` agrees."""
    doc = _document("u12")
    situation = doc.situation(fixtures_situation("u12"))
    status = doc.status(situation, "x_permitted", ("a",))
    assert (status.status, status.value, status.evidence) == ("SETTLED", True, "enumeration")
    base = route.source_case(doc, "norm-defaults-status", model=situation.to_dict(),
                             predicate="x_permitted", tuple=["a"])
    rows = route.run_cases([{**base, "method": "enumerate"}, {**base, "method": "table3"}])
    assert [r["point_status"] for r in rows] == ["SETTLED yes", "UNKNOWN"]


def rows_order(name):
    return list(_document(name).filled.order)


def test_audit_certificate_replays_on_the_switched_source(lean_executable):
    """Review A1: the migration audit's certificate is `gaps: none` on `U.switch p`, which
    Lean's `normDefaults_wire_gaps_sound` turns into `unreached_switch`'s hypothesis. In 6.3's
    counterexample U's own certificate replays on U, but Lean finds the switched gap reachable."""
    env, units, situations = next((e, u, s) for n, e, u, s in fixtures() if n == "u15-deny")
    rules = [NormDocument._decode(u) for u in units]
    audit = nd.audit_completions(Environment(env), rules, model=situations[0])
    (entry,) = audit["completions"]
    switched = nd.UnspecifiedDocument(Environment(nd._profiled(env, ("x_permitted",)).to_dict()), rules)
    case = route.source_case(switched, "norm-defaults-gaps", predicate="x_permitted",
                             packages={"reached:x_permitted": entry["certificate"]})
    assert route.run_cases([case])[0]["gaps"] == "none"

    env, units, situations = next((e, u, s) for n, e, u, s in fixtures() if n == "a1-switch-deny")
    rules = [NormDocument._decode(u) for u in units]
    unswitched = nd.UnspecifiedDocument(Environment(env), rules)
    (line,) = nd.report(unswitched, prove=True, predicates=("p_permitted",))
    audit = nd.audit_completions(Environment(env), rules, model=situations[0])
    entry = next(e for e in audit["completions"] if e["predicate"] == "p_permitted")
    assert entry["switched_gaps"] == "reachable" and "certificate" not in entry
    switched = nd.UnspecifiedDocument(Environment(nd._profiled(env, ("p_permitted",)).to_dict()), rules)
    situation = switched.situation(situations[0])
    filling = {k: frozenset(tuple(r) for r in v) for k, v in entry["switched_witness"]["filling"].items()}
    cases = [route.source_case(unswitched, "norm-defaults-gaps", predicate="p_permitted",
                               packages={"reached:p_permitted": line.certificate}),
             route.source_case(switched, "norm-defaults-gaps", predicate="p_permitted",
                               model=switched.with_filling(situation, filling).to_dict(),
                               tuple=entry["switched_witness"]["tuple"]),
             route.source_case(switched, "norm-defaults-gaps", predicate="p_permitted",
                               packages={"reached:p_permitted": line.certificate})]
    assert [r["gaps"] for r in route.run_cases(cases)] == ["none", "reachable", "unknown"]


def test_spec8_differentials(lean_executable):
    """Spec 8: 1,000 generated trees regenerate byte for byte in Lean; on 1,000 generated
    situations every `table3` entry and every status is Lean's (conformance/norm_defaults_differential.py)."""
    result = differential.run()
    assert result["mismatches"] == []
    assert result["counts"]["elaborate"] == 1000 and result["counts"]["status"] > 9000
    assert result["counts"]["conflict:latent"] > 0 and result["wide"] > 0 and result["unspecified"] > 500


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
    rows = route.run_cases([case, flipped])
    assert [r["verdict"] for r in rows] == ["CONFLICT-FREE", "UNKNOWN"]

    certified = certificate_case(doc)
    dropped = deepcopy(certified)
    dropped["certificate"]["premise_meaning_ids"] = [
        pid for i, pid in enumerate(dropped["certificate"]["premise_meaning_ids"]) if i != 1]
    rows = route.run_cases([certified, dropped])
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
                            for k, d in mutants.items()])
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
    row = route.run_cases([{"id": "p", "kind": "admission", "environment": raw, "document": document}])[0]
    assert {k: v for k, v in row.items() if k not in ("id", "status")} == profiled
