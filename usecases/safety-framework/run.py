"""Runs VE on every case of the safety-framework use case (PLAN sections 5, 9 and 10).

    python usecases/safety-framework/run.py            # compute, write results.json, print the comparison
    python usecases/safety-framework/run.py --check    # compute and fail if results.json would change

The harness never reads the answer key while it computes a result. `compare`
reads `answer-key.json` afterwards and lists every disagreement.

What VE does here, per case and per complete choice of the reading sets that
bear on an item (its cone):

1. The document of the choice is assembled from rules that VE parsed alone with
   its one-reading check (`translation.py`) and admitted by `SoftNormDocument`,
   which also builds the soft elaboration T' (a default rule gives way to a
   strict rule on the same act).
2. The case is a finite model over T's base vocabulary: the level tables and
   closure sentences of `facts.d1.ve` (closed world over the named levels),
   the case facts of `cases.json`, and the minimal decision findings the soft
   premises force (an exception is found only where a sufficient condition the
   text states holds). VE validates the model, Background included.
3. The premises are checked on the case: the model satisfies every premise, or
   VE's prover certifies that the premises and the case facts are inconsistent
   (the certificate is replayed). Neither is UNKNOWN.
4. An item is a selection question (`NormDocument.selected_rules`), a completed
   outcome under both defaults (`NormDocument.outcome`), a conflict check
   (`check_conflict` on a cluster's document: a witness from a generic search
   over situations, or tableau certificates of conflict-freedom), or an
   entailment with a replayed certificate (family N).

ALL / SOME(c) / NONE combine the per-choice answers. The SOME condition is the
set of choices, compared with the key's condition as a set.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
import sys
import time
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import translation as T  # noqa: E402
import vocabulary as V  # noqa: E402
from ve import ast as A  # noqa: E402
from ve.ast import _Decoder  # noqa: E402
from ve.entailment import check_entailment_certificate, prove_entailment  # noqa: E402
from ve.evaluate import evaluate  # noqa: E402
from ve.model import FiniteModel  # noqa: E402
from ve.norms import _instantiate, check_conflict  # noqa: E402

RESULTS = HERE / "results.json"
SETS = T.READING_SETS
BASE_CHOICE = {name: values[0] for name, values in SETS.items()}
ACTIVITIES = json.loads((HERE / "cases.json").read_text())["activities"]
CASES = {c["id"]: c for c in json.loads((HERE / "cases.json").read_text())["cases"]}
PROVER_STEPS = 20000

DM = ("harm_mitigated", "severe_harm_mitigated", "significant_harm_mitigated")
SEC = ("secured", "adequately_secured")
# Item kind -> (predicates, sign): "pos" means a rule requires, permits or affirms.
SELECTION_ITEMS = {
    "DM": (DM, True), "SEC": (SEC, True), "CCA": (("assessed",), True),
    "RRA": (("residual_assessed",), True), "SC": (("safety_case",), True), "PRA": (("periodic_assessed",), True),
    "RECSEC": (("applied",), True), "DISC": (("shared",), True), "PROXIMITY": (("proximity_assessed",), True),
    "FURTHER_CCA": (("further_assessed",), True), "SUBMISSION": (("case_submitted",), True),
    "YEARLY_REVIEW": (("yearly_review",), True), "ADD": (("safeguards_added",), True),
    "FREQUENT_REVIEW": (("frequent_review",), True), "ACCEPTABLE": (("acceptable",), True),
    "PERMITS": (("proceed",), True), "FORBIDS": (("proceed",), False),
}
SILENT_ITEMS = {"SEC": SEC, "GOV": ("proceed",), "PROXIMITY": ("proximity_assessed",),
                "DISC": ("shared",), "CCA": ("assessed",)}


# --- rules, cones and choices ---------------------------------------------------

@lru_cache(maxsize=None)
def rule_predicate(rule_id):
    return json.loads(T.parsed_rule(rule_id))["predicate"]


def cone(predicates):
    """The reading sets with a candidate rule on one of `predicates`."""
    sets = set()
    for block in T.rule_blocks():
        if rule_predicate(block.id) in predicates:
            sets.update(set_id for set_id, _ in block.when)
    return tuple(sorted(sets))


def choices(sets):
    for values in itertools.product(*(SETS[s] for s in sets)):
        yield tuple(zip(sets, values))


def full_choice(assignment):
    return {**BASE_CHOICE, **dict(assignment)}


_DOCS = {}


def document(choice, default="deny", variant=()):
    """The document of a choice; `variant` is a tuple of (kind, payload) edits (mutants, N2 off)."""
    drop, extra, precedence = set(), [], None
    for kind, payload in variant:
        if kind == "drop":
            drop.update(payload)
        elif kind == "add":
            rule_id, text, *when = payload
            if all(choice.get(k) == v for k, v in (when[0] if when else ())):
                extra.append((rule_id, text))
        elif kind == "precedence":
            precedence = payload
    included = tuple(sorted(b.id for b in T.rule_blocks() if b.id not in drop and T.applies(b, choice)))
    key = (included, default, tuple(extra), json.dumps(precedence, sort_keys=True))
    if key not in _DOCS:
        _DOCS[key] = T.document(choice, default=default, drop=drop, extra=tuple(extra), precedence=precedence)
    return _DOCS[key]


# --- cases as finite models -----------------------------------------------------------

def case_atoms(case, *, without=()):
    atoms = set()
    for level in case.get("levels", []):
        atoms.add(("reached", "p", level))
    for predicate in ACTIVITIES.get(case.get("activity") or "", []):
        atoms.add((predicate, "p"))
    for finding in case.get("findings", []):
        atoms.add(tuple(finding))
    return frozenset(a for a in atoms if a[0] not in without)


@lru_cache(maxsize=None)
def fact_atoms():
    atoms = set()
    for _, _, formulas in T.facts():
        for f in formulas:
            if type(f) is A.Unary:
                atoms.add((f.predicate, f.term.name))
            elif type(f) is A.Binary:
                atoms.add((f.predicate, f.left.name, f.right.name))
    return frozenset(atoms)


DOMAINS = {"proposal": ["p"], "level": list(V.LEVELS), "domain": list(V.DOMAINS),
           "measure": list(V.MEASURES), "threat": list(V.THREATS)}


def _model(env, atoms, domains=DOMAINS):
    relations = {p: [] for p in env.predicates}
    for atom in atoms:
        if atom[0] in relations:
            relations[atom[0]].append(list(atom[1:]))
    return FiniteModel.from_dict(env, {"complete": True, "domains": domains,
                                       "constants": {c: c for c in env.constants},
                                       "relations": {p: sorted(rows) for p, rows in relations.items()}})


_MODELS = {}


def case_model(doc, atoms):
    """The case over the document's base vocabulary E' (decision predicates included).

    A decision predicate holds exactly where a sufficient condition of its rule's
    exception holds: the decider finds no other exception (PLAN 3.3: no invented finding).
    """
    env = doc.elaborated.base_environment()
    key = (env.environment_id, atoms)
    if key in _MODELS:
        return _MODELS[key]
    all_atoms = set(fact_atoms() | atoms)
    plain = _model(T.base_environment(), frozenset(a for a in all_atoms if a[0] in T.base_environment().predicates))
    for rule in doc.rules:
        if rule.exception is None:
            continue
        name = "soft__excepted__" + rule.core.name.replace("-", "_")
        sorts = T.environment().predicates[rule.core.predicate].arguments
        for values in itertools.product(*(plain.domains[s] for s in sorts)):
            for wire in rule.exception["sufficient"]:
                condition = _Decoder().decode(wire)
                if holds_at(T.base_environment(), condition, plain, sorts, values):
                    all_atoms.add((name, *values))
    _MODELS[key] = _model(env, frozenset(all_atoms))
    return _MODELS[key]


def holds_at(env, formula, model, sorts, values):
    """The value of an open formula over the context `sorts` (in argument order) at `values`."""
    from ve.evaluate import _Evaluator
    A._Checker(env).formula(formula, tuple(reversed(sorts)))
    return _Evaluator(env, model, 1_000_000, trace=False).formula(
        formula, tuple(zip(reversed(sorts), reversed(values))))[0]


def holds(env, formula, model):
    result = evaluate(env, formula, model, trace=False)
    if result.value is None:
        raise SystemExit(f"evaluation {result.status}: {formula}")
    return result.value


@lru_cache(maxsize=None)
def premise_status(atoms):
    """`model` if the case model satisfies every premise; `inconsistent` with a
    replayed certificate if VE proves the premises and case facts contradictory."""
    env = T.base_environment()
    model = _model(env, frozenset(a for a in fact_atoms() | atoms if a[0] in env.predicates))
    premises = [f for _, _, formulas in T.facts() for f in formulas]
    failed = [i for i, f in enumerate(premises) if not holds(env, f, model)]
    if not failed:
        return ("model", None)
    refuted = refute(premises, [_case_formula(atoms)])
    return ("inconsistent" if refuted else "UNKNOWN", [str(premises[i]) for i in failed])


def predicates_of(formula, found=None):
    found = set() if found is None else found
    if type(formula) in (A.Unary, A.Binary):
        found.add(formula.predicate)
    for field in ("left", "right", "body"):
        child = getattr(formula, field, None)
        if child is not None and not isinstance(child, (A.Var, A.Const)):
            predicates_of(child, found)
    return found


def constants_of(formula, found=None):
    found = set() if found is None else found
    if type(formula) is A.Const:
        found.add(formula.name)
    for field in ("term", "left", "right", "body"):
        child = getattr(formula, field, None)
        if child is not None:
            constants_of(child, found)
    return found


PROVER_CALLS = [0]


def PREMISES():
    return [f for _, _, formulas in T.facts() for f in formulas]


def identifier_lint():
    """P7 / M5: no identifier packs a level, number or condition into its name.

    A constant may carry a digit only if it is a source label (a level or a
    security level). No predicate name contains a constant name, a digit, or a
    condition word. Rules per source commitment are counted."""
    env = T.environment()
    labels = set(V.LEVELS) | set(V.MEASURES)
    words = ("_if_", "_unless_", "_after_", "_before_", "_requires_", "_when_")
    violations = []
    for name in env.constants:
        if re.search(r"[0-9]", name) and name not in labels:
            violations.append(f"constant {name}")
    for name in env.predicates:
        if re.search(r"[0-9]", name) or any(w in f"_{name}_" for w in words) or any(
                c in name for c in env.constants if len(c) > 4):
            violations.append(f"predicate {name}")
    per_source = {}
    for block in T.rule_blocks():
        source = block.source.split(",")[0]
        per_source.setdefault(source, []).append(block.id)
    return {"violations": violations, "rules_per_source": per_source}


def invention_audit():
    """M6: every premise and rule is traced to a source span (its header), and every forced
    choice the translation makes is listed."""
    untraced = [b.id for b in T.read_blocks("facts.d1.ve") + T.rule_blocks() if not b.source.strip()]
    bridges = [b.id for b in T.read_blocks("facts.d1.ve") if "bridge" in b.source]
    return {"untraced": untraced, "bridges": bridges,
            "forced_choices": [
                "completion defaults: every regulated predicate is run under deny and under allow (M7)",
                "an unset open term is false in a case model (the decider made no such finding)",
                "a soft exception is found exactly where a sufficient condition the text states holds",
                "D3: \"a year\" from 2026-04-17 is 365 days (no 29 February in between; W6a has no year unit)",
                "D2: unexamined (action, harm) cells count as possible (risk@0 unexamined: possible)"]}


def refute(premises, stated, goal=None, env=None):
    """A replayed certificate that `premises + stated` entail `goal` (default: a contradiction).

    The prover is tried on growing premise sets: those sharing a predicate with
    `stated` and the goal, then one more hop. Fewer premises keep the search
    small; a certificate from a subset is a certificate from the whole set."""
    env = T.base_environment() if env is None else env
    goal = A.Bottom() if goal is None else goal
    symbols = set().union(*(predicates_of(f) for f in stated), predicates_of(goal))
    names = set().union(*(constants_of(f) for f in stated), constants_of(goal))
    chosen = []
    for _ in range(4):
        # A ground fact enters only if it names a constant of the question.
        chosen = [f for f in premises
                  if (predicates_of(f) & symbols
                      and (type(f) in (A.Forall, A.Implies) or not constants_of(f) or constants_of(f) & names))
                  or (not predicates_of(f) and constants_of(f) & names)]
        PROVER_CALLS[0] += 1
        proof = prove_entailment(env, tuple(chosen) + tuple(stated), goal, max_steps=PROVER_STEPS)
        if proof.status == "Found":
            if check_entailment_certificate(env, tuple(chosen) + tuple(stated), goal, proof.certificate).valid:
                return proof.certificate
            raise SystemExit("a certificate failed replay")
        symbols |= set().union(set(), *(predicates_of(f) for f in chosen))
    return None


def _case_formula(atoms):
    """The case facts as one sentence: there is a proposal p with every stated atom."""
    def term(name):
        return A.Var(0) if name == "p" else A.Const(name)
    body = A.Top()
    for atom in sorted(atoms):
        f = A.Unary(atom[0], term(atom[1])) if len(atom) == 2 else A.Binary(atom[0], term(atom[1]), term(atom[2]))
        body = f if type(body) is A.Top else A.And(body, f)
    return A.Exists("proposal", body)


def _atom_formula(atom):
    if len(atom) == 2:
        return A.Unary(atom[0], A.Const(atom[1]))
    return A.Binary(atom[0], A.Const(atom[1]), A.Const(atom[2]))


# --- selection ------------------------------------------------------------------------

def selections(doc, model, predicate):
    """{argument tuple: [(rule, sign)]} for every tuple with proposal p where some rule selects."""
    el = doc.elaborated
    if predicate not in el.order:
        return {}
    sorts = T.environment().predicates[predicate].arguments
    found = {}
    for values in itertools.product(*(model.domains[s] for s in sorts)):
        if values[0] != "p":
            continue
        rules = el.selected_rules(predicate, model, values)
        if rules:
            found[values] = [(r.name, r.sign) for r in rules]
    return found


def selected(doc, model, predicates, sign, values=None):
    rules = set()
    for predicate in predicates:
        for args, picks in selections(doc, model, predicate).items():
            if values is not None and tuple(args) != tuple(values):
                continue
            rules.update(name for name, s in picks if s == sign)
    return sorted(rules)


def completed(doc, model, predicate, values):
    el = doc.elaborated
    if predicate not in el.order:
        return doc.env.predicates[predicate].regulated.default == "allow"
    sorts = T.environment().predicates[predicate].arguments
    return holds_at(el.base_environment(), el.outcome(predicate, base=True), model, sorts, values)


# --- items ---------------------------------------------------------------------------------

def item_predicates(kind):
    if kind in SELECTION_ITEMS:
        return SELECTION_ITEMS[kind][0]
    if kind == "GOV":
        return ("proceed",)
    if kind.startswith("SILENT:"):
        part = kind.split(":", 1)[1]
        if part == "CCA+GOV":
            return ("assessed", "proceed")
        if part == "EVIDENCE":
            return tuple(sorted(T.environment().predicates.keys() & {rule_predicate(b.id) for b in T.rule_blocks()}))
        return SILENT_ITEMS[part]
    if kind == "CATCH_ALL":
        return ("acceptable",) + DM + SEC
    if kind == "FORBIDS+L0":
        return ("proceed",)
    if kind == "CHECKPOINT_MCCA":
        return ("change_assessed",)
    raise KeyError(kind)


def answer(kind, case, choice, *, default="deny", variant=(), detail=None, level=None):
    """The value of one item at one complete choice, with the rules that decide it."""
    doc = document(choice, default, variant)
    atoms = case_atoms(case)
    model = case_model(doc, atoms)
    if kind in SELECTION_ITEMS:
        predicates, sign = SELECTION_ITEMS[kind]
        values = ("p", level) if kind == "PROXIMITY" else None
        rules = selected(doc, model, predicates, sign, values)
        if detail is not None:
            detail["rules"] = rules
            if kind == "DM":
                detail["release"] = selected(doc, model, DM, False)
            if kind == "CCA":
                detail["release"] = selected(doc, model, ("assessed",), False)
        return bool(rules)
    if kind == "GOV":
        counter = case_model(doc, case_atoms(case, without=("governance_found_acceptable",)))
        rules = selected(doc, counter, ("proceed",), False)
        if detail is not None:
            detail["rules"] = rules
        return bool(rules)
    if kind.startswith("SILENT:") and not kind.startswith("SILENT:EVIDENCE") and kind != "SILENT:CCA+GOV":
        predicates = SILENT_ITEMS[kind.split(":", 1)[1]]
        rules = selected(doc, model, predicates, True) + selected(doc, model, predicates, False)
        if detail is not None:
            detail["rules"] = rules
        return not rules
    if kind.startswith("SILENT:EVIDENCE"):
        # One regulated predicate at a time (the item is the conjunction over predicates).
        predicates = (kind.split("@", 1)[1],) if "@" in kind else item_predicates(kind)
        plain = case_model(doc, case_atoms(case, without=("circumvention_evidence",)))
        same = all(selections(doc, model, p) == selections(doc, plain, p) for p in predicates)
        return same
    if kind == "CATCH_ALL":
        acceptable = selected(doc, model, ("acceptable",), True)
        safeguards = selected(doc, model, DM + SEC, True)
        if detail is not None:
            detail["rules"] = acceptable + safeguards
        return bool(acceptable) and not safeguards
    if kind == "CHECKPOINT_MCCA":
        # The act of F5 names "various checkpoints"; no regulated predicate has a
        # slot for a particular checkpoint, so no rule can require an assessment of one.
        slots = {s for d in T.environment().predicates.values() if d.regulated is not None for s in d.arguments}
        if detail is not None:
            detail["rules"] = selected(doc, model, ("change_assessed",), True)
            detail["regulated_argument_sorts"] = sorted(slots)
        return "checkpoint" in slots
    raise KeyError(kind)


def item_result(kind, case, *, level=None, variant=(), predicates=None):
    """{"cone": [...], "true": [assignments], "details": {...}} over the item's cone."""
    if kind == "SILENT:EVIDENCE":
        parts = [item_result(f"{kind}@{p}", case, variant=variant, predicates=(p,)) for p in item_predicates(kind)]
        return intersect_results(parts)
    sets = cone(predicates or item_predicates(kind))
    true, release, details = [], [], {}
    for assignment in choices(sets):
        choice = full_choice(assignment)
        detail = {}
        value = answer(kind, case, choice, variant=variant, detail=detail, level=level)
        label = ",".join(f"{s}={v}" for s, v in assignment) or "-"
        details[label] = {"holds": value, **detail}
        if value:
            true.append(dict(assignment))
        if detail.get("release"):
            release.append(dict(assignment))
    result = {"cone": list(sets), "true": true, "details": details}
    if kind in ("DM", "CCA"):
        result["release_true"] = release
    return result


