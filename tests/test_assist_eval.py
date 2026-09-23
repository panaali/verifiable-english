"""ve_experiments.assist_eval: loop, arms, budget, text protocol, Gemini wiring, audit export (offline)."""
from decimal import Decimal
import json
from pathlib import Path

import pytest

from ve_experiments.assist_eval import audit, items, prompts
from ve_experiments.assist_eval.authors import (GeminiAuthor, Turn, parse_text_calls, render_transcript,
                                                vertex_tools)
from ve_experiments.assist_eval.loop import Limits, SessionRun, eval_success, evaluate_document
from ve_experiments.assist_eval.pricing import claude_cost

ITEM = {"id": "demo", "payload": {
    "id": "demo", "root": "n02",
    "glossary": [{"term": "ready", "sense": "ready: packing completed (R01)"},
                 {"term": "ready", "sense": "ready: staffing arranged (R02)"},
                 {"term": "sealed", "sense": "sealed: seal applied (R03)"}],
    "premises": [{"id": "n00", "text": "unit1 is sealed. Rules r01 are declared."}],
    "records": [{"id": "r01", "text": "If unit1 is sealed, then unit2 is ready (packing completed)."}],
    "nodes": [{"id": "n02", "parents": ["n00"], "text": "Because unit1 is sealed, unit2 is ready."}],
    "argument": "[n02] Because unit1 is sealed, unit2 is ready."}}

GOOD_CALLS = [
    {"tool": "freeze_target", "arguments": {"target": "t_n02", "text": "@unit2 is ready_packing_completed."}},
    {"tool": "add_node", "arguments": {"name": "fact", "text": "@unit1 is sealed.", "anchors": ["n00.1"]}},
    {"tool": "add_node", "arguments": {"name": "rule", "anchors": ["r01.1"],
                                       "text": "if (@unit1 is sealed), then (@unit2 is ready_packing_completed)."}},
    {"tool": "add_node", "arguments": {"name": "goal", "text": "@unit2 is ready_packing_completed.",
                                       "anchors": ["n02.1"], "parents": ["rule", "fact"]}},
    {"tool": "check_step", "arguments": {"name": "goal"}},
    {"tool": "waive", "arguments": {"sentence": "n00.2", "reason": "Only lists declared rule names."}},
    {"tool": "status", "arguments": {}},
]


def block(value):
    return "Plan.\n```json\n" + json.dumps(value) + "\n```"


class FakeAuthor:
    """Scripted text-protocol author: fixed cost and ceiling per turn."""

    def __init__(self, replies, cost="0.10", ceiling="0.20", parse=True):
        self.replies, self.cost, self.cap = list(replies), Decimal(cost), Decimal(ceiling)
        self.prompts = []

    def start(self, system, opening, tools=None):
        self.system, self.opening = system, opening

    def ceiling(self, history):
        return self.cap

    def turn(self, history, call_id, parse_calls=True):
        self.prompts.append(render_transcript(self.opening, history))
        text = self.replies.pop(0) if self.replies else "nothing"
        calls, error = parse_text_calls(text) if parse_calls else ([], None)
        return Turn(text, calls, self.cost, {"input_tokens": 10, "output_tokens": 5}, protocol_error=error)


def run(tmp_path, author, arm="A3", **limits):
    return SessionRun(ITEM, split="dev", author_name="opus", author=author, arm=arm, out_dir=tmp_path / arm,
                      limits=Limits(**{"budget_usd": 2.0, **limits})).run()


def test_text_protocol_parses_last_block_and_reports_errors():
    calls, error = parse_text_calls("x ```json\n{\"calls\": [{\"tool\": \"a\"}]}\n``` y ```json\n"
                                    "{\"calls\": [{\"tool\": \"status\", \"arguments\": {}}]}\n```")
    assert error is None and calls == [{"id": "c0", "name": "status", "arguments": {}}]
    assert parse_text_calls("no block")[1]
    assert parse_text_calls(block({"calls": []}))[1]
    assert parse_text_calls(block({"calls": [{"arguments": {}}]}))[1]


