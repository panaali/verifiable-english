"""Answer the frozen RSP questions with the translated VE documents.

The key is read only by compare().  A result records the route and the selected
rule or certificate; an unsupported question remains UNDECIDED with its cause.
"""
from __future__ import annotations

import argparse
from collections import Counter
import itertools
import json
import copy
import re
import sys
import time
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
THRESHOLDS = {block.id.split("-")[1].upper(): formula.term.name
              for block, formulas in T.facts() if block.id.startswith("threshold-") for formula in formulas}
CASES = {c["id"]: c for c in json.loads((HERE / "cases.json").read_text())["cases"]}
SETS = T.READING_SETS
BASE = {name: values[0] for name, values in SETS.items()}
MUTANT = None
WITHOUT_NARROWING = None
PROVER_CALLS = 0
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
    if WITHOUT_NARROWING == "N1":
        rules = [r for r in rules if not commitment_under_n1(r["name"])]
    if WITHOUT_NARROWING == "N3":
        rules = [r for r in rules if r["name"] != "f15-financial-interest"]
    if MUTANT == "m3":
        rules = [r for r in rules if r["name"] != "f26-need-not-delay"]
        if include is None or "f26-need-not-delay" in include:
            from ve.norm_english import parse_english
            text = ("Rule 1. Every situation must delay AI development as well as deployment, "
                    "if all of the following hold: (a) that situation is classified as "
                    "\"competitor_better_mitigation\"; (b) both that situation is classified as "
                    "\"clear_evidence\" and that situation is classified as \"delay_needed\".")
            added = parse_english(T.environment(), text).rules[0].to_dict()["norm"]
            added["name"] = "m3-f26-delay"
            rules.append(added)
    included = {r["name"] for r in rules}
    for rule in rules:
        rule["over"] = [n for n in ({} if MUTANT == "m1" else T.PRECEDENCE).get(rule["name"], ()) if n in included]
    return SoftNormDocument(SoftEnvironment(V.environment(default)), [{"norm": r} for r in rules])


@lru_cache(maxsize=None)
def commitment_under_n1(name):
    """The strict rules backed by a source commitment, excluding hedges and recommendations."""
    block = next(b for b in T.rule_blocks() if b.id == name)
    source = block.source.lower()
    norm = json.loads(T.parsed_rule(name))
    return (norm.get("mode", "strict") == "strict" and
            (bool(re.search(r"\b(will|commit|must|required|requires)\b", source)) or
             block.source.startswith("F1 to F4,")) and
            "will not necessarily" not in source and "should" not in source)


def atoms(case):
    found = set(listed_facts())
    found.update(("crossed", "s", THRESHOLDS[t]) for t in case["thresholds"])
    found.update((name, "s") for name in SITUATIONS.get(case["id"], ()))
    for term, value in case["findings"].items():
        if value and term in OT:
            found.add((OT[term], "s"))
    if "T4" in case["thresholds"]:
        found.add(("highly_capable", "s"))  # a model witness of the stated 3.6 definition
    if case["findings"].get("OT5"):
        found.add(("crossed", "s", THRESHOLDS["T4"]))
    found.update((name, "s") for name in case.get("extra", ()))
    return found


@lru_cache(maxsize=None)
def listed_facts():
    """The four threshold constants are facts.d1.ve premises, not a copied table."""
    out = []
    for block, formulas in T.facts():
        if block.id.startswith("threshold-"):
            for formula in formulas:
                if type(formula) is not A.Unary or type(formula.term) is not A.Const:
                    raise AssertionError("threshold fact is not a ground unary premise")
                out.append((formula.predicate, formula.term.name))
    return tuple(out)


def model(doc, case):
    env = doc.elaborated.base_environment()
    key = (env.environment_id, frozenset(atoms(case)))
    if key in _MODELS:
        return _MODELS[key]
    relations = {p: [] for p in env.predicates}
    for atom in atoms(case):
        if atom[0] in relations:
            relations[atom[0]].append(list(atom[1:]))
    _MODELS[key] = FiniteModel.from_dict(env, {"complete": True,
        "domains": {"situation": ["s"], "threshold": list(V.THRESHOLDS)},
        "constants": {c: c for c in env.constants},
        "relations": {p: sorted(v) for p, v in relations.items()}})
    return _MODELS[key]