# --- conditions ------------------------------------------------------------------------------

LITERAL = re.compile(r"(RS[0-9a-z]+)=([A-Za-z]+)")
ALIASES = {"G": "RS1=G", "S": "RS1=S", "U": "RS2=U", "P": "RS2=P", "Ds": "RS3=Ds", "F": "RS3=F",
           "M": "RS7=M", "E": "RS7=E", "R": "RS5=R", "D": "RS5=D", "rel": "RS8=rel", "scope": "RS8=scope"}


def condition_vars(text):
    expanded = re.sub(r"\b([A-Za-z]+)\b(?![=])", lambda m: ALIASES.get(m[1], m[1]), text)
    return expanded, sorted({m[1] for m in LITERAL.finditer(expanded)})


def condition_holds(expanded, assignment):
    python = LITERAL.sub(lambda m: repr(assignment.get(m[1]) == m[2]), expanded)
    python = python.replace("&", " and ").replace("|", " or ").replace("!", " not ")
    return eval(python, {"__builtins__": {}})  # noqa: S307 - our own key syntax, letters and operators only


def verdict_set(verdict, variables):
    """The assignments over `variables` that a key verdict describes."""
    space = [dict(zip(variables, values)) for values in itertools.product(*(SETS[v] for v in variables))]
    if verdict == "ALL":
        return {json.dumps(a, sort_keys=True) for a in space}
    if verdict == "NONE":
        return set()
    m = re.fullmatch(r"SOME\((.+)\)", verdict)
    expanded, _ = condition_vars(m[1])
    return {json.dumps(a, sort_keys=True) for a in space if condition_holds(expanded, a)}


