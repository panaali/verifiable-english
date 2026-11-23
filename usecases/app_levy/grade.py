"""Compare a run file with the sealed answers (sha256 checked). SAME-FAMILY. Committed BEFORE the headline run.

usage: python3 -I grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/stock/app-levy [--out GRADES.json]
Reads <dir>/sealed/answers.jsonl (sha256 must equal the seal) and <dir>/questions.jsonl (scope and the writer's tags).
Per in-scope question: match (VE's answer equals the sealed answer: Q1 yes / no; Q2 and Q3 GBP to the penny), disagree
(VE answered, differently: goes to two fresh graders; VE certain and graded wrong = a WRONG answer), refused (OPEN),
unsupported, writer-ambiguous (the writer filled "ambiguous": not correct whatever VE says). Probes apart.
Side numbers by ACTUAL USE (batch 2 audits): this law has no table row (units.jsonl: 0), so "excluding table rows" is
the headline; outside Lean = the writer tagged it stated-judgment / bridge-only, or flips.json shows a stated judgment or
an encoder judgement decides it (flips.py, committed with the cases, never reads answers). Amount kinds (Q2, Q3) from
the encoder's case (cases.py), batch 2's names: LIN (0.5 % and N - A; GBP 15,000), SUM (a pay bill over two or more
earnings items; a determination's amounts totalling GBP 15,000), PROD (15,000 / N over the members; 15,000 / T).
"""
import hashlib
import json
import re
import sys
from decimal import Decimal
from pathlib import Path

SEALED_SHA256 = "bdf682783ef26498dbcf63818c2479c508756ab6a450256d282b4851401b051c"
QUESTIONS_SHA256 = "e8b5d606b22a28db380a092454a95f1f16feaa0a0b380b29c338a2b00037dede"
TABLE_UNITS = set()
HERE = Path(__file__).resolve().parent


def number(v):
    if v in (None, ""):
        return None
    m = re.search(r"-?\d[\d,]*(?:\.\d+)?", str(v))
    return None if m is None else Decimal(m.group(0).replace(",", ""))


def same(kind, ve, w):
    if kind == "Q1":
        first = str(w.get("answer", "")).strip().lower().split()
        return bool(first) and first[0].strip(".,;:") == ve.get("answer")
    if kind in ("Q2", "Q3"):
        wv = number(w.get("value")) if w.get("value") not in (None, "") else number(w.get("answer"))
        return ve.get("answer") == "AMOUNT" and wv is not None and Decimal(ve["gbp"]) == wv.quantize(Decimal("0.01"))
    raise ValueError(kind)


def kinds():
    """qid -> amount kind for Q2 / Q3, from the encoder's case only."""
    sys.path.insert(0, str(HERE))
    import cases as K
    out = {}
    for c in K.CASES:
        f = set(c["facts"])
        route13 = "not_taken13:g" in f and all(f"notified13:{x}" in f for x in c["groups"].get("g", []))
        route8 = "not_taken8:g" in f
        for q in c["questions"]:
            x = q["item"]
            k = ["LIN"]
            if q["form"] == "amount" and len([j for j, p in c["earnings"].items() if p == x]) > 1:
                k.append("SUM")
            if c["groups"] and x in c["groups"].get("g", []):
                if "detmade:g" in f:
                    k.append("SUM-det")
                if route13:
                    k.append("PROD-N")
                if route8:
                    k.append("PROD-T")
            if q["form"] != "charged":
                out[q["qid"]] = "+".join(k)
    return out


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
    encoder = {q for v in flips["encoder"].values() for q in v["changed"]}
    akind = kinds()
    sealed = {a["qid"]: a for a in map(json.loads, raw.decode().splitlines()) if a}
    meta = {}
    for c in map(json.loads, qraw.decode().splitlines()):
        for x in c["questions"]:
            meta[x["qid"]] = {"scope": c["scope"], "kind": x["kind"], "tag": x["tag"]}
    ve = {q: a for r in run["records"] for q, a in r["answers"].items()}
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
        outside = sorted(x for x, hit in (("tag", m["tag"] != "none"), ("stated", qid in stated),
                                          ("encoder", qid in encoder)) if hit)
        rows.append({"qid": qid, **m, "status": status, "ve": v, "uses_table_row": False,
                     "outside": outside, "amount_kind": akind.get(qid) if m["kind"] != "Q1" else None,
                     "writer": {k: w.get(k) for k in ("answer", "value")},
                     "writer_ambiguous": bool(w.get("ambiguous"))})
    ins = [r for r in rows if r["scope"] == "in"]
    count = lambda rs, st: sum(r["status"] == st for r in rs)  # noqa: E731
    sub = lambda rs: {"written": len(rs), "match": count(rs, "match")}  # noqa: E731
    summary = {"in_scope_written": len(ins), "match": count(ins, "match"), "disagree": count(ins, "disagree"),
               "refused": count(ins, "refused"), "unsupported": count(ins, "unsupported"),
               "writer_ambiguous": sum(r["status"].startswith("writer-ambiguous") for r in ins),
               "writer_ambiguous_qids": sorted(r["qid"] for r in ins if r["writer_ambiguous"]),
               "by_tag": {t: sub([r for r in ins if r["tag"] == t]) for t in ("none", "bridge-only", "stated-judgment")},
               "without_outside_lean": sub([r for r in ins if not r["outside"]]),
               "excluding_table_rows_by_use": sub([r for r in ins if not r["uses_table_row"]]),
               "by_question_kind": {k: sub([r for r in ins if r["kind"] == k]) for k in ("Q1", "Q2", "Q3")},
               "amount_by_kind": {k: sub([r for r in ins if r["amount_kind"] == k])
                                  for k in sorted({r["amount_kind"] for r in ins if r["amount_kind"]})},
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
