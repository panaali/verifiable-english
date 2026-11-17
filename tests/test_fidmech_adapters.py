"""fid-mech-b3: the execution adapters (plan section 6; Opus round 2 points 6 and 12).

The projection keeps each document's answer fields (RSP `ve`; PF `ve` and `soft.ve`, no release field; FSF `ve`,
`ve_rel` and `premises`, never the key's `key_rel`), and per item the selected rule ids (RSP choices[*].rules,
FSF details[*]["rules"], PF selected_rules) and the case-model atoms. The Lean tests run each document's baseline
in a fresh worker process and compare it with the committed results.json.
"""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from subprocesses import HANG_TIMEOUT
from tools.fidmech import adapters as A
from tools.fidmech import worker as W

ROOT = Path(__file__).resolve().parents[1]
LEAN_SERVICE = ROOT / "lean/.lake/build/bin/ve_service"
needs_lean = pytest.mark.skipif(not LEAN_SERVICE.exists(), reason="the Lean service is not built")


def committed(document):
    return json.loads((ROOT / "usecases" / document / "results.json").read_text())


@needs_lean
@pytest.mark.parametrize("document", A.DOCUMENTS)
def test_the_adapters_baseline_projection_equals_the_committed_results(document, tmp_path):
    """A fresh worker process runs run() (and FSF's with_comparison()) on a scratch copy of usecases/; its answers,
    rules and agreement equal the projection of the committed results.json, and every item with a case has its
    case-model atoms."""
    outcome = W.Worker(document, ROOT, tmp_path, fresh=True).run(W.BASELINE, HANG_TIMEOUT)
    assert outcome.status == "ok", outcome.error
    live, saved = outcome.projection, A.project(document, committed(document))
    assert live.answers == saved.answers
    assert live.rules == saved.rules
    assert live.agree == saved.agree
    key = {e["id"]: e for e in json.loads((ROOT / "usecases" / document / "answer-key.json").read_text())["items"]}
    with_case = [i for i in live.atoms if key.get(i, {}).get("case") is not None]
    assert with_case and all(live.atoms[i] for i in with_case)
    expected = {"anthropic-rsp": ("K20", [("develops_highly_capable", "c"), ("competitors_evidence", "s")]),
                "openai-preparedness": ("K3", [("distilled_finetuned_or_quantized_from_below_high", "s")]),
                "safety-framework": ("A-L1-DEV", [("reached", "p", "cbrn_uplift_tcl")])}[document]
    item = next(i for i in live.atoms if key.get(i, {}).get("case") == expected[0])
    assert set(expected[1]) <= set(live.atoms[item]), (item, live.atoms[item])


def test_the_answer_fields_follow_the_plans_table():
    assert A.ANSWER_FIELDS == {"anthropic-rsp": ("ve",), "openai-preparedness": ("ve", "soft.ve"),
                               "safety-framework": ("ve", "ve_rel", "premises")}
    rows = [{"id": "Q1", "key": "ALL", "ve": "NONE", "agree": False, "route": "D1", "status": "x", "cause": None,
             "soft": {"key": "RS1=default", "ve": ["RS1=default"]}, "key_rel": "ALL", "ve_rel": "NONE",
             "premises": "model", "seconds": 3, "deviation": {"answer": "NONE"}}]
    assert A.answers_of("anthropic-rsp", rows) == {"Q1": (("ve", "NONE"),)}
    assert A.answers_of("openai-preparedness", rows) == {"Q1": (("ve", "NONE"), ("soft.ve", ("RS1=default",)))}
    assert A.answers_of("safety-framework", rows) == {"Q1": (("ve", "NONE"), ("ve_rel", "NONE"),
                                                             ("premises", "model"))}
    assert A.answers_of("openai-preparedness", [{"id": "Q2", "ve": {"b": "ALL", "a": "NONE"}}]) == {
        "Q2": (("ve", (("a", "NONE"), ("b", "ALL"))),)}
    with pytest.raises(ValueError, match="twice"):
        A.answers_of("anthropic-rsp", rows + rows)


