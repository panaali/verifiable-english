"""Regression tests for the 2026-09-23 held-out RE-reviews (Astra xhigh, Opus xhigh; reviews/assist-heldout-
review2-*.md): full-graph packets, per-anchor and coverage checks, claim-step checks, freeze, budget, blinding.

Offline: no model calls (tests/conftest.py fails any test that tries one).
"""
from decimal import Decimal
import argparse
import json
from pathlib import Path

import pytest

from ve.assist import AssistSession
from ve_experiments import paid
from ve_experiments.assist_eval import audit, cli, dossier, scoring
from ve_experiments.assist_eval.authors import (AuthorError, ClaudeTextAuthor, GeminiAuthor, ItemBudgetExhausted,
                                                refuse_account_env)
from ve_experiments.assist_eval.items import items, labels
from ve_experiments.assist_eval.loop import Limits, SessionRun, new_session

DEV = {i["id"]: i for i in items("dev")}
SMUGGLE = DEV["i0b251ba74b2be0d9f163e75c4b235c7d"]
SHIFT_ROOT = DEV["i0e03b71bf431d179be0530712161e8af"]
RUN = Path(__file__).resolve().parents[1] / "experiments" / "assist-eval" / "runs" / "dev-tune-2"

# Two ways to reach "unit1 is sealed": the stated fact n00, or the unstated n01 + rule r02.
ITEM = {"id": "demo2", "payload": {
    "id": "demo2", "root": "n02",
    "glossary": [{"term": "ready", "sense": "ready: packing completed (R01)"},
                 {"term": "ready", "sense": "ready: staffing arranged (R02)"},
                 {"term": "sealed", "sense": "sealed: seal applied (R03)"}],
    "premises": [{"id": "n00", "text": "unit1 is sealed."}, {"id": "n01", "text": "unit3 is sealed."}],
    "records": [{"id": "r01", "text": "If unit1 is sealed, then unit2 is ready (packing completed)."},
                {"id": "r02", "text": "If unit3 is sealed, then unit1 is sealed."}],
    "nodes": [{"id": "n02", "parents": ["n00"], "text": "Because unit1 is sealed, unit2 is ready."}],
    "argument": "[n02] Because unit1 is sealed, unit2 is ready."}}
RULE1 = "if (@unit1 is sealed), then (@unit2 is ready_packing_completed)."
RULE2 = "if (@unit3 is sealed), then (@unit1 is sealed)."
GOAL = "@unit2 is ready_packing_completed."


def demo_session(item=ITEM):
    session = new_session(item, author="test", arm="A3", split="dev")
    tid = next(iter(session.targets))
    assert session.apply("freeze_target", {"target": tid, "text": GOAL})["ok"]
    return session


def add(session, name, text, anchors=(), parents=()):
    r = session.apply("add_node", {"name": name, "text": text, "anchors": list(anchors), "parents": list(parents)})
    assert r["ok"], r
    if parents:
        session.apply("check_step", {"name": name})


def export(tmp_path, session, name):
    d = tmp_path / name / "dev" / "opus" / "A3" / ITEM["id"]
    d.mkdir(parents=True)
    (d / "session.json").write_text(json.dumps(session.to_ledger()))
    return audit.packet_for(d, ITEM)


# ------------------------------------------------------------------ 1. complete graph in the packet (Astra A1)

