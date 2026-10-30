"""Answer the frozen Preparedness questions with the translated VE documents.

The key is read only by compare().  A result records the route and the selected rules, certificate or witness;
an unsupported question stays UNDECIDED with its cause.  The pattern is usecases/anthropic-rsp/run.py, whose
verdict() and applies() are imported unchanged.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import itertools
import json
import re
import sys
import time
from collections import Counter
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pf_translation as T  # noqa: E402
import pf_vocabulary as V  # noqa: E402
from ve import ast as A  # noqa: E402
from ve.entailment import prove_entailment, check_entailment_certificate  # noqa: E402
from ve.model import FiniteModel  # noqa: E402
from ve.norms import check_conflict  # noqa: E402
from ve.softnorms import SoftEnvironment, SoftNormDocument  # noqa: E402


def _rsp_run():
    """usecases/anthropic-rsp/run.py under its own module name; its directory does not stay on sys.path."""
    name = "anthropic_rsp_run"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, HERE.parent / "anthropic-rsp" / "run.py")
    module = importlib.util.module_from_spec(spec)
    path = list(sys.path)
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path[:] = path
    sys.modules[name] = module
    return module


RSP = _rsp_run()
verdict, applies = RSP.verdict, RSP.applies

RESULTS = HERE / "results.json"
CASES = {c["id"]: c for c in json.loads((HERE / "cases.json").read_text())["cases"]}
SETS = T.READING_SETS
BASE = {name: values[0] for name, values in SETS.items()}
NARROWED = ("RS0",)  # N1: every RS0 statement is a commitment (PLAN 3.1)
MUTANT = None
WITHOUT_NARROWING = None
PROVER_CALLS = 0

LEVEL_IDS = {"BIO-H": "biological_and_chemical_high", "BIO-C": "biological_and_chemical_critical",
             "CYB-H": "cybersecurity_high", "CYB-C": "cybersecurity_critical",
             "AIS-H": "ai_self_improvement_high", "AIS-C": "ai_self_improvement_critical"}
# The case's proposal (cases.json "activities"). A large-scale internal deployment is an internal deployment.
ACTIVITY = {"DEV": ("further_development",), "INT": ("internal_deployment",),
            "LINT": ("internal_deployment", "large_scale_internal"), "EXT": ("external_deployment",)}
OT = {"OT1": "threshold_determined", "OT2": "sufficient_safeguards", "OT9": "likely_to_cross",
      "OT10": "forecast_critical", "OT11": "reasonable_evidence", "OT12": "adjustment_confirmed",
      "OT13": "major_deployment", "OT18": "rapid_risk", "OT20": "significant_increase",
      "OT21": "immediate_reaction_needed"}
# What each case's situation states beyond its findings (cases.json "situation"), as D1 base atoms.
SITUATIONS = {
    "K3": ("distilled_from_below_high",), "K4": ("distilled_from_below_high",),
    "K6": ("adjustment_made",), "K7": ("further_development",), "K8": ("further_development",),
    "K9": ("undermining_found",), "K10": ("sandbagging_found",), "K11": ("coverage_ambiguous",),
    "K13": ("fast_track_requested",), "K14": ("deeper_testing_warranted", "third_party_available"),
    "K15": ("research_category_review",), "K16": ("employee_request",),
    "K17": ("substantiated_noncompliance",), "K18": ("nuclear_found",), "K19": ("ara_found",),
    "K20": ("safeguards_report_compiled",), "G5": ("nuclear_found",), "G6": ("persuasion_risk",),
}
# Atoms a case's situation states as false ("not already implemented", "no highly sensitive information").
STATED_FALSE = {"K2": ("safeguards_already_assessed",), "K16": ("highly_sensitive",)}
# K9's model has High capability "in a Tracked Category" without naming it: every High level is tried.
SOME_HIGH_LEVEL = {"K9"}

ATOMS = {"SEC": ("security_controls", "security_practices", "development_security_controls"), "MIS": ("misuse_safeguards",),
         "ALN": ("alignment_safeguards",), "SUF": ("safeguards_before_deployment", "safeguards_during_development"),
         "HALT": ("halt_development",),
         "CAPREP": ("capabilities_report",), "SAFEREP": ("safeguards_report",), "MREP": ("misalignment_report",),
         "DISC": ("safeguards_disclosed",), "PUBRES": ("public_disclosure",),
         "CONTRIB": ("pandemic_policy_contribution", "cyberdefense_contribution")}
K_ITEMS = {"START_WORK_ON_SAFEGUARDS": ("safeguard_work",), "SAG_RECOMMENDS_SAFEGUARDS": ("safeguards_recommended",),
           "ADDITIONAL_SAFETY_MEASURES": ("additional_safety_measures",),
           "CAPABILITIES_REPORT": ("capabilities_report",),
           "VALIDATE_AND_REVIEW_SUFFICIENCY": ("validate_evidence", "review_sufficiency"),
           "KEEP_SAFEGUARDS_MORE_PROTECTIVE": ("more_protective",),
           "PUBLICLY_ACKNOWLEDGE_ADJUSTMENT": ("adjustment_acknowledged",),
           "SHARE_INFORMATION_TO_VALIDATE": ("validation_shared",),
           "SAFEGUARDS_DURING_DEVELOPMENT": ("safeguards_during_development",), "HALT": ("halt_development",),
           "ROBUST_SAFEGUARDS_CASE": ("robust_case",), "ELICITATION_OR_CONSERVATIVE_BOUND": ("sandbagging_bound",),
           "SAG_FINAL_DETERMINATION": ("coverage_decided",), "ANNUAL_REVIEW": ("annual_review",),
           "CHAIR_COORDINATES_WITH_LEADERSHIP": ("chair_coordination",),
           "THIRD_PARTY_EVALUATION": ("third_party_evaluation",),
           "SAG_RECEIVES_RESULTS": ("research_results_received",),
           "REQUEST_AND_RECEIVE_SUMMARY": ("summary_access",), "CORRECTIVE_ACTION": ("corrective_action",),
           "HEIGHTEN_SAFEGUARDS_WITH_US_GOVERNMENT": ("nuclear_safeguards",),
           "CONVERT_TO_TRACKED_CATEGORY": ("ara_tracking",),
           "RESIDUAL_RISK_ASSESSMENT": ("residual_risk_assessment",)}
ALL_OF = {"VALIDATE_AND_REVIEW_SUFFICIENCY"}  # "validating ... and reviewing ..." asks for both acts
# Table 1, F2, F3 and F4: the rules that attach to a capability threshold (G5, G9).
THRESHOLD_PREDICATES = ("security_controls", "security_practices", "development_security_controls", "misuse_safeguards", "alignment_safeguards",
                        "safeguards_before_deployment", "safeguards_during_development", "halt_development",
                        "pandemic_policy_contribution", "cyberdefense_contribution", "deployment_permitted")
SAFEGUARD_PREDICATES = THRESHOLD_PREDICATES + ("access_limited", "misalignment_risk_minimized")
# The Critical-specific rules (Table 1's Critical rows and 4.4): G2.
CRITICAL_PREDICATES = ("safeguards_during_development", "halt_development")

M2_PERMISSION = ("Rule 1. Every situation may be deployed, if all of the following hold: (a) all of the following "
                 "hold: (i) there is a level such that both that situation has reached that level and that level "
                 "is high; (ii) that situation is classified as \"external_deployment\"; (b) that situation is "
                 "classified as \"misuse_standard_met\".")
M3_ALIGNMENT = {"f1-alignment-cyb-strict": "must", "f1-alignment-cyb-default": "should"}


def vocabulary(default=None):
    """D1's vocabulary; with a default, every regulated act completes to it (PLAN 3.3: both defaults are run)."""
    raw = copy.deepcopy(V.environment())  # V.environment() shares its declarations with the module
    if default is not None:
        for entry in raw["vocabulary"]["predicates"].values():
            if "regulated" in entry:
                entry["regulated"]["default"] = default
    if MUTANT == "m2":
        raw["vocabulary"]["predicates"]["misuse_standard_met"] = V.base(
            ["situation"], "misuse safeguards meet the High standard at {0} (Appendix C.1, OT4)")
    return raw


