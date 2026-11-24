"""CROSS-FAMILY grading with the frozen grade.py (cd90cdc036) unchanged: only the sealed and questions sha256 it checks are
the Codex set's (reviews/spare/statute-corpus/batch2/nmw/xfam/ISOLATION.md seal), and the output's label.
usage: python3 -I grade_xfam.py RUN-xfam.json <manage-agents>/reviews/spare/statute-corpus/batch2/nmw/xfam --out GRADES-xfam.json"""
import contextlib
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import grade as G  # noqa: E402

G.SEALED_SHA256 = "c7e3ee9231aed8e8a72bc2f5bccd5a1f3ba7334a75afc63e01438e7fbd719f21"
G.QUESTIONS_SHA256 = "484615ce85bbd60faf55eecda253420ebba4e7b6a08794d228d2401ae059c623"
argv = sys.argv[1:]
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    G.main(argv)  # writes the full grades file to --out (frozen behaviour)
if "--out" in argv:
    out = Path(argv[argv.index("--out") + 1])
    d = json.loads(out.read_text(encoding="utf-8"))
    d["label"] = "CROSS-FAMILY"
    out.write_text(json.dumps(d, indent=1, sort_keys=True) + "\n", encoding="utf-8")
print(buf.getvalue())