def test_packet_exports_the_complete_graph_so_a_helper_cannot_hide_the_reasoning(tmp_path):
    stated, other = demo_session(), demo_session()
    for s in (stated, other):
        add(s, "f1", "@unit1 is sealed.", ["n00.1"])
        add(s, "f3", "@unit3 is sealed.", ["n01.1"])
        add(s, "r1", RULE1, ["r01.1"])
        add(s, "r2", RULE2, ["r02.1"])
    add(stated, "h", "@unit1 is sealed.", parents=["f1"])        # the sentence's own reason
    add(other, "h", "@unit1 is sealed.", parents=["f3", "r2"])   # an unstated alternative
    for s in (stated, other):
        add(s, "goal", GOAL, ["n02.1"], ["r1", "h"])
        assert s.checks["goal"]["status"] == "follows" and s.checks["h"]["status"] == "follows"
    a, b = export(tmp_path, stated, "a"), export(tmp_path, other, "b")
    unit = lambda p: next(u for u in p["units"] if u["sentence"] == "n02.1")
    assert unit(a)["reasons"] == ["n00.1", "r01.1"] and unit(b)["reasons"] == ["n01.1", "r01.1", "r02.1"]
    helper = [n for n in b["nodes"] if not n["anchors"]]
    assert len(helper) == 1 and helper[0]["kind"] == "step" and len(helper[0]["derived_from"]) == 2
    assert {k: v for k, v in a.items() if k != "packet"} != {k: v for k, v in b.items() if k != "packet"}
    text = json.dumps(b)
    for leak in ("follows", "certified", "countermodel", "status", "parents", "goal", "opus", "A3"):
        assert leak not in text, leak  # certification stays hidden; author node names are replaced


# ------------------------------------------------------------------ 2. anchors (Astra A2, Opus A1/A2)

def test_each_anchor_alone_must_entail_its_assumption():
    joint = demo_session()
    add(joint, "q", GOAL, ["n00.1", "r01.1"])  # Q anchored to P and P -> Q: jointly entailed, singly not
    v = dossier.graph_violations(joint, ITEM)
    assert any("q does not state what its anchor n00.1 alone says" in x for x in v)
    split = demo_session()
    add(split, "p", "@unit1 is sealed.", ["n00.1"])
    add(split, "r", RULE1, ["r01.1"])
    assert not [x for x in dossier.graph_violations(split, ITEM) if "anchor" in x]


def test_given_coverage_needs_all_the_sentence_says_and_counts_steps():
    session = new_session(SMUGGLE, author="test", arm="A3", split="dev")
    tid = next(iter(session.targets))
    session.apply("freeze_target", {"target": tid, "text": "@unit0 is sized."})
    add(session, "one_fact", "@unit0 is sized.", ["n19.1"])  # "unit0 is sized; unit0 is released." (part)
    v = dossier.graph_violations(session, SMUGGLE)
    assert any("given n19.1 do not state all it says" in x for x in v)
    assert not any("one_fact does not state" in x for x in v)  # the part itself is faithful
    full = dossier.analyse(SMUGGLE)["reference"]["n19.1"]
    session.apply("add_node", {"name": "all_facts", "text": full, "anchors": []})
    session.apply("add_node", {"name": "rest", "text": full, "anchors": ["n19.1"], "parents": ["all_facts"]})
    assert not any("n19.1" in x for x in dossier.graph_violations(session, SMUGGLE))  # a step covers it too


def test_claim_steps_must_not_be_tautologies_nor_leave_their_sentence():
    session = demo_session()
    add(session, "f1", "@unit1 is sealed.", ["n00.1"])
    add(session, "taut", "if (@unit1 is sealed), then (@unit1 is sealed).", ["n02.1"], ["f1"])
    assert session.checks["taut"]["status"] == "follows"  # certified: the checker alone accepts it
    add(session, "far", "@unit3 is sealed.", ["n02.1"], ["f1"])
    v = dossier.graph_violations(session, ITEM)
    assert any("step taut" in x and "non-valid" in x for x in v)
    assert any("step far uses what its sentence(s) n02.1 do not mention: unit3 is sealed" in x for x in v)


