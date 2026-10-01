"""An independent reading of PLAN sections 3 and 4 in plain Python (stdlib only, no `ve` import).

It recomputes families A, B, C and G of the answer key from the commitment
table (PLAN 4.2) and the reading sets (PLAN 3.1), written directly as Python
conditions, and reports where it differs from the key (PLAN 6, "Independent
check of the key") and from VE (`results.json`). It shares no code with the
VE translation. The same author wrote both, so it checks transcription and
arithmetic, not judgement.

    python usecases/safety-framework/reference.py
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES = {c["id"]: c for c in json.loads((HERE / "cases.json").read_text())["cases"]}
ACTIVITIES = json.loads((HERE / "cases.json").read_text())["activities"]
SETS = {"RS1": ("S", "G"), "RS2": ("P", "U"), "RS3": ("F", "Ds"), "RS4aim": ("default", "intent"),
        "RS5": ("D", "R"), "RS6": ("same", "different"), "RS7": ("E", "M"), "RS8": ("scope", "rel"),
        "RS9": ("same", "different")}
MISUSE = {"cbrn_uplift_tcl", "cbrn_uplift_level_1", "cyber_uplift_level_1", "harmful_manipulation_level_1"}
ML_RD = {"stealth_and_situational_awareness_tcl", "ml_rd_acceleration_level_1", "ml_rd_automation_level_1"}
TRACKED = {"cbrn_uplift_tcl", "stealth_and_situational_awareness_tcl"}
RECOMMENDED = {"cbrn_uplift_level_1": "SL2+", "cyber_uplift_level_1": "SL2+", "harmful_manipulation_level_1": "SL2+",
               "ml_rd_acceleration_level_1": "SL3", "ml_rd_automation_level_1": "SL4"}


def situation(case, without=()):
    facts = set(ACTIVITIES.get(case.get("activity") or "", [])) | {f[0] for f in case["findings"] if len(f) == 2}
    return {"levels": set(case["levels"]), "facts": facts - set(without)}


def requirements(s, c):
    """{atom: "must" | "need not" | "must not proceed"} at situation s under choice c (PLAN 4.2)."""
    levels, f = s["levels"], s["facts"]
    external, internal, hri = "external" in f, "internal" in f, "high_risk" in f
    dev = "further_development" in f
    misuse = levels & MISUSE
    mlrd_ccl = levels & (ML_RD - TRACKED)
    mlrd_tcl = levels & (ML_RD & TRACKED)
    out = {}
    if c["RS1"] == "G":
        if misuse:
            out["SEC"] = "must"                                   # F9: for further development or deployment
            if external:
                out["DM"] = "must"                                # "required only for external deployment"
            elif (internal or dev) and c["RS8"] == "rel":
                out["DM"] = "need not"                            # "not internal deployment or further development"
        if mlrd_ccl or mlrd_tcl:
            out["SEC"] = "must"                                   # F10, F11
            if external or hri:
                out["DM"] = "must"                                # "only for external and high-risk internal"
            elif dev and c["RS8"] == "rel":
                out["DM"] = out.get("DM", "need not")             # "not further development"
            if misuse and hri and c["RS8"] == "rel" and c["RS9"] == "same" and mlrd_ccl:
                out["DM"] = "conflict"                            # F9 releases, F10 requires one act (C3)
    gov = False
    if external and (c["RS2"] == "U" or misuse or levels & ML_RD):
        gov = True                                                # F12 (P: misuse T/CCL; U: every model), F13
    if hri and (c["RS2"] == "U" or levels & ML_RD):
        gov = True                                                # F13: high-risk internal deployment
    if gov and "governance_found_acceptable" not in f:
        out["GOV"] = "must not proceed"
    if "first_deployment" in f and "frontier" in f:
        released = c["RS7"] == "E" and "low_risk" in f and "governance_found_acceptable" in f
        out["CCA"] = "need not" if released else "must"          # F2, F3 (footnote 4)
    if levels:
        out["RRA"] = "must"                                       # F7
    if levels - TRACKED:
        out["SC"] = "must"                                        # F7
    if mlrd_tcl:
        out["PRA"] = "must"                                       # F17
    if c["RS3"] == "Ds" and any(l in RECOMMENDED for l in levels):
        out["RECSEC"] = "should"                                  # F16 under Ds (N2: default force)
    return out


def verdict(holds, sets):
    space = list(itertools.product(*(SETS[s] for s in sets)))
    true = [x for x in space if holds({**{k: v[0] for k, v in SETS.items()}, **dict(zip(sets, x))})]
    if not true:
        return "NONE", []
    if len(true) == len(space):
        return "ALL", []
    return "SOME", [dict(zip(sets, x)) for x in true]


ALL_SETS = ("RS1", "RS2", "RS3", "RS7", "RS8", "RS9")


def family_a_b():
    rows = {}
    for cid, case in CASES.items():
        if case["family"] == "A":
            for atom in ("DM", "SEC", "GOV", "CCA"):
                if atom == "GOV":
                    s = situation(case, without=("governance_found_acceptable",))
                    rows[f"{cid}/GOV"] = verdict(lambda c: requirements(s, c).get("GOV") == "must not proceed",
                                                 ALL_SETS)
                else:
                    s = situation(case)
                    rows[f"{cid}/{atom}"] = verdict(lambda c, a=atom: requirements(s, c).get(a) in ("must",
                                                                                                   "conflict"),
                                                    ALL_SETS)
        if case["family"] == "B":
            s = situation(case)
            for atom in ("RRA", "SC", "PRA", "RECSEC", "DISC"):
                rows[f"{cid}/{atom}"] = verdict(lambda c, a=atom: a in requirements(s, c), ALL_SETS)
    return rows


def matches(key_verdict, ours):
    """Compare a key verdict with (verdict, true choices), conditions as sets of choices."""
    kind, true = ours
    if key_verdict in ("ALL", "NONE"):
        return key_verdict == kind
    if kind != "SOME":
        return False
    import re
    cond = re.fullmatch(r"SOME\((.+)\)", key_verdict)[1]
    aliases = {"G": ("RS1", "G"), "S": ("RS1", "S"), "U": ("RS2", "U"), "P": ("RS2", "P"), "Ds": ("RS3", "Ds"),
               "M": ("RS7", "M"), "E": ("RS7", "E"), "rel": ("RS8", "rel"), "R": ("RS5", "R")}
    literals = []
    for part in cond.split("&"):
        part = part.strip()
        literals.append(tuple(part.split("=")) if "=" in part else aliases[part])
    space = list(itertools.product(*(SETS[s] for s in ALL_SETS)))
    wanted = {x for x in space if all(dict(zip(ALL_SETS, x)).get(k, SETS[k][0]) == v for k, v in literals)}
    got = {x for x in space if any(all(dict(zip(ALL_SETS, x))[k] == v for k, v in t.items()) for t in true)}
    return wanted == got


def family_c_g():
    rows = {}
    witness = {"levels": {"cbrn_uplift_level_1", "ml_rd_acceleration_level_1"}, "facts": {"internal", "high_risk"}}
    conflict = verdict(lambda c: requirements(witness, c).get("DM") == "conflict", ALL_SETS)
    rows["C3"] = rows["C-doc"] = conflict
    for cid in ("C1", "C2", "C4", "C5"):
        rows[cid] = ("NONE", [])        # PLAN 6.4: blocked default (C1), exception (C2), no shared act (C4, C5)
    g1 = situation(CASES["G1"])
    rows["G1"] = verdict(lambda c: "SEC" not in requirements(g1, c), ALL_SETS)
    g2 = situation(CASES["G2"])
    rows["G2"] = verdict(lambda c: "GOV" not in requirements(g2, c), ALL_SETS)
    return rows


def rel_rows():
    """The REL annotations of family A: a "need not" on DM."""
    rows = {}
    for cid, case in CASES.items():
        if case["family"] == "A":
            s = situation(case)
            rows[f"{cid}/DM"] = verdict(lambda c: requirements(s, c).get("DM") == "need not", ALL_SETS)
    return rows


def main():
    key = {k["id"]: k for k in json.loads((HERE / "answer-key.json").read_text())["items"]}
    rows = {**family_a_b(), **family_c_g()}
    rel = rel_rows()
    differ = [i for i, r in rows.items() if not matches(key[i]["key"], r)]
    differ += [f"{i} (REL)" for i, r in rel.items() if "rel" in key[i] and not matches(key[i]["rel"], r)]
    items = [i for i in differ if not i.endswith("(REL)")]
    notes = [i for i in differ if i.endswith("(REL)")]
    print(f"reference against the key: {len(rows) - len(items)}/{len(rows)} items (A, B, C, G1, G2); "
          f"REL notes differing: {len(notes)}")
    for i in differ:
        print("  differs", i)
    return {"compared": len(rows), "items_differ": items, "rel_notes_differ": notes}


if __name__ == "__main__":
    main()
