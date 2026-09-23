"""ve assist: session, anchoring, checks, status, ledger, API, proposer, suggestions, CLI."""
import json
from pathlib import Path

import pytest

from ve.assist import (AssistSession, LedgerReplayError, call_tool, select_p5_item, source_from_p5,
                       source_from_text, tool_schemas)
from ve.assist.cli import main as cli_main
from ve.assist.ground import ground_countermodel
from ve.environment import Environment, LANGUAGE, PROFILE, SPEC_REVISION
from ve.parser import parse

ROOT = Path(__file__).resolve().parents[1]

ENV = {"language": LANGUAGE, "profile": PROFILE, "spec_revision": SPEC_REVISION, "vocabulary": {
    "sorts": {"service": {"description": "A service in the inventory."}},
    "predicates": {
        "deployed": {"arguments": ["service"], "description": "Recorded as deployed."},
        "reviewed": {"arguments": ["service"], "description": "Recorded as reviewed."},
        "safe": {"arguments": ["service"], "description": "Recorded as safe."}},
    "constants": {"api": {"sort": "service", "description": "The public API."},
                  "web": {"sort": "service", "description": "The web front end."}}}}

TEXT = """[given] Every reviewed service is safe. The API is reviewed.

[claimed] So the API is safe.

[context] This paragraph is commentary."""

P5_ITEM = {"id": "demo", "payload": {
    "id": "demo", "root": "n02",
    "glossary": [{"term": "ready", "sense": "ready: packing completed (R01)"},
                 {"term": "ready", "sense": "ready: staffing arranged (R02)"},
                 {"term": "sealed", "sense": "sealed: seal applied (R03)"}],
    "premises": [{"id": "n00", "text": "unit1 is sealed. Rules r01 are declared."}],
    "records": [{"id": "r01", "text": "If unit1 is sealed, then unit2 is ready (packing completed)."}],
    "nodes": [{"id": "n02", "parents": ["n00"], "text": "Because unit1 is sealed, unit2 is ready."}],
    "argument": "[n02] Because unit1 is sealed, unit2 is ready."}}


def new_session(**options):
    source = source_from_text(TEXT)
    return AssistSession.create(ENV, source, [{"id": "t_main", "sentence": "p2.1"}], options=options)


def build_success(session):
    ok = lambda r: (r["ok"] or pytest.fail(json.dumps(r))) and r
    ok(session.apply("freeze_target", {"target": "t_main", "text": "@api is safe."}))
    ok(session.apply("add_node", {"name": "rule", "anchors": ["p1.1"],
                                  "text": "for every service s, (if (s is reviewed), then (s is safe))."}))
    ok(session.apply("add_node", {"name": "fact", "text": "@api is reviewed", "anchors": ["p1.2"]}))
    ok(session.apply("add_node", {"name": "goal", "text": "@api is safe.", "anchors": ["p2.1"],
                                  "parents": ["rule", "fact"]}))
    return ok(session.apply("check_step", {"name": "goal"}))


# ---------------------------------------------------------------- sources

def test_text_source_roles_and_sentence_ids():
    source = source_from_text(TEXT)
    rows = {s["id"]: s for s in source["sentences"]}
    assert list(rows) == ["p1.1", "p1.2", "p2.1", "p3.1"]
    assert rows["p1.1"]["role"] == "given" and rows["p2.1"]["role"] == "claimed"
    assert rows["p3.1"]["asserting"] is False


def test_p5_loader_names_senses_and_freezes_nothing():
    built = source_from_p5(P5_ITEM)
    env = Environment(built["environment"])
    assert {"ready_packing_completed", "ready_staffing_arranged", "sealed"} <= set(env.predicates)
    assert env.predicates["sealed"].description == "sealed: seal applied (R03)"
    assert built["targets"] == [{"id": "t_n02", "sentence": "n02.1"}]
    roles = {s["id"]: s["role"] for s in built["source"]["sentences"]}
    assert roles == {"n00.1": "given", "n00.2": "given", "r01.1": "given", "n02.1": "claimed"}
    assert built["metadata"]["p5_paragraph_parents"] == {"n02": ["n00"]}


def test_p5_real_dev_file_loads_when_present():
    path = Path("/Users/seyran/code/ve-codex/experiments/P5-shifting-definitions/materials/dev.jsonl.gz")
    if not path.exists():
        pytest.skip("P5 materials not available")
    built = source_from_p5(select_p5_item(path, 0))
    session = AssistSession.create(built["environment"], built["source"], built["targets"])
    assert session.targets["t_n14"]["sentence"] == "n14.1"


# ---------------------------------------------------------------- core actions

def test_targets_must_be_frozen_first_and_are_immutable():
    s = new_session()
    r = s.apply("add_node", {"name": "fact", "text": "@api is reviewed.", "anchors": ["p1.2"]})
    assert not r["ok"] and "Freeze every target" in r["error"]["message"]
    assert s.apply("freeze_target", {"target": "t_main", "text": "@api is safe."})["ok"]
    again = s.apply("freeze_target", {"target": "t_main", "text": "@web is safe."})
    assert not again["ok"] and "already frozen" in again["error"]["message"]
    assert len(s.events) == 3  # rejected actions are logged too