def test_a3_loop_success_finish_and_accounting(tmp_path):
    author = FakeAuthor([block({"calls": GOOD_CALLS}),
                         block({"calls": [{"tool": "finish", "arguments": {"verdict": "complete"}}]})])
    result = run(tmp_path, author)
    # the tool itself never counts a waiver as success; the evaluation tolerates waivers of GIVEN sentences
    assert result["stop_reason"] == "finish" and result["tool_success"] is True
    assert result["tool_success_strict"] is False and result["verification"] == {"ok": True, "problems": []}
    assert result["proposer_model"] is None
    assert result["turns"] == 2 and result["tool_calls"] == 8 and result["protocol_errors"] == 0
    assert result["spent_usd"]["total"] == "0.20"
    # the second prompt carries the first turn's results and the budget line
    assert "=== Turn 1: harness response ===" in author.prompts[1] and "[budget] spent $0.1000" in author.prompts[1]
    # the saved session ledger replays
    from ve.assist import AssistSession
    ledger = json.loads((tmp_path / "A3" / "session.json").read_text())
    session = AssistSession.from_ledger(ledger)
    assert session.usage()["tokens"]["author"]["calls"] == 2
    assert len((tmp_path / "A3" / "transcript.jsonl").read_text().splitlines()) == 2


def test_budget_stops_before_a_call_that_could_exceed_it(tmp_path):
    author = FakeAuthor([block({"calls": [{"tool": "status", "arguments": {}}]})] * 5, cost="0.6", ceiling="1.0")
    result = run(tmp_path, author, budget_usd=1.5)
    assert result["stop_reason"] == "budget" and result["turns"] == 1
    assert Decimal(result["spent_usd"]["total"]) <= Decimal("1.5")


def test_protocol_errors_turn_and_call_caps(tmp_path):
    many = block({"calls": [{"tool": "status", "arguments": {}}] * 12})
    author = FakeAuthor(["I will think first.", many, many])
    result = run(tmp_path, author, max_tool_calls=15, calls_per_turn=10)
    assert result["protocol_errors"] == 1 and result["stop_reason"] == "max_tool_calls"
    rows = [json.loads(l) for l in (tmp_path / "A3" / "transcript.jsonl").read_text().splitlines()]
    assert "TooManyCalls" in rows[1]["feedback"] and "ToolCallCap" in rows[2]["feedback"]


def test_unknown_tools_and_bad_finish_are_rejected_not_raised(tmp_path):
    author = FakeAuthor([block({"calls": [{"tool": "propose", "arguments": {"sentence": "n02.1"}},
                                          {"tool": "finish", "arguments": {"verdict": "maybe"}}]})])
    result = run(tmp_path, author, max_turns=1)
    assert result["stop_reason"] == "max_turns" and result["finish"] is None
    feedback = json.loads((tmp_path / "A3" / "transcript.jsonl").read_text().splitlines()[0])["feedback"]
    assert "UnknownTool" in feedback and "verdict" in feedback


class FakeProposer:
    model_id = "fake"

    def __init__(self):
        self.costs = []

    def ceiling(self, session, sentence, k=None, note=None):
        return Decimal("0.05")

    def __call__(self, system, prompt, item_id):
        self.costs.append(Decimal("0.01"))
        return {"text": json.dumps({"candidates": [{"ve": "@unit1 is sealed.", "reading": "fact"}]}),
                "input_tokens": 100, "output_tokens": 20, "model": "fake", "account_label": "t", "call_key": "k"}


def test_a4_proposer_is_charged_to_the_same_budget(tmp_path):
    calls = [GOOD_CALLS[0], {"tool": "propose", "arguments": {"sentence": "n00.1"}},
             {"tool": "accept", "arguments": {"candidate": "q1.1", "name": "fact", "anchors": ["n00.1"]}}]
    author = FakeAuthor([block({"calls": calls})])
    result = SessionRun(ITEM, split="dev", author_name="opus", author=author, arm="A4", out_dir=tmp_path / "A4",
                        limits=Limits(budget_usd=2.0, max_turns=1), proposer_factory=FakeProposer).run()
    assert result["spent_usd"]["proposer"] == "0.01" and result["spent_usd"]["total"] == "0.11"
    assert result["status"]["provenance"]["proposer-verbatim"] == 1
    assert "propose" in (tmp_path / "A4" / "prompt.json").read_text()
    # the fake proposer wrote no calls ledger: verify_session rejects the recorded call, so no success
    assert not result["verification"]["ok"] and result["tool_success"] is False
    assert any("calls ledger" in p for p in result["verification"]["problems"])
    assert result["proposer_model"] == "haiku" and result["account"] is None  # main account by default


