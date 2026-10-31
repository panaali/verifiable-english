"""Independent, stdlib-only reading of PLAN 3 and 4 for families A, B, C and G.

This module does not import VE or the translation.  It compares its own choice sets with the frozen key, so a
wrong key cell is reported, never rewritten.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES = {c["id"]: c for c in json.loads((HERE / "cases.json").read_text())["cases"]}
SETS = {"RS2": ("nest", "sep"), "RS3": ("ext", "any"), "RS18": ("inuse", "devonly"), "RS4": ("N", "P"),
        "RS4s": ("scoped", "unscoped"), "RS11": ("final", "process"), "RS17": ("bperm", "bmight"),
        "RS15": ("explanation", "rule")}
ALIASES = {"nest": ("RS2", "nest"), "any": ("RS3", "any"), "inuse": ("RS18", "inuse"), "N": ("RS4", "N"),
           "unscoped": ("RS4s", "unscoped"), "final": ("RS11", "final"), "bperm": ("RS17", "bperm"),
           "explanation": ("RS15", "explanation")}
HIGH = {"BIO-C": "BIO-H", "CYB-C": "CYB-H", "AIS-C": "AIS-H"}  # PLAN 4.1: one High and one Critical per category


def choices(names):
    return [dict(zip(names, values)) for values in itertools.product(*(SETS[n] for n in names))]


def reached(case, c):
    levels = set(case["levels"])
    if c.get("RS2") == "nest":
        levels |= {HIGH[level] for level in case["levels"] if level in HIGH}
    return levels


def a_answer(case, atom):
    x = case["activity"]
    high = lambda c: any(level.endswith("-H") for level in reached(case, c))
    critical = any(level.endswith("-C") for level in case["levels"])
    internal = x in ("INT", "LINT")
    if atom == "SEC":    # F1's SEC bullet in every High row, F4 (C.3), 2.2's controls "as they are developed"
        return ("RS2",), high
    if atom == "MIS":    # BIO-H "before external deployment", CYB-H "for external deployment"
        return ("RS2",), lambda c: x == "EXT" and bool({"BIO-H", "CYB-H"} & reached(case, c))
    if atom == "ALN":    # CYB-H "for large-scale internal deployment"
        return ("RS2",), lambda c: x == "LINT" and "CYB-H" in reached(case, c)
    if atom == "SUF":    # F2 (High, before deployment: RS3) or F3 (Critical, during development: RS18)
        return ("RS2", "RS3", "RS18"), lambda c: (
            high(c) and (x == "EXT" or internal and c["RS3"] == "any")
            or critical and (x == "DEV" or internal and c["RS18"] == "inuse"))
    if atom == "HALT":   # Critical rows, "halt further development" while no Critical standard is specified
        return (), lambda c: critical and x == "DEV"
    raise KeyError(atom)


def b_answer(case, atom):
    high = lambda c: any(level.endswith("-H") for level in reached(case, c))
    if atom in ("CAPREP", "PUBRES"):   # every covered model; every major deployment
        return (), lambda c: True
    if atom == "SAFEREP":              # section 4: covered systems that reach a capability threshold
        return (), lambda c: bool(case["levels"])
    if atom == "MREP":                 # Table 2 LRA; the case leaves the LRA capability unset
        return ("RS4", "RS4s"), lambda c: bool(case["levels"]) and c["RS4"] == "N" and c["RS4s"] == "unscoped"
    if atom == "DISC":                 # 5.2 "beyond a High threshold"
        return ("RS2",), high
    if atom == "CONTRIB":              # BIO-C's and CYB-H's rows
        return ("RS2",), lambda c: "BIO-C" in case["levels"] or "CYB-H" in reached(case, c)
    raise KeyError(atom)


def case_answer(item):
    id_ = item["id"]
    case = CASES.get(item["case"])
    if id_.startswith("A-"):
        return a_answer(case, item["item"])
    if id_.startswith("B-"):
        return b_answer(case, item["item"])
    if id_.startswith("C"):
        if id_ in ("C6", "C-doc"):     # Leadership's final decisions against the Board's permission to reverse
            return ("RS11", "RS17"), lambda c: c["RS11"] == "final" and c["RS17"] == "bperm"
        return (), lambda c: False
    if id_ == "G6":                    # change log item 4 is a rule only under RS15 = rule
        return ("RS15",), lambda c: c["RS15"] == "explanation"
    if id_ == "G8":                    # F2 is a deployment rule, F3 is Critical's
        return (), lambda c: False
    if id_.startswith("G"):
        return (), lambda c: True
    raise KeyError(id_)


def terms(key):
    if not key.startswith("SOME(") or key.count("(") != key.count(")"):
        return None
    out = []
    for term in key[5:-1].replace("∨", "|").replace("∧", "&").split("|"):
        words = [w.strip().strip("()").strip() for w in term.split("&")]
        if not all(w in ALIASES for w in words):
            return None
        out.append(dict(ALIASES[w] for w in words))
    return out


def matches(key, names, holds):
    if key in ("ALL", "NONE"):
        return all(bool(holds(c)) == (key == "ALL") for c in choices(names))
    wanted = terms(key)
    if wanted is None:
        return False
    return all(bool(holds(c)) == any(all(c.get(n) == v for n, v in t.items()) for t in wanted)
               for c in choices(sorted(set(names) | {n for t in wanted for n in t})))


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