def test_step_follows_with_replayed_certificate_and_success():
    s = new_session()
    result = build_success(s)
    assert result["status"] == "follows" and len(result["certificate_digest"]) == 64
    status = s.apply("status")
    assert status["success"] is True, status["failures"]
    assert status["targets"][0]["certified"] and status["targets"][0]["replay"] == "Checked"
    assert status["coverage"]["uncovered"] == [] and status["provenance"]["hand-written"] == 3


def test_every_node_has_a_deterministic_paraphrase():
    s = new_session()
    build_success(s)
    views = s.apply("show")["nodes"]
    assert [v["paraphrase"] for v in views] == [
        "Every service that is reviewed is safe.", "Api is reviewed.", "Api is safe."]


def test_countermodel_is_checked_and_readable():
    s = new_session()
    s.apply("freeze_target", {"target": "t_main", "text": "@api is safe."})
    s.apply("add_node", {"name": "fact", "text": "@api is reviewed.", "anchors": ["p1.2"]})
    s.apply("add_node", {"name": "goal", "text": "@api is safe.", "anchors": ["p2.1"], "parents": ["fact"]})
    result = s.apply("check_step", {"name": "goal"})
    assert result["status"] == "countermodel"
    assert "api is reviewed" in result["countermodel"]["true"]
    assert "api is safe" in result["countermodel"]["false"]
    assert "premise_suggestions" not in result
    status = s.apply("status")
    assert not status["success"] and status["unproved_steps"][0]["node"] == "goal"


def test_rewrite_invalidates_checks_and_tracks_history():
    s = new_session()
    build_success(s)
    r = s.apply("rewrite", {"name": "fact", "text": "@web is reviewed."})
    assert r["invalidated_checks"] == ["fact", "goal"]
    assert s.apply("show", {"name": "fact"})["node"]["history"][0]["text"] == "@api is reviewed."
    assert s.apply("status")["unproved_steps"][0]["check"] == "unchecked"
    assert not s.apply("rewrite", {"name": "rule", "parents": ["goal"]})["ok"]  # cycle


def test_unanchored_load_bearing_assumption_fails_item():
    s = new_session()
    s.apply("freeze_target", {"target": "t_main", "text": "@api is safe."})
    s.apply("add_node", {"name": "fact", "text": "@api is reviewed.", "anchors": ["p1.2"]})
    # A bridge the prose never states, anchored to nothing:
    s.apply("add_node", {"name": "bridge", "text": "if (@api is reviewed), then (@api is safe)."})
    s.apply("add_node", {"name": "goal", "text": "@api is safe.", "anchors": ["p2.1"],
                         "parents": ["fact", "bridge"]})
    assert s.apply("check_step", {"name": "goal"})["status"] == "follows"
    s.apply("waive", {"sentence": "p1.1", "reason": "covered by bridge for the demo"})
    status = s.apply("status")
    row = status["unanchored_assumptions"][0]
    assert row["node"] == "bridge" and row["load_bearing"] and row["needed_by"] == ["goal"]
    assert not status["success"] and any("load-bearing" in f for f in status["failures"])


def test_assumption_anchored_to_claimed_sentence_is_not_anchored():
    s = new_session()
    s.apply("freeze_target", {"target": "t_main", "text": "@api is safe."})
    s.apply("add_node", {"name": "cheat", "text": "@api is safe.", "anchors": ["p2.1"]})
    s.apply("add_node", {"name": "goal", "text": "@api is safe.", "anchors": ["p2.1"], "parents": ["cheat"]})
    s.apply("check_step", {"name": "goal"})
    row = s.apply("status")["unanchored_assumptions"][0]
    assert row["anchor_state"] == "anchored_to_claim_only" and row["load_bearing"]


def test_idle_unanchored_assumption_is_reported_not_failing():
    s = new_session()
    build_success(s)
    s.apply("add_node", {"name": "extra", "text": "@web is deployed."})
    status = s.apply("status")
    assert status["unanchored_assumptions"][0]["load_bearing"] is False
    assert status["success"]


def test_waivers_and_coverage():
    s = new_session()
    s.apply("freeze_target", {"target": "t_main", "text": "@api is safe."})
    assert not s.apply("waive", {"sentence": "p2.1", "reason": "no"})["ok"]  # target sentence
    assert not s.apply("waive", {"sentence": "p1.1", "reason": ""})["ok"]
    s.apply("waive", {"sentence": "p1.1", "reason": "restated elsewhere"})
    cov = s.apply("status")["coverage"]
    assert cov["waived"] == 1 and cov["uncovered"] == ["p1.2", "p2.1"]


def test_declare_requires_gloss_and_gates_near_duplicates():
    s = new_session()
    s.apply("freeze_target", {"target": "t_main", "text": "@api is safe."})
    assert not s.apply("declare", {"name": "audited", "gloss": "", "arguments": ["service"]})["ok"]
    assert not s.apply("declare", {"name": "audited", "gloss": "audited", "arguments": ["service"]})["ok"]
    blocked = s.apply("declare", {"name": "reviewed_twice", "gloss": "Reviewed by two people.",
                                  "arguments": ["service"]})
    assert not blocked["ok"] and "reviewed" in blocked["error"]["message"]
    ok = s.apply("declare", {"name": "reviewed_twice", "gloss": "Reviewed by two people.",
                             "arguments": ["service"], "acknowledge": ["reviewed"]})
    assert ok["ok"] and "reviewed_twice" in s.env.predicates


