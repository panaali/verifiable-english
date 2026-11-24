"""CROSS-FAMILY run of the FROZEN HICBC build (statute-hicbc-1123, commit d2f6e370c6, the audited headline) on the Codex set
(reviews/spare/statute-corpus/hicbc/xfam/).

Nothing of the build changes: this wrapper imports the frozen run.py, encode.py and rules.py unchanged and only swaps their
case source: `cases` -> xfam/cases_xfam.py (the fresh encoder's records) and the bridge file -> xfam/bridge/bridges.jsonl
(the frozen bridge on those records, bridges_xfam.py; pinned by sha256 below, as run.py pins its own). The mutant pool is
forced to the "fork" start method so its workers inherit the swap. A planted error is caught when it changes at least one
cross-family answer (run.py's own rule; the answers it changes are listed).

usage (repository root): uv run --frozen python -B usecases/hicbc/xfam/run_xfam.py --mutants --workers 5 --lean-workers 4 --out RUN-xfam.json
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
XFAM_BRIDGES_SHA256 = "42eda9f9e48508dd25f7d1955a6fbb702bd240cbe572b488fe28996ef028385e"
QUESTIONS_ENC_SHA256 = "25f165d10b33475df8024ccd08eba9600139866357b9de7b8547bca3e43d7e09"
import encode as E  # noqa: E402

E.HERE = X  # load_bridges() reads X/bridge/bridges.jsonl
import run as RUN  # noqa: E402

assert RUN.K is cases_xfam
RUN.BRIDGES_SHA256 = XFAM_BRIDGES_SHA256
RUN.HERE = X  # the run file records the sha256 of xfam/questions-enc.jsonl and xfam/bridge/bridges.jsonl


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
    out["xfam"] = {"cases_xfam_sha256": hashlib.sha256((X / "cases_xfam.py").read_bytes()).hexdigest(),
                   "bridges_sha256": XFAM_BRIDGES_SHA256}
    if out_path:
        text = json.dumps(out, indent=1, sort_keys=True) + "\n"
        Path(out_path).write_text(text, encoding="utf-8")
        print("run file", out_path, hashlib.sha256(text.encode()).hexdigest())
    return out


if __name__ == "__main__":
    main()
