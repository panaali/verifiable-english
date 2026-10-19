"""ET-8 (events-time-causation plan 5, fixture R2 and the ET-1 component): Asimov's v2 rules and the ET-1
component re-run with `permitted` completed `unspecified` under `norm-defaults@0`. Each test reruns part of a harness
(`usecases/asimov-extended/asimov_unspecified.py`, `experiments/events-time-causation/et8_component.py`) on Lean's
alternatives route and compares it with the committed results; every verdict, status and text is Lean's."""
from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "usecases" / "asimov-extended"))
sys.path.insert(0, str(REPO / "experiments" / "events-time-causation"))

import asimov_unspecified as asimov  # noqa: E402
import et8_component as component  # noqa: E402

ASIMOV = json.loads((REPO / "usecases/asimov-extended/unspecified-results.json").read_text())
EVIDENCE = REPO / "docs/events-time-causation/et-8/evidence"
COMPONENT = json.loads((EVIDENCE / "component-results.json").read_text())
# Records whose clear set the completion keeps, removes or empties, one per group, and one that needs risk@0.
RECORDS = ("S:a", "S:e", "R:obedience-destroys-robot", "R:rescue-destroys-robot", "O:O6 j-later-authority-unlawful",
           "P:P6 two-deaths-vs-one", "P:P2 certain-injury-vs-possible-death")


@lru_cache(maxsize=1)
def sources():
    raw = asimov.environment()
    doc, check = asimov.checked(raw)
    rules = [rule.to_dict() for rule in doc.rules]
    return check, {d: asimov.source_case(asimov.environment(d), rules) for d in ("allow", "deny", "unspecified")}


def test_v2_rules_stay_checked_and_conflict_free_under_unspecified():
    check, src = sources()
    assert check == ASIMOV["checked"] == {"rules": 13, "same_text": True, "same_blocks": True,
                                          "same_text_digest": True}
    assert src["unspecified"]["environment"]["vocabulary"]["predicates"]["permitted"]["regulated"]["default"] == \
        "unspecified"
    packages, result = asimov.conflict(src["unspecified"])
    assert result == ASIMOV["conflict"]
    assert (result["verdict"], result["unproved"], result["unspecified"]) == ("CONFLICT-FREE", [], ["permitted"])
    assert asimov.witnesses(src["unspecified"], packages) == ASIMOV["witnesses"]


def test_rerun_spec_models_and_records_equal_the_committed_results():
    _, src = sources()
    models = {item["id"]: item["scenario"] for item in asimov.spec_cases()}
    spec = asimov.decide(src["unspecified"], {name: models[name] for name in ("a", "d-full", "o-7")})
    assert spec == {name: ASIMOV["spec_models"]["results"][name] for name in spec}
    section = asimov.records_section(src, names=RECORDS)
    assert section["not_run_need_risk"] == ASIMOV["records"]["not_run_need_risk"]
    assert sorted(section["results"]) == sorted(set(RECORDS) - {"P:P2 certain-injury-vs-possible-death"})
    assert section["results"] == {n: ASIMOV["records"]["results"][n] for n in section["results"]}
    assert section["allow_differs_from_committed"] == []


def test_the_committed_counts_derive_from_the_committed_rows():
    """The summary counts are those of the per-record rows; an action is clear only where it is clear under every
    filling (never beyond allow's clear set), and UNDECIDED only from two validated fillings."""
    records, rows = ASIMOV["records"], ASIMOV["records"]["results"]
    assert (records["records"], records["run"], len(rows), len(records["not_run_need_risk"])) == (51, 43, 43, 8)
    assert records["clear"] == {"allow": sum(bool(r["allow"]) for r in rows.values()),
                                "deny": sum(bool(r["deny"]) for r in rows.values()),
                                "unspecified": sum(bool(r["unspecified"]["clear"]) for r in rows.values())}
    assert (records["clear"], ASIMOV["spec_models"]["clear"]) == ({"allow": 30, "deny": 11, "unspecified": 11}, 2)
    assert all(set(r["unspecified"]["clear"]) <= set(r["allow"]) for r in rows.values())
    assert all(sorted(r["unspecified"]["clear"]) == sorted(r["deny"]) for r in rows.values())
    assert records["with_undecided"] == sorted(
        n for n, r in rows.items() if any(s == "undecided" for s, _ in r["unspecified"]["statuses"].values()))
    decided = [r["unspecified"] for r in rows.values()] + list(ASIMOV["spec_models"]["results"].values())
    pairs = [pair for row in decided for pair in row["statuses"].values()]
    assert all((status == "undecided") == (evidence == "fillings") for status, evidence in pairs)
    assert {status for status, _ in pairs} == {"clear", "not clear", "undecided"}


def test_the_switched_component_differs_from_phase_1_only_in_the_completion_and_the_legend():
    phase1 = json.loads(component.PHASE1.read_text())
    src, scenario = component.component()
    assert scenario == phase1["scenario"] and src["norms"] == phase1["norms"] and src["units"] == phase1["units"]
    env, old = src["environment"], phase1["environment"]
    assert env["profiles"] == sorted([*old["profiles"], "norm-defaults@0"])
    assert env["vocabulary"]["predicates"]["permitted"] == {
        **old["vocabulary"]["predicates"]["permitted"], "description": "The response may be given",
        "regulated": {**old["vocabulary"]["predicates"]["permitted"]["regulated"], "default": "unspecified"}}
    assert "hard constraint" not in json.dumps(env["vocabulary"]["predicates"]["permitted"])
    rest = lambda e: {k: v for k, v in e["vocabulary"]["predicates"].items() if k != "permitted"}  # noqa: E731
    assert rest(env) == rest(old)
    assert json.loads((EVIDENCE / "component.json").read_text()) == src | {"scenario": scenario}


def test_the_et1_component_on_the_completion_equals_the_committed_results():
    """As translated, no rule permits refusal: CONFLICT-FREE, no FOLLOWABLE certificate, and a DILEMMA
    `UNSETTLED(refuse)` where refusal is the only response. Only with u0172.s02 read as a permission (the targeted
    audit's question) is the component FOLLOWABLE, conditional on both premises."""
    _, results = component.compute()
    assert results == COMPONENT
    found, reading = results["component"], results["permission_reading"]
    assert (found["conflict"]["verdict"], found["followable_certificate"], found["followable"]["verdict"]) == (
        "CONFLICT-FREE", False, "UNKNOWN")
    assert found["refusal_only"]["witness"]["verdict"] == "DILEMMA"
    assert found["refusal_only"]["witness"]["diagnosis"].startswith("UNSETTLED(refuse): ")
    assert found["phase1_scenario"]["witness"]["diagnosis"].startswith("UNSETTLED(refuse, answer): ")
    assert found["phase1_scenario"]["scenario"] == {"undermine": ["not clear", "kleene"],
                                                     "refuse": ["undecided", "fillings"],
                                                     "answer": ["undecided", "fillings"]}
    assert (reading["followable"]["verdict"], reading["followable"]["conditional_on"]) == (
        "FOLLOWABLE", ["u0172.s02:refusal-available", "u0172.s02:refusal-compatible"])
    assert reading["refusal_only"]["scenario"] == {"refuse": ["clear", "kleene"]}
