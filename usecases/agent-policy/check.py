"""Runs VE on every case of the agent-policy use case (PLAN sections 5 to 11).

`python usecases/agent-policy/check.py` writes `results.json` and prints the
comparison with `answer-key.json`. The harness never reads the answer key
while it computes a result; `compare` reads it afterwards.

Evidence per logged action (PLAN section 12 records why it is staged):

1. Stage 1: for each rule, VE's prover proves that the rule's guard and
   carve-outs hold, or fail, for the action. The premises are the inventory
   and the action's own record, restricted to sentences that share a
   predicate with the goal (fewer premises keep a proof valid).
2. Stage 2: each rule's selection formula from `NormDocument.selection`,
   proved from the stage-1 lemmas by the focused search in `focused.py`.
3. Completed outcomes: `permitted(a)`, `not permitted(a)` or a contradiction,
   proved with the norm layers of each default environment.

VE's checker replays every certificate before it counts. The closed-world
model of a record only chooses which direction to try: it satisfies the
record, so it already refutes the other direction. A formula proved neither
way is OPEN only with a second checked model of the same premises that gives
it the other value; otherwise it is UNKNOWN.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing
import os
import subprocess
import sys
import time
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

import focused  # noqa: E402
import mutants as mutant_edits  # noqa: E402
from environments import TOOLS  # noqa: E402
from ve.ast import (And, Binary, Bottom, Const, Exists, Not, Or, Unary, Var,  # noqa: E402
                    formula_to_data)
from ve.english import parse_english as parse_sentences  # noqa: E402
from ve.entailment import _binding, _validate_inputs, check_entailment_certificate, prove_entailment  # noqa: E402
from ve.environment import Environment  # noqa: E402
from ve.errors import VEError  # noqa: E402
from ve.evaluate import evaluate  # noqa: E402
from ve.model import FiniteModel  # noqa: E402
from ve.norm_english import parse_english as parse_rules  # noqa: E402
from ve.norms import (NormDocument, Norm, _any, _bind, _instantiate, check_conflict,  # noqa: E402
                      check_norm_entailment_certificate)
from ve.search import _used_predicates  # noqa: E402

VARIANTS = ("deny-neednot", "deny-must", "allow-neednot", "allow-must")
PERMISSION, OBLIGATION = "permitted", "report_required"
STAGE1_STEPS = 2000
POLICY_STEPS = 5000
FOCUSED_NODES = 20000
LEAN_ROUTE = REPO / "lean/.lake/build/bin/ve_conformance"
LEAN_NORMS = REPO / "lean/.lake/build/bin/ve_norms_route"
RUST = REPO / "rust/target/release/ve"


def read_json(name):
    return json.loads((HERE / name).read_text())


def sha256(name):
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()


LOG_CONSTANTS = read_json("log.vocabulary.json")["constants"]
_ENVIRONMENTS = {}


def environment(variant="deny-neednot", action=None, *, log=False, data=None):
    """A default environment, with the inventory and one action (or the whole log) if asked."""
    key = (variant, action, log, json.dumps(data, sort_keys=True) if data else None)
    if key not in _ENVIRONMENTS:
        raw = data if data is not None else read_json(f"environment.{variant}.json")
        raw = json.loads(json.dumps(raw))
        if log or action is not None:
            raw["vocabulary"]["constants"].update(
                {k: v for k, v in LOG_CONSTANTS.items() if log or v["sort"] != "action" or k == action})
        _ENVIRONMENTS[key] = Environment(raw)
    return _ENVIRONMENTS[key]


def base_of(env):
    return NormDocument(env, ()).base_environment()


# --- the policy --------------------------------------------------------------

def policy(text=None, names=None, env=None):
    """The authored rules. The committed text is checked against its manifest;
    a mutant text is parsed without one and given the names in `names`."""
    env = env or environment()
    if text is None:
        return parse_rules(env, (HERE / "policy.ve").read_text(), read_json("policy.manifest.json"))
    parsed = parse_rules(env, text)
    rename = {r.name: names[i] for i, r in enumerate(parsed.rules)}
    return NormDocument(env, [Norm(rename[r.name], r.predicate, r.sign, r.guard, r.unless,
                                   tuple(rename[o] for o in r.over)) for r in parsed.rules])


def numbers(rules):
    return {r.name: i for i, r in enumerate(rules, 1)}


def applies_open(rule):
    return And(rule.guard, Not(_any(rule.unless)))


def at(formula, action):
    return _instantiate(formula, (Const(action),))


# --- the log -----------------------------------------------------------------

def constants_of(formula, found=None):
    found = set() if found is None else found
    if type(formula) is Const:
        found.add(formula.name)
    for field in ("term", "left", "right", "body"):
        child = getattr(formula, field, None)
        if child is not None:
            constants_of(child, found)
    return found


_PARSED = {}


def parse_paragraph(text):
    """One paragraph of the log, parsed with the one-reading check (cached by text)."""
    if text not in _PARSED:
        _PARSED[text] = tuple(parse_sentences(base_of(environment(log=True)), text).formulas)
    return _PARSED[text]


def parse_log(text, pool=None):
    """The inventory paragraph and one record per action, each parsed with one reading."""
    paragraphs = text.split("\n\n")
    missing = [p for p in paragraphs if p not in _PARSED]
    if pool is not None and missing:
        _PARSED.update(zip(missing, pool.map(parse_paragraph, missing)))
    inventory = parse_paragraph(paragraphs[0])
    records = {}
    for paragraph in paragraphs[1:]:
        formulas = parse_paragraph(paragraph)
        actions = {c for f in formulas for c in constants_of(f)
                   if c in LOG_CONSTANTS and LOG_CONSTANTS[c]["sort"] == "action"}
        if len(actions) != 1:
            raise VEError(f"a record must mention exactly one action: {sorted(actions)}")
        records[actions.pop()] = formulas
    return inventory, records


# --- finite models -----------------------------------------------------------

def _model(env, domains, constants, relations):
    return FiniteModel.from_dict(env, {"complete": True,
                                       "domains": {s: list(v) for s, v in domains.items()},
                                       "constants": dict(constants),
                                       "relations": {p: sorted(map(list, relations.get(p, ())))
                                                     for p in env.predicates}})


def record_model(env, premises):
    """The closed-world model of a sub-log: each constant its own element, the
    stated atoms true and all others false. It is checked, never assumed."""
    domains = {sort: [] for sort in env.model_sorts}
    for name, decl in env.constants.items():
        domains[decl.sort].append(name)
    relations = {p: set() for p in env.predicates}
    for formula in premises:
        if type(formula) in (Unary, Binary):
            args = (formula.term,) if type(formula) is Unary else (formula.left, formula.right)
            relations[formula.predicate].add(tuple(a.name for a in args))
    return _model(env, domains, {n: n for n in env.constants}, relations)


def with_relations(env, model, changes):
    relations = {p: set(rows) for p, rows in model.relations.items()}
    relations.update(changes)
    return _model(env, model.domains, model.constants, relations)


def value(env, formula, model):
    result = evaluate(env, formula, model, trace=False)
    if result.value is None:
        raise VEError(f"evaluation failed: {result.status}")
    return bool(result.value)


def satisfies(env, premises, model):
    return all(value(env, f, model) for f in premises)


def one_atom_variants(env, model, predicates=None):
    """Valid models that differ from `model` in exactly one base atom."""
    for predicate in sorted(predicates or env.predicates):
        if env.predicates[predicate].regulated is not None:
            continue
        sorts = env.predicates[predicate].arguments
        for args in product(*(model.domains[s] for s in sorts)):
            try:
                yield (predicate, list(args)), with_relations(
                    env, model, {predicate: set(model.relations[predicate]) ^ {tuple(args)}})
            except VEError:
                continue


# --- evidence ------------------------------------------------------------------

class Evidence:
    """Counts every prover call and keeps each replayed certificate for Lean."""

    def __init__(self, keep=False):
        self.keep = keep
        self.counts = {"ve_prover_calls": 0, "ve_prover_steps": 0, "focused_calls": 0,
                       "focused_nodes": 0, "certificates": 0, "open_by_models": 0,
                       "unknown": 0, "model_witnesses": 0}
        self.cases = []
        self.witnesses = []
        self.exported = {}
        self.cache = {}

    def _store(self, env, premises, goal, certificate, *, norm=None):
        self.counts["certificates"] += 1
        if self.keep:
            self.cases.append({"env": env, "premises": tuple(premises), "goal": goal,
                               "certificate": certificate, "norm": norm})

    def prove(self, env, premises, goal, *, steps=STAGE1_STEPS):
        """VE's own prover; the certificate is replayed inside `prove_entailment`."""
        cache_key = ("ve", env.environment_id, tuple(premises), goal)
        if cache_key in self.cache:
            return self.cache[cache_key]
        self.counts["ve_prover_calls"] += 1
        result = prove_entailment(env, premises, goal, max_steps=steps)
        self.counts["ve_prover_steps"] += result.steps
        found = None
        if result.status == "Found":
            found = {"prover": "ve", "steps": result.steps}
            self._store(env, premises, goal, result.certificate)
        self.cache[cache_key] = found
        return found

    def focus(self, env, premises, goal, *, doc=None, lemmas=(), instantiate=(), active_premises=False):
        """The focused search; `doc` makes it a norm entailment over `doc`'s layers."""
        cache_key = ("focused", env.environment_id, tuple(premises), goal, tuple(instantiate), active_premises)
        if cache_key in self.cache:
            return self.cache[cache_key]
        self.counts["focused_calls"] += 1
        replay = None
        if doc is not None:
            replay = lambda c: check_norm_entailment_certificate(doc, lemmas, goal, c)  # noqa: E731
        found = None
        try:
            certificate, nodes = focused.prove(env, premises, goal, instantiate=instantiate,
                                               max_nodes=FOCUSED_NODES, replay=replay,
                                               active_premises=active_premises)
            self.counts["focused_nodes"] += nodes
            found = {"prover": "focused", "nodes": nodes}
            self._store(env, premises, goal, certificate, norm=doc)
        except focused.Failed:
            pass
        self.cache[cache_key] = found
        return found

    def witness(self, env, model, formula, expected):
        """A model result that counts as evidence; Rust re-evaluates it later."""
        self.counts["model_witnesses"] += 1
        if self.keep:
            self.witnesses.append({"env": env, "model": model, "formula": formula, "value": expected})

    def export(self):
        """JSON-ready Lean `certificate` cases and Rust evaluation cases."""
        return {"counts": dict(self.counts), "lean": [lean_case(c) for c in self.cases],
                "rust": [{"environment": w["env"].to_dict(), "model": w["model"].to_dict(),
                          "ast": [formula_to_data(w["env"], w["formula"])], "value": w["value"]}
                         for w in self.witnesses]}

    def merge(self, exported):
        for name, count in exported["counts"].items():
            self.counts[name] += count
        self.exported.setdefault("lean", []).extend(exported["lean"])
        self.exported.setdefault("rust", []).extend(exported["rust"])

    def flush(self):
        """Move this process's own kept cases into the exported lists."""
        exported = self.export()
        self.exported.setdefault("lean", []).extend(exported["lean"])
        self.exported.setdefault("rust", []).extend(exported["rust"])
        self.cases, self.witnesses = [], []