_MODELS = {}
_PREMISES_CHECKED = set()


def check_premises(doc, case, choice):
    from ve.evaluate import evaluate
    key = (frozenset(atoms(case)), tuple((s, choice[s]) for s in ("RS3o", "RS3i", "RS3c")))
    if key in _PREMISES_CHECKED:
        return
    env = doc.elaborated.base_environment()
    witness = model(doc, case)
    for block, formulas in T.facts():
        if applies(block, choice):
            for formula in formulas:
                result = evaluate(env, formula, witness, trace=False)
                if result.value is not True:
                    raise AssertionError(f"case {case['id']} does not satisfy premise {block.id}: {result.status}")
    _PREMISES_CHECKED.add(key)


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


def completed(doc, case, predicate, values):
    from ve.evaluate import _Evaluator
    env = doc.elaborated.base_environment()
    formula = doc.elaborated.outcome(predicate, base=True)
    sorts = V.environment()["vocabulary"]["predicates"][predicate]["arguments"]
    A._Checker(env).formula(formula, tuple(reversed(sorts)))
    return _Evaluator(env, model(doc, case), 1_000_000, trace=False).formula(
        formula, tuple(zip(reversed(sorts), reversed(values))))[0]


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
        check_premises(deny, case, choice)
        left = selected(deny, case, predicate, sign, values)
        right = selected(allow, case, predicate, sign, values)
        if requirement and V.REGULATED[predicate]["regulated"]["role"] != "obligation":
            left = right = []
        outcome_values = values or (("s",) if len(V.environment()["vocabulary"]["predicates"][predicate]["arguments"]) == 1 else None)
        rows.append({"choice": assignment, "holds": bool(left and right),
                     "rules": sorted(set(left) & set(right)),
                     "default_sensitive": (completed(deny, case, predicate, outcome_values) !=
                                           completed(allow, case, predicate, outcome_values))
                     if outcome_values and predicate != "in_scope" else None})
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
    if id_ == "D4" and MUTANT == "m6":
        env = stage0.date_environment(("start_day", "limit_day"))
        facts = [stage0._q(["date_on", stage0._day("start_day"), ["date", "2026-08-03"]]),
                 stage0._q(["shift_days", stage0._day("limit_day"), stage0._day("start_day"), "60"])]
        later = stage0._proved(env, facts, stage0._q(["date_before", ["date", "2026-09-02"],
                                                      stage0._day("limit_day")]))
        if later:
            return constant(False, "D3 ve-units@1 quantity certificate replay", "m6: 60-day deadline is later")
        return {"route": "D3 ve-units@1", "undecided": "resource limit: no certificate for changed deadline"}
    certificate = dates()["certificates"].get(id_)
    if certificate is True:
        return constant(True, "D3 ve-units@1 quantity certificate replay", id_)
    if certificate is False:
        return {"route": "D3 ve-units@1", "undecided": "resource limit: no replayed quantity certificate"}
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
def opposite_sign_pairs():
    """The only rule pairs that can oppose one another on one regulated act."""
    rules = [json.loads(T.parsed_rule(b.id)) for b in T.rule_blocks()]
    return tuple((left["name"], right["name"]) for left, right in itertools.combinations(rules, 2)
                 if left["predicate"] == right["predicate"] and left["sign"] != right["sign"])


def conflict(id_):
    context = MUTANT if MUTANT in ("m1", "m3") else WITHOUT_NARROWING if WITHOUT_NARROWING == "N1" else None
    return _conflict(id_, context)