def test_declare_flags_renamed_conclusion_lexically_and_semantically():
    s = new_session()
    s.apply("freeze_target", {"target": "t_main", "text": "@api is safe."})
    blocked = s.apply("declare", {"name": "so_safe", "gloss": "So the API is safe.", "arguments": ["service"]})
    assert not blocked["ok"] and "conclusion:t_main" in blocked["error"]["message"]
    assert s.apply("declare", {"name": "so_safe", "gloss": "So the API is safe.", "arguments": ["service"],
                               "acknowledge": ["conclusion:t_main", "safe"]})["ok"]
    s.apply("add_node", {"name": "carrier", "anchors": ["p1.1"],
                         "text": "(@api is so_safe) and (if (@api is so_safe), then (@api is safe))."})
    s.apply("add_node", {"name": "goal", "text": "@api is safe.", "anchors": ["p2.1"], "parents": ["carrier"]})
    s.apply("check_step", {"name": "goal"})
    status = s.apply("status")
    assert status["renamed_conclusions"] == [{"target": "t_main", "assumptions": ["carrier"]}]
    assert not status["success"]


def test_declare_rechecks_existing_certificates():
    s = new_session()
    build_success(s)
    r = s.apply("declare", {"name": "gamma", "gloss": "An unrelated marker for testing.",
                            "arguments": ["service"]})
    assert r["ok"] and r["rechecked"] == ["goal"]
    assert s.apply("status")["success"]


# ---------------------------------------------------------------- ledger

def test_ledger_replays_and_detects_tampering():
    s = new_session()
    build_success(s)
    s.apply("status")
    ledger = json.loads(json.dumps(s.to_ledger()))
    replayed = AssistSession.from_ledger(ledger)
    assert len(replayed.events) == len(s.events)
    assert replayed.apply("status")["success"]
    ledger["events"][3]["args"]["text"] = "@web is reviewed."
    with pytest.raises(LedgerReplayError):
        AssistSession.from_ledger(ledger)


def test_ledger_usage_counts_actions_and_tokens():
    s = new_session()
    build_success(s)
    s.apply("record_usage", {"role": "author", "input_tokens": 100, "output_tokens": 20})
    usage = s.usage()
    assert usage["tokens"]["author"] == {"input_tokens": 100, "output_tokens": 20, "calls": 1}
    assert usage["actions"]["add_node"] == 3 and usage["tool_result_chars"] > 0


# ---------------------------------------------------------------- API

def test_tool_schemas_per_arm():
    base = {t["name"] for t in tool_schemas()}
    assert "propose" not in base and "accept" not in base and "record_usage" not in base
    check = next(t for t in tool_schemas() if t["name"] == "check_step")
    assert "suggest_premises" not in check["input_schema"]["properties"]
    full = {t["name"] for t in tool_schemas(proposer=True)}
    assert {"propose", "accept"} <= full
    check = next(t for t in tool_schemas(premise_suggestions=True) if t["name"] == "check_step")
    assert "suggest_premises" in check["input_schema"]["properties"]


def test_call_tool_logs_rejections_and_replays():
    s = new_session()
    assert call_tool(s, "propose", {"sentence": "p1.1"})["error"]["code"] == "UnknownTool"
    assert call_tool(s, "status", {"verbose": True})["error"]["code"] == "InvalidArguments"
    assert call_tool(s, "freeze_target", '{"target": "t_main", "text": "@api is safe."}')["ok"]
    assert len(s.events) == 3 and s.events[0]["rejected_by_api"]
    assert len(AssistSession.from_ledger(json.loads(json.dumps(s.to_ledger()))).events) == 3


# ---------------------------------------------------------------- premise suggestions (off by default)

def test_premise_suggestions_are_off_by_default():
    s = new_session()
    s.apply("freeze_target", {"target": "t_main", "text": "@api is safe."})
    s.apply("add_node", {"name": "fact", "text": "@api is reviewed.", "anchors": ["p1.2"]})
    s.apply("add_node", {"name": "goal", "text": "@api is safe.", "parents": ["fact"]})
    r = s.apply("check_step", {"name": "goal", "suggest_premises": True})
    assert not r["ok"] and "disabled" in r["error"]["message"]


def test_premise_suggestions_when_enabled_are_labelled_and_logged():
    s = new_session(premise_suggestions=True)
    s.apply("freeze_target", {"target": "t_main", "text": "@api is safe."})
    s.apply("add_node", {"name": "rule", "anchors": ["p1.1"],
                         "text": "for every service s, (if (s is reviewed), then (s is safe))."})
    s.apply("add_node", {"name": "fact", "text": "@api is reviewed.", "anchors": ["p1.2"]})
    s.apply("add_node", {"name": "goal", "text": "@api is safe.", "anchors": ["p2.1"], "parents": ["fact"]})
    r = s.apply("check_step", {"name": "goal", "suggest_premises": True})
    kinds = [x["kind"] for x in r["premise_suggestions"]]
    assert kinds == ["use_existing_node", "bridge"]
    assert r["premise_suggestions"][0]["node"] == "rule"
    bridge = r["premise_suggestions"][1]
    assert "assumes the step" in bridge["risk"]
    s.apply("add_node", {"name": "br", "suggestion": bridge["id"]})
    assert s.nodes["br"].origin == "suggestion-verbatim"
    assert AssistSession.from_ledger(json.loads(json.dumps(s.to_ledger())))