def relevant(premises, formula):
    used = _used_predicates(formula)
    return tuple(p for p in premises if _used_predicates(p) & used)


def decide(env, premises, formula, model, prove, evidence):
    """(value, how): proved True/False, or None with "models" (OPEN) or "unknown"."""
    truth = value(env, formula, model)
    if prove(formula if truth else Not(formula)) is not None:
        return truth, "certificate"
    for change, other in one_atom_variants(env, model, _used_predicates(formula, *premises)):
        if value(env, formula, other) != truth and satisfies(env, premises, other):
            evidence.counts["open_by_models"] += 1
            evidence.witness(env, model, formula, truth)
            evidence.witness(env, other, formula, not truth)
            return None, "models"
    evidence.counts["unknown"] += 1
    return None, "unknown"


# --- per action (PLAN section 5) ----------------------------------------------------

def verdict_of(split, rules, names):
    positive = {names[r.name] for r in rules if r.sign}
    negative = {names[r.name] for r in rules if not r.sign}
    s_pos, s_neg, s_open = set(split["positive"]), set(split["negative"]), set(split["open"])
    if s_pos and s_neg:
        return "CONFLICT"
    if s_pos and not s_neg and not s_open & negative:
        return "APPROVED"
    if s_neg and not s_pos and not s_open & positive:
        return "REJECTED"
    if not (s_pos or s_neg or s_open):
        return "NOT-COVERED"
    return "UNDETERMINED"


