"""Grade a CROSS-FAMILY run file with the frozen grade.py against this set's seals (Codex set, hmo/xfam/).

The frozen grade.py runs unchanged; only its two seal constants are set to this set's (xfam/ISOLATION.md seal table). One
listing rule is applied after it (audit-hmo.md (a) note "writer-ambiguous"): grade.py tests "refused" first, so a sealed
record that fills "ambiguous" would be listed as refused where VE refused; here every question of such a record is listed
writer-ambiguous (not correct either way; VE's answer and whether it agrees are shown). Added: k/n per question kind,
the disagreements with both answers.

usage: python3 -I grade_xfam.py RUN-xfam.json <manage-agents>/reviews/spare/statute-corpus/hmo/xfam [--out GRADES-xfam.json]
"""
import contextlib
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import grade as G  # noqa: E402

G.SEALED_SHA256 = "7823c97a7f59b53b2a07659a3b5e68baa423705043c1e136657c5b1bfe82ff85"
G.QUESTIONS_SHA256 = "6524802f3b22579f17b95944037538cc21e69e0b1d5111ba631579f4d85c9151"


def count(rs):
    out = {}
    for r in rs:
        out[r["verdict"]] = out.get(r["verdict"], 0) + 1
    return out


def main(argv):
    run_path, xd = argv[0], Path(argv[1])
    out_path = argv[argv.index("--out") + 1] if "--out" in argv else "/dev/null"
    sealed_p, q_p = str(xd / "sealed" / "answers.jsonl"), str(xd / "questions.jsonl")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        G.main([run_path, sealed_p, q_p, "--out", out_path])
    doc = json.load(open(out_path, encoding="utf-8")) if out_path != "/dev/null" else None
    if doc is None:
        raise SystemExit("--out is required")
    sealed = G.load(sealed_p, G.SEALED_SHA256)
    amb = sorted(cid for cid, rec in sealed.items() if rec.get("ambiguous"))
    for r in doc["rows"]:
        cid = r["qid"].split("/")[0]
        if cid in amb and r["verdict"] != "writer-ambiguous":
            r["verdict_frozen_grade_py"] = r["verdict"]
            r["verdict"] = "writer-ambiguous"
    rows = doc["rows"]
    plain = [r for r in rows if r["tag"] == "none"]
    correct = [r for r in rows if r["verdict"] == "correct"]
    doc["label"] = "CROSS-FAMILY"
    doc["number"] = {"correct": len(correct), "written": len(rows)}
    doc["number_excluding_stated_judgment_and_bridge_only"] = {
        "correct": sum(r["verdict"] == "correct" for r in plain), "written": len(plain)}
    doc["verdicts"], doc["verdicts_excluding"] = count(rows), count(plain)
    doc["by_question"] = {qq: count([r for r in rows if r["qid"].endswith(qq)]) for qq in ("Q1", "Q2", "Q3")}
    doc["by_kind"] = {qq: f"{sum(r['verdict'] == 'correct' for r in rows if r['qid'].endswith(qq))}/"
                          f"{sum(1 for r in rows if r['qid'].endswith(qq))}" for qq in ("Q1", "Q2", "Q3")}
    doc["writer_ambiguous_records"] = amb
    doc["disagreements"] = [{"qid": r["qid"], "ve": r["ve"], "sealed": r["sealed"]}
                            for r in rows if r["verdict"] == "disagreement"]
    Path(out_path).write_text(json.dumps(doc, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    keys = ("number", "number_excluding_stated_judgment_and_bridge_only", "verdicts", "by_question", "by_kind",
            "writer_ambiguous_records", "disagreements", "probes", "agreement_audit", "run_sha256")
    print(json.dumps({k: doc[k] for k in keys}, indent=1, sort_keys=True, default=str))
    print("refused:", [r["qid"] for r in rows if r["verdict"] == "refused"])
    print("writer-ambiguous:", [(r["qid"], r["ve"] if isinstance(r["ve"], str) else "lists", r["agrees_with_sealed"])
                                for r in rows if r["verdict"] == "writer-ambiguous"])


if __name__ == "__main__":
    main(sys.argv[1:])