# ---------------------------------------------------------------- proposer (fake backend)

class FakeProposer:
    def __init__(self, replies):
        self.replies, self.calls = list(replies), []

    def __call__(self, system, prompt, item):
        self.calls.append((system, prompt, item))
        return {"text": self.replies.pop(0), "input_tokens": 1000, "output_tokens": 50,
                "model": "fake-haiku", "account_label": "test"}


def test_propose_parses_dedupes_drops_and_distinguishes():
    s = new_session()
    s.apply("freeze_target", {"target": "t_main", "text": "@api is safe."})
    s.proposer = FakeProposer(['```json\n{"candidates": ['
                               '{"ve": "@api is reviewed.", "reading": "the API"},'
                               '{"ve": "@api is reviewed", "reading": "duplicate"},'
                               '{"ve": "@api is audited.", "reading": "unknown symbol"},'
                               '{"ve": "for every service s, (s is reviewed).", "reading": "all"}]}\n```'])
    r = s.apply("propose", {"sentence": "p1.2"})
    assert r["ok"] and [c["id"] for c in r["candidates"]] == ["q1.1", "q1.2"]
    assert r["candidates"][0]["paraphrase"] == "Api is reviewed."
    assert r["dropped"][0]["error"]["code"] == "UnknownSymbol"
    comparison = r["comparisons"][0]
    assert comparison["relation"] == "b_stronger"
    assert comparison["distinguishing_models"][0]["kind"] == "a_true_b_false"
    assert s.events[-1]["tokens"]["proposer"] == {"input_tokens": 1000, "output_tokens": 50, "calls": 1}
    assert "Sentence to formalise:\nThe API is reviewed." in s.proposer.calls[0][1]
    # Acceptance is explicit and provenance-marked.
    s.apply("accept", {"candidate": "q1.1", "name": "fact", "anchors": ["p1.2"]})
    s.apply("add_node", {"name": "fact2", "candidate": "q1.2", "text": "@web is reviewed."})
    assert s.nodes["fact"].origin == "proposer-verbatim"
    assert s.nodes["fact2"].origin == "proposer-edited"
    s.apply("rewrite", {"name": "fact", "text": "@web is reviewed."})
    assert s.nodes["fact"].origin == "proposer-edited"
    # Replay reuses recorded model output; no backend is needed.
    replayed = AssistSession.from_ledger(json.loads(json.dumps(s.to_ledger())))
    assert replayed.proposer is None and replayed.nodes["fact2"].origin == "proposer-edited"


def test_propose_repairs_once_then_gives_up():
    s = new_session(propose_repair_rounds=1)
    s.apply("freeze_target", {"target": "t_main", "text": "@api is safe."})
    s.proposer = FakeProposer(['{"candidates": [{"ve": "@api is audited."}]}',
                               '{"candidates": [{"ve": "@api is reviewed."}]}'])
    r = s.apply("propose", {"sentence": "p1.2", "k": 1})
    assert [c["text"] for c in r["candidates"]] == ["@api is reviewed."]
    assert "None of those candidates parsed" in s.proposer.calls[1][1]
    assert s.events[-1]["tokens"]["proposer"]["calls"] == 2


def test_propose_without_backend_is_an_error():
    s = new_session()
    r = s.apply("propose", {"sentence": "p1.2"})
    assert not r["ok"] and "No proposer" in r["error"]["message"]


# ---------------------------------------------------------------- ground search and closure induction

def test_ground_countermodel_finds_models_and_reports_validity():
    env = Environment(ENV)
    f = lambda t: parse(env, t + "\n").formulas[0]
    status, model = ground_countermodel(env, [f("(@api is reviewed) or (@web is reviewed).")], f("@api is reviewed."))
    assert status == "Found" and model.relations["reviewed"] == frozenset({("e1",)})
    assert ground_countermodel(env, [f("@api is reviewed.")], f("(@api is reviewed) or (@web is safe)."))[0] == "NotFound"
    assert ground_countermodel(env, [], f("for every service s, (s is safe)."))[0] == "Unsupported"


def test_closure_induction_invariant_is_passed_to_the_prover():
    from conformance.closure_certificates import environment
    from ve import And, Forall, Implies, Named, Reach, Unary, Var
    from ve.closure import induction_step
    from ve.printer import print_formula
    raw = environment().to_dict()
    raw["vocabulary"]["constants"] = {}
    env = Environment(raw)
    p, edge = Unary("p", Var(0)), Named("rel")
    goal = Forall("item", Implies(And(p, induction_step("item", edge, p)),
                                  Forall("item", Implies(Reach("plus", edge, Var(1), Var(0)), p))))
    source = {"sentences": [{"id": "s1", "text": "Closure preserves p.", "role": "claimed"}]}
    s = AssistSession.create(env, source, [{"id": "t", "sentence": "s1"}])
    text = print_formula(env, goal) + "."
    s.apply("freeze_target", {"target": "t", "text": text})
    s.apply("add_node", {"name": "top", "text": "true."})
    s.apply("add_node", {"name": "goal", "text": text, "anchors": ["s1"], "parents": ["top"]})
    r = s.apply("check_step", {"name": "goal", "invariants": ["for every item x, (x is p)."]})
    assert r["status"] == "follows", r