def analyse_action(action, rules, inventory, record, evidence, *, outcomes=True):
    names = numbers(rules)
    env = environment("deny-neednot", action)
    doc = NormDocument(env, rules)
    base = base_of(env)
    premises = tuple(inventory) + tuple(record)
    model = record_model(base, premises)
    if not satisfies(base, premises, model):
        raise VEError(f"{action}: the closed-world model does not satisfy the record")

    applies, lemmas = {}, []
    for rule in rules:
        formula = at(applies_open(rule), action)
        truth, how = decide(base, premises, formula, model,
                            lambda goal: evidence.prove(base, relevant(premises, goal), goal), evidence)
        applies[names[rule.name]] = {"value": truth, "evidence": how}
        if truth is not None:
            lemmas.append(formula if truth else Not(formula))
    lemmas = tuple(lemmas)

    selected, parts = {}, {}
    for predicate in (PERMISSION, OBLIGATION):
        own = [r for r in rules if r.predicate == predicate]
        formulas = doc.selection(predicate)[2]
        for rule in own:
            truth, how = decide(base, premises, at(formulas[rule.name], action), model,
                                lambda goal: evidence.focus(base, lemmas, goal), evidence)
            selected[names[rule.name]] = {"value": truth, "evidence": how}
        parts[predicate] = {
            "positive": [names[r.name] for r in own if r.sign and selected[names[r.name]]["value"] is True],
            "negative": [names[r.name] for r in own if not r.sign and selected[names[r.name]]["value"] is True],
            "open": [names[r.name] for r in own if selected[names[r.name]]["value"] is None],
            "verdict": None}
        parts[predicate]["verdict"] = verdict_of(parts[predicate], own, names)

    finite = {predicate: sorted(names[r.name] for r in doc.selected_rules(predicate, model, (action,)))
              for predicate in (PERMISSION, OBLIGATION)}
    reported = next((type(f) is not Not for f in record
                     if _flag(f) == ("reported", action)), None)
    result = {"verdict": parts[PERMISSION]["verdict"], "permission": parts[PERMISSION],
              "obligation": parts[OBLIGATION], "finite_model": finite, "reported": reported,
              "complete": all(v["value"] is not None for v in applies.values()),
              "applies": applies, "selected": selected}
    if outcomes:
        inconsistent = any(p["positive"] and p["negative"] for p in parts.values())
        result["outcomes"] = completed_outcomes(action, rules, premises, lemmas, inconsistent, evidence)
    return result


def _flag(formula):
    formula = formula.body if type(formula) is Not else formula
    if type(formula) is Unary and type(formula.term) is Const:
        return (formula.predicate, formula.term.name)
    return None