@lru_cache(maxsize=None)
def _conflict(id_, context):
    cluster = CLUSTERS.get(id_)
    if id_ == "C-doc":
        # Only pairs that can select opposite signs on one regulated predicate
        # can witness a conflict.  Both witnesses are checked on the full D1.
        sets = ("RS4", "RS7")
    else:
        sets = tuple(sorted({s for b in T.rule_blocks() if b.id in cluster for s, _ in b.when}))
    rows = []
    for assignment in choices(sets):
        choice = {**BASE, **assignment}
        checks = []
        pairs = opposite_sign_pairs() if id_ == "C-doc" else (cluster,)
        for pair in pairs:
            target = next((name for name, members in CLUSTERS.items()
                           if len(members) == 2 and set(members) == set(pair)), id_)
            doc = document(tuple(sorted(choice.items())), "deny", pair)
            checked = check_conflict(doc.elaborated, model=model(doc, witness(target)), prove=True)
            checks.append(checked.status)
        rows.append({"choice": assignment, "holds": True if "CONFLICT" in checks else
                     False if all(status == "CONFLICT-FREE" for status in checks) else None,
                     "w1": checks, "rules": "all opposite-sign pairs" if id_ == "C-doc" else list(cluster)})
    result = {"route": "D1 norms@0 W1 check_conflict with a validated witness model",
              "cone": list(sets), "choices": rows}
    if any(row["holds"] is None for row in rows):
        result["undecided"] = "resource limit: W1 lacks a conflict-freedom certificate"
    return result


def t_case_formula(case):
    var = A.Var(0)
    nodes = []
    for term, value in case["findings"].items():
        if MUTANT == "m5" and case["id"] in ("T1", "T2") and term == "OT15":
            continue  # without the factor, competitive cost remains an open term
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
    global PROVER_CALLS
    env = T.base_environment()
    premises = tuple(f for block, formulas in T.facts() if applies(block, choice) for f in formulas)
    stated = premises + (t_case_formula(case),)
    goal = t_goal(negative)
    PROVER_CALLS += 1
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
    if MUTANT == "m5" and case["id"] in ("T1", "T2"):
        found.discard(("full_substitution_at_competitive_cost", "s"))
    if negative:
        # Counterexample to 'not met': crossing is possible without a complete
        # definition, or with scenario (2) unconstrained by its inner converse.
        found.update({("crossed", "s", THRESHOLDS["T4"]), ("highly_capable", "s")})
        if MUTANT == "m5" and case["id"] == "T2" and choice["RS3o"] == "iff":
            found.add(("full_substitution_at_competitive_cost", "s"))
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
        if MUTANT == "m5":
            return constant(False, "D3 ve-units@1", "m5: no factor premise; competitive costs remains open")
        within = factor_within_five("4.5")
        if within is None:
            return {"route": "D3 ve-units@1", "undecided": "resource limit: factor proof and counterproof absent"}
        return constant(within, "D3 ve-units@1 quantity certificate replay",
                        "4.5 <= 5.0 under the policy's stated factor")
    if case["id"] in ("T1", "T2") and MUTANT != "m5":
        measured = factor_within_five(str(case["quantities"]["cost_factor"]))
        if measured is None:
            return {"route": "D3 ve-units@1", "undecided": "resource limit: factor proof and counterproof absent"}
        if measured != case["findings"]["OT15"]:
            raise AssertionError("OT15 case finding disagrees with VE's factor certificate")
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


@lru_cache(maxsize=None)
def factor_within_five(cost):
    from ve.environment import Environment
    from ve.profiles import LANGUAGE, SPEC_REVISION
    from ve.units import prove_quantity, check_quantity_certificate
    env = Environment({"language": LANGUAGE, "profiles": ["order@0", "relational-fol@0", "time@0"],
        "spec_revision": SPEC_REVISION, "unit_schema": "ve-units@1",
        "units": {"factor": {"scale": "10", "display": {"kind": "decimal", "label": "factor"}}},
        "vocabulary": {"sorts": {}, "predicates": {}, "constants": {}}})
    goal = {"format": "ve-quantity@1", "formula": ["le", ["decimal", "factor", cost],
                                                    ["decimal", "factor", "5.0"]]}
    proof = prove_quantity(env, [], goal)
    if proof is not None and check_quantity_certificate(env, [], goal, proof):
        return True
    opposite = {"format": "ve-quantity@1", "formula": ["lt", ["decimal", "factor", "5.0"],
                                                        ["decimal", "factor", cost]]}
    proof = prove_quantity(env, [], opposite)
    if proof is not None and check_quantity_certificate(env, [], opposite, proof):
        return False
    return None


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
    if id_ in ("G1", "G3"):
        return gap_probe(id_)
    if id_ in ("G5", "G6"):
        feature = {"G5": "ET: no reviewer nonresponse consequence in D1",
                   "G6": "SC: no priority between the review and approval duties"}[id_]
        return {"route": "D1", "undecided": f"translation limit ({feature})"}
    if id_ == "G4":
        return {"route": "D3 ve-units@1", "undecided": "VE limit (ET): RS11 at/trigger deadline is not in D3"}
    return {"route": "D1", "undecided": "unmapped gap question"}


