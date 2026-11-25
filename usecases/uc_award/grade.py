"""Compare a run file with the sealed answers (sha256 checked). SAME-FAMILY. Committed BEFORE the headline run.

usage: python3 -I grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/batch2/uc-award [--out GRADES.json]
Reads <dir>/sealed/answers.jsonl (sha256 must equal the seal) and <dir>/questions.jsonl (scope, covers, the writer's tags).
Per in-scope question: match (VE's answer equals the sealed answer: Q1, Q2 the amount to the penny; Q3 SINGLE/JOINT and
the row), disagree (VE answered, differently: goes to two fresh graders; VE certain and graded wrong = a WRONG answer),
refused (OPEN), unsupported, writer-ambiguous (the writer filled "ambiguous": not correct whatever VE says, ISOLATION D11).
Probes apart. Also: the fourth number (CHALLENGE B4: in-scope questions whose covers name no table-row unit) and the
amount kinds (ISOLATION D8: the run record's amount_kind, set by encode rule from the case facts).
"""
import hashlib
import json
import sys
from decimal import Decimal

SEALED_SHA256 = "0c0bac1506127103a43dd824443506d4a3b4f7d8990e3ca28f590e3b9775de0d"
QUESTIONS_SHA256 = "1beb0fb72156a17104accd63004f0141ea543d2e78d928e49333172b27e96b24"
TABLE_PREFIXES = ("reg. 22 table", "reg. 36 table")


def money(v):
    return None if v in (None, "") else Decimal(str(v).replace("£", "").replace(",", "")).quantize(Decimal("0.01"))


def same(kind, ve, w):
    if kind in ("Q1", "Q2"):
        return ve.get("answer") == "AMOUNT" and money(ve.get("gbp")) == money(w.get("gbp"))
    if kind == "Q3":
        return ve.get("answer") == w.get("answer") and (ve.get("row") or "") == (w.get("row") or "")
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
    sealed = {a["qid"]: a for a in map(json.loads, raw.decode().splitlines()) if a}
    meta = {}
    for c in map(json.loads, qraw.decode().splitlines()):
        for x in c["questions"]:
            meta[x["qid"]] = {"scope": c["scope"], "kind": x["kind"], "tag": x["tag"],
                              "table": any(cv.startswith(TABLE_PREFIXES) for cv in x["covers"])}
    ve, akind = {}, {}
    for r in run["records"]:
        for q, a in r["answers"].items():
            ve[q] = a
            akind[q] = r.get("amount_kind")
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
        kind = akind.get(qid) if m["kind"] in ("Q1", "Q2") else None
        rows.append({"qid": qid, **m, "amount_kind": kind, "status": status, "ve": v,
                     "writer": {k: w.get(k) for k in ("answer", "gbp", "row")}})
    ins = [r for r in rows if r["scope"] == "in"]
    count = lambda rs, st: sum(r["status"] == st for r in rs)  # noqa: E731

    def block(rs):
        return {"written": len(rs), "match": count(rs, "match"), "disagree": count(rs, "disagree"),
                "refused": count(rs, "refused"), "unsupported": count(rs, "unsupported"),
                "writer_ambiguous": sum(r["status"].startswith("writer-ambiguous") for r in rs)}
    summary = {"in_scope": block(ins),
               "excluding_stated_judgment": block([r for r in ins if r["tag"] == "none"]),
               "by_tag": {t: block([r for r in ins if r["tag"] == t]) for t in ("none", "bridge-only", "stated-judgment")},
               "excluding_table_rows": block([r for r in ins if not r["table"]]),
               "by_question_kind": {k: block([r for r in ins if r["kind"] == k]) for k in ("Q1", "Q2", "Q3")},
               "by_amount_kind": {k: block([r for r in ins if r["amount_kind"] == k])
                                  for k in sorted({r["amount_kind"] for r in ins if r["amount_kind"]})},
               "probes": {"written": len(rows) - len(ins),
                          "unsupported": sum(r["status"] == "probe-unsupported" for r in rows)},
               "run_commit": run["commit"], "run_tree_clean": run["tree_clean"]}
    out = {"summary": summary, "rows": rows}
    text = json.dumps(out, indent=1, sort_keys=True) + "\n"
    if "--out" in argv:
        open(argv[argv.index("--out") + 1], "w", encoding="utf-8").write(text)
    print(json.dumps(summary, indent=1, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv[1:])
