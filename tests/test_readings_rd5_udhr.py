"""The UDHR pilot of readings-defaults RD-5 (usecases/udhr-pilot/run-20261010T1400Z), against its saved evidence.

The report tests read only what the run saved (`metrics.json`, `unmigrated.json`, the migrated document, the check
reports and the query answers), never a live diff or a fresh measurement, so they hold after syncs with main and after
the merge. Two tests rerun a part of the pilot through Lean: the migration, which must reproduce the committed
document byte for byte, and the witness replay of one set, which must equal the recorded statuses.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from tests import lean_routes

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "usecases/udhr-pilot/run-20261010T1400Z"
sys.path.insert(0, str(RUN))

import migrate  # noqa: E402
import summary  # noqa: E402


def saved(name):
    return json.loads((RUN / name).read_text())


METRICS = saved("metrics.json")
UNMIGRATED = saved("unmigrated.json")
AFTER = saved("reports/after.check.json")
META, SOURCE = migrate.split_document((RUN / "translation.ve.md").read_bytes())


def lean():
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service has not been built")


def test_the_summary_is_rendered_from_the_saved_metrics():
    assert (RUN / "SUMMARY.md").read_text() == summary.render(METRICS, AFTER)


def test_the_share_is_the_span_bytes_of_leans_decided_units():
    """3.9: the decided units are Lean's (the check report's readings block); the bytes are their spans."""
    after = METRICS["after"]["share"]
    assert after["decided_units"] == AFTER["readings"]["decided_units"]
    spans = {u["id"]: u["span"][1] - u["span"][0] for u in META["units"]}
    assert after["decided_bytes"] == sum(spans[u] for u in after["decided_units"]) == 2111
    assert after["source_bytes"] == len(SOURCE) == 10916
    assert after["decided_share_percent"] == f"{100 * after['decided_bytes'] / after['source_bytes']:.2f}" == "19.34"
    assert after["basis"] == "readings-verdicts decided_units"
    before = METRICS["before"]["share"]
    assert (before["decided_bytes"], before["decided_units"], before["basis"]) == \
        (0, [], "no Lean answer across readings")
    assert set(after["decided_units"]) <= {u for u in spans}
    # Every decided unit's set migrated (or it is the fixed unit), and no set left on W2 is decided.
    sets = {s["unit"]: s for s in META["reading_sets"]}
    left = {x["set"] for x in UNMIGRATED["not_migrated"]}
    assert all(u not in sets or sets[u]["id"] in UNMIGRATED["migrated"] for u in after["decided_units"])
    assert not [s for s in left if sets[s[3:]]["unit"] in after["decided_units"]]


def test_the_migration_record_holds_together():
    assert UNMIGRATED["sets"] == len(META["reading_sets"]) == 49
    ids = [s["id"] for s in META["reading_sets"]]
    left = [x["set"] for x in UNMIGRATED["not_migrated"]]
    assert sorted(UNMIGRATED["migrated"] + left) == sorted(ids) and not set(UNMIGRATED["migrated"]) & set(left)
    assert (len(UNMIGRATED["migrated"]), len(left)) == (22, 27)
    for x in UNMIGRATED["not_migrated"]:
        # E1: every set left on W2 is one Lean's split refused for two readings declaring a name differently.
        assert x["reason"].startswith(f"InvalidInput: readings {x['set']}@") and x["reason"].endswith(" differently")
    for item in META["reading_sets"]:
        if item["id"] in UNMIGRATED["migrated"]:
            assert "models" not in item and (item["situations"] or len(item["readings"]) == 1)
            assert all("companion" in r and r["content"] is not None for r in item["readings"])
            assert all(set(r["admission"]["distinguishing_models"]) == {o["id"] for o in item["readings"]} - {r["id"]}
                       for r in item["readings"])
        else:
            assert not any("companion" in r for r in item["readings"]) and "situations" not in item
    assert sorted(UNMIGRATED["copied_declarations"]) == ["rs_u052:case_excluded", "rs_u112:exercise_unprotected",
                                                         "rs_u114:no_implied_right"]
    assert META["environment"]["profiles"] == sorted({*migrate.ADDED_PROFILES, "documents@1", "norms@0",
                                                      "relational-fol@0"})


def test_the_saved_measurements_meet_the_limits():
    """Plan 3.8's limits, read from their owners where Python holds them (the document bytes, the choices checked one
    at a time); the per-frame limits are the frozen decoders', and Lean admitted the document under them."""
    from ve.document import MAX_DOCUMENT_BYTES
    from ve.readings_sup import MAX_CHOICES
    comp, after = METRICS["components"], METRICS["after"]
    assert after["document_bytes"] <= MAX_DOCUMENT_BYTES and comp["max_choices"] <= MAX_CHOICES
    assert after["load"]["wall_seconds"] <= 120  # the lean-first section 4 budget for the pilot's load
    assert comp["count"] == comp["companion_cases"] + 1 == len(UNMIGRATED["migrated"]) + 1
    per = comp["per_component"]
    assert comp["max_rules_in_one_choice_document"] == max(c["rules"] for s in per.values() for c in s["per_choice"])
    assert all(c["rules"] == c["author_rules"] + c["generated_rules"] for s in per.values() for c in s["per_choice"])
    assert sorted(comp["main_unchecked_sets"]) == sorted(x["set"] for x in UNMIGRATED["not_migrated"])
    assert (after["premises"], after["conflict"], METRICS["before"]["premises"]) == ("model", "CONFLICT-FREE",
                                                                                   "UNKNOWN")
    assert after["bytes_by_status"] == METRICS["before"]["bytes_by_status"]