# Each predicate's completed outcome under its own two defaults. A layer only
# mentions its own predicate (no guard mentions a regulated predicate), so the
# other predicate's default does not enter the proof.
OUTCOME_VARIANTS = {PERMISSION: {"deny": "deny-neednot", "allow": "allow-neednot"},
                    OBLIGATION: {"need not": "deny-neednot", "must": "deny-must"}}


def completed_outcomes(action, rules, premises, lemmas, inconsistent, evidence):
    """P (holds), F (fails), ⊥ (the layers contradict the record) or ? (two
    checked models of the layers and the record disagree), per default."""
    out = {predicate: {} for predicate in OUTCOME_VARIANTS}
    for predicate, variants in OUTCOME_VARIANTS.items():
        for default, variant in variants.items():
            out[predicate][default] = _outcome(variant, predicate, action, rules, premises, lemmas,
                                               inconsistent, evidence)
    return out


def _outcome(variant, predicate, action, rules, premises, lemmas, inconsistent, evidence):
    env = environment(variant, action)
    doc = NormDocument(env, rules)
    layers = tuple(f for _, f in doc.premises())
    labels = [label for label, _ in doc.premises()]
    opened = {p: (labels.index(f"layer:norms:{p}"), action) for p in doc.order}

    def attempt(goal, predicates):
        return evidence.focus(env, layers + lemmas, goal, doc=doc, lemmas=lemmas,
                              instantiate=[opened[p] for p in predicates])

    if inconsistent:
        # A conflict makes the layers contradict the record at this action.
        return "⊥" if attempt(Bottom(), doc.order) else "unknown"
    base = base_of(env)
    closed = record_model(base, premises)
    full = layers + tuple(premises)
    model = _complete(env, doc, base, closed, action)
    if not satisfies(env, full, model):
        raise VEError(f"{action}: the completed model does not satisfy the layers")
    atom = Unary(predicate, Const(action))
    truth = value(env, atom, model)
    if attempt(atom if truth else Not(atom), [predicate]):
        return "P" if truth else "F"
    for _, other in one_atom_variants(base, closed):
        candidate = _complete(env, doc, base, other, action)
        if value(env, atom, candidate) != truth and satisfies(env, full, candidate):
            evidence.counts["open_by_models"] += 1
            evidence.witness(env, model, atom, truth)
            evidence.witness(env, candidate, atom, not truth)
            return "?"
    evidence.counts["unknown"] += 1
    return "unknown"


def _complete(env, doc, base, model, action):
    """The norm model whose regulated relations are the completed outcomes at `action`."""
    relations = {p: set(rows) for p, rows in model.relations.items()}
    for name in doc.order:
        outcome = at(doc.outcome(name, base=True), action)
        relations[name] = {(action,)} if value(base, outcome, model) else set()
    return _model(env, model.domains, model.constants, relations)


# --- policy level (PLAN section 7) ----------------------------------------------

def policy_model(base, model):
    """A record model seen in the policy's own environment (log names dropped)."""
    return _model(base, model.domains, {n: model.constants[n] for n in base.constants},
                  {p: model.relations[p] for p in base.predicates})


def fresh_tool(base, model, action):
    domains = {s: list(v) for s, v in model.domains.items()}
    domains["$string"] = [*domains["$string"], "other_tool"]
    relations = {p: set(r) for p, r in model.relations.items()}
    relations["tool"] = {(action, "other_tool")}
    return _model(base, domains, model.constants, relations)


def candidate_models(base, records, inventory):
    """Record models in the policy environment, plus each with a fresh, undeclared tool."""
    out = []
    for action, record in records.items():
        env = base_of(environment("deny-neednot", action))
        model = policy_model(base, record_model(env, tuple(inventory) + tuple(record)))
        out.append((action, "record", model))
        out.append((action, "fresh tool", fresh_tool(base, model, action)))
    return out


def exists_action(formula):
    return Exists("action", formula)


def refute(base, premises, formula, evidence, *, active_premises=False):
    """A certificate for `not formula`: VE's prover first, then the focused search."""
    goal = Not(formula)
    return (evidence.prove(base, premises, goal, steps=POLICY_STEPS)
            or evidence.focus(base, premises, goal, active_premises=active_premises))


def first_witness(base, models, formula, evidence):
    for action, kind, model in models:
        if value(base, formula, model):
            evidence.witness(base, model, formula, True)
            return {"action": action, "model": kind}
    return None


