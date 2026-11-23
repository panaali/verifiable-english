"""Compare a run file with the sealed answers (sha256 checked). SAME-FAMILY. Committed BEFORE the headline run.

usage: python3 -I grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/stock/hos-driving [--out GRADES.json]
Reads <dir>/sealed/answers.jsonl (sha256 must equal the seal) and <dir>/questions-enc.jsonl (scope and kind; the
writer's tags are all "none", ISOLATION.md run 1, so questions.jsonl is not opened). Per in-scope question: match (VE's
answer equals the sealed answer: Q1 / Q3 yes or no; Q2 the minutes), disagree (VE answered differently: goes to two
fresh graders; VE certain and graded wrong = a WRONG answer), refused (two readings, D1), open, unsupported,
writer-ambiguous (the writer filled "ambiguous": not correct whatever VE says, D6). Probes apart.
The number = matches (+ disagreements both graders give to VE, added later from grader verdicts) over in scope.
"""
import hashlib
import json
import sys

SEALED_SHA256 = "e7a0f5080e1c401ef2416c2da771143373f1f844322cc35a1138317524ca4211"
ENC_SHA256 = "8a99acb9d630bed4e903c3f355a4feed69320d3eccc2575212b32c4eb2a1be68"


def yn(v):
    s = str(v).strip().lower()
    return "yes" if s.startswith("yes") else "no" if s.startswith("no") else s


def same(kind, ve, w):
    if kind in ("Q1", "Q3"):
        return ve.get("answer") in ("yes", "no") and yn(w.get("answer")) == ve.get("answer")
    if kind == "Q2":
        if ve.get("answer") != "DURATION":
            return False
        try:
            return int(str(w.get("value")).strip()) == int(ve.get("minutes"))
        except (TypeError, ValueError):
            return False
    raise ValueError(kind)


def main(argv):
    run = json.load(open(argv[0], encoding="utf-8"))
    d = argv[1]
    raw = open(d + "/sealed/answers.jsonl", "rb").read()
    if hashlib.sha256(raw).hexdigest() != SEALED_SHA256:
        raise SystemExit("sealed answers.jsonl sha256 differs from the seal")
    qraw = open(d + "/questions-enc.jsonl", "rb").read()
    if hashlib.sha256(qraw).hexdigest() != ENC_SHA256:
        raise SystemExit("questions-enc.jsonl sha256 differs from the seal")
    sealed = {a["qid"]: a for a in map(json.loads, raw.decode().splitlines()) if a}
    meta = {}
    for c in map(json.loads, qraw.decode().splitlines()):
        for x in c["questions"]:
            meta[x["qid"]] = {"scope": c["scope"], "kind": x["kind"], "case": c["id"]}
    ve = {qid: a for r in run["records"] for qid, a in r["answers"].items()}
    rows, count = [], {}
    for qid, mq in meta.items():
        w, a = sealed[qid], ve.get(qid, {"answer": "MISSING"})
        if mq["scope"] != "in":
            verdict = "probe-unsupported" if a["answer"] == "UNSUPPORTED" else "probe-answered"
        elif w.get("ambiguous"):
            verdict = "writer-ambiguous" + ("-agree" if same(mq["kind"], a, w) else "")
        elif a["answer"] == "REFUSED":
            verdict = "refused"
        elif a["answer"] == "OPEN":
            verdict = "open"
        elif a["answer"] == "UNSUPPORTED":
            verdict = "unsupported"
        else:
            verdict = "match" if same(mq["kind"], a, w) else "disagree"
        count[verdict] = count.get(verdict, 0) + 1
        rows.append({"qid": qid, "kind": mq["kind"], "scope": mq["scope"], "verdict": verdict, "ve": a,
                     "sealed": {"answer": w.get("answer"), "value": w.get("value")},
                     "ambiguous": bool(w.get("ambiguous"))})
    inscope = sum(1 for m in meta.values() if m["scope"] == "in")
    out = {"format": "hos-driving-grades@1", "label": "SAME-FAMILY", "run_commit": run.get("commit"),
           "run_tree_clean": run.get("tree_clean"), "in_scope": inscope, "counts": count,
           "number": f"{count.get('match', 0)}/{inscope}", "rows": rows}
    text = json.dumps(out, indent=1, sort_keys=True) + "\n"
    if "--out" in argv:
        open(argv[argv.index("--out") + 1], "w", encoding="utf-8").write(text)
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, sort_keys=True))
    for r in rows:
        if r["verdict"] in ("disagree", "writer-ambiguous", "writer-ambiguous-agree", "refused", "open"):
            print(r["qid"], r["verdict"], "VE", r["ve"], "sealed", r["sealed"])


if __name__ == "__main__":
    main(sys.argv[1:])
