"""Which answers lean on what is decided outside the text (staged route, no Lean): flip each stated judgment or stated
convention (translation.STATED and the half-up convention, per item) and each encoder judgement (FLIPS below), re-run
the case, list the answers that change. No bridge exists in this law. SAME-FAMILY. Committed with the cases, never reads
answers. Usage: .venv/bin/python -B usecases/app_levy/flips.py [--out F]"""
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


def _drop(*fs):
    return lambda c: [c["facts"].remove(f) for f in fs]


def _add(*fs):
    return lambda c: c["facts"].extend(fs)


def _move_totals(first, second):
    def fn(c):
        for base in ("paid", "due"):
            a, b = f"{base}_{first}", f"{base}_{second}"
            c["ints"][a], c["ints"][b] = c["ints"][b], c["ints"][a]
    return fn


# encoder judgement -> the other reading (cases.py "judgement")
FLIPS = {
    "L011": ("no s. 101(2) determination read from the written agreement", _drop("detmade:g")),
    "L015": ("'replaced it with' not read as an alteration", _drop("altmade:g")),
    "L017": ("the action of 20 May 2027 read as not taken within the period", _add("not_taken8:g")),
    "L018": ("the action of 30 May 2027 read as taken within the period", _drop("not_taken8:g")),
    "L024": ("the stated totals written on the second member", _move_totals("wilding", "yew")),
    "L025": ("the stated totals written on the second member", _move_totals("alder", "beech")),
    "L026": ("the stated totals written on the second member", _move_totals("dahlia", "elder")),
    "L035": ("the stated totals written on the second member", _move_totals("bay", "cove")),
}


def answers(case):
    return R.run_case(case)[0]


def one(case):
    out = {"stated": {}, "encoder": {}}
    base = answers(case)
    if True:
        items = {"person": case["persons"], "group": list(case["groups"])}
        for s in (*T.STATED, "halfup"):
            kind = "group" if s in T.FACTS_GROUP else "person"
            for x in items[kind]:
                if s == "rnd_fig" and f"rnd_{x}" not in case["ints"]:
                    continue  # a stated figure flip needs a stated figure (none here: not a reading)
                tag = f"{s}:{x}"
                c = copy.deepcopy(case)
                c["facts"] = [f for f in c["facts"] if f != tag] if tag in c["facts"] else c["facts"] + [tag]
                got = answers(c)
                out["stated"].setdefault(s, []).extend(q for q in got if got[q] != base[q])
        if case["id"] in FLIPS:
            what, fn = FLIPS[case["id"]]
            c = copy.deepcopy(case)
            fn(c)
            got = answers(c)
            out["encoder"][case["id"]] = {"flip": what, "changed": [q for q in got if got[q] != base[q]]}
    return out


def main(argv):
    from concurrent.futures import ProcessPoolExecutor
    out = {"stated": {}, "encoder": {}}
    with ProcessPoolExecutor(max_workers=6) as pool:
        for part in pool.map(one, K.CASES):
            for s, qs in part["stated"].items():
                out["stated"].setdefault(s, []).extend(qs)
            out["encoder"].update(part["encoder"])
    text = json.dumps(out, indent=1, sort_keys=True)
    if "--out" in argv:
        Path(argv[argv.index("--out") + 1]).write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main(sys.argv[1:])
