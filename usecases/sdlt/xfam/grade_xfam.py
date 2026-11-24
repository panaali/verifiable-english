"""CROSS-FAMILY grading with the frozen grade.py (172ff2caf5) unchanged: only the sealed and questions sha256 it checks are
the Codex set's (reviews/spare/statute-corpus/batch2/sdlt/xfam/ISOLATION.md seal), and the output's label.
usage: python3 -I grade_xfam.py RUN-xfam.json <manage-agents>/reviews/spare/statute-corpus/batch2/sdlt/xfam --out GRADES-xfam.json"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import grade as G  # noqa: E402

G.SEALED_SHA256 = "3aa7270010bf7de180bdae3c5635ea1b3b27e73096ad36af62f1b6d7ac9dae46"
G.QUESTIONS_SHA256 = "e7a32623f5b85cdb410cfef78a16153bc117adffd299f073510b6619ead6607b"
G.main(sys.argv[1:])
if "--out" in sys.argv:
    p = Path(sys.argv[sys.argv.index("--out") + 1])
    d = json.loads(p.read_text())
    d["label"] = "CROSS-FAMILY"
    p.write_text(json.dumps(d, indent=1, sort_keys=True) + "\n", encoding="utf-8")
