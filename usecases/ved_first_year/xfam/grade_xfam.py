"""CROSS-FAMILY grading with the frozen grade.py (29e5829ae3) unchanged: only the seals it checks are the Codex set's
(reviews/spare/statute-corpus/stock/ved-first-year/xfam/ISOLATION.md seal), its flips file is xfam/flips-xfam.json (written
by flips_xfam.py before the run, never from answers; the same-family flips.json is keyed by the same case ids and is not
read), and the output's label.
usage: python3 -I grade_xfam.py RUN-xfam.json <manage-agents>/reviews/spare/statute-corpus/stock/ved-first-year/xfam --out GRADES-xfam.json"""
import json
import sys
from pathlib import Path

X = Path(__file__).resolve().parent
sys.path.insert(0, str(X.parent))
import grade as G  # noqa: E402

G.SEALED_SHA256 = "d833668948b24ba677a49880cd3a2d707c0d6bd63c50ffd9ceb5d1f32c25e841"
G.QUESTIONS_SHA256 = "7e8920de8fff8ae82e45be4f11a211c3a0b33c11e059586eea8b445e79c7dd27"


class _Here:
    def __truediv__(self, name):
        return X / ("flips-xfam.json" if name == "flips.json" else name)


G.HERE = _Here()
G.main(sys.argv[1:])
if "--out" in sys.argv:
    p = Path(sys.argv[sys.argv.index("--out") + 1])
    d = json.loads(p.read_text())
    d["label"] = "CROSS-FAMILY"
    p.write_text(json.dumps(d, indent=1, sort_keys=True) + "\n", encoding="utf-8")
