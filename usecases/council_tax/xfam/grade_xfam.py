"""CROSS-FAMILY grading with the frozen grade.py (1946ba1f0f) unchanged: only the sealed and questions sha256 it checks are
the Codex set's (reviews/spare/statute-corpus/batch2/council-tax/xfam/ISOLATION.md seal), and the output's label.
usage: python3 -I grade_xfam.py RUN-xfam.json <manage-agents>/reviews/spare/statute-corpus/batch2/council-tax/xfam --out GRADES-xfam.json"""
import contextlib
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import grade as G  # noqa: E402

G.SEALED_SHA256 = "d6f345cc43ee88ea83c86cc79961eefa7dd55b0969c67b395381d68c81b72628"
G.QUESTIONS_SHA256 = "1c171a555dd07297df09943d52613f83686878d744897896338b4322411144b5"
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
