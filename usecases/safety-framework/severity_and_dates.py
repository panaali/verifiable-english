"""Families S and D: the severity document D2 (`risk@0`) and the date document D3 (`ve-units@1`).

D2 is a risk environment: one harm constant per named level, classed by the
text's own words ("severe" for CCLs, "significant but not severe" for TCLs,
"catastrophic" for the L7 rationale), with the one order the Glossary states
(severe above significant). Its decision record states, for each level, that
deploying an unmitigated model at that level *might* lead to that level's harm
(the CCL and TCL definitions: "absent mitigation measures ... may pose
heightened risk"). Nothing states that it *leads to* the harm. The Lean risk
route (`ve_risk_route`) admits the environment, regenerates the order, class
and outcome tables, and is the authority for every S answer except S4.

S4 asks about security levels, not harms, so it is asked in D1: the vocabulary
has the word `at_least_as_strong` and no premise uses it.

D3 states the version dates of 5.3 and the retrieval date as W6a day
quantities. VE's quantity prover finds certificates (replayed by VE's checker);
a refutation is a checked countermodel. RS10 is the reading set of the review
anchor in 5.1.
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(HERE))

from conformance.risk import Log, base, const, record, statement  # noqa: E402
from ve.environment import Environment  # noqa: E402
from ve.profiles import LANGUAGE, SPEC_REVISION  # noqa: E402
from ve.units import check_quantity_certificate, day_number, prove_quantity, quantity_countermodel  # noqa: E402

RISK_ROUTE = REPO / "lean/.lake/build/bin/ve_risk_route"
LEVELS = {  # level -> (class, the text's words)
    "cbrn_uplift_tcl": ("significant", "CBRN TCL: \"significant but not severe harm\" (2.2.1)"),
    "cbrn_uplift_level_1": ("severe", "\"additional expected harm at severe scale\" (table 2.2.1.a)"),
    "cyber_uplift_level_1": ("severe", "\"additional expected harm at severe scale\" (table 2.2.2.a)"),
    "harmful_manipulation_level_1": ("severe", "\"additional expected harm at severe scale\" (table 2.2.3.a)"),
    "stealth_and_situational_awareness_tcl": ("significant", "TCL: \"significant but not severe levels of harm\" "
                                                             "(Glossary)"),
    "ml_rd_acceleration_level_1": ("severe", "ML R&D CCLs: risks that \"may reach a severe scale\" (3.2.2)"),
    "ml_rd_automation_level_1": ("severe", "ML R&D CCLs: risks that \"may reach a severe scale\" (3.2.2)"),
}
CATASTROPHIC = "harm_of_unchecked_ml_rd_automation"


def risk_environment():
    harms = {f"harm_of_{level}": cls for level, (cls, _) in LEVELS.items()}
    harms[CATASTROPHIC] = "catastrophic"
    descriptions = {f"harm_of_{level}": words for level, (_, words) in LEVELS.items()}
    descriptions[CATASTROPHIC] = ("the L7 rationale: \"This could be catastrophic if there is no effective way of "
                                  "defending\" (3.2.2)")
    return {"language": LANGUAGE, "profiles": ["alternatives@0", "norms@0", "relational-fol@0", "risk@0"],
            "spec_revision": SPEC_REVISION,
            "vocabulary": {
                "sorts": {"developer": {"description": "the developer that decides on a deployment"},
                          "action": {"description": "a deployment the developer may take"},
                          "harm": {"description": "the harm a level's definition names"}},
                "predicates": {
                    "available": base(["action", "developer"], "{0} is available to {1}"),
                    "leads_to": base(["action", "harm"], "{0} leads to {1}"),
                    "inaction": base(["action"], "{0} is inaction"),
                    "taken": base(["action"], "{0} is taken"),
                    "permitted": {"arguments": ["action"], "description": "the deployment may be taken",
                                  "regulated": {"role": "permission", "default": "allow", "act": "{0} be taken"}},
                    "required": {"arguments": ["action"], "description": "the deployment must be taken",
                                 "regulated": {"role": "obligation", "default": "deny", "act": "{0} be taken",
                                               "permission": "permitted"}}},
                "constants": {h: const("harm", descriptions[h]) for h in harms}},
            "alternatives": {"chooser": "developer", "action": "action", "harm": "harm", "available": "available",
                             "leads_to": "leads_to", "outcomes": "signed", "decided_by": "the developer",
                             "performed": {"permission": "permitted", "obligation": "required"},
                             "inaction": "inaction", "taken": "taken"},
            "risk": {"severity": {"sort": "severity", "classes": ["catastrophic", "severe", "significant"],
                                  "more_severe": [["severe", "significant"]], "unranked": [],
                                  "decided_by": "the framework's Glossary"},
                     "harm_classes": [[h, c] for h, c in harms.items()], "unexamined": "possible"}}


def risk_run(*cases):
    out = subprocess.run([str(RISK_ROUTE), "-"], input=json.dumps(list(cases)), text=True, capture_output=True,
                         timeout=600)
    if out.returncode not in (0, 1) or not out.stdout:
        raise SystemExit(f"ve_risk_route failed: {out.stderr[:500]}")
    return json.loads(out.stdout)


def d2(order_mutant=False):
    env = risk_environment()
    if order_mutant:
        env["risk"]["severity"]["more_severe"].append(["catastrophic", "severe"])
    policy = risk_run({"id": "p", "kind": "risk-elaborate", "environment": env, "document": {"norms": []}})[0]
    if policy.get("status") != "ok":
        raise SystemExit(f"D2 not admitted: {policy}")
    log = Log()
    seq = 1
    cells = [(f"deploy_{level}", f"harm_of_{level}") for level in LEVELS]
    cells.append(("deploy_ml_rd_automation_level_1", CATASTROPHIC))
    for action, harm in cells:
        log.add(seq, f"T{seq}", "statement", statement(action, harm, "might", author="the framework",
                                                       support="testimony"))
        seq += 1
    alternatives = [{"name": f"deploy_{level}", "label": f"deploying an unmitigated model that has reached {level}"}
                    for level in LEVELS] + [{"name": "nothing", "label": "not deploying", "inaction": True}]
    decision = log.add(100, "D", "decision", record("severity", "the_developer", "the developer",
                                                    (policy["environment_id"], policy["document_hash"]),
                                                    alternatives, [], log.cite(*[e["id"] for e in log.entries])))
    report = risk_run({"id": "d", "kind": "risk-decision", "environment": env, "document": {"norms": []},
                       "decision": decision, "entries": log.entries[:-1]})[0]
    if report.get("status") != "ok":
        raise SystemExit(f"D2 decision not admitted: {report}")
    classes = {}
    order = set()
    for premise in policy["risk_premises"]:
        ast = premise["ast"]
        if premise["label"] == "risk:class":
            classes[ast[2][1]] = ast[3][1]
        if premise["label"] == "risk:order" and ast[0] == "binary":
            order.add((ast[2][1], ast[3][1]))
    might = {(m["alternative"], m["harm"]) for m in report["tables"]["might"]}
    leads = {(m["alternative"], m["harm"]) for m in report["tables"]["leads"]}
    return {"environment_id": policy["environment_id"], "document_hash": policy["document_hash"],
            "decision_record_id": report["decision_record_id"], "classes": classes,
            "order": sorted(order), "unranked": policy["unranked_severities"],
            "stated_cells": [{"alternative": a, "harm": h, "might": (a, h) in might, "leads": (a, h) in leads}
                             for a, h in cells],
            "might_cells": len(might), "leads_cells": len(leads), "conditional_on": report["conditional_on"],
            "unexamined_possible": len(report["lines"]["unexamined_possible"])}


def family_s(d2_result):
    classes, order = d2_result["classes"], {tuple(p) for p in d2_result["order"]}
    out = {}
    for level in LEVELS:
        out[f"S1-{level}"] = classes.get(f"harm_of_{level}", "UNKNOWN")
    import vocabulary as V
    critical = [l for l in LEVELS if classes[f"harm_of_{l}"] == "severe"]
    tracked = [l for l in LEVELS if l not in critical]
    s2 = all((classes[f"harm_of_{c}"], classes[f"harm_of_{t}"]) in order for c in critical for t in tracked)
    out["S2"] = "ALL" if s2 else "NONE"
    ordered = ("catastrophic", "severe") in order or ("severe", "catastrophic") in order
    out["S3"] = "ALL" if ordered else "NONE"
    cell = next(c for c in d2_result["stated_cells"]
                if c["alternative"] == "deploy_cbrn_uplift_level_1" and c["harm"] == "harm_of_cbrn_uplift_level_1")
    out["S5"] = "ALL" if cell["might"] and classes["harm_of_cbrn_uplift_level_1"] == "severe" else "NONE"
    out["S6"] = "ALL" if cell["leads"] else "NONE"
    out["S4"] = s4()
    del V
    return out


def s4(extra=()):
    """Is "security_level_4 is at least as strong as security_level_3" entailed by the D1 premises?"""
    import run as R
    import translation as T
    from ve import ast as A
    premises = tuple(f for _, _, formulas in T.facts() for f in formulas) + tuple(extra)
    goal = A.Binary("at_least_as_strong", A.Const("security_level_4"), A.Const("security_level_3"))
    if R.refute(premises, [], goal) is not None:
        return "ALL"
    env = T.base_environment()
    atoms = frozenset(a for a in R.fact_atoms() if a[0] in env.predicates)
    model = R._model(env, atoms)
    countermodel = all(R.holds(env, f, model) for f in premises) and not R.holds(env, goal, model)
    return "NONE" if countermodel else "UNKNOWN"


# --- D3: dates ----------------------------------------------------------------------------------

DATES = {  # constant -> (ISO date, source)
    "version_1_0_date": ("2024-05-17", "5.3 \"Version 1.0 (May 17, 2024)\""),
    "version_2_0_date": ("2025-02-04", "5.3 \"Version 2.0 (February 4, 2025)\""),
    "version_3_0_date": ("2025-09-22", "5.3 \"Version 3.0 (September 22, 2025)\""),
    "version_3_1_date": ("2026-04-17", "title page \"Published : April 17, 2026\"; 5.3 \"Version 3.1 (April 17, 2026)\""),
    "retrieval_date": ("2026-10-01", "PLAN 1: the pinned PDF was retrieved on 2026-10-01 (an observation)"),
}


def date_environment():
    constants = {name: {"sort": "$int", "unit": "day", "description": source,
                        "verbalisation": "the " + name.replace("_", " ").replace(" date", " date")}
                 for name, (_, source) in DATES.items()}
    constants["review_deadline"] = {"sort": "$int", "unit": "day",
                                    "description": "the last day by which the yearly review of 5.1 is due",
                                    "verbalisation": "the review deadline"}
    constants["review_anchor"] = {"sort": "$int", "unit": "day",
                                  "description": "the day from which \"at least once a year\" (5.1) is counted "
                                                 "(RS10: the publication of 3.1, or an unstated last review)",
                                  "verbalisation": "the review anchor"}
    return {"language": LANGUAGE, "profiles": ["order@0", "relational-fol@0", "time@0"],
            "spec_revision": SPEC_REVISION, "unit_schema": "ve-units@1",
            "units": {"day": {"scale": "1", "display": {"kind": "iso_date"}},
                      "elapsed_day": {"scale": "1", "display": {"kind": "decimal", "label": "days"}}},
            "vocabulary": {"sorts": {}, "predicates": {}, "constants": constants}}


def q(formula):
    return {"format": "ve-quantity@1", "formula": formula}


def day(name):
    return ["const", "day", name]


def d3():
    env = Environment(date_environment())
    stated = [q(["date_on", day(name), ["date", iso]]) for name, (iso, _) in DATES.items()]
    order = list(DATES)[:4]
    goals = {
        "D1": q(["and", ["date_before", day(order[0]), day(order[1])],
                 ["and", ["date_before", day(order[1]), day(order[2])],
                  ["date_before", day(order[2]), day(order[3])]]]),
        "D3": q(["date_before", day("version_3_1_date"), day("retrieval_date")]),
    }
    out = {}
    for item, goal in goals.items():
        certificate = prove_quantity(env, stated, goal)
        valid = certificate is not None and check_quantity_certificate(env, stated, goal, certificate)
        out[item] = {"verdict": "ALL" if valid else "UNKNOWN", "certificate": bool(valid)}
    # D2 under RS10. Bridge (O9): "a year" from 2026-04-17 is 365 days (no 29 February in between).
    deadline = [q(["shift_days", day("review_deadline"), day("review_anchor"), "365"])]
    goal = q(["date_no_later", day("review_deadline"), ["date", "2027-04-17"]])
    readings = {}
    publication = stated + deadline + [q(["date_on", day("review_anchor"), day("version_3_1_date")])]
    certificate = prove_quantity(env, publication, goal)
    readings["publication"] = bool(certificate) and check_quantity_certificate(env, publication, goal, certificate)
    unstated = stated + deadline
    values = {name: str(day_number(iso)) for name, (iso, _) in DATES.items()}
    values["review_anchor"] = str(day_number("2026-06-01"))
    values["review_deadline"] = str(day_number("2026-06-01") + 365)
    refuted = quantity_countermodel(env, unstated, goal, {"complete": True, "domains": {}, "relations": {},
                                                          "constants": values})
    readings["unstated"] = not refuted
    out["D2"] = {"true": [{"RS10": r} for r, holds in readings.items() if holds], "cone": ["RS10"],
                 "countermodel_for_unstated": refuted,
                 "countermodel_anchor": "2026-06-01 (a last review the text does not date)"}
    return out


def run():
    result = {"d2": d2(), "d3": d3()}
    result["S"] = family_s(result["d2"])
    # Mutant m3: an order SL2+ < SL3 < SL4 (S4) and an order on catastrophic (S3).
    from ve import ast as A
    invented = (A.Binary("at_least_as_strong", A.Const("security_level_3"), A.Const("security_level_2_plus")),
                A.Binary("at_least_as_strong", A.Const("security_level_4"), A.Const("security_level_3")))
    result["m3"] = {"S4": s4(invented), "traced_to_source": False}
    return result


def compare(result):
    key = {item["id"]: item for item in json.loads((HERE / "answer-key.json").read_text())["items"]}
    rows = []
    s = result["S"]
    for level in LEVELS:
        item = next(k for k in key.values() if k["item"] == f"SEVERITY:{level}")
        rows.append({"id": item["id"], "key": item["key"], "ve": s[f"S1-{level}"],
                     "agree": item["key"] == s[f"S1-{level}"]})
    for item_id in ("S2", "S3", "S4", "S5", "S6"):
        rows.append({"id": item_id, "key": key[item_id]["key"], "ve": s[item_id], "agree": key[item_id]["key"] == s[item_id]})
    d = result["d3"]
    for item_id in ("D1", "D3"):
        rows.append({"id": item_id, "key": key[item_id]["key"], "ve": d[item_id]["verdict"],
                     "agree": key[item_id]["key"] == d[item_id]["verdict"]})
    d2_true = d["D2"]["true"]
    ve = "ALL" if len(d2_true) == 2 else "NONE" if not d2_true else f"SOME(RS10={d2_true[0]['RS10']})"
    rows.append({"id": "D2", "key": key["D2"]["key"], "ve": ve, "agree": ve == key["D2"]["key"]})
    return rows


if __name__ == "__main__":
    result = run()
    print(json.dumps({k: result[k] for k in ("S", "d3", "m3")}, indent=1))
    print(compare(result))
