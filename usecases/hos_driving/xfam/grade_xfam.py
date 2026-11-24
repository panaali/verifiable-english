"""CROSS-FAMILY grading with the frozen grade.py (351c8d1e68) unchanged: only the sealed and encoder-file sha256 it checks are
the Codex set's (reviews/spare/statute-corpus/stock/hos-driving/xfam/ISOLATION.md seal), and the output's label.
usage: python3 -I grade_xfam.py RUN-xfam.json <manage-agents>/reviews/spare/statute-corpus/stock/hos-driving/xfam --out GRADES-xfam.json"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import grade as G  # noqa: E402

G.SEALED_SHA256 = "6c1bf05a5a6ceef61435cd27c61f00a30ad8cc2b4e33c905fe233467fe054553"
G.ENC_SHA256 = "d6f32468cd2778538b83f8cb0d14817c5eb53d93f30355b86c2f0ed1dbd97308"
G.main(sys.argv[1:])
if "--out" in sys.argv:
    p = Path(sys.argv[sys.argv.index("--out") + 1])
    d = json.loads(p.read_text())
    d["label"] = "CROSS-FAMILY"
    p.write_text(json.dumps(d, indent=1, sort_keys=True) + "\n", encoding="utf-8")
