"""Which answers lean on what is decided outside the text (staged route, no Lean): flip each stated judgment
(translation.STATED) and each encoder judgement (FLIPS below), re-run the case, list the answers that change. No bridge
exists in this law. SAME-FAMILY. Usage: .venv/bin/python -B usecases/eu_sea_passengers/flips.py [--out F]"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))
import cases as K  # noqa: E402
import run as R  # noqa: E402
import translation as T  # noqa: E402

# encoder judgement -> the other reading (cases.py "judgement")
FLIPS = {
    "E018": ("pax_transport read false (a pleasure operation not a passenger transport service)",
             lambda c: c["facts"].remove("pax_transport")),
    "E030": ("open_t read false (a travel pass is not an open ticket)", lambda c: c["facts"].remove("open_t")),
}


def answers(case):
    return R.run_case(case)[0]


def main(argv):
    out = {"stated": {}, "encoder": {}}
    for case in K.CASES:
        base = answers(case)
        for s in T.STATED:
            c = copy.deepcopy(case)
            c["facts"] = [f for f in c["facts"] if f != s] if s in c["facts"] else c["facts"] + [s]
            got = answers(c)
            out["stated"].setdefault(s, []).extend(q for q in got if got[q] != base[q])
        if case["id"] in FLIPS:
            what, fn = FLIPS[case["id"]]
            c = copy.deepcopy(case)
            fn(c)
            got = answers(c)
            out["encoder"][case["id"]] = {"flip": what, "changed": [q for q in got if got[q] != base[q]]}
    text = json.dumps(out, indent=1, sort_keys=True)
    if "--out" in argv:
        Path(argv[argv.index("--out") + 1]).write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main(sys.argv[1:])