def mutated_rule(block_id):
    """The rule a mutant changes, parsed by VE from its mutated text."""
    from ve.norm_english import parse_english
    modal = M3_ALIGNMENT[block_id]
    text = (f"Rule 1. Every situation {modal} have misalignment safeguards, "
            "if that situation has reached \"cybersecurity_high\".")
    data = parse_english(SoftEnvironment(vocabulary()), text).rules[0].to_dict()["norm"]
    data["name"] = block_id
    return data


def rule_data(block):
    if MUTANT == "m3" and block.id in M3_ALIGNMENT:
        return mutated_rule(block.id)
    return json.loads(T.parsed_rule(block.id))


def prediction_blocks():
    """Without N1 (RS0 = prediction), the RS0 statements carry no norm."""
    return set(T.RS0_STATEMENTS) | {b.id for b in T.rule_blocks() if ("RS0", "commitment") in b.when}


def precedence():
    table = dict(T.PRECEDENCE)
    if MUTANT == "m1":
        table.pop("f11-exception")
    if MUTANT == "m6" or WITHOUT_NARROWING == "N2":
        table.pop(T.N2_PRECEDENCE[0])
    return table


@lru_cache(maxsize=None)
def document(names, default, include=None):
    choice = dict(names)
    rules = [rule_data(b) for b in T.rule_blocks()
             if applies(b, choice) and (include is None or b.id in include)]
    if WITHOUT_NARROWING == "N1":
        rules = [r for r in rules if r["name"] not in prediction_blocks()]
    if MUTANT == "m2" and (include is None or "m2-invented-permission" in include):
        from ve.norm_english import parse_english
        data = parse_english(SoftEnvironment(vocabulary()), M2_PERMISSION).rules[0].to_dict()["norm"]
        data["name"] = "m2-invented-permission"
        rules.append(data)
    included = {r["name"] for r in rules}
    table = precedence()
    for rule in rules:
        rule["over"] = [n for n in table.get(rule["name"], ()) if n in included]
    return memoized(SoftNormDocument(SoftEnvironment(vocabulary(default)), [{"norm": r} for r in rules]))


def memoized(doc):
    """The elaborated document's base environment is rebuilt (and revalidated) on every call; it does not change
    for one document, so it is built once."""
    env = doc.elaborated.base_environment()
    doc.elaborated.base_environment = lambda: env
    return doc


@lru_cache(maxsize=None)
def table1_facts():
    """The ground Table 1 premises of facts.d1.ve (level grade and category), read from the parsed facts."""
    out = []
    for block, formulas in T.facts():
        for formula in formulas:
            if type(formula) is A.Unary and type(formula.term) is A.Const:
                out.append((formula.predicate, formula.term.name))
            elif type(formula) is A.Binary and type(formula.left) is A.Const and type(formula.right) is A.Const:
                out.append((formula.predicate, formula.left.name, formula.right.name))
    return tuple(out)


def high_of(level):
    """The High level of a Critical level's category, from the Table 1 premises."""
    facts = table1_facts()
    category = next(f[2] for f in facts if f[0] == "in_category" and f[1] == level)
    return next(f[1] for f in facts if f[0] == "in_category" and f[2] == category and ("high", f[1]) in facts)


def selected_facts(choice):
    return tuple((b, fs) for b, fs in T.facts() if applies(b, choice))


def atoms(case, choice, level=None):
    found = set(table1_facts())
    levels = [LEVEL_IDS[name] for name in case.get("levels", ())] + ([level] if level else [])
    for name in levels:
        found.add(("reached", "s", name))
        if choice.get("RS2") == "nest" and ("critical", name) in found:
            found.add(("reached", "s", high_of(name)))
    findings = case.get("findings", {})
    if findings.get("OT7", True):
        found.add(("covered", "s"))
    if not findings.get("OT6", False):
        found.add(("critical_standard_unspecified", "s"))
    for name in ACTIVITY.get(case.get("activity"), ()):
        found.add((name, "s"))
    for term, value in findings.items():
        if value and term in OT:
            found.add((OT[term], "s"))
    found.update((name, "s") for name in SITUATIONS.get(case["id"], ()))
    found.update((name, "s") for name in case.get("extra", ()))
    return frozenset(found)


_MODELS = {}
_PREMISES = set()


def model(doc, found):
    env = doc.elaborated.base_environment()
    key = (env.environment_id, found)
    if key not in _MODELS:
        relations = {p: [] for p in env.predicates}
        for atom in found:
            if atom[0] in relations:
                relations[atom[0]].append(list(atom[1:]))
        _MODELS[key] = FiniteModel.from_dict(env, {"complete": True,
            "domains": {"situation": ["s"], "level": list(V.LEVELS), "category": sorted({c for c, _ in V.LEVELS.values()}),
                        "proposal": ["p"], "requirement": ["r"], "capability": ["k"]},
            "constants": {c: c for c in env.constants},
            "relations": {p: sorted(v) for p, v in relations.items()}})
    return _MODELS[key]