# ---------------------------------------------------------------- CLI

def run_cli(capsys, *argv):
    code = cli_main([str(a) for a in argv])
    out = capsys.readouterr()
    return code, out.out + out.err


def test_cli_worked_example(tmp_path, capsys):
    env = tmp_path / "env.json"
    env.write_text(json.dumps(ENV))
    text = tmp_path / "arg.txt"
    text.write_text(TEXT)
    session = tmp_path / "s.json"
    code, out = run_cli(capsys, "new", session, "--env", env, "--text", text, "--target", "p2.1")
    assert code == 0 and "t_p2_1 -> p2.1" in out
    assert run_cli(capsys, "freeze", session, "t_p2_1", "@api is safe.")[0] == 0
    run_cli(capsys, "add", session, "rule", "for every service s, (if (s is reviewed), then (s is safe)).",
            "--anchor", "p1.1")
    run_cli(capsys, "add", session, "fact", "@api is reviewed.", "--anchor", "p1.2")
    code, out = run_cli(capsys, "add", session, "goal", "@api is safe.", "--anchor", "p2.1",
                        "--parent", "rule", "--parent", "fact")
    assert "says: Api is safe." in out
    code, out = run_cli(capsys, "check", session, "goal")
    assert code == 0 and "FOLLOWS" in out
    code, out = run_cli(capsys, "status", session)
    assert out.startswith("SUCCESS")
    code, out = run_cli(capsys, "replay", session)
    assert "reproduce" in out
    code, out = run_cli(capsys, "call", session, "check_step", '{"name": "rule"}')
    assert code == 2 and "assumption" in out
    code, out = run_cli(capsys, "new", session, "--env", env, "--text", text, "--target", "p2.1")
    assert code == 2 and "never overwritten" in out


def test_python_m_ve_dispatches_assist(capsys):
    from ve.__main__ import main
    assert main(["assist", "tools"]) == 0
    assert "check_step" in capsys.readouterr().out


def test_redundant_parentheses_from_the_proposer_are_normalised_and_flagged():
    from ve.assist.proposer import strip_redundant_parentheses
    raw = ("if (((@api is reviewed) and ((@web is reviewed) and (@web is safe)))), "
           "then (((@api is safe) and ((@api is deployed) and (@web is deployed)))).")
    fixed = strip_redundant_parentheses(raw)
    assert fixed == ("if ((@api is reviewed) and ((@web is reviewed) and (@web is safe))), "
                     "then ((@api is safe) and ((@api is deployed) and (@web is deployed))).")
    assert strip_redundant_parentheses("(@api is safe).") == "@api is safe."
    assert strip_redundant_parentheses("@api is (safe.") == "@api is (safe."
    s = new_session()
    s.apply("freeze_target", {"target": "t_main", "text": "@api is safe."})
    s.proposer = FakeProposer([json.dumps({"candidates": [{"ve": raw, "reading": "x"}]})])
    r = s.apply("propose", {"sentence": "p1.1"})
    assert r["candidates"][0]["repaired"] == "redundant parentheses removed"
    assert r["candidates"][0]["text"] == fixed


def test_haiku_backend_configuration_without_calling_a_model(tmp_path, monkeypatch):
    from ve_experiments.assist_haiku import ClaudeProposer, HaikuProposer
    from ve_experiments.claude_cli import MODELS, command, isolated_env
    monkeypatch.delenv("VE_ASSIST_CLAUDE_ACCOUNT", raising=False)
    monkeypatch.delenv("VE_CLAUDE_ACCOUNT_CONFIG_DIR", raising=False)
    proposer = HaikuProposer(tmp_path / "calls.jsonl", max_calls=10)
    client = proposer.client
    assert HaikuProposer is ClaudeProposer and proposer.model == "haiku"
    assert client.account_label == "lead-main"  # no personal default account
    assert client.controls.model == MODELS["haiku"] and client.max_calls == 10
    argv = command("claude", client.controls, "sys", tmp_path / "mcp.json")
    assert "--effort" not in argv and argv[argv.index("--model") + 1] == "claude-haiku-4-5-20251001"
    env = isolated_env({"PATH": "/bin"}, tmp_path, tmp_path, "token", client.controls)
    assert env["CLAUDE_CODE_NO_MODEL_FALLBACK"] == "1" and "MAX_THINKING_TOKENS" not in env


def test_invalid_arguments_are_rejected_and_logged():
    s = new_session()
    r = s.apply("freeze_target", {"target": "t_main", "txt": "@api is safe."})
    assert r["error"]["code"] == "AssistError" and "Invalid arguments" in r["error"]["message"]
    assert len(s.events) == 1


# ---------------------------------------------------------------- regression tests: code review loopholes

def _status_after(s, goal="goal"):
    assert s.apply("check_step", {"name": goal})["status"] == "follows"
    return s.apply("status")


