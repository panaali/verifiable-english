"""Smoke test on made-up cases (smoke_cases.py; written with the translation, not from the question file): the staged
route (no Lean) gives the hand-worked answers, and every planted error changes at least one of them.
Usage (repository root): .venv/bin/python -B usecases/copilot_ext_policy/smoke_test.py [--no-mutants]"""
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))
sys.setrecursionlimit(200000)

import run as R  # noqa: E402
import smoke_cases as S  # noqa: E402
import translation as T  # noqa: E402


def norm(a):
    return "OPEN" if a["answer"] == "OPEN" else {k: v for k, v in a.items() if k in ("answer", "value")}


def _mutant(m):
    sys.setrecursionlimit(200000)
    mg = {}
    for c in S.CASES:
        mg.update({q: norm(a) for q, a in R.run_case(c, m).items()})
    return m, mg


def main():
    t0 = time.time()
    got = {}
    for c in S.CASES:
        got.update({q: norm(a) for q, a in R.run_case(c).items()})
    bad = [(q, got.get(q), e) for q, e in S.EXPECTED.items() if got.get(q) != e]
    for b in bad:
        print("MISMATCH", *b)
    print(f"smoke: {len(S.EXPECTED) - len(bad)}/{len(S.EXPECTED)} as hand-worked ({time.time() - t0:.0f} s)")
    alive = []
    if "--no-mutants" not in sys.argv:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=len(T.MUTANTS)) as pool:
            res = dict(pool.map(_mutant, list(T.MUTANTS)))
        for m, (desc, _) in T.MUTANTS.items():
            changed = [q for q in got if res[m].get(q) != got[q]]
            print(m, "killed" if changed else "ALIVE", len(changed), changed[:6], desc)
            if not changed:
                alive.append(m)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