def test_eval_success_tolerates_only_given_waivers():
    base = {"success": False, "failures": ["1 asserting sentence(s) waived (a waiver is reported, never success): n00.2"],
            "waivers": [{"sentence": "n00.2", "role": "given", "counts_against_success": True}]}
    assert eval_success(base) == (False, True)
    claimed = {**base, "waivers": [{"sentence": "n02.1", "role": "claimed", "counts_against_success": True}]}
    assert eval_success(claimed) == (False, False)
    other = {**base, "failures": base["failures"] + ["1 claimed sentence(s) not derived by a certified step: n02.1"]}
    assert eval_success(other) == (False, False)
    assert eval_success({"success": True, "failures": [], "waivers": []}) == (True, True)
    assert eval_success(None) == (False, False)


def test_a3_tool_list_has_no_proposer(tmp_path):
    run(tmp_path, FakeAuthor([]), max_turns=0)
    names = [t["name"] for t in json.loads((tmp_path / "A3" / "prompt.json").read_text())["tools"]]
    assert "propose" not in names and "accept" not in names and "finish" in names


def document(target="@unit2 is ready_packing_completed.", finish=None):
    doc = {"targets": {"t_n02": target},
           "nodes": [{"name": "goal", "text": "@unit2 is ready_packing_completed.", "anchors": ["n02.1"],
                      "parents": ["rule", "fact"]},
                     {"name": "fact", "text": "@unit1 is sealed.", "anchors": ["n00.1"]},
                     {"name": "rule", "anchors": ["r01.1"],
                      "text": "if (@unit1 is sealed), then (@unit2 is ready_packing_completed)."}],
           "waivers": {"n00.2": "Only lists rule names."}}
    if finish:
        doc["finish"] = finish
    return doc


def test_a2_document_evaluation_orders_nodes_and_freezes_targets():
    session, diag, frozen = evaluate_document(ITEM, document(), None, author="opus", split="dev", attempt=1)
    assert eval_success(diag["status"]) == (False, True) and not diag["node_errors"]
    assert diag["checks"] == [{"node": "goal", "status": "follows"}]
    _, diag2, frozen2 = evaluate_document(ITEM, document(target="@unit2 is ready_staffing_arranged."), frozen,
                                          author="opus", split="dev", attempt=2)
    assert frozen2 == frozen and "frozen" in diag2["note"] and eval_success(diag2["status"])[1]
    broken = document()
    broken["nodes"] = broken["nodes"][:1]
    _, diag3, _ = evaluate_document(ITEM, broken, frozen, author="opus", split="dev", attempt=3)
    assert diag3["node_errors"] and not diag3["status"]["success"]


def test_a2_loop_retries_on_diagnostics_then_stops_on_success(tmp_path):
    bad = document()
    bad["nodes"][2]["text"] = "if (@unit1 is sealed), then (@unit2 is ready_staffing_arranged)."
    author = FakeAuthor([block(bad), block(document())])
    result = run(tmp_path, author, arm="A2")
    assert result["stop_reason"] == "success" and result["turns"] == 2 and result["tool_success"]
    assert "countermodel" in author.prompts[1]
    assert (tmp_path / "A2" / "attempt-001.json").exists() and (tmp_path / "A2" / "attempt-002.json").exists()


def test_a2_finish_gap_ends_the_session(tmp_path):
    author = FakeAuthor([block(document(finish={"verdict": "gap", "gap_steps": ["goal"]}))])
    result = run(tmp_path, author, arm="A2")
    assert result["stop_reason"] == "finish" and result["finish"]["verdict"] == "gap"


def test_system_prompts_share_the_task_text():
    a2 = prompts.author_system("A2", text_protocol=True)
    a3 = prompts.author_system("A3", text_protocol=False, tools=[])
    assert prompts.TASK.strip() in a2 and prompts.TASK.strip() in a3
    assert "Tool-call protocol" not in a3 and "Tool-call protocol" in prompts.author_system(
        "A3", text_protocol=True, tools=[prompts.FINISH_TOOL])


