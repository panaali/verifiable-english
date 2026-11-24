"""CROSS-FAMILY grading with the frozen grade.py (d2f6e370c6) unchanged: only the sealed sha256 it checks is the Codex set's
(reviews/spare/statute-corpus/hicbc/xfam/ISOLATION.md seal), and the output's label.
usage: python3 -I grade_xfam.py RUN-xfam.json <xfam>/sealed/answers.jsonl [--grades G.jsonl] --out GRADES-xfam.json"""
import contextlib
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import grade as G  # noqa: E402

G.SEALED_SHA256 = "38489fd8024237237d250351bc6a7c6dcb136955bea045202010b2208f5e15cb"
argv = sys.argv[1:]
out = None
if "--out" in argv:
    i = argv.index("--out")
    out = argv[i + 1]
    del argv[i:i + 2]
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    G.main(argv)
d = json.loads(buf.getvalue())
d["label"] = "CROSS-FAMILY"
text = json.dumps(d, indent=1, sort_keys=True) + "\n"
if out:
    Path(out).write_text(text, encoding="utf-8")
print(text)
