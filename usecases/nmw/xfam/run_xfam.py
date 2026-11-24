"""CROSS-FAMILY run of the FROZEN NMW build (statute-nmw-1123, commit cd90cdc036, the audited headline) on the Codex set
(reviews/spare/statute-corpus/batch2/nmw/xfam/).

Nothing of the build changes: this wrapper imports the frozen run.py, encode.py and translation.py unchanged and only
swaps the case source: `cases` -> xfam/cases_xfam.py (the fresh encoder's records), the bridge file encode.py reads ->
xfam/bridge/bridges.jsonl (the frozen bridges.py on the encoder's bridge dates, bridges_xfam.py), and the encoder file whose sha256 the
run file records -> xfam/questions-enc.jsonl. The mutant pool is forced to the "fork" start method so its workers inherit
the swap. A planted error is caught when it changes at least one cross-family answer (run.py's own rule).

usage (repository root): .venv/bin/python -B usecases/nmw/xfam/run_xfam.py --mutants --out RUN-xfam.json
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
QUESTIONS_ENC_SHA256 = "2a857245b15e0b89e84b70ef465bb57e3519bb8263e0e0d6ea7a70873715c298"
import encode as E  # noqa: E402

E.HERE = X  # bridges() reads X/bridge/bridges.jsonl
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
                   "bridges_sha256": hashlib.sha256((X / "bridge" / "bridges.jsonl").read_bytes()).hexdigest()}
    if out_path:
        text = json.dumps(out, indent=1, sort_keys=True) + "\n"
        Path(out_path).write_text(text, encoding="utf-8")
        print("run file", out_path, hashlib.sha256(text.encode()).hexdigest())
    return out


if __name__ == "__main__":
    main()