def test_claude_list_price_uses_cache_breakdown():
    cost = claude_cost("claude-opus-5-5", {"input_tokens": 1000, "cache_creation_input_tokens": 1000,
                                           "cache_read_input_tokens": 10000, "output_tokens": 1000})
    assert cost == Decimal("0.004") + Decimal("0.005") + Decimal("0.002") + Decimal("0.02")


def test_heldout_selection_is_seeded_and_stratified():
    rows = items.heldout_items()
    labs = items.labels()
    assert [r["id"] for r in rows] == items.item_ids("heldout")
    assert len({r["group"] for r in rows}) == 12
    kinds = [labs[r["id"]]["kind"] for r in rows]
    assert sorted(kinds) == sorted(["benign", "shift", "smuggle"] * 4)
    assert not {r["id"] for r in rows} & set(items.item_ids("dev"))


def test_gemini_wiring_function_calls_and_responses(tmp_path):
    from ve_experiments.paid import Ledger, OfflineBackend, PaidClient, PaidReply
    replies = [
        [{"id": "a", "name": "freeze_target", "arguments": GOOD_CALLS[0]["arguments"]},
         {"id": "b", "name": "status", "arguments": {}}],
        [{"id": "c", "name": "finish", "arguments": {"verdict": "gap", "gap_steps": []}}],
    ]
    seen = []

    def respond(request):
        seen.append(request)
        calls = replies[len(seen) - 1]
        content = {"role": "model", "parts": [{"function_call": {"name": c["name"], "args": c["arguments"],
                                                                 "id": c["id"]}} for c in calls]}
        return PaidReply("", 1000, 10, 90, 0, "offline", {}, {"role": "assistant", "vertex_content": content}, calls,
                         "STOP")

    backend = OfflineBackend(respond)
    backend.count = lambda request: 900  # the offline backend has no tokenizer
    author = GeminiAuthor(tmp_path / "ledger.jsonl", cap_usd=1, backend=backend,
                          client=PaidClient(backend, Ledger(tmp_path / "ledger.jsonl", 1)))
    result = SessionRun(ITEM, split="dev", author_name="gemini", author=author, arm="A3", out_dir=tmp_path / "g",
                        limits=Limits(budget_usd=1.0)).run()
    assert result["stop_reason"] == "finish" and result["turns"] == 2
    assert result["spent_usd"]["author"] == str(2 * (Decimal(1000) * 2 + Decimal(100) * 12) / Decimal(10**6))
    second = seen[1].messages
    assert second[2]["vertex_content"]["parts"][0]["function_call"]["name"] == "freeze_target"
    parts = second[3]["vertex_content"]["parts"]
    assert [p["function_response"]["name"] for p in parts[:2]] == ["freeze_target", "status"]
    assert parts[2]["text"].startswith("[budget]")
    assert seen[0].tools and "parameters_json_schema" in seen[0].tools[0]
    assert vertex_tools([prompts.FINISH_TOOL])[0]["name"] == "finish"


@pytest.fixture(autouse=True)
def demo_item(monkeypatch):
    """The audit/report layer looks items up by id; the synthetic ITEM is not a registered item."""
    real = audit._item_for
    monkeypatch.setattr(audit, "_item_for", lambda result: ITEM if result["item_id"] == "demo" else real(result))


def test_audit_packet_is_blind_and_judged_conservatively(tmp_path):
    author = FakeAuthor([block({"calls": GOOD_CALLS})])
    run(tmp_path, author, max_turns=1)
    packet = audit.packet_for(tmp_path / "A3")
    text = json.dumps(packet)
    for leak in ("follows", "certified", "parents", "A3", "opus", "demo", "status", "check"):
        assert leak not in text
    kinds = {u["sentence"]: u["kind"] for u in packet["units"]}
    assert kinds == {"n00.1": "formalised", "n00.2": "waiver", "r01.1": "formalised", "n02.1": "formalised"}
    waiver = next(u for u in packet["units"] if u["kind"] == "waiver")
    assert waiver["code"] == "declared" and "Only lists" not in text  # W code, never the author's reason
    target_unit = next(u for u in packet["units"] if u["sentence"] == "n02.1")
    assert target_unit["formalisation"][0].startswith("(frozen conclusion)")
    good = {"units": [{"unit": u["unit"], "verdict": "faithful" if u["kind"] == "formalised" else "acceptable"}
                      for u in packet["units"]]}
    assert audit.judge(packet, block(good))["pass"]
    good["units"][0]["verdict"] = "unclear"
    assert not audit.judge(packet, block(good))["pass"]
    assert not audit.judge(packet, "no json")["pass"]


