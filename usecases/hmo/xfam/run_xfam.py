"""CROSS-FAMILY run of the FROZEN HMO build (statute-hmo-1123, commit 89d055081c, the audited headline) on the Codex set.

Nothing of the build changes: this wrapper imports the frozen run.py, encode.py and translation.py unchanged and only swaps
their case source: `cases` -> xfam/cases_xfam.py (the fresh encoder's records, verbatim). run.py's worker pool is made to
FORK (Python 3.14's default start method on Linux is forkserver, whose workers would import the same-family cases.py by
name: the ids collide by design), and a worker is asked which cases module it sees before the run. The run file records
the sha256 of xfam/questions-enc.jsonl (checked against the seal) and of cases_xfam.py. The sealed answers are NOT read here.
Mutants: run.py counts a planted error caught when it changes at least one in-scope answer of the cases run (this set's).

usage (repository root): .venv/bin/python -B usecases/hmo/xfam/run_xfam.py --mutants --jobs 12 --out RUN-xfam.json
"""
import hashlib
import json
import multiprocessing
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

X = Path(__file__).resolve().parent
L = X.parent
sys.path.insert(0, str(L.parents[1]))
sys.path.insert(0, str(L))
sys.path.insert(0, str(X))
import cases_xfam  # noqa: E402

sys.modules["cases"] = cases_xfam
QUESTIONS_ENC_SHA256 = "c0392ad3e31c03a924cc328c388b2a1243f2fe9cf7dc732ba88341138508328a"
multiprocessing.set_start_method("fork", force=True)

import run as RUN  # noqa: E402

assert RUN.K is cases_xfam, RUN.K
RUN.HERE = X  # the run file records the sha256 of xfam/questions-enc.jsonl


def _which_cases(_):
    import run as R2
    return Path(sys.modules["cases"].__file__).name, Path(R2.K.__file__).name


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    out_path = None
    if "--out" in argv:
        i = argv.index("--out")
        out_path = argv[i + 1]
        del argv[i:i + 2]
    with ProcessPoolExecutor(max_workers=2) as pool:
        seen = set(pool.map(_which_cases, range(4)))
    if seen != {("cases_xfam.py", "cases_xfam.py")}:
        raise SystemExit(f"a worker sees another cases module: {seen}")
    out = RUN.main(argv)
    if out["questions_enc_sha256"] != QUESTIONS_ENC_SHA256:
        raise SystemExit("xfam/questions-enc.jsonl differs from the sealed encoder file")
    enc = [json.loads(x) for x in (X / "questions-enc.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    want = sorted(c["id"] for c in enc)
    got = sorted(r["id"] for r in out["records"])
    out["label"] = "CROSS-FAMILY (Codex gpt-6-astra writer, Opus 5.5 encoder; frozen same-family translation)"
    out["xfam"] = {"cases_xfam_sha256": hashlib.sha256((X / "cases_xfam.py").read_bytes()).hexdigest(),
                   "questions_enc_sha256": QUESTIONS_ENC_SHA256, "worker_cases_module": sorted(seen),
                   "missing_ids": sorted(set(want) - set(got)), "extra_ids": sorted(set(got) - set(want))}
    text = json.dumps(out, indent=1, sort_keys=True) + "\n"
    if out_path:
        Path(out_path).write_text(text, encoding="utf-8")
        print("xfam run file", out_path, hashlib.sha256(text.encode()).hexdigest())
    if want != got:
        print("ids differ from questions-enc.jsonl:", out["xfam"]["missing_ids"], out["xfam"]["extra_ids"])
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
