"""CROSS-FAMILY grading with the frozen grade.py (9517f4dcd2) unchanged: only the sealed and questions sha256 it checks are
the Codex set's (reviews/spare/statute-corpus/batch2/uc-award/xfam/ISOLATION.md seal), and the output's label.
usage: python3 -I grade_xfam.py RUN-xfam.json <manage-agents>/reviews/spare/statute-corpus/batch2/uc-award/xfam --out GRADES-xfam.json"""
import contextlib
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import grade as G  # noqa: E402

G.SEALED_SHA256 = "83975703e2d1f80fd22893c05bf0d35c962d7a42a83411ae1343818579768e7f"
G.QUESTIONS_SHA256 = "fe5ed5617b0c86920865d3d1b7de45141500f4070bce2f60ccadb94725734a62"
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