def check_premises(doc, found, choice):
    """VE evaluates every premise the choice selects on the case model; a case that breaks one is an error."""
    from ve.evaluate import evaluate
    key = (found, choice.get("RS2"))
    if key in _PREMISES:
        return
    env = doc.elaborated.base_environment()
    witness = model(doc, found)
    for block, formulas in selected_facts(choice):
        for formula in formulas:
            result = evaluate(env, formula, witness, trace=False)
            if result.value is not True:
                raise AssertionError(f"case model does not satisfy premise {block.id}: {result.status}")
    _PREMISES.add(key)


def regulated(predicate):
    return vocabulary()["vocabulary"]["predicates"][predicate]["regulated"]


def selected(doc, found, predicate, sign):
    return sorted(r.name for r in doc.elaborated.selected_rules(predicate, model(doc, found), ("s",))
                  if r.sign == sign)


def completed(doc, found, predicate):
    from ve.evaluate import _Evaluator
    env = doc.elaborated.base_environment()
    formula = doc.elaborated.outcome(predicate, base=True)
    A._Checker(env).formula(formula, ("situation",))
    return _Evaluator(env, model(doc, found), 1_000_000, trace=False).formula(formula, (("situation", "s"),))[0]


@lru_cache(maxsize=None)
def cone(predicate):
    return tuple(sorted({s for b in T.rule_blocks() if json.loads(T.parsed_rule(b.id))["predicate"] == predicate
                         for s, _ in b.when if s not in NARROWED}))


def choices(sets):
    for values in itertools.product(*(SETS[s] for s in sets)):
        yield dict(zip(sets, values))


def negated(predicates):
    """Base atoms a rule on these predicates tests negatively (guard "not" or "unless")."""
    found = set()
    for b in T.rule_blocks():
        rule = json.loads(T.parsed_rule(b.id))
        if rule["predicate"] in predicates:
            text = json.dumps([rule["guard"], rule["unless"]])
            found |= set(re.findall(r'\["not", \["unary", "([a-z_]+)"', text))
            found |= {u[1] for u in rule["unless"] if u[0] == "unary"}
    return found


def unset_negations(case, predicates):
    """A negated open term the case leaves unset would be read as false by the complete case model."""
    stated = {OT[t] for t in case.get("findings", {}) if t in OT} | set(STATED_FALSE.get(case["id"], ()))
    stated |= set(SITUATIONS.get(case["id"], ())) | {"critical_standard_unspecified"}
    return sorted(negated(predicates) - stated)


def case_sets(case, predicates, extra=()):
    sets = set(extra)
    for predicate in predicates:
        sets |= set(cone(predicate))
    if any(LEVEL_IDS[name].endswith("_critical") for name in case.get("levels", ())):
        sets.add("RS2")
    return tuple(sorted(sets))


def query(case, predicates, sign=True, *, mode="any", role=None, level=None, extra_sets=()):
    """Per choice: does VE select a rule of this sign on the predicates, under both completion defaults?"""
    gaps = unset_negations(case, predicates)
    if gaps:
        return {"route": "D1", "undecided": f"translation limit (JT): the case leaves {', '.join(gaps)} unset"}
    sets = case_sets(case, predicates, extra_sets)
    rows = []
    for assignment in choices(sets):
        choice = {**BASE, **assignment}
        names = tuple(sorted(choice.items()))
        deny, allow = document(names, "deny"), document(names, "allow")
        found = atoms(case, choice, level)
        check_premises(deny, found, choice)
        per, other = {}, {}
        for predicate in predicates:
            other[predicate] = sorted(set(selected(deny, found, predicate, not sign)) |
                                      set(selected(allow, found, predicate, not sign)))
            if role and regulated(predicate)["role"] != role:
                per[predicate] = []
                continue
            left, right = selected(deny, found, predicate, sign), selected(allow, found, predicate, sign)
            per[predicate] = sorted(set(left) & set(right))
        hits = [bool(v) for v in per.values()]
        holds = all(hits) if mode == "all" else any(hits)
        rules = sorted({n for v in per.values() for n in v})
        modes = {json.loads(T.parsed_rule(n)).get("mode", "strict") if n in {b.id for b in T.rule_blocks()}
                 else "strict" for n in rules}
        sensitive = [p for p in predicates if completed(deny, found, p) != completed(allow, found, p)]
        rows.append({"choice": assignment, "holds": holds, "rules": rules,
                     "soft": holds and modes == {"default"}, "default_sensitive": bool(sensitive),
                     "sensitive_predicates": sensitive,
                     "silent_predicates": [p for p in predicates if not per[p] and not other[p]],
                     "other_sign_rules": sorted({n for v in other.values() for n in v})})
    return {"route": "D1 soft-norms@0 selected_rules, deny and allow completion", "cone": list(sets),
            "choices": rows}


def over_levels(case, predicates, **options):
    """K9: the verdict must be the same for each High level the unnamed Tracked Category could be."""
    highs = [name for name in V.LEVELS if ("high", name) in table1_facts()]
    results = [query(case, predicates, level=name, **options) for name in highs]
    if len({json.dumps(r.get("choices"), sort_keys=True) for r in results}) != 1:
        return {"route": "D1", "undecided": "translation limit (SC): the answer depends on the unnamed category"}
    result = results[0]
    result["route"] += "; the same for each High level"
    return result


def silence(case, predicates, *, baseline=None, route="silence"):
    """Holds when no rule on the predicates is selected (beyond the baseline case's, when one is given)."""
    sets = case_sets(case, predicates)
    rows = []
    for assignment in choices(sets):
        choice = {**BASE, **assignment}
        names = tuple(sorted(choice.items()))
        rules = set()
        base_rules = set()
        for default in ("deny", "allow"):
            doc = document(names, default)
            found = atoms(case, choice)
            check_premises(doc, found, choice)
            for predicate in predicates:
                for sign in (True, False):
                    rules |= set(selected(doc, found, predicate, sign))
                    if baseline is not None:
                        base_rules |= set(selected(doc, atoms(baseline, choice), predicate, sign))
        new = sorted(rules - base_rules)
        rows.append({"choice": assignment, "holds": not new, "rules": new})
    return {"route": f"D1 soft-norms@0 selected_rules, deny and allow completion; {route}",
            "cone": list(sets), "choices": rows}


def mentioning(difference):
    """The predicates of every rule whose guard tests an atom in which two case models differ: only these rules
    can be selected in one model and not the other."""
    names = {atom[0] for atom in difference}
    return tuple(sorted({r["predicate"] for r in (json.loads(T.parsed_rule(b.id)) for b in T.rule_blocks())
                         if names & set(re.findall(r'"([a-z_]+)"', json.dumps([r["guard"], r["unless"]])))}))


