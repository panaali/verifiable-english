"""ve_experiments.assist_eval: loop, arms, budget, text protocol, Gemini wiring, audit export (offline)."""
from decimal import Decimal
import json

import pytest

from ve_experiments.assist_eval import audit, items, prompts
from ve_experiments.assist_eval.authors import (GeminiAuthor, Turn, parse_text_calls, render_transcript,
                                                vertex_tools)
from ve_experiments.assist_eval.loop import Limits, SessionRun, evaluate_document
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
    assert result["stop_reason"] == "finish" and result["tool_success"] is True
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
    def __init__(self):
        self.costs = []

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
    assert diag["status"]["success"] and not diag["node_errors"]
    assert diag["checks"] == [{"node": "goal", "status": "follows"}]
    _, diag2, frozen2 = evaluate_document(ITEM, document(target="@unit2 is ready_staffing_arranged."), frozen,
                                          author="opus", split="dev", attempt=2)
    assert frozen2 == frozen and "frozen" in diag2["note"] and diag2["status"]["success"]
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


def test_audit_packet_is_blind_and_judged_conservatively(tmp_path):
    author = FakeAuthor([block({"calls": GOOD_CALLS})])
    run(tmp_path, author, max_turns=1)
    packet = audit.packet_for(tmp_path / "A3")
    text = json.dumps(packet)
    for leak in ("follows", "certified", "parents", "A3", "opus", "demo", "status", "check"):
        assert leak not in text
    kinds = {u["sentence"]: u["kind"] for u in packet["units"]}
    assert kinds == {"n00.1": "formalised", "n00.2": "waiver", "r01.1": "formalised", "n02.1": "formalised"}
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
    gap = {"tool_success": False, "status": status, "finish": {"verdict": "gap", "gap_steps": ["s3"]}}
    assert audit.classify(gap, True, "shift")["faithful_complete"]
    assert not audit.classify(gap, True, "benign")["faithful_complete"]
    done = {"tool_success": True, "status": {**status, "unproved_steps": []}, "finish": None}
    assert audit.classify(done, False, "benign")["certified_unfaithful"]
    assert audit.classify(done, True, "smuggle")["flawed_certified_alarm"]
    assert audit.auditor_for("opus") == "gemini" and audit.auditor_for("gemini") == "opus"