def policy_findings(doc, inventory, records, evidence):
    names = numbers(doc.rules)
    base = doc.base_environment()
    models = candidate_models(base, records, inventory)
    records_only = [m for m in models if m[1] == "record"]
    positive, negative, selected = doc.selection(PERMISSION)
    selected = {**selected, **doc.selection(OBLIGATION)[2]}
    permission = [r for r in doc.rules if r.predicate == PERMISSION]
    findings = {}

    conflict = {}
    for target, sorts, formula in doc.conflict_targets():
        claim = _bind(formula, sorts, binder=Exists)
        witness = first_witness(base, records_only, claim, evidence)
        if witness is not None:
            report = check_conflict(doc, model=next(m for a, k, m in records_only if a == witness["action"]))
            conflict[target] = {"status": report.status, "witness": witness["action"],
                                "situation": report.situation}
        else:
            proof = refute(base, (), claim, evidence)
            conflict[target] = {"status": "CONFLICT-FREE" if proof else "UNKNOWN", **(proof or {})}
    findings["conflict"] = conflict

    pairs = {}
    for left in (r for r in permission if r.sign):
        for right in (r for r in permission if not r.sign):
            claim = exists_action(And(selected[left.name], selected[right.name]))
            label = f"{names[left.name]},{names[right.name]}"
            witness = first_witness(base, records_only, claim, evidence)
            if witness is not None:
                pairs[label] = {"status": "satisfiable", "witness": witness["action"]}
            else:
                proof = refute(base, (), claim, evidence)
                pairs[label] = {"status": "refuted" if proof else "unknown", **(proof or {})}
    findings["pairs"] = pairs

    never, dead = {}, {}
    for rule in doc.rules:
        for table, formula, alive, gone in ((never, selected[rule.name], "decides", "never decides"),
                                            (dead, applies_open(rule), "applies", "dead")):
            claim = exists_action(formula)
            witness = first_witness(base, records_only, claim, evidence)
            if witness is not None:
                table[names[rule.name]] = {"status": alive, "witness": witness["action"]}
            else:
                proof = refute(base, (), claim, evidence)
                table[names[rule.name]] = {"status": gone if proof else "unknown", **(proof or {})}
    findings["never_deciding"] = never
    findings["dead_guards"] = dead

    schema = tuple(parse_sentences(base, (HERE / "log-schema.ve").read_text()).formulas)
    covered = Or(positive, negative)
    queries = [(t, Binary("tool", Var(0), Const(t))) for t in TOOLS]
    unnamed = Not(Binary("tool", Var(0), Const(TOOLS[0])))
    for t in TOOLS[1:]:
        unnamed = And(unnamed, Not(Binary("tool", Var(0), Const(t))))
    queries.append(("(an undeclared tool)", unnamed))
    gaps = {}
    for tool, condition in queries:
        gap = exists_action(And(condition, Not(covered)))
        witness = None
        for action, kind, model in models:
            # One-atom variants keep the functional, total tool, so only a
            # model whose action has this tool can yield a witness.
            if not value(base, exists_action(condition), model):
                continue
            for change, candidate in [(None, model), *one_atom_variants(base, model)]:
                if value(base, gap, candidate) and satisfies(base, schema, candidate):
                    evidence.witness(base, candidate, gap, True)
                    witness = {"action": action, "model": kind,
                               **({"changed_atom": change} if change else {})}
                    break
            if witness:
                break
        if witness is not None:
            gaps[tool] = {"status": "gap", **witness}
            continue
        # Only this tool's schema sentence is needed; fewer premises keep the proof valid.
        own = tuple(f for f in schema if tool in constants_of(f))
        proof = refute(base, own, gap, evidence, active_premises=True)
        gaps[tool] = {"status": "covered" if proof else "unknown", **(proof or {})}
    findings["tool_gaps"] = gaps

    overlaps = set()
    for _, _, model in records_only:
        for left, right, _ in doc.overlap_witnesses(model):
            overlaps.add((names[left], names[right]))
    findings["overlaps"] = [list(p) for p in sorted(overlaps)]
    findings["precedence_edges"] = sum(len(r.over) for r in doc.rules)
    return findings


# --- whole runs ----------------------------------------------------------------------

WORKERS = int(os.environ.get("AGENT_POLICY_WORKERS", min(6, os.cpu_count() or 1)))


def _analyse(job):
    action, rules, inventory, record, outcomes, keep = job
    evidence = Evidence(keep=keep)
    result = analyse_action(action, rules, inventory, record, evidence, outcomes=outcomes)
    return action, result, evidence.export()


def run(policy_text=None, log_text=None, *, names=None, evidence=None, outcomes=True, level=True,
        actions=None, pool=None):
    """All per-action results (in `pool` if given) and, if `level`, the policy findings."""
    evidence = evidence or Evidence()
    started = time.time()
    doc = policy(policy_text, names)
    inventory, records = parse_log(log_text if log_text is not None else (HERE / "log.ve").read_text(), pool)
    jobs = [(a, doc.rules, inventory, records[a], outcomes, evidence.keep)
            for a in sorted(records) if actions is None or a in actions]
    per_action = {}
    for action, result, exported in (pool.imap_unordered(_analyse, jobs) if pool else map(_analyse, jobs)):
        per_action[action] = result
        evidence.merge(exported)
    result = {"actions": dict(sorted(per_action.items())), "rules": [r.name for r in doc.rules]}
    if level:
        result["policy"] = policy_findings(doc, inventory, records, evidence)
        evidence.flush()
    result["seconds"] = round(time.time() - started, 1)
    return result


def run_mutants(base, evidence, pool=None, names=None):
    """Each mutant's per-action results; a policy mutant also reruns the policy findings."""
    policy_text = (HERE / "policy.ve").read_text()
    log_text = (HERE / "log.ve").read_text()
    out = {}
    for name, edit in mutant_edits.MUTANTS.items():
        if names is not None and name not in names:
            continue
        mutant_policy, mutant_log = edit(policy_text, log_text)
        changed_policy = mutant_policy != policy_text
        result = run(mutant_policy if changed_policy else None, mutant_log, names=mutant_edits.names(),
                     evidence=evidence, outcomes=False, level=changed_policy, pool=pool)
        if not changed_policy:
            result["policy"] = base["policy"]
        out[name] = {"result": result, "changes": changes(base, result)}
    return out


