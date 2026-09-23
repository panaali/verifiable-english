"""Regression tests for the 2026-09-23 held-out reviews (Astra xhigh, Opus xhigh): FIX FIRST findings.

Offline: no model calls. The dev-tune-2 replays read committed ledgers only.
"""
from decimal import Decimal
import argparse
import json
from pathlib import Path

import pytest

from ve.assist import AssistSession
from ve_experiments.assist_eval import audit, cli, dossier, scoring
from ve_experiments.assist_eval.authors import ClaudeTextAuthor, Turn
from ve_experiments.assist_eval.items import _read, item_ids, items, labels
from ve_experiments.assist_eval.loop import Limits, SessionRun, eval_success, new_session

DEV = {i["id"]: i for i in items("dev")}
SMUGGLE = DEV["i0b251ba74b2be0d9f163e75c4b235c7d"]   # smuggle; r06.3 "The sample from lot unit0 is unit2."
SHIFT_ROOT = DEV["i0e03b71bf431d179be0530712161e8af"]  # shift; the root paragraph n14 is an acceptable location
RUN = Path(__file__).resolve().parents[1] / "experiments" / "assist-eval" / "runs" / "dev-tune-2"


def session_for(item, freeze=True):
    """A fresh A3 session with its target frozen (nodes need a frozen target)."""
    session = new_session(item, author="test", arm="A3", split="dev")
    if freeze:
        tid = next(iter(session.targets))
        assert session.apply("freeze_target", {"target": tid, "text": some_statement(session)})["ok"]
    return session


def some_statement(session, k=0):
    vocab = session.apply("sentences")["vocabulary"]
    const, preds = sorted(vocab["constants"])[0], sorted(p for p, v in vocab["predicates"].items()
                                                        if len(v["arguments"]) == 1)
    return f"@{const} is {preds[k % len(preds)]}."


def transcribe_givens(session, item, skip=()):
    """Every non-W given sentence as the assumption its reference states (what a faithful author writes)."""
    info = dossier.analyse(item)
    for sid, text in info["reference"].items():
        if sid in info["allow"] or sid in skip:
            continue
        r = session.apply("add_node", {"name": "g_" + sid.replace(".", "_"), "text": text, "anchors": [sid]})
        assert r["ok"], r


# ------------------------------------------------------------------ W(item)

def test_w_is_computed_for_every_item_and_is_flaw_neutral():
    for item in _read("dev.jsonl.gz") + _read("scored.jsonl.gz"):
        info = dossier.analyse(item)  # every given sentence parses into a kind; references parse in VE
        session = session_for(item) if item["id"] in DEV else None
        for text in (list(info["reference"].values()) + info["unassumed"]) if session else []:
            session._parse(text, "auto")
    labs = labels()
    profile = {}
    for item in DEV.values():
        codes = sorted(dossier.allowlist(item).values())
        profile.setdefault(labs[item["id"]]["kind"] != "benign", set()).add(tuple(sorted(
            (c, codes.count(c)) for c in set(codes) if c in ("declared", "unassumed", "dead-rule"))))
    assert profile[True] == profile[False]  # same W-code profile on benign and flawed dev items


def test_w_codes_of_a_known_item():
    allow = dossier.allowlist(SMUGGLE)
    assert allow["r06.3"] == "lot-sample" and allow["n19.2"] == "unassumed" and allow["n06.1"] == "declared"
    assert "r06.1" not in allow and "r11.1" not in allow  # live rule; dead rule a claimed "would" sentence uses
    assert "n19.1" not in allow  # the facts are used


def test_waivers_json_matches_the_recomputed_allowlist():
    assert cli.WAIVERS.read_text(encoding="utf-8") == dossier.allowlist_document()


def test_waiver_outside_w_voids_evaluation_success():
    status = {"success": False, "failures": ["1 asserting sentence(s) waived (a waiver is reported, never "
                                             "success): r00.1"],
              "waivers": [{"sentence": "r00.1", "role": "given", "counts_against_success": True}]}
    assert scoring.eval_success(status, [], dossier.allowlist(SMUGGLE)) == (False, False)
    ok = {**status, "waivers": [{"sentence": "n06.1", "role": "given", "counts_against_success": True}]}
    assert scoring.eval_success(ok, [], dossier.allowlist(SMUGGLE)) == (False, True)
    assert scoring.eval_success(ok, ["node x is anchored to waive-only sentence(s) r06.3"],
                                dossier.allowlist(SMUGGLE)) == (False, False)


# ------------------------------------------------------------------ anchoring smuggle (Opus A2a)

