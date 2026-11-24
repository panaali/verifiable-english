"""CROSS-FAMILY run of the FROZEN Fair Work notice and redundancy build (statute-fwa-australia-1123, commit bbcc68c026, the audited headline) on the
Codex set (reviews/spare/statute-corpus/stock/fwa-australia/xfam/).

Nothing of the build changes: this wrapper imports the frozen run.py, encode.py and translation.py unchanged and only
swaps their case source: `cases` -> xfam/cases_xfam.py (the fresh encoder's records) and encode.bridges() -> the frozen
age bridge's output on those records' dates of birth and notice days (xfam/bridge/bridges.jsonl, checked by sha256 below). The mutant pool
is forced to the "fork" start method so its workers inherit the swap (Python 3.14 defaults to forkserver, whose workers
would re-import encode.py and read the same-family bridge file). A planted error is caught when it changes at least one
cross-family answer (run.py's own rule; the answers it changes are listed).

usage (repository root): .venv/bin/python -B usecases/fwa_australia/xfam/run_xfam.py --mutants --workers 4 --out RUN-xfam.json
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
XFAM_BRIDGES_SHA256 = "99b9383b8f66e8d7e3f76c0a2217ff756da06c743ae4b292c95b31a5a5db0d77"
QUESTIONS_ENC_SHA256 = "88ce4e2f5503813e051a77e6e121414c265531427b7a87328d6f19e2458dbd86"

import encode as E  # noqa: E402

_raw = (X / "bridge" / "bridges.jsonl").read_bytes()
if hashlib.sha256(_raw).hexdigest() != XFAM_BRIDGES_SHA256:
    raise SystemExit("xfam/bridge/bridges.jsonl differs from its recorded sha256")
_BR = {}
for _line in _raw.decode("utf-8").splitlines():
    if _line.strip():
        _r = json.loads(_line)
        _BR[_r["case"]] = (_r["years"], _r["days"])
E.bridges = lambda: dict(_BR)
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
    out["xfam"] = {"cases_xfam_sha256": hashlib.sha256((X / "cases_xfam.py").read_bytes()).hexdigest(),
                   "bridges_sha256": XFAM_BRIDGES_SHA256}
    if out_path:
        text = json.dumps(out, indent=1, sort_keys=True) + "\n"
        Path(out_path).write_text(text, encoding="utf-8")
        print("run file", out_path, hashlib.sha256(text.encode()).hexdigest())
    return out


if __name__ == "__main__":
    main()
