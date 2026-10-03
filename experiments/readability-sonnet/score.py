"""Mechanical scoring for the readability eval (no model calls).

    # one writing attempt: outcome and the exact VE message the editor shows
    uv run python experiments/readability-sonnet/score.py check W07 "If ..., running the job leads to ..."

    # metrics, Wilson 95% intervals and the pre-registered pass bars
    uv run python experiments/readability-sonnet/score.py report --reading reading.jsonl --writing writing.jsonl

Reading responses, one JSON object per line:
    {"item": "R01", "condition": "VE-L" | "VE-C" | "EN", "session": "s1",
     "answer": "B", "reason": "..."}
  or "raw" in place of answer/reason, holding the session's reply text
  ("ANSWER: B\\nREASON: ..."). Each item is answered in each of its conditions
  by two separate fresh sessions (session ids s1, s2).

Writing responses, one JSON object per line:
    {"task": "W01", "session": "s1",
     "attempts": [{"sentence": "...", "reason": "..."}, ...]}   (1 to 3 attempts)
  Every attempt is rescored here; the recorded loop must have stopped at the
  first correct attempt and shown, after each failed one, exactly the
  `ve_message` that `check` prints for it.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

LABEL = "proxy: Claude Sonnet 5.5, upper bound for careful readers"
OPPOSITE = [{"PERMITTED", "FORBIDDEN"}, {"REQUIRED", "NOT-REQUIRED"}, {"YES", "NO"}, {"MIGHT", "CANNOT"},
            {"FOLLOWS", "GAP"}]
BARS = {
    "critical_ve_l": "critical misreadings in VE-L <= 2%",
    "ve_l_vs_en": "VE-L accuracy >= EN accuracy on items that have EN",
    "agreement_ve_l": "two-session agreement >= 90% in VE-L",
    "silent_wrong": "writing silent-wrong-meaning <= 5%",
    "within3": "meaning-correct within 3 attempts >= 80%",
}


def wilson(k, n, z=1.959964):
    """Wilson score interval for k successes in n trials."""
    if n == 0:
        return {"k": 0, "n": 0, "rate": None, "low": None, "high": None}
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return {"k": k, "n": n, "rate": p, "low": max(0.0, centre - half), "high": min(1.0, centre + half)}


def critical(answer_label, key_label):
    """Opposite verdict, a definite answer where the key is 'does not say', or
    'does not say' where the text decides. CONFLICT confusions are wrong but
    not critical."""
    if answer_label == key_label or answer_label is None:
        return False
    if "DNS" in (answer_label, key_label):
        return True
    return {answer_label, key_label} in OPPOSITE


def load_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def parse_reply(raw):
    answer = re.search(r"^\s*ANSWER:\s*([A-D])\b", raw, re.M | re.I)
    reason = re.search(r"^\s*REASON:\s*(.+)$", raw, re.M | re.I)
    return (answer[1].upper() if answer else None), (reason[1].strip() if reason else None)


# --- reading ------------------------------------------------------------------

def reading_metrics(responses, items):
    by_id = {i["id"]: i for i in items}
    rows = []
    for r in responses:
        item = by_id[r["item"]]
        if r["condition"] not in item["conditions"]:
            raise SystemExit(f"{r['item']} has no condition {r['condition']}")
        answer, reason = (r.get("answer"), r.get("reason"))
        if answer is None and "raw" in r:
            answer, reason = parse_reply(r["raw"])
        labels = {o["letter"]: o["label"] for o in item["options"]}
        label = labels.get(answer)
        rows.append({"item": item["id"], "condition": r["condition"], "session": r.get("session"),
                     "answer": answer, "answer_label": label, "key_label": item["key_label"],
                     "correct": answer == item["key"], "critical": critical(label, item["key_label"]),
                     "unparsed": label is None, "reason": reason,
                     "constructs": item["constructs"], "rendering": item["rendering"]["type"],
                     "form": item["rendering"]["form"],
                     "explicit_notation": bool(item["rendering"]["explicit_notation"]),
                     "legend_dependent": item["legend_dependent"], "has_en": "EN" in item["conditions"],
                     "world_knowledge": bool(item.get("world_knowledge"))})
    out = {"label": LABEL, "per_condition": {}, "per_construct": {}, "per_rendering": {}, "per_form": {},
           "per_notation": {}, "legend_dependent": {}, "world_knowledge_items": {}}
    conditions = sorted({r["condition"] for r in rows})
    for c in conditions:
        cr = [r for r in rows if r["condition"] == c]
        dns_key = [r for r in cr if r["key_label"] == "DNS"]
        dns_answer = [r for r in cr if r["answer_label"] == "DNS"]
        sessions = defaultdict(list)
        for r in cr:
            sessions[r["item"]].append(r)
        pairs = [(v[0]["answer"], v[1]["answer"]) for v in sessions.values() if len(v) >= 2]
        out["per_condition"][c] = {
            "accuracy": wilson(sum(r["correct"] for r in cr), len(cr)),
            "critical_misreadings": wilson(sum(r["critical"] for r in cr), len(cr)),
            "unparsed_answers": sum(r["unparsed"] for r in cr),
            "abstention_recall": wilson(sum(r["answer_label"] == "DNS" for r in dns_key), len(dns_key)),
            "abstention_precision": wilson(sum(r["key_label"] == "DNS" for r in dns_answer), len(dns_answer)),
            "two_session_agreement": wilson(sum(a == b for a, b in pairs), len(pairs)),
        }
        for key, field in (("per_construct", "constructs"), ("per_rendering", "rendering"), ("per_form", "form"),
                           ("per_notation", "explicit_notation"), ("legend_dependent", "legend_dependent"),
                           ("world_knowledge_items", "world_knowledge")):
            groups = defaultdict(list)
            for r in cr:
                for g in (r[field] if isinstance(r[field], list) else [r[field]]):
                    groups[str(g)].append(r)
            out[key][c] = {g: {"accuracy": wilson(sum(r["correct"] for r in v), len(v)),
                               "critical": wilson(sum(r["critical"] for r in v), len(v))}
                           for g, v in sorted(groups.items())}
    en_items = {r["item"] for r in rows if r["condition"] == "EN"}
    out["ve_l_vs_en_same_items"] = {
        c: wilson(sum(r["correct"] for r in rows if r["condition"] == c and r["item"] in en_items),
                  sum(1 for r in rows if r["condition"] == c and r["item"] in en_items))
        for c in conditions}
    out["reasons"] = [{k: r[k] for k in ("item", "condition", "session", "answer", "answer_label", "key_label",
                                         "correct", "critical", "reason")} for r in rows]
    return out


# --- writing ------------------------------------------------------------------

def check(task_id, sentence):
    import writing_spec
    return writing_spec.score(writing_spec.task_by_id(task_id), sentence)


def writing_metrics(responses, tasks):
    by_id = {t["id"]: t for t in tasks}
    sessions = []
    for r in responses:
        task = by_id[r["task"]]
        attempts = r["attempts"][:3]
        scored = []
        for a in attempts:
            s = check(task["id"], a["sentence"])
            scored.append({"sentence": a["sentence"], "reason": a.get("reason"), "outcome": s["outcome"],
                           "ve_message": s.get("ve_message")})
            if s["outcome"] == "correct":
                break
        if len(scored) < len(attempts):
            raise SystemExit(f"{r['task']} {r.get('session')}: attempts continue after a correct attempt")
        fixes = [{"message": scored[i]["ve_message"], "failed_as": scored[i]["outcome"]}
                 for i in range(len(scored) - 1) if scored[i + 1]["outcome"] == "correct"]
        sessions.append({"task": task["id"], "session": r.get("session"), "family": task["family"],
                         "constructs": task["constructs"], "attempts": scored, "fixed_by": fixes})
    n = len(sessions)
    first = [s["attempts"][0]["outcome"] for s in sessions]
    final = [s["attempts"][-1]["outcome"] for s in sessions]
    all_attempts = [a["outcome"] for s in sessions for a in s["attempts"]]
    one_reading = lambda o: o in ("correct", "wrong_meaning", "unknown", "condition_unverified")
    out = {"label": LABEL, "sessions": n,
           "first_try": {
               "parse_rate": wilson(sum(o not in ("parse_failure",) for o in first), n),
               "one_reading_rate": wilson(sum(one_reading(o) for o in first), n),
               "meaning_correct": wilson(sum(o == "correct" for o in first), n),
               "silent_wrong_meaning": wilson(sum(o == "wrong_meaning" for o in first), n),
               "parse_failures": sum(o == "parse_failure" for o in first),
               "ambiguous": sum(o == "ambiguous" for o in first),
               "not_one_sentence": sum(o == "not_one_sentence" for o in first),
               "unknown_equivalence": sum(o in ("unknown", "condition_unverified") for o in first)},
           "within_3": {
               "meaning_correct": wilson(sum(o == "correct" for o in final), n),
               "silent_wrong_meaning_final": wilson(sum(o == "wrong_meaning" for o in final), n),
               "parse_failure_final": sum(o == "parse_failure" for o in final),
               "ambiguous_final": sum(o == "ambiguous" for o in final),
               "unknown_equivalence_final": sum(o in ("unknown", "condition_unverified") for o in final)},
           "per_attempt": {
               "attempts": len(all_attempts),
               "silent_wrong_meaning": wilson(sum(o == "wrong_meaning" for o in all_attempts), len(all_attempts)),
               "parse_failures": sum(o == "parse_failure" for o in all_attempts),
               "ambiguous": sum(o == "ambiguous" for o in all_attempts)},
           "per_construct": {}, "per_family": {},
           "messages_that_led_to_a_fix": [dict(f, task=s["task"], session=s["session"])
                                          for s in sessions for f in s["fixed_by"]],
           "sessions_detail": sessions}
    for key, field in (("per_construct", "constructs"), ("per_family", "family")):
        groups = defaultdict(list)
        for s in sessions:
            for g in (s[field] if isinstance(s[field], list) else [s[field]]):
                groups[g].append(s)
        out[key] = {g: {"first_try_correct": wilson(sum(s["attempts"][0]["outcome"] == "correct" for s in v), len(v)),
                        "within_3_correct": wilson(sum(s["attempts"][-1]["outcome"] == "correct" for s in v), len(v)),
                        "silent_wrong_final": wilson(sum(s["attempts"][-1]["outcome"] == "wrong_meaning"
                                                         for s in v), len(v))}
                    for g, v in sorted(groups.items())}
    return out


# --- pass bars ----------------------------------------------------------------

def bars(reading, writing):
    result = {}
    if reading:
        pc = reading["per_condition"]
        if "VE-L" in pc:
            crit = pc["VE-L"]["critical_misreadings"]
            result["critical_ve_l"] = {"value": crit, "met": crit["rate"] is not None and crit["rate"] <= 0.02}
            agree = pc["VE-L"]["two_session_agreement"]
            result["agreement_ve_l"] = {"value": agree, "met": agree["rate"] is not None and agree["rate"] >= 0.90}
        same = reading["ve_l_vs_en_same_items"]
        if "VE-L" in same and "EN" in same and same["EN"]["n"]:
            result["ve_l_vs_en"] = {"value": {"VE-L": same["VE-L"], "EN": same["EN"]},
                                    "met": same["VE-L"]["rate"] >= same["EN"]["rate"]}
    if writing:
        silent = writing["within_3"]["silent_wrong_meaning_final"]
        result["silent_wrong"] = {"value": silent, "met": silent["rate"] is not None and silent["rate"] <= 0.05}
        within = writing["within_3"]["meaning_correct"]
        result["within3"] = {"value": within, "met": within["rate"] is not None and within["rate"] >= 0.80}
    return {k: {"bar": BARS[k], **v} for k, v in result.items()}


def pct(w):
    if w["rate"] is None:
        return "n/a (n = 0)"
    return f"{w['k']}/{w['n']} = {100 * w['rate']:.1f}% (95% CI {100 * w['low']:.1f} to {100 * w['high']:.1f})"


def markdown(reading, writing, passbars):
    lines = [f"# Readability eval results ({LABEL})", ""]
    if reading:
        lines += ["## Reading", "", "| Condition | Accuracy | Critical misreadings | Abstention recall | "
                  "Abstention precision | Two-session agreement |", "|---|---|---|---|---|---|"]
        for c, m in reading["per_condition"].items():
            lines.append(f"| {c} | {pct(m['accuracy'])} | {pct(m['critical_misreadings'])} | "
                         f"{pct(m['abstention_recall'])} | {pct(m['abstention_precision'])} | "
                         f"{pct(m['two_session_agreement'])} |")
        lines += ["", "Items with an EN source, accuracy per condition: " +
                  "; ".join(f"{c} {pct(w)}" for c, w in reading["ve_l_vs_en_same_items"].items()), ""]
        lines += ["### Per construct", "", "| Condition | Construct | Accuracy | Critical |", "|---|---|---|---|"]
        for c, groups in reading["per_construct"].items():
            for g, m in groups.items():
                lines.append(f"| {c} | {g} | {pct(m['accuracy'])} | {pct(m['critical'])} |")
        lines += ["", "### Per rendering type", "", "| Condition | Rendering | Accuracy | Critical |",
                  "|---|---|---|---|"]
        for c, groups in reading["per_form"].items():
            for g, m in groups.items():
                lines.append(f"| {c} | form: {g} | {pct(m['accuracy'])} | {pct(m['critical'])} |")
        for c, groups in reading["per_rendering"].items():
            for g, m in groups.items():
                lines.append(f"| {c} | {g} | {pct(m['accuracy'])} | {pct(m['critical'])} |")
        lines.append("")
    if writing:
        w = writing
        lines += ["## Writing", "", f"Sessions: {w['sessions']}", "",
                  "| Measure | First try | Within 3 attempts |", "|---|---|---|",
                  f"| Meaning correct | {pct(w['first_try']['meaning_correct'])} | "
                  f"{pct(w['within_3']['meaning_correct'])} |",
                  f"| Silent wrong meaning | {pct(w['first_try']['silent_wrong_meaning'])} | "
                  f"{pct(w['within_3']['silent_wrong_meaning_final'])} |",
                  f"| Parses | {pct(w['first_try']['parse_rate'])} | |",
                  f"| One reading | {pct(w['first_try']['one_reading_rate'])} | |", "",
                  f"Parse failures (first try): {w['first_try']['parse_failures']}; ambiguous: "
                  f"{w['first_try']['ambiguous']}; unknown equivalence: {w['first_try']['unknown_equivalence']}.",
                  "", "### Per construct", "", "| Construct | First try | Within 3 | Silent wrong (final) |",
                  "|---|---|---|---|"]
        for g, m in w["per_construct"].items():
            lines.append(f"| {g} | {pct(m['first_try_correct'])} | {pct(m['within_3_correct'])} | "
                         f"{pct(m['silent_wrong_final'])} |")
        lines += ["", "### VE messages followed by a correct attempt", ""]
        lines += [f"- {f['task']} {f['session']} ({f['failed_as']}): {f['message']}"
                  for f in w["messages_that_led_to_a_fix"]] or ["- none"]
        lines.append("")
    lines += ["## Pass bars (fixed before any run)", "", "| Bar | Value | Met |", "|---|---|---|"]
    for b in passbars.values():
        v = b["value"]
        shown = "; ".join(f"{k} {pct(x)}" for k, x in v.items()) if "rate" not in v else pct(v)
        lines.append(f"| {b['bar']} | {shown} | {'met' if b['met'] else 'NOT MET'} |")
    return "\n".join(lines) + "\n"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)
    c = sub.add_parser("check", help="score one writing attempt")
    c.add_argument("task")
    c.add_argument("sentence")
    r = sub.add_parser("report", help="metrics and pass bars")
    r.add_argument("--reading")
    r.add_argument("--writing")
    r.add_argument("--json", help="write the full metrics JSON here")
    args = p.parse_args(argv)
    if args.command == "check":
        print(json.dumps(check(args.task, args.sentence), indent=1, ensure_ascii=False, default=str))
        return 0
    items = json.loads((HERE / "items.json").read_text())["items"]
    tasks = json.loads((HERE / "writing.json").read_text())["tasks"]
    reading = reading_metrics(load_jsonl(args.reading), items) if args.reading else None
    writing = writing_metrics(load_jsonl(args.writing), tasks) if args.writing else None
    passbars = bars(reading, writing)
    if args.json:
        Path(args.json).write_text(json.dumps({"reading": reading, "writing": writing, "pass_bars": passbars},
                                              indent=1, ensure_ascii=False, default=str) + "\n")
    print(markdown(reading, writing, passbars))
    return 0


if __name__ == "__main__":
    sys.exit(main())
