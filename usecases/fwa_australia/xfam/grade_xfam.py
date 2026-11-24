"""CROSS-FAMILY grading with the frozen grade.py (bbcc68c026) unchanged: only the sealed and questions sha256 it checks are
the Codex set's (reviews/spare/statute-corpus/stock/fwa-australia/xfam/ISOLATION.md seal), its flips file is xfam/flips.json
(empty: the same-family flips.json names same-family qids, which collide with this set's ids), and the output's label.
usage: python3 -I grade_xfam.py RUN-xfam.json <manage-agents>/reviews/spare/statute-corpus/stock/fwa-australia/xfam --out GRADES-xfam.json"""
import json
import sys
from pathlib import Path

X = Path(__file__).resolve().parent
sys.path.insert(0, str(X.parent))
import grade as G  # noqa: E402

G.SEALED_SHA256 = "ae38373631e610e67681ad292d99f906bcf8ec246c26af9a9fd198fbc6b724d0"
G.QUESTIONS_SHA256 = "d8d4048f6b67cfa80a9a07d04c5e0f65acc9235bc7fcd7f444922bb4fbdfeb9f"
G.HERE = X
G.main(sys.argv[1:])
if "--out" in sys.argv:
    p = Path(sys.argv[sys.argv.index("--out") + 1])
    d = json.loads(p.read_text())
    d["label"] = "CROSS-FAMILY"
    p.write_text(json.dumps(d, indent=1, sort_keys=True) + "\n", encoding="utf-8")
