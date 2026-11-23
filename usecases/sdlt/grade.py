"""Compare a run file with the sealed answers (sha256 checked). SAME-FAMILY. Committed BEFORE the encoder's file was opened.

usage: python3 -I grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/batch2/sdlt [--out GRADES.json]
Reads <dir>/sealed/answers.jsonl (sha256 must equal the seal) and <dir>/questions.jsonl (scope, the writer's tags and
amount kinds). Per in-scope question: match (VE's answer equals the sealed answer: Q1 the amount to the penny; Q2 YES/NO;
Q3 NO RELIEF, or the amount to the penny), disagree (VE answered, differently: goes to two fresh graders; VE certain and
graded wrong = a WRONG answer), refused (OPEN), unsupported, writer-ambiguous (the writer filled "ambiguous": not correct
whatever VE says). Out-of-scope questions apart. Summary per tag, per amount kind and per kind combination
(SELECTION.md "Amount kinds"), and the in-scope questions that use no table-row unit (CHALLENGE B4).
The number = matches (+ disagreements both graders give to VE, added later from grader verdicts) over in-scope written.
"""
import hashlib
import json
import sys
from decimal import Decimal

SEALED_SHA256 = "531b416b8c86e2de05c87108eac6693921d97929a74459ac83193053ae8208c1"
QUESTIONS_SHA256 = "14988807af0ee6f43cf4505c24f6bbcc6b000877bec59eb70183dc8a33093a87"
KINDS = ("NEW-BAND", "NEW-TREP", "SUM", "PROD")


def money(v):
    return None if v in (None, "") else Decimal(str(v).replace("£", "").replace(",", "")).quantize(Decimal("0.01"))


def same(kind, ve, w):
    if ve.get("answer") != w.get("answer"):
        return False
    if w.get("answer") == "AMOUNT":
        return money(ve.get("gbp")) == money(w.get("gbp"))
    return True


def tally(rs):
    return {"written": len(rs), "match": sum(r["status"] == "match" for r in rs),
            "refused": sum(r["status"] == "refused" for r in rs),
            "unsupported": sum(r["status"] == "unsupported" for r in rs),
            "disagree": sum(r["status"] == "disagree" for r in rs),
            "writer_ambiguous": sum(r["status"].startswith("writer-ambiguous") for r in rs)}


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
                              "amount_kind": x.get("amount_kind", []), "covers": x.get("covers", [])}
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
        rows.append({"qid": qid, **m, "status": status, "ve": v, "writer": {k: w.get(k) for k in ("answer", "gbp")}})
    ins = [r for r in rows if r["scope"] == "in"]
    summary = {"in_scope_written": len(ins), **{k: v for k, v in tally(ins).items() if k != "written"},
               "by_tag": {t: tally([r for r in ins if r["tag"] == t]) for t in ("none", "bridge-only", "stated-judgment")},
               "by_question_kind": {k: tally([r for r in ins if r["kind"] == k]) for k in ("Q1", "Q2", "Q3")},
               "by_amount_kind": {k: tally([r for r in ins if k in r["amount_kind"]]) for k in KINDS},
               "by_amount_kind_set": {"+".join(s) or "none": tally([r for r in ins if tuple(r["amount_kind"]) == s])
                                      for s in sorted({tuple(r["amount_kind"]) for r in ins})},
               "no_table_row_unit": tally([r for r in ins if not r["amount_kind"]]),
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
