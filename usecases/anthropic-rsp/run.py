"""Answer the frozen RSP questions with the translated VE documents.

The key is read only by compare().  A result records the route and the selected
rule or certificate; an unsupported question remains UNDECIDED with its cause.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rsp_translation as T  # noqa: E402
import rsp_vocabulary as V  # noqa: E402
from ve.model import FiniteModel  # noqa: E402
from ve.norms import check_conflict  # noqa: E402
from ve import ast as A  # noqa: E402
from ve.entailment import prove_entailment, check_entailment_certificate  # noqa: E402
from ve.softnorms import SoftEnvironment, SoftNormDocument  # noqa: E402

RESULTS = HERE / "results.json"
THRESHOLDS = dict(zip((f"T{i}" for i in range(1, 5)), V.THRESHOLDS))
CASES = {c["id"]: c for c in json.loads((HERE / "cases.json").read_text())["cases"]}
SETS = T.READING_SETS
BASE = {name: values[0] for name, values in SETS.items()}
OT = {"OT2": "more_capable_than_analyzed", "OT3a": "exceeds_prior_report",
      "OT3b": "exceeds_all_analyzed", "OT4": "significantly_redacted", "OT5": "highly_capable",
      "OT7": "delay_needed", "OT8": "clear_evidence", "OT10": "material_safety_risk",
      "OT11": "noteworthy", "OT15": "full_substitution_at_competitive_cost",
      "OT16": "double_rate", "OT17": "automation_attributable", "OT18": "marginal_justification",
      "OT19": "marginal_major_role", "OT22": "autonomous_research_use",
      "OT28": "continuation_accelerates"}
SITUATIONS = {
    "B-PUB": ("publicly_deployed",), "B-INT": ("internally_deployed",),
    "B-INTD": ("internally_deployed",), "B-AUT": ("internally_deployed",),
    "K2": ("publicly_deployed",), "K3": ("publicly_deployed",),
    "K4": ("internally_deployed",), "K7": ("risk_report_approved",),
    "K11": ("ltbt_requested_review",), "K12": ("selecting_reviewers",),
    "K13": ("candidate_has_financial_interest",),
    "K14": ("submitted_under_external_review",),
    "K15": ("noncompliance_report_received", "substantiated"),
    "K16": ("concerns_rso",), "K17": ("rsp_updated",),
    "K18": ("describes_mitigation_and_deviates",),
    "K19a": ("in_the_lead",), "K19b": ("in_the_lead",),
    "K20": ("competitors_strong_measures",), "K21": ("competitor_better_mitigation",),
    "K22": ("roadmap_goal_missed",), "G4": ("publicly_deployed",),
    "G7": ("noncompliance_report_received", "substantiated"),
    "G8": ("goal_revised_less_ambitious",),
}
PREDICATES = {
    "PUBLISH_RISK_REPORTS": "risk_reports_published", "OFF_CYCLE_ANALYSIS": "off_cycle_published",
    "MARGINAL_RISK_ANALYSES": "marginal_analysed", "BOARD_AND_LTBT_APPROVAL": "board_approved",
    "SHARE_WITH_BOARD_AND_LTBT": "governance_notified", "FULL_EXTERNAL_REVIEW": "full_review",
    "EXTERNAL_REVIEW": "ltbt_review", "LTBT_APPROVAL": "reviewers_approved",
    "CONSULT_BOARD": "reviewers_approved", "SELECT_REVIEWER": "candidate_selected",
    "SHARE_WITH_REVIEWERS_WITHIN_ONE_WEEK": "shared_with_reviewers",
    "PROMPT_BOARD_NOTICE": "board_notified", "PUBLIC_NOTICE": "public_notice",
    "BOARD_MEMBER_AMONG_RECIPIENTS": "board_member_recipient",
    "PUBLISH_BY_EFFECTIVE_DATE_AND_CHANGE_LOG": "update_published",
    "TRACK_AND_REPORT_DEVIATION": "deviation_reported", "STRONG_ARGUMENT": "argument_required",
    "DELAY": "delay", "MEET_OR_EXCEED_COMPETITOR_POSTURE": "posture_matched",
    "SIGNIFICANT_EFFORT": "significant_effort", "RISK_REPORT_ADDRESSES_MISS": "goal_miss_addressed",
    "OTHER_CONSEQUENCE": "delay", "QUARTERLY_UPDATE": "quarterly_updates",
    "ASSESS": "assessed_in_report", "INSCOPE": "in_scope",
}


def applies(block, choice):
    return all(choice.get(name) == value for name, value in block.when)


@lru_cache(maxsize=None)
def document(names, default, include=None):
    choice = dict(names)
    rules = [json.loads(T.parsed_rule(b.id)) for b in T.rule_blocks()
             if applies(b, choice) and (include is None or b.id in include)]
    included = {r["name"] for r in rules}
    for rule in rules:
        rule["over"] = [n for n in T.PRECEDENCE.get(rule["name"], ()) if n in included]
    return SoftNormDocument(SoftEnvironment(V.environment(default)), [{"norm": r} for r in rules])


def atoms(case):
    found = {("listed", name) for name in V.THRESHOLDS}
    found.update(("crossed", "s", THRESHOLDS[t]) for t in case["thresholds"])
    found.update((name, "s") for name in SITUATIONS.get(case["id"], ()))
    for term, value in case["findings"].items():
        if value and term in OT:
            found.add((OT[term], "s"))
    if case["findings"].get("OT5"):
        found.add(("crossed", "s", THRESHOLDS["T4"]))
    found.update((name, "s") for name in case.get("extra", ()))
    return found


def model(doc, case):
    env = doc.elaborated.base_environment()
    relations = {p: [] for p in env.predicates}
    for atom in atoms(case):
        if atom[0] in relations:
            relations[atom[0]].append(list(atom[1:]))
    return FiniteModel.from_dict(env, {"complete": True,
        "domains": {"situation": ["s"], "threshold": list(V.THRESHOLDS)},
        "constants": {c: c for c in env.constants},
        "relations": {p: sorted(v) for p, v in relations.items()}})


def selected(doc, case, predicate, sign, values=None):
    m = model(doc, case)
    sorts = V.environment()["vocabulary"]["predicates"][predicate]["arguments"]
    domains = [m.domains[s] for s in sorts]
    names = set()
    for args in itertools.product(*domains):
        if args[0] != "s" or (values is not None and tuple(args) != tuple(values)):
            continue
        names.update(r.name for r in doc.elaborated.selected_rules(predicate, m, args) if r.sign == sign)
    return sorted(names)


def cone(predicate):
    return tuple(sorted({set_id for b in T.rule_blocks()
        if json.loads(T.parsed_rule(b.id))["predicate"] == predicate for set_id, _ in b.when}))


def choices(sets):
    for values in itertools.product(*(SETS[s] for s in sets)):
        yield dict(zip(sets, values))


def query(case, predicate, sign=True, values=None, *, extra_sets=(), requirement=False):
    sets = tuple(sorted(set(cone(predicate)) | set(extra_sets)))
    rows = []
    for assignment in choices(sets):
        choice = {**BASE, **assignment}
        deny = document(tuple(sorted(choice.items())), "deny")
        allow = document(tuple(sorted(choice.items())), "allow")
        left = selected(deny, case, predicate, sign, values)
        right = selected(allow, case, predicate, sign, values)
        if requirement and V.REGULATED[predicate]["regulated"]["role"] != "obligation":
            left = right = []
        rows.append({"choice": assignment, "holds": bool(left and right),
                     "rules": sorted(set(left) & set(right)), "default_sensitive": left != right})
    return {"route": "D1 soft-norms@0 selected_rules, deny and allow completion",
            "cone": list(sets), "choices": rows}


def constant(value, route, reason):
    return {"route": route, "cone": [],
            "choices": [{"choice": {}, "holds": value, "reason": reason}]}


@lru_cache(maxsize=None)
def severity():
    import stage0
    return stage0.d2()


def severity_answer(id_):
    report = severity()
    if not report["admitted"]:
        return {"route": "D2 risk@0", "undecided": "resource limit or risk-route refusal"}
    if id_.startswith("S1-"):
        threshold = THRESHOLDS[id_[3:]]
        harm = "harm_of_" + threshold
        value = report["classes"].get(harm, "none")
        return {"route": "D2 risk@0 risk:class", "value": value,
                "reason": "risk environment harm class" if value != "none" else
                          "D2 refuses an unclassified T4 harm; no class was assigned"}
    if id_ in ("S3", "S4"):
        cell = next(c for c in report["stated_cells"] if c["harm"] == "harm_of_non_novel_chem_bio_weapons")
        field = "might" if id_ == "S3" else "leads"
        return constant(cell[field], "D2 risk@0 risk-decision", f"{field} cell for T1")
    if id_ == "S5":
        return constant(report["classes"].get("existential_threats") == "catastrophic",
                        "D2 risk@0 risk:class", "footnote 1's stated instance")
    return {"route": "D2 risk@0", "undecided": "VE limit (WG): no severity order between the T1 and T2 harms"}


@lru_cache(maxsize=None)
def dates():
    import stage0
    return stage0.d3()


def date_answer(id_):
    import stage0
    certificate = dates()["certificates"].get(id_)
    if certificate is not None:
        return constant(certificate, "D3 ve-units@1 quantity certificate replay", id_)
    if id_ == "D3a":
        env = stage0.date_environment(("start_day", "limit_day"))
        facts = [stage0._q(["date_on", stage0._day("start_day"), ["date", "2026-05-20"]]),
                 stage0._q(["shift_days", stage0._day("limit_day"), stage0._day("start_day"), "30"])]
        late = stage0._proved(env, facts, stage0._q(["date_before", stage0._day("limit_day"),
                                                      ["date", "2026-07-01"]]))
        if late:
            return constant(False, "D3 ve-units@1 quantity certificate replay", "30-day limit precedes publication")
        return {"route": "D3 ve-units@1", "undecided": "resource limit: no certificate for the 30-day violation"}
    return {"route": "D3 ve-units@1", "undecided": "VE limit (ET/QT): calendar-month cadence or approximate date"}


CLUSTERS = {
    "C1": ("f24-delay", "f26-need-not-delay"),
    "C2": ("f12-final", "f12-board-approval"),
    "C3": ("rows-cond", "rows-uncond", "f10-in-line"),
    "C4": ("f13-redact-p", "f16-only-legal"),
    "C5": ("f24-delay", "f25-delay"),
    "C6": ("f19-unredacted", "f13-minimize-default"),
    "C7": ("f25-delay", "f26-need-not-delay"),
}


def witness(id_):
    extra = {"C1": ("in_the_lead", "competitor_better_mitigation", "significant_lead"),
             "C2": ("marginal_major_role",),
             "C7": ("competitors_strong_measures", "competitor_better_mitigation")}
    return {"id": "W", "thresholds": [], "findings": {"OT5": True, "OT8": True, "OT7": True},
            "extra": extra.get(id_, ())}


@lru_cache(maxsize=None)
def conflict(id_):
    cluster = CLUSTERS.get(id_)
    if id_ == "C-doc":
        # Only pairs that can select opposite signs on one regulated predicate
        # can witness a conflict.  Both witnesses are checked on the full D1.
        sets = ("RS4",)
    else:
        sets = tuple(sorted({s for b in T.rule_blocks() if b.id in cluster for s, _ in b.when}))
    rows = []
    for assignment in choices(sets):
        choice = {**BASE, **assignment}
        pair = None if id_ == "C-doc" else cluster
        doc = document(tuple(sorted(choice.items())), "deny", pair)
        checks = []
        for target in (("C1", "C7") if id_ == "C-doc" else (id_,)):
            checked = check_conflict(doc.elaborated, model=model(doc, witness(target)))
            checks.append(checked.status)
        rows.append({"choice": assignment, "holds": "CONFLICT" in checks,
                     "w1": checks, "rules": list(pair) if pair else "whole D1"})
    return {"route": "D1 norms@0 W1 check_conflict with a validated witness model",
            "cone": list(sets), "choices": rows}


def t_case_formula(case):
    var = A.Var(0)
    nodes = []
    for term, value in case["findings"].items():
        name = OT.get(term, term)
        if name not in T.base_environment().predicates:
            continue
        node = A.Unary(name, var)
        nodes.append(node if value else A.Not(node))
    if not nodes:
        nodes.append(A.Top())
    body = nodes[0]
    for node in nodes[1:]:
        body = A.And(body, node)
    return A.Exists("situation", body)


def t_goal(negative=False):
    atom = A.Binary("crossed", A.Var(0), A.Const("automated_rd"))
    return A.Exists("situation", A.Not(atom) if negative else atom)


def t_proof(case, choice, negative=False):
    env = T.base_environment()
    premises = tuple(f for block, formulas in T.facts() if applies(block, choice) for f in formulas)
    stated = premises + (t_case_formula(case),)
    goal = t_goal(negative)
    proof = prove_entailment(env, stated, goal, max_steps=20000)
    if proof.status == "Found":
        if not check_entailment_certificate(env, stated, goal, proof.certificate).valid:
            raise AssertionError("T-family entailment certificate failed replay")
        return "replayed certificate"
    return None


def t_countermodel(case, choice, negative=False):
    """A complete one-situation model checked by VE against every selected premise."""
    from ve.evaluate import evaluate
    env = T.base_environment()
    found = atoms(case)
    if negative:
        # Counterexample to 'not met': crossing is possible without a complete
        # definition, or with scenario (2) unconstrained by its inner converse.
        found.update({("crossed", "s", THRESHOLDS["T4"]), ("highly_capable", "s")})
        if choice["RS3o"] == "iff" and choice["RS3i"] == "suff":
            found.add(("scenario_2", "s"))
    relations = {p: [] for p in env.predicates}
    for atom in found:
        if atom[0] in relations:
            relations[atom[0]].append(list(atom[1:]))
    m = FiniteModel.from_dict(env, {"complete": True,
        "domains": {"situation": ["s"], "threshold": list(V.THRESHOLDS)},
        "constants": {c: c for c in env.constants},
        "relations": {p: sorted(v) for p, v in relations.items()}})
    for block, formulas in T.facts():
        if applies(block, choice):
            for formula in formulas:
                result = evaluate(env, formula, m, trace=False)
                if result.value is not True:
                    return None
    result = evaluate(env, t_goal(negative), m, trace=False)
    return "validated countermodel" if result.value is False else None


def threshold_answer(id_, case):
    if id_ == "T5":
        return {"route": "D3 ve-units@1", "undecided": "VE limit (QT): factor-of-five quantity not represented in D3"}
    sets = ("RS3o", "RS3i", "RS3c")
    negative = id_ in ("T2b", "T4b")
    rows = []
    for assignment in choices(sets):
        choice = {**BASE, **assignment}
        proof = t_proof(case, choice, negative)
        counter = None if proof else t_countermodel(case, choice, negative)
        rows.append({"choice": assignment, "holds": bool(proof),
                     "reason": proof or counter or "UNKNOWN"})
    if any(row["reason"] == "UNKNOWN" for row in rows):
        return {"route": "D1 relational-fol@0", "undecided": "resource limit: neither proof nor countermodel",
                "choices": rows}
    return {"route": "D1 relational-fol@0 entailment certificate or validated finite countermodel",
            "cone": list(sets), "choices": rows}


def silence(case, predicates):
    parts = {name: query(case, name) for name in predicates}
    rows = []
    for assignment in choices(tuple(sorted(set().union(*(part["cone"] for part in parts.values()))))):
        holds = all(not any(r["holds"] for r in part["choices"] if all(
            assignment.get(s) == r["choice"].get(s) for s in part["cone"])) for part in parts.values())
        rows.append({"choice": assignment, "holds": holds,
                     "reason": "no selected rule on the queried acts"})
    return {"route": "D1 soft-norms@0 selected_rules, deny and allow completion; silence",
            "cone": sorted(set().union(*(part["cone"] for part in parts.values()))), "choices": rows}


def gap_answer(id_, case):
    if id_ == "G2":
        return silence(case, ("assessed_in_report", "off_cycle_published"))
    if id_ in ("G1", "G3", "G5", "G6"):
        feature = {"G1": "AP: no proceed act for the row plans",
                   "G3": "SC: an unlisted cyber threshold is outside D1's closed vocabulary",
                   "G5": "ET: no reviewer nonresponse consequence in D1",
                   "G6": "SC: no priority between the review and approval duties"}[id_]
        return {"route": "D1", "undecided": f"translation limit ({feature})"}
    if id_ == "G4":
        return {"route": "D3 ve-units@1", "undecided": "VE limit (ET): RS11 at/trigger deadline is not in D3"}
    return {"route": "D1", "undecided": "unmapped gap question"}


def never_answer(id_):
    if id_ == "N1":
        result = silence(CASES["B-VOL"], ("assessed_in_report",))
    elif id_ == "N2":
        result = silence(CASES["K21"], ("delay",))
        # Other Appendix A scenarios are absent from K21; this is the
        # F26-specific question under both RS4 readings.
    elif id_ == "N3":
        result = silence(CASES["K19a"], ("posture_matched",))
    else:
        return {"route": "D1", "undecided": "VE limit (SC): no exhaustive dead-rule or changelog-rule certificate"}
    result["route"] += "; family N witness situation"
    return result


def answer(item):
    id_, kind = item["id"], item["item"]
    case = CASES.get(item["case"])
    if id_.startswith("S"):
        return severity_answer(id_)
    if id_.startswith("D"):
        return date_answer(id_)
    if id_.startswith("C"):
        return conflict(id_)
    if id_.startswith("T"):
        return threshold_answer(id_, case)
    if id_.startswith("N"):
        return never_answer(id_)
    if id_.startswith("A-"):
        number = int(kind[-1])
        predicate = "plans_in_place" if kind.startswith("PROT") else "strong_argument"
        return query(case, predicate, values=("s", THRESHOLDS[f"T{number}"]))
    if id_.startswith("B-"):
        return query(case, PREDICATES[kind])
    if id_.startswith("K"):
        part = kind.split(":", 1)[-1]
        predicate = PREDICATES.get(part)
        if predicate is None:
            return {"route": "D1", "undecided": "translation limit: no predicate for this question"}
        if id_ in ("K9", "K10"):
            return {"route": "D1", "undecided": "translation limit (AP): F4's external-review bullet is bundled in plans_in_place"}
        return query(case, predicate, not kind.startswith("FORBIDS:"), requirement=kind.startswith("REQUIRED:"))
    if id_ == "G7":
        return {"route": "D1", "parts": {
            "REQUIRED:PROMPT_BOARD_NOTICE": query(case, PREDICATES["PROMPT_BOARD_NOTICE"]),
            "COVERED:QUARTERLY_UPDATE": query(case, PREDICATES["QUARTERLY_UPDATE"])}}
    if id_ == "G8":
        result = query(case, "goals_kept")
        for row in result["choices"]:
            row["holds"] = not row["holds"]
        result["route"] += "; silence is no selected goals_kept rule"
        return result
    if id_.startswith("G"):
        return gap_answer(id_, case)
    return {"route": "D1", "undecided": "VE limit: this question needs a conflict, silence, entailment, risk or time route"}


def verdict(result):
    if "undecided" in result:
        return "UNDECIDED"
    if "value" in result:
        return result["value"]
    if "parts" in result:
        return {name: verdict(part) for name, part in result["parts"].items()}
    yes = [r["choice"] for r in result["choices"] if r["holds"]]
    if not yes:
        return "NONE"
    if len(yes) == len(result["choices"]):
        return "ALL"
    return "SOME(" + " | ".join("&".join(f"{s}={v}" for s, v in c.items()) for c in yes) + ")"


ALIASES = {"cond": ("RS1", "cond"), "uncond": ("RS1", "uncond"),
           "Ds": ("RS2", "Ds"), "iffo": ("RS3o", "iff"), "iffi": ("RS3i", "iff"),
           "result": ("RS3c", "result"), "rel": ("RS4", "rel"),
           "trigger": ("RS11", "trigger"), "bound": ("RS9", "bound"),
           "intent": ("RS12strive", "intent")}


def same_set(key, result):
    if "undecided" in result:
        return False
    if "value" in result:
        return key == result["value"]
    if "parts" in result:
        return isinstance(key, dict) and set(key) == set(result["parts"]) and all(
            same_set(key[name], part) for name, part in result["parts"].items())
    if key in ("ALL", "NONE"):
        return all(row["holds"] == (key == "ALL") for row in result["choices"])
    if not isinstance(key, str) or not key.startswith("SOME("):
        return False
    terms = [x.strip() for x in key[5:-1].replace("∨", "|").replace("∧", "&").split("|")]
    desired = []
    for term in terms:
        desired.append(dict(ALIASES[x.strip()] for x in term.split("&")))
    return all(row["holds"] == any(all(row["choice"].get(s, BASE[s]) == v for s, v in d.items())
                                   for d in desired) for row in result["choices"])


def compare(items):
    key = json.loads((HERE / "answer-key.json").read_text())["items"]
    return [{"id": k["id"], "key": k["key"], "ve": verdict(items[k["id"]]),
             "agree": same_set(k["key"], items[k["id"]]),
             "classification": "agree" if same_set(k["key"], items[k["id"]]) else
                (items[k["id"]].get("undecided", "unclassified disagreement"))}
            for k in key]


def run():
    key = json.loads((HERE / "answer-key.json").read_text())["items"]
    items = {k["id"]: answer({name: k[name] for name in ("id", "case", "item")}) for k in key}
    return {"items": items, "comparison": compare(items)}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    result = run()
    rendered = json.dumps(result, indent=1, sort_keys=True) + "\n"
    if args.check:
        if RESULTS.read_text() != rendered:
            raise SystemExit("results.json is out of date")
    else:
        RESULTS.write_text(rendered)
    print(sum(r["agree"] for r in result["comparison"]), "/", len(result["comparison"]))


if __name__ == "__main__":
    main()