def gap_probe(id_):
    """Ask VE about the two absent acts using an extension of D1's vocabulary.

    G1 names proceeding, which D1 has no predicate for; G3 names a cyber
    threshold outside the table.  The extension supplies only a query slot;
    the source translation contributes no rule for it.  m2/m4 add the invented
    rule/row to the same probe and must change exactly this result.
    """
    from ve.norm_english import parse_english
    raw = copy.deepcopy(V.environment())
    if id_ == "G1":
        raw["vocabulary"]["predicates"].pop("website_version")
        raw["vocabulary"]["predicates"]["proceed"] = {
            "arguments": ["situation"], "description": "development or deployment proceeds",
            "regulated": {"role": "permission", "default": "allow", "act": "{0} proceed"}}
        raw["vocabulary"]["predicates"]["plans_missing"] = {
            "arguments": ["situation"], "description": "the row's plans are not in place"}
        values = [({}, None)]
    else:
        raw["vocabulary"]["constants"]["cyber_capability"] = {
            "sort": "threshold", "description": "the hypothetical cyber threshold named by G3"}
        values = [(c, None) for c in choices(("RS1",))]
    rows = []
    audit_rules, audit_thresholds = set(), set()
    for assignment, _ in values:
        choice = {**BASE, **assignment}
        rules = [json.loads(T.parsed_rule(b.id)) for b in T.rule_blocks()
                 if applies(b, choice) and b.id != "f23-website"]
        if id_ == "G1" and (MUTANT == "m2" or WITHOUT_NARROWING == "N2"):
            text = ("Rule 1. Every situation must not proceed, if both that situation has crossed "
                    "\"novel_chem_bio_weapons\" and that situation is classified as \"plans_missing\".")
            data = parse_english(SoftEnvironment(raw), text).rules[0].to_dict()["norm"]
            data["name"] = "m2-invented-stop" if MUTANT == "m2" else "without-n2-v2-stop"
            rules.append(data)
        audit_rules.update(r["name"] for r in rules if r["name"] not in {b.id for b in T.rule_blocks()})
        doc = SoftNormDocument(SoftEnvironment(raw), [{"norm": r} for r in rules])
        env = doc.elaborated.base_environment()
        relations = {p: [] for p in env.predicates}
        for predicate, threshold in listed_facts():
            relations[predicate].append([threshold])
        if id_ == "G1":
            relations["crossed"].append(["s", THRESHOLDS["T2"]])
            relations["plans_missing"].append(["s"])
        else:
            relations["crossed"].append(["s", "cyber_capability"])
            if MUTANT == "m4":
                relations["listed"].append(["cyber_capability"])
                audit_thresholds.update(threshold for (threshold,) in relations["listed"]
                                        if threshold not in V.THRESHOLDS)
        m = FiniteModel.from_dict(env, {"complete": True,
            "domains": {"situation": ["s"], "threshold": list(raw["vocabulary"]["constants"])},
            "constants": {c: c for c in env.constants},
            "relations": {p: sorted(v) for p, v in relations.items()}})
        if id_ == "G1":
            selected_rules = doc.elaborated.selected_rules("proceed", m, ("s",))
        else:
            selected_rules = doc.elaborated.selected_rules("plans_in_place", m, ("s", "cyber_capability"))
        rows.append({"choice": assignment, "holds": not bool(selected_rules),
                     "rules": [r.name for r in selected_rules]})
    return {"route": "D1 soft-norms@0 selected_rules on a query-only vocabulary extension",
            "cone": ["RS1"] if id_ == "G3" else [], "choices": rows,
            "audit_input": {"rules": sorted(audit_rules), "thresholds": sorted(audit_thresholds)}}


