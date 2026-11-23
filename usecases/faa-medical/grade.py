"""Compare a 14 CFR 61.23 run file with the SEALED answers (ISOLATION.md; law 1's grade.py adapted). SAME-FAMILY.
Committed before the headline run.

The sealed answers and questions.jsonl are checked against their sha256 (ISOLATION.md seal) before they are read. Per
in-scope case (questions.jsonl "scope" = "in"):
  Q1 and Q2 always; Q3 only where the sealed Q2 is YES (ISOLATION.md D6, fixed before the writer ran).
Each question is:
  correct        VE's Lean-admitted answer equals the sealed answer (a writer-ambiguous record is counted apart: the
                 strict count, law 1's rule, counts it NOT correct);
  refused        VE answered OPEN or UNSUPPORTED (no single certified answer, no Lean-admitted document, or not encodable);
  disagreement   VE certain and different: goes to two fresh graders on different seats (a grader-side verdict).
The number is reported twice (SELECTION.md counting rule): all in-scope questions, and excluding those the writer tagged
bridge-only or stated-judgment. Out-of-scope probes are reported apart (sealed NOT SUPPORTED: VE agrees when it gave no
answer, UNSUPPORTED or OPEN, to all three questions). The agreement audit draws 15 correct questions with
random.Random(SEED).sample over their sorted ids.

Usage: python3 -I grade.py RUN.json SEALED_ANSWERS.jsonl QUESTIONS.jsonl [--out GRADES.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random

SEALED_SHA256 = "23126e226fb5e590fa335de3acf787d65af911cba986cff2b9630d8d7a5e55f6"
QUESTIONS_SHA256 = "70dbc8e12b7b5e221db1f96b6fc2bcfc3a5b23ee10faec3f1e3e2b4306918fcf"
SEED = 20261123
NO_ANSWER = ("OPEN", "UNSUPPORTED", "MISSING")


def load(path, sha):
    raw = open(path, "rb").read()
    got = hashlib.sha256(raw).hexdigest()
    if got != sha:
        raise SystemExit(f"{path}: sha256 {got} != {sha}")
    return {d["id"]: d for d in (json.loads(x) for x in raw.decode("utf-8").splitlines() if x.strip())}, got


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("sealed")
    ap.add_argument("questions")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    sealed, sealed_sha = load(a.sealed, SEALED_SHA256)
    questions, _ = load(a.questions, QUESTIONS_SHA256)
    run_raw = open(a.run, "rb").read()
    run = json.loads(run_raw)
    by_id = {r["id"]: r for r in run["records"]}
    rows, probes = [], []
    for pid in sorted(questions):
        s, ve = sealed[pid], by_id.get(pid, {}).get("answers", {})
        if questions[pid]["scope"] != "in":
            probes.append({"id": pid, "sealed": [s["q1"], s["q2"], s["q3"]],
                           "ve": [ve.get("Q1", "MISSING"), ve.get("Q2", "MISSING"), ve.get("Q3", "MISSING")],
                           "agree": all(ve.get(q, "MISSING") in NO_ANSWER for q in ("Q1", "Q2", "Q3"))})
            continue
        asked = [("Q1", s["q1"]), ("Q2", s["q2"])]
        if s["q2"] == "YES":
            asked.append(("Q3", s["q3"]))
        for qq, want in asked:
            mine = ve.get(qq, "MISSING")
            status = "refused" if mine in NO_ANSWER else "correct" if mine == want else "disagreement"
            rows.append({"qid": f"{pid}/{qq}", "sealed": want, "ve": mine, "status": status,
                         "writer_ambiguous": s.get("ambiguous") is not None,
                         "tag": (s.get("tags") or {}).get(qq, "none")})
    n = len(rows)
    strict = [r for r in rows if r["status"] == "correct" and not r["writer_ambiguous"]]
    plain = [r for r in rows if r["tag"] not in ("bridge-only", "stated-judgment")]
    plain_strict = [r for r in plain if r["status"] == "correct" and not r["writer_ambiguous"]]
    agreements = sorted(r["qid"] for r in rows if r["status"] == "correct")
    audit = sorted(random.Random(SEED).sample(agreements, min(15, len(agreements))))
    out = {"format": "faa-medical-grades@1", "label": "SAME-FAMILY", "run_sha256": hashlib.sha256(run_raw).hexdigest(),
           "run_commit": run.get("commit"), "run_tree_clean": run.get("tree_clean"), "sealed_sha256": sealed_sha,
           "seed": SEED, "denominator_in_scope_questions": n,
           "correct_agreements_strict": len(strict),
           "agreements_in_writer_ambiguous_records": sum(r["status"] == "correct" and r["writer_ambiguous"] for r in rows),
           "refused": sum(r["status"] == "refused" for r in rows),
           "disagreements": [r for r in rows if r["status"] == "disagreement"],
           "excluding_bridge_only_and_stated_judgment": {"denominator": len(plain), "correct_strict": len(plain_strict)},
           "tags": {t: sum(r["tag"] == t for r in rows) for t in ("none", "bridge-only", "stated-judgment")},
           "by_question": {qq: {st: sum(r["status"] == st for r in rows if r["qid"].endswith(qq))
                                for st in ("correct", "refused", "disagreement")} for qq in ("Q1", "Q2", "Q3")},
           "audit_sample": audit, "probes": probes, "rows": rows}
    text = json.dumps(out, indent=1, sort_keys=True) + "\n"
    if a.out:
        open(a.out, "w", encoding="utf-8").write(text)
    summary = {k: out[k] for k in ("denominator_in_scope_questions", "correct_agreements_strict",
                                   "agreements_in_writer_ambiguous_records", "refused", "by_question",
                                   "excluding_bridge_only_and_stated_judgment", "tags")}
    summary["disagreements"] = len(out["disagreements"])
    summary["probes_agree"] = f"{sum(p['agree'] for p in probes)} of {len(probes)}"
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
