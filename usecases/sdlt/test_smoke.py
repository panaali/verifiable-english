"""Smoke test of the translation on synthetic cases (hand-worked from the pinned text; not corpus questions).
usage (repository root, after lake build): .venv/bin/python -B usecases/sdlt/test_smoke.py  -> exit 0 when all hold.
X1 £400,000 house, one first-time buyer: Table A 0 + 2,500 + 7,500 = 10,000; relief: 5% x 100,000 = 5,000.
X2 £1,600,000 lease (99 years), an equivalent house abroad before: Table A 0 + 2,500 + 33,750 + 57,500 + 12,000 = 105,750;
   relief NO (para. 6(1)(b)(i) and 1(3)). X3 £300,000 house + £100,000 garden bought by a linked transaction: amounts
   OPEN (s. 55(1C) Step 3 not written); relief YES for both (paras. 1(5)-(6), 2). X4 £260,000 mixed land: Table B
   0 + 2,000 + 500 = 2,500. X5 house with garden land in the same transaction (9(3)): relief YES, 5% x 50,000 = 2,500.
X6 an earlier 20-year lease abroad is ignored (6(2)): relief YES, tax 0. Every planted error changes some answer here."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))
import run  # noqa: E402
import smoke_cases  # noqa: E402
import translation as T  # noqa: E402

WANT = {"X1-1": ("AMOUNT", "10000.00"), "X1-2": ("YES", None), "X1-3": ("AMOUNT", "5000.00"),
        "X2-1": ("AMOUNT", "105750.00"), "X2-2": ("NO", None), "X2-3": ("NO RELIEF", None),
        "X3-1": ("OPEN", None), "X3-2": ("YES", None), "X3-3": ("YES", None), "X3-4": ("OPEN", None),
        "X4-1": ("AMOUNT", "2500.00"), "X5-1": ("YES", None), "X5-2": ("AMOUNT", "2500.00"),
        "X6-1": ("YES", None), "X6-2": ("AMOUNT", "0.00")}
fails, base = 0, {}
for c in smoke_cases.CASES:
    got = run.run_case(c)[0]
    base.update(got)
    for qid, a in got.items():
        ok = (a["answer"], a.get("gbp")) == WANT[qid]
        fails += not ok
        print("PASS" if ok else "FAIL", qid, a, "want", WANT[qid])
for m in T.MUTANTS:
    changed = [q for c in smoke_cases.CASES for q, a in run.run_case(c, m)[0].items() if a != base[q]]
    fails += not changed
    print("PASS" if changed else "FAIL", "mutant", m, "changes", changed)
print("result:", "all pass" if not fails else f"{fails} failed")
sys.exit(1 if fails else 0)