def result_set(result, variables):
    space = [dict(zip(variables, values)) for values in itertools.product(*(SETS[v] for v in variables))]
    true = [t for t in result["true"]]
    return {json.dumps(a, sort_keys=True) for a in space
            if any(all(a[k] == v for k, v in t.items()) for t in true)}


def describe(result):
    """ALL, NONE or SOME(<choices>) for a result over its cone, in the key's vocabulary."""
    total = 1
    for s in result["cone"]:
        total *= len(SETS[s])
    if not result["true"]:
        return "NONE"
    if len(result["true"]) == total:
        return "ALL"
    return "SOME(" + minimal_condition(result) + ")"


def minimal_condition(result):
    """A short DNF over the cone that holds exactly at the result's true choices."""
    sets = result["cone"]
    true = {tuple(t[s] for s in sets) for t in result["true"]}
    space = list(itertools.product(*(SETS[s] for s in sets)))
    best = None
    literals = [(s, v) for s in sets for v in SETS[s]]
    for size in range(1, len(sets) + 1):
        terms = []
        for combo in itertools.combinations(literals, size):
            if len({s for s, _ in combo}) < size:
                continue
            covered = {x for x in space if all(x[sets.index(s)] == v for s, v in combo)}
            if covered <= true:
                terms.append((combo, covered))
        cover, remaining = [], set(true)
        for combo, covered in sorted(terms, key=lambda t: (-len(t[1]), t[0])):
            if covered & remaining:
                cover.append(combo)
                remaining -= covered
        if not remaining:
            best = cover
            break
    return " | ".join(" & ".join(f"{s}={v}" for s, v in term) for term in best)