def only(case, predicates, allowed):
    """G9: the selected rules on the predicates are exactly the allowed ones, under every choice."""
    result = silence(case, predicates, route="only the C.3 access rule")
    for row in result["choices"]:
        row["holds"] = bool(row["rules"]) and set(row["rules"]) <= set(allowed)
    return result


def constant(value, route, reason):
    return {"route": route, "cone": [], "choices": [{"choice": {}, "holds": value, "reason": reason}]}


# --- C: W1 conflicts ------------------------------------------------------------------------------------------

CLUSTERS = {
    "C1": ("f11-within", "f11-exception", "f2-deploy", "f2-deploy-any", "f2-reminder", "f2-reminder-any"),
    "C2": ("f16-informed", "f16-without-noinput", "f16-without-nodelib"),
    "C3": ("f1-halt-strict", "f1-halt-default", "f3-develop", "f3-develop-inuse", "f3-reminder"),
    "C4": ("f6-rel", "f7-evaluations", "f7-report"),
    "C5": ("f1-security-strict", "f1-security-default", "f2-deploy", "f2-deploy-any"),
    "C6": ("f16-final", "f16-process", "f16-board-reverse"),
}
WITNESS = {
    "C1": ("covered", "external_deployment", "internal_deployment", "adjustment_confirmed",
           "adjustment_conditions", "adjustment_made"),
    "C2": ("leadership_decision", "decided_without_sag"),
    "C3": ("further_development", "critical_standard_unspecified"),
    "C4": ("covered", "distilled_from_below_high", "significant_increase"),
    "C5": ("covered", "external_deployment"),
    "C6": ("leadership_decision", "board_finds_necessary"),
    "m2": ("external_deployment", "misuse_standard_met"),
}
WITNESS_LEVELS = {"C1": ("BIO-H",), "C3": ("BIO-C",), "C5": ("AIS-H",), "m2": ("BIO-H",)}


def witness(names):
    extra = sorted({a for n in names for a in WITNESS[n]})
    return {"id": "W", "levels": sorted({lv for n in names for lv in WITNESS_LEVELS.get(n, ())}),
            "activity": None, "findings": {}, "extra": extra}


def w1(choice, include, case):
    """W1 on the rules with D1's declared completion defaults: a stress-test default on a permission dual would
    itself make an obligation conflict with its unstated permission."""
    names = tuple(sorted(choice.items()))
    doc = document(names, None, include)
    found = atoms(case, choice)
    check_premises(doc, found, choice)
    return check_conflict(doc.elaborated, model=model(doc, found), prove=True).status


@lru_cache(maxsize=None)
def opposite_pairs(context):
    """Rule pairs that can select opposite answers on one act: one predicate with both signs, or an obligation
    with its permission dual."""
    blocks = {b.id: b for b in T.rule_blocks()}
    rules = [rule_data(b) for b in blocks.values()]
    if MUTANT == "m2":
        rules.append({"name": "m2-invented-permission", "predicate": "deployment_permitted", "sign": True})
    duals = {name: decl["regulated"].get("permission") for name, decl in vocabulary()["vocabulary"]["predicates"].items()
             if "regulated" in decl}
    pairs = []
    for left, right in itertools.combinations(rules, 2):
        same = left["predicate"] == right["predicate"] and left["sign"] != right["sign"]
        dual = any(duals.get(a["predicate"]) == b["predicate"] and a["sign"] and not b["sign"]
                   for a, b in ((left, right), (right, left)))
        if same or dual:
            pairs.append((left["name"], right["name"]))
    return tuple(pairs)


def pair_sets(pair):
    blocks = {b.id: b for b in T.rule_blocks()}
    return tuple(sorted({s for n in pair if n in blocks for s, _ in blocks[n].when if s not in NARROWED}))


def conflict(id_):
    return _conflict(id_, MUTANT, WITHOUT_NARROWING)


@lru_cache(maxsize=None)
def _conflict(id_, mutant, narrowing):
    if id_ == "C-doc":
        return document_conflict()
    cluster = CLUSTERS[id_]
    sets = pair_sets(cluster)
    rows = []
    for assignment in choices(sets):
        choice = {**BASE, **assignment}
        status = w1(choice, cluster, witness((id_,)))
        rows.append({"choice": assignment, "holds": True if status == "CONFLICT" else
                     False if status == "CONFLICT-FREE" else None, "w1": [status], "rules": list(cluster)})
    result = {"route": "D1 norms@0 W1 check_conflict with a validated witness model", "cone": list(sets),
              "choices": rows}
    if any(row["holds"] is None for row in rows):
        result["undecided"] = "resource limit: W1 lacks a conflict-freedom certificate"
    return result


def document_conflict():
    """Every opposite pair, each over its own choices; the document conflicts under a choice when a pair does."""
    pairs = opposite_pairs(MUTANT)
    case = witness(tuple(WITNESS))
    per_pair = {}
    for pair in pairs:
        sets = pair_sets(pair)
        include = pair
        per_pair[pair] = (sets, {tuple(sorted(a.items())): w1({**BASE, **a}, include, case) for a in choices(sets)})
    sets = tuple(sorted({s for p_sets, _ in per_pair.values() for s in p_sets}))
    rows = []
    for assignment in choices(sets):
        statuses = [statuses[tuple(sorted((s, assignment[s]) for s in p_sets))]
                    for p_sets, statuses in per_pair.values()]
        conflicts = [" & ".join(p) for p, (p_sets, st) in per_pair.items()
                     if st[tuple(sorted((s, assignment[s]) for s in p_sets))] == "CONFLICT"]
        rows.append({"choice": assignment, "holds": True if conflicts else
                     False if all(s == "CONFLICT-FREE" for s in statuses) else None,
                     "w1": sorted(set(statuses)), "rules": conflicts})
    result = {"route": "D1 norms@0 W1 check_conflict per opposite-sign pair with a validated witness model",
              "cone": list(sets), "choices": rows, "pairs": [" & ".join(p) for p in pairs]}
    if MUTANT == "m2":
        result["audit_input"] = {"rules": ["m2-invented-permission"]}
    if any(row["holds"] is None for row in rows):
        result["undecided"] = "resource limit: W1 lacks a conflict-freedom certificate"
    return result


# --- N: never applies ------------------------------------------------------------------------------------------

N1_RULES = ("f1-halt-strict", "f1-halt-default", "f3-develop", "f3-develop-inuse", "f3-reminder")


def entailed(premises, goal):
    global PROVER_CALLS
    env = T.base_environment()
    PROVER_CALLS += 1
    proof = prove_entailment(env, premises, goal, max_steps=20000)
    if proof.status != "Found":
        return None
    if not check_entailment_certificate(env, premises, goal, proof.certificate).valid:
        raise AssertionError("N1 entailment certificate failed replay")
    return "replayed certificate"