def test_review1_duplicate_unanchored_assumptions_cannot_hide_each_other():
    s = new_session()
    s.apply("freeze_target", {"target": "t_main", "text": "@api is safe."})
    s.apply("add_node", {"name": "fact", "text": "@api is reviewed.", "anchors": ["p1.2"]})
    for name in ("bridge1", "bridge2"):
        s.apply("add_node", {"name": name, "text": "if (@api is reviewed), then (@api is safe)."})
    s.apply("add_node", {"name": "goal", "text": "@api is safe.", "anchors": ["p2.1"],
                         "parents": ["fact", "bridge1", "bridge2"]})
    s.apply("waive", {"sentence": "p1.1", "reason": "restated by the bridges"})
    status = _status_after(s)
    rows = {r["node"]: r for r in status["unanchored_assumptions"]}
    assert rows["bridge1"]["load_bearing"] and rows["bridge2"]["load_bearing"]
    assert not status["success"]


def test_review2_claimed_anchor_plus_given_anchor_is_claim_only():
    s = new_session()
    s.apply("freeze_target", {"target": "t_main", "text": "@api is safe."})
    s.apply("add_node", {"name": "fact", "text": "@api is reviewed.", "anchors": ["p1.2"]})
    s.apply("add_node", {"name": "cheat", "text": "@api is safe.", "anchors": ["p2.1", "p1.1"]})
    s.apply("add_node", {"name": "goal", "text": "@api is safe.", "anchors": ["p2.1"], "parents": ["fact", "cheat"]})
    status = _status_after(s)
    row = status["unanchored_assumptions"][0]
    assert row["node"] == "cheat" and row["anchor_state"] == "anchored_to_claim_only" and row["load_bearing"]
    assert not status["success"] and "assumption cheat alone entails target t_main" in status["failures"]


def test_review2_given_anchored_assumption_that_alone_implies_target_is_flagged():
    s = new_session()
    s.apply("freeze_target", {"target": "t_main", "text": "@api is safe."})
    s.apply("add_node", {"name": "rule", "anchors": ["p1.1"],
                         "text": "for every service s, (if (s is reviewed), then (s is safe))."})
    s.apply("add_node", {"name": "fact", "text": "(@api is reviewed) and (@api is safe).", "anchors": ["p1.2"]})
    s.apply("add_node", {"name": "goal", "text": "@api is safe.", "anchors": ["p2.1"], "parents": ["fact"]})
    status = _status_after(s)
    assert status["failures"] == ["assumption fact alone entails target t_main"]


def test_review3_target_must_be_a_claimed_sentence():
    from ve.assist import AssistError
    with pytest.raises(AssistError, match="must be a claimed sentence"):
        AssistSession.create(ENV, source_from_text(TEXT), [{"id": "t", "sentence": "p1.2"}])


def test_review3_untagged_plain_text_defaults_to_claimed_not_given():
    source = source_from_text("Every reviewed service is safe. The API is reviewed.\n\nSo the API is safe.")
    assert {r["role"] for r in source["sentences"]} == {"claimed"}
    s = AssistSession.create(ENV, source, [{"id": "t_main", "sentence": "p2.1"}])
    s.apply("freeze_target", {"target": "t_main", "text": "@api is safe."})
    s.apply("add_node", {"name": "rule", "anchors": ["p1.1"],
                         "text": "for every service s, (if (s is reviewed), then (s is safe))."})
    s.apply("add_node", {"name": "fact", "text": "@api is reviewed.", "anchors": ["p1.2"]})
    s.apply("add_node", {"name": "goal", "text": "@api is safe.", "anchors": ["p2.1"], "parents": ["rule", "fact"]})
    status = _status_after(s)
    assert {r["anchor_state"] for r in status["unanchored_assumptions"]} == {"anchored_to_claim_only"}
    assert not status["success"]


def test_review4_vacuous_target_is_rejected():
    s = new_session()
    for text in ("true.", "(@api is safe) or (not (@api is safe))."):
        r = s.apply("freeze_target", {"target": "t_main", "text": text})
        assert not r["ok"] and "vacuous" in r["error"]["message"]
    from ve.assist import AssistError
    with pytest.raises(AssistError, match="vacuous"):
        AssistSession.create(ENV, source_from_text(TEXT), [{"id": "t", "sentence": "p2.1", "formula": "true."}])


def test_review5_declare_requires_frozen_targets():
    s = new_session()
    r = s.apply("declare", {"name": "okay", "gloss": "Cleared for release by ops.", "arguments": ["service"]})
    assert not r["ok"] and "Freeze every target" in r["error"]["message"]
    assert "okay" not in s.env.predicates


def test_review5_renamed_conclusion_through_an_ordinary_assumption_chain():
    s = new_session()
    s.apply("freeze_target", {"target": "t_main", "text": "@api is safe."})
    assert s.apply("declare", {"name": "gamma", "gloss": "An unrelated marker for testing.",
                               "arguments": ["service"]})["ok"]
    s.apply("add_node", {"name": "carrier", "anchors": ["p1.1"],
                         "text": "(@api is gamma) and (if (@api is gamma), then (@web is reviewed))."})
    s.apply("add_node", {"name": "ordinary", "text": "if (@web is reviewed), then (@api is safe)."})
    s.apply("add_node", {"name": "fact", "text": "@api is reviewed.", "anchors": ["p1.2"]})
    s.apply("add_node", {"name": "goal", "text": "@api is safe.", "anchors": ["p2.1"],
                         "parents": ["carrier", "ordinary"]})
    status = _status_after(s)
    assert status["renamed_conclusions"] == [{"target": "t_main", "assumptions": ["carrier", "ordinary"]}]
    assert not status["success"]


