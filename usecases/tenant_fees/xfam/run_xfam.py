"""CROSS-FAMILY run of the FROZEN Tenant Fees Act 2019 build (run commit 2ff32a6208) on the Codex-written set.

Nothing of the build changes: this wrapper imports the frozen run.py, encode.py and translation.py unchanged and only
swaps their case source: `cases` -> xfam/cases_xfam.py (the fresh encoder's records) and bridge/bridges.jsonl ->
xfam/bridges.jsonl (the frozen bridge script's output on the encoder's xfam/inputs.jsonl, checked by sha256 below). The
frozen run.py already counts a planted error caught when it changes at least one answer.

usage (repository root): .venv/bin/python -B usecases/tenant_fees/xfam/run_xfam.py --mutants --out RUN-xfam.json
"""
import hashlib
import json
import sys
from pathlib import Path

X = Path(__file__).resolve().parent
L = X.parent
sys.path.insert(0, str(L.parents[1]))
sys.path.insert(0, str(L))
sys.path.insert(0, str(X))
import cases_xfam  # noqa: E402  (checks xfam/questions-enc.jsonl against its sha256 at import)

sys.modules["cases"] = cases_xfam
XFAM_BRIDGES_SHA256 = "b83824019637db54718a3f42155dde13c1027516f35ebb208a917bbf3d73b4b4"
QUESTIONS_ENC_SHA256 = "3a2f1e2eadec53c6560bbbc8d9a234566179e5c0b2e31ade23e450394178ad0f"

import encode as E  # noqa: E402


def _bridges():
    raw = (X / "bridges.jsonl").read_bytes()
    if hashlib.sha256(raw).hexdigest() != XFAM_BRIDGES_SHA256:
        raise SystemExit("xfam/bridges.jsonl differs from its recorded sha256")
    out = {}
    for line in raw.decode("utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            out[(r["case"], r["item"])] = r["intcap"]
    return out


E.bridges = _bridges
import run as RUN  # noqa: E402

RUN.HERE = X  # the run file records the sha256 of xfam/questions-enc.jsonl


def main(argv=None):
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