# --- conflicts ---------------------------------------------------------------------------------

def witness_situations():
    """A generic search space: up to two named levels reached, under each activity, no findings."""
    levels = list(V.LEVELS)
    subsets = [()] + [(l,) for l in levels] + list(itertools.combinations(levels, 2))
    for subset in subsets:
        for activity in ("DEV", "INT", "HRI", "LRX", "EXT", "EXT-NONFRONTIER"):
            yield {"id": f"W:{'+'.join(subset) or 'none'}:{activity}", "levels": list(subset),
                   "activity": activity, "findings": []}


def cluster_conflict(rule_ids, choice, variant=()):
    """The conflict status of the sub-document of `rule_ids` at one choice.

    CONFLICT: a situation that satisfies every premise, on which VE's W1 check
    finds two rules of opposite sign selected (`check_conflict` with that model).
    CONFLICT-FREE: for every W1 conflict target, VE's prover certifies (replayed)
    that no situation satisfying the premises makes it true. The plain W1 check
    over all base structures, without the premises, is recorded beside it.
    """
    doc = document(choice, "deny", variant)
    keep = {r.core.name for r in doc.rules} & set(rule_ids)
    drop = tuple(sorted({r.core.name for r in doc.rules} - keep))
    sub = document(choice, "deny", variant + (("drop", drop),))
    if not sub.rules:
        return {"status": "CONFLICT-FREE", "rules": []}
    signs = {}
    for rule in sub.rules:
        signs.setdefault(rule.core.predicate, set()).add(rule.core.sign)
    # Only rules of opposite sign on one predicate can conflict (no dual pairs are declared).
    search = witness_situations() if any(len(v) == 2 for v in signs.values()) else ()
    for situation in search:
        atoms = case_atoms(situation)
        if premise_status(atoms)[0] != "model":
            continue
        model = case_model(sub, atoms)
        report = check_conflict(sub.elaborated, model=model)
        if report.status == "CONFLICT":
            return {"status": "CONFLICT", "witness": situation["id"], "situation": report.situation,
                    "rules": sorted(keep)}
    plain = check_conflict(sub.elaborated, prove=True).status
    env = sub.elaborated.base_environment()
    premises = tuple(f for _, _, formulas in T.facts() for f in formulas)
    for target, sorts, formula in sub.elaborated.conflict_targets():
        goal = formula
        for sort in reversed(sorts):
            goal = A.Exists(sort, goal)
        if refute(premises, [goal], env=env) is None:
            return {"status": "UNKNOWN", "rules": sorted(keep), "target": target, "w1_without_premises": plain}
    return {"status": "CONFLICT-FREE", "rules": sorted(keep), "w1_without_premises": plain}


