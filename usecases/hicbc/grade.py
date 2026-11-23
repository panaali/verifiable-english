"""Compare a HICBC run file with the sealed answers (sha256 checked). Committed before the headline run. SAME-FAMILY.

The number (manage-agents reviews/spare/statute-corpus/SELECTION.md counting rule; law 1's PAGE.md 'The number'):
in-scope questions answered correctly / in-scope questions written. Questions: Q1 and Q3 of every in-scope household, Q2
where the sealed Q1 is YES. Correct = VE's Lean-admitted answer equals the sealed answer (Q2 as whole pounds, Q3 as a set of
names), or, for a disagreement, two fresh graders on different seats both side with VE (--grades FILE: {"id","q","verdicts"}).
Not correct, listed: refused (OPEN), unsupported, disputed (graders split), writer-ambiguous (the household's sealed record
has "ambiguous" filled: every question of it), and wrong (VE certain, graded wrong: must be 0). Reported beside: the number
without bridge-only and stated-judgment questions (writer's tags), and the probes.

Usage: python3 -I usecases/hicbc/grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/hicbc/sealed/answers.jsonl [--grades G.jsonl]
"""
import hashlib
import json
import sys

SEALED_SHA256 = "9f98854d19eb65b14ac4afbc0529c682ddb5d5ae8adeebcd7bbf400143a945b0"


def norm(q, v):
    if v is None:
        return None
    if q == "Q3":
        return sorted(v) if isinstance(v, list) else v
    if q == "Q2":
        s = str(v).replace("£", "").replace(",", "").strip()
        try:
            return int(float(s)) if float(s) == int(float(s)) else s
        except ValueError:
            return s
    return v


def main(argv):
    run_path, sealed_path = argv[0], argv[1]
    grades = {}
    if "--grades" in argv:
        for l in open(argv[argv.index("--grades") + 1], encoding="utf-8"):
            if l.strip():
                g = json.loads(l)
                grades[(g["id"], g["q"])] = g["verdicts"]
    raw = open(sealed_path, "rb").read()
    if hashlib.sha256(raw).hexdigest() != SEALED_SHA256:
        sys.exit("sealed answers.jsonl sha256 mismatch")
    sealed = {json.loads(l)["id"]: json.loads(l) for l in raw.decode("utf-8").splitlines() if l.strip()}
    run = json.load(open(run_path, encoding="utf-8"))
    rows, probes = [], []
    for rec in run["records"]:
        s = sealed[rec["id"]]
        if rec.get("scope") == "out":
            probes.append({"id": rec["id"], "ve": rec["answers"]["Q1"], "sealed": s["q1"]})
            continue
        qs = ["Q1", "Q3"] + (["Q2"] if s["q1"] == "YES" else [])
        for qq in sorted(qs):
            want = norm(qq, s[{"Q1": "q1", "Q2": "q2_gbp", "Q3": "q3"}[qq]])
            got = rec["answers"].get(qq)
            tag = (s.get("tags") or {}).get(qq) or "none"
            row = {"id": rec["id"], "q": qq, "ve": got, "sealed": want, "tag": tag}
            if got in ("OPEN", None, "N/A"):
                row["status"] = "refused" if got != "N/A" else "wrong"   # N/A = VE said NO where the writer said YES
            elif got == "UNSUPPORTED":
                row["status"] = "unsupported"
            elif norm(qq, got) == want:
                row["status"] = "correct"
            else:
                v = grades.get((rec["id"], qq))
                if v is None:
                    row["status"] = "disagree-ungraded"
                elif all(x == "VE" for x in v):
                    row["status"] = "correct-by-graders"
                elif all(x == "WRITER" for x in v):
                    row["status"] = "wrong"
                else:
                    row["status"] = "disputed"
                row["verdicts"] = v
            if s.get("ambiguous") and row["status"] in ("correct", "correct-by-graders"):
                row["status"] = "writer-ambiguous"
            rows.append(row)
    ok = ("correct", "correct-by-graders")
    n = len(rows)
    c = sum(r["status"] in ok for r in rows)
    core = [r for r in rows if r["tag"] not in ("bridge-only", "stated-judgment")]
    by = {}
    for r in rows:
        by[r["status"]] = by.get(r["status"], 0) + 1
    out = {"headline": f"{c} / {n}", "correct": c, "written": n,
           "excluding_bridge_only_and_stated_judgment": f"{sum(r['status'] in ok for r in core)} / {len(core)}",
           "bridge_only": f"{sum(r['status'] in ok for r in rows if r['tag'] == 'bridge-only')} / {sum(r['tag'] == 'bridge-only' for r in rows)}",
           "stated_judgment": f"{sum(r['status'] in ok for r in rows if r['tag'] == 'stated-judgment')} / {sum(r['tag'] == 'stated-judgment' for r in rows)}",
           "by_status": by, "wrong": [r for r in rows if r["status"] == "wrong"],
           "not_correct": [r for r in rows if r["status"] not in ok],
           "probes": probes, "run_commit": run["commit"], "run_tree_clean": run["tree_clean"],
           "rows": rows}
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv[1:])
