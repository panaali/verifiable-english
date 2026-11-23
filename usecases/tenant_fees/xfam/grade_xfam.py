"""CROSS-FAMILY grading with the frozen grade.py (2ff32a6208) unchanged: only the two sealed sha256 it checks are the
Codex set's (reviews/spare/statute-corpus/tenant-fees/xfam/ISOLATION.md seal).
usage: python3 -I grade_xfam.py RUN-xfam.json <manage-agents>/reviews/spare/statute-corpus/tenant-fees/xfam --out GRADES-xfam.json"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import grade as G  # noqa: E402

G.SEALED_SHA256 = "43235b05ab6f0a6ed7af8aea866b2a78a1d1c87f5fc33b23edb997729151e1ee"
G.QUESTIONS_SHA256 = "78989ebff6c12a716f72be9640ae27f53f601dcc1e2a12e4d275d05d73591210"
G.main(sys.argv[1:])