def conflict_result(rule_ids, variant=()):
    predicates = {rule_predicate(r) for r in rule_ids if r in {b.id for b in T.rule_blocks()}}
    sets = cone(predicates)
    true, details = [], {}
    for assignment in choices(sets):
        outcome = cluster_conflict(rule_ids, full_choice(assignment), variant)
        details[",".join(f"{s}={v}" for s, v in assignment) or "-"] = outcome
        if outcome["status"] == "UNKNOWN":
            raise SystemExit(f"conflict check UNKNOWN for {rule_ids} at {assignment}: {outcome}")
        if outcome["status"] == "CONFLICT":
            true.append(dict(assignment))
    return {"cone": list(sets), "true": true, "details": details}


def rules_on(*predicates):
    return tuple(b.id for b in T.rule_blocks() if rule_predicate(b.id) in predicates)


CONFLICT_CLUSTERS = {
    "CONFLICT:f15:f16": ("f15-same", "f15-diff", "f16-ds"),
    "CONFLICT:f2:f3": ("f2", "f3"),
    "CONFLICT:f9:f10": ("f9-dm", "f9-rel", "f10-dm-same", "f10-dm-diff", "f10-rel-same", "f10-rel-diff"),
    "CONFLICT:f16:sec": ("f16-ds", "f9-sec", "f10-sec"),
    "CONFLICT:f8:f12f13": ("f8", "f12-p", "f12-u", "f13-p", "f13-u"),
}


def document_conflicts():
    """Per regulated predicate, the choices of its cone where its rules conflict."""
    by_predicate = {}
    for block in T.rule_blocks():
        by_predicate.setdefault(rule_predicate(block.id), []).append(block.id)
    return {p: conflict_result(tuple(ids)) for p, ids in sorted(by_predicate.items())}


def _total(result):
    total = 1
    for s in result["cone"]:
        total *= len(SETS[s])
    return total


def intersect_results(results):
    # A part that holds at every choice of its cone constrains nothing; its sets stay outside the cone.
    results = [r for r in results if len(r["true"]) != _total(r)]
    sets = sorted({s for r in results for s in r["cone"]})
    true = []
    for assignment in choices(tuple(sets)):
        a = dict(assignment)
        if all(any(all(a[k] == v for k, v in t.items()) for t in r["true"]) for r in results):
            true.append(a)
    return {"cone": sets, "true": true, "details": {}, "predicates_checked": len(results)}


def union_result(results):
    # A result with no true choice adds nothing to a union; its reading sets stay outside the cone.
    results = [r for r in results if r["true"]] or results[:1]
    sets = sorted({s for r in results for s in r["cone"]})
    true = []
    for assignment in choices(tuple(sets)):
        a = dict(assignment)
        if any(any(all(a[k] == v for k, v in t.items()) for t in r["true"]) for r in results):
            true.append(a)
    return {"cone": sets, "true": true}


# --- family N -----------------------------------------------------------------------------------

