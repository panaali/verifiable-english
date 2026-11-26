"""Compare a run file with the sealed answers (sha256 checked). SAME-FAMILY. Committed BEFORE the headline run.

usage: python3 -I grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/stock/ved-first-year [--out GRADES.json]
Reads <dir>/sealed/answers.jsonl (sha256 must equal the seal) and <dir>/questions.jsonl (scope and the writer's tags).
Per in-scope question: match (VE's answer equals the sealed answer: Q1 / Q2 GBP to the penny, or "this Part does not
apply"; Q3 yes / no), disagree (VE answered, differently: goes to two fresh graders; VE certain and graded wrong = a WRONG
answer), refused (OPEN), unsupported, writer-ambiguous (the writer filled "ambiguous": not correct whatever VE says, D6).
Probes apart. Side numbers by ACTUAL USE (batch 2 / 3 audits): table rows = the answer's admitted documents contain a
table-row unit (7-31); outside Lean = the writer tagged it stated-judgment / bridge-only, or flips.json shows the bridged
duration or an encoder judgement decides it (flips.py, committed with the cases, never reads answers); reading R1 (the
sufficient half of 1GC(5)) reported beside; price SUM = the documents use unit 40 with an accessory counted.
"""
import hashlib
import json
import re
import sys
from decimal import Decimal
from pathlib import Path

SEALED_SHA256 = "6068d2e8390673841174c794fe83a3a53330bc427a070199f1a2b4c137611fdc"
QUESTIONS_SHA256 = "72bb0614f0f13f5f8269854ec2fc39371b8f4205b36c20db0855fc3eed2ec600"
TABLE_UNITS = set(range(7, 32))
HERE = Path(__file__).resolve().parent


def number(v):
    if v in (None, ""):
        return None
    m = re.search(r"-?\d[\d,]*(?:\.\d+)?", str(v))
    return None if m is None else Decimal(m.group(0).replace(",", ""))


def writer_not_apply(w):
    t = (str(w.get("answer", "")) + " " + str(w.get("value", ""))).lower()
    return w.get("value") in (None, "") and ("does not apply" in t or "not apply" in t)


def same(kind, ve, w):
    if kind in ("Q1", "Q2"):
        if ve.get("answer") == "NOT_APPLY" or writer_not_apply(w):
            return ve.get("answer") == "NOT_APPLY" and writer_not_apply(w)
        wv = number(w.get("value")) if w.get("value") not in (None, "") else number(w.get("answer"))
        return ve.get("answer") == "AMOUNT" and wv is not None and Decimal(ve["gbp"]) == wv.quantize(Decimal("0.01"))
    if kind == "Q3":
        first = str(w.get("answer", "")).strip().lower().split()
        return bool(first) and first[0].strip(".,;:") == ve.get("answer")
    raise ValueError(kind)


