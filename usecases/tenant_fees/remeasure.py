"""date-arith-remeasure (manage-agents reviews/dri-ruling-date-arith-20261123.md item 3): Tenant Fees Act 2019, BEFORE and AFTER.

Measurement only, scratch branch remeasure-tenant-fees-1124 (frozen evidence commit 2ff32a6208 + after-release e22d9ce609).
The law's one bridge (bridge/bridges.py) is the Sch. 1 para. 4(5) late-rent cap: a sum, over each day after the due date while
rent stays unpaid, of a daily interest amount in money. The merged written form (ve/surface/dates.py) writes dates, offsets,
ages, month ends and comparisons, not a count of days turned into money, so nothing is rewritten: AFTER = BEFORE's encoding on
the merged build.

--cf OUT.json: the staged route without the Lean replay, the bridge's cap (intcap_<x>) moved to 0.00 and to 99999.00; a
               graded answer that changes rests on the bridge.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))

import cases as K  # noqa: E402
import encode as E  # noqa: E402
import run as RUN  # noqa: E402

_ORIG = E.bridges


def main(argv):
    out_path = argv[1]
    cases = K.CASES
    base = {c["id"]: RUN.run_case(c)[0] for c in cases}
    res = {"base": base, "changed": {}}
    for name, value in (("cap_zero", "0.00"), ("cap_large", "99999.00")):
        real = _ORIG()
        E.bridges = lambda real=real, value=value: {k: value for k in real}
        try:
            alt = {c["id"]: RUN.run_case(c)[0] for c in cases}
        finally:
            E.bridges = _ORIG
        res["changed"][name] = sorted(q for cid in base for q in base[cid] if alt[cid][q] != base[cid][q])
        print(name, len(res["changed"][name]), flush=True)
    Path(out_path).write_text(json.dumps(res, indent=1, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1:])