def never_reached(choice):
    """N1: from the selected premises, no model OpenAI possessed at publication satisfies a HALT guard or F3's
    "reached" guard (the forecast branch is a separate rule and is not covered by the dated fact)."""
    env = T.base_environment()
    premises = tuple(f for _, fs in selected_facts(choice) for f in fs)
    reasons = []
    for block_id in N1_RULES:
        guard = json.loads(T.parsed_rule(block_id))["guard"]
        goal = A.formula_from_data(env, ["forall", "situation", ["implies", ["unary", "existing_at_publication",
                                                                             ["var", 0]], ["not", guard]]])
        reasons.append(entailed(premises, goal))
    return reasons


def never_answer(id_):
    if id_ == "N1":
        rows = []
        for assignment in choices(("RS2",)):
            reasons = never_reached({**BASE, **assignment})
            rows.append({"choice": assignment, "holds": all(reasons) if all(reasons) else None,
                         "reason": "replayed certificate" if all(reasons) else "UNKNOWN", "rules": list(N1_RULES)})
        result = {"route": "D1 relational-fol@0 entailment certificate per guard", "cone": ["RS2"], "choices": rows}
        if any(row["holds"] is None for row in rows):
            result["undecided"] = "resource limit: no entailment certificate"
        return result
    if id_ == "N2":
        return persuasion_probe()
    if id_ == "N3":
        return {"route": "D1", "deferred": "dead rules"}
    return {"route": "D1", "undecided": "VE limit (SC): D1 has no closure premise that the level sort holds "
                                        "exactly Table 1's six levels, so an unnamed seventh level is not excluded"}


def persuasion_probe():
    """N2: a query-only persuasion safeguard act, asked on the full D1 with every level reached and every
    activity; the translation contributes no rule for it (RSP G1's probe pattern)."""
    raw = vocabulary()
    raw["vocabulary"]["predicates"]["persuasion_safeguards"] = {
        "arguments": ["situation"], "description": "persuasion-specific safeguards (query only)",
        "regulated": {"role": "obligation", "default": "deny", "act": "{0} have persuasion safeguards"}}
    case = {"id": "N2", "levels": list(LEVEL_IDS), "activity": None, "findings": {},
            "extra": ("persuasion_risk", *sorted({a for v in ACTIVITY.values() for a in v}))}
    rows = []
    for assignment in choices(("RS15",)):
        choice = {**BASE, **assignment}
        rules = [{**rule_data(b), "name": b.id} for b in T.rule_blocks() if applies(b, choice)]
        doc = memoized(SoftNormDocument(SoftEnvironment(raw), [{"norm": r} for r in rules]))
        found = atoms(case, choice)
        check_premises(doc, found, choice)
        picked = [r.name for r in doc.elaborated.selected_rules("persuasion_safeguards", model(doc, found), ("s",))]
        rows.append({"choice": assignment, "holds": not picked, "rules": picked})
    return {"route": "D1 soft-norms@0 selected_rules on a query-only vocabulary extension", "cone": ["RS15"],
            "choices": rows}


def guard_atoms(node, negative=False, out=None):
    """The base predicates a guard names, split by whether they occur under a negation."""
    out = out if out is not None else {True: set(), False: set()}
    if isinstance(node, list) and node:
        if node[0] in ("unary", "binary"):
            out[negative].add(node[1])
        for child in node[1:]:
            guard_atoms(child, negative != (node[0] == "not") if node[0] == "not" else negative, out)
    return out


def witness_for(block):
    """A case model on which VE selects the rule: first its guard's positive atoms alone, then every atom but the
    negated ones; each with every level reached, under the rule's own reading."""
    rule = json.loads(T.parsed_rule(block.id))
    names = guard_atoms(rule["guard"])
    unless = guard_atoms(rule["unless"])
    blocked = names[True] | unless[False] | unless[True]
    situation = {n for n, d in vocabulary()["vocabulary"]["predicates"].items()
                 if "regulated" not in d and d["arguments"] == ["situation"]}
    capability = {n for n, d in vocabulary()["vocabulary"]["predicates"].items()
                  if "regulated" not in d and d["arguments"] == ["capability"]}
    choice = {**BASE, **dict(block.when)}
    names_ = tuple(sorted(choice.items()))
    sort = vocabulary()["vocabulary"]["predicates"][rule["predicate"]]["arguments"][0]
    arg = {"situation": "s", "capability": "k"}[sort]
    for positive in (names[False] - blocked, (situation | capability) - blocked):
        found = set(atoms({"id": block.id, "levels": list(LEVEL_IDS), "activity": None, "findings": {}}, choice))
        found = {a for a in found if a[0] not in situation or a[0] in positive}
        found |= {(n, "s") for n in positive & situation} | {(n, "k") for n in positive & capability}
        found = frozenset(found)
        ok = True
        for default in ("deny", "allow"):
            doc = document(names_, default)
            try:
                check_premises(doc, found, choice)
            except AssertionError:
                ok = False
                break
            picked = doc.elaborated.selected_rules(rule["predicate"], model(doc, found), (arg,))
            ok = ok and block.id in {r.name for r in picked}
        if ok:
            return sorted(found - set(table1_facts()))
    return None


def dead_rules(items):
    """N3: every F1 to F17 rule has a witness: a case model on which VE selected it, in a scored item of this
    run or in a model built from the rule's own guard."""
    seen = {name for item in items.values() for row in item.get("choices", []) for name in row.get("rules", [])
            if isinstance(row.get("rules"), list)}
    commitments = [b for b in T.rule_blocks() if re.match(r"f\d+-", b.id)]
    witnesses = {b.id: "a scored case" if b.id in seen else witness_for(b) for b in commitments}
    missing = sorted(n for n, w in witnesses.items() if w is None)
    result = {"route": "D1 soft-norms@0 selected_rules: a validated case model per rule", "cone": [],
              "choices": [{"choice": {}, "holds": False if not missing else None,
                           "reason": "every commitment selected on a validated case model"}],
              "witnesses": witnesses}
    if missing:
        result["undecided"] = f"translation limit (SC): no witness model for {', '.join(missing)}"
    return result


# --- S, T, D: D2 and D3 ------------------------------------------------------------------------------------------

# Footnote 1 gives counts in words; each lower bound is read two ways (the least count the plural admits: one or
# two of the unit), and an answer is scored only when both readings agree.
SEVERITY_BRIDGES = {"one": {"thousands": 1_000, "millions": 1_000_000, "hundreds of billions": 100_000_000_000},
                    "two": {"thousands": 2_000, "millions": 2_000_000, "hundreds of billions": 200_000_000_000}}


