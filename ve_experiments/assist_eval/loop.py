"""Budgeted authoring loop for one (item, author, arm) session.

Arms (PLAN-ASSIST "After review"; A1 is the existing P5 one-shot result):
  A2  checker-feedback-only: the author writes the WHOLE graph as one JSON
      document each turn; the harness builds a fresh session from it (targets
      frozen from the first document that freezes), checks every step and
      returns diagnostics; repeat until success, "finish", or budget.
  A3  interactive ve assist tools, no proposer, premise suggestions off.
  A4  full tool: A3 + the proposer (propose/accept; Haiku 4.5 by default,
      ``proposer_model``); premise suggestions off.

Every session's final ledger (and every A2 attempt ledger) is checked with
``ve.assist.verify_session`` against the dossier, the arm's options and the
session's dedicated proposer calls ledger; a ledger that does not verify is
never a tool success.

Evaluation success rule (``scoring.eval_success``). The fixed tool reports any
waiver of an asserting sentence as "never success". Every P5 dossier has given
sentences that no VE statement states faithfully ("Rules r00, r14 are
declared.", "The checks that ... remain unassumed.", "The sample from lot ...").
``tool_success`` in this evaluation is therefore: the tool's status is success,
OR its ONLY failure is the waiver line and every waived sentence is in the
preregistered allowlist W(item) (``dossier.py``, hashed as ``waivers.json``),
AND the dossier graph checks pass (no anchor on a waive-only sentence, every
given-anchored assumption states its anchor's content, no assumed "remain
unassumed" check). ``tool_success_strict`` records the tool's own verdict.

Budget (identical for every arm and author): a hard per-item dollar cap on
TOTAL spend (author + proposer) over EVERY attempt at the item: a session
restarted after an infrastructure abort starts with the aborted attempts'
spend already charged (``prior_spent``), and an item whose budget is exhausted
stops ("budget"); it is never reset. Before each author call the harness
computes that call's worst-case cost (all input uncached, full output
allowance) and stops if spent + ceiling would exceed the cap; proposer calls are
gated the same way. Turn and tool-call caps are secondary safety limits.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from decimal import Decimal
import json
import os
from pathlib import Path
import time

from ve.assist import AssistSession, call_tool, source_from_p5, tool_schemas, verify_session
from ve.assist.proposer import build_prompt

from . import dossier, prompts
from .authors import AuthorAbort, GeminiAuthor, last_json_block
from .pricing import ceiling as price_ceiling, claude_cost
from .scoring import WAIVER_FAILURE, eval_success as _eval_success

ARMS = {"A2": {"tools": False, "proposer": False},
        "A3": {"tools": True, "proposer": False},
        "A4": {"tools": True, "proposer": True}}
MAX_RESULT_CHARS = 8000
ARM_OPTIONS = {"premise_suggestions": False}
DEFAULT_PROPOSER = "haiku"


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
                                options=dict(ARM_OPTIONS), metadata=metadata)


def eval_success(status, session=None, item=None):
    """(strict, evaluation) success; see the module docstring. With ``session`` and ``item`` the waivers must
    lie in W(item) and the dossier graph checks must pass."""
    if session is None or item is None:
        return _eval_success(status)
    return _eval_success(status, dossier.graph_violations(session, item), dossier.allowlist(item))


def neutral_violations(session, item, status):
    """Violations the author may see during a session. Anchor and assumption checks concern only the given
    sentences' own content (flaw-neutral). Waivers outside W are shown only once they are the sole remaining
    obstacle (W marks rules whose conditions are underivable, so earlier feedback could hint at derivability)."""
    rows = dossier.graph_violations(session, item)
    shown = [v for v in rows if not v.startswith("waiver outside W")]
    if status and all(WAIVER_FAILURE.match(f) for f in status["failures"]) and not shown:
        shown = rows
    return shown


def verify_ledger(ledger, item, calls_path):
    """``verify_session`` summary for one ledger (dedicated calls ledger; a missing file is no rows)."""
    out = verify_session(ledger, item=item, options=ARM_OPTIONS, calls=str(calls_path))
    return {"ok": out["ok"], "problems": out["problems"][:20]}


def compact_status(status):
    return {"success": status["success"], "failures": status["failures"],
            "targets": [{k: t.get(k) for k in ("id", "text", "certified", "reason", "replay", "node")}
                        for t in status["targets"]],
            "unproved_steps": status["unproved_steps"],
            "unanchored_assumptions": [{k: u[k] for k in ("node", "anchor_state", "load_bearing", "needed_by")}
                                       for u in status["unanchored_assumptions"]],
            "uncovered": status["coverage"]["uncovered"], "underived": status["coverage"].get("underived", []),
            "covered": status["coverage"]["covered"], "derived": status["coverage"].get("derived"),
            "waived": status["coverage"]["waived"],
            "waivers": [{k: w[k] for k in ("sentence", "role", "counts_against_success")}
                        for w in status.get("waivers", [])],
            "renamed_conclusions": status["renamed_conclusions"], "provenance": status["provenance"]}


class CostedProposer:
    """``ClaudeProposer`` backend (``model`` haiku/sonnet/opus) that also prices each call at list price,
    including failed calls and earlier infrastructure attempts (tokens spent are always charged)."""

    def __init__(self, ledger, account, model=DEFAULT_PROPOSER, max_calls=None):
        from ve_experiments.assist_haiku import ClaudeProposer
        self.inner = ClaudeProposer(ledger, model=model, account=account, max_calls=max_calls)
        self.inner.client.infrastructure_retries = True
        self.model, self.model_id = self.inner.model, self.inner.model_id
        self.costs = []

    def secret_needles(self):
        return self.inner.secret_needles()

    def _charge_attempts(self, attempts):
        for a in attempts or []:
            self.costs.append(claude_cost(self.model_id, {"input_tokens": a.get("input_tokens") or 0,
                                                          "output_tokens": a.get("output_tokens") or 0}))

    def __call__(self, system, prompt, item_id):
        try:
            row = self.inner.client.sample(item_id, system, prompt, 0)
        except Exception as exc:
            spent = getattr(exc, "usage", None)
            if type(spent) is dict:
                self._charge_attempts([spent] if not spent.get("not_started") else [])
                self._charge_attempts(spent.get("prior_attempts"))
            raise
        self.costs.append(claude_cost(self.model_id, row["usage"]))
        self._charge_attempts(row.get("prior_attempts"))
        return {"text": row["text"], "input_tokens": row["input_tokens"], "output_tokens": row["output_tokens"],
                "model": row["served_model"], "account_label": row["account_label"], "call_key": row["key"],
                "prior_attempts": row.get("prior_attempts", [])}

    def ceiling(self, session, sentence, k=None, note=None):
        if sentence not in session.sentences:
            return Decimal(0)  # rejected before any call
        k = session.options["proposer_k"] if k is None else k
        prompt = build_prompt(session, sentence, k if k in (1, 2, 3) else 3, note)
        rounds = 1 + session.options["propose_repair_rounds"]
        return rounds * price_ceiling(self.model_id, len(prompt) // 3 + 1500 + 1500 * (rounds - 1), 2048)


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
    shown = neutral_violations(session, item, status)
    if shown:
        diag["evaluation_violations"] = shown
    return session, diag, frozen


# ------------------------------------------------------------------ the loop

class SessionRun:
    def __init__(self, item, *, split, author_name, author, arm, out_dir, limits=Limits(),
                 account=None, proposer_factory=None, proposer_model=DEFAULT_PROPOSER, restart=0,
                 prior_spent=Decimal(0)):
        if arm not in ARMS:
            raise ValueError(f"unknown arm {arm}")
        self.item, self.split, self.author_name, self.author, self.arm = item, split, author_name, author, arm
        self.out = Path(out_dir)
        self.limits = limits
        # Spend of earlier (aborted) attempts at this item counts against the same budget.
        self.spent = {"author": Decimal(0), "proposer": Decimal(0), "prior_attempts": Decimal(str(prior_spent))}
        self.turns = self.tool_calls = self.protocol_errors = 0
        self.history = []
        self.session = new_session(item, author=author_name, arm=arm, split=split)
        self.restart = restart  # > 0: fresh author call ids after an infrastructure abort (the paid ledger
        # refuses an identity whose infrastructure retries are exhausted)
        self.proposer = None
        self.account, self.proposer_model = account, proposer_model if ARMS[arm]["proposer"] else None
        self.calls_path = self.out / "proposer-calls.jsonl"
        if ARMS[arm]["proposer"]:
            factory = proposer_factory or (lambda: CostedProposer(self.calls_path, account, proposer_model))
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
        return self.spent["author"] + self.spent["proposer"] + self.spent["prior_attempts"]

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
            if args["verdict"] == "complete":
                status = self.session.apply("status")
                if not eval_success(status, self.session, self.item)[1]:
                    extra = neutral_violations(self.session, self.item, status)
                    return {"ok": False, "error": {"code": "NotComplete", "message":
                            'finish "complete" refused: status is not success (apart from permitted waivers of '
                            'given sentences) or an evaluation check fails. Remaining failures: '
                            + "; ".join(status["failures"] + extra)[:1500]}}
            self.finish = {"verdict": args["verdict"], "gap_steps": list(args.get("gap_steps") or []),
                           "note": str(args.get("note") or "")[:1000]}
            return {"ok": True, "finished": self.finish["verdict"]}
        if name == "propose" and self.proposer is not None and type(args) is dict:
            need = self.proposer.ceiling(self.session, args.get("sentence"), args.get("k"), args.get("note"))
            if not self.affordable(need):
                return self.session.log_rejection("propose", args, {
                    "code": "BudgetExhausted", "message": "not enough budget left for a proposer call"})
        before = len(self.proposer.costs) if self.proposer else 0
        result = call_tool(self.session, name, args)
        if self.proposer:
            self.spent["proposer"] += sum(self.proposer.costs[before:], Decimal(0))
        if name == "status" and type(result) is dict and result.get("ok", True) is not False:
            shown = neutral_violations(self.session, self.item, result.get("status", result))
            if shown:
                result = {**result, "evaluation_violations": shown}
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
                call_id = f"assist-eval/{self.split}/{self.author_name}/{self.arm}/{self.item['id']}/t{self.turns + 1}" + (
                    f"/restart{self.restart}" if self.restart else "")
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
            self.spent["author"] += getattr(exc, "cost", Decimal(0))  # tokens the failed call spent
        final = self.a2_session if self.arm == "A2" else self.session
        status = final.apply("status") if final is not None else None
        verification = None
        if final is not None:
            ledger = final.to_ledger()
            self._write("session.json", ledger)
            verification = verify_ledger(ledger, self.item, self.calls_path)
            if self.arm == "A2":
                bad = [p.name for p in sorted(self.out.glob("attempt-*.json"))
                       if not verify_ledger(json.loads(p.read_text(encoding="utf-8")), self.item,
                                            self.calls_path)["ok"]]
                verification["attempts_failing"] = bad
        strict, success = eval_success(status, final, self.item) if final is not None else (False, False)
        verified = bool(verification and verification["ok"])
        result = {"item_id": self.item["id"], "split": self.split, "author": self.author_name, "arm": self.arm,
                  "stop_reason": reason, "finish": self.finish, "turns": self.turns, "tool_calls": self.tool_calls,
                  "protocol_errors": self.protocol_errors,
                  "spent_usd": {k: str(v) for k, v in self.spent.items()} | {"total": str(self.total)},
                  "budget_usd": self.limits.budget_usd, "limits": asdict(self.limits),
                  "tool_success": success and verified, "tool_success_strict": strict and verified,
                  "verification": verification, "proposer_model": self.proposer_model,
                  "account": self.account,
                  "status": compact_status(status) if status else None,
                  "restart": self.restart, "prior_attempts_spent_usd": str(self.spent["prior_attempts"]),
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
            self.a2_last_success = eval_success(diag.get("status"), session, self.item)[1]
            fin = doc.get("finish")
            if type(fin) is dict and fin.get("verdict") == "complete" and not self.a2_last_success:
                diag["finish_refused"] = ('"complete" refused: this document does not pass every check '
                                          "(apart from waivers of given sentences); fix it or finish with gap")
            elif type(fin) is dict and fin.get("verdict") in ("complete", "gap"):
                self.finish = {"verdict": fin["verdict"], "gap_steps": list(fin.get("gap_steps") or []),
                               "note": str(fin.get("note") or "")[:1000]}
        self._feedback(turn, None, {"diagnostics": clip(diag, 3 * MAX_RESULT_CHARS)})
