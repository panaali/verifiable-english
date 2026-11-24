"""CROSS-FAMILY run of the FROZEN PAWHP build (pawhp-build-1123, commit 873c9ea940, the audited headline) on the Codex set.

Nothing of the build changes: this wrapper imports the frozen run.py, encode.py and translation.py unchanged and only
swaps their case source: `cases` -> xfam/cases_xfam.py (the fresh encoder's records) and encode.BRIDGES -> the births
of xfam/bridges.jsonl (the frozen bridge script's output on xfam/questions-enc.jsonl, checked by sha256 below). Mutants:
the frozen build names its kill targets by same-family ids, so here a planted error is caught when it changes at least
one cross-family answer (the cases it changes are listed).

usage (repository root): uv run --frozen python -B usecases/pawhp/xfam/run_xfam.py --mutants --out RUN-xfam.json
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
XFAM_BRIDGES_SHA256 = "d3edd7e1bb70630f697eadd715239a7e0a51c2b211aa7f69c2f51b3081ef7e19"
QUESTIONS_ENC_SHA256 = "b40ded55b1ee2b937bd6de6368240abff6b6ae3dc4abc6184dcd6cb5efea5665"

import encode as E  # noqa: E402

_raw = (X / "bridges.jsonl").read_bytes()
if hashlib.sha256(_raw).hexdigest() != XFAM_BRIDGES_SHA256:
    raise SystemExit("xfam/bridges.jsonl differs from its recorded sha256")
E.BRIDGES.clear()
E.BRIDGES.update({d["id"]: d["births"] for d in (json.loads(x) for x in _raw.decode("utf-8").splitlines()) if "id" in d})
import run as RUN  # noqa: E402

RUN.MUTANT_TARGETS = {m: [] for m in RUN.MUTANT_TARGETS}
# M6 (row statute-xfam-wrong-pawhp-1): counting the in-patient period from the entry day must flip P020/Q1
XFAM_MUST = {"M6": [("P020", "Q1")]}
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
    for name, m in out["mutants"].items():
        m["killed"] = bool(m["changed"])
        if name in XFAM_MUST:
            m["must_flip"] = ["/".join(x) for x in XFAM_MUST[name]]
            m["flipped"] = [f"{pid}/{qq}" for pid, qq in XFAM_MUST[name]
                            if (m["changed_answers"].get(pid, {}).get(qq)
                                not in (None, next(r for r in out["records"] if r["id"] == pid)["staged"][qq]))]
            m["killed"] = m["killed"] and m["flipped"] == m["must_flip"]
    if out_path:
        text = json.dumps(out, indent=1, sort_keys=True) + "\n"
        Path(out_path).write_text(text, encoding="utf-8")
        print("run file", out_path, hashlib.sha256(text.encode()).hexdigest())
        print("mutants caught", {m: v["killed"] for m, v in out["mutants"].items()})
    return out


if __name__ == "__main__":
    main()
