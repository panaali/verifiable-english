"""CROSS-FAMILY grading with the frozen grade.py (5a7c862e71) unchanged: only the two sealed sha256 it checks are the
Codex set's (reviews/spare/statute-corpus/faa-medical/xfam/ISOLATION.md seal), and the output's label.
usage: python3 -I grade_xfam.py RUN-xfam.json <xfam>/sealed/answers.jsonl <xfam>/questions.jsonl --out GRADES-xfam.json"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import grade as G  # noqa: E402

G.SEALED_SHA256 = "99619b6756cb9079d9c6d2e2a09349477c502f2df19240fc38ba26061815415f"
G.QUESTIONS_SHA256 = "bfa2461b9c6c6e21b8dacd48509ebf1cf4692cb70ba5f952d2d8fc2f46a21690"
G.main()
if "--out" in sys.argv:
    p = Path(sys.argv[sys.argv.index("--out") + 1])
    d = json.loads(p.read_text())
    d["label"] = "CROSS-FAMILY"
    p.write_text(json.dumps(d, indent=1, sort_keys=True) + "\n", encoding="utf-8")
