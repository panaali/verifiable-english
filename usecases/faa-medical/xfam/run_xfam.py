"""CROSS-FAMILY run of the FROZEN 14 CFR 61.23 build (run commit 5a7c862e71) on the Codex-written set.

Nothing of the build changes: this wrapper imports the frozen run.py, encode.py and translation.py unchanged and only
swaps their case source: `cases` -> xfam/cases_xfam.py (the fresh encoder's records) and bridge/bridges.jsonl ->
xfam/bridges.jsonl (the frozen bridge script's output on those records' dates, checked by sha256 below). Mutants: the
frozen build names its kill targets by same-family case ids, so here a planted error is caught when it changes at least
one cross-family answer (the cases it changes are listed).

usage (repository root): uv run --frozen python -B usecases/faa-medical/xfam/run_xfam.py --mutants --out RUN-xfam.json
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
import cases_xfam  # noqa: E402

sys.modules["cases"] = cases_xfam
XFAM_BRIDGES_SHA256 = "477d8426f60dcb62953eed07177c1b799faaf770f3882467e78154ab1a85daf9"
QUESTIONS_ENC_SHA256 = "f4bfa9baef3635528c536e1422de4f297c33daeea470603ea2016a903380d9a4"

import encode as E  # noqa: E402


def _load_bridges(_sha):
    raw = (X / "bridges.jsonl").read_bytes()
    if hashlib.sha256(raw).hexdigest() != XFAM_BRIDGES_SHA256:
        raise SystemExit("xfam/bridges.jsonl differs from its recorded sha256")
    return {d["id"]: d for d in (json.loads(x) for x in raw.decode("utf-8").splitlines() if x.strip())}


E.load_bridges = _load_bridges
import translation as T  # noqa: E402

cases_xfam.MUTANT_TARGETS = {m: [] for m in T.MUTANTS}  # set on the module object; the encoder file is unchanged
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
    for m in out["mutants"].values():
        m["killed"] = bool(m["changed"])
    if out_path:
        text = json.dumps(out, indent=1, sort_keys=True) + "\n"
        Path(out_path).write_text(text, encoding="utf-8")
        print("run file", out_path, hashlib.sha256(text.encode()).hexdigest())
        print("mutants caught", {m: v["killed"] for m, v in out["mutants"].items()})
    return out


if __name__ == "__main__":
    main()
