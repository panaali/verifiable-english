"""Budgeted authoring loop for one (item, author, arm) session.

Arms (PLAN-ASSIST "After review"; A1 is the existing P5 one-shot result):
  A2  checker-feedback-only: the author writes the WHOLE graph as one JSON
      document each turn; the harness builds a fresh session from it (targets
      frozen from the first document that freezes), checks every step and
      returns diagnostics; repeat until success, "finish", or budget.
  A3  interactive ve assist tools, no proposer, premise suggestions off.
  A4  full tool: A3 + the Haiku 4.5 proposer (propose/accept); premise
      suggestions off.

Budget (identical for every arm and author): a hard per-item dollar cap on
TOTAL spend (author + proposer). Before each author call the harness computes
that call's worst-case cost (all input uncached, full output allowance) and
stops if spent + ceiling would exceed the cap; proposer calls are gated the
same way. Turn and tool-call caps are secondary safety limits.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from decimal import Decimal
import json
import os
from pathlib import Path
import time

from ve.assist import AssistSession, call_tool, source_from_p5, tool_schemas
from ve.assist.proposer import build_prompt

from . import prompts
from .authors import AuthorAbort, GeminiAuthor, last_json_block
from .pricing import ceiling as price_ceiling, claude_cost

ARMS = {"A2": {"tools": False, "proposer": False},
        "A3": {"tools": True, "proposer": False},
        "A4": {"tools": True, "proposer": True}}
MAX_RESULT_CHARS = 8000
HAIKU = "claude-haiku-4-5-20251001"


@dataclass
class Limits:
    budget_usd: float = 3.00
    max_turns: int = 80
    max_tool_calls: int = 300
    calls_per_turn: int = 10


# ------------------------------------------------------------------ helpers

def clip(value, limit=MAX_RESULT_CHARS):
    text = json.dumps(value, ensure_ascii=False)
    if len(text) <= limit:
        return value
    return {"truncated": True, "chars": len(text), "head": text[:limit]}


def new_session(item, *, author, arm, split):
    built = source_from_p5(item)
    metadata = {**built["metadata"], "eval": {"author": author, "arm": arm, "split": split,
                                              "prompt_version": prompts.PROMPT_VERSION}}
    return AssistSession.create(built["environment"], built["source"], built["targets"],
                                options={"premise_suggestions": False}, metadata=metadata)


def compact_status(status):
    return {"success": status["success"], "failures": status["failures"],
            "targets": [{k: t.get(k) for k in ("id", "text", "certified", "reason", "replay", "node")}
                        for t in status["targets"]],
            "unproved_steps": status["unproved_steps"],
            "unanchored_assumptions": [{k: u[k] for k in ("node", "anchor_state", "load_bearing", "needed_by")}
                                       for u in status["unanchored_assumptions"]],
            "uncovered": status["coverage"]["uncovered"],
            "covered": status["coverage"]["covered"], "waived": status["coverage"]["waived"],
            "renamed_conclusions": status["renamed_conclusions"], "provenance": status["provenance"]}


class CostedProposer:
    """HaikuProposer backend that also prices each call at list price."""

    def __init__(self, ledger, account):
        from ve_experiments.assist_haiku import HaikuProposer
        self.inner = HaikuProposer(ledger, account=account)
        self.inner.client.infrastructure_retries = True
        self.costs = []

    def __call__(self, system, prompt, item_id):
        row = self.inner.client.sample(item_id, system, prompt, 0)
        self.costs.append(claude_cost(HAIKU, row["usage"]))
        return {"text": row["text"], "input_tokens": row["input_tokens"], "output_tokens": row["output_tokens"],
                "model": row["served_model"], "account_label": row["account_label"], "call_key": row["key"]}

    @staticmethod
    def ceiling(session, sentence, k=None, note=None):
        if sentence not in session.sentences:
            return Decimal(0)  # rejected before any call
        k = session.options["proposer_k"] if k is None else k
        prompt = build_prompt(session, sentence, k if k in (1, 2, 3) else 3, note)
        rounds = 1 + session.options["propose_repair_rounds"]
        return rounds * price_ceiling(HAIKU, len(prompt) // 3 + 1500 + 1500 * (rounds - 1), 2048)


# ------------------------------------------------------------------ A2 document evaluation

def evaluate_document(item, doc, frozen, *, author, split, attempt):
    """Build a fresh session from a whole-graph document; return (session, diagnostics, frozen)."""
    session = new_session(item, author=author, arm="A2", split=split)
    diag = {"attempt": attempt}
    if type(doc) is not dict:
        diag["fatal"] = "no JSON document found in the reply"
        return session, diag, frozen
    targets = doc.get("targets") if type(doc.get("targets")) is dict else {}
    use = frozen or targets
    if frozen and targets and targets != frozen:
        diag["note"] = "targets are frozen from your first freezing document; changes were ignored"
    errors = {}
    for tid in session.targets:
        if tid not in use:
            errors[tid] = "missing target statement"
            continue
        r = session.apply("freeze_target", {"target": tid, "text": use[tid]})
        if not r["ok"]:
            errors[tid] = r["error"]["message"]
    if errors:
        diag["target_errors"] = errors
        diag["fatal"] = "every target must be frozen before nodes are checked"
        return session, diag, frozen
    frozen = frozen or {tid: use[tid] for tid in session.targets}
    rows = doc.get("nodes") if type(doc.get("nodes")) is list else []
    node_errors, pending = [], []
    for i, row in enumerate(rows):
        if type(row) is not dict or not isinstance(row.get("name"), str):
            node_errors.append({"index": i, "error": "node needs a string name"})
            continue
        pending.append(row)
    progress = True
    while pending and progress:  # add nodes once their parents exist (any document order)
        progress, rest = False, []
        waiting = {r["name"] for r in pending}
        for row in pending:
            parents = row.get("parents") if isinstance(row.get("parents"), list) else []
            if any(isinstance(p, str) and p not in session.nodes and p in waiting and p != row["name"]
                   for p in parents):
                rest.append(row)
                continue
            waiting.discard(row["name"])
            args = {k: row[k] for k in ("name", "text", "anchors", "parents") if k in row}
            r = session.apply("add_node", args)
            if not r["ok"]:
                node_errors.append({"name": row["name"], "error": r["error"]["message"]})
            progress = True
        pending = rest
    for row in pending:
        node_errors.append({"name": row["name"], "error": "parent cycle or parent never added"})
    waivers = doc.get("waivers") if type(doc.get("waivers")) is dict else {}
    for sid, reason in waivers.items():
        r = session.apply("waive", {"sentence": sid, "reason": reason})
        if not r["ok"]:
            node_errors.append({"waiver": sid, "error": r["error"]["message"]})
    checks = []
    for name, node in list(session.nodes.items()):
        if node.kind != "step":
            continue
        r = session.apply("check_step", {"name": name})
        view = {"node": name, "status": r.get("status", "error")}
        if r.get("countermodel"):
            view["countermodel"] = r["countermodel"]
        if r.get("warning"):
            view["warning"] = r["warning"]
        checks.append(view)
    status = session.apply("status")
    diag.update(node_errors=node_errors, checks=checks, status=compact_status(status))
    return session, diag, frozen


# ------------------------------------------------------------------ the loop

class SessionRun:
    def __init__(self, item, *, split, author_name, author, arm, out_dir, limits=Limits(),
                 account="saeedi.danial", proposer_factory=None):
        if arm not in ARMS:
            raise ValueError(f"unknown arm {arm}")
        self.item, self.split, self.author_name, self.author, self.arm = item, split, author_name, author, arm
        self.out = Path(out_dir)
        self.limits = limits
        self.spent = {"author": Decimal(0), "proposer": Decimal(0)}
        self.turns = self.tool_calls = self.protocol_errors = 0
        self.history = []
        self.session = new_session(item, author=author_name, arm=arm, split=split)
        self.proposer = None
        if ARMS[arm]["proposer"]:
            factory = proposer_factory or (lambda: CostedProposer(self.out / "proposer-calls.jsonl", account))
            self.proposer = factory()
            self.session.proposer = self.proposer
        self.tools = (tool_schemas(proposer=bool(self.proposer)) + [prompts.FINISH_TOOL]) if ARMS[arm]["tools"] else []
        text_protocol = not isinstance(author, GeminiAuthor)
        self.system = prompts.author_system(arm, text_protocol=text_protocol, tools=self.tools,
                                            per_turn=limits.calls_per_turn)
        self.opening = prompts.item_materials(self.session)
        self.author.start(self.system, self.opening, self.tools if not text_protocol else None)
        self.text_protocol = text_protocol
        self.finish = None
        self.a2_frozen = None
        self.a2_session = None
        self.a2_last_success = False

    # -- accounting
    @property
    def total(self):
        return self.spent["author"] + self.spent["proposer"]

    def state(self):
        return {"spent": float(self.total), "budget": self.limits.budget_usd, "tool_calls": self.tool_calls,
                "max_tool_calls": self.limits.max_tool_calls, "turns": self.turns,
                "max_turns": self.limits.max_turns}

    def affordable(self, ceiling):
        return self.total + ceiling <= Decimal(str(self.limits.budget_usd))

    # -- persistence
    def _write(self, name, value):
        path = self.out / name
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(json.dumps(value, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
        os.replace(tmp, path)

    def _log_turn(self, row):
        with (self.out / "transcript.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")

    # -- tool execution
    def _execute(self, call):
        name, args = call["name"], call["arguments"]
        if isinstance(args, str):
            try:
                args = json.loads(args) if args.strip() else {}
            except ValueError:
                pass
        if name == "finish":
            if type(args) is not dict or args.get("verdict") not in ("complete", "gap"):
                return {"ok": False, "error": {"code": "InvalidArguments",
                                               "message": 'finish needs verdict "complete" or "gap"'}}
            self.finish = {"verdict": args["verdict"], "gap_steps": list(args.get("gap_steps") or []),
                           "note": str(args.get("note") or "")[:1000]}
            return {"ok": True, "finished": self.finish["verdict"]}
        if name == "propose" and self.proposer is not None and type(args) is dict:
            need = CostedProposer.ceiling(self.session, args.get("sentence"), args.get("k"), args.get("note"))
            if not self.affordable(need):
                return self.session.log_rejection("propose", args, {
                    "code": "BudgetExhausted", "message": "not enough budget left for a proposer call"})
        before = len(self.proposer.costs) if self.proposer else 0
        result = call_tool(self.session, name, args)
        if self.proposer:
            self.spent["proposer"] += sum(self.proposer.costs[before:], Decimal(0))
        return result

    # -- turns
    def _stop_reason(self):
        if self.finish:
            return "finish"
        if self.turns >= self.limits.max_turns:
            return "max_turns"
        if self.arm != "A2" and self.tool_calls >= self.limits.max_tool_calls:
            return "max_tool_calls"
        return None

    def run(self):
        self.out.mkdir(parents=True, exist_ok=True)
        (self.out / "transcript.jsonl").write_text("", encoding="utf-8")
        self._write("prompt.json", {"system": self.system, "opening": self.opening, "tools": self.tools})
        start = time.monotonic()
        reason = None
        try:
            while reason is None:
                reason = self._stop_reason()
                if reason:
                    break
                need = self.author.ceiling(self.history)
                if not self.affordable(need):
                    reason = "budget"
                    break
                call_id = f"assist-eval/{self.split}/{self.author_name}/{self.arm}/{self.item['id']}/t{self.turns + 1}"
                turn = self.author.turn(self.history, call_id, parse_calls=self.arm != "A2")
                self.turns += 1
                self.spent["author"] += turn.cost
                self.session.apply("record_usage", {"role": "author",
                                                    "input_tokens": int(turn.usage.get("input_tokens", 0) or 0),
                                                    "output_tokens": int(turn.usage.get("output_tokens", 0) or 0)})
                if self.arm == "A2":
                    self._a2_turn(turn)
                else:
                    self._tool_turn(turn)
                    self._write("session.json", self.session.to_ledger())
                if self.arm == "A2" and self.a2_session is not None and not self.finish:
                    if self.a2_last_success:
                        reason = "success"
        except AuthorAbort as exc:
            reason = "abort: " + str(exc)
        final = self.a2_session if self.arm == "A2" else self.session
        status = final.apply("status") if final is not None else None
        if final is not None:
            self._write("session.json", final.to_ledger())
        result = {"item_id": self.item["id"], "split": self.split, "author": self.author_name, "arm": self.arm,
                  "stop_reason": reason, "finish": self.finish, "turns": self.turns, "tool_calls": self.tool_calls,
                  "protocol_errors": self.protocol_errors,
                  "spent_usd": {k: str(v) for k, v in self.spent.items()} | {"total": str(self.total)},
                  "budget_usd": self.limits.budget_usd, "limits": asdict(self.limits),
                  "tool_success": bool(status and status["success"]),
                  "status": compact_status(status) if status else None,
                  "elapsed_s": round(time.monotonic() - start, 1), "prompt_version": prompts.PROMPT_VERSION}
        self._write("result.json", result)
        return result

    def _feedback(self, turn, results, extra=None):
        """Record the turn and build the next harness message (text or function responses)."""
        budget = prompts.budget_line(self.state())
        if self.text_protocol or not turn.calls:
            body = {"results": results} if results is not None else {}
            if extra:
                body.update(extra)
            text = json.dumps(body, ensure_ascii=False) + "\n" + budget
            row = {"text": turn.text, "feedback": text}
            if not self.text_protocol:
                row.update(assistant=turn.raw["assistant"], reply_message={"role": "user", "content": text})
        else:
            message = GeminiAuthor.function_responses(turn.calls, [r["result"] for r in results])
            message["vertex_content"]["parts"].append({"text": budget})
            row = {"text": turn.text, "feedback": json.dumps(results, ensure_ascii=False) + "\n" + budget,
                   "assistant": turn.raw["assistant"], "reply_message": message}
        self.history.append(row)
        self._log_turn({"turn": self.turns, "text": turn.text, "calls": turn.calls, "usage": turn.usage,
                        "cost_usd": str(turn.cost), "protocol_error": turn.protocol_error,
                        "feedback": row["feedback"], "spent_total_usd": str(self.total)})

    def _tool_turn(self, turn):
        if turn.protocol_error:
            self.protocol_errors += 1
            self._feedback(turn, None, {"protocol_error": turn.protocol_error})
            return
        results = []
        for i, call in enumerate(turn.calls):
            if i >= self.limits.calls_per_turn:
                result = {"ok": False, "error": {"code": "TooManyCalls", "message":
                          f"at most {self.limits.calls_per_turn} calls per turn; this call was not run"}}
            elif self.finish:
                result = {"ok": False, "error": {"code": "Finished", "message": "session already finished"}}
            elif self.tool_calls >= self.limits.max_tool_calls:
                result = {"ok": False, "error": {"code": "ToolCallCap", "message": "tool-call cap reached"}}
            else:
                self.tool_calls += 1
                result = self._execute(call)
            results.append({"tool": call["name"], "result": clip(result)})
        self._feedback(turn, results)

    def _a2_turn(self, turn):
        self.a2_last_success = False
        if turn.protocol_error:
            self.protocol_errors += 1
            self._feedback(turn, None, {"protocol_error": turn.protocol_error})
            return
        doc, error = last_json_block(turn.text)
        session, diag, self.a2_frozen = evaluate_document(self.item, doc, self.a2_frozen, author=self.author_name,
                                                          split=self.split, attempt=self.turns)
        if doc is None:
            self.protocol_errors += 1
            diag["fatal"] = error
        else:
            self.a2_session = session
            self._write(f"attempt-{self.turns:03d}.json", session.to_ledger())
            self.a2_last_success = bool(diag.get("status", {}).get("success"))
            fin = doc.get("finish")
            if type(fin) is dict and fin.get("verdict") in ("complete", "gap"):
                self.finish = {"verdict": fin["verdict"], "gap_steps": list(fin.get("gap_steps") or []),
                               "note": str(fin.get("note") or "")[:1000]}
        self._feedback(turn, None, {"diagnostics": clip(diag, 3 * MAX_RESULT_CHARS)})
