"""Blind cross-family fidelity audit, human spot-check list, and the results report.

Export (no model calls): each finished session becomes a PACKET with the
dossier's sentences (id, role, text), the predicate glosses, and one UNIT per
asserting sentence that has a formalisation (the deterministic paraphrases of
the nodes anchored to it, plus the frozen target for a target sentence) or a
waiver (with its reason). A packet carries NO parents, check results, status,
certification, arm, author, cost or item id; packet ids are salted hashes and
the mapping stays in ``audit/mapping.json``. Packets are shuffled with a seed.

Auditor = a different family from the author: GPT-6 Astra (``codex exec``,
read-only sandbox, reasoning effort high, an empty working directory) audits
Claude authors (Opus, Haiku); Opus 5.5 (claude CLI) audits Gemini. (The design
first named Gemini 3.1 Pro as the auditor of Claude authors; the lead replaced
it on 2026-09-23 before any dev-tune-2 audit ran.) Every verdict records the
auditor and the served auditor model. A packet PASSES iff every formalised unit
is "faithful" and every waiver "acceptable"; a missing, unparseable or
"unclear" verdict, or a packet with no units, fails it (conservative). An
auditor call that errors is logged in ``audit/errors.jsonl`` and leaves no
verdict (rerun ``audit-run`` to retry); the command exits nonzero while any
packet lacks a verdict. Auditor spend is evaluation cost, not charged to the
author's budget.
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
from collections import Counter
import random
import re
import subprocess
import tempfile
import time

from ve.assist import AssistSession

from . import prompts
from .authors import ClaudeTextAuthor, last_json_block
from .items import labels

AUDIT_SEED = 20260923
SALT = "ve-assist-eval-audit@1"
SPOT_PER_PACKET = 2
A1_CITATION = ("A1 (existing P5 one-shot, Gemini 3.1 Pro, DEV only): surface VE 0/12 replay after one repair "
               "($1.145812, ve-codex experiments/P5-shifting-definitions/AUTHORING-FEASIBILITY-RESULTS.md); "
               "schema-constrained JSON 0/12 ($1.827890 probe, JSON-AUTHORING-RESULTS.md). Fidelity not assessed.")


def session_dirs(run_dir):
    return sorted(p.parent for p in Path(run_dir).glob("*/*/*/*/result.json"))


def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def packet_for(session_dir):
    ledger = session_dir / "session.json"
    if not ledger.exists():
        return None
    session = AssistSession.from_ledger(_load(ledger))  # replays and verifies every recorded result
    by_sentence = {}
    for node in session.nodes.values():
        for sid in node.anchors:
            others = [a for a in node.anchors if a != sid]
            by_sentence.setdefault(sid, []).append(session.paraphrase_formula(node.formula) + (
                f"  (also anchored to: {', '.join(others)})" if others else ""))
    units = []
    for sid in session.sentence_order:
        s = session.sentences[sid]
        if not s["asserting"]:
            continue
        formal = list(by_sentence.get(sid, []))
        for tid, row in session.targets.items():
            if row["sentence"] == sid and row["formula"] is not None:
                formal.insert(0, "(frozen conclusion) " + session.paraphrase_formula(row["formula"]))
        if formal:
            units.append({"unit": f"u{len(units) + 1}", "kind": "formalised", "sentence": sid,
                          "role": s["role"], "text": s["text"], "formalisation": formal})
        elif sid in session.waivers:
            units.append({"unit": f"u{len(units) + 1}", "kind": "waiver", "sentence": sid, "role": s["role"],
                          "text": s["text"], "waiver_reason": session.waivers[sid]})
    packet_id = "p" + hashlib.sha256((SALT + str(session_dir.resolve())).encode()).hexdigest()[:12]
    return {"packet": packet_id,
            "sentences": [{"id": sid, "role": session.sentences[sid]["role"], "text": session.sentences[sid]["text"]}
                          for sid in session.sentence_order],
            "glossary": {k: v.description for k, v in session.env.predicates.items()},
            "units": units}


def export(run_dir):
    run_dir = Path(run_dir)
    out = run_dir / "audit"
    (out / "packets").mkdir(parents=True, exist_ok=True)
    mapping = {}
    for d in session_dirs(run_dir):
        packet = packet_for(d)
        result = _load(d / "result.json")
        if packet is None:
            continue
        mapping[packet["packet"]] = {"session_dir": str(d.relative_to(run_dir)), "author": result["author"],
                                     "arm": result["arm"], "item_id": result["item_id"], "split": result["split"]}
        (out / "packets" / f"{packet['packet']}.json").write_text(json.dumps(packet, ensure_ascii=False, indent=1))
    order = sorted(mapping)
    random.Random(AUDIT_SEED).shuffle(order)
    (out / "mapping.json").write_text(json.dumps({"order": order, "packets": mapping}, indent=1))
    return len(order)


def audit_prompt(packet):
    return prompts.AUDIT_INSTRUCTIONS + "\n\nPACKET:\n" + json.dumps(packet, ensure_ascii=False, indent=1)


def auditor_for(author):
    return "codex" if author in ("opus", "haiku") else "opus"


class CodexAuditor:
    """GPT-6 Astra through ``codex exec`` (headless, read-only sandbox, no stdin, empty working directory).

    Every call is ledgered (prompt digest, served model from the CLI header, tokens used, exit code, reply);
    a completed call with the same key replays from the ledger at no cost. Codex runs on a subscription:
    tokens are recorded, dollars are not priced (``cost_usd`` 0)."""

    ARGS = ("exec", "-s", "read-only", "-c", "model_reasoning_effort=high", "--skip-git-repo-check")
    NOTE = "\n\nAnswer from this message alone: do not run commands or read files."

    def __init__(self, ledger, *, workdir="/private/tmp/ve-assist-audit-codex-empty", timeout_s=1200,
                 runner=subprocess.run):
        self.ledger, self.workdir, self.timeout_s, self.runner = Path(ledger), Path(workdir), timeout_s, runner

    def _rows(self):
        if not self.ledger.exists():
            return []
        return [json.loads(l) for l in self.ledger.read_text(encoding="utf-8").splitlines() if l.strip()]

    def _append(self, row):
        self.ledger.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    def single(self, call_id, system, prompt):
        text = system + "\n\n" + prompt + self.NOTE
        key = hashlib.sha256(json.dumps([call_id, text, self.ARGS]).encode()).hexdigest()
        done = [r for r in self._rows() if r.get("key") == key and r.get("status") == "ok"]
        if done:
            return done[-1]["text"], Decimal(0), done[-1]
        self.workdir.mkdir(parents=True, exist_ok=True)
        self._append({"key": key, "call_id": call_id, "status": "started",
                      "time": datetime.now(timezone.utc).isoformat()})
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "reply.txt"
            start = time.monotonic()
            proc = self.runner(["codex", *self.ARGS, "-o", str(out), text], cwd=self.workdir,
                               stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=self.timeout_s)
            reply = out.read_text(encoding="utf-8") if out.exists() else ""
        log = (proc.stdout or "") + "\n" + (proc.stderr or "")
        model = re.search(r"^model: (\S+)", log, re.M)
        tokens = re.search(r"tokens used\s*\n\s*([\d,]+)", log)
        row = {"key": key, "call_id": call_id, "prompt_sha256": hashlib.sha256(text.encode()).hexdigest(),
               "served_model": model[1] if model else None,
               "tokens_used": int(tokens[1].replace(",", "")) if tokens else None,
               "returncode": proc.returncode, "elapsed_s": round(time.monotonic() - start, 1),
               "text": reply, "status": "ok" if proc.returncode == 0 and reply.strip() else "error",
               "time": datetime.now(timezone.utc).isoformat()}
        if row["status"] != "ok":
            row["log_tail"] = log[-1500:]
        self._append(row)
        if row["status"] != "ok":
            raise RuntimeError(f"codex exec failed (exit {proc.returncode}): {log[-300:]}")
        return reply, Decimal(0), row


def judge(packet, reply_text):
    value, error = last_json_block(reply_text)
    expected = {u["unit"]: u["kind"] for u in packet["units"]}
    sentence_of = {u["unit"]: u["sentence"] for u in packet["units"]}
    rows = [] if error else value.get("units") if isinstance(value.get("units"), list) else []
    verdicts = {r.get("unit"): r for r in rows if isinstance(r, dict)}
    problems = []
    for uid, kind in expected.items():
        v = verdicts.get(uid, {}).get("verdict")
        ok = v == "faithful" if kind == "formalised" else v == "acceptable"
        if not ok:
            problems.append({"unit": uid, "sentence": sentence_of[uid], "kind": kind, "verdict": v,
                             "reason": verdicts.get(uid, {}).get("reason")})
    return {"pass": bool(expected) and not problems and not error, "problems": problems,
            "units": {u: verdicts.get(u) for u in expected}, **({"error": error} if error else {})}


def make_auditor(who, out, account):
    if who == "codex":
        return CodexAuditor(out / "codex-audit-calls.jsonl")
    # one calls ledger per Claude account (the endpoint refuses mixed accounts in one ledger)
    name = "opus-audit-calls.jsonl" if account == "saeedi.danial" else f"opus-audit-calls.{account or 'main'}.jsonl"
    return ClaudeTextAuthor("opus", out / name, account=account)


def run_audit(run_dir, *, account=None, auditors=None):
    """Audit every exported packet that has no verdict yet; return the number still missing a verdict."""
    run_dir = Path(run_dir)
    out = run_dir / "audit"
    mapping = _load(out / "mapping.json")
    (out / "verdicts").mkdir(exist_ok=True)
    auditors = dict(auditors or {})
    missing = 0
    for pid in mapping["order"]:
        target = out / "verdicts" / f"{pid}.json"
        if target.exists():
            continue
        packet = _load(out / "packets" / f"{pid}.json")
        who = auditor_for(mapping["packets"][pid]["author"])
        if not packet["units"]:  # nothing was formalised or waived: fails without an auditor call
            verdict = {"packet": pid, "auditor": None, "auditor_model": None, "cost_usd": "0", "reply": None,
                       "pass": False, "problems": [{"unit": None, "verdict": None, "reason": "empty packet"}],
                       "units": {}}
            target.write_text(json.dumps(verdict, ensure_ascii=False, indent=1))
            continue
        try:
            if who not in auditors:
                auditors[who] = make_auditor(who, out, account)
            text, cost, row = auditors[who].single(f"assist-audit/{pid}", prompts.AUDIT_SYSTEM,
                                                   audit_prompt(packet))
        except Exception as exc:  # logged; the packet stays unaudited and a rerun retries it
            missing += 1
            with (out / "errors.jsonl").open("a", encoding="utf-8") as f:
                f.write(json.dumps({"packet": pid, "auditor": who, "error": f"{type(exc).__name__}: {exc}"[:2000],
                                    "time": datetime.now(timezone.utc).isoformat()}) + "\n")
            continue
        model = (row or {}).get("served_model") if isinstance(row, dict) else None
        verdict = {"packet": pid, "auditor": who, "auditor_model": model, "cost_usd": str(cost), "reply": text,
                   **({"auditor_tokens": row.get("tokens_used")} if isinstance(row, dict) and "tokens_used" in row
                      else {}),
                   **judge(packet, text)}
        target.write_text(json.dumps(verdict, ensure_ascii=False, indent=1))
    return missing


# ------------------------------------------------------------------ report

def _paragraphs(session_dir, steps):
    ledger = session_dir / "session.json"
    if not ledger.exists():
        return set()
    session = AssistSession.from_ledger(_load(ledger), verify=False)
    found = set()
    for name in steps:
        node = session.nodes.get(name)
        if node:
            found |= {a.split(".")[0] for a in node.anchors if session.sentences[a]["role"] == "claimed"}
    return found


def unit_origins(session_dir, verdict):
    """For each failing unit: the provenance of the formal statements shown for its sentence."""
    ledger = session_dir / "session.json"
    if verdict is None or not ledger.exists():
        return {}
    session = AssistSession.from_ledger(_load(ledger), verify=False)
    out = {}
    for problem in verdict.get("problems", []):
        sid = problem.get("sentence")
        if sid is None:
            continue
        origins = [n.origin for n in session.nodes.values() if sid in n.anchors]
        origins += [row.get("origin", "hand-written") for row in session.targets.values()
                    if row["sentence"] == sid and row["formula"] is not None]
        out[problem["unit"]] = {"sentence": sid, "kind": problem.get("kind"), "verdict": problem.get("verdict"),
                                "origins": sorted(set(origins))}
    return out


def attribute(result, verdict, cls, origins):
    """One cause per non-faithful-complete session (see README "Failure attribution")."""
    if cls["faithful_complete"]:
        return None
    stop = str(result.get("stop_reason"))
    if stop.startswith(("abort: run cap", "abort: context")):
        return "budget"
    if stop.startswith("abort"):
        return "infrastructure"
    if not (result.get("verification") or {}).get("ok"):
        return "ledger-verification"
    if verdict is None:
        return "unaudited"
    if not verdict["pass"]:
        if any(p.get("reason") == "empty packet" for p in verdict.get("problems", [])):
            return "author: nothing formalised"
        rows = list(origins.values())
        if any("proposer-verbatim" in r["origins"] for r in rows):
            return "audit-fail: proposer candidate accepted unchanged"
        if rows and all(r["verdict"] in (None, "unclear") for r in rows):
            return "audit-fail: audit disagreement (unclear/missing verdicts)"
        if not rows:
            return "audit-fail: audit disagreement (unclear/missing verdicts)"
        return "audit-fail: author-written"
    if cls["flawed_certified_alarm"]:
        return "alarm: flawed item certified"
    if stop in ("budget", "max_turns", "max_tool_calls"):
        return "budget"
    return "tool refusal"


def classify(result, audit_pass, kind, audited=True):
    status = result.get("status") or {}
    tool = bool(result.get("tool_success"))
    unproved = {r["node"] for r in status.get("unproved_steps", [])}
    finish = result.get("finish") or {}
    target_stated = all(t.get("reason") != "no step node states the frozen target" and t.get("text")
                        for t in status.get("targets", [])) and bool(status.get("targets"))
    gap_route = (finish.get("verdict") == "gap" and bool(unproved) and unproved <= set(finish.get("gap_steps", []))
                 and target_stated and not status.get("uncovered")
                 and not any(w.get("role") == "claimed" for w in status.get("waivers", []))
                 and not any(u["load_bearing"] for u in status.get("unanchored_assumptions", []))
                 and not status.get("renamed_conclusions"))
    certified_faithful = tool and audit_pass
    faithful_complete = certified_faithful if kind == "benign" else (audit_pass and gap_route and not tool)
    return {"tool_success": tool, "audit_pass": audit_pass, "certified_faithful": certified_faithful,
            "certified_unfaithful": tool and audited and not audit_pass, "gap_route": gap_route,
            "faithful_complete": faithful_complete, "flawed_certified_alarm": tool and kind != "benign"}


def report(run_dir):
    run_dir = Path(run_dir)
    mapping = _load(run_dir / "audit" / "mapping.json")["packets"] if (run_dir / "audit" / "mapping.json").exists() else {}
    by_dir = {v["session_dir"]: k for k, v in mapping.items()}
    labs = labels()
    rows, spot = [], []
    rng = random.Random(AUDIT_SEED)
    for d in session_dirs(run_dir):
        result = _load(d / "result.json")
        pid = by_dir.get(str(d.relative_to(run_dir)))
        verdict_path = run_dir / "audit" / "verdicts" / f"{pid}.json"
        verdict = _load(verdict_path) if pid and verdict_path.exists() else None
        kind = labs[result["item_id"]]["kind"]
        cls = classify(result, bool(verdict and verdict["pass"]), kind, audited=verdict is not None)
        origins = unit_origins(d, verdict)
        row = {**{k: result[k] for k in ("split", "author", "arm", "item_id", "stop_reason", "turns", "tool_calls")},
               "kind": kind, "spent_usd": result["spent_usd"]["total"], "audited": verdict is not None,
               "auditor": (verdict or {}).get("auditor"), "auditor_model": (verdict or {}).get("auditor_model"),
               "verified": bool((result.get("verification") or {}).get("ok")),
               "tool_success_strict": bool(result.get("tool_success_strict")),
               "proposer_model": result.get("proposer_model"), "account": result.get("account"),
               "provenance": (result.get("status") or {}).get("provenance"),
               **cls, "failing_units": origins, "attribution": attribute(result, verdict, cls, origins)}
        if kind != "benign" and (result.get("finish") or {}).get("verdict") == "gap":
            located = _paragraphs(d, result["finish"].get("gap_steps", []))
            row["gap_paragraphs"] = sorted(located)
            row["gap_located"] = any(set(loc) == located for loc in labs[result["item_id"]]["acceptable_locations"])
        rows.append(row)
        if pid:
            packet = _load(run_dir / "audit" / "packets" / f"{pid}.json")
            chosen = packet["units"] if row["tool_success"] else rng.sample(
                packet["units"], min(SPOT_PER_PACKET, len(packet["units"])))
            for unit in chosen:
                spot.append({"packet": pid, **unit, "auditor_verdict": (verdict or {}).get("units", {}).get(unit["unit"]),
                             "reason_selected": "tool-certified session" if row["tool_success"] else "random sample"})
    groups = {}
    for r in rows:
        groups.setdefault((r["split"], r["author"], r["arm"]), []).append(r)
    table = []
    for (split, author, arm), rs in sorted(groups.items()):
        n = len(rs)
        count = lambda key, sub=rs: sum(bool(r.get(key)) for r in sub)
        benign = [r for r in rs if r["kind"] == "benign"]
        table.append({"split": split, "author": author, "arm": arm, "n": n,
                      "tool_success": count("tool_success"), "audit_pass": count("audit_pass"),
                      "certified_faithful": count("certified_faithful"),
                      "certified_faithful_benign": f"{count('certified_faithful', benign)}/{len(benign)}",
                      "certified_unfaithful": count("certified_unfaithful"),
                      "faithful_complete": count("faithful_complete"),
                      "flawed_certified_alarm": count("flawed_certified_alarm"),
                      "gap_located": count("gap_located"),
                      "mean_spent_usd": round(sum(float(r["spent_usd"]) for r in rs) / n, 4),
                      "total_spent_usd": round(sum(float(r["spent_usd"]) for r in rs), 4),
                      "audited": count("audited"), "verified": count("verified"),
                      "tool_success_strict": count("tool_success_strict"),
                      "attribution": dict(sorted(Counter(r["attribution"] for r in rs if r["attribution"]).items()))})
    out = {"a1": A1_CITATION, "table": table, "rows": rows}
    (run_dir / "report.json").write_text(json.dumps(out, indent=1))
    with (run_dir / "audit-spotcheck.jsonl").open("w") as f:
        for row in spot:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return out