def test_the_selected_rule_ids_are_read_from_each_documents_own_place():
    """Opus round 2 point 6: RSP choices[*].rules (C-doc rows hold rule groups), FSF details[*]["rules"] through
    parts and alternatives, PF selected_rules (never audit_input.rules, the built rules no block holds)."""
    rsp = {"K1": {"choices": [{"rules": ["b", "a"]}, {"rules": []}]},
           "C-doc": {"choices": [{"rules": [["f12-final", "f12-board-approval"], ["x"]]}]},
           "G7": {"parts": {"P": {"choices": [{"rules": ["p1"]}]}}}, "S1": {"value": "NONE"}}
    assert A.rules_of("anthropic-rsp", rsp, ["K1", "C-doc", "G7", "S1", "D9"]) == {
        "K1": ("a", "b"), "C-doc": ("f12-board-approval", "f12-final", "x"), "G7": ("p1",), "S1": (), "D9": ()}
    fsf = {"A": {"details": {"-": {"holds": True, "rules": ["f2"], "release": ["f3"]}}},
           "G6": {"parts": {"GOV": {"details": {"RS2=U": {"rules": ["f13-u"]}}}}},
           "G3": {"alternatives": {"G3a": {"details": {"-": {"rules": ["f6-tcl"]}}}}}}
    assert A.rules_of("safety-framework", fsf, ["A", "G6", "G3"]) == {"A": ("f2",), "G6": ("f13-u",),
                                                                      "G3": ("f6-tcl",)}
    pf = {"K3": {"selected_rules": ["f6-rel"], "audit_input": {"rules": ["invented"]},
                 "choices": [{"rules": ["only-in-a-choice"]}]}}
    assert A.rules_of("openai-preparedness", pf, ["K3"]) == {"K3": ("f6-rel",)}
    with pytest.raises(ValueError, match="no rule id"):
        A.rules_of("anthropic-rsp", {"K1": {"choices": [{"rules": [1]}]}}, ["K1"])


def test_the_committed_results_give_the_rule_ids_the_rsp_tests_name():
    rules = A.project("anthropic-rsp", committed("anthropic-rsp")).rules
    assert (rules["K15a"], rules["K17"]) == (("f20-notify-board",), ("f23-publish",))
    fsf = A.project("safety-framework", committed("safety-framework")).rules
    assert fsf["G6"] == ("f12-u", "f13-u") and fsf["G3"] == ("f6-tcl",)
    assert A.project("openai-preparedness", committed("openai-preparedness")).rules["K3"] == ("f6-rel",)


def stub(tmp_path, document, items, **functions):
    (tmp_path / "answer-key.json").write_text(json.dumps({"items": items}))
    return SimpleNamespace(HERE=tmp_path, CASES={"c1": {"id": "c1"}}, **functions)


def test_the_case_model_atoms_are_those_true_in_every_model_the_item_read(tmp_path):
    """Opus round 2 point 6: PF's atoms depend on the choice, so an item keeps the atoms of every choice it read;
    FSF's are case plus facts, over every alternative of a case; RSP's are the case's atoms."""
    items = [{"id": "Q1", "case": "c1"}, {"id": "Q2", "case": None}]
    pf = stub(tmp_path, "openai-preparedness", items, BASE={"RS2": "sep"},
              atoms=lambda case, choice: {("a", "s"), ("nest", "s")} if choice["RS2"] == "nest" else {("a", "s")})
    results = {"Q1": {"choices": [{"choice": {"RS2": "nest"}}, {"choice": {"RS2": "sep"}}]}}
    assert A.atoms_of("openai-preparedness", pf, results, ["Q1", "Q2"]) == {"Q1": (("a", "s"),), "Q2": ()}
    fsf = stub(tmp_path, "safety-framework", items, item_case=lambda id_, case: case,
               situations=lambda case: [{"x": 1}, {"x": 2}], fact_atoms=lambda: frozenset({("fact", "p")}),
               case_atoms=lambda s: frozenset({("common", "p"), ("only", str(s["x"]))}))
    assert A.atoms_of("safety-framework", fsf, {}, ["Q1"]) == {"Q1": (("common", "p"), ("fact", "p"))}
    rsp = stub(tmp_path, "anthropic-rsp", items, atoms=lambda case: {("b", "s"), ("a", "s")})
    assert A.atoms_of("anthropic-rsp", rsp, {}, ["Q1", "Q2"]) == {"Q1": (("a", "s"), ("b", "s")), "Q2": ()}


def test_freeze_reads_a_json_round_trip_as_the_same_value():
    value = {"b": [1, {"c": ("x", None)}], "a": True}
    assert A.freeze(value) == A.freeze(json.loads(json.dumps(value))) == (("a", True), ("b", (1, (("c", ("x", None)),))))
    assert W.projection_from_json(W.projection_json(A.Projection({"Q": (("ve", "ALL"),)}, {"Q": ("r",)},
                                                                 {"Q": (("a", "s"),)}, {"Q": True}))) == \
        A.Projection({"Q": (("ve", "ALL"),)}, {"Q": ("r",)}, {"Q": (("a", "s"),)}, {"Q": True})


def test_an_unknown_document_has_no_adapter():
    with pytest.raises(ValueError, match="no adapter"):
        A.project("eligibility", {"comparison": [], "items": {}})
