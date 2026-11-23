"""Compare a run file with the sealed answers (sha256 checked). SAME-FAMILY. Committed BEFORE the headline run.

usage: python3 -I grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/stock/eu-sea-passengers [--out GRADES.json]
Reads <dir>/sealed/answers.jsonl (sha256 must equal the seal) and <dir>/questions.jsonl (scope and the writer's tags).
Per in-scope question: match (VE's answer equals the sealed answer: Q1 / Q2 yes / no; Q3 EUR to the cent), disagree (VE
answered, differently: goes to two fresh graders; VE certain and graded wrong = a WRONG answer), refused (OPEN),
unsupported, writer-ambiguous (the writer filled "ambiguous": not correct whatever VE says). Probes apart.
Side numbers by ACTUAL USE (batch 2 audits): this law has no table row (units.jsonl: 0), so "excluding table rows" is
the headline; outside Lean = the writer tagged it stated-judgment / bridge-only, or flips.json shows a stated judgment or
an encoder judgement decides it (flips.py, committed with the cases, never reads answers). Q3 amount kinds from the
encoder's case (cases.py): LIN (25 / 50 % of the price), PROD-literal (a return: half the return price), THRESHOLD (the
carrier states a threshold).
"""
import hashlib
import json
import re
import sys
from decimal import Decimal
from pathlib import Path

SEALED_SHA256 = "1b967b67fac93ae897caef6675b9dc22681f6bde87404a6a39ee170944af5107"
QUESTIONS_SHA256 = "8b3b9b60e11a2f3034ce5f7ef6491b3791787dc72f2305df55e05658918efa2e"
TABLE_UNITS = set()
HERE = Path(__file__).resolve().parent


def number(v):
    if v in (None, ""):
        return None
    m = re.search(r"-?\d[\d,]*(?:\.\d+)?", str(v))
    return None if m is None else Decimal(m.group(0).replace(",", ""))


def same(kind, ve, w):
    if kind in ("Q1", "Q2"):
        first = str(w.get("answer", "")).strip().lower().split()
        return bool(first) and first[0].strip(".,;:") == ve.get("answer")
    if kind == "Q3":
        wv = number(w.get("value")) if w.get("value") not in (None, "") else number(w.get("answer"))
        return ve.get("answer") == "AMOUNT" and wv is not None and Decimal(ve["eur"]) == wv.quantize(Decimal("0.01"))
    raise ValueError(kind)


def kinds():
    sys.path.insert(0, str(HERE))
    import cases as K
    out = {}
    for c in K.CASES:
        k = ["LIN"]
        if "ret" in c["facts"]:
            k.append("PROD-literal")
        if "has_thr" in c["facts"]:
            k.append("THRESHOLD")
        out[c["id"]] = "+".join(k)
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
                                          ("encoder", qid in encoder)) if hit)
        rows.append({"qid": qid, **m, "status": status, "ve": v, "uses_table_row": bool(TABLE_UNITS & set(u["units"])),
                     "outside": outside, "amount_kind": akind.get(qid[:4]) if m["kind"] == "Q3" else None,
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
               "q3_by_amount_kind": {k: sub([r for r in ins if r["amount_kind"] == k])
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