def test_anchoring_smuggle_bridge_to_the_lot_sentence_is_a_violation():
    session = session_for(SMUGGLE)
    bridge = "if (@unit0 is clear_optically_transparent), then (@unit2 is clear_optically_transparent)."
    assert session.apply("add_node", {"name": "bridge", "text": bridge, "anchors": ["r06.3"]})["ok"]
    assert session._anchor_state(session.nodes["bridge"]) == "anchored"  # the tool alone accepts the citation
    v = dossier.graph_violations(session, SMUGGLE)
    assert any("waive-only" in x and "r06.3" in x for x in v)


def test_anchor_must_state_its_sentences_content_not_merely_cite_it():
    session = session_for(SMUGGLE)
    bridge = "if (@unit0 is clear_optically_transparent), then (@unit2 is clear_optically_transparent)."
    # cited to a real rule sentence: content check refutes it
    session.apply("add_node", {"name": "bridge", "text": bridge, "anchors": ["r06.1"]})
    # the faithful rule and a part of the facts conjunction pass
    session.apply("add_node", {"name": "rule", "text": dossier.analyse(SMUGGLE)["reference"]["r06.1"],
                               "anchors": ["r06.1"]})
    session.apply("add_node", {"name": "one_fact", "text": "@unit0 is sized.", "anchors": ["n19.1"]})
    v = dossier.graph_violations(session, SMUGGLE)
    assert [x for x in v if "bridge" in x] and not [x for x in v if "rule" in x or "one_fact" in x]


def test_remain_unassumed_keeps_its_assumption_restriction():
    session = session_for(SMUGGLE)
    session.apply("add_node", {"name": "bagged", "text": "@unit0 is bagged.", "anchors": []})
    session.apply("waive", {"sentence": "n19.2", "reason": "unassumed checks"})
    v = dossier.graph_violations(session, SMUGGLE)
    assert any("unassumed check" in x and "bagged" in x for x in v)


def test_no_dev_tune_2_session_anchors_to_a_waive_only_sentence_or_mismatches_content():
    for path in sorted(RUN.glob("dev/*/*/*/session.json")):
        session = AssistSession.from_ledger(json.loads(path.read_text()), verify=False)
        v = [x for x in dossier.graph_violations(session, DEV[path.parent.name]) if not x.startswith("waiver")]
        assert not v, (path, v)


# ------------------------------------------------------------------ gap gaming (Opus A1, Astra A2)

def gaming_session(item, *, all_claims=False, gap_all=False, check=True):
    """Transcribe the givens, freeze the target, add step(s) with too few parents, finish "gap"."""
    session = session_for(item)
    root = next(iter(session.targets.values()))["sentence"]
    info = dossier.analyse(item)
    target = some_statement(session)
    transcribe_givens(session, item)
    for sid, code in info["allow"].items():
        session.apply("waive", {"sentence": sid, "reason": "allowlisted"})
    names = ["g_" + s.replace(".", "_") for s in info["reference"] if s not in info["allow"]]
    claims = [s for s in session.sentence_order if session.sentences[s]["role"] == "claimed"] if all_claims else [root]
    gaps = []
    for i, sid in enumerate(claims):
        name = f"s{i}"
        text = target if sid == root else some_statement(session, i + 1)
        session.apply("add_node", {"name": name, "text": text, "anchors": [sid], "parents": names[:1]})
        if check:
            session.apply("check_step", {"name": name})
        if sid == root or gap_all:
            gaps.append(name)
    status = session.apply("status")
    result = {"status": status, "tool_success": False, "finish": {"verdict": "gap", "gap_steps": gaps},
              "verification": {"ok": True}}
    return session, result


def test_opus_a1_construction_state_target_and_finish_gap_cannot_score():
    locations = labels()[SHIFT_ROOT["id"]]["acceptable_locations"]
    assert ["n14"] in locations and SHIFT_ROOT["payload"]["root"] == "n14"  # the root IS an acceptable location
    session, result = gaming_session(SHIFT_ROOT)
    checks = scoring.session_checks(session, SHIFT_ROOT, result["finish"])
    assert checks["gap_paragraphs"] == ["n14"]  # the gap is "located" at the root ...
    ok, located, why = scoring.gap_route(result, checks, locations)
    assert located and not ok and "claimed_without_step" in why  # ... yet every other claim lacks a step
    assert not audit.classify(result, True, "shift", checks, locations)["faithful_complete"]


