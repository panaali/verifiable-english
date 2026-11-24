"""Smoke test: the made-up cases of smoke_cases.py (not from the question file) against hand-worked answers, then every
planted error must change at least one of them. Bridges computed by bridge/posthog_bridge.py (the same script).
usage (repository root): .venv/bin/python -B usecases/posthog_leave/smoke_test.py [--no-mutants]
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "bridge"))

import encode as E  # noqa: E402
import posthog_bridge as PB  # noqa: E402
import run as R  # noqa: E402
import smoke_cases as S  # noqa: E402
import translation as T  # noqa: E402

BR = {}
for c in S.CASES:
    for b in E.bridge_inputs(c):
        r = PB.one(b)
        BR[(r["case"], r["item"], r["kind"])] = r["values"]
E.bridges = lambda: BR


def val(a):
    return a.get("value", a["answer"])


def main():
    base, bad = {}, []
    for c in S.CASES:
        got = R.run_case(c)[0]
        for qid, a in got.items():
            base[qid] = a
            if val(a) != S.EXPECT[qid]:
                bad.append((qid, val(a), S.EXPECT[qid]))
    for b in bad:
        print("FAIL", *b)
    print(f"smoke: {len(base) - len(bad)}/{len(base)} as hand-worked")
    if "--no-mutants" not in sys.argv:
        dead = 0
        for m, (desc, _) in T.MUTANTS.items():
            ch = [q for c in S.CASES for q, a in R.run_case(c, m)[0].items() if a != base[q]]
            dead += bool(ch)
            print(m, "KILLED" if ch else "SURVIVED", ch[:4], desc)
        print(f"mutants killed {dead}/{len(T.MUTANTS)}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