def changes(base, mutant):
    """Per-action differences in verdict or deciding sets; policy-level differences."""
    names = {i: n for i, n in enumerate(mutant["rules"], 1)}
    label = lambda n: "M" if names[n] == mutant_edits.NEW_RULE else n  # noqa: E731
    diff = {}
    for action, now in mutant["actions"].items():
        before = base["actions"][action]
        fields = {}
        if now["verdict"] != before["verdict"]:
            fields["verdict"] = now["verdict"]
        for part in ("positive", "negative", "open"):
            if now["permission"][part] != before["permission"][part]:
                fields[part] = [label(n) for n in now["permission"][part]]
        if fields:
            diff[action] = fields
    before, now = policy_summary(base["policy"]), policy_summary(mutant["policy"])
    policy_diff = {field: now[field] for field in now if now[field] != before[field]}
    return {"actions": diff, "policy": policy_diff}


# --- Lean and Rust replay (PLAN metric M9) ---------------------------------------------

def _plain(env):
    """The environment with the regulated predicates declared as ordinary ones."""
    data = env.to_dict()
    for decl in data["vocabulary"]["predicates"].values():
        decl.pop("regulated", None)
    data["profiles"] = [p for p in data["profiles"] if p != "norms@0"]
    return Environment(data)


def lean_case(item):
    """A P0 `certificate` case. A norm-entailment certificate is rebound to the plain
    environment with the layers as ordinary premises (PLAN section 8, fallback)."""
    env, premises, goal, certificate = item["env"], item["premises"], item["goal"], item["certificate"]
    if item["norm"] is not None:
        env = _plain(env)
        validated = _validate_inputs(env, premises, goal)
        certificate = {**_binding(env, validated, goal), "trace": certificate["trace"]}
        if not check_entailment_certificate(env, premises, goal, certificate, max_steps=1_000_000).valid:
            raise VEError("a rebound norm certificate does not replay in Python")
    return {"kind": "certificate", "environment": env.to_dict(),
            "premises": [formula_to_data(env, p) for p in premises],
            "conclusion": formula_to_data(env, goal), "certificate": certificate,
            "norm": item["norm"] is not None}


def replay_lean(exported, batch=100):
    if not LEAN_ROUTE.exists():
        return {"status": "skipped: lake build has not produced ve_conformance"}
    cases = exported.get("lean", [])
    valid = {"base": 0, "norm layers as premises": 0}
    total = {"base": 0, "norm layers as premises": 0}
    for start in range(0, len(cases), batch):
        chunk = cases[start:start + batch]
        payload = [{k: v for k, v in c.items() if k != "norm"} | {"id": str(start + i)}
                   for i, c in enumerate(chunk)]
        done = subprocess.run([str(LEAN_ROUTE), "route", "-"], input=json.dumps(payload), text=True,
                              capture_output=True, timeout=3600)
        rows = json.loads(done.stdout)
        for case, row in zip(chunk, rows):
            kind = "norm layers as premises" if case["norm"] else "base"
            total[kind] += 1
            valid[kind] += row.get("valid") is True
    return {"certificates": total, "valid": valid}


def replay_rust(exported, batch=200):
    if not RUST.exists():
        return {"status": "skipped: cargo has not produced rust/target/release/ve"}
    cases = exported.get("rust", [])
    agree = 0
    for start in range(0, len(cases), batch):
        chunk = cases[start:start + batch]
        payload = [{k: v for k, v in c.items() if k != "value"} | {"id": str(start + i)}
                   for i, c in enumerate(chunk)]
        done = subprocess.run([str(RUST), "conformance", "-"], input=json.dumps(payload), text=True,
                              capture_output=True, timeout=3600)
        rows = json.loads(done.stdout)
        agree += sum(row.get("values") == [case["value"]] for case, row in zip(chunk, rows))
    return {"models": len(cases), "agree": agree}