def family_n(evaluations):
    env = T.base_environment()
    premises = tuple(f for _, _, formulas in T.facts() for f in formulas)
    out = {}
    # N1: no TCL concerns cyber or harmful manipulation.
    goals = {}
    for domain in ("cyber", "harmful_manipulation"):
        goal = A.Not(A.Exists("level", A.And(A.Unary("tracked", A.Var(0)),
                                               A.Binary("concerns", A.Var(0), A.Const(domain)))))
        certificate = refute(premises, [], goal)
        goals[domain] = {"certificate_replayed": certificate is not None,
                         "certificate_sha256": hashlib.sha256(json.dumps(certificate, sort_keys=True)
                                                              .encode()).hexdigest() if certificate else None}
    out["N1"] = {"verdict": "ALL" if all(g["certificate_replayed"] for g in goals.values()) else "UNKNOWN",
                 "goals": goals}
    # N2: whether some security level is recommended for the CBRN TCL. Two checked models.
    goal = A.Exists("measure", A.Binary("recommends", A.Const("cbrn_uplift_tcl"), A.Var(0)))
    base = _model(env, frozenset(a for a in fact_atoms() if a[0] in env.predicates))
    other = _model(env, frozenset(a for a in fact_atoms() if a[0] in env.predicates)
                   | {("recommends", "cbrn_uplift_tcl", "security_level_2_plus")})
    models = {}
    for name, model in (("without", base), ("with", other)):
        models[name] = {"premises_hold": all(holds(env, f, model) for f in premises),
                        "goal": holds(env, goal, model)}
    certifiable = not (models["without"]["premises_hold"] and models["with"]["premises_hold"]
                       and models["without"]["goal"] != models["with"]["goal"])
    out["N2"] = {"verdict": "CERTIFIABLE" if certifiable else "NOT_CERTIFIABLE", "models": models}
    # N3: every rule has a witness: a situation satisfying the premises, at a choice that
    # includes the rule, where VE selects it.
    witnesses, dead = {}, []
    situations = list(CASES.values()) + list(witness_situations())
    for block in T.rule_blocks():
        choice = {**BASE_CHOICE, **dict(block.when)}
        doc = document(choice)
        predicate = rule_predicate(block.id)
        found = None
        for situation in situations:
            atoms = case_atoms(situation)
            if premise_status(atoms)[0] != "model":
                continue
            model = case_model(doc, atoms)
            if any(block.id in [name for name, _ in picks]
                   for picks in selections(doc, model, predicate).values()):
                found = situation["id"]
                break
        if found is None:
            dead.append(block.id)
        else:
            witnesses[block.id] = found
    out["N3"] = {"verdict": "NONE" if not dead else "SOME", "without_witness": dead, "witnesses": witnesses,
                 "rules": len(T.rule_blocks())}
    return out


# --- default sensitivity (M7) -----------------------------------------------------------------

def relevant_predicates(kind, case, choice):
    """The predicates an item asks about at this case: for DM and SEC, the bullet of the case's level."""
    levels = set(case.get("levels", []))
    if kind in ("DM", "SEC") and levels:
        level = next(iter(levels))
        tracked_ml = level == "stealth_and_situational_awareness_tcl"
        misuse = level in ("cbrn_uplift_tcl", "cbrn_uplift_level_1", "cyber_uplift_level_1",
                           "harmful_manipulation_level_1")
        if kind == "SEC":
            return ("adequately_secured",) if tracked_ml else ("secured",)
        if tracked_ml:
            return ("significant_harm_mitigated",)
        if misuse or choice["RS9"] == "same":
            return ("harm_mitigated",)
        return ("severe_harm_mitigated",)
    return item_predicates(kind)


def default_sensitive(kind, case, level=None):
    """Per choice: does a completed outcome of the item's predicates differ between the
    defaults, and does no rule select on them (silent)? M7 expects the two to coincide."""
    if kind not in SELECTION_ITEMS and not kind.startswith("SILENT:") or kind.startswith("SILENT:EVIDENCE"):
        return None
    rows = []
    for assignment in choices(cone(item_predicates(kind))):
        choice = full_choice(assignment)
        predicates = relevant_predicates(kind, case, choice)
        values, silent = {}, {}
        for default in ("deny", "allow"):
            doc = document(choice, default)
            model = case_model(doc, case_atoms(case))
            for predicate in predicates:
                sorts = T.environment().predicates[predicate].arguments
                for args in itertools.product(*(model.domains[s] for s in sorts)):
                    if args[0] != "p" or (level is not None and args[1:] != (level,)):
                        continue
                    values.setdefault((predicate, args), []).append(completed(doc, model, predicate, args))
                    if default == "deny":
                        silent[(predicate, args)] = not (predicate in doc.elaborated.order and
                                                         doc.elaborated.selected_rules(predicate, model, args))
        sensitive = {k: a != b for k, (a, b) in values.items()}
        rows.append({"choice": dict(assignment), "sensitive": any(sensitive.values()),
                     "coincide": all(sensitive[k] == silent[k] for k in sensitive)})
    return rows


# --- the run ---------------------------------------------------------------------------------

def progress(message):
    print(f"[{time.strftime('%H:%M:%S')}] {message}", file=sys.stderr, flush=True)