def test_classify_endpoints():
    status = {"targets": [{"id": "t", "text": "x", "certified": False, "reason": None}],
              "unproved_steps": [{"node": "s3"}], "unanchored_assumptions": [], "uncovered": [],
              "renamed_conclusions": []}
    clean = {"violations": [], "claimed_without_step": [], "gap_steps": ["s3"], "non_gap_uncertified": [],
             "gap_not_refuted": [], "gap_repairable_from_dossier": [], "gap_paragraphs": ["n14"]}
    loc = [["n14"], ["n15", "n14"]]
    gap = {"tool_success": False, "status": status, "finish": {"verdict": "gap", "gap_steps": ["s3"]},
           "verification": {"ok": True}}
    assert audit.classify(gap, True, "shift", clean, loc)["faithful_complete"]
    assert not audit.classify(gap, True, "benign", clean, loc)["faithful_complete"]
    assert not audit.classify(gap, True, "shift", {**clean, "gap_paragraphs": ["n02"]}, loc)["faithful_complete"]
    assert not audit.classify({**gap, "verification": {"ok": False}}, True, "shift", clean, loc)["faithful_complete"]
    done = {"tool_success": True, "status": {**status, "unproved_steps": []}, "finish": None,
            "verification": {"ok": True}}
    assert audit.classify(done, False, "benign", clean, loc)["certified_unfaithful"]
    assert audit.classify(done, True, "smuggle", clean, loc)["flawed_certified_alarm"]
    # a dossier violation voids tool success
    assert not audit.classify(done, True, "benign", {**clean, "violations": ["waiver outside W: r1"]},
                              loc)["tool_success"]
    assert audit.auditors_for("opus") == ["codex"] and audit.auditors_for("gemini") == ["codex", "opus"]
    # an unaudited certified session is not counted as certified-unfaithful
    assert not audit.classify(done, False, "benign", clean, loc, audited=False)["certified_unfaithful"]


class FakeCompleted:
    def __init__(self, returncode, stdout, stderr):
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr


def codex_stdout(*items, usage=None):
    rows = [{"type": "thread.started", "thread_id": "t-1"}, {"type": "turn.started"}]
    rows += [{"type": "item.completed", "item": item} for item in items]
    rows.append({"type": "turn.completed", "usage": usage or {"input_tokens": 12000, "output_tokens": 345}})
    return "\n".join(json.dumps(r) for r in rows) + "\n"


def test_codex_auditor_pins_the_model_isolates_the_packet_and_replays(tmp_path):
    seen = []

    def runner(cmd, **kw):
        work = Path(cmd[cmd.index("-C") + 1])
        seen.append((cmd, kw, sorted(p.name for p in work.iterdir()), (work / "packet.json").read_text()))
        Path(cmd[cmd.index("-o") + 1]).write_text('{"units": []}')
        return FakeCompleted(0, codex_stdout({"type": "agent_message", "text": "{}"}),
                             "model: gpt-6-astra\nsandbox: read-only\n")

    auditor = audit.CodexAuditor(tmp_path / "codex.jsonl", runner=runner)
    text, cost, row = auditor.single("assist-audit/p1", "SYS", "PROMPT\n\nPACKET:\n{\"units\": []}")
    assert text == '{"units": []}' and cost == 0
    assert row["served_model"] == "gpt-6-astra" and row["tokens_used"] == 12345
    assert "turn.completed" in row["stdout"]  # the --json events are kept for checking
    cmd, kw, listing, packet = seen[0]
    assert cmd[:5] == ["codex", "exec", "-m", "gpt-6-astra", "-s"] and "--json" in cmd
    # a fresh temporary directory holding ONLY the packet: no run directory, mapping.json or labels
    assert listing == ["packet.json"] and packet == '{"units": []}'
    assert kw["cwd"] == Path(cmd[cmd.index("-C") + 1]) and "assist-eval" not in str(kw["cwd"])
    assert kw["stdin"] is not None and "SYS" in cmd[-1]
    auditor.single("assist-audit/p1", "SYS", "PROMPT\n\nPACKET:\n{\"units\": []}")  # replays from the ledger
    assert len(seen) == 1

    def failing(cmd, **kw):
        return FakeCompleted(1, "", "error: usage limit")
    with pytest.raises(RuntimeError):
        audit.CodexAuditor(tmp_path / "c2.jsonl", runner=failing).single("x", "S", "P")


