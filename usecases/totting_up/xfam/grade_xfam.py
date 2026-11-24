"""CROSS-FAMILY grading with the frozen grade.py (cd55af80ab) unchanged: only the sealed and questions sha256 it checks are
the Codex set's (reviews/spare/statute-corpus/stock/totting-up/xfam/ISOLATION.md seal), and the output's label.
usage: python3 -I grade_xfam.py RUN-xfam.json <manage-agents>/reviews/spare/statute-corpus/stock/totting-up/xfam --out GRADES-xfam.json"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import grade as G  # noqa: E402

G.SEALED_SHA256 = "f33b16d8dfcf9b6f651e99615fb0613eea11211390cf4bb165ec8ea74e2f81b0"
G.QUESTIONS_SHA256 = "e766ba58900720e4246e33b436ba97721768b972ec5ecfe10e117e3f5db544d6"
G.main(sys.argv[1:])
if "--out" in sys.argv:
    p = Path(sys.argv[sys.argv.index("--out") + 1])
    d = json.loads(p.read_text())
    d["label"] = "CROSS-FAMILY"
    p.write_text(json.dumps(d, indent=1, sort_keys=True) + "\n", encoding="utf-8")
