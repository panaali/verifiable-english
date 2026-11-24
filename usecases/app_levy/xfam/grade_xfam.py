"""CROSS-FAMILY grading with the frozen grade.py (084f3cea90) unchanged: only the sealed and questions sha256 it checks are
the Codex set's (reviews/spare/statute-corpus/stock/app-levy/xfam/ISOLATION.md seal), its flips file is xfam/flips.json
(empty: the same-family flips.json names same-family qids, which collide with this set's ids), its amount kinds read the
cross-family encoder's records (the module `cases` = xfam/cases_xfam.py), and the output's label.
usage: python3 -I grade_xfam.py RUN-xfam.json <manage-agents>/reviews/spare/statute-corpus/stock/app-levy/xfam --out GRADES-xfam.json"""
import json
import sys
from pathlib import Path

X = Path(__file__).resolve().parent
sys.path.insert(0, str(X.parent))
sys.path.insert(0, str(X))
import cases_xfam  # noqa: E402

sys.modules["cases"] = cases_xfam
import grade as G  # noqa: E402

G.SEALED_SHA256 = "6a438314438d289c8cfb28c76869da20b736cd940b288d1e37f883ed947573b7"
G.QUESTIONS_SHA256 = "1f636ae5ef7bcfee37e3b8959e1920a4aa48e8082fee465c616374f4e297035b"
G.HERE = X
G.main(sys.argv[1:])
if "--out" in sys.argv:
    p = Path(sys.argv[sys.argv.index("--out") + 1])
    d = json.loads(p.read_text())
    d["label"] = "CROSS-FAMILY"
    p.write_text(json.dumps(d, indent=1, sort_keys=True) + "\n", encoding="utf-8")
