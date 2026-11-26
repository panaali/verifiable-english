"""Which answers lean on what is decided outside the text (staged route, no Lean): flip each encoder judgement (FLIPS),
the bridged duration of each licence (to the other side of six years), and translator reading R1 (the sufficient half of
1GC(5): translation.EURO6D_READ off); re-run the case, list the answers that change. This law has no stated judgment
(WRITER-BRIEF: none). SAME-FAMILY. Never reads answers. Usage: .venv/bin/python -B usecases/ved_first_year/flips.py [--out F]"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "bridge"))
import cases as K  # noqa: E402
import encode as E  # noqa: E402
import run as R  # noqa: E402
import translation as T  # noqa: E402
import years as Y  # noqa: E402

UK_REG = {"V014": "2026-05-06", "V028": "2026-03-01", "V033": "2026-05-04", "V034": "2026-08-01"}


def _veh(c):
    return c["vehicles"][0]


def _ind6d(c):
    _veh(c)["facts"].append("ind6d")


def _attach(n):
    def fn(c):
        a = [a for a in _veh(c)["accessories"] if a["id"] == f"v1a{n}"][0]
        a["facts"].append("a_attached")
    return fn


def _uk_reg(cid):
    def fn(c):
        _veh(c)["ints"]["dreg"] = UK_REG[cid]
    return fn


# encoder judgement -> the other reading (cases.py "judgement", in order)
FLIPS = {
    "V009": [("UK approval certificate's Euro 6d read as ind6d", _ind6d)],
    "V013": [("roof box fitted later read as attached", _attach(2)),
             ("UK approval certificate's Euro 6d read as ind6d", _ind6d)],
    "V014": [("first registered read as the UK registration", _uk_reg("V014"))],
    "V016": [("UK approval certificate's Euro 6d read as ind6d", _ind6d)],
    "V023": [("UK approval certificate's Euro 6d read as ind6d", _ind6d)],
    "V028": [("first registered read as the UK registration", _uk_reg("V028"))],
    "V033": [("first registered read as the UK registration", _uk_reg("V033"))],
    "V034": [("first registered read as the UK registration", _uk_reg("V034")),
             ("towbar attached at the Belgian registration read as attached", _attach(1))],
}


def answers(case):
    return R.run_case(case)[0]


def _bridges_for(case):
    """Bridge rows recomputed from the case's (possibly flipped) first registration date."""
    v = _veh(case)
    return {(case["id"], l["id"]): Y.years(v["ints"]["dreg"], l["date"]) for l in v["licences"]}


def main(argv):
    real = E.bridges()
    out = {"stated": {}, "bridge": {}, "encoder": {}, "reading_R1": {}}
    for case in K.CASES:
        base = answers(case)
        changed = set()
        for l in _veh(case)["licences"]:
            y, d = real[(case["id"], l["id"])]
            E.bridges = lambda y=y, l=l: {**real, (case["id"], l["id"]): (6, 0) if y < 6 else (5, 0)}
            got = answers(case)
            E.bridges = lambda: real
            changed |= {q for q in got if got[q] != base[q]}
        out["bridge"][case["id"]] = sorted(changed)
        for what, fn in FLIPS.get(case["id"], []):
            c = copy.deepcopy(case)
            fn(c)
            E.bridges = lambda c=c: {**real, **_bridges_for(c)}
            got = answers(c)
            E.bridges = lambda: real
            out["encoder"].setdefault(case["id"], []).append(
                {"flip": what, "changed": sorted(q for q in got if got[q] != base[q])})
        T.EURO6D_READ = False
        got = answers(case)
        T.EURO6D_READ = True
        out["reading_R1"][case["id"]] = sorted(q for q in got if got[q] != base[q])
    out["bridge_decisive"] = sorted(q for v in out["bridge"].values() for q in v)
    out["encoder_decisive"] = sorted({q for v in out["encoder"].values() for f in v for q in f["changed"]})
    out["reading_R1_decisive"] = sorted(q for v in out["reading_R1"].values() for q in v)
    text = json.dumps(out, indent=1, sort_keys=True)
    if "--out" in argv:
        Path(argv[argv.index("--out") + 1]).write_text(text + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("bridge_decisive", "encoder_decisive", "reading_R1_decisive")}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