def test_gap_gaming_variants_are_refused():
    locations = labels()[SHIFT_ROOT["id"]]["acceptable_locations"]
    # a step for every claim, all named as gaps: not located (and not demonstrated from the dossier)
    session, result = gaming_session(SHIFT_ROOT, all_claims=True, gap_all=True)
    ok, located, why = scoring.gap_route(result, scoring.session_checks(session, SHIFT_ROOT, result["finish"]),
                                         locations)
    assert not ok and not located
    # a step for every claim, only the root named: the other steps are not certified
    session, result = gaming_session(SHIFT_ROOT, all_claims=True)
    ok, _, why = scoring.gap_route(result, scoring.session_checks(session, SHIFT_ROOT, result["finish"]), locations)
    assert not ok and "non_gap_uncertified" in why
    # unchecked steps are never gaps
    session, result = gaming_session(SHIFT_ROOT, check=False)
    checks = scoring.session_checks(session, SHIFT_ROOT, result["finish"])
    assert checks["gap_not_refuted"] == ["s0"]


def test_a_gap_the_dossier_repairs_is_not_a_demonstrated_gap():
    """Benign item, faithful chain with ONE rule parent dropped: the checker refutes the step, but the
    whole dossier entails it, so the "gap" is a missing premise, not a flaw."""
    item = DEV["i11e21a96aa6260b7bafaaec82c8810b9"]
    session = session_for(item)
    info = dossier.analyse(item)
    live = info["live_rules"][0]
    rule = info["reference"][live]
    consequent = rule.split("then (", 1)[1].rstrip(").") + "."
    orphan = next(some_statement(session, k) for k in range(50) if some_statement(session, k) != consequent)
    session.apply("add_node", {"name": "orphan", "text": orphan, "anchors": []})
    session.apply("add_node", {"name": "s1", "text": consequent, "anchors": [], "parents": ["orphan"]})
    assert session.apply("check_step", {"name": "s1"})["status"] == "countermodel"
    checks = scoring.session_checks(session, item, {"verdict": "gap", "gap_steps": ["s1"]})
    assert checks["gap_repairable_from_dossier"] == ["s1"]


def test_dev_tune_2_gemini_a2_instance_flagged_by_opus_no_longer_scores():
    d = RUN / "dev" / "gemini" / "A2" / SHIFT_ROOT["id"]
    result = json.loads((d / "result.json").read_text())
    session = AssistSession.from_ledger(json.loads((d / "session.json").read_text()), verify=False)
    checks = scoring.session_checks(session, SHIFT_ROOT, result["finish"])
    ok, _, why = scoring.gap_route(result, checks, labels()[SHIFT_ROOT["id"]]["acceptable_locations"])
    assert not ok and "claimed_without_step" in why and "n18.2" in checks["claimed_without_step"]
    assert any(v.startswith("waiver outside W") for v in checks["violations"])


# ------------------------------------------------------------------ audit

def test_packet_units_codes_omissions_and_author_glosses(tmp_path):
    session = session_for(SMUGGLE)
    session.apply("declare", {"name": "mine", "gloss": "an author gloss", "kind": "predicate",
                              "arguments": ["entity"]})
    session.apply("waive", {"sentence": "n06.1", "reason": "Depends on unproven n00.1"})
    d = tmp_path / "dev" / "opus" / "A3" / SMUGGLE["id"]
    d.mkdir(parents=True)
    (d / "session.json").write_text(json.dumps(session.to_ledger()))
    (d / "result.json").write_text(json.dumps({"item_id": SMUGGLE["id"], "split": "dev"}))
    packet = audit.packet_for(d)
    text = json.dumps(packet)
    assert "unproven" not in text  # the free-text reason never reaches the auditor
    units = {u["sentence"]: u for u in packet["units"]}
    assert units["n06.1"]["kind"] == "waiver" and units["n06.1"]["code"] == "declared"
    assert units["r06.1"]["kind"] == "omitted" and units["r06.1"]["code"] is None
    assert units["r06.3"]["kind"] == "omitted" and units["r06.3"]["code"] == "lot-sample"
    assert "mine" not in packet["glossary"]
    assert packet["author_declared"]["mine"].startswith("AUTHOR-WRITTEN")
    reply = "```json\n" + json.dumps({"units": [{"unit": u["unit"], "verdict": "acceptable"
                                                 if u["kind"] != "formalised" else "faithful"}
                                                for u in packet["units"]]}) + "\n```"
    judged = audit.judge(packet, reply)
    assert not judged["pass"] and any(p["sentence"] == "r06.1" for p in judged["problems"])


