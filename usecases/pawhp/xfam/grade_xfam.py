"""CROSS-FAMILY grading with the frozen grade.py (873c9ea940) unchanged: only the sealed sha256 it checks is the Codex
set's (reviews/spare/statute-corpus/pawhp/xfam/ISOLATION.md seal), and the output's label.
usage: python3 -I grade_xfam.py RUN-xfam.json <xfam>/sealed/answers.jsonl --out GRADES-xfam.json"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import grade as G  # noqa: E402

G.SEALED_SHA256 = "7acede8b0068f373752277fb18dc80e45560b3492c1da2f40bdd50aa3e6312c3"
G.main()
if "--out" in sys.argv:
    p = Path(sys.argv[sys.argv.index("--out") + 1])
    d = json.loads(p.read_text())
    d["label"] = "CROSS-FAMILY"
    p.write_text(json.dumps(d, indent=1, sort_keys=True) + "\n", encoding="utf-8")
