"""Blind cross-family fidelity audit, human spot-check list, and the results report.

Export (no model calls): each finished session becomes a PACKET with the
dossier's sentences (id, role, text), the predicate glosses, and one UNIT per
asserting sentence that has a formalisation (the deterministic paraphrases of
the nodes anchored to it, plus the frozen target for a target sentence) or a
waiver (with its reason). A packet carries NO parents, check results, status,
certification, arm, author, cost or item id; packet ids are salted hashes and
the mapping stays in ``audit/mapping.json``. Packets are shuffled with a seed.

Auditor = a different family from the author: Gemini 3.1 Pro audits Claude
authors (Opus, Haiku); Opus 5.5 audits Gemini. A packet PASSES iff every
formalised unit is "faithful" and every waiver "acceptable"; a missing,
unparseable or "unclear" verdict fails it (conservative). Auditor spend is
evaluation cost, not charged to the author's budget.
"""
from __future__ import annotations

from decimal import Decimal
import hashlib
import json
from pathlib import Path
import random

from ve.assist import AssistSession

from . import prompts
from .authors import ClaudeTextAuthor, GeminiAuthor, last_json_block
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
    return "gemini" if author in ("opus", "haiku") else "opus"


def judge(packet, reply_text):
    value, error = last_json_block(reply_text)
    expected = {u["unit"]: u["kind"] for u in packet["units"]}
    if error:
        return {"pass": False, "error": error, "units": {}}
    rows = value.get("units") if isinstance(value.get("units"), list) else []
    verdicts = {r.get("unit"): r for r in rows if isinstance(r, dict)}
    problems = []
    for uid, kind in expected.items():
        v = verdicts.get(uid, {}).get("verdict")
        ok = v == "faithful" if kind == "formalised" else v == "acceptable"
        if not ok:
            problems.append({"unit": uid, "verdict": v, "reason": verdicts.get(uid, {}).get("reason")})
    return {"pass": bool(expected) and not problems, "problems": problems,
            "units": {u: verdicts.get(u) for u in expected}}


def run_audit(run_dir, *, gemini_ledger, gemini_cap_usd, account="saeedi.danial"):
    run_dir = Path(run_dir)
    out = run_dir / "audit"
    mapping = _load(out / "mapping.json")
    (out / "verdicts").mkdir(exist_ok=True)
    auditors = {}
    for pid in mapping["order"]:
        target = out / "verdicts" / f"{pid}.json"
        if target.exists():
            continue
        packet = _load(out / "packets" / f"{pid}.json")
        who = auditor_for(mapping["packets"][pid]["author"])
        if who not in auditors:
            auditors[who] = (GeminiAuthor(gemini_ledger, cap_usd=gemini_cap_usd, output_tokens=16000)
                             if who == "gemini" else
                             ClaudeTextAuthor("opus", out / "opus-audit-calls.jsonl", account=account))
        text, cost, _ = auditors[who].single(f"assist-audit/{pid}", prompts.AUDIT_SYSTEM, audit_prompt(packet))
        verdict = {"packet": pid, "auditor": who, "cost_usd": str(cost), "reply": text, **judge(packet, text)}
        target.write_text(json.dumps(verdict, ensure_ascii=False, indent=1))


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


def classify(result, audit_pass, kind):
    status = result.get("status") or {}
    tool = bool(result.get("tool_success"))
    unproved = {r["node"] for r in status.get("unproved_steps", [])}
    finish = result.get("finish") or {}
    target_stated = all(t.get("reason") != "no step node states the frozen target" and t.get("text")
                        for t in status.get("targets", [])) and bool(status.get("targets"))
    gap_route = (finish.get("verdict") == "gap" and bool(unproved) and unproved <= set(finish.get("gap_steps", []))
                 and target_stated and not status.get("uncovered")
                 and not any(u["load_bearing"] for u in status.get("unanchored_assumptions", []))
                 and not status.get("renamed_conclusions"))
    certified_faithful = tool and audit_pass
    faithful_complete = certified_faithful if kind == "benign" else (audit_pass and gap_route and not tool)
    return {"tool_success": tool, "audit_pass": audit_pass, "certified_faithful": certified_faithful,
            "certified_unfaithful": tool and not audit_pass, "gap_route": gap_route,
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
        row = {**{k: result[k] for k in ("split", "author", "arm", "item_id", "stop_reason", "turns", "tool_calls")},
               "kind": kind, "spent_usd": result["spent_usd"]["total"], "audited": verdict is not None,
               **classify(result, bool(verdict and verdict["pass"]), kind)}
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
                      "audited": count("audited")})
    out = {"a1": A1_CITATION, "table": table, "rows": rows}
    (run_dir / "report.json").write_text(json.dumps(out, indent=1))
    with (run_dir / "audit-spotcheck.jsonl").open("w") as f:
        for row in spot:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return out