def never_answer(id_):
    if id_ == "N5" and WITHOUT_NARROWING == "N2":
        result = gap_probe("G1")
        result["route"] += "; v2.0 changelog read as a standing stop rule"
        return result
    if id_ == "N1":
        result = silence(CASES["B-VOL"], ("assessed_in_report",))
    elif id_ == "N2":
        witness_case = {**CASES["K21"], "findings": {**CASES["K21"]["findings"], "OT7": True}}
        result = silence(witness_case, ("delay",))
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
        if id_ in ("K12a", "K12b"):
            return {"route": "D1", "undecided": "translation limit (SC): Board consultation and LTBT approval share one act"}
        if id_ in ("K15a", "K17"):
            return {"route": "D1/D3", "undecided": "VE limit (ET): prompt notice or effective-date order is not encoded"}
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
    if not result["choices"] or any(row["holds"] is None for row in result["choices"]):
        return "UNDECIDED"
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
    if not result["choices"] or any(row["holds"] is None for row in result["choices"]):
        return False
    if key in ("ALL", "NONE"):
        return all(row["holds"] == (key == "ALL") for row in result["choices"])
    if not isinstance(key, str) or not key.startswith("SOME("):
        return False
    terms = [x.strip() for x in key[5:-1].replace("∨", "|").replace("∧", "&").split("|")]
    desired = []
    for term in terms:
        desired.append(dict(ALIASES[x.strip()] for x in term.split("&")))
    if any(not set(d) <= set(result["cone"]) for d in desired):
        return False
    return all(row["holds"] == any(all(row["choice"].get(s, BASE[s]) == v for s, v in d.items())
                                   for d in desired) for row in result["choices"])


def compare(items):
    key = json.loads((HERE / "answer-key.json").read_text())["items"]
    rows = []
    for entry in key:
        result = items[entry["id"]]
        agrees = same_set(entry["key"], result)
        reason = result.get("undecided")
        status = "agree" if agrees else ("UNDECIDED-faithful" if reason else "disagree")
        cause = None
        if reason:
            family = reason.split("(")[1].split(")")[0].split(":")[0] if "(" in reason else "unspecified"
            cause = {"kind": "translation limit" if reason.startswith("translation limit") else
                     "resource limit" if reason.startswith("resource limit") else "VE limit",
                     "feature_family": family, "reason": reason}
        elif not agrees:
            cause = {"kind": "VE bug or key finding", "feature_family": "pending source audit",
                     "reason": "requires a minimal repro before classification"}
        rows.append({"id": entry["id"], "key": entry["key"], "ve": verdict(result),
                     "agree": agrees, "status": status, "cause": cause,
                     "route": result["route"]})
    return rows


def run():
    global PROVER_CALLS
    PROVER_CALLS = 0
    document.cache_clear()
    _MODELS.clear()
    _PREMISES_CHECKED.clear()
    key = json.loads((HERE / "answer-key.json").read_text())["items"]
    items = {k["id"]: answer({name: k[name] for name in ("id", "case", "item")}) for k in key}
    return {"items": items, "comparison": compare(items),
            "cost": {"documents_built": document.cache_info().currsize, "prover_calls": PROVER_CALLS}}


def without_narrowings(baseline):
    """Unscored §9 comparison, rerunning VE with each source narrowing removed alone."""
    global WITHOUT_NARROWING
    base = {row["id"]: row["ve"] for row in baseline["comparison"]}
    out = {}
    try:
        for name in ("N1", "N2", "N3"):
            WITHOUT_NARROWING = name
            variant = run()
            out[name] = {"changed": {row["id"]: {"with": base[row["id"]], "without": row["ve"]}
                                     for row in variant["comparison"] if row["ve"] != base[row["id"]]},
                         "unscored": True}
    finally:
        WITHOUT_NARROWING = None
        document.cache_clear()
    return out


EXPECTED_MUTANTS = {"m1": ["C2", "C-doc"], "m2": ["G1"],
                    "m3": ["C1", "C7", "C-doc", "N2"], "m4": ["G3"],
                    "m5": ["T1", "T2b", "T5"], "m6": ["D4"]}


