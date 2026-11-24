"""CROSS-FAMILY run of the FROZEN apprenticeship levy build (statute-app-levy-1123, commit 084f3cea90, the audited headline) on the Codex set
(reviews/spare/statute-corpus/stock/app-levy/xfam/).

Nothing of the build changes: this wrapper imports the frozen run.py, encode.py and translation.py unchanged and only swaps
their case source: `cases` -> xfam/cases_xfam.py (the fresh encoder's records). This law has no bridge. The mutant pool is
forced to the "fork" start method so its workers inherit the swap. A planted error is caught when it changes at least one
cross-family answer (run.py's own rule; the answers it changes are listed).

usage (repository root): .venv/bin/python -B usecases/app_levy/xfam/run_xfam.py --mutants --workers 4 --out RUN-xfam.json
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
QUESTIONS_ENC_SHA256 = "0c5fd5240100d929ef0fce1d7b6b55fc87bcc7e95f96edc2f6dfa33de268b4b2"

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
    out["xfam"] = {"cases_xfam_sha256": hashlib.sha256((X / "cases_xfam.py").read_bytes()).hexdigest()}
    if out_path:
        text = json.dumps(out, indent=1, sort_keys=True) + "\n"
        Path(out_path).write_text(text, encoding="utf-8")
        print("run file", out_path, hashlib.sha256(text.encode()).hexdigest())
    return out


if __name__ == "__main__":
    main()