def test_codex_auditor_rejects_another_model_and_voids_tool_use(tmp_path):
    def reply(stdout, stderr):
        def runner(cmd, **kw):
            Path(cmd[cmd.index("-o") + 1]).write_text('{"units": []}')
            return FakeCompleted(0, stdout, stderr)
        return runner

    ok_events = codex_stdout({"type": "agent_message", "text": "{}"})
    for stdout, stderr in ((ok_events, "model: gpt-5.6-sol\n"),  # a different model: rejected
                           (ok_events, ""),                          # no reported model: rejected
                           (codex_stdout({"type": "command_execution", "command": "cat mapping.json"},
                                         {"type": "agent_message", "text": "{}"}), "model: gpt-6-astra\n")):
        ledger = tmp_path / f"c{len(stdout)}{len(stderr)}.jsonl"
        auditor = audit.CodexAuditor(ledger, runner=reply(stdout, stderr), sessions=tmp_path / "none")
        with pytest.raises(audit.AuditorViolation):
            auditor.single("x", "S", "P")
        rows = [json.loads(l) for l in ledger.read_text().splitlines()]
        assert rows[-1]["status"] == "void" and rows[-1]["stdout"] == stdout
    # the model can also come from the session rollout named by the thread id
    rollout = tmp_path / "sessions" / "2026" / "rollout-2026-t-1.jsonl"
    rollout.parent.mkdir(parents=True)
    rollout.write_text(json.dumps({"type": "turn_context", "payload": {"model": "gpt-6-astra"}}) + "\n")
    auditor = audit.CodexAuditor(tmp_path / "r.jsonl", runner=reply(ok_events, ""), sessions=tmp_path / "sessions")
    assert auditor.single("x", "S", "P")[2]["served_model"] == "gpt-6-astra"


class ScriptedAuditor:
    def __init__(self, reply=None, fail=False):
        self.reply, self.fail = reply, fail

    def single(self, call_id, system, prompt):
        if self.fail:
            raise RuntimeError("ledger halted")
        return self.reply(prompt), Decimal(0), {"served_model": "scripted", "tokens_used": 7}


def _packet_units(prompt):
    return json.loads(prompt.split("PACKET:\n", 1)[1])["units"]


