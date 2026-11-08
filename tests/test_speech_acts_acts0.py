"""CI-5: `speech-acts@0` with `acts@0`, simple acts only (commands-imperatives 9), through the service and the saved A/B."""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import pytest

from test_speech_acts_lean import F0, U, answer, certificate, command, elaborate, polar, run1, unit
from tests import lean_routes
from ve import Environment
from ve.english import EnglishVocabulary
from ve.english_grammar import export
from ve.profiles import BY_NAME
from ve.wire import digest

ROOT = Path(__file__).resolve().parents[1]
AB = json.loads((ROOT / "docs/commands-imperatives/ci-5/AB.json").read_text())
ACTS = ["acts@0", "norms@0", "relational-fol@0", "speech-acts@0"]


def test_the_spec_names_the_speech_profile_gate_and_points_other_claims_to_it():
    """The route's documented profile list follows the CI-5 gate, including its simple-act limit."""
    spec = (ROOT / "docs/spec/speech-acts.md").read_text()
    gate = spec.split("### 1.6 Supported combinations", 1)[1].split("\n### ", 1)[0]
    first_paragraph = gate.split("\n\n", 1)[1].split("\n\n", 1)[0]
    admitted = first_paragraph.split("among statement and checker profiles", 1)[0]
    assert set(re.findall(r"`([\w.-]+@\d+)`", admitted)) == set(ACTS)
    assert "optional `acts@0`" in first_paragraph
    assert "simple acts" in first_paragraph
    assert "joined acts outside a declared fixed phrase are" in first_paragraph

    well_formed = spec.split("### 4.1 Well-formedness", 1)[1].split("\n### ", 1)[0]
    diagnostics = spec.split("## 7. Diagnostics", 1)[1].split("\n## ", 1)[0]
    choices = spec.split("## 12. Resolved choices", 1)[1].split("\n## ", 1)[0]
    assert all("allowlist of 1.6" in part for part in (well_formed, diagnostics, choices))
    lean_route_doc = (ROOT / "lean/SPEECH-ACTS.md").read_text()
    assert "allowlist in spec 1.6 (including optional `acts@0` for simple acts)" in lean_route_doc


def with_act(env, predicate, act, fixed):
    """`env` under `acts@0`, with one more unary obligation and the fixed phrases."""
    env = copy.deepcopy(env)
    env["profiles"] = sorted({*env["profiles"], "acts@0"})
    env["vocabulary"]["acts"] = {"fixed": fixed}
    env["vocabulary"]["predicates"][predicate] = {
        "arguments": ["user"], "description": predicate,
        "regulated": {"role": "obligation", "default": "deny", "act": act}}
    return env


def read(env, wording):
    lexicon = export(EnglishVocabulary(Environment(env)))
    [row] = lean_routes.rows("english.command", [{"id": "c", "environment": env, "lexicon": lexicon, "unit": "u1",
                                                  "wording": wording, "queries": []}])
    return row


def certified(env, premises, conclusion, env_id):
    """`certificate` searches the environment without `acts@0`; its meaning ids name the document's whole list."""
    found = certificate({**env, "profiles": [p for p in env["profiles"] if p != "acts@0"]}, premises, conclusion, env_id)
    domain = "ve-meaning-v0.2:" + ",".join(env["profiles"]) + "\n"
    return {**found, "premise_meaning_ids": [digest(domain, {"environment_id": env_id, "ast": a}) for a in premises],
            "conclusion_meaning_id": digest(domain, {"environment_id": env_id, "ast": conclusion})}


@pytest.mark.parametrize("row", [r for r in AB["rows"] if r["class"] == "b1"], ids=lambda r: r["wording"])
def test_each_b1_row_is_its_lean_fixture_and_reads_one_simple_act(row):
    fixtures = (ROOT / "lean/VE/Commands/Examples.lean").read_text()
    assert f'"{row["wording"]}"' in fixtures
    answered = read(row["environment"], row["wording"])["result"]
    assert answered["outcome"] == "one" and answered["reading"]["command"]["args"] == []
    assert answered["reading"]["command"]["act"] == row["head"]["command"]["result"]["reading"]["command"]["act"]
    assert answered["reading"]["command"]["act"] in row["environment"]["vocabulary"]["predicates"]


@pytest.mark.parametrize("row", [r for r in AB["rows"] if r["class"] == "b2"], ids=lambda r: r["name"])
def test_each_b2_row_stays_refused_at_declaration(row):
    assert row["base"]["elaborate"]["error"] == "UnsupportedProfile: speech-acts@0 with acts@0"
    assert row["head"]["elaborate"]["error"] == row["refusal"]
    assert run1({"id": "e", "kind": "speech-elaborate", "environment": row["environment"],
                 "document": {"units": []}})["error"] == row["refusal"]
    assert row["refusal"].startswith("InvalidInput: act phrase for ")


def test_the_gate_admits_acts_and_refuses_the_rest():
    assert elaborate(F0(extra_profiles=["acts@0"]), {"units": []})["status"] == "ok"
    for extra in ("soft-norms@0", "rights@0", "alternatives@0", "time@0", "closure@0"):
        env = F0(extra_profiles=["acts@0", extra])
        assert run1({"id": "e", "kind": "speech-elaborate", "environment": env, "document": {"units": []}})[
            "error"] == f"UnsupportedProfile: speech-acts@0 with {extra}"


def test_the_acts_row_drops_speech_acts_only():
    refused = {name for row in BY_NAME["acts@0"] for name, _ in row["refuses"]}
    assert refused == {"soft-norms@0", "rights@0", "alternatives@0", "closure@0", "order@0", "ve.discourse@1"}
    assert "acts@0" not in {name for row in BY_NAME["speech-acts@0"] for name, _ in row["refuses"]}


def test_the_identity_binds_the_fixed_phrases():
    act = "{0} enter a clarification or restatement"
    one = with_act(F0(), "enter_required", act, ["clarification or restatement"])
    two = with_act(F0(), "enter_required", act, ["clarification or restatement", "the old form"])
    assert elaborate(one, {"units": []})["environment_id"] != elaborate(two, {"units": []})["environment_id"]
    assert elaborate(one, {"units": []})["environment_id"] != elaborate(F0(), {"units": []})["environment_id"]


def test_a_command_elaborates_the_same_rule_and_answers_alike_with_acts_on():
    doc = {"units": [unit("u1", 0, "instruction", command("require", "click_required", ["check"])),
                     unit("u2", 2, "asserted", ["implies", ["binary", "click_required", ["const", "alice"],
                                                            ["const", "check"]], U("reviewed", "atlas")]),
                     unit("u5", 4, "question", polar(U("reviewed", "atlas")))]}
    conclusion = ["and", ["top"], U("reviewed", "atlas")]
    lines = []
    for env in (F0(), F0(extra_profiles=["acts@0"])):
        elaborated = elaborate(env, doc)
        cert = certified(env, elaborated["premises"], conclusion, elaborated["environment_id"])
        lines.append((elaborated["commands"][0]["demand"],
                      answer(env, doc, "u5", answer="yes", evidence={"certificate": cert})["answer"]))
    assert lines[0] == lines[1]
    assert lines[1][1].startswith("supported yes")


def test_a_fixed_phrase_does_not_generalise_over_its_object():
    env = next(r for r in AB["rows"] if r["wording"].startswith("Choose declared"))["environment"]
    assert read(env, "Choose declared kinds of things for the old word.")["result"]["outcome"] == "refused"