def mutants(baseline):
    global MUTANT
    base = {row["id"]: row["ve"] for row in baseline["comparison"]}
    out = {}
    try:
        for name, expected in EXPECTED_MUTANTS.items():
            MUTANT = name
            document.cache_clear()
            mutated = run()
            changed = sorted(row["id"] for row in mutated["comparison"] if row["ve"] != base[row["id"]])
            audit = invention_audit_for(mutated)
            out[name] = {"changed": changed, "expected": sorted(expected),
                         "exact": changed == sorted(expected),
                         "invention_audit_flags": bool(audit["untraced"] or audit["thresholds_without_premise"])}
    finally:
        MUTANT = None
        document.cache_clear()
    return out


def invention_audit_for(result):
    import stage0
    inputs = [item["audit_input"] for item in result["items"].values() if "audit_input" in item]
    return stage0.invention_audit(
        {name for item in inputs for name in item["rules"]},
        {name for item in inputs for name in item["thresholds"]})


def metrics(result):
    import stage0
    coverage = json.loads((HERE / "coverage.json").read_text())
    rows = result["comparison"]
    by_family = {family: {"correct": sum(r["agree"] for r in rows if r["id"][0] == family),
                          "key": sum(r["id"][0] == family for r in rows),
                          "faithful_undecided": sum(r["id"][0] == family and r["status"] == "UNDECIDED-faithful"
                                                   for r in rows)} for family in "ABKTCGNSD"}
    all_choices = [choice for item in result["items"].values() for choice in item.get("choices", [])]
    return {
        "M1": by_family,
        "M2": {"reading_sets": len(SETS), "max_choices_per_item": max(len(i.get("choices", []))
                                                                     for i in result["items"].values()),
               "some_answers": sum(isinstance(r["ve"], str) and r["ve"].startswith("SOME(") for r in rows),
               "ve_readings": "P2 pending (RS1 has a no-rule reading)"},
        "M3": {"bytes_by_status": coverage["master_bytes_by_status"],
               "bytes_by_kind": coverage["bytes_by_kind"], "residual": coverage["residual"]},
        "M4": {"conditional_by_family": dict(Counter(r["id"][0] for r in rows if
                       isinstance(r["ve"], str) and r["ve"].startswith("SOME(")))},
        "M5": stage0.identifier_lint(), "M6": invention_audit_for(result),
        "M7": {"sensitive_choices": sum(r.get("default_sensitive") is True for r in all_choices),
               "insensitive_choices": sum(r.get("default_sensitive") is False for r in all_choices)},
        "M8": {"replayed_certificates": sum(r.get("reason") == "replayed certificate" for r in all_choices),
               "validated_countermodels": sum(r.get("reason") == "validated countermodel" for r in all_choices),
               "w1_conflict_witnesses": sum("CONFLICT" in r.get("w1", []) for r in all_choices),
               "unknown_items": [r["id"] for r in rows if r["status"] == "UNDECIDED-faithful"]},
        "M9": {"mutants": result["mutants"], "detected": sum(v["exact"] for v in result["mutants"].values())},
        "M10": {"units": len(json.loads((HERE / "spans.json").read_text())["units"]),
                "rules": len(T.rule_blocks()), "cases": len(CASES),
                "choices": len(all_choices), "documents_built": result["cost"]["documents_built"],
                "prover_calls": result["cost"]["prover_calls"],
                "wall_time": "printed by run.py; intentionally not pinned by --check"},
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    started = time.monotonic()
    result = run()
    result["mutants"] = mutants(result)
    result["metrics"] = metrics(result)
    result["without_narrowings"] = without_narrowings(result)
    rendered = json.dumps(result, indent=1, sort_keys=True) + "\n"
    if args.check:
        if RESULTS.read_text() != rendered:
            raise SystemExit("results.json is out of date")
    else:
        RESULTS.write_text(rendered)
    print(sum(r["agree"] for r in result["comparison"]), "/", len(result["comparison"]),
          f"({time.monotonic() - started:.1f} s)")


if __name__ == "__main__":
    main()