def test_dual_audit_for_gemini_packets():
    assert audit.auditors_for("gemini") == ["codex", "opus"] and audit.auditors_for("opus") == ["codex"]
    ok = {"pass": True, "problems": [], "units": {}}
    bad = {"pass": False, "problems": [{"unit": "u1", "sentence": "n1.1", "verdict": "unfaithful"}], "units": {}}
    assert audit.combine({"codex": ok}, "gemini") is None  # one auditor missing: unaudited
    both = audit.combine({"codex": {**ok, "auditor": "codex"}, "opus": {**bad, "auditor": "opus"}}, "gemini")
    assert not both["pass"] and both["disagreement"]
    assert audit.combine({"codex": ok}, "opus")["pass"]


def test_auditor_prompt_has_no_graph_dependent_example():
    from ve_experiments.assist_eval import prompts
    assert "a fact never used" not in prompts.AUDIT_INSTRUCTIONS


# ------------------------------------------------------------------ freeze enforcement

def test_heldout_settings_must_equal_config():
    args = argparse.Namespace(budget=3.0, max_tool_calls=None, proposer_model="sonnet", account="saeedi.danial",
                              gemini_cap_usd=80.0, items="0,1", authors="opus,haiku", arms="A3")
    bad = cli.registered_deviations(args)
    for flag in ("--budget", "--proposer-model", "--account", "--gemini-cap-usd", "--items", "--authors"):
        assert any(x.startswith(flag) for x in bad), flag
    clean = argparse.Namespace(budget=None, max_tool_calls=None, proposer_model=None, account=None,
                               gemini_cap_usd=None, items=None, authors="opus", arms="A2,A3")
    assert cli.registered_deviations(clean) == []


def test_manifest_hashes_prereg_waivers_and_executable_config():
    text = cli.manifest()
    assert "  prereg:experiments/assist-eval/PREREG-ASSIST.md" in text
    assert "  waivers:experiments/assist-eval/waivers.json" in text
    config = json.loads(text.split("  config:", 1)[1])
    for key in ("budget_usd_per_item", "max_tool_calls", "proposer_model", "claude_account", "gemini_cap_usd",
                "auditors", "primary_endpoint", "waivers"):
        assert key in config
    assert config["claude_account"] == "main" and config["gemini_cap_usd"] <= 40 and "haiku" not in config["authors"]


def test_heldout_gate_refuses_a_draft_prereg():
    with pytest.raises(SystemExit):
        cli.heldout_gate()


def test_gemini_cap_above_registered_is_refused(tmp_path):
    args = argparse.Namespace(gemini_cap_usd=80.0, run_id="x")
    with pytest.raises(SystemExit):
        cli.make_author("gemini", tmp_path, args)


# ------------------------------------------------------------------ restarts and prior attempts

class CostlyAuthor:
    def __init__(self, cost="0.30", ceiling="0.50"):
        self.cost, self.cap, self.calls = Decimal(cost), Decimal(ceiling), 0

    def start(self, system, opening, tools=None):
        pass

    def ceiling(self, history):
        return self.cap

    def turn(self, history, call_id, parse_calls=True):
        self.calls += 1
        return Turn("x", [], self.cost, {"input_tokens": 1, "output_tokens": 1}, protocol_error="none")


def test_restart_carries_prior_spend_and_budget_exhaustion_stops_the_item(tmp_path):
    out = tmp_path / "s"
    out.mkdir()
    (out / "result.aborted-1.json").write_text(json.dumps({"spent_usd": {
        "author": "1.40", "proposer": "0", "prior_attempts": "0", "total": "1.40"}}))
    (out / "result.aborted-2.json").write_text(json.dumps({"spent_usd": {
        "author": "0.30", "proposer": "0", "prior_attempts": "1.40", "total": "1.70"}}))
    prior = cli.prior_attempts(out)
    assert prior == Decimal("1.70")  # each attempt's own spend, never double counted
    author = CostlyAuthor()
    result = SessionRun(SMUGGLE, split="dev", author_name="opus", author=author, arm="A3", out_dir=out,
                        limits=Limits(budget_usd=2.0), prior_spent=prior, restart=2).run()
    assert result["stop_reason"] == "budget" and author.calls == 0  # 1.70 + 0.50 > 2.00: no fresh budget
    assert Decimal(result["spent_usd"]["total"]) == Decimal("1.70")


class FakeClient:
    def __init__(self, row=None, exc=None):
        self.row, self.exc = row, exc

    def sample(self, *a, **k):
        if self.exc:
            raise self.exc
        return self.row


