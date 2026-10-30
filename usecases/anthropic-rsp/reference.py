"""Independent, stdlib-only reading of PLAN 3 and 4 for A, B, C and G.

This module does not import VE or the translation.  It compares its own choice
sets with the frozen key, so a wrong key cell is reported, never rewritten.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES = {c["id"]: c for c in json.loads((HERE / "cases.json").read_text())["cases"]}
SETS = {"RS1": ("cond", "uncond", "ov"), "RS2": ("F", "Ds"),
        "RS3o": ("suff", "iff"), "RS3i": ("suff", "iff"),
        "RS3c": ("third", "result"), "RS4": ("scope", "rel"),
        "RS7": ("exec", "final"), "RS11": ("at", "trigger"),
        "RS12strive": ("default", "intent")}
ALIASES = {"cond": ("RS1", "cond"), "uncond": ("RS1", "uncond"),
           "Ds": ("RS2", "Ds"), "rel": ("RS4", "rel"),
           "trigger": ("RS11", "trigger"), "intent": ("RS12strive", "intent")}


def choices(names):
    return [dict(zip(names, values)) for values in itertools.product(*(SETS[n] for n in names))]


def case_answer(item):
    id_ = item["id"]
    case = CASES.get(item["case"])
    if id_.startswith("A-"):
        target = int(item["item"][-1])
        reached = f"T{target}" in case["thresholds"]
        if item["item"].startswith("PROT"):
            return ("RS1",), lambda c: c["RS1"] == "uncond" or c["RS1"] == "cond" and reached
        return ("RS2",), lambda c: reached and c["RS2"] == "Ds"
    if id_.startswith("B-"):
        facts = case["findings"]
        scope = (id_[:5] == "B-PUB" or id_.startswith("B-INTD") or
                 id_.startswith("B-AUT") and facts.get("OT22") is True)
        return (), lambda c: scope
    if id_.startswith("C"):
        if id_ in ("C1", "C7", "C-doc"):
            return ("RS4",), lambda c: c["RS4"] == "rel"
        return (), lambda c: False
    if id_ == "G4":
        return ("RS11",), lambda c: c["RS11"] == "trigger"
    if id_ == "G8":
        return ("RS12strive",), lambda c: c["RS12strive"] == "intent"
    if id_ == "G7":
        return (), lambda c: {"REQUIRED:PROMPT_BOARD_NOTICE": False,
                              "COVERED:QUARTERLY_UPDATE": True}
    if id_.startswith("G"):
        return (), lambda c: True
    raise KeyError(id_)


def matches(key, names, holds):
    if isinstance(key, dict):
        return all(all(bool(holds(c)[part]) == (answer == "ALL") for c in choices(names))
                   for part, answer in key.items())
    if key in ("ALL", "NONE"):
        return all(bool(holds(c)) == (key == "ALL") for c in choices(names))
    if not key.startswith("SOME("):
        return False
    terms = [dict(ALIASES[word.strip()] for word in term.split("&"))
             for term in key[5:-1].split("|")]
    return all(bool(holds(c)) == any(all(c.get(name, SETS[name][0]) == value
                                             for name, value in term.items()) for term in terms)
               for c in choices(names))


def compare():
    rows = []
    for item in json.loads((HERE / "answer-key.json").read_text())["items"]:
        if item["id"][0] not in "ABCG":
            continue
        names, holds = case_answer(item)
        rows.append({"id": item["id"], "agrees": matches(item["key"], names, holds)})
    return rows


def main():
    rows = compare()
    print(f"independent reference versus frozen key: {sum(r['agrees'] for r in rows)}/{len(rows)}")
    for row in rows:
        if not row["agrees"]:
            print("  differs", row["id"])


if __name__ == "__main__":
    main()
