"""Compare a run file with the sealed answers (sha256 checked). SAME-FAMILY. Committed BEFORE the headline run.

usage: python3 -I grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/tenant-fees [--out GRADES.json]
Reads <dir>/sealed/answers.jsonl (sha256 must equal the seal) and <dir>/questions.jsonl (scope and the writer's tags).
Per in-scope question: match (VE's answer equals the sealed answer: Q1 answer; Q2 amount; Q3 answer, amount and date),
disagree (VE answered, differently: goes to two fresh graders; VE certain and graded wrong = a WRONG answer), refused
(OPEN), unsupported, writer-ambiguous (the writer filled "ambiguous": not correct whatever VE says). Probes apart.
The number = matches (+ disagreements both graders give to VE, added later from grader verdicts) over in-scope written.
"""
import hashlib
import json
import sys
from decimal import Decimal

SEALED_SHA256 = "29986a727135cd6cc989f7e18ceec91d7d2d188b061c0332dffca854258a0b9f"
QUESTIONS_SHA256 = "c5f1979dc9d70aa45746058eb830b15f18e69c5c20ac70e6e4b259119a4b50c9"


def money(v):
    return None if v in (None, "") else Decimal(str(v).replace("£", "").replace(",", "")).quantize(Decimal("0.01"))


def same(kind, ve, w):
    if kind == "Q1":
        return ve.get("answer") == w.get("answer")
    if kind == "Q2":
        return ve.get("answer") == "AMOUNT" and money(ve.get("gbp")) == money(w.get("gbp"))
    if kind == "Q3":
        if ve.get("answer") != w.get("answer"):
            return False
        if w.get("answer") == "NO":
            return True
        return money(ve.get("gbp")) == money(w.get("gbp")) and (ve.get("date") or "") == (w.get("date") or "")
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
        rows.append({"qid": qid, **m, "status": status, "ve": v, "writer": {k: w.get(k) for k in ("answer", "gbp", "date")}})
    ins = [r for r in rows if r["scope"] == "in"]
    plain = [r for r in ins if r["tag"] == "none"]
    count = lambda rs, st: sum(r["status"] == st for r in rs)  # noqa: E731
    summary = {"in_scope_written": len(ins), "match": count(ins, "match"), "disagree": count(ins, "disagree"),
               "refused": count(ins, "refused"), "unsupported": count(ins, "unsupported"),
               "writer_ambiguous": sum(r["status"].startswith("writer-ambiguous") for r in ins),
               "excluding_bridge_and_stated": {"written": len(plain), "match": count(plain, "match"),
                                               "disagree": count(plain, "disagree")},
               "by_tag": {t: {"written": sum(r["tag"] == t for r in ins),
                              "match": sum(r["tag"] == t and r["status"] == "match" for r in ins)}
                          for t in ("none", "bridge-only", "stated-judgment")},
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