def run():
    started = time.time()
    key_items = json.loads((HERE / "answer-key.json").read_text())["items"]
    # Only the item list (id, case, kind) is read here; the verdicts are read by compare().
    plan = [{k: v for k, v in item.items() if k in ("id", "case", "item", "level")} for item in key_items]
    results = {"cases": {}, "items": {}, "premises": {}}
    evaluations = []
    for item in plan:
        kind, case_id = item["item"], item["case"]
        if case_id is None:
            continue
        case = CASES[case_id]
        status = premise_status(case_atoms(case))
        results["premises"][case_id] = {"status": status[0], "failed": status[1]}
        if kind == "SILENT:CCA+GOV":
            parts = {"SILENT:CCA": item_result("SILENT:CCA", case), "GOV": item_result("GOV", case)}
            results["items"][item["id"]] = {"parts": parts, "premises": status[0]}
            evaluations.extend(parts.values())
            continue
        if kind == "FORBIDS+L0":
            other = CASES["G9-L0"]
            results["premises"]["G9-L0"] = {"status": premise_status(case_atoms(other))[0], "failed": None}
            parts = {"FORBIDS": item_result("FORBIDS", case), "FORBIDS@G9-L0": item_result("FORBIDS", other)}
            results["items"][item["id"]] = {"parts": parts, "premises": status[0]}
            evaluations.extend(parts.values())
            continue
        if kind == "PROXIMITY":
            result = item_result(kind, case, level=item.get("level"))
        else:
            result = item_result(kind, case)
        result["premises"] = status[0]
        results["items"][item["id"]] = result
        evaluations.append(result)
    progress("conflict clusters")
    for name, rule_ids in CONFLICT_CLUSTERS.items():
        results["items"][next(i["id"] for i in plan if i["item"] == name)] = conflict_result(rule_ids)
    progress("document conflicts")
    per_predicate = document_conflicts()
    results["document_conflicts"] = per_predicate
    results["items"]["C-doc"] = union_result(list(per_predicate.values()))
    progress("family N")
    n = family_n(evaluations)
    for item_id in ("N1", "N2", "N3"):
        results["items"][item_id] = n[item_id]
    progress("default sensitivity")
    results["default_sensitive"] = {}
    for item in plan:
        if item["case"] is None or item["item"] in ("SILENT:CCA+GOV", "FORBIDS+L0", "GOV", "CATCH_ALL",
                                                     "CHECKPOINT_MCCA"):
            continue
        rows = default_sensitive(item["item"], CASES[item["case"]], item.get("level"))
        if rows is not None:
            results["default_sensitive"][item["id"]] = {
                "choices": len(rows), "sensitive_choices": sum(r["sensitive"] for r in rows),
                "mismatch": [r["choice"] for r in rows if not r["coincide"]]}
    progress("variants")
    results["variants"] = variants()
    results["lint"] = identifier_lint()
    results["invention_audit"] = invention_audit()
    results["cost"] = {"rule_candidates": len(T.rule_blocks()), "premises": len(PREMISES()),
                       "documents_built": len(_DOCS), "case_models": len(_MODELS),
                       "cases": len(CASES), "prover_calls": PROVER_CALLS[0]}
    results["seconds"] = round(time.time() - started, 1)
    return results


# --- variants: without N1 (prediction), without N2 (strict), mutants ----------------------------

F16_STRICT = ("f16-strict", "Rule 1. Every proposal must apply each measure to the model weights, if there is a "
              "level such that all of the following hold: (a) that proposal has reached that level; (b) at least one "
              "of the following holds: (i) that level recommends that measure; (ii) there is a second measure such "
              "that both that level recommends the second measure and the second measure includes that measure, "
              "unless at least one of the following holds: (a) that proposal is classified as \"like_public_models\"; "
              "(b) either that proposal is classified as \"security_assessed_adequate\" or that proposal is classified "
              "as \"open_release_benefits_outweigh_risks\", or both.")
MUTANTS = {
    "m1": (("precedence", {}),),
    "m2": (),  # a fact edit, below
    "m3": (),  # a D2 order edit (severity family), reported with family S
    "m4": (),  # a fact edit, below
    "m5": (("drop", ("f8",)), ("add", ("m5-f8", "Rule 1. Every proposal may proceed, if it is not the case that "
                                       "there is a level such that that proposal has reached that level."))),
    # m6 deletes the sentence "This is required only for external deployment, not internal deployment
    # or further development" from F9: the release goes, and DM-h is no longer limited to external deployment.
    "m6": (("drop", ("f9-rel", "f9-dm", "f9-acc")),
           ("add", ("m6-f9-dm", "Rule 1. Every proposal must have mitigations make the residual risk of harm "
                    "acceptable, if there is a level such that both that proposal has reached that level and that "
                    "level is misuse.", (("RS1", "G"),))),
           ("add", ("m6-f9-acc", "Rule 1. Every proposal is acceptable, if there is a level such that all of the "
                    "following hold: (a) both that proposal has reached that level and that level is misuse; (b) all "
                    "of the following hold: (i) that proposal mitigates that level; (ii) at least one of the following "
                    "holds: (a) there is a measure such that both that level recommends that measure and that proposal "
                    "applies that measure; (b) either that proposal is classified as \"security_assessed_adequate\" or "
                    "that proposal is classified as \"open_release_benefits_outweigh_risks\", or both."))),
}


def variants():
    out = {}
    # Without N2: F16 under Ds is strict.
    strict = (("drop", ("f16-ds",)), ("add", (*F16_STRICT, (("RS3", "Ds"),))))
    out["without_N2"] = {
        "C1": conflict_result(("f15-same", "f15-diff", "f16-ds", "f16-strict"), strict),
        "B-L2/RECSEC": item_result("RECSEC", CASES["B-L2"], variant=strict),
    }
    # Without N1: every rule from a "will" sentence is a prediction, not a norm.
    prediction = (("drop", tuple(sorted(T.WILL_RULES))),)
    changed = []
    for item_id, case_id, kind in (("A-L2-EXT/DM", "A-L2-EXT", "DM"), ("A-L2-EXT/SEC", "A-L2-EXT", "SEC"),
                                   ("B-L2/RRA", "B-L2", "RRA"), ("B-L2/SC", "B-L2", "SC"),
                                   ("B-L5/PRA", "B-L5", "PRA"), ("K5/SUBMISSION", "K5", "SUBMISSION"),
                                   ("K6/YEARLY_REVIEW", "K6", "YEARLY_REVIEW"), ("R2/ACCEPTABLE", "R2", "ACCEPTABLE")):
        with_n1 = describe(item_result(kind, CASES[case_id]))
        without = describe(item_result(kind, CASES[case_id], variant=prediction))
        changed.append({"item": item_id, "with_N1": with_n1, "without_N1": without})
    out["without_N1"] = changed
    # Mutants m1, m5, m6 (rules); m2, m4 (facts) are checked against the premises and the N family.
    out["m1"] = {"C2": conflict_result(("f2", "f3"), MUTANTS["m1"])}
    out["m5"] = {"C5": conflict_result(("m5-f8", "f12-p", "f12-u", "f13-p", "f13-u"), MUTANTS["m5"])}
    m6 = {}
    for k in range(1, 5):
        for act in ("DEV", "INT", "HRI"):
            case_id = f"A-L{k}-{act}"
            r = item_result("DM", CASES[case_id], variant=MUTANTS["m6"])
            m6[f"{case_id}/DM"] = describe(r)
    m6["C3"] = describe(conflict_result(CONFLICT_CLUSTERS["CONFLICT:f9:f10"] + ("m6-f9-dm",), MUTANTS["m6"]))
    out["m6"] = m6
    out["m2"] = mutant_fact("recommends", "cbrn_uplift_tcl", "security_level_2_plus")
    out["m4"] = mutant_cyber_tcl()
    return out


