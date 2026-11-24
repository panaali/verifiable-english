"""CROSS-FAMILY run of the FROZEN ved-first-year build (statute-ved-first-year-1123, commit 29e5829ae3, the audited headline)
on the Codex set (reviews/spare/statute-corpus/stock/ved-first-year/xfam/).

Nothing of the build changes: this wrapper imports the frozen run.py, encode.py, translation.py and bridge/years.py
unchanged and only swaps their inputs: `cases` -> xfam/cases_xfam.py (the fresh encoder's records), and encode.bridges()
-> the rows of xfam/bridge/bridges.jsonl (the frozen years.py run by xfam/bridge_xfam.py on the encoder's dates; the
same-family bridge/bridges.jsonl is keyed by the same case ids and is never read here). The process pools are forced to
the "fork" start method so their workers inherit the swap. A planted error is caught when it changes at least one
cross-family answer (run.py's own rule). Every in-scope qid of questions-enc.jsonl must get an answer (else exit).

usage (repository root): .venv/bin/python -B usecases/ved_first_year/xfam/run_xfam.py --mutants --workers 8 --out RUN-xfam.json
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
QUESTIONS_ENC_SHA256 = "2e5541f390010b1b2580888a82318e74eb09a3aa70731626891f360ffb83b1b0"
CASES_XFAM_SHA256 = "84d93c0847a2d6b3abdfd2d51a3fbc18e680500cdb07659f5cc92dc005fe74f7"
if hashlib.sha256((X / "cases_xfam.py").read_bytes()).hexdigest() != CASES_XFAM_SHA256:
    raise SystemExit("xfam/cases_xfam.py differs from the encoder's file")

import encode as E  # noqa: E402
import run as RUN  # noqa: E402

BRIDGES = X / "bridge" / "bridges.jsonl"


def xfam_bridges():
    out = {}
    for line in BRIDGES.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            out[(r["case"], r["licence"])] = (r["years"], r["days"])
    return out


E.bridges = xfam_bridges
RUN.HERE = X  # the run file records the sha256 of xfam/questions-enc.jsonl


def main(argv=None):
    multiprocessing.set_start_method("fork", force=True)
    want = {r["case"] + "/" + r["licence"] for r in cases_xfam.BRIDGE_INPUTS}
    have = {k[0] + "/" + k[1] for k in xfam_bridges()}
    if want != have:
        raise SystemExit("xfam/bridge/bridges.jsonl does not match cases_xfam.BRIDGE_INPUTS (run bridge_xfam.py)")
    argv = list(sys.argv[1:] if argv is None else argv)
    out_path = None
    if "--out" in argv:
        i = argv.index("--out")
        out_path = argv[i + 1]
        del argv[i:i + 2]
    out = RUN.main(argv)
    if out["questions_enc_sha256"] != QUESTIONS_ENC_SHA256:
        raise SystemExit("xfam/questions-enc.jsonl differs from the sealed encoder file")
    if "--cases" not in argv:
        asked = {q["qid"] for c in cases_xfam.ENC for q in c["questions"]}
        got = {q for r in out["records"] for q in r["answers"]}
        if asked != got:
            raise SystemExit(f"qids without an answer: {sorted(asked - got)}; extra: {sorted(got - asked)}")
    out["label"] = "CROSS-FAMILY (Codex gpt-6-astra writer, Opus 5.5 encoder; frozen same-family translation)"
    out["xfam"] = {"cases_xfam_sha256": CASES_XFAM_SHA256,
                   "bridges_sha256": hashlib.sha256(BRIDGES.read_bytes()).hexdigest()}
    if out_path:
        text = json.dumps(out, indent=1, sort_keys=True) + "\n"
        Path(out_path).write_text(text, encoding="utf-8")
        print("run file", out_path, hashlib.sha256(text.encode()).hexdigest())
    return out


if __name__ == "__main__":
    main()
