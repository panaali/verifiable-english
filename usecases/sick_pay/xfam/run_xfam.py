"""CROSS-FAMILY run of the frozen statutory sick pay build on the Codex-written set (xfam/cases_xfam.py, the encoder's file).

The frozen run.py is imported and run unchanged with its own --cases-module option (workers import xfam.cases_xfam by
name); this wrapper only relabels the run file (CROSS-FAMILY, this set's questions-enc sha256), records each case's
CALENDAR lines beside its encoder judgement, and exits non-zero unless every qid of xfam/questions-enc.jsonl has an answer.
The sealed answers are NOT read here.

usage (repository root): .venv/bin/python -B usecases/sick_pay/xfam/run_xfam.py [--mutants] [--workers N] --out FILE
"""
import hashlib
import importlib
import json
import sys
from pathlib import Path

X = Path(__file__).resolve().parent
SP = X.parent
sys.path.insert(0, str(SP))
import run as R  # noqa: E402

MODULE = "xfam.cases_xfam"


def main(argv):
    out_path = None
    if "--out" in argv:
        i = argv.index("--out")
        out_path = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    out = R.main(argv + ["--cases-module", MODULE])
    K = importlib.import_module(MODULE)
    enc = (X / "questions-enc.jsonl").read_bytes()
    want = [q["qid"] for c in map(json.loads, enc.decode().splitlines()) for q in c["questions"]]
    got = {q for r in out["records"] for q in r["answers"]}
    missing = [q for q in want if q not in got]
    cal = {c["id"]: c.get("calendar", []) for c in K.CASES}
    for r in out["records"]:
        if r["id"] in cal:
            r["calendar"] = cal[r["id"]]
    out.update({"format": "sick-pay-run@1+xfam", "label": "CROSS-FAMILY", "cases_module": MODULE,
                "questions_enc_sha256": hashlib.sha256(enc).hexdigest(), "missing_qids": missing})
    text = json.dumps(out, indent=1, sort_keys=True) + "\n"
    if out_path:
        Path(out_path).write_text(text, encoding="utf-8")
        print("xfam run file", out_path, hashlib.sha256(text.encode()).hexdigest())
    if missing:
        print("MISSING answers for", missing)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