def test_every_witness_and_companion_check_is_recorded_equal():
    w = METRICS["witnesses"]
    comp = [x for v in w["in_components"].values() for x in v["witnesses"]]
    alone = [x for v in w["alone"].values() for x in v["witnesses"]]
    assert (w["in_components_total"], w["in_components_same"]) == (len(comp), sum(x["same"] for x in comp)) == \
        (152, 152)
    assert (w["alone_total"], w["alone_same"]) == (len(alone), sum(x["same"] for x in alone)) == (459, 459)
    assert all(x["same"] == (x["lean"] == x["recorded"]) for x in comp + alone)
    assert w["companions_alone"] == len(w["alone"]) == 156
    assert w["companions_alone_model"] == sum(v["premises"] == "model" for v in w["alone"].values()) == 156
    # Every migrated set's companions were replayed in its component; a reading without a companion has none.
    assert {v["set"] for v in w["in_components"].values() if "set" in v} == set(UNMIGRATED["migrated"])
    assert [k for k, v in w["in_components"].items() if "set" not in v] == ["u114.no_implied_right"]


def test_the_queries_answer_as_the_spec_derived_and_their_english_is_saved():
    names = [q["name"] for q in METRICS["queries"]]
    assert names == ["u029-recognise", "u081-secure", "u081-secure-under-2", "u081-none"]
    for q in METRICS["queries"]:
        answer = saved(q["answer"])
        assert q["exit"] == 0 and q["verdict"] == q["expected"] == answer["verdict"]
        assert q["english"] == answer["english"] and answer["sentence"] == q["sentence"]
    under = METRICS["queries"][2]
    assert under["under"] == ["rs_u081:2"] and len(under["english"]) == 3


def test_copied_environment_holds_only_what_the_assertion_mentions():
    """The copied companion of `rs_u052`'s asserted reading: the main frame's declarations of the predicates it
    mentions and their sorts, without the verbalisation the norm companion gives them (so Lean's split refuses the
    set, E1)."""
    formula = ["forall", "prosecution", ["implies", ["or", ["unary", "arises_from_non_political_crime", ["var", 0]],
                                                           ["unary", "arises_from_acts_contrary_to_un", ["var", 0]]],
                                         ["not", ["unary", "asylum_right_covers_case", ["var", 0]]]]]
    main = {"vocabulary": {"constants": {}, "sorts": {"prosecution": {"description": "p"}, "person": {}},
                           "predicates": {name: {"arguments": ["prosecution"], "description": name}
                                          for name in ("arises_from_non_political_crime",
                                                       "arises_from_acts_contrary_to_un",
                                                       "asylum_right_covers_case", "unused")}}}
    like = {"language": "L", "profiles": ["p"], "spec_revision": "r"}
    env, lines = migrate.copied_environment(main, formula, like)
    assert sorted(env["vocabulary"]["predicates"]) == ["arises_from_acts_contrary_to_un",
                                                       "arises_from_non_political_crime", "asylum_right_covers_case"]
    assert list(env["vocabulary"]["sorts"]) == ["prosecution"] and env["profiles"] == ["p"]
    assert lines == ["sort prosecution", "predicate arises_from_acts_contrary_to_un",
                     "predicate arises_from_non_political_crime", "predicate asylum_right_covers_case"]


def test_the_migration_reproduces_the_committed_document(tmp_path):
    """Rerun through Lean from run 20261006T1800Z at bd6c7ab2: the same document and record, byte for byte."""
    lean()
    migrate.migrate(out=tmp_path)
    assert (tmp_path / "translation.ve.md").read_bytes() == (RUN / "translation.ve.md").read_bytes()
    assert json.loads((tmp_path / "unmigrated.json").read_text()) == UNMIGRATED


def test_one_sets_witnesses_replay_equal_in_its_component_and_alone():
    """`rs_u025`'s companions (witnesses SETTLED yes, SETTLED no and UNDECIDED): each witness Lean replays, in the
    component and alone, is the recorded one."""
    lean()
    import witnesses
    from ve.readings_route import document_wire, run_lean
    from ve.readings_s1 import wire
    env, doc = wire(META["environment"]), wire(document_wire(META["units"], META["reading_sets"]))
    [row] = run_lean([{"id": "split", "kind": "readings-elaborate", "environment": env, "document": doc}])
    parts = {c["component"]: c for c in row["components"]}
    got = witnesses.in_components(env, doc, {"rs_u025": parts["rs_u025"]}, only={"rs_u025"})
    assert got == {k: v for k, v in METRICS["witnesses"]["in_components"].items() if k.startswith("u025.")}
    assert {w["recorded"] for v in got.values() for w in v["witnesses"]} == {"SETTLED yes", "SETTLED no", "UNDECIDED"}
    keys = {"u025.practice_prohibited", "u025.state_prohibits"}
    assert witnesses.alone(only=keys) == {k: METRICS["witnesses"]["alone"][k] for k in keys}