def mutant_cyber_tcl():
    """m4: an invented cyber TCL (a level that is tracked and concerns cyber)."""
    premises = tuple(f for _, _, formulas in T.facts() for f in formulas)
    invented = A.Exists("level", A.And(A.Unary("tracked", A.Var(0)), A.Binary("concerns", A.Var(0), A.Const("cyber"))))
    return {"fact": "there is a level that is tracked and concerns cyber", "traced_to_source": False,
            "premises_inconsistent": refute(premises, [invented]) is not None}


def mutant_fact(*atom):
    """Add one invented fact: is it consistent with the premises, and does N1 / N2 change?"""
    env = T.base_environment()
    premises = tuple(f for _, _, formulas in T.facts() for f in formulas)
    stated = premises + (_atom_formula(atom),)
    model = _model(env, frozenset(a for a in fact_atoms() if a[0] in env.predicates) | {atom})
    consistent = all(holds(env, f, model) for f in stated)
    traced = atom in fact_atoms()
    effect = {}
    if atom[0] == "recommends":
        goal = A.Exists("measure", A.Binary("recommends", A.Const("cbrn_uplift_tcl"), A.Var(0)))
        effect["N2_entailed"] = refute(premises, [_atom_formula(atom)], goal) is not None
    if atom[0] == "tracked":
        effect["premises_inconsistent"] = refute(premises, [_atom_formula(atom)]) is not None
    return {"fact": list(atom), "traced_to_source": traced, "model_satisfies_premises": consistent, **effect}


# --- comparison --------------------------------------------------------------------------------

def compare(results):
    key_items = json.loads((HERE / "answer-key.json").read_text())["items"]
    rows = []
    for item in key_items:
        if item["plan"] in ("6.7", "6.8"):
            continue  # families S and D: severity_and_dates.compare
        got = results["items"].get(item["id"])
        if got is None:
            rows.append({"id": item["id"], "key": item["key"], "ve": "NOT RUN", "agree": False})
            continue
        if item["id"].startswith(("N1", "N2", "N3")):
            ve = got["verdict"]
            rows.append({"id": item["id"], "key": item["key"], "ve": ve, "agree": ve == item["key"]})
            continue
        if "parts" in got:
            agree, shown = True, {}
            for part, verdict in item["key"].items():
                r = got["parts"][part]
                agree &= same_set(verdict, r)
                shown[part] = describe(r)
            rows.append({"id": item["id"], "key": item["key"], "ve": shown, "agree": agree,
                         "premises": got.get("premises")})
            continue
        ve = describe(got)
        agree = same_set(item["key"], got)
        row = {"id": item["id"], "key": item["key"], "ve": ve, "agree": agree}
        if got.get("premises") not in (None, "model"):
            row["premises"] = got["premises"]
            row["agree"] = False
        if "rel" in item:
            rel = {"cone": got["cone"], "true": got.get("release_true", [])}
            row["key_rel"] = item["rel"]
            row["ve_rel"] = describe(rel)
            if not same_set(item["rel"], rel):
                row["agree"] = False
        rows.append(row)
    return rows


def same_set(verdict, result):
    if verdict in ("ALL", "NONE") or verdict.startswith("SOME("):
        variables = sorted(set(result["cone"]) | set(condition_vars(verdict)[1] if verdict.startswith("SOME(") else []))
        return verdict_set(verdict, variables) == result_set(result, variables)
    return False


def severity_and_dates_available():
    import severity_and_dates
    return severity_and_dates.RISK_ROUTE.exists()


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    results = run()
    import severity_and_dates
    results["d2_d3"] = severity_and_dates.run()
    results["comparison"] = compare(results) + severity_and_dates.compare(results["d2_d3"])
    seconds = results.pop("seconds")
    text = json.dumps(results, indent=1, sort_keys=True) + "\n"
    if args.check:
        if RESULTS.read_text() != text:
            raise SystemExit("results.json is out of date")
    else:
        RESULTS.write_text(text)
    rows = results["comparison"]
    agree = sum(r["agree"] for r in rows)
    print(f"agreement with the answer key: {agree}/{len(rows)} ({seconds} s)")
    for row in rows:
        if not row["agree"]:
            print("  DISAGREE", row["id"], "key", row["key"], "VE", row["ve"],
                  *(f"rel key {row['key_rel']} VE {row['ve_rel']}",) if "key_rel" in row else (),
                  *(f"premises {row['premises']}",) if "premises" in row else ())
    return 0


if __name__ == "__main__":
    sys.exit(main())
