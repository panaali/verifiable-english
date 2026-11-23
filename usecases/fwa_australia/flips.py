"""Which answers lean on what is decided outside the text (staged route, no Lean): flip each stated judgment
(translation.STATED), the bridged age (to the other side of 'over 45') and each encoder judgement (FLIPS below), re-run
the case, list the answers that change. SAME-FAMILY. Usage: .venv/bin/python -B usecases/fwa_australia/flips.py [--out F]"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))
import cases as K  # noqa: E402
import encode as E  # noqa: E402
import run as R  # noqa: E402
import translation as T  # noqa: E402

# encoder judgement -> the other reading (cases.py "judgement")
FLIPS = {
    "N014": ("isrs_award read true", lambda c: c["facts"].append("isrs_award")),
    "N018": ("meat_conn read false", lambda c: c["facts"].remove("meat_conn")),
    "N025": ("emp_init and not_required read true", lambda c: c["facts"].extend(["emp_init", "not_required"])),
    "N031": ("service other than casual read as the casual period",
             lambda c: c["ints"].update({f"ncy_{t}_e": 3 for t in ("ntc", "end", "trm")} |
                                        {f"ncd_{t}_e": 40 for t in ("ntc", "end", "trm")})),
}


def answers(case):
    return R.run_case(case)[0]


def main(argv):
    real = E.bridges()
    out = {"stated": {}, "bridge": {}, "encoder": {}}
    for case in K.CASES:
        base = answers(case)
        for s in T.STATED:
            c = copy.deepcopy(case)
            c["facts"] = [f for f in c["facts"] if f != s] if s in c["facts"] else c["facts"] + [s]
            got = answers(c)
            out["stated"].setdefault(s, []).extend(q for q in got if got[q] != base[q])
        y, d = real[case["id"]]
        over = y > 45 or (y == 45 and d > 0)
        E.bridges = lambda: {**real, case["id"]: (45, 0) if over else (46, 0)}
        got = answers(case)
        E.bridges = lambda: real
        out["bridge"][case["id"]] = [q for q in got if got[q] != base[q]]
        if case["id"] in FLIPS:
            what, fn = FLIPS[case["id"]]
            c = copy.deepcopy(case)
            fn(c)
            got = answers(c)
            out["encoder"][case["id"]] = {"flip": what, "changed": [q for q in got if got[q] != base[q]]}
    out["bridge_decisive"] = sorted(q for v in out["bridge"].values() for q in v)
    text = json.dumps(out, indent=1, sort_keys=True)
    if "--out" in argv:
        Path(argv[argv.index("--out") + 1]).write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main(sys.argv[1:])