def lean_norms_route(doc, inventory, records):
    """The document conflict results on the flag-free environment (PLAN section 8)."""
    if not LEAN_NORMS.exists():
        return {"status": "skipped: lake build has not produced ve_norms_route"}
    env = Environment(read_json("environment.lean.json"))
    lean_doc = NormDocument(env, doc.rules)
    base = lean_doc.base_environment()
    flagged = doc.base_environment()
    cases, notes = [], {}
    for target, sorts, formula in lean_doc.conflict_targets():
        claim = _bind(formula, sorts, binder=Exists)
        for action, record in records.items():
            model = record_model(base_of(environment("deny-neednot", action)), tuple(inventory) + tuple(record))
            flag_model = policy_model(flagged, model)
            lean_model = policy_model(base, model)
            if value(base, claim, lean_model):
                report = check_conflict(doc, model=flag_model)
                cases.append({"id": f"witness:{target}", "kind": "norms-conflict",
                              "environment": env.to_dict(), "norms": [r.to_dict() for r in doc.rules],
                              "witness": {"target": target, "model": lean_model.to_dict(), "tuple": [action]}})
                notes[target] = {"python_flagged_model": report.status}
                break
    # Conflict-freedom packages: the committed document (expected: none for
    # `permitted`), its obligation rules alone, and the fixed mutant m1.
    m1_text, _ = mutant_edits.m1((HERE / "policy.ve").read_text(), "")
    documents = {"policy": lean_doc,
                 "obligation rules only": NormDocument(env, [r for r in doc.rules if r.predicate == OBLIGATION]),
                 "mutant m1": NormDocument(env, policy(m1_text, mutant_edits.names()).rules)}
    certified = {}
    for name, document in documents.items():
        packages = _packages(document)
        certified[name] = sorted(packages)
        cases.append({"id": f"packages:{name}", "kind": "norms-conflict", "environment": env.to_dict(),
                      "norms": [r.to_dict() for r in document.rules], "packages": packages})
    done = subprocess.run([str(LEAN_NORMS), "-"], input=json.dumps(cases), text=True,
                          capture_output=True, timeout=1800)
    rows = json.loads(done.stdout)
    return {"rows": [{k: row.get(k) for k in ("id", "verdict", "target", "detail", "error")} for row in rows],
            "certified_targets": certified, "python": notes}


def _packages(document):
    """Conflict packages over the flag-free Background, where a certificate is found."""
    base = document.base_environment()
    evidence = Evidence()
    packages = {}
    for target, sorts, formula in document.conflict_targets():
        goal = _bind(Not(formula), sorts)
        certificate = None
        result = prove_entailment(base, (), goal, max_steps=POLICY_STEPS)
        if result.status == "Found":
            certificate = result.certificate
        else:
            try:
                certificate, _ = focused.prove(base, (), goal, max_nodes=FOCUSED_NODES)
            except focused.Failed:
                pass
        if certificate is not None:
            packages[target] = {"environment_id": document.env.environment_id,
                                "document_hash": document.document_hash, "target": target,
                                "certificate": certificate}
    return packages


# --- comparison with the answer key (PLAN section 9) ------------------------------------

def key_rules(entry):
    return {"positive": entry["positive"], "negative": entry["negative"], "open": entry["open"]}


def rule_25(result):
    covered = result["obligation"]["positive"]
    if result["obligation"]["verdict"] == "UNDETERMINED":
        return "undetermined"
    if not covered:
        return "not covered"
    if result["verdict"] != "APPROVED":
        return "required"
    return "required (reported)" if result["reported"] else "required, BREACH"


def compare(results, key):
    actions = results["actions"]
    report = {"verdict_disagreements": {}, "rule_disagreements": {}, "outcome_disagreements": {},
              "rule_25_disagreements": {}}
    confusion = {}
    for action, expected in key["actions"].items():
        got = actions[action]
        confusion.setdefault(expected["verdict"], {}).setdefault(got["verdict"], 0)
        confusion[expected["verdict"]][got["verdict"]] += 1
        if got["verdict"] != expected["verdict"]:
            report["verdict_disagreements"][action] = {"key": expected["verdict"], "ve": got["verdict"]}
        mine = {part: got["permission"][part] for part in ("positive", "negative", "open")}
        if mine != key_rules(expected):
            report["rule_disagreements"][action] = {"key": key_rules(expected), "ve": mine}
        if "outcomes" in got:
            outcome = got["outcomes"][PERMISSION]
            if outcome != {"deny": expected["deny"], "allow": expected["allow"]}:
                report["outcome_disagreements"][action] = {"key": [expected["deny"], expected["allow"]],
                                                           "ve": [outcome["deny"], outcome["allow"]]}
        if rule_25(got) != expected["rule_25"]:
            report["rule_25_disagreements"][action] = {"key": expected["rule_25"], "ve": rule_25(got)}
    n = len(key["actions"])
    report["M1"] = f"{n - len(report['verdict_disagreements'])}/{n}"
    report["M2"] = f"{n - len(report['rule_disagreements'])}/{n}"
    report["confusion"] = confusion
    report["M3_silent_decisions"] = sorted(
        a for a, r in actions.items() if r["verdict"] in ("APPROVED", "REJECTED")
        and not (r["permission"]["positive"] or r["permission"]["negative"]))
    if all("outcomes" in r for r in actions.values()):
        report["M4_default_sensitive"] = sorted(
            a for a, r in actions.items()
            if r["outcomes"][PERMISSION]["deny"] != r["outcomes"][PERMISSION]["allow"])
        report["obligation"] = {
            "covered": sorted(a for a, r in actions.items() if r["obligation"]["positive"]),
            "breach_neednot": sorted(a for a, r in actions.items() if _breach(r, "need not")),
            "breach_must": sorted(a for a, r in actions.items() if _breach(r, "must"))}
    return report


def _breach(result, default):
    """APPROVED, the report proved required under this default, and not reported."""
    return (result["verdict"] == "APPROVED" and result["outcomes"][OBLIGATION][default] == "P"
            and result["reported"] is False)


