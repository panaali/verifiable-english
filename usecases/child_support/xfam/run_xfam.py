"""CROSS-FAMILY run of the FROZEN child-support build (statute-child-support-1123, commit e0964364db, the audited headline) on
the Codex set (reviews/spare/statute-corpus/stock/child-support/xfam/).

Nothing of the build changes: this wrapper imports the frozen run.py (with encode.py and translation.py) unchanged and passes
the fresh encoder's records (xfam/cases_xfam.py) as run.main's own case-module argument K. No bridge exists for this law.
The mutant pool is forced to the "fork" start method (Python 3.14 defaults to forkserver; the workers receive the cases as
arguments either way). A planted error is caught when it changes at least one cross-family answer (run.py's own rule).

usage (repository root): .venv/bin/python -B usecases/child_support/xfam/run_xfam.py --mutants --workers 8 --out /tmp/RUN-xfam.json
"""
import hashlib
import json
import multiprocessing
import sys
from pathlib import Path

X = Path(__file__).resolve().parent
L = X.parent
sys.path.insert(0, str(L.parents[1]))
sys.path.insert(0, str(L))
sys.path.insert(0, str(X))
QUESTIONS_ENC_SHA256 = "0a785b3fd198b37c95aa74e2ab22986698b385d42c66e62835e2a3f84ffe6d76"
CASES_XFAM_SHA256 = "702617f4fa8fdce8a60d5cba2ac433a89cc5eec9a0f5188fd52f2d60f343d47b"
if hashlib.sha256((X / "cases_xfam.py").read_bytes()).hexdigest() != CASES_XFAM_SHA256:
    raise SystemExit("xfam/cases_xfam.py differs from the encoder's file")
import cases_xfam  # noqa: E402
import run as RUN  # noqa: E402

RUN.HERE = X  # the run file records the sha256 of xfam/questions-enc.jsonl


def main(argv=None):
    multiprocessing.set_start_method("fork", force=True)
    argv = list(sys.argv[1:] if argv is None else argv)
    out_path = None
    if "--out" in argv:
        i = argv.index("--out")
        out_path = argv[i + 1]
        del argv[i:i + 2]
    out = RUN.main(argv, K=cases_xfam)
    if out["questions_enc_sha256"] != QUESTIONS_ENC_SHA256:
        raise SystemExit("xfam/questions-enc.jsonl differs from the sealed encoder file")
    out["label"] = "CROSS-FAMILY (Codex gpt-6-astra writer, Opus 5.5 encoder; frozen same-family translation)"
    out["xfam"] = {"cases_xfam_sha256": CASES_XFAM_SHA256}
    if out_path:
        text = json.dumps(out, indent=1, sort_keys=True) + "\n"
        Path(out_path).write_text(text, encoding="utf-8")
        print("run file", out_path, hashlib.sha256(text.encode()).hexdigest())
    return out


if __name__ == "__main__":
    main()