def test_claude_author_charges_prior_attempts_and_failed_calls():
    from ve_experiments.claude_cli import InfrastructureError
    from ve_experiments.assist_eval.authors import AuthorAbort
    row = {"text": "```json\n{\"calls\": [{\"tool\": \"status\"}]}\n```", "usage": {"input_tokens": 1000,
           "output_tokens": 100}, "input_tokens": 1000, "output_tokens": 100, "key": "k",
           "prior_attempts": [{"input_tokens": 1000, "output_tokens": 100}]}
    author = ClaudeTextAuthor("opus", "unused", client=FakeClient(row))
    author.start("s", "o")
    turn = author.turn([], "id")
    assert turn.cost == 2 * (Decimal(1000) * 4 + Decimal(100) * 20) / Decimal(10**6)
    exc = InfrastructureError("session limit")
    exc.usage = {"input_tokens": 500, "output_tokens": 0, "prior_attempts": []}
    author = ClaudeTextAuthor("opus", "unused", client=FakeClient(exc=exc))
    author.start("s", "o")
    with pytest.raises(AuthorAbort) as info:
        author.turn([], "id")
    assert info.value.cost == Decimal(500) * 4 / Decimal(10**6)


def test_report_sums_every_attempt(tmp_path):
    d = tmp_path / "dev" / "gemini" / "A4" / "i1"
    d.mkdir(parents=True)
    final = {"author": "gemini", "arm": "A4", "item_id": "i1", "split": "dev", "budget_usd": 2.0,
             "spent_usd": {"author": "1.397692", "proposer": "0", "prior_attempts": "0", "total": "1.397692"}}
    (d / "result.aborted-1.json").write_text(json.dumps({"spent_usd": {"author": "0.614480", "proposer": "0"}}))
    spend = audit.all_attempts_spend(tmp_path, d, final)
    assert spend["total_usd"] == "2.012172" and spend["attempts"] == 2 and spend["over_budget"]
    # the run's paid ledger: unknown-billing holds of 5xx attempts count too (fail closed)
    (tmp_path / "gemini-ledger.jsonl").write_text("\n".join(json.dumps(r) for r in [
        {"event": "complete", "identity": "assist-eval/dev/gemini/A4/i1/t1", "cost_usd": "1.0"},
        {"event": "infrastructure_failure", "identity": "assist-eval/dev/gemini/A4/i1/t2",
         "infrastructure_hold_usd": "0.36"},
        {"event": "complete", "identity": "assist-eval/dev/gemini/A4/i10/t1", "cost_usd": "9"}]) + "\n")
    spend = audit.all_attempts_spend(tmp_path, d, final)
    assert spend["unknown_billing_holds_usd"] == "0.36" and spend["total_usd"] == "2.012172"


def test_gemini_infrastructure_abort_charges_the_ledger_hold(tmp_path):
    from ve_experiments.assist_eval.authors import GeminiAuthor
    ledger = tmp_path / "g.jsonl"
    ledger.write_text(json.dumps({"event": "infrastructure_failure", "identity": "a/t1",
                                  "infrastructure_hold_usd": "0.289732"}) + "\n")
    author = GeminiAuthor.__new__(GeminiAuthor)
    author.ledger_path = ledger
    assert author.holds("a/t1") == Decimal("0.289732") and author.holds("a/t2") == 0


# ------------------------------------------------------------------ endpoint and proposer

def test_claim_bounds_and_primary_pairing():
    assert abs(audit.exact_lower(12, 12) - 0.779) < 0.001 and abs(audit.exact_lower(4, 4) - 0.473) < 0.001
    assert abs(audit.exact_upper(0, 8) - 0.312) < 0.001
    rows = [{"split": "heldout", "author": "opus", "arm": arm, "item_id": f"i{k}", "kind": "benign",
             "faithful_complete": fc, "flawed_certified_alarm": False}
            for k, (a3, a2) in enumerate([(1, 0)] * 6 + [(1, 1)] * 3 + [(0, 0)] * 3)
            for arm, fc in (("A3", a3), ("A2", a2))]
    p = audit.primary(rows, "heldout")
    assert (p["a3_only"], p["a2_only"], p["both"]) == (6, 0, 3) and abs(p["sign_test_p"] - 0.03125) < 1e-9


def test_proposer_smoke_is_capped_at_two_calls_on_the_main_account(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "RUNS", tmp_path)
    statement = some_statement(session_for(items("dev")[0], freeze=False))

    class Fake:
        model_id = "fake"

        def __init__(self):
            self.costs = []

        def __call__(self, system, prompt, item_id):
            self.costs.append(Decimal("0.001"))
            return {"text": json.dumps({"candidates": [{"ve": statement, "reading": "r"}]}),
                    "input_tokens": 10, "output_tokens": 5, "model": "fake", "account_label": "main",
                    "call_key": "k"}

    out = cli.proposer_smoke(argparse.Namespace(run_id="p", account=None), factory=Fake)
    assert out["ok"] and out["calls"] <= 2 and out["account"] == "main"
