"""Compare a PAWHP run file with the SEALED answers (PAGE.md 'The number'). SAME-FAMILY. Committed before the headline run.

The sealed file is checked against its sha256 (ISOLATION.md) before it is read. Per in-scope person:
  Q1 always; Q2 only where the sealed Q1 is YES; Q3 only where the sealed Q3 is not null (an application stated).
Each question is:
  correct        VE's Lean-admitted answer equals the sealed answer (a writer-ambiguous record is listed apart: strict
                 rule, PAGE.md, counts it NOT correct);
  refused        VE answered OPEN (no single certified answer, or Lean did not admit the document);
  disagreement   VE certain and different: goes to two fresh graders on different seats (a grader-side verdict).
Out-of-scope probes are reported apart (sealed 'NOT SUPPORTED' vs VE 'UNSUPPORTED').
The agreement audit draws 15 correct questions with random.Random(SEED).sample over their sorted ids.

Usage: python grade.py RUN.json SEALED_ANSWERS.jsonl [--out GRADES.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from decimal import Decimal

SEALED_SHA256 = "bf8db1212c92abb159f0ae2b55a4c98c3468c91ef48699983eaf26aa4527f4ff"
SEED = 20261123


def money(v):
    try:
        return str(Decimal(str(v).replace("£", "").replace(",", "")).quantize(Decimal("0.01")))
    except Exception:  # noqa: BLE001
        return str(v)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("sealed")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    raw = open(a.sealed, "rb").read()
    got_sha = hashlib.sha256(raw).hexdigest()
    if got_sha != SEALED_SHA256:
        raise SystemExit(f"sealed answers sha256 {got_sha} != {SEALED_SHA256}")
    sealed = {d["id"]: d for d in (json.loads(x) for x in raw.decode("utf-8").splitlines() if x.strip())}
    run_raw = open(a.run, "rb").read()
    run = json.loads(run_raw)
    rows, probes = [], []
    for rec in run["records"]:
        s = sealed[rec["id"]]
        ve = rec["answers"]
        if rec.get("scope") == "out":
            probes.append({"id": rec["id"], "sealed_q1": s["q1"], "ve_q1": ve["Q1"],
                           "agree": s["q1"] == "NOT SUPPORTED" and ve["Q1"] == "UNSUPPORTED"})
            continue
        asked = [("Q1", s["q1"])]
        if s["q1"] == "YES":
            asked.append(("Q2", money(s["q2_gbp"]) if s["q2_gbp"] is not None else None))
        if s["q3"] is not None:
            asked.append(("Q3", s["q3"]))
        for qq, want in asked:
            mine = ve.get(qq, "MISSING")
            if qq == "Q2" and mine not in ("OPEN", "N/A", "MISSING"):
                mine = money(mine)
            if mine in ("OPEN", "MISSING", "UNSUPPORTED"):
                status = "refused"
            elif mine == want:
                status = "correct"
            else:
                status = "disagreement"
            rows.append({"qid": f"{rec['id']}/{qq}", "sealed": want, "ve": mine, "status": status,
                         "writer_ambiguous": s.get("ambiguous") is not None})
    n = len(rows)
    strict = [r for r in rows if r["status"] == "correct" and not r["writer_ambiguous"]]
    agreements = sorted(r["qid"] for r in rows if r["status"] == "correct")
    audit = sorted(random.Random(SEED).sample(agreements, min(15, len(agreements))))
    out = {"format": "pawhp-grades@1", "label": "SAME-FAMILY", "run_sha256": hashlib.sha256(run_raw).hexdigest(),
           "run_commit": run.get("commit"), "sealed_sha256": got_sha, "seed": SEED,
           "denominator_in_scope_questions": n,
           "correct_agreements_strict": len(strict),
           "agreements_in_writer_ambiguous_records": sum(r["status"] == "correct" and r["writer_ambiguous"] for r in rows),
           "refused": sum(r["status"] == "refused" for r in rows),
           "disagreements": [r for r in rows if r["status"] == "disagreement"],
           "by_question": {qq: {st: sum(r["status"] == st for r in rows if r["qid"].endswith(qq))
                                for st in ("correct", "refused", "disagreement")} for qq in ("Q1", "Q2", "Q3")},
           "audit_sample": audit, "probes": probes, "rows": rows}
    text = json.dumps(out, indent=1, sort_keys=True) + "\n"
    if a.out:
        open(a.out, "w", encoding="utf-8").write(text)
    summary = {k: out[k] for k in ("denominator_in_scope_questions", "correct_agreements_strict",
                                   "agreements_in_writer_ambiguous_records", "refused", "by_question")}
    summary["disagreements"] = len(out["disagreements"])
    summary["probes_agree"] = sum(p["agree"] for p in probes)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
