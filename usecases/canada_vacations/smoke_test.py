"""Smoke test on made-up cases (smoke_cases.py; written with the translation, not from the question file): the staged route
(no Lean) gives the hand-worked answers, and every planted error changes at least one of them.
Usage (repository root): .venv/bin/python -B usecases/canada_vacations/smoke_test.py [--no-mutants]"""
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))

import run as R  # noqa: E402
import smoke_cases as S  # noqa: E402
import translation as T  # noqa: E402


def norm(a):
    return "OPEN" if a["answer"] == "OPEN" else {k: v for k, v in a.items() if k in ("answer", "value")}


def _mutant(m):
    mg = {}
    for c in S.CASES:
        mg.update({q: norm(a) for q, a in R.run_case(c, m)[0].items()})
    return m, mg


def main():
    t0 = time.time()
    got = {}
    for c in S.CASES:
        got.update({q: norm(a) for q, a in R.run_case(c)[0].items()})
    bad = [(q, got.get(q), e) for q, e in S.EXPECTED.items() if got.get(q) != e]
    for b in bad:
        print("MISMATCH", *b)
    print(f"smoke: {len(S.EXPECTED) - len(bad)}/{len(S.EXPECTED)} as hand-worked ({time.time() - t0:.0f} s)")
    alive = []
    if "--no-mutants" not in sys.argv:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=6) as pool:
            res = dict(pool.map(_mutant, list(T.MUTANTS)))
        for m, (desc, _) in T.MUTANTS.items():
            changed = [q for q in got if res[m].get(q) != got[q]]
            print(m, "killed" if changed else "ALIVE", len(changed), changed[:6], desc)
            if not changed:
                alive.append(m)
        print(f"mutants: {len(T.MUTANTS) - len(alive)}/{len(T.MUTANTS)} killed")
    return 1 if bad or alive else 0


if __name__ == "__main__":
    sys.exit(main())