def test_opus_a1_tautology_construction_no_longer_reaches_the_gap_route():
    """Freeze a target at the (acceptable) root, give every other claimed sentence a tautology, finish gap."""
    item, locations = SHIFT_ROOT, labels()[SHIFT_ROOT["id"]]["acceptable_locations"]
    session = new_session(item, author="test", arm="A3", split="dev")
    tid, target = next(iter(session.targets.items()))
    info = dossier.analyse(item)
    const = sorted(session.apply("sentences")["vocabulary"]["constants"])[0]
    pred = sorted(p for p, v in session.apply("sentences")["vocabulary"]["predicates"].items()
                  if len(v["arguments"]) == 1)[0]
    session.apply("freeze_target", {"target": tid, "text": f"@{const} is {pred}."})
    names = []
    for sid, text in info["reference"].items():
        if sid not in info["allow"]:
            name = "g_" + sid.replace(".", "_")
            session.apply("add_node", {"name": name, "text": text, "anchors": [sid]})
            names.append(name)
    for sid in info["allow"]:
        session.apply("waive", {"sentence": sid, "reason": "allowlisted"})
    gaps = []
    for i, sid in enumerate(s for s in session.sentence_order if session.sentences[s]["role"] == "claimed"):
        if sid == target["sentence"]:
            text = f"@{const} is {pred}."
            gaps.append(f"s{i}")
        else:
            unit, term = info["mentions"][sid][0]
            name = next(n for n, t in info["terms"].items() if t == term)
            text = f"if (@{unit if unit != '*' else const} is {name}), then (@{unit if unit != '*' else const} is {name})."
        session.apply("add_node", {"name": f"s{i}", "text": text, "anchors": [sid], "parents": names[:1]})
        session.apply("check_step", {"name": f"s{i}"})
    result = {"status": session.apply("status"), "tool_success": False, "verification": {"ok": True},
              "finish": {"verdict": "gap", "gap_steps": gaps}}
    checks = scoring.session_checks(session, item, result["finish"])
    assert not checks["non_gap_uncertified"]  # every tautology IS certified ...
    ok, _, why = scoring.gap_route(result, checks, locations)
    assert not ok and "violations" in why  # ... and the claim-step check refuses them
    assert any("non-valid" in v for v in checks["violations"])


def test_no_faithful_dev_session_is_rejected_by_the_new_checks():
    """Replay (report counts in the README): 42 faithful-complete dev-tune-2 sessions, 718 claim steps."""
    report = json.loads((RUN / "replay-v4" / "report.json").read_text())
    faithful = {(r["author"], r["arm"], r["item_id"]) for r in report["rows"] if r["faithful_complete"]}
    steps = 0
    for key in sorted(faithful):
        path = RUN / "dev" / key[0] / key[1] / key[2] / "session.json"
        session = AssistSession.from_ledger(json.loads(path.read_text()), verify=False)
        assert dossier.graph_violations(session, DEV[key[2]]) == [], key
        steps += sum(1 for n in session.nodes.values() if n.kind == "step"
                     and any(session.sentences[a]["role"] == "claimed" for a in n.anchors))
    assert (len(faithful), steps) == (42, 718)


# ------------------------------------------------------------------ 3. freeze (Opus A3, Astra A3)

def test_manifest_hashes_the_whole_ve_package():
    text = cli.manifest()
    for path in ("ve/entailment.py", "ve/parser.py", "ve/lexicon/oewn-2025.json", "ve/assist/session.py",
                 "ve_experiments/paid.py"):
        assert f"  {path}\n" in text, path
    config = json.loads(text.split("  config:", 1)[1])
    assert config["auditors"]["codex_model"] == audit.CODEX_MODEL == "gpt-6-astra"
    assert config["auditors"]["opus_audit_output_tokens"] == audit.OPUS_AUDIT_OUTPUT_TOKENS


def frozen_gate(tmp_path, monkeypatch):
    prereg = tmp_path / "PREREG.md"
    prereg.write_text("Status: FROZEN 2026-09-24\n")
    monkeypatch.setattr(cli, "PREREG", prereg)
    monkeypatch.setattr(cli, "manifest", lambda: "stamped manifest\n")
    manifest = tmp_path / "HASHES.txt"
    manifest.write_text("stamped manifest\n")
    monkeypatch.setattr(cli, "MANIFEST", manifest)
    monkeypatch.setattr(cli, "RUNS", tmp_path / "runs")
    return argparse.Namespace(budget=None, max_tool_calls=None, proposer_model=None, account=None,
                              gemini_cap_usd=None, items=None, authors="opus,gemini", arms="A2,A3,A4",
                              run_id="heldout-1")


def test_heldout_gate_allows_one_run_id_only(tmp_path, monkeypatch):
    args = frozen_gate(tmp_path, monkeypatch)
    cli.heldout_gate(args)  # a frozen, matching, full-set first run passes
    (tmp_path / "runs" / "heldout-1" / "heldout").mkdir(parents=True)
    cli.heldout_gate(args)  # resuming the same run id passes
    with pytest.raises(SystemExit, match="exactly one held-out run"):
        cli.heldout_gate(argparse.Namespace(**{**vars(args), "run_id": "heldout-2"}))
    with pytest.raises(SystemExit, match="--arms"):
        cli.heldout_gate(argparse.Namespace(**{**vars(args), "arms": "A3"}))


