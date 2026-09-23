"""Blind cross-family fidelity audit, human spot-check list, and the results report.

Export (no model calls): each finished session becomes a PACKET with the
dossier's sentences (id, role, text), the dossier's predicate glossary (any
predicate the author declared is listed apart, under "author_declared", marked
as author text), and one UNIT per asserting sentence:
* ``formalised``: the deterministic paraphrases of the nodes anchored to it
  (plus the frozen target for a target sentence) and, for steps, the sentence
  ids their parents are anchored to ("reasons");
* ``waiver``: the sentence was waived; the unit shows its allowlist CODE and
  the code's fixed description (never the author's free-text reason);
* ``omitted``: neither formalised nor waived; shows its code, if any.
A packet carries NO check results, status, certification, arm, author, cost or
item id; packet ids are salted hashes and the mapping stays in
``audit/mapping.json``. Packets are shuffled with a seed.

Auditors: GPT-6 Astra (``codex exec``, read-only sandbox, reasoning effort
high, an empty working directory) audits EVERY packet; Opus 5.5 (claude CLI,
main account) additionally audits the packets of Gemini-authored sessions.
Verdicts are ``audit/verdicts/<packet>.<auditor>.json``. A packet PASSES iff
every required auditor passes it; an auditor passes it iff every formalised
unit is "faithful" and every waiver/omitted unit "acceptable" (a waiver outside
W or an omitted sentence without a code fails deterministically); a missing,
unparseable or "unclear" verdict, or a packet with no units, fails it
(conservative). An auditor call that errors is logged in
``audit/errors.jsonl`` and leaves no verdict (rerun ``audit-run`` to retry);
the command exits nonzero while any packet lacks a required verdict. Auditor
spend is evaluation cost, not charged to the author's budget.
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
from collections import Counter
from functools import lru_cache
import random
import re
import subprocess
import tempfile
import time

from ve.assist import AssistSession

from . import dossier, prompts
from .authors import ClaudeTextAuthor, last_json_block
from .items import items as load_items, labels
from .scoring import gap_route, session_checks

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


@lru_cache(maxsize=None)
def _items_by_id(split):
    return {i["id"]: i for i in load_items(split)}


def _item_for(result):
    return _items_by_id(result["split"])[result["item_id"]]


def support_sentences(session, name, seen=None):
    """The sentence ids a step's derivation rests on: its parents' anchors, following UNANCHORED parents
    (helpers) down to the anchored nodes they rest on, so a helper cannot hide the reasoning."""
    seen = set() if seen is None else seen
    out = set()
    for p in session.nodes[name].parents:
        if p in seen or p not in session.nodes:
            continue
        seen.add(p)
        parent = session.nodes[p]
        out |= set(parent.anchors) if parent.anchors else support_sentences(session, p, seen)
    return out


def packet_for(session_dir, item=None):
    ledger = session_dir / "session.json"
    if not ledger.exists():
        return None
    session = AssistSession.from_ledger(_load(ledger))  # replays and verifies every recorded result
    item = item or _item_for(_load(session_dir / "result.json"))
    allow = dossier.allowlist(item)
    # The COMPLETE node graph under neutral ids (author node names are not shown): every node, anchored or
    # not, its statement, its anchors and the nodes it is derived from. No check result or status.
    ids = {name: f"N{i}" for i, name in enumerate(session.nodes, 1)}
    graph = [{"id": ids[n.name], "kind": n.kind, "statement": session.paraphrase_formula(n.formula),
              "anchors": list(n.anchors), **({"derived_from": [ids[p] for p in n.parents if p in ids]}
                                             if n.parents else {})}
             for n in session.nodes.values()]
    by_sentence, reasons = {}, {}
    for node in session.nodes.values():
        for sid in node.anchors:
            others = [a for a in node.anchors if a != sid]
            by_sentence.setdefault(sid, []).append(f"[{ids[node.name]}] " + session.paraphrase_formula(node.formula) + (
                f"  (also anchored to: {', '.join(others)})" if others else ""))
            if node.parents:
                reasons.setdefault(sid, set()).update(support_sentences(session, node.name))
    units = []
    for sid in session.sentence_order:
        s = session.sentences[sid]
        if not s["asserting"]:
            continue
        formal = list(by_sentence.get(sid, []))
        for tid, row in session.targets.items():
            if row["sentence"] == sid and row["formula"] is not None:
                formal.insert(0, "(frozen conclusion) " + session.paraphrase_formula(row["formula"]))
        base = {"unit": f"u{len(units) + 1}", "sentence": sid, "role": s["role"], "text": s["text"]}
        code = allow.get(sid)
        coded = {"code": code, "code_description": dossier.W_CODES[code]} if code else {"code": None}
        if sid in session.waivers:
            units.append({**base, "kind": "waiver", **coded})
        elif formal:
            units.append({**base, "kind": "formalised", "formalisation": formal,
                          **({"reasons": sorted(reasons[sid] - {sid})} if reasons.get(sid) else {})})
        else:
            units.append({**base, "kind": "omitted", **coded})
    packet_id = "p" + hashlib.sha256((SALT + str(session_dir.resolve())).encode()).hexdigest()[:12]
    public = session.config["environment"]["vocabulary"]["predicates"]
    declared = {k: v.description for k, v in session.env.predicates.items() if k not in public}
    return {"packet": packet_id,
            "sentences": [{"id": sid, "role": session.sentences[sid]["role"], "text": session.sentences[sid]["text"]}
                          for sid in session.sentence_order],
            "glossary": {k: v["description"] for k, v in public.items()},
            **({"author_declared": {k: "AUTHOR-WRITTEN gloss (not dossier text): " + v
                                    for k, v in declared.items()}} if declared else {}),
            "nodes": graph,
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


def auditors_for(author):
    """Codex audits every packet; Opus additionally audits Gemini-authored packets."""
    return ["codex", "opus"] if author == "gemini" else ["codex"]


CODEX_MODEL = "gpt-6-astra"  # GPT-6 Astra, pinned with -m; any other reported model is rejected
CODEX_SESSIONS = Path.home() / ".codex" / "sessions"
QUIET_ITEMS = {"agent_message", "reasoning"}  # the only event items a text-only audit may produce


class AuditorViolation(RuntimeError):
    """The auditor call is not a valid audit (wrong or unknown model, or it used a tool): no verdict."""


def codex_events(stdout):
    rows = []
    for line in (stdout or "").splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                value = json.loads(line)
            except ValueError:
                continue
            if isinstance(value, dict):
                rows.append(value)
    return rows


def _find_key(value, key):
    if isinstance(value, dict):
        for k, v in value.items():
            if k == key and isinstance(v, str):
                yield v
            else:
                yield from _find_key(v, key)
    elif isinstance(value, list):
        for v in value:
            yield from _find_key(v, key)


def codex_tool_uses(events):
    """Every event item that is not a message or reasoning (a command, file change, MCP or web call...)."""
    out = []
    for e in events:
        item = e.get("item")
        if isinstance(item, dict) and item.get("type") not in QUIET_ITEMS:
            out.append(str(item.get("type")))
    return out


def codex_served_model(stderr, events, sessions=CODEX_SESSIONS):
    """The model the CLI reports: the stderr header, else any "model" field of the JSON events, else the
    session rollout named by the thread id (turn_context.model). None when nothing reports it."""
    models = re.findall(r"^model: (\S+)", stderr or "", re.M) + [m for e in events for m in _find_key(e, "model")]
    thread = next((e.get("thread_id") for e in events if e.get("type") == "thread.started"), None)
    if not models and thread and Path(sessions).exists():
        for path in Path(sessions).glob(f"**/rollout-*{thread}.jsonl"):
            for line in path.read_text(encoding="utf-8").splitlines():
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if row.get("type") == "turn_context" and isinstance(row.get("payload", {}).get("model"), str):
                    models.append(row["payload"]["model"])
    models = sorted(set(models))
    return models[0] if len(models) == 1 else (None if not models else "MIXED:" + ",".join(models))


class CodexAuditor:
    """GPT-6 Astra through ``codex exec`` (headless, read-only sandbox, no stdin, model pinned with ``-m``).

    Blinding: every call runs in a FRESH temporary directory that holds only ``packet.json`` (the packet
    the prompt also carries); the run directory, ``mapping.json`` and the labels are never in it. The
    read-only sandbox can still read absolute paths, so ``--json`` events are kept (``stdout`` in the
    ledger) and a call whose events show any tool use (a command, file read, MCP or web call) is VOID: no
    verdict. A reported model other than ``CODEX_MODEL`` (or none) is rejected the same way.

    Every call is ledgered (prompt digest, served model, tokens, exit code, reply, stdout events); a
    completed call with the same key replays from the ledger at no cost. Codex runs on a subscription:
    tokens are recorded, dollars are not priced (``cost_usd`` 0)."""

    ARGS = ("exec", "-m", CODEX_MODEL, "-s", "read-only", "-c", "model_reasoning_effort=high",
            "--skip-git-repo-check", "--json")
    NOTE = "\n\nAnswer from this message alone: do not run commands or read files."

    def __init__(self, ledger, *, timeout_s=1200, runner=None, sessions=CODEX_SESSIONS):
        # runner None: ``subprocess.run`` looked up at call time (so the test guard in tests/conftest.py sees it)
        self.ledger, self.timeout_s = Path(ledger), timeout_s
        self.runner = runner or (lambda *a, **k: subprocess.run(*a, **k))
        self.sessions = Path(sessions)
        self.last_workdir = None

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
        self._append({"key": key, "call_id": call_id, "status": "started",
                      "time": datetime.now(timezone.utc).isoformat()})
        with tempfile.TemporaryDirectory(prefix="ve-assist-audit-") as tmp:
            work = Path(tmp) / "packet"
            work.mkdir()
            packet = prompt.split("PACKET:\n", 1)[1] if "PACKET:\n" in prompt else prompt
            (work / "packet.json").write_text(packet, encoding="utf-8")
            self.last_workdir = sorted(p.name for p in work.iterdir())
            out = Path(tmp) / "reply.txt"
            start = time.monotonic()
            proc = self.runner(["codex", *self.ARGS, "-C", str(work), "-o", str(out), text], cwd=work,
                               stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=self.timeout_s)
            reply = out.read_text(encoding="utf-8") if out.exists() else ""
        events = codex_events(proc.stdout)
        model = codex_served_model(proc.stderr, events, self.sessions)
        tools = codex_tool_uses(events)
        usage = next((e.get("usage") for e in reversed(events) if e.get("type") == "turn.completed"), None)
        tokens = re.search(r"tokens used\s*\n\s*([\d,]+)", (proc.stdout or "") + "\n" + (proc.stderr or ""))
        used = (sum(v for k, v in usage.items() if k in ("input_tokens", "output_tokens") and type(v) is int)
                if isinstance(usage, dict) else int(tokens[1].replace(",", "")) if tokens else None)
        status = "ok" if proc.returncode == 0 and reply.strip() else "error"
        why = None
        if status == "ok" and model != CODEX_MODEL:
            status, why = "void", f"reported model {model!r} is not the pinned {CODEX_MODEL}"
        elif status == "ok" and tools:
            status, why = "void", f"the auditor used tools ({', '.join(sorted(set(tools)))}); verdict void"
        row = {"key": key, "call_id": call_id, "prompt_sha256": hashlib.sha256(text.encode()).hexdigest(),
               "served_model": model, "pinned_model": CODEX_MODEL, "tokens_used": used,
               **({"usage": usage} if isinstance(usage, dict) else {}), "tool_uses": tools,
               "returncode": proc.returncode, "elapsed_s": round(time.monotonic() - start, 1),
               "text": reply, "status": status, "stdout": proc.stdout or "",
               "time": datetime.now(timezone.utc).isoformat(), **({"void_reason": why} if why else {})}
        if status == "error":
            row["log_tail"] = ((proc.stdout or "") + "\n" + (proc.stderr or ""))[-1500:]
        self._append(row)
        if status == "void":
            raise AuditorViolation(why)
        if status != "ok":
            raise RuntimeError(f"codex exec failed (exit {proc.returncode}): {row['log_tail'][-300:]}")
        return reply, Decimal(0), row


def judge(packet, reply_text):
    value, error = last_json_block(reply_text)
    expected = {u["unit"]: u for u in packet["units"]}
    rows = [] if error else value.get("units") if isinstance(value.get("units"), list) else []
    verdicts = {r.get("unit"): r for r in rows if isinstance(r, dict)}
    problems = []
    for uid, unit in expected.items():
        v = verdicts.get(uid, {}).get("verdict")
        if unit["kind"] == "formalised":
            ok, why = v == "faithful", None
        else:  # waiver / omitted: must be on the allowlist AND judged acceptable
            ok = v == "acceptable" and unit.get("code") is not None
            why = None if unit.get("code") is not None else f"{unit['kind']} sentence outside the allowlist W"
        if not ok:
            problems.append({"unit": uid, "sentence": unit["sentence"], "kind": unit["kind"], "verdict": v,
                             "reason": why or verdicts.get(uid, {}).get("reason")})
    return {"pass": bool(expected) and not problems and not error, "problems": problems,
            "units": {u: verdicts.get(u) for u in expected}, **({"error": error} if error else {})}


OPUS_AUDIT_OUTPUT_TOKENS = 6000  # dev-tune-2 Opus audits used at most 3,083 output tokens
EXPECTED_MODELS = {"codex": CODEX_MODEL, "opus": "claude-opus-5-5"}


def make_auditor(who, out, account):
    if who == "codex":
        return CodexAuditor(out / "codex-audit-calls.jsonl")
    # one calls ledger per Claude account (the endpoint refuses mixed accounts in one ledger)
    name = f"opus-audit-calls.{account or 'main'}.jsonl"
    auditor = ClaudeTextAuthor("opus", out / name, account=account, output_tokens=OPUS_AUDIT_OUTPUT_TOKENS)
    auditor.client.infrastructure_retries = False  # one backend attempt per gated call (a rerun retries)
    return auditor


def verdict_path(out, pid, who):
    return out / "verdicts" / f"{pid}.{who}.json"


def run_audit(run_dir, *, account=None, auditors=None, max_usd=None):
    """Audit every exported packet by every required auditor that has no verdict yet; return the number of
    (packet, auditor) verdicts still missing.

    ``max_usd``: a hard cap on PRICED auditor spend (Opus, at list price) for this invocation. Before each
    priced call the auditor's worst-case ceiling is checked against it; a call that could cross it is not
    made (the verdict stays missing). A failed call is charged the tokens it reported. Spend is appended to
    ``audit/spend.jsonl``. A reported model other than the pinned one voids the call (no verdict)."""
    run_dir = Path(run_dir)
    out = run_dir / "audit"
    mapping = _load(out / "mapping.json")
    (out / "verdicts").mkdir(exist_ok=True)
    auditors = dict(auditors or {})
    real = set()
    missing = 0
    spent = Decimal(0)
    cap = Decimal(str(max_usd)) if max_usd is not None else None

    def log(name, row):
        with (out / name).open("a", encoding="utf-8") as f:
            f.write(json.dumps({**row, "time": datetime.now(timezone.utc).isoformat()}) + "\n")

    for pid in mapping["order"]:
        packet = _load(out / "packets" / f"{pid}.json")
        for who in auditors_for(mapping["packets"][pid]["author"]):
            target = verdict_path(out, pid, who)
            if target.exists():
                continue
            if not any(u["kind"] != "omitted" for u in packet["units"]):
                # nothing was formalised or waived: fails without an auditor call
                verdict = {"packet": pid, "auditor": who, "auditor_model": None, "cost_usd": "0", "reply": None,
                           "pass": False, "problems": [{"unit": None, "verdict": None, "reason": "empty packet"}],
                           "units": {}}
                target.write_text(json.dumps(verdict, ensure_ascii=False, indent=1))
                continue
            system, prompt = prompts.AUDIT_SYSTEM, audit_prompt(packet)
            try:
                if who not in auditors:
                    auditors[who] = make_auditor(who, out, account)
                    real.add(who)
                auditor = auditors[who]
                if cap is not None and hasattr(auditor, "single_ceiling"):
                    need = auditor.single_ceiling(system, prompt)
                    if spent + need > cap:
                        missing += 1
                        log("errors.jsonl", {"packet": pid, "auditor": who, "error": f"auditor cap: spent {spent} "
                                             f"+ ceiling {need} > ${cap}; not called"})
                        continue
                text, cost, row = auditor.single(f"assist-audit/{pid}", system, prompt)
                spent += Decimal(str(cost))
                if cost:
                    log("spend.jsonl", {"packet": pid, "auditor": who, "cost_usd": str(cost)})
                model = (row or {}).get("served_model") if isinstance(row, dict) else None
                if who in real and model != EXPECTED_MODELS[who]:
                    raise AuditorViolation(f"reported model {model!r} is not the pinned {EXPECTED_MODELS[who]}")
            except Exception as exc:  # logged; the packet stays unaudited and a rerun retries it
                lost = Decimal(str(getattr(exc, "cost", 0) or 0))
                spent += lost
                if lost:
                    log("spend.jsonl", {"packet": pid, "auditor": who, "cost_usd": str(lost), "failed": True})
                missing += 1
                log("errors.jsonl", {"packet": pid, "auditor": who, "error": f"{type(exc).__name__}: {exc}"[:2000]})
                continue
            verdict = {"packet": pid, "auditor": who, "auditor_model": model, "cost_usd": str(cost), "reply": text,
                       **({"auditor_tokens": row.get("tokens_used")} if isinstance(row, dict) and "tokens_used" in row
                          else {}),
                       **judge(packet, text)}
            target.write_text(json.dumps(verdict, ensure_ascii=False, indent=1))
    return missing


def load_verdicts(run_dir, pid, author, legacy=False):
    """{auditor: verdict} for one packet. ``legacy``: a run audited before the dual-audit layout keeps ONE
    verdict per packet in ``verdicts/<packet>.json``; it stands in for every required auditor (a proxy,
    reported as such)."""
    out = Path(run_dir) / "audit"
    if legacy:
        path = out / "verdicts" / f"{pid}.json"
        if not path.exists():
            return {}
        v = _load(path)
        return {who: {**v, "legacy_proxy": True} for who in auditors_for(author)}
    return {who: _load(verdict_path(out, pid, who)) for who in auditors_for(author)
            if verdict_path(out, pid, who).exists()}


def combine(verdicts, author):
    """One packet decision from the required auditors: pass iff every required auditor passed."""
    required = auditors_for(author)
    have = [verdicts[w] for w in required if w in verdicts]
    if len(have) < len(required):
        return None
    problems = [dict(p, auditor=v.get("auditor")) for v in have for p in v.get("problems", [])]
    passes = {w: bool(verdicts[w]["pass"]) for w in required}
    return {"pass": all(passes.values()), "passes": passes, "problems": problems,
            "disagreement": len(set(passes.values())) > 1,
            "legacy_proxy": any(v.get("legacy_proxy") for v in have),
            "units": {w: verdicts[w].get("units", {}) for w in required}}


# ------------------------------------------------------------------ report

def unit_origins(session, verdict):
    """For each failing unit: the provenance of the formal statements shown for its sentence."""
    if verdict is None or session is None:
        return {}
    out = {}
    for problem in verdict.get("problems", []):
        sid = problem.get("sentence")
        if sid is None:
            continue
        origins = [n.origin for n in session.nodes.values() if sid in n.anchors]
        origins += [row.get("origin", "hand-written") for row in session.targets.values()
                    if row["sentence"] == sid and row["formula"] is not None]
        key = f"{problem.get('auditor')}:{problem['unit']}" if problem.get("auditor") else problem["unit"]
        out[key] = {"sentence": sid, "kind": problem.get("kind"), "verdict": problem.get("verdict"),
                    "origins": sorted(set(origins))}
    return out


def attribute(result, verdict, cls, origins):
    """One cause per non-faithful-complete session (see README "Failure attribution")."""
    if cls["faithful_complete"]:
        return None
    if cls.get("over_budget"):
        return "budget"  # spend over every attempt exceeded the item budget: scored as a failure
    stop = str(result.get("stop_reason"))
    if stop.startswith(("abort: run cap", "abort: context")):
        return "budget"
    if stop.startswith("abort"):
        return "infrastructure"
    if not (result.get("verification") or {}).get("ok"):
        return "ledger-verification"
    if cls.get("violations"):
        return "dossier contract violation (waiver outside W / anchor content / unassumed check)"
    if verdict is None:
        return "unaudited"
    if not verdict["pass"]:
        if any(p.get("reason") == "empty packet" for p in verdict.get("problems", [])):
            return "author: nothing formalised"
        rows = list(origins.values())
        if any("proposer-verbatim" in r["origins"] for r in rows):
            return "audit-fail: proposer candidate accepted unchanged"
        if not rows or all(r["verdict"] in (None, "unclear") for r in rows):
            return "audit-fail: audit disagreement (unclear/missing verdicts)"
        return "audit-fail: author-written"
    if cls["flawed_certified_alarm"]:
        return "alarm: flawed item certified"
    if stop in ("budget", "max_turns", "max_tool_calls"):
        return "budget"
    return "tool refusal" if cls["kind"] == "benign" else "gap route: " + ", ".join(cls["gap_route_failures"][:3])


def classify(result, audit_pass, kind, checks, acceptable_locations, audited=True, over_budget=False):
    """Endpoints of one session. ``checks`` = ``scoring.session_checks`` (None: no ledger). An item whose
    spend over every attempt exceeds its budget (``all_attempts_spend``) is a FAILURE on every endpoint."""
    verified = bool((result.get("verification") or {}).get("ok"))
    violations = (checks or {}).get("violations") or []
    tool = bool(result.get("tool_success")) and verified and not violations and not over_budget
    if checks is None:
        route, located, why = False, False, ["no session ledger"]
    else:
        route, located, why = gap_route(result, checks, acceptable_locations)
    certified_faithful = tool and audit_pass
    faithful_complete = (certified_faithful if kind == "benign" else (audit_pass and route and not tool)) \
        and not over_budget
    return {"kind": kind, "over_budget": bool(over_budget), "tool_success": tool, "audit_pass": audit_pass, "certified_faithful": certified_faithful,
            "certified_unfaithful": tool and audited and not audit_pass, "gap_route": route,
            "gap_route_failures": [] if kind == "benign" else why, "gap_located": located if kind != "benign"
            else None, "violations": violations, "faithful_complete": faithful_complete,
            "flawed_certified_alarm": tool and kind != "benign"}


def all_attempts_spend(run_dir, d, result):
    """Spend over every attempt at the session: the final record plus every ``result.aborted-N.json``;
    for Gemini, reconciled against the run's paid ledger (every call billed under the session's identity)."""
    own = lambda r: Decimal(r["spent_usd"]["author"]) + Decimal(r["spent_usd"]["proposer"])
    total = own(result) + sum((own(_load(p)) for p in sorted(d.glob("result.aborted-*.json"))), Decimal(0))
    out = {"records_usd": str(total), "attempts": 1 + len(list(d.glob("result.aborted-*.json")))}
    ledger = Path(run_dir) / "gemini-ledger.jsonl"
    if result["author"] == "gemini" and ledger.exists():
        prefix = f"assist-eval/{result['split']}/gemini/{result['arm']}/{result['item_id']}/"
        billed, held = Decimal(0), Decimal(0)
        for line in ledger.read_text(encoding="utf-8").splitlines():
            row = json.loads(line) if line.strip() else {}
            if str(row.get("identity", "")).startswith(prefix):
                if row.get("event") == "complete":
                    billed += Decimal(str(row.get("cost_usd") or 0))
                elif row.get("event") == "infrastructure_failure":
                    held += Decimal(str(row.get("infrastructure_hold_usd") or 0))
        # billed = completed calls; held = the ledger's ceiling for 5xx/timeouts whose billing is unknown
        # (counted against the item budget, fail closed)
        out["paid_ledger_billed_usd"], out["unknown_billing_holds_usd"] = str(billed), str(held)
        total = max(total, billed + held)
    out["total_usd"] = str(total)
    out["over_budget"] = total > Decimal(str(result.get("budget_usd", 0)))
    return out


def _uptake(session):
    """A4: did the author use the proposer? (successful propose calls, candidates accepted)."""
    if session is None:
        return {"propose_ok": 0, "accepted": 0}
    ok = sum(1 for e in session.events if e.get("action") == "propose" and (e.get("result") or {}).get("ok"))
    accepted = sum(1 for n in session.nodes.values() if n.origin.startswith("proposer"))
    return {"propose_ok": ok, "accepted": accepted}


def sign_test(b, c):
    """Exact two-sided sign test p for b vs c discordant pairs."""
    from math import comb
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(comb(n, k) for k in range(0, min(b, c) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def exact_lower(k, n, alpha=0.05):
    """One-sided exact (Clopper-Pearson) lower bound for k/n."""
    from math import comb
    if k == 0:
        return 0.0
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        tail = sum(comb(n, j) * mid ** j * (1 - mid) ** (n - j) for j in range(k, n + 1))
        lo, hi = (mid, hi) if tail < alpha else (lo, mid)
    return round(lo, 4)


def exact_upper(k, n, alpha=0.05):
    return round(1 - exact_lower(n - k, n, alpha), 4)


def primary(rows, split):
    """Primary endpoint: Opus A3 vs A2 faithful-complete, paired by item at the same total budget."""
    a3 = {r["item_id"]: r for r in rows if (r["split"], r["author"], r["arm"]) == (split, "opus", "A3")}
    a2 = {r["item_id"]: r for r in rows if (r["split"], r["author"], r["arm"]) == (split, "opus", "A2")}
    both = sorted(set(a3) & set(a2))
    cell = lambda x, y: sum(1 for i in both if bool(a3[i]["faithful_complete"]) == x
                            and bool(a2[i]["faithful_complete"]) == y)
    b, c = cell(True, False), cell(False, True)
    k3 = sum(bool(a3[i]["faithful_complete"]) for i in both)
    alarms = sum(bool(a3[i]["flawed_certified_alarm"]) for i in both)
    flawed = sum(a3[i]["kind"] != "benign" for i in both)
    return {"endpoint": "Opus A3 vs A2 faithful-complete, paired by item", "split": split, "pairs": len(both),
            "both": cell(True, True), "a3_only": b, "a2_only": c, "neither": cell(False, False),
            "sign_test_p": sign_test(b, c), "a3_faithful_complete": f"{k3}/{len(both)}",
            "a3_lower_95": exact_lower(k3, len(both)) if both else None,
            "a3_alarms": f"{alarms}/{flawed}", "a3_alarm_upper_95": exact_upper(alarms, flawed) if flawed else None}


ROLES = {"opus": "primary", "gemini": "secondary", "haiku": "dropped (dev only)"}


def report(run_dir, *, legacy_audit=False, out_dir=None):
    run_dir = Path(run_dir)
    out_dir = Path(out_dir) if out_dir else run_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    mapping = _load(run_dir / "audit" / "mapping.json")["packets"] if (run_dir / "audit" / "mapping.json").exists() else {}
    by_dir = {v["session_dir"]: k for k, v in mapping.items()}
    labs = labels()
    rows, spot = [], []
    rng = random.Random(AUDIT_SEED)
    for d in session_dirs(run_dir):
        result = _load(d / "result.json")
        item = _item_for(result)
        pid = by_dir.get(str(d.relative_to(run_dir)))
        verdicts = load_verdicts(run_dir, pid, result["author"], legacy_audit) if pid else {}
        verdict = combine(verdicts, result["author"]) if pid else None
        kind = labs[result["item_id"]]["kind"]
        session = (AssistSession.from_ledger(_load(d / "session.json"), verify=False)
                   if (d / "session.json").exists() else None)
        checks = session_checks(session, item, result.get("finish")) if session else None
        spend = all_attempts_spend(run_dir, d, result)
        cls = classify(result, bool(verdict and verdict["pass"]), kind, checks,
                       labs[result["item_id"]]["acceptable_locations"], audited=verdict is not None,
                       over_budget=spend["over_budget"])
        origins = unit_origins(session, verdict)
        row = {**{k: result[k] for k in ("split", "author", "arm", "item_id", "stop_reason", "turns", "tool_calls")},
               "author_role": ROLES.get(result["author"], "other"),
               "spent_usd": result["spent_usd"]["total"], "spend_all_attempts": spend,
               "audited": verdict is not None, "auditors": sorted(verdicts),
               "audit_disagreement": bool(verdict and verdict["disagreement"]),
               "legacy_audit_proxy": bool(verdict and verdict["legacy_proxy"]),
               "verified": bool((result.get("verification") or {}).get("ok")),
               "tool_success_strict": bool(result.get("tool_success_strict")),
               "proposer_model": result.get("proposer_model"), "account": result.get("account"),
               "provenance": (result.get("status") or {}).get("provenance"),
               **({"proposer_uptake": _uptake(session)} if result["arm"] == "A4" else {}),
               **cls, "checks": {k: v for k, v in (checks or {}).items() if k != "violations"},
               "failing_units": origins, "attribution": attribute(result, verdict, cls, origins)}
        rows.append(row)
        if pid:
            packet = _load(run_dir / "audit" / "packets" / f"{pid}.json")
            chosen = packet["units"] if row["tool_success"] else rng.sample(
                packet["units"], min(SPOT_PER_PACKET, len(packet["units"])))
            for unit in chosen:
                spot.append({"packet": pid, **unit,
                             "auditor_verdicts": {w: v.get("units", {}).get(unit["unit"]) for w, v in verdicts.items()},
                             "reason_selected": "tool-certified session" if row["tool_success"] else "random sample"})
    groups = {}
    for r in rows:
        groups.setdefault((r["split"], r["author"], r["arm"]), []).append(r)
    table = []
    for (split, author, arm), rs in sorted(groups.items()):
        n = len(rs)
        count = lambda key, sub=rs: sum(bool(r.get(key)) for r in sub)
        benign = [r for r in rs if r["kind"] == "benign"]
        spend = [float(r["spend_all_attempts"]["total_usd"]) for r in rs]
        row = {"split": split, "author": author, "author_role": ROLES.get(author, "other"), "arm": arm, "n": n,
               "tool_success": count("tool_success"), "audit_pass": count("audit_pass"),
               "certified_faithful": count("certified_faithful"),
               "certified_faithful_benign": f"{count('certified_faithful', benign)}/{len(benign)}",
               "certified_unfaithful": count("certified_unfaithful"),
               "faithful_complete": count("faithful_complete"),
               "flawed_certified_alarm": count("flawed_certified_alarm"),
               "gap_located": count("gap_located"), "violations": sum(bool(r["violations"]) for r in rs),
               "mean_spent_usd": round(sum(spend) / n, 4), "total_spent_usd": round(sum(spend), 4),
               "over_budget_items": sum(r["spend_all_attempts"]["over_budget"] for r in rs),
               "audited": count("audited"), "audit_disagreement": count("audit_disagreement"),
               "legacy_audit_proxy": count("legacy_audit_proxy"), "verified": count("verified"),
               "tool_success_strict": count("tool_success_strict"),
               "attribution": dict(sorted(Counter(r["attribution"] for r in rs if r["attribution"]).items()))}
        if arm == "A4":
            used = sum(1 for r in rs if r["proposer_uptake"]["propose_ok"])
            row["proposer"] = f"proposer offered, uptake {used}/{n} sessions"
            row["arm_role"] = "exploratory"
        table.append(row)
    splits = sorted({r["split"] for r in rows})
    out = {"a1": A1_CITATION, "scoring": "ve-assist-eval-scoring@2 (W allowlist, dossier graph checks, gap route, "
           "dual audit for Gemini)" + (" -- LEGACY AUDIT PROXY: one pre-v4 verdict per packet stands in for every "
           "required auditor" if legacy_audit else ""),
           "primary": [primary(rows, sp) for sp in splits], "table": table, "rows": rows}
    (out_dir / "report.json").write_text(json.dumps(out, indent=1))
    with (out_dir / "audit-spotcheck.jsonl").open("w") as f:
        for row in spot:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return out
