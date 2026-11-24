"""CROSS-FAMILY grading with the frozen grade.py (0118ab489e) unchanged: only the sealed and questions sha256 it checks are
the Codex set's (reviews/spare/statute-corpus/stock/eu-sea-passengers/xfam/ISOLATION.md seal), its case records
(grade.kinds) are xfam/cases_xfam.py, and the output's label.
usage: python3 -I grade_xfam.py RUN-xfam.json <manage-agents>/reviews/spare/statute-corpus/stock/eu-sea-passengers/xfam --out GRADES-xfam.json"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import cases_xfam  # noqa: E402

sys.modules["cases"] = cases_xfam  # grade.kinds() reads the case records: the cross-family encoder's, not the build's
import grade as G  # noqa: E402

G.SEALED_SHA256 = "223a005ec1557f0f4a8b60d4079a991dc39daba6ccdf4942e34026a9e29919b0"
G.QUESTIONS_SHA256 = "f234cb70f6669582cfa87e9c5b9768c8de49c2ed875d0a5206ffb64dee273c44"
G.main(sys.argv[1:])
if "--out" in sys.argv:
    p = Path(sys.argv[sys.argv.index("--out") + 1])
    d = json.loads(p.read_text())
    d["label"] = "CROSS-FAMILY"
    p.write_text(json.dumps(d, indent=1, sort_keys=True) + "\n", encoding="utf-8")
