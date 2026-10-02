"""Lean readings route (docs/spec/composition-s1.md 8.4) on inputs in the shapes of the item-1 fixtures (9.2).

The Lean executable decodes the environment and the W2 document, runs the checks of 4.1 with section 7's texts,
regenerates every candidate's document, its source keys and its generated names, and checks each recorded
situation with `separates` (sound by `separates_sound`). Nothing here is decided by Python: the situation ids are
computed as the decoder computes them, and every expectation was derived from the spec. Checked: K1's separation
both ways and its finding, K19's rights candidates under a fixed limitation, K2b's base outside the author's
vocabulary, K5's fixed table under `decisions`, K8's duplicate across sets, K20's unit attached to two sets, K18's
abstention, and delegation of another case kind to the lower route.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from ve.wire import digest
from tests.test_norms import environment, obligation, permission

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean/.lake/build/bin/ve_readings_route"
SOFT_PROFILES = ("norms@0", "readings@1", "relational-fol@0", "soft-norms@0")


@pytest.fixture(scope="module")
def lean():
    if not LEAN.exists():
        lake = shutil.which("lake")
        if lake is None:
            pytest.skip("lake is required for the readings Lean route")
        built = subprocess.run([lake, "build", "ve_readings_route"], cwd=ROOT / "lean", capture_output=True,
                               text=True, timeout=1800)
        assert built.returncode == 0, built.stdout + built.stderr
    return LEAN


def run(executable, cases):
    result = subprocess.run([str(executable), "-"], input=json.dumps(cases), text=True,
                            capture_output=True, timeout=180)
    assert result.returncode in (0, 1), result.stderr
    rows = json.loads(result.stdout)
    assert len(rows) == len(cases)
    return rows


def env_k(profiles=SOFT_PROFILES):
    predicates = {"asks": {"arguments": ["agent", "user"], "description": "{0} asks {1}"},
                  "avoid_required": obligation("deny", None, act="{0} avoid deceiving {1}", args=("agent", "user")),
                  "help_required": obligation("deny", None, act="{0} help {1}", args=("agent", "user"))}
    raw = environment(predicates, sorts=("agent", "user")).to_dict()
    raw["profiles"] = sorted(profiles)
    return raw


def env_rights():
    predicates = {"arrest_permitted": permission("allow", act="{0} arrest {1}", args=("state", "person")),
                  "arbitrary_arrest": {"arguments": ["state", "person"], "description": "base"},
                  "journalist": {"arguments": ["person"], "description": "base"}}
    raw = environment(predicates, sorts=("state", "person")).to_dict()
    raw["profiles"] = sorted({"norms@0", "readings@1", "relational-fol@0", "rights@0", "soft-norms@0"})
    raw["vocabulary"]["rights"] = {"holders": ["person"], "bearers": ["state", "person"]}
    return raw


def norm_object(name, pred, sign, mode="strict", over=(), guard=("top",)):
    body = {"name": name, "predicate": pred, "sign": sign, "guard": list(guard), "unless": [], "over": list(over)}
    if mode == "default":
        body.update({"mode": "default", "exception": {"decided_by": "unstated", "sufficient": [], "necessary": [],
                                                      "factors": []}})
    return body


def norm(*args, **kwargs):
    return {"norm": norm_object(*args, **kwargs)}


def situation_id(raw, entry):
    ident = "v0.2:" + ",".join(raw["profiles"])
    env_id = digest(f"ve-environment-{ident}\n", raw)
    return digest(f"ve-situation-{ident}\n", {"environment_id": env_id, "situation": entry})


def entry(base, witness, probe, value, fixed=(), decisions=()):
    return {"base": base, "fixed": list(fixed), "witness": witness, "decisions": list(decisions),
            "probe": probe, "value": value}


def reading(rid, content, models, kind="norm"):
    return {"id": rid, "kind": kind, "content": content, "meaning_id": "m",
            "admission": {"who": "w", "why": "y", "distinguishing_models": models}}


def reading_set(sid, unit, readings, situations):
    return {"id": sid, "unit": unit, "version": 1, "status": "open", "readings": readings, "situations": situations}


M0 = {"domains": {"agent": ["a"], "user": ["u"]}, "constants": {}, "relations": {"asks": []}}
Q0 = {"outcome": {"predicate": "avoid_required", "tuple": ["a", "u"]}}
EXCEPTED = {"key": {"excepted": "no-deception"}, "tuples": [["a", "u"]]}


def k1_document(raw, *, situation=None, fixed_units=(), extra_sets=()):
    sigma = situation or entry(M0, "default", Q0, False, decisions=[EXCEPTED])
    sid = situation_id(raw, sigma)
    rs1 = reading_set("rs1", "u1", [
        reading("strict", norm("no-deception", "avoid_required", True), {"default": sid}),
        reading("default", norm("no-deception", "avoid_required", True, "default"), {"strict": sid})], {sid: sigma})
    units = [{"id": "u1"}] + [{"id": u, "content": c} for u, c in fixed_units] + \
        [{"id": s["unit"]} for s in extra_sets]
    return {"units": units, "reading_sets": [rs1, *extra_sets]}, sid


def validate(lean, raw, document):
    return run(lean, [{"id": "v", "kind": "readings-validate", "environment": raw, "document": document}])[0]


def test_k1_separation_keys_and_finding(lean):
    raw = env_k()
    document, sid = k1_document(raw)
    row = validate(lean, raw, document)
    assert row["status"] == "ok", row
    [rs1] = row["sets"]
    strict, default = rs1["candidates"]
    assert strict["owned"] == [] and strict["shared"] == []
    assert default["owned"] == [{"key": {"excepted": "no-deception"}, "name": "soft__excepted__no_deception"}]
    assert rs1["findings"] == ["SeparatedByDecisionOnly: rs1: 0, 1"]
    pair = rs1["pairs"][0]["pair"]
    assert pair == {"situation": sid, "witness": "default", "separated": True, "witness_admissible": True,
                    "witness_value": False, "other_admissible": True, "other_value": True}
    separate = run(lean, [{"id": "s", "kind": "readings-separate", "environment": raw, "document": document,
                           "set": "rs1", "situation": sid, "other": "strict"}])[0]
    assert separate["status"] == "ok" and separate["pair"] == pair


def test_k1_strict_witness_does_not_separate(lean):
    raw = env_k()
    document, _ = k1_document(raw, situation=entry(M0, "strict", Q0, True))
    row = validate(lean, raw, document)
    assert row == {"id": "v", "status": "error", "error": "distinguishing model does not separate readings"}


def test_k2b_base_outside_the_author_vocabulary(lean):
    raw = env_k()
    base = {**M0, "relations": {"asks": [], "soft__excepted__no_deception": [["a", "u"]]}}
    sigma = entry(base, "default", Q0, False, decisions=[EXCEPTED])
    document, sid = k1_document(raw, situation=sigma)
    assert validate(lean, raw, document)["error"] == f"InvalidInput: invalid situation {sid}"


def test_k5_shared_table_and_decisions_it_does_not_own(lean):
    raw = env_k()
    be_kind = ("u0", norm("be-kind", "help_required", True, "default"))
    shared = {"key": {"excepted": "be-kind"}, "tuples": [["a", "u"]]}
    document, _ = k1_document(raw, situation=entry(M0, "default", Q0, False, fixed=[shared], decisions=[EXCEPTED]),
                              fixed_units=[be_kind])
    row = validate(lean, raw, document)
    assert row["status"] == "ok", row
    assert row["sets"][0]["candidates"][1]["shared"] == [{"key": {"excepted": "be-kind"},
                                                          "name": "soft__excepted__be_kind"}]
    document, sid = k1_document(raw, situation=entry(M0, "default", Q0, False, decisions=[shared, EXCEPTED]),
                                fixed_units=[be_kind])
    assert validate(lean, raw, document)["error"] == \
        f"InvalidInput: situation {sid} decides excepted be-kind, which reading default does not own"


def test_k8_duplicate_declaration_across_sets(lean):
    raw = env_k()
    rs2 = reading_set("rs2", "u2", [reading("x", norm("no-deception", "help_required", True), {})], {})
    document, _ = k1_document(raw, extra_sets=[rs2])
    assert validate(lean, raw, document)["error"] == "DuplicateDeclaration: no-deception in reading sets rs1 and rs2"


def test_k20_fixed_unit_attached_to_two_sets(lean):
    raw = env_k()
    sigma2 = entry(M0, "default", {"outcome": {"predicate": "help_required", "tuple": ["a", "u"]}}, False,
                   decisions=[{"key": {"excepted": "be-kind"}, "tuples": [["a", "u"]]}])
    sid2 = situation_id(raw, sigma2)
    rs2 = reading_set("rs2", "u2", [
        reading("strict", norm("be-kind", "help_required", True), {"default": sid2}),
        reading("default", norm("be-kind", "help_required", True, "default"), {"strict": sid2})], {sid2: sigma2})
    asks = ["binary", "asks", ["var", 1], ["var", 0]]
    both = ("u3", norm("both-x", "avoid_required", False, over=("no-deception", "be-kind"), guard=asks))
    document, _ = k1_document(raw, fixed_units=[both], extra_sets=[rs2])
    assert validate(lean, raw, document)["error"] == \
        "UnsupportedProfile: readings@1 fixed unit u3 depends on reading sets rs1 and rs2"
    only = ("u3", norm("both-x", "avoid_required", False, over=("no-deception",), guard=asks))
    document, _ = k1_document(raw, fixed_units=[only], extra_sets=[rs2])
    row = validate(lean, raw, document)
    assert row["status"] == "ok", row
    assert [s["set"] for s in row["sets"]] == ["rs1", "rs2"]


def test_k18_norm_defaults_abstention(lean):
    raw = env_k(profiles=("norm-defaults@0", *SOFT_PROFILES))
    document, _ = k1_document(raw)
    assert validate(lean, raw, document)["error"] == \
        "UnsupportedProfile: readings@1 content with norm-defaults@0 is not implemented"


def test_k19_rights_candidates_under_a_fixed_limitation(lean):
    raw = env_rights()
    arbitrary = ["binary", "arbitrary_arrest", ["var", 1], ["var", 0]]

    def claim(mode):
        return {"right": {"name": "r9", "holder": "person", "lines": [
            {"kind": "claim", "norm": norm_object("no-arbitrary-arrest", "arrest_permitted", False, mode,
                                                  guard=arbitrary)}]}}
    base = {"domains": {"state": ["texas"], "person": ["ann", "bob"]}, "constants": {},
            "relations": {"arbitrary_arrest": [["texas", "ann"]], "journalist": []}}
    sigma = entry(base, "default", {"outcome": {"predicate": "arrest_permitted", "tuple": ["texas", "ann"]}}, True,
                  decisions=[{"key": {"excepted": "no-arbitrary-arrest"}, "tuples": [["texas", "ann"]]}])
    sid = situation_id(raw, sigma)
    l29 = {"limitation": {"name": "l29", "scope": "all", "kinds": "all", "decided_by": "unstated", "factors": [],
                          "conditions": [
                              {"name": "determined_by_law", "role": "necessary",
                               "verbalisation": "the limitation is determined by law"},
                              {"name": "solely_for_permitted_purpose", "role": "necessary",
                               "verbalisation": "the limitation is solely for a permitted purpose"}]}}
    rs9 = reading_set("rs9", "u9", [reading("strict", claim("strict"), {"default": sid}, kind="right"),
                                    reading("default", claim("default"), {"strict": sid}, kind="right")],
                      {sid: sigma})
    row = validate(lean, raw, {"units": [{"id": "u9"}, {"id": "u29", "content": l29}], "reading_sets": [rs9]})
    assert row["status"] == "ok", row
    [rs] = row["sets"]
    strict, default = rs["candidates"]
    assert [k["key"] for k in strict["shared"]] == [
        {"lim": "l29", "act": "arrest_permitted"},
        {"cond": "l29", "act": "arrest_permitted", "condition": "determined_by_law"},
        {"cond": "l29", "act": "arrest_permitted", "condition": "solely_for_permitted_purpose"}]
    assert strict["owned"] == [] and strict["findings"] == []
    assert default["findings"] == ["UnlicensedLimitation: exception of rule no-arbitrary-arrest on right r9"
                                   " under rs9@1:1"]
    assert rs["findings"] == ["SeparatedByDecisionOnly: rs9: 0, 1"]
    assert rs["pairs"][0]["pair"]["separated"] is True


def test_other_kinds_go_to_the_lower_route(lean):
    raw = env_k()
    row = run(lean, [{"id": "e", "kind": "soft-elaborate", "environment": raw,
                      "norms": [norm("no-deception", "avoid_required", True, "default")]}])[0]
    assert row["status"] == "ok", row
