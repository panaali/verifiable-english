"""Write RESULTS.md from runs/ (analysis fixed before any run, sealed with the eval).

    uv run python experiments/readability-sonnet/results.py

Uses score.py's metrics and pass bars unchanged, and adds:
- every answer: item, condition, session, letter, label, key, correct, critical, reason;
- every writing attempt with its outcome and the VE message shown after it;
- the 3 hardest constructs: reading, by lowest VE-L accuracy (ties: more critical
  misreadings, then more responses); writing, by lowest within-3 meaning-correct
  rate (ties: more silent wrong meanings, then more sessions);
- the two scorer cases the pre-run check flagged (two unparsed answers counted as
  agreeing; a DNS answer to R07 counted as critical), and which models answered.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import score  # noqa: E402

RUNS = HERE / "runs"
PROXY = "proxy: Claude Sonnet 5.5 with only the context a human user would get"


def cell(text):
    return str(text if text is not None else "").replace("|", "\\|").replace("\n", " ")


def hardest(groups, rate, tie):
    ranked = sorted(groups.items(), key=lambda kv: (rate(kv[1])["rate"], -tie(kv[1])["k"], -rate(kv[1])["n"]))
    return ranked[:3]


def main():
    items = json.loads((HERE / "items.json").read_text())["items"]
    tasks = json.loads((HERE / "writing.json").read_text())["tasks"]
    reading = score.reading_metrics(score.load_jsonl(RUNS / "reading.jsonl"), items)
    writing = score.writing_metrics(score.load_jsonl(RUNS / "writing.jsonl"), tasks)
    passbars = score.bars(reading, writing)
    (RUNS / "metrics.json").write_text(json.dumps({"reading": reading, "writing": writing, "pass_bars": passbars},
                                                  indent=1, ensure_ascii=False, default=str) + "\n")
    models, calls = {}, 0
    for path in sorted(RUNS.glob("*/*/*.json")):
        rec = json.loads(path.read_text())
        for c in [rec.get("call")] + [t["call"] for t in rec.get("turns", [])]:
            if c:
                calls += 1
                for m in c.get("models", []):
                    models[m] = models.get(m, 0) + 1
    by_item = {i["id"]: i for i in items}
    body = score.markdown(reading, writing, passbars).split("\n", 1)[1]
    out = ["# Readability eval results", "", f"**{PROXY}.** Pre-registered label: \"{score.LABEL}\".", "",
           f"Models in the {calls} successful calls (call counts): "
           + ", ".join(f"`{m}` {n}" for m, n in sorted(models.items())) + ".", body]

    out += ["## The 3 hardest constructs", "", "Reading (VE-L, lowest accuracy):", ""]
    ve_l = reading["per_construct"].get("VE-L", {})
    for g, m in hardest(ve_l, lambda m: m["accuracy"], lambda m: m["critical"]):
        out.append(f"- {g}: accuracy {score.pct(m['accuracy'])}; critical {score.pct(m['critical'])}")
    out += ["", "Writing (lowest within-3 meaning-correct):", ""]
    for g, m in hardest(writing["per_construct"], lambda m: m["within_3_correct"], lambda m: m["silent_wrong_final"]):
        out.append(f"- {g}: within 3 {score.pct(m['within_3_correct'])}; first try "
                   f"{score.pct(m['first_try_correct'])}; silent wrong (final) {score.pct(m['silent_wrong_final'])}")

    pairs = {}
    for r in reading["reasons"]:
        pairs.setdefault((r["item"], r["condition"]), []).append(r)
    none_pairs = [k for k, v in pairs.items() if len(v) == 2 and v[0]["answer_label"] is None
                  and v[1]["answer_label"] is None]
    r07_dns = [r for r in reading["reasons"] if r["item"] == "R07" and r["answer_label"] == "DNS"]
    out += ["", "## Scorer cases flagged by the pre-run check", "",
            f"- Pairs where both answers were unparsed (counted as agreeing): {len(none_pairs)}"
            + (f" ({', '.join(f'{i} {c}' for i, c in none_pairs)})" if none_pairs else "") + ".",
            f"- DNS answers to R07 (key CONFLICT; scored critical): {len(r07_dns)}"
            + (f" ({', '.join(r['condition'] + ' ' + r['session'] for r in r07_dns)})" if r07_dns else "") + ".",
            ""]

    out += ["## Every reading answer", "",
            "| Item | Condition | Session | Answer | Key | Correct | Critical | Constructs | Reason |",
            "|---|---|---|---|---|---|---|---|---|"]
    order = {"VE-L": 0, "VE-C": 1, "EN": 2}
    for r in sorted(reading["reasons"], key=lambda r: (r["item"], order[r["condition"]], r["session"])):
        out.append(f"| {r['item']} | {r['condition']} | {r['session']} | {r['answer']} {r['answer_label'] or ''} | "
                   f"{by_item[r['item']]['key']} {r['key_label']} | {'yes' if r['correct'] else 'no'} | "
                   f"{'CRITICAL' if r['critical'] else ''} | {', '.join(by_item[r['item']]['constructs'])} | "
                   f"{cell(r['reason'])} |")

    out += ["", "## Every writing attempt", "",
            "| Task | Session | Attempt | Sentence | Outcome | VE message shown after it | Reason |",
            "|---|---|---|---|---|---|---|"]
    for s in sorted(writing["sessions_detail"], key=lambda s: (s["task"], s["session"])):
        for n, a in enumerate(s["attempts"], 1):
            shown = "" if a["outcome"] == "correct" or n == 3 else a["ve_message"]
            out.append(f"| {s['task']} | {s['session']} | {n} | {cell(a['sentence'])} | {a['outcome']} | "
                       f"{cell(shown)} | {cell(a['reason'])} |")
    (HERE / "RESULTS.md").write_text("\n".join(out) + "\n")
    print(score.markdown(reading, writing, passbars))


if __name__ == "__main__":
    main()