def test_account_environment_overrides_are_refused(tmp_path, monkeypatch):
    assert refuse_account_env({}) is None
    for name in ("VE_CLAUDE_ACCOUNT_CONFIG_DIR", "CLAUDE_CODE_OAUTH_TOKEN"):
        with pytest.raises(AuthorError, match=name):
            refuse_account_env({name: "x"})
    monkeypatch.setenv("CLAUDE_CODE_OAUTH_TOKEN", "sk-not-a-real-token-000000")
    with pytest.raises(AuthorError) as info:
        ClaudeTextAuthor("opus", tmp_path / "calls.jsonl")  # the real backend refuses to start
    assert "sk-not" not in str(info.value)  # the value is never echoed
    with pytest.raises(SystemExit, match="account override refused"):
        cli.heldout_gate(frozen_gate(tmp_path, monkeypatch))


# ------------------------------------------------------------------ 4. budget (Astra B, Opus B1)

class Flaky:
    """Synthetic Vertex backend: 504 errors, then replies (Astra's re-review cases)."""

    def __init__(self, *script):
        self.script, self.calls = list(script), 0

    def count(self, request):
        return 0

    async def generate(self, request):
        self.calls += 1
        step = self.script.pop(0)
        if step == 504:
            raise paid.InfrastructureError("HTTP 504: deadline exceeded", status_code=504)
        return step


def reply(input_tokens=1000):
    return paid.PaidReply("", input_tokens, 50, 0, 0, "rev-1", {}, {"role": "model", "content": ""})


CEILING = paid.cost("pro", 4096, 16000)  # count 0 -> margin 4,096 input tokens, 16,000 output


def gemini_run(tmp_path, monkeypatch, backend, prior="0", budget=2.0, cap=40):
    monkeypatch.setattr(paid.time, "sleep", lambda s: None)
    ledger = tmp_path / "gemini-ledger.jsonl"
    author = GeminiAuthor(ledger, cap_usd=cap, backend=backend)
    result = SessionRun(SMUGGLE, split="dev", author_name="gemini", author=author, arm="A3",
                        out_dir=tmp_path / "s", limits=Limits(budget_usd=budget, max_turns=1),
                        prior_spent=Decimal(prior)).run()
    identity = f"assist-eval/dev/gemini/A3/{SMUGGLE['id']}/t1"
    return result, author, author.charged(identity)


def test_504s_then_success_after_1_70_stop_before_the_cap(tmp_path, monkeypatch):
    backend = Flaky(504, 504, 504, reply())
    result, _, charged = gemini_run(tmp_path, monkeypatch, backend, prior="1.70")
    # 1.70 + one hold (0.2002) + another attempt's ceiling > 2.00: the retry is refused, the item stops
    assert backend.calls == 1 and result["stop_reason"] == "budget"
    assert Decimal(result["spent_usd"]["author"]) == charged == CEILING
    assert Decimal(result["spent_usd"]["total"]) <= Decimal("2.00")


def test_four_failed_attempts_never_cross_the_item_budget(tmp_path, monkeypatch):
    backend = Flaky(504, 504, 504, 504)
    result, _, charged = gemini_run(tmp_path, monkeypatch, backend, prior="1.40")
    assert backend.calls == 2 and result["stop_reason"] == "budget"  # a third attempt would reach $2.0006
    assert Decimal(result["spent_usd"]["author"]) == charged == 2 * CEILING
    assert Decimal(result["spent_usd"]["total"]) <= Decimal("2.00")


def test_a_recovered_504_charges_its_hold_in_session(tmp_path, monkeypatch):
    backend = Flaky(504, 504, 504, reply())
    result, author, charged = gemini_run(tmp_path, monkeypatch, backend)
    assert backend.calls == 4 and result["stop_reason"] == "max_turns"
    assert charged == 3 * CEILING + paid.cost("pro", 1000, 50)
    assert Decimal(result["spent_usd"]["author"]) == charged  # the three holds are charged to the turn


