"""Compare a run file with the sealed answers (sha256 checked). SAME-FAMILY. Committed BEFORE the headline run.

usage: python3 -I grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/stock/fwa-australia [--out GRADES.json]
Reads <dir>/sealed/answers.jsonl (sha256 must equal the seal) and <dir>/questions.jsonl (scope and the writer's tags).
Per in-scope question: match (VE's answer equals the sealed answer: Q1 weeks or "none"; Q2 yes / no; Q3 AUD to the cent),
disagree (VE answered, differently: goes to two fresh graders; VE certain and graded wrong = a WRONG answer), refused
(OPEN), unsupported, writer-ambiguous (the writer filled "ambiguous": not correct whatever VE says). Probes apart.
Side numbers by ACTUAL USE (batch 2 audits): table rows = the answer's admitted documents contain a table-row unit
(4-7, 11-20); outside Lean = the writer tagged it stated-judgment / bridge-only, or flips.json shows a stated judgment,
the bridged age or an encoder judgement decides it (flips.py, committed with the cases, never reads answers).
"""
import hashlib
import json
import re
import sys
from decimal import Decimal
from pathlib import Path

SEALED_SHA256 = "981f999e7c3c2879280e2c6c5eadf3f1abe2b63be0849a45de8bc843d5855e71"
QUESTIONS_SHA256 = "a4e7ca1967cc754bb9932f427424c51968dc7860d287353ce9741b5152bae8e2"
TABLE_UNITS = set(range(4, 8)) | set(range(11, 21))
HERE = Path(__file__).resolve().parent


def number(v):
    if v in (None, ""):
        return None
    m = re.search(r"-?\d[\d,]*(?:\.\d+)?", str(v))
    return None if m is None else Decimal(m.group(0).replace(",", ""))


def writer_none(w):
    return (str(w.get("answer", "")).strip().lower().startswith("none")
            or str(w.get("value", "")).strip().lower() == "none"
            or (w.get("value") in (None, "") and "none" in str(w.get("answer", "")).lower()))


def same(kind, ve, w):
    if kind == "Q1":
        if ve.get("answer") == "none" or writer_none(w):
            return ve.get("answer") == "none" and writer_none(w)
        wv = number(w.get("value")) if w.get("value") not in (None, "") else number(w.get("answer"))
        return ve.get("answer") == "DURATION" and wv is not None and Decimal(ve["weeks"]) == wv
    if kind == "Q2":
        first = str(w.get("answer", "")).strip().lower().split()
        return bool(first) and first[0].strip(".,;:") == ve.get("answer")
    if kind == "Q3":
        wv = number(w.get("value")) if w.get("value") not in (None, "") else number(w.get("answer"))
        return ve.get("answer") == "AMOUNT" and wv is not None and Decimal(ve["aud"]) == wv.quantize(Decimal("0.01"))
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
    stated = {q for qs in flips["stated"].values() for q in qs}
    bridge = set(flips["bridge_decisive"])
    encoder = {q for v in flips["encoder"].values() for q in v["changed"]}
    sealed = {a["qid"]: a for a in map(json.loads, raw.decode().splitlines()) if a}
    meta = {}
    for c in map(json.loads, qraw.decode().splitlines()):
        for x in c["questions"]:
            meta[x["qid"]] = {"scope": c["scope"], "kind": x["kind"], "tag": x["tag"],
                              "form": "piln" if "payment in lieu" in x["text"] else None}
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
        outside = sorted(x for x, hit in (("tag", m["tag"] != "none"), ("stated", qid in stated),
                                          ("bridge", qid in bridge), ("encoder", qid in encoder)) if hit)
        rows.append({"qid": qid, **m, "status": status, "ve": v, "uses_table_row": bool(TABLE_UNITS & set(u["units"])),
                     "outside": outside, "writer": {k: w.get(k) for k in ("answer", "value")}})
    ins = [r for r in rows if r["scope"] == "in"]
    count = lambda rs, st: sum(r["status"] == st for r in rs)  # noqa: E731
    sub = lambda rs: {"written": len(rs), "match": count(rs, "match")}  # noqa: E731
    summary = {"in_scope_written": len(ins), "match": count(ins, "match"), "disagree": count(ins, "disagree"),
               "refused": count(ins, "refused"), "unsupported": count(ins, "unsupported"),
               "writer_ambiguous": sum(r["status"].startswith("writer-ambiguous") for r in ins),
               "by_tag": {t: sub([r for r in ins if r["tag"] == t]) for t in ("none", "bridge-only", "stated-judgment")},
               "without_outside_lean": sub([r for r in ins if not r["outside"]]),
               "excluding_table_rows_by_use": sub([r for r in ins if not r["uses_table_row"]]),
               "by_question_kind": {k: sub([r for r in ins if r["kind"] == k]) for k in ("Q1", "Q2", "Q3")},
               "q3_by_form": {"redundancy pay (PROD: table weeks x weekly base rate)":
                              sub([r for r in ins if r["kind"] == "Q3" and r["form"] != "piln"]),
                              "payment in lieu (PROD: weeks x weekly full rate; +1 week LIN)":
                              sub([r for r in ins if r["kind"] == "Q3" and r["form"] == "piln"])},
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
