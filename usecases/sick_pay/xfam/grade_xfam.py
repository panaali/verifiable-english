"""Grade a CROSS-FAMILY run file with the frozen grade.py against this set's seals (Codex set, stock/sick-pay/xfam/).

The frozen grade.py runs unchanged; only its two seal constants are set to this set's (ISOLATION.md seal table). Added
beside its summary (from the run file and questions.jsonl only): the strict "without anything computed outside Lean"
count with the encoder's CALENDAR lines also counted as outside Lean, and the disagreements with both answers.

usage: python3 -I grade_xfam.py RUN-xfam.json <manage-agents>/reviews/spare/statute-corpus/stock/sick-pay/xfam [--out F]
"""
import contextlib
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import grade as G  # noqa: E402

G.SEALED_SHA256 = "52a0a0c184687681774d8d3bb046a65b970faace7ac9393ab33b9b282210dc31"
G.QUESTIONS_SHA256 = "8f7a0cfb9006e1a95705b77fd89312aa98c9e7af89840f7f969da886f8405b71"


def main(argv):
    run = json.load(open(argv[0], encoding="utf-8"))
    out_path = argv[argv.index("--out") + 1] if "--out" in argv else None
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        G.main(argv[:2] + (["--out", out_path] if out_path else []))
    summary = json.loads(buf.getvalue())
    cal = {q: bool(r.get("calendar")) for r in run["records"] for q in r["answers"]}
    if out_path:
        doc = json.load(open(out_path, encoding="utf-8"))
        rows = doc["rows"]
        ins = [r for r in rows if r["scope"] == "in"]
        strict = [r for r in ins if r["tag"] == "none" and not r["encoder_judgement"] and not cal.get(r["qid"])]
        summary["xfam"] = {
            "label": run.get("label"), "questions_enc_sha256": run.get("questions_enc_sha256"),
            "without_outside_lean_incl_calendar": {"written": len(strict),
                                                   "match": sum(r["status"] == "match" for r in strict)},
            "cases_with_calendar_lines": sum(1 for r in run["records"] if r.get("calendar")),
            "disagreements": [{"qid": r["qid"], "kind": r["kind"], "ve": r["ve"], "writer": r["writer"]}
                              for r in ins if r["status"].endswith("differ") or r["status"] == "disagree"],
        }
        doc["summary"] = summary
        Path(out_path).write_text(json.dumps(doc, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=1, sort_keys=True, default=str))


if __name__ == "__main__":
    main(sys.argv[1:])
