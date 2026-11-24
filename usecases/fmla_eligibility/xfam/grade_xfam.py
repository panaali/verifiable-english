"""CROSS-FAMILY grading with the frozen grade.py (f62d7d5169) unchanged: only the sealed and questions sha256 it checks are
the Codex set's (reviews/spare/statute-corpus/stock/fmla-eligibility/xfam/ISOLATION.md seal), and the output's label.
usage: python3 -I grade_xfam.py RUN-xfam.json <manage-agents>/reviews/spare/statute-corpus/stock/fmla-eligibility/xfam --out GRADES-xfam.json"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import grade as G  # noqa: E402

G.SEALED_SHA256 = "8d20cad19a3699218c470f84418a0ae1cf4787f41e2913855f553a08eb00a766"
G.QUESTIONS_SHA256 = "ae6c2bf6abd7fb97bd80ce7cb869bdf0afc49d185b7e6a2219d86ea171ab43d7"
G.main(sys.argv[1:])
if "--out" in sys.argv:
    p = Path(sys.argv[sys.argv.index("--out") + 1])
    d = json.loads(p.read_text())
    d["label"] = "CROSS-FAMILY"
    p.write_text(json.dumps(d, indent=1, sort_keys=True) + "\n", encoding="utf-8")
