"""CROSS-FAMILY run of the FROZEN hos-driving build (statute-hos-driving-1123, commit 351c8d1e68, the audited headline) on the
Codex set (reviews/spare/statute-corpus/stock/hos-driving/xfam/).

Nothing of the build changes: this wrapper imports the frozen run.py, encode.py, translation.py and bridge/clock.py
unchanged and only swaps their case source: `cases` -> xfam/cases_xfam.py (the fresh encoder's records and activity
readings; encode.py reads ACTIVITY from it). The bridge is the frozen clock.py, called by the frozen encode.py on the
encoder's records (its every call is in the run file's bridge trail). The process pools are forced to the "fork" start
method so their workers inherit the swap (Python 3.14 defaults to forkserver, whose workers would re-import the
same-family cases.py). A planted error is caught when it changes at least one cross-family answer (run.py's own rule).

usage (repository root): .venv/bin/python -B usecases/hos_driving/xfam/run_xfam.py --mutants --workers 8 --out /tmp/RUN-xfam.json
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
import cases_xfam  # noqa: E402

sys.modules["cases"] = cases_xfam
QUESTIONS_ENC_SHA256 = "d6f32468cd2778538b83f8cb0d14817c5eb53d93f30355b86c2f0ed1dbd97308"
CASES_XFAM_SHA256 = "9b0fede2ff02ad2125a9afd23c7477336814c7bd601e594b372f52d38ac111ee"
if hashlib.sha256((X / "cases_xfam.py").read_bytes()).hexdigest() != CASES_XFAM_SHA256:
    raise SystemExit("xfam/cases_xfam.py differs from the encoder's file")

import encode as E  # noqa: E402,F401  (binds encode.ACTIVITY to the encoder's readings before any worker forks)
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
    out = RUN.main(argv)
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