def main(argv):
    run = json.load(open(argv[0], encoding="utf-8"))
    d = argv[1]
    raw = open(d + "/sealed/answers.jsonl", "rb").read()
    if hashlib.sha256(raw).hexdigest() != SEALED_SHA256:
        raise SystemExit("sealed answers.jsonl sha256 differs from the seal")
    qraw = open(d + "/questions.jsonl", "rb").read()
    if hashlib.sha256(qraw).hexdigest() != QUESTIONS_SHA256:
        raise SystemExit("questions.jsonl sha256 differs from the seal")
    flips = json.loads((HERE / "flips.json").read_text(encoding="utf-8"))
    bridge = set(flips["bridge_decisive"])
    encoder = set(flips["encoder_decisive"])
    r1 = set(flips["reading_R1_decisive"])
    sealed = {a["qid"]: a for a in map(json.loads, raw.decode().splitlines()) if a}
    meta = {}
    for c in map(json.loads, qraw.decode().splitlines()):
        for x in c["questions"]:
            meta[x["qid"]] = {"scope": c["scope"], "kind": x["kind"], "tag": x["tag"]}
    ve = {q: a for r in run["records"] for q, a in r["answers"].items()}
    use = {q: u for r in run["records"] for q, u in r.get("uses", {}).items()}
    rows = []
    for qid, m in meta.items():
        w, v = sealed[qid], ve[qid]
        if m["scope"] == "out":
            status = "probe-unsupported" if v["answer"] == "UNSUPPORTED" else "probe-answered"
        elif v["answer"] == "UNSUPPORTED":
            status = "unsupported"
        elif v["answer"] == "OPEN":
            status = "refused"
        elif w.get("ambiguous"):
            status = "writer-ambiguous" + ("-match" if same(m["kind"], v, w) else "-differ")
        elif same(m["kind"], v, w):
            status = "match"
        else:
            status = "disagree"
        u = use.get(qid, {"units": [], "facts": []})
        outside = sorted(x for x, hit in (("tag", m["tag"] != "none"), ("bridge", qid in bridge),
                                          ("encoder", qid in encoder)) if hit)
        acc_used = 40 in u["units"] and any(f.startswith("alp_") or f.startswith("anp_") for f in u["facts"])
        rows.append({"qid": qid, **m, "status": status, "ve": v, "uses_table_row": bool(TABLE_UNITS & set(u["units"])),
                     "uses_price_sum": acc_used, "outside": outside, "reading_R1": qid in r1,
                     "writer": {k: w.get(k) for k in ("answer", "value")}})
    ins = [r for r in rows if r["scope"] == "in"]
    count = lambda rs, st: sum(r["status"] == st for r in rs)  # noqa: E731
    sub = lambda rs: {"written": len(rs), "match": count(rs, "match")}  # noqa: E731
    summary = {"in_scope_written": len(ins), "match": count(ins, "match"), "disagree": count(ins, "disagree"),
               "refused": count(ins, "refused"), "unsupported": count(ins, "unsupported"),
               "writer_ambiguous": sum(r["status"].startswith("writer-ambiguous") for r in ins),
               "writer_ambiguous_qids": sorted(r["qid"] + ":" + r["status"] for r in ins
                                               if r["status"].startswith("writer-ambiguous")),
               "disagree_qids": sorted(r["qid"] for r in ins if r["status"] == "disagree"),
               "by_tag": {t: sub([r for r in ins if r["tag"] == t]) for t in ("none", "bridge-only", "stated-judgment")},
               "without_outside_lean": sub([r for r in ins if not r["outside"]]),
               "without_outside_lean_or_R1": sub([r for r in ins if not r["outside"] and not r["reading_R1"]]),
               "excluding_table_rows_by_use": sub([r for r in ins if not r["uses_table_row"]]),
               "by_question_kind": {k: sub([r for r in ins if r["kind"] == k]) for k in ("Q1", "Q2", "Q3")},
               "amount_kinds_by_use": {
                   "table row lookup (Q1)": sub([r for r in ins if r["kind"] == "Q1"]),
                   "price SUM with an accessory counted (Q2, Q3)": sub([r for r in ins if r["kind"] != "Q1"
                                                                        and r["uses_price_sum"]]),
                   "thresholds LIN, price without a counted accessory (Q2, Q3)": sub(
                       [r for r in ins if r["kind"] != "Q1" and not r["uses_price_sum"]])},
               "probes": {"written": len(rows) - len(ins),
                          "unsupported": sum(r["status"] == "probe-unsupported" for r in rows)},
               "not_correct": sorted(r["qid"] for r in ins if r["status"] != "match"),
               "run_commit": run["commit"], "run_tree_clean": run["tree_clean"]}
    out = {"summary": summary, "rows": rows}
    text = json.dumps(out, indent=1, sort_keys=True) + "\n"
    if "--out" in argv:
        open(argv[argv.index("--out") + 1], "w", encoding="utf-8").write(text)
    print(json.dumps(summary, indent=1, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv[1:])