def harm_environment():
    from ve.profiles import LANGUAGE, SPEC_REVISION
    return {"language": LANGUAGE, "profiles": ["order@0", "relational-fol@0", "time@0"],
            "spec_revision": SPEC_REVISION, "unit_schema": "ve-units@1",
            "units": {"person": {"scale": "1", "display": {"kind": "decimal", "label": "people"}},
                      "usd": {"scale": "1", "display": {"kind": "decimal", "label": "USD"}}},
            "vocabulary": {"sorts": {}, "predicates": {}, "constants": {}}}


@lru_cache(maxsize=None)
def certified(env_name, formula):
    """True when VE proves the quantity formula and replays its certificate; None otherwise."""
    from ve.environment import Environment
    from ve.units import prove_quantity, check_quantity_certificate
    import stage0
    data = harm_environment() if env_name == "harm" else stage0.quantity_environment()
    env = Environment(data)
    goal = {"format": "ve-quantity@1", "formula": json.loads(formula)}
    proof = prove_quantity(env, [], goal)
    return True if proof is not None and check_quantity_certificate(env, [], goal, proof) else None


def decide(env_name, yes, no):
    if certified(env_name, json.dumps(yes)):
        return True
    if certified(env_name, json.dumps(no)):
        return False
    return None


def severe(deaths, damage, bounds):
    people = ["num", "person", str(bounds["millions" if MUTANT == "m5" else "thousands"])]
    usd = ["num", "usd", str(bounds["hundreds of billions"])]
    many = decide("harm", ["le", people, ["num", "person", str(deaths)]], ["lt", ["num", "person", str(deaths)], people])
    costly = decide("harm", ["le", usd, ["num", "usd", str(damage)]], ["lt", ["num", "usd", str(damage)], usd])
    if many or costly:
        return True
    return False if many is False and costly is False else None


def severity_answer(item):
    id_ = item["id"]
    if id_ in ("S6", "S7", "S8"):
        import stage0
        probe = stage0.risk_probe()
        if not probe["admitted"]:
            return {"route": "D2 risk@0", "undecided": "resource limit or risk-route refusal"}
        if id_ == "S6":
            order = stage0.risk_environment()["risk"]["severity"]["more_severe"]
            return constant(bool(order), "D2 risk@0 admitted severity order", "the admitted order is empty")
        if id_ == "S7":
            return constant(probe["bio_h_might"], "D2 risk@0 risk-decision might table", "Table 1 BIO-H might cell")
        return constant(probe["invented_leads"], "D2 risk@0 risk-decision leads table", "no Table 1 leads cell")
    rows = []
    for reading, bounds in SEVERITY_BRIDGES.items():
        if id_ == "S5":
            people = ["num", "person", str(bounds["millions" if MUTANT == "m5" else "thousands"])]
            holds = decide("harm", ["le", people, ["num", "person", str(bounds["millions"])]],
                           ["lt", ["num", "person", str(bounds["millions"])], people])
        else:
            q = item["quantities"]  # the item's one stated harm; the other quantity is none
            holds = severe(q.get("deaths", 0), q.get("economic_damage_usd", 0), bounds)
        rows.append({"choice": {"QT-bound": reading}, "holds": holds,
                     "reason": "replayed quantity certificate" if holds is not None else "UNKNOWN"})
    result = {"route": "D3 ve-units@1 quantity certificate replay under both lower-bound bridges",
              "cone": [], "choices": rows}
    if any(r["holds"] is None for r in rows):
        result["undecided"] = "resource limit: no quantity certificate"
    elif len({r["holds"] for r in rows}) > 1:
        result["undecided"] = "VE limit (QT): the answer depends on the lower bound of the count word"
    else:
        result["choices"] = [{"choice": {}, "holds": rows[0]["holds"], "reason": "replayed quantity certificate",
                              "bridges": rows}]
    return result


def ratio_answer(case):
    """T: 4.4's indicator "in 1/5th the wall-clock time": factor x current <= baseline, in days."""
    factor = "4" if MUTANT == "m4" else "5"
    current, baseline = 7 * case["quantities"]["weeks"], 7 * case["quantities"]["weeks_2024"]
    scaled = ["scale", "elapsed_day", factor, ["num", "elapsed_day", str(current)]]
    holds = decide("quantity", ["le", scaled, ["num", "elapsed_day", str(baseline)]],
                   ["lt", ["num", "elapsed_day", str(baseline)], scaled])
    if holds is None:
        return {"route": "D3 ve-units@1", "undecided": "resource limit: no quantity certificate"}
    return constant(holds, "D3 ve-units@1 quantity certificate replay", f"{factor} x {current} days vs {baseline} days")


def date_answer(item):
    id_ = item["id"]
    if id_ in ("D1", "D4"):
        start, end = item["dates"] if id_ == "D1" else (f"{year}-01-01" for year in item["years"])
        holds = decide("quantity", ["date_before", ["date", start], ["date", end]],
                       ["date_before", ["date", end], ["date", start]])
        if holds is None:
            return {"route": "D3 ve-units@1", "undecided": "resource limit: no quantity certificate"}
        return constant(holds, "D3 ve-units@1 quantity certificate replay",
                        "version date before retrieval" if id_ == "D1" else "Table 1 baseline years")
    start, end = item["dates"]
    set_id = {"D2": "RS10", "D3": "RS14"}[id_]
    rows = []
    for assignment in choices((set_id,)):
        if assignment[set_id] == "unstated":
            rows.append({"choice": assignment, "holds": False, "reason": "no start point: no deadline is stated"})
            continue
        holds = certified("quantity", json.dumps(["shift_days", ["date", end], ["date", start], "365"]))
        rows.append({"choice": assignment, "holds": bool(holds),
                     "reason": "replayed quantity certificate (a year is 365 days, O9)" if holds else "UNKNOWN"})
    if any(r["reason"] == "UNKNOWN" for r in rows):
        return {"route": "D3 ve-units@1", "undecided": "resource limit: no quantity certificate"}
    return {"route": "D3 ve-units@1 quantity certificate replay", "cone": [set_id], "choices": rows}


# --- dispatch and comparison ------------------------------------------------------------------------------------

