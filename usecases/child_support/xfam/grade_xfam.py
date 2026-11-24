"""CROSS-FAMILY grading with the frozen grade.py (e0964364db) unchanged: only the sealed and questions sha256 it checks are the
Codex set's (reviews/spare/statute-corpus/stock/child-support/xfam/ISOLATION.md seal), and the output's label.
usage: python3 -I grade_xfam.py RUN-xfam.json <manage-agents>/reviews/spare/statute-corpus/stock/child-support/xfam --out GRADES-xfam.json"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import grade as G  # noqa: E402

G.SEALED_SHA256 = "00ef1a0ab6ecb11d840761ddada272847668fe10fad98a942f3668640fa522ed"
G.QUESTIONS_SHA256 = "6110b20180d5857f728e8e5c0cc9028327b72df9eb51af3c5eed0ce06766cde2"
G.main(sys.argv[1:])
if "--out" in sys.argv:
    p = Path(sys.argv[sys.argv.index("--out") + 1])
    d = json.loads(p.read_text())
    d["label"] = "CROSS-FAMILY"
    p.write_text(json.dumps(d, indent=1, sort_keys=True) + "\n", encoding="utf-8")