def test_audit_run_logs_errors_and_report_attributes_failures(tmp_path):
    run_dir = tmp_path / "run"
    calls = [GOOD_CALLS[0], {"tool": "propose", "arguments": {"sentence": "n00.1"}},
             {"tool": "accept", "arguments": {"candidate": "q1.1", "name": "fact", "anchors": ["n00.1"]}}]
    out = run_dir / "dev" / "opus" / "A4" / "demo"
    SessionRun(ITEM, split="dev", author_name="opus", author=FakeAuthor([block({"calls": calls})]), arm="A4",
               out_dir=out, limits=Limits(budget_usd=2.0, max_turns=1), proposer_factory=FakeProposer).run()
    assert audit.export(run_dir) == 1
    # an auditor failure leaves no verdict and is logged
    assert audit.run_audit(run_dir, auditors={"codex": ScriptedAuditor(fail=True)}) == 1
    assert "ledger halted" in (run_dir / "audit" / "errors.jsonl").read_text()
    # the auditor rejects the proposer-accepted fact: attributed to the proposer
    reply = lambda prompt: block({"units": [
        {"unit": u["unit"], "verdict": "unfaithful" if u["sentence"] == "n00.1" else
         "faithful" if u["kind"] == "formalised" else "acceptable"} for u in _packet_units(prompt)]})
    assert audit.run_audit(run_dir, auditors={"codex": ScriptedAuditor(reply)}) == 0
    verdict = json.loads(next((run_dir / "audit" / "verdicts").glob("*.json")).read_text())
    assert verdict["auditor"] == "codex" and verdict["auditor_model"] == "scripted" and not verdict["pass"]
    import ve_experiments.assist_eval.audit as mod
    original = mod.labels
    mod.labels = lambda: {"demo": {"kind": "benign", "acceptable_locations": []}}
    try:
        row = audit.report(run_dir)["rows"][0]
    finally:
        mod.labels = original
    assert row["attribution"] == "ledger-verification"  # the fake proposer has no calls ledger
    failing = row["failing_units"]
    # n00.1 was the proposer's; r01.1 was omitted and is outside W (fails deterministically, no origin)
    assert {u["sentence"]: u["origins"] for u in failing.values()} == {"n00.1": ["proposer-verbatim"], "r01.1": []}
    cls = {"faithful_complete": False, "flawed_certified_alarm": False, "kind": "benign", "violations": []}
    ok = {"stop_reason": "finish", "verification": {"ok": True}}
    assert audit.attribute(ok, {"pass": False}, cls, failing) == "audit-fail: proposer candidate accepted unchanged"
    hand = {"u9": {"verdict": "unfaithful", "origins": ["hand-written"]}}
    assert audit.attribute(ok, {"pass": False}, cls, hand) == "audit-fail: author-written"
    unclear = {"u9": {"verdict": "unclear", "origins": ["hand-written"]}}
    assert audit.attribute(ok, {"pass": False}, cls, unclear).startswith("audit-fail: audit disagreement")
    assert audit.attribute({**ok, "stop_reason": "budget"}, {"pass": True}, cls, {}) == "budget"
    assert audit.attribute(ok, {"pass": True}, cls, {}) == "tool refusal"
    empty = {"pass": False, "problems": [{"unit": None, "verdict": None, "reason": "empty packet"}]}
    assert audit.attribute(ok, empty, cls, {}) == "author: nothing formalised"
    assert audit.attribute({**ok, "stop_reason": "abort: x"}, None, cls, {}) == "infrastructure"


def test_empty_packet_fails_without_an_auditor_call(tmp_path):
    run_dir = tmp_path / "run"
    out = run_dir / "dev" / "gemini" / "A3" / "demo"
    SessionRun(ITEM, split="dev", author_name="gemini", author=FakeAuthor([]), arm="A3", out_dir=out,
               limits=Limits(budget_usd=2.0, max_turns=0)).run()
    audit.export(run_dir)
    never = ScriptedAuditor(reply=lambda prompt: pytest.fail("an empty packet must not reach an auditor"))
    assert audit.run_audit(run_dir, auditors={"codex": never, "opus": never}) == 0
    verdicts = [json.loads(p.read_text()) for p in (run_dir / "audit" / "verdicts").glob("*.json")]
    # a Gemini packet needs both auditors; an empty packet fails for each without a call
    assert sorted(v["auditor"] for v in verdicts) == ["codex", "opus"]
    assert all(v["pass"] is False and v["auditor_model"] is None for v in verdicts)


def test_gemini_margin_covers_undercounted_tool_declarations():
    # dev-tune-1: counted ~3.5k, billed 4,004 -> the old 2% + 256 margin halted the run ledger
    assert GeminiAuthor._margin(3520) >= 4004 and GeminiAuthor._margin(6345) >= 9337


def test_finish_complete_is_refused_until_status_succeeds(tmp_path):
    author = FakeAuthor([block({"calls": [{"tool": "finish", "arguments": {"verdict": "complete"}}]}),
                         block({"calls": [{"tool": "finish", "arguments": {"verdict": "gap", "gap_steps": []}}]})])
    result = run(tmp_path, author)
    rows = [json.loads(l) for l in (tmp_path / "A3" / "transcript.jsonl").read_text().splitlines()]
    assert "NotComplete" in rows[0]["feedback"] and result["finish"]["verdict"] == "gap" and result["turns"] == 2


def test_a2_finish_complete_on_a_failing_document_is_refused(tmp_path):
    bad = document(finish={"verdict": "complete"})
    bad["nodes"] = bad["nodes"][:1]
    author = FakeAuthor([block(bad)], ceiling="0.2")
    result = run(tmp_path, author, arm="A2", max_turns=1)
    assert result["finish"] is None and "finish_refused" in author.prompts[0] + (
        tmp_path / "A2" / "transcript.jsonl").read_text()