def _proposed_session(proposer=None):
    s = new_session()
    s.apply("freeze_target", {"target": "t_main", "text": "@api is safe."})
    s.proposer = proposer or FakeProposer(['{"candidates": [{"ve": "@api is reviewed."}]}'])
    assert s.apply("propose", {"sentence": "p1.2", "k": 1})["ok"]
    return s


def test_review6_config_digest_is_checked_on_load():
    ledger = json.loads(json.dumps(_proposed_session().to_ledger()))
    ledger["config"]["targets"][0]["formula"] = "@web is safe."
    with pytest.raises(LedgerReplayError, match="config_digest"):
        AssistSession.from_ledger(ledger)
    ledger = json.loads(json.dumps(new_session().to_ledger()))
    ledger["config"]["source"]["sentences"][2]["role"] = "given"
    with pytest.raises(LedgerReplayError, match="config_digest"):
        AssistSession.from_ledger(ledger, verify=False)


def test_review6_token_totals_are_recomputed_not_copied():
    ledger = json.loads(json.dumps(_proposed_session().to_ledger()))
    ledger["events"][1]["tokens"]["proposer"]["input_tokens"] = 1
    with pytest.raises(LedgerReplayError, match="tokens"):
        AssistSession.from_ledger(ledger, verify=False)
    ledger = json.loads(json.dumps(_proposed_session().to_ledger()))
    ledger["events"][1]["model_calls"][0]["input_tokens"] = -500
    with pytest.raises(LedgerReplayError):
        AssistSession.from_ledger(ledger, verify=False)


def test_review6_forged_rejected_by_api_event_is_refused():
    s = new_session()
    call_tool(s, "nope", {})
    ledger = json.loads(json.dumps(s.to_ledger()))
    assert AssistSession.from_ledger(ledger)
    ledger["events"][0]["tokens"] = {"author": {"input_tokens": -500, "output_tokens": 0, "calls": 1}}
    with pytest.raises(LedgerReplayError, match="API rejection"):
        AssistSession.from_ledger(ledger, verify=False)
    ledger["events"][0].pop("tokens")
    ledger["events"][0]["result"] = {"ok": True}
    with pytest.raises(LedgerReplayError, match="API rejection"):
        AssistSession.from_ledger(ledger, verify=False)


class LedgeredProposer(FakeProposer):
    """Fake backend that writes a claude-CLI-style calls ledger."""
    model_id = "claude-haiku-4-5-20251001"

    def __init__(self, replies):
        super().__init__(replies)
        self.rows = []

    def __call__(self, system, prompt, item):
        reply = super().__call__(system, prompt, item)
        key = f"key-{len(self.rows)}"
        self.rows.append({"key": key, "item_id": item, "status": "ok", "system": system, "prompt": prompt,
                          "text": reply["text"], "input_tokens": 1000, "output_tokens": 50,
                          "served_model": "fake-haiku", "account_label": "test",
                          "controls": {"model": self.model_id}})
        return {**reply, "call_key": key}


def test_review6_verify_session_rebuilds_config_and_matches_calls_ledger():
    from ve.assist import verify_session
    built = source_from_p5(P5_ITEM)
    s = AssistSession.create(built["environment"], built["source"], built["targets"], metadata=built["metadata"])
    s.proposer = LedgeredProposer(['{"candidates": [{"ve": "@unit1 is sealed."}]}'])
    assert s.apply("propose", {"sentence": "n00.1", "k": 1})["ok"]
    assert s.events[-1]["model_calls"][0]["requested_model"] == "claude-haiku-4-5-20251001"
    rows = s.proposer.rows
    ledger = json.loads(json.dumps(s.to_ledger()))
    good = verify_session(ledger, item=P5_ITEM, calls=rows)
    assert good["ok"], good["problems"]
    # Forged config with a recomputed digest: replays, but differs from the dossier.
    from ve.assist.session import config_digest
    fresh = AssistSession.create(built["environment"], built["source"], built["targets"], metadata=built["metadata"])
    forged = json.loads(json.dumps(fresh.to_ledger()))
    forged["config"]["source"]["sentences"][0]["text"] = "unit1 is sealed and every unit is ready."
    forged["config"]["config_digest"] = config_digest(forged["config"])
    assert AssistSession.from_ledger(forged, verify=False)
    assert "config source differs from the rebuilt configuration" in verify_session(forged, item=P5_ITEM)["problems"]
    # Consistently lowered tokens: replays, but disagrees with the calls ledger.
    cheaper = json.loads(json.dumps(ledger))
    cheaper["events"][-1]["model_calls"][0]["input_tokens"] = 10
    cheaper["events"][-1]["tokens"]["proposer"]["input_tokens"] = 10
    assert AssistSession.from_ledger(cheaper)
    assert any("input_tokens differs" in p for p in verify_session(cheaper, item=P5_ITEM, calls=rows)["problems"])
    # A call the session never recorded (hidden spend) is reported.
    extra = rows + [{**rows[0], "key": "key-hidden"}]
    assert any("never recorded" in p for p in verify_session(ledger, item=P5_ITEM, calls=extra)["problems"])