def test_a_billed_validation_failure_is_charged(tmp_path, monkeypatch):
    backend = Flaky(reply(input_tokens=5000))  # above the 4,096-token reservation: billed, then rejected
    result, _, charged = gemini_run(tmp_path, monkeypatch, backend)
    assert result["stop_reason"].startswith("abort: infrastructure")
    assert charged == paid.cost("pro", 5000, 50) > 0
    assert Decimal(result["spent_usd"]["author"]) == charged


def test_claude_infrastructure_retries_are_gated_on_the_item_budget(tmp_path):
    from ve_experiments import claude_cli as cc
    client = cc.ClaudeCLI(tmp_path / "calls.jsonl", infrastructure_retries=True)
    attempts = []

    def once(*a, **k):
        attempts.append(1)
        raise cc.InfrastructureError("HTTP 529 overloaded")
    client._sample_once = once
    author = ClaudeTextAuthor("opus", tmp_path / "unused", client=client)
    author.start("sys", "open")
    author.attempt_gate = lambda ceiling, already: False  # the item budget cannot cover another attempt
    with pytest.raises(ItemBudgetExhausted):
        author.turn([], "id")
    assert len(attempts) == 1


def test_an_over_budget_item_scores_as_a_failure():
    status = {"targets": [], "unproved_steps": [], "unanchored_assumptions": [], "uncovered": [],
              "renamed_conclusions": []}
    done = {"tool_success": True, "status": status, "finish": None, "verification": {"ok": True},
            "stop_reason": "finish"}
    clean = {"violations": [], "claimed_without_step": [], "gap_steps": [], "non_gap_uncertified": [],
             "gap_not_refuted": [], "gap_repairable_from_dossier": [], "gap_paragraphs": []}
    assert audit.classify(done, True, "benign", clean, [])["faithful_complete"]
    over = audit.classify(done, True, "benign", clean, [], over_budget=True)
    assert not over["faithful_complete"] and not over["tool_success"] and over["over_budget"]
    assert audit.attribute(done, {"pass": True}, over, {}) == "budget"


# ------------------------------------------------------------------ auditor spend cap

def test_audit_run_gates_priced_auditor_calls_on_max_usd(tmp_path):
    session = demo_session()
    add(session, "f1", "@unit1 is sealed.", ["n00.1"])
    d = tmp_path / "run" / "dev" / "gemini" / "A3" / ITEM["id"]
    d.mkdir(parents=True)
    (d / "session.json").write_text(json.dumps(session.to_ledger()))
    (d / "result.json").write_text(json.dumps({"author": "gemini", "arm": "A3", "item_id": ITEM["id"],
                                               "split": "dev"}))
    run_dir = tmp_path / "run"
    audit._items_by_id.cache_clear()
    mapping = {"order": [], "packets": {}}
    packet = audit.packet_for(d, ITEM)
    (run_dir / "audit" / "packets").mkdir(parents=True)
    (run_dir / "audit" / "packets" / f"{packet['packet']}.json").write_text(json.dumps(packet))
    mapping["order"].append(packet["packet"])
    mapping["packets"][packet["packet"]] = {"session_dir": "dev/gemini/A3/demo2", "author": "gemini",
                                            "arm": "A3", "item_id": ITEM["id"], "split": "dev"}
    (run_dir / "audit" / "mapping.json").write_text(json.dumps(mapping))

    class Priced:
        calls = 0

        def single_ceiling(self, system, prompt):
            return Decimal("0.30")

        def single(self, call_id, system, prompt):
            Priced.calls += 1
            return "{}", Decimal("0.10"), {"served_model": "x"}

    class Free:
        def single(self, call_id, system, prompt):
            return "{}", Decimal(0), {"served_model": "y"}

    missing = audit.run_audit(run_dir, auditors={"codex": Free(), "opus": Priced()}, max_usd=0.25)
    assert missing == 1 and Priced.calls == 0  # 0 + 0.30 > 0.25: the Opus call is not made
    assert "auditor cap" in (run_dir / "audit" / "errors.jsonl").read_text()