def policy_summary(findings):
    return {
        "conflict": {t: v["status"] for t, v in findings["conflict"].items()},
        "satisfiable_pairs": sorted([int(x) for x in k.split(",")] for k, v in findings["pairs"].items()
                                    if v["status"] == "satisfiable"),
        "pair_queries": len(findings["pairs"]),
        "unknown_pairs": sorted(k for k, v in findings["pairs"].items() if v["status"] == "unknown"),
        "never_deciding": sorted(int(n) for n, v in findings["never_deciding"].items()
                                 if v["status"] == "never decides"),
        "dead_guards": sorted(int(n) for n, v in findings["dead_guards"].items() if v["status"] == "dead"),
        "covered_tools": sorted(t for t, v in findings["tool_gaps"].items() if v["status"] == "covered"),
        "gap_tools": sorted(t for t, v in findings["tool_gaps"].items() if v["status"] == "gap"),
        "unknown": sorted(str(k) for part in ("never_deciding", "dead_guards", "tool_gaps")
                          for k, v in findings[part].items() if v["status"] == "unknown"),
        "overlaps": findings["overlaps"],
    }


def reference_agreement(results):
    import reference_policy
    reference = reference_policy.verdicts()
    disagreements = {}
    for action, got in results["actions"].items():
        ref = reference[action]
        mine = {"verdict": got["verdict"], **{p: got["permission"][p] for p in ("positive", "negative", "open")}}
        theirs = {k: ref[k] for k in ("verdict", "positive", "negative", "open")}
        if mine != theirs:
            disagreements[action] = {"reference": theirs, "ve": mine}
    return disagreements


def finite_model_agreement(results):
    """Entailment vs `selected_rules` on the closed-world model, for complete records."""
    complete = sorted(a for a, r in results["actions"].items() if r["complete"])
    disagreements = {}
    for action in complete:
        r = results["actions"][action]
        for predicate, part in ((PERMISSION, "permission"), (OBLIGATION, "obligation")):
            proved = sorted(r[part]["positive"] + r[part]["negative"])
            if proved != r["finite_model"][predicate]:
                disagreements.setdefault(action, {})[predicate] = {"entailment": proved,
                                                                    "model": r["finite_model"][predicate]}
    return complete, disagreements


EVIDENCE = Path(os.environ.get("TMPDIR", "/tmp")) / "ve-agent-policy-evidence.json"


def base_summary(base):
    key = read_json("answer-key.json")
    complete, finite = finite_model_agreement(base)
    return {
        "inputs": {name: sha256(name) for name in ("policy.ve", "log.ve", "log-schema.ve", "answer-key.json")},
        "actions": {a: {k: r[k] for k in ("verdict", "permission", "obligation", "outcomes", "reported",
                                         "complete", "finite_model", "applies", "selected")}
                    | {"rule_25": rule_25(r)} for a, r in base["actions"].items()},
        "policy": base["policy"],
        "policy_summary": policy_summary(base["policy"]),
        "comparison": compare(base, key),
        "M8": {"finite_model_complete_records": complete, "finite_model_disagreements": finite,
               "reference_disagreements": reference_agreement(base)},
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("part", choices=("base", "mutants", "replay"),
                        help="base: every action and the policy findings; mutants: section 11; "
                             "replay: Lean and Rust replay of the evidence kept by the last base run")
    parser.add_argument("names", nargs="*", help="mutants to run (default: all)")
    parser.add_argument("--write", action="store_true", help="merge the part into results.json")
    args = parser.parse_args(argv)
    started = time.time()
    path = HERE / "results.json"
    results = json.loads(path.read_text()) if path.exists() else {}
    with multiprocessing.get_context("fork").Pool(WORKERS) as pool:
        if args.part == "base":
            evidence = Evidence(keep=True)
            base = run(evidence=evidence, pool=pool)
            part = base_summary(base)
            part["M10"] = {**evidence.counts, "seconds": round(time.time() - started, 1),
                           "workers": WORKERS, "rules": len(base["rules"]),
                           "log_sentences": sum(len(p.split("\n"))
                                                for p in (HERE / "log.ve").read_text().split("\n\n"))}
            EVIDENCE.write_text(json.dumps(evidence.exported))
            results.update(part)
        elif args.part == "mutants":
            evidence = Evidence()
            base = {"actions": results["actions"], "policy": results["policy"]}
            chosen = args.names or list(mutant_edits.MUTANTS)
            ran = run_mutants(base, evidence, pool=pool, names=chosen)
            results.setdefault("mutants", {}).update(
                {name: {"changes": m["changes"], "policy_summary": policy_summary(m["result"]["policy"]),
                        "seconds": m["result"]["seconds"]} for name, m in ran.items()})
        else:
            exported = json.loads(EVIDENCE.read_text())
            results["M9"] = {"lean_p0": replay_lean(exported), "rust_models": replay_rust(exported),
                             "lean_norms_route": lean_norms_route(policy(), *parse_log((HERE / "log.ve").read_text(), pool))}
    print(json.dumps({k: results.get(k) for k in ("comparison", "policy_summary", "M8", "M9", "M10")
                      if args.part != "mutants"} if args.part != "mutants" else results["mutants"],
                     indent=1, ensure_ascii=False)[:6000])
    print("seconds", round(time.time() - started, 1))
    if args.write:
        path.write_text(json.dumps(results, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
    return results


if __name__ == "__main__":
    main()