class FailingProposer:
    model_id = "claude-haiku-4-5-20251001"

    def __init__(self):
        self.items = []

    def __call__(self, system, prompt, item):
        from ve_experiments.claude_cli import EndpointError
        self.items.append(item)
        exc = EndpointError("Input overhead drift for identical content")
        exc.usage = {"input_tokens": 900, "output_tokens": 12, "model": "claude-haiku-4-5-20251001",
                     "account_label": "test", "call_key": "k1"}
        raise exc


def test_review7_backend_error_is_logged_with_spent_usage_and_retryable():
    s = new_session()
    s.apply("freeze_target", {"target": "t_main", "text": "@api is safe."})
    s.proposer = failing = FailingProposer()
    r = call_tool(s, "propose", {"sentence": "p1.2", "k": 1})
    assert not r["ok"] and r["error"]["code"] == "ProposerBackendError"
    assert s.events[-1]["tokens"]["proposer"] == {"input_tokens": 900, "output_tokens": 12, "calls": 1}
    assert s.usage()["tokens"]["proposer"]["input_tokens"] == 900
    s.proposer = FakeProposer(['{"candidates": [{"ve": "@api is reviewed."}]}'])
    assert s.apply("propose", {"sentence": "p1.2", "k": 1})["ok"]
    assert s.proposer.calls[0][2] != failing.items[0]  # fresh backend key for the retry
    replayed = AssistSession.from_ledger(json.loads(json.dumps(s.to_ledger())))
    assert replayed.usage()["tokens"]["proposer"]["input_tokens"] == 1900


def test_review7_cli_backend_error_is_logged_not_a_traceback(tmp_path, capsys, monkeypatch):
    import ve.assist.cli as cli
    env = tmp_path / "env.json"
    env.write_text(json.dumps(ENV))
    text = tmp_path / "arg.txt"
    text.write_text(TEXT)
    session = tmp_path / "s.json"
    run_cli(capsys, "new", session, "--env", env, "--text", text, "--target", "p2.1")
    run_cli(capsys, "freeze", session, "t_p2_1", "@api is safe.")
    monkeypatch.setattr(cli, "_proposer", lambda args: FailingProposer())
    code, out = run_cli(capsys, "propose", session, "p1.2")
    assert code == 2 and "ProposerBackendError" in out
    events = json.loads(session.read_text())["events"]
    assert events[-1]["tokens"]["proposer"]["input_tokens"] == 900
    code, out = run_cli(capsys, "call", session, "status", "{}")
    assert code == 0 and '"input_tokens": 900' in out


def test_review8_failed_propose_does_not_make_the_session_unloadable():
    s = new_session()
    assert not s.apply("propose", {"sentence": "p1.2"})["ok"]  # no backend configured
    replayed = AssistSession.from_ledger(json.loads(json.dumps(s.to_ledger())))
    assert len(replayed.events) == 1


def test_review9_error_path_redacts_parsed_stream_and_reports_usage(tmp_path, monkeypatch):
    import subprocess
    import ve_experiments.claude_cli as cc
    from ve_experiments.assist_haiku import ClaudeProposer
    secret, model = "sk-SECRET-TOKEN-123", cc.MODELS["sonnet"]
    fake = tmp_path / "claude"
    fake.write_text("#!/bin/sh\n")
    stream = "\n".join(json.dumps(r) for r in [
        {"type": "system", "subtype": "init", "model": model, "tools": [], "mcp_servers": [], "agents": []},
        {"type": "assistant", "message": {"id": "m1", "model": model,
                                          "content": [{"type": "text", "text": "echo " + secret}]}},
        {"type": "result", "subtype": "success", "is_error": False, "num_turns": 1, "result": "echo " + secret,
         "stop_reason": "end_turn", "modelUsage": {model: {}},
         "usage": {"input_tokens": 900, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0,
                   "output_tokens": 7}}])
    dates = iter([None, cc.EndpointError("Injected context date would drift")])

    def date_check(controls):
        outcome = next(dates)
        if outcome:
            raise outcome
    monkeypatch.setattr(cc.shutil, "which", lambda name: str(fake))
    monkeypatch.setattr(cc.subprocess, "check_output", lambda *a, **k: cc.Controls().cli_version)
    monkeypatch.setattr(cc.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 0, stream, ""))
    monkeypatch.setattr(cc, "oauth_token", lambda config=None: secret)
    monkeypatch.setattr(cc, "check_context_date", date_check)
    monkeypatch.setenv("VE_ASSIST_CLAUDE_ACCOUNT", "work")
    proposer = ClaudeProposer(tmp_path / "calls.jsonl", model="sonnet",
                              working_directory=str(tmp_path / "empty"))
    assert proposer.client.account_label == "work" and proposer.model_id == "claude-sonnet-5"
    with pytest.raises(cc.EndpointError) as caught:
        proposer("sys", "prompt", "item")
    assert caught.value.usage["input_tokens"] == 900 and caught.value.usage["model"] == model
    written = (tmp_path / "calls.jsonl").read_text()
    assert secret not in written and "[REDACTED]" in written
    with pytest.raises(ValueError):
        ClaudeProposer(tmp_path / "x.jsonl", model="gpt")