def gap_answer(id_, case):
    if id_ == "G1":
        return silence(case, ("halt_development", "deployment_permitted"), route="no rule forbids development")
    if id_ == "G2":
        return silence(case, CRITICAL_PREDICATES, route="no Critical-specific rule")
    if id_ == "G3":
        return silence(case, ("alignment_safeguards",))
    if id_ == "G4":
        return silence(case, ("misuse_safeguards", "alignment_safeguards"))
    if id_ == "G5":
        return silence(case, THRESHOLD_PREDICATES, route="no threshold rule")
    if id_ == "G6":
        baseline = {"id": "G6-baseline", "levels": [], "activity": None, "findings": {}}
        return silence(case, mentioning(atoms(case, BASE) - atoms(baseline, BASE)), baseline=baseline,
                       route="no rule beyond those of a case without persuasion")
    if id_ == "G7":
        return {"route": "D1", "undecided": "translation limit (SC): footnote 5's indicator relation between "
                                            "biological evaluations and the category's capabilities is not in D1"}
    if id_ == "G8":
        return query(case, ATOMS["SUF"], role="obligation")
    if id_ == "G9":
        return only(case, SAFEGUARD_PREDICATES, ("c3-access-strict", "c3-access-default"))
    if id_ == "G10":
        return query(case, ("deployment_permitted",), sign=False, role="permission")
    return {"route": "D1", "undecided": "unmapped gap question"}


def answer(item):
    id_, kind = item["id"], item["item"]
    case = CASES.get(item["case"])
    if id_.startswith("A-") or id_.startswith("B-"):
        return query(case, ATOMS[kind], role="obligation")
    if id_.startswith("K"):
        verb, name = kind.split(":", 1)
        options = {"mode": "all" if name in ALL_OF else "any",
                   "role": "permission" if verb == "PERMITS" else "obligation"}
        if case["id"] in SOME_HIGH_LEVEL:
            return over_levels(case, K_ITEMS[name], **options)
        return query(case, K_ITEMS[name], **options)
    if id_.startswith("T"):
        return ratio_answer(case)
    if id_.startswith("C"):
        return conflict(id_)
    if id_.startswith("G"):
        return gap_answer(id_, case)
    if id_.startswith("N"):
        return never_answer(id_)
    if id_.startswith("S"):
        return severity_answer(item)
    if id_.startswith("D"):
        return date_answer(item)
    return {"route": "D1", "undecided": "unmapped question"}


ALIASES = {"nest": ("RS2", "nest"), "any": ("RS3", "any"), "inuse": ("RS18", "inuse"), "N": ("RS4", "N"),
           "unscoped": ("RS4s", "unscoped"), "coupled": ("RS16", "coupled"), "permission": ("RS13", "permission"),
           "explanation": ("RS15", "explanation"), "final": ("RS11", "final"), "bperm": ("RS17", "bperm"),
           "publication": ("RS10", "publication"), "appointment": ("RS14", "appointment"),
           "exception": ("RS5", "exception"), "req": ("RS6", "req"), "noinput": ("RS7", "noinput")}


def key_terms(key):
    """SOME(a & b | (c & d)) as a list of {set: value}; None for a cell that does not parse."""
    if not isinstance(key, str) or not key.startswith("SOME(") or not key.endswith(")") \
            or key.count("(") != key.count(")"):
        return None
    terms = []
    for term in key[5:-1].replace("∨", "|").replace("∧", "&").split("|"):
        words = [w.strip().strip("()").strip() for w in term.split("&")]
        if not all(w in ALIASES for w in words):
            return None
        terms.append(dict(ALIASES[w] for w in words))
    return terms


def same_set(key, result):
    if "undecided" in result or not result.get("choices") or any(r["holds"] is None for r in result["choices"]):
        return False
    if key in ("ALL", "NONE"):
        return all(row["holds"] == (key == "ALL") for row in result["choices"])
    desired = key_terms(key)
    if desired is None or any(not set(d) <= set(result["cone"]) for d in desired):
        return False
    return all(row["holds"] == any(all(row["choice"].get(s) == v for s, v in d.items()) for d in desired)
               for row in result["choices"])


# Every disagreement, classified after its source sentence was read (PLAN 12 lists them).
CAUSES = {}
TRANSCRIPTION = {"SOME(N": "SOME(N ∧ unscoped)"}


def classify(entry, result, agrees):
    reason = result.get("undecided")
    if agrees:
        return "agree", None
    if reason:
        family = reason.split("(")[1].split(")")[0].split(":")[0] if "(" in reason else "unspecified"
        kind = ("resource limit" if reason.startswith("resource limit") else
                "translation limit" if reason.startswith("translation limit") else "VE limit")
        return ("resource-limit" if kind == "resource limit" else "UNDECIDED-faithful",
                {"kind": kind, "feature_family": family, "reason": reason})
    if entry["key"] in TRANSCRIPTION:
        plan = TRANSCRIPTION[entry["key"]]
        return "disagree", {"kind": "key finding", "feature_family": "transcription",
                            "reason": f"answer-key.json holds the truncated cell {entry['key']!r}; PLAN 6.2 says "
                                      f"{plan}; VE's answer equals the PLAN cell: "
                                      f"{same_set(plan.replace('∧', '&'), result)}"}
    cause = CAUSES.get(entry["id"], {"kind": "VE bug or key finding", "feature_family": "pending source audit",
                                     "reason": "requires a minimal repro before classification"})
    return "disagree", cause


def compare(items):
    key = json.loads((HERE / "answer-key.json").read_text())["items"]
    rows = []
    for entry in key:
        result = items[entry["id"]]
        agrees = same_set(entry["key"], result)
        status, cause = classify(entry, result, agrees)
        row = {"id": entry["id"], "key": entry["key"], "ve": verdict(result), "agree": agrees, "status": status,
               "cause": cause, "route": result["route"]}
        if "soft" in entry and result.get("choices"):
            soft = [r for r in result["choices"] if r.get("soft")]
            row["soft"] = {"key": entry["soft"], "ve": sorted({"&".join(f"{s}={v}" for s, v in r["choice"].items())
                                                               for r in soft})}
        rows.append(row)
    return rows


def run():
    global PROVER_CALLS
    PROVER_CALLS = 0
    document.cache_clear()
    opposite_pairs.cache_clear()
    _conflict.cache_clear()
    _MODELS.clear()
    _PREMISES.clear()
    key = json.loads((HERE / "answer-key.json").read_text())["items"]
    items = {}
    for k in key:
        items[k["id"]] = answer({name: k[name] for name in ("id", "case", "item")} |
                                {name: k[name] for name in ("quantities", "dates", "years") if name in k})
    items["N3"] = dead_rules(items)
    return {"items": items, "comparison": compare(items),
            "cost": {"documents_built": document.cache_info().currsize, "prover_calls": PROVER_CALLS}}


