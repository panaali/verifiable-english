"""Lean-first batch 10b: the fuzzer gate accepts only the retired DF-19 difference (build checklist 13),
and the recorded evidence shows no unexplained difference over the fourteen date seeds (build checklist 20)."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
B10B = ROOT / "docs/lean-first/b10b"
DF19 = "fields do not match: expected [sort, description], got [description, sort, verbalisation]"


def _load(name):
    spec = importlib.util.spec_from_file_location(f"lean_first_b10b_{name}", B10B / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _gate():
    return _load("fuzzer_gate")


def test_delta_evidence_table_is_generated_from_the_evidence():
    report = _load("verify_report")
    text = (B10B / "DELTA.md").read_text()
    assert report.BEGIN in text and report.END in text
    assert text.split(report.BEGIN, 1)[1].split(report.END, 1)[0].strip("\n") == report.render().strip("\n")


def test_every_seeded_bug_was_caught():
    bugs = json.loads((B10B / "evidence/seeded-bugs.json").read_text())["mutants"]
    assert len(bugs) >= 3
    assert all(bug["mutated_exit"] != 0 and bug["restored_exit"] == 0 for bug in bugs)
    assert all((ROOT / bug["test"].split("::")[0]).exists() for bug in bugs)


def _finding(signature, classes):
    return {"signature": signature, "surface": "environment", "profile": "norm-defaults", "classes": classes,
            "answers": {}}


def _run(lean, replay_status="reproduces", new=()):
    python = {"outcome": "ok", "value": None}
    answers = {"python": python, "lean": lean, "rust": {"outcome": "n/a"}}
    return {"corpus": {"environment": {"norm-defaults": 1}}, "mutants": {"environment": {"zero-fault": 1}},
            "new": list(new),
            "items": {"sampled": {"environment": [
                          {"input": "same", "answers_sha256": json.dumps(answers, sort_keys=True),
                           "profile": "norm-defaults", "answers": answers}]},
                      "replayed": [{"id": "environment-d253e2ea451c5fa3", "input": "entry",
                                    "status": replay_status, "answers_sha256": replay_status}],
                      "new": {f["signature"]: "same" for f in new}}}


BASE = _run({"outcome": "error", "code": "InvalidInput", "text": DF19})
HEAD = _run({"outcome": "ok", "value": None}, replay_status="fixed")


def test_the_retired_df19_difference_is_explained():
    result = _gate().compare(BASE, HEAD)
    assert result["unexplained"] == [] and len(result["explained"]) == 2
    assert _gate().compare(BASE, copy.deepcopy(BASE)) == {"explained": [], "unexplained": []}


@pytest.mark.parametrize("answer", [
    {"outcome": "error", "code": "ResourceLimit", "text": "ResourceLimit: arbitrary"},
    {"outcome": "error", "code": "InvalidInput", "text": "InvalidInput: another fault"},
    {"outcome": "ok", "value": {"wrong": True}},
])
def test_df19_rejection_does_not_explain_an_unrelated_lean_answer(answer):
    head = _run(answer, replay_status="fixed")
    assert _gate().compare(BASE, head)["unexplained"]


@pytest.mark.parametrize("mutate", [
    # Python's answer changed too: not a Lean-only decoder fix.
    lambda head: head["items"]["sampled"]["environment"][0]["answers"].update(python={"outcome": "error"}),
    # A changed answer with no recorded answers (not a norm-defaults input).
    lambda head: head["items"]["sampled"]["environment"][0].pop("answers"),
    # A different sampled input.
    lambda head: head["items"]["sampled"]["environment"][0].update(input="other"),
    # A replayed entry that is not retired changed.
    lambda head: head["items"]["replayed"][0].update(id="environment-other"),
    # A head-only finding on an input DF-19 did not mask.
    lambda head: (head["new"].append(_finding("grown", ["diagnostic"])), head["items"]["new"].update(grown="other")),
    # A head-only finding DF-19 masked, but of the outcome class: not a wording or order difference.
    lambda head: (head["new"].append(_finding("grown", ["outcome"])), head["items"]["new"].update(grown="same")),
    # The sample itself changed size.
    lambda head: head["mutants"]["environment"].update({"one-fault": 1}),
])
def test_any_other_difference_fails_the_gate(mutate):
    head = copy.deepcopy(HEAD)
    mutate(head)
    for row in head["items"]["sampled"]["environment"]:
        row["answers_sha256"] = json.dumps(row.get("answers"), sort_keys=True) + row["input"]
    assert _gate().compare(BASE, head)["unexplained"]


def test_an_unmasked_diagnostic_finding_is_listed():
    head = _run(HEAD["items"]["sampled"]["environment"][0]["answers"]["lean"], replay_status="fixed",
                new=[_finding("unmasked", ["diagnostic"])])
    result = _gate().compare(BASE, head)
    assert result["unexplained"] == []
    assert [row.get("unmasked") for row in result["explained"]] == [None, None, "unmasked"]


def test_a_base_answer_other_than_df19_is_not_explained():
    base = _run({"outcome": "error", "code": "InvalidInput", "text": "something else"})
    assert _gate().compare(base, HEAD)["unexplained"]


def test_a_repeated_profile_is_explained_only_with_pythons_own_text():
    gate = _gate()
    refused = {"outcome": "error", "code": "UnsupportedProfile", "text": gate.REPEATED}

    def pair(head_lean, python_text):
        base, head = _run({"outcome": "ok", "value": None}), _run(head_lean, replay_status="fixed")
        for run in (base, head):
            row = run["items"]["sampled"]["environment"][0]
            row["answers"]["python"] = {"outcome": "error", "code": "UnsupportedProfile", "text": python_text}
            row["answers_sha256"] = json.dumps(row["answers"], sort_keys=True)
        return gate.compare(base, head)

    result = pair(refused, gate.REPEATED)
    assert result["unexplained"] == [] and result["explained"][0]["kind"] == "repeated-profile"
    assert pair(refused, "UnsupportedProfile: something else")["unexplained"]
    assert pair({**refused, "text": "UnsupportedProfile: other"}, gate.REPEATED)["unexplained"]


def test_fourteen_date_seeds_have_no_unexplained_difference():
    evidence = json.loads((B10B / "evidence/fuzzer-seeds.json").read_text())
    gate = _gate()
    assert evidence["base_commit"].startswith("7345e3ed")
    assert evidence["retired"] == sorted(gate.RETIRED)
    assert [row["seed"] for row in evidence["seeds"]] == list(gate.SEEDS)
    assert all(row["unexplained"] == [] for row in evidence["seeds"])
    assert all(row["base_not_reproduced"] == [] and row["head_not_reproduced"] == sorted(gate.RETIRED)
               for row in evidence["seeds"])
    assert all(sum(sum(counts.values()) for counts in row["mutants"].values()) > 25000
               for row in evidence["seeds"])
    for row in evidence["seeds"]:
        replays = [e for e in row["explained"] if "replayed" in e]
        assert [e["replayed"] for e in replays] == sorted(gate.RETIRED)
        sampled = [e for e in row["explained"] if "index" in e]
        assert {e["kind"] for e in sampled} <= {"df19", "repeated-profile"}
        assert any(e["kind"] == "df19" for e in sampled)
        assert all(e["base_lean"]["text"].startswith(gate.DF19) for e in sampled if e["kind"] == "df19")
        assert all(e["head_lean"]["text"] == gate.REPEATED and e["head_lean_agrees_with_python"]
                   for e in sampled if e["kind"] == "repeated-profile")
        unmasked = [e for e in row["explained"] if "unmasked" in e]
        assert all(e["classes"] == ["diagnostic"] for e in unmasked)
        assert row["head_new"] == row["base_new"] + len(unmasked) - row["base_only_new"]
