"""Which cross-family answers lean on what is decided outside the text (staged route, no Lean), as the frozen flips.py does
for the same-family cases: the bridged duration of each licence put on the other side of six years; translator reading R1
off (translation.EURO6D_READ); and each encoder judgement flipped to its other reading (FLIPS below, written by the
operator from cases_xfam.JUDGEMENT before the run; never from answers). Never reads answers.
usage (repository root): .venv/bin/python -B usecases/ved_first_year/xfam/flips_xfam.py --out usecases/ved_first_year/xfam/flips-xfam.json"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

X = Path(__file__).resolve().parent
L = X.parent
sys.path.insert(0, str(L.parents[1]))
sys.path.insert(0, str(L))
sys.path.insert(0, str(L / "bridge"))
sys.path.insert(0, str(X))
import cases_xfam as K  # noqa: E402

sys.modules["cases"] = K
import run_xfam  # noqa: E402,F401  (the same swap as the run: encode.bridges -> xfam/bridge/bridges.jsonl)
import encode as E  # noqa: E402
import run as R  # noqa: E402
import translation as T  # noqa: E402
import years as Y  # noqa: E402


def _veh(c, owner):
    i = [v["owner"] for v in K.V[c["id"]]].index(owner)
    return c["vehicles"][i]


def set_facts(owner, add=(), drop=()):
    def fn(c):
        v = _veh(c, owner)
        v["facts"] = [f for f in v["facts"] if f not in drop] + [f for f in add if f not in v["facts"]]
    return fn


def set_dreg(owner, day):
    def fn(c):
        _veh(c, owner)["ints"]["dreg"] = day
    return fn


def set_acc(owner, n, add=(), drop=()):
    def fn(c):
        v = _veh(c, owner)
        a = [a for a in v["accessories"] if a["id"] == f"{v['id']}a{n}"][0]
        a["facts"] = [f for f in a["facts"] if f not in drop] + [f for f in add if f not in a["facts"]]
    return fn


def set_co2(owner, figure):
    def fn(c):
        _veh(c, owner)["ints"]["co2"] = figure
    return fn


# encoder judgement -> the other reading: case id -> [(what, fn)]  (filled from cases_xfam.JUDGEMENT)
FLIPS: dict = {
    "V001": [("Ben: zero rate of emissions read as the certificate's figure, co2 0", set_co2("Ben", "0"))],
    "V003": [("Ben: first registered read as the UK registration (1 May 2025)", set_dreg("Ben", "2025-05-01")),
             ("Ben: UK approval certificate's Euro 6d read as ind6d", set_facts("Ben", add=["ind6d"]))],
    "V005": [("Alice: first registered read as the UK registration (1 May 2025)", set_dreg("Alice", "2025-05-01"))],
    "V010": [("Cara: zero rate of emissions read as the certificate's figure, co2 0", set_co2("Cara", "0"))],
    "V011": [("Cara: zero rate of emissions read as the certificate's figure, co2 0", set_co2("Cara", "0"))],
}


def answers(case):
    return R.run_case(case)[0]


def _bridges_for(case):
    return {(case["id"], l["id"]): Y.years(v["ints"]["dreg"], l["date"]) for v in case["vehicles"] for l in v["licences"]}


def main(argv):
    real = E.bridges()
    out = {"bridge": {}, "encoder": {}, "reading_R1": {}}
    for case in K.CASES:
        base = answers(case)
        changed = set()
        for v in case["vehicles"]:
            for l in v["licences"]:
                y, _ = real[(case["id"], l["id"])]
                E.bridges = lambda l=l, y=y: {**real, (case["id"], l["id"]): (6, 0) if y < 6 else (5, 0)}
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