def without_narrowings(baseline):
    """Unscored PLAN 9 comparison: VE rerun with each narrowing removed alone."""
    global WITHOUT_NARROWING
    base = {row["id"]: row["ve"] for row in baseline["comparison"]}
    out = {}
    try:
        for name in ("N1", "N2"):
            WITHOUT_NARROWING = name
            variant = run()
            out[name] = {"changed": {row["id"]: {"with": base[row["id"]], "without": row["ve"]}
                                     for row in variant["comparison"] if row["ve"] != base[row["id"]]},
                         "unscored": True}
    finally:
        WITHOUT_NARROWING = None
        document.cache_clear()
    return out


EXPECTED_MUTANTS = {"m1": ["C1", "C-doc"], "m2": ["C-doc"],
                    "m3": ["A-CYB-H-DEV/ALN", "A-CYB-H-INT/ALN", "A-CYB-H-EXT/ALN", "A-CYB-C-DEV/ALN",
                           "A-CYB-C-INT/ALN", "A-CYB-C-EXT/ALN", "G3"],
                    "m4": ["T2"], "m5": ["S1"], "m6": ["C2", "C-doc"]}


def invention_audit_for(result):
    """M6 on the rules a run actually built: a rule that is no rules.d1.ve block is untraced."""
    import stage0
    blocks = {b.id for b in T.rule_blocks()}
    built = {name for item in result["items"].values() for name in item.get("audit_input", {}).get("rules", ())}
    base = stage0.invention_audit()
    return {"untraced": sorted(base["untraced"] + [n for n in built if n not in blocks]),
            "choice_mismatches": base["choice_mismatches"], "thresholds_without_premise": base["thresholds_without_premise"]}


def mutants(baseline):
    global MUTANT
    base = {row["id"]: row["ve"] for row in baseline["comparison"]}
    out = {}
    try:
        for name, expected in EXPECTED_MUTANTS.items():
            MUTANT = name
            mutated = run()
            changed = sorted(row["id"] for row in mutated["comparison"] if row["ve"] != base[row["id"]])
            audit = invention_audit_for(mutated)
            out[name] = {"changed": changed, "expected": sorted(expected), "exact": changed == sorted(expected),
                         "changes": {row["id"]: {"from": base[row["id"]], "to": row["ve"]}
                                     for row in mutated["comparison"] if row["id"] in changed},
                         "invention_audit_flags": bool(audit["untraced"])}
    finally:
        MUTANT = None
        document.cache_clear()
    return out


FAMILIES = "ABKTCGNSD"


def metrics(result):
    import stage0
    coverage = json.loads((HERE / "coverage.json").read_text())
    rows = result["comparison"]
    by_family = {f: {"correct": sum(r["agree"] for r in rows if r["id"][0] == f),
                     "key": sum(r["id"][0] == f for r in rows),
                     "faithful_undecided": sum(r["id"][0] == f and r["status"] == "UNDECIDED-faithful" for r in rows),
                     "resource_limit": sum(r["id"][0] == f and r["status"] == "resource-limit" for r in rows),
                     "disagree": sum(r["id"][0] == f and r["status"] == "disagree" for r in rows)} for f in FAMILIES}
    all_choices = [c for item in result["items"].values() for c in item.get("choices", [])]
    return {
        "M1": by_family,
        "useful_answers": {"correct": sum(r["agree"] for r in rows), "key": len(rows),
                           "faithful_undecided": sum(r["status"] == "UNDECIDED-faithful" for r in rows),
                           "field": "comparison[].agree; comparison[].status == 'UNDECIDED-faithful' marks the rest"},
        "M2": {"reading_sets": len(SETS), "narrowed": list(NARROWED),
               "max_choices_per_item": max(len(i.get("choices", [])) for i in result["items"].values()),
               "some_answers": sum(isinstance(r["ve"], str) and r["ve"].startswith("SOME(") for r in rows),
               "ve_readings": "pending: every reading set stays open in pf.d1.ve.md; the harness answers per choice"},
        "M3": {"bytes_by_status": coverage["master_bytes_by_status"], "bytes_by_kind": coverage["bytes_by_kind"],
               "residual": coverage["residual"]},
        "M4": {"conditional_by_family": dict(Counter(r["id"][0] for r in rows
                                                     if isinstance(r["ve"], str) and r["ve"].startswith("SOME(")))},
        "M5": stage0.identifier_lint(), "M6": invention_audit_for(result),
        "M7": {"sensitive_choices": sum(r.get("default_sensitive") is True for r in all_choices),
               "insensitive_choices": sum(r.get("default_sensitive") is False for r in all_choices),
               "sensitive_exactly_where_silent": all(r["sensitive_predicates"] == r["silent_predicates"]
                                                     for r in all_choices if "sensitive_predicates" in r),
               "soft_rows": sum(bool(r.get("soft")) for r in all_choices),
               "soft_key_items": sum("soft" in r for r in rows),
               "soft_key_items_matched": sum("soft" in r and bool(r["soft"]["ve"]) for r in rows)},
        "M8": {"certificate_items": sorted(i for i, item in result["items"].items() if "certificate" in item["route"]
                                           and "undecided" not in item),
               "w1_conflict_witnesses": sum("CONFLICT" in r.get("w1", []) for r in all_choices),
               "w1_conflict_free": sum(r.get("w1") == ["CONFLICT-FREE"] for r in all_choices),
               "unknown_items": [r["id"] for r in rows if r["status"] in ("UNDECIDED-faithful", "resource-limit")]},
        "M9": {"mutants": result["mutants"], "detected": sum(v["exact"] for v in result["mutants"].values())},
        "M10": {"units": len(json.loads((HERE / "spans.json").read_text())["units"]), "rules": len(T.rule_blocks()),
                "cases": len(CASES), "choices": len(all_choices), "documents_built": result["cost"]["documents_built"],
                "prover_calls": result["cost"]["prover_calls"],
                "wall_time": "printed by run.py; intentionally not pinned by --check"},
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--base-only", action="store_true", help="print the scored comparison only (no mutants)")
    args = parser.parse_args(argv)
    started = time.monotonic()
    result = run()
    if args.base_only:
        for row in result["comparison"]:
            if not row["agree"]:
                print(row["id"], row["key"], row["ve"], row["status"], (row["cause"] or {}).get("reason", ""))
        print(sum(r["agree"] for r in result["comparison"]), "/", len(result["comparison"]),
              f"({time.monotonic() - started:.1f} s)")
        return 0
    result["mutants"] = mutants(result)
    result["metrics"] = metrics(result)
    result["without_narrowings"] = without_narrowings(result)
    rendered = json.dumps(result, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    if args.check:
        if RESULTS.read_text() != rendered:
            raise SystemExit("results.json is out of date")
    else:
        RESULTS.write_text(rendered)
    print(sum(r["agree"] for r in result["comparison"]), "/", len(result["comparison"]),
          f"({time.monotonic() - started:.1f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
