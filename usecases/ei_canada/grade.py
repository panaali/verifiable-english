"""Grade a run file against the sealed answers (sha256 checked). Committed BEFORE the headline run.

usage: python3 -I usecases/ei_canada/grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/batch2/ei-canada [--out G.json]

Strict comparison: Q1 the word (YES/NO); Q2 the word and the number of weeks (or NONE); Q3 the word and the amount to the
cent (or NONE). A question the writer marked ambiguous counts not correct (writer-ambiguous) whatever VE says. OPEN,
UNSUPPORTED and refused answers are not correct. Probes (scope out) are reported apart.
"""
import hashlib
import json
import sys
from decimal import Decimal

SEAL = {"sealed/answers.jsonl": "50a6e6ebaaa91a922495e296884f6f17834d2723840c567bf9fef8c6c8e43c03",
        "questions.jsonl": "ee7784374c00baf872317ec7a64fe55faf1696c8deb4658c5290eff733f077cd"}


def same(ve, s, kind):
    a = ve.get("answer")
    if kind == "Q1":
        return a in ("YES", "NO") and a == s["answer"]
    if a == "NONE" or s["answer"] == "NONE":
        return a == s["answer"]
    if kind == "Q2":
        return a == "WEEKS" and s["answer"] == "WEEKS" and int(ve["weeks"]) == int(s["weeks"])
    if kind == "Q3":
        return a == "CAD" and s["answer"] == "CAD" and Decimal(ve["cad"]) == Decimal(s["cad"])
    return False


def main(argv):
    run, d = argv[0], argv[1]
    for f, h in SEAL.items():
        got = hashlib.sha256(open(f"{d}/{f}", "rb").read()).hexdigest()
        if got != h:
            sys.exit(f"seal mismatch: {f} {got}")
    sealed = {a["qid"]: a for a in map(json.loads, open(f"{d}/sealed/answers.jsonl")) if a}
    qs = {}
    for line in open(f"{d}/questions.jsonl"):
        c = json.loads(line)
        for q in c["questions"]:
            qs[q["qid"]] = dict(q, scope=c["scope"], case=c["id"])
    R = json.load(open(run))
    ve = {qid: a for r in R["records"] for qid, a in r["answers"].items()}
    rows, summ = {}, {}
    for qid, q in qs.items():
        s, v = sealed[qid], ve.get(qid, {"answer": "MISSING"})
        if q["scope"] == "out":
            st = "probe-unsupported" if v["answer"] == "UNSUPPORTED" else "probe-answered"
        elif s.get("ambiguous"):
            st = "writer-ambiguous"
        elif v["answer"] in ("OPEN", "MISSING"):
            st = "refused" if not v.get("lean_rejected") else "lean-rejected"
        elif v["answer"] == "UNSUPPORTED":
            st = "unsupported"
        elif same(v, s, q["kind"]):
            st = "correct"
        else:
            st = "disagree"
        rows[qid] = {"status": st, "kind": q["kind"], "tag": q["tag"], "akind": q.get("akind"), "ve": v,
                     "sealed": {k: s[k] for k in ("answer", "weeks", "cad", "ambiguous")}}
        summ[st] = summ.get(st, 0) + 1
    ins = [r for r in rows.values() if r["status"] not in ("probe-unsupported", "probe-answered")]
    out = {"run": run, "run_sha256": hashlib.sha256(open(run, "rb").read()).hexdigest(), "summary": summ,
           "in_scope": len(ins), "correct": sum(r["status"] == "correct" for r in ins), "rows": rows}
    if "--out" in argv:
        json.dump(out, open(argv[argv.index("--out") + 1], "w"), indent=1, sort_keys=True)
    print(json.dumps({k: out[k] for k in ("run_sha256", "summary", "in_scope", "correct")}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
