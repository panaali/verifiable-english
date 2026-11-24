"""CROSS-FAMILY grading with the frozen grade.py (ecc971dbc4) unchanged: only the sealed and questions sha256 it checks (SEAL) are
the Codex set's (reviews/spare/statute-corpus/batch2/ei-canada/xfam/ISOLATION.md seal), and the output's label.
usage: python3 -I grade_xfam.py RUN-xfam.json <manage-agents>/reviews/spare/statute-corpus/batch2/ei-canada/xfam --out GRADES-xfam.json"""
import contextlib
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import grade as G  # noqa: E402

G.SEAL = {"sealed/answers.jsonl": "2dfcd33c36dc91b4b1db5c66daaccab6b33da2939962e7b747292c9efb999aa1",
          "questions.jsonl": "9ce80357172b018fb73f17c1d00d4e96460fabb2d4fbbda98767f6909c0a7ee1"}
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
