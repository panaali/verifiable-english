"""Compare an HMO run file with the SEALED answers. SAME-FAMILY. Committed before the headline run.

The sealed file is checked against its sha256 (manage-agents reviews/spare/statute-corpus/hmo/ISOLATION.md) before it is read;
questions.jsonl (sha256 checked) gives each case's tag. 26 in-scope cases x 3 questions = 78 graded one by one:
  correct          VE's Lean-admitted answer equals the sealed answer (Q3: both lists equal as sets) and the sealed record
                   is not writer-ambiguous;
  writer-ambiguous the sealed record fills "ambiguous": not correct, listed (VE's agreement shown);
  refused          VE answered OPEN;
  disagreement     VE certain and different: goes to two fresh graders on different seats (verdicts added later as
                   GRADERS.json); until then not correct.
The number is reported with and without stated-judgment / bridge-only questions. Out-of-scope probes are reported apart.
Agreement audit: 15 correct questions drawn with random.Random(SEED).sample over their sorted ids.

Usage: python3 -I grade.py RUN.json SEALED_ANSWERS.jsonl QUESTIONS.jsonl [--out GRADES.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random

SEALED_SHA256 = "dcee61586d0c246adc3c7c09325072e5a7d7ef82dec4f5d06605e38df0fae555"
QUESTIONS_SHA256 = "58aa4b86012de495bc0ff41d4049d61794b1a8da7775d5b94a7f8a4bcfc6f290"
SEED = 20261123


def load(path, sha):
    raw = open(path, "rb").read()
    got = hashlib.sha256(raw).hexdigest()
    if got != sha:
        raise SystemExit(f"{path}: sha256 {got} is not the sealed {sha}")
    return {d["id"]: d for d in (json.loads(x) for x in raw.decode("utf-8").splitlines() if x.strip())}


def ve_value(answers, qq):
    v = answers.get(qq)
    if qq == "Q3" and isinstance(v, dict):
        return {"tests": sorted(v["tests"]), "sch14": sorted(v["sch14"])}
    return v


def sealed_value(rec, qq):
    if qq == "Q1":
        return rec["q1"]
    if qq == "Q2":
        return rec["q2"]
    return {"tests": sorted(rec["q3_tests"] or []), "sch14": sorted(rec["q3_sch14"] or [])}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("sealed")
    ap.add_argument("questions")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    run = json.load(open(a.run))
    sealed = load(a.sealed, SEALED_SHA256)
    questions = load(a.questions, QUESTIONS_SHA256)
    recs = {r["id"]: r for r in run["records"]}
    rows, probes = [], []
    for cid in sorted(questions):
        qrec, srec, vrec = questions[cid], sealed[cid], recs.get(cid)
        if qrec["scope"] == "out":
            probes.append({"id": cid, "sealed": srec["q1"], "ve": (vrec or {}).get("answers", {}).get("Q1")})
            continue
        for qq in ("Q1", "Q2", "Q3"):
            ve = ve_value(vrec["answers"], qq) if vrec else "MISSING"
            sv = sealed_value(srec, qq)
            if ve in ("OPEN", "MISSING", None):
                verdict = "refused"
            elif srec.get("ambiguous"):
                verdict = "writer-ambiguous"
            elif ve == sv:
                verdict = "correct"
            else:
                verdict = "disagreement"
            rows.append({"qid": f"{cid}/{qq}", "tag": qrec["tag"], "verdict": verdict, "ve": ve, "sealed": sv,
                         "agrees_with_sealed": ve == sv})
    def count(rs):
        out = {}
        for r in rs:
            out[r["verdict"]] = out.get(r["verdict"], 0) + 1
        return out
    plain = [r for r in rows if r["tag"] == "none"]
    correct = sorted(r["qid"] for r in rows if r["verdict"] == "correct")
    audit = sorted(random.Random(SEED).sample(correct, min(15, len(correct))))
    out = {"format": "hmo-grades@1", "label": "SAME-FAMILY", "run_commit": run.get("commit"),
           "run_sha256": hashlib.sha256(open(a.run, "rb").read()).hexdigest(),
           "number": {"correct": len(correct), "written": len(rows)},
           "number_excluding_stated_judgment_and_bridge_only": {
               "correct": sum(r["verdict"] == "correct" for r in plain), "written": len(plain)},
           "verdicts": count(rows), "verdicts_excluding": count(plain),
           "by_question": {qq: count([r for r in rows if r["qid"].endswith(qq)]) for qq in ("Q1", "Q2", "Q3")},
           "rows": rows, "probes": probes, "agreement_audit_seed": SEED, "agreement_audit": audit}
    text = json.dumps(out, indent=1, sort_keys=True) + "\n"
    if a.out:
        open(a.out, "w").write(text)
    print(json.dumps({k: out[k] for k in ("number", "number_excluding_stated_judgment_and_bridge_only", "verdicts",
                                          "by_question")}, indent=1))
    print("disagreements:", [r["qid"] for r in rows if r["verdict"] == "disagreement"])
    print("writer-ambiguous:", [r["qid"] for r in rows if r["verdict"] == "writer-ambiguous"])
    print("refused:", [r["qid"] for r in rows if r["verdict"] == "refused"])
    print("probes:", probes)
    print("audit:", audit)


if __name__ == "__main__":
    main()
