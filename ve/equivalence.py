"""Three-valued comparison: checked proofs, checked models, or UNKNOWN.

Bounds are per direction/search/replay, not a total wall-clock allowance. Finite
search exhaustion never certifies entailment. See docs/oracle.md for FO2 and the
operational non-vacuity criterion used by the experiment validators.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .assurance import semantic_entry
from .ast import (And, Binary, Bottom, Const, Document, Eq, Exists, Forall,
                  Formula, Implies, Not, Or, Top, Unary, Var, Reach, Body, check_formula)
from .entailment import check_entailment_certificate, prove_entailment
from .environment import validate_identifier
from .errors import ResourceLimit, VEError
from .evaluate import evaluate
from .identity import meaning_id
from .limits import MAX_DEPTH, MAX_ENTITIES, MAX_EVALUATIONS, MAX_NODES
from .model import FiniteModel
from .search import check_countermodel, find_countermodel

EQUIVALENT = "EQUIVALENT"
DIFFERENT = "DIFFERENT"
UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class Budgets:
    max_proof_steps: int = 10_000
    max_domain_size: int = 2
    max_models: int = 10_000
    max_evaluations: int = 100_000

    def __post_init__(self):
        if any(type(x) is not int or x < 0 for x in asdict(self).values()):
            raise ValueError("Oracle budgets must be nonnegative integers")
        if self.max_domain_size > MAX_ENTITIES or self.max_evaluations > MAX_EVALUATIONS:
            raise ValueError("Oracle budgets exceed the VE runtime envelope")

    def search_options(self):
        return {k: v for k, v in asdict(self).items() if k != "max_proof_steps"}


def _budgets(budgets):
    if budgets is None:
        return Budgets()
    if type(budgets) is dict:
        return Budgets(**budgets)
    if type(budgets) is not Budgets:
        raise TypeError("Expected Budgets or a budget-field dictionary")
    return budgets


@dataclass(frozen=True, slots=True)
class DirectionResult:
    status: str
    certificate: dict | None = None
    model: FiniteModel | None = None
    reason: str = ""
    attempts: tuple[dict, ...] = ()

    def to_dict(self):
        return {"status": self.status, "certificate": self.certificate,
                "model": self.model.to_dict() if self.model else None,
                "reason": self.reason, "attempts": list(self.attempts)}


@dataclass(frozen=True, slots=True)
class ComparisonResult:
    status: str
    a_implies_b: DirectionResult
    b_implies_a: DirectionResult
    environment_id: str
    a_meaning_id: str
    b_meaning_id: str
    reason: str = ""
    nonempty_sorts: tuple[str, ...] = ()
    nonempty_certificates: dict[str, dict] = field(default_factory=dict)

    @property
    def relation_detail(self):
        """A checked refinement, independent of the strict-strength relation."""
        if self.status == DIFFERENT and len(self.nonempty_certificates) == 2:
            return "differs_only_on_empty_sorts"
        return None

    @property
    def failed_directions(self):
        return tuple(label for label, direction in (
            ("a_not_implies_b", self.a_implies_b),
            ("b_not_implies_a", self.b_implies_a)) if direction.status == "COUNTERMODEL")

    @property
    def relation(self):
        """Strict strength of b relative to a; never inferred from search failure."""
        forward, reverse = self.a_implies_b.status, self.b_implies_a.status
        return {("ENTAILED", "ENTAILED"): "equivalent",
                ("ENTAILED", "COUNTERMODEL"): "weaker",
                ("COUNTERMODEL", "ENTAILED"): "stronger",
                ("COUNTERMODEL", "COUNTERMODEL"): "incomparable"}.get((forward, reverse), "unknown")

    @property
    def certificates(self):
        return {name: direction.certificate for name, direction in (
            ("a_implies_b", self.a_implies_b), ("b_implies_a", self.b_implies_a))
                if direction.certificate is not None}

    @property
    def models(self):
        return {name: direction.model for name, direction in (
            ("a_not_implies_b", self.a_implies_b), ("b_not_implies_a", self.b_implies_a))
                if direction.model is not None}

    def to_dict(self):
        return {"status": self.status, "relation": self.relation,
                "relation_detail": self.relation_detail,
                "nonempty_equivalence": ({"sorts": list(self.nonempty_sorts),
                    "certificates": self.nonempty_certificates}
                    if self.relation_detail else None),
                "failed_directions": list(self.failed_directions), "reason": self.reason,
                "environment_id": self.environment_id, "a_meaning_id": self.a_meaning_id,
                "b_meaning_id": self.b_meaning_id,
                "a_implies_b": self.a_implies_b.to_dict(),
                "b_implies_a": self.b_implies_a.to_dict()}


def _direction(env, a, b, budgets):
    attempts = []

    def proof_attempt(maximum):
        try:
            proof = prove_entailment(env, (a,), b, max_steps=maximum)
            attempts.append({"kind": "proof", "status": proof.status, "steps": proof.steps,
                             "detail": proof.detail})
            if proof.status == "Found":
                replay = check_entailment_certificate(env, (a,), b, proof.certificate,
                                                      max_steps=budgets.max_proof_steps)
                if replay.valid:
                    return DirectionResult("ENTAILED", certificate=proof.certificate,
                                           attempts=tuple(attempts)), proof.steps, False
                attempts.append({"kind": "replay", **replay.to_dict()})
            return None, proof.steps, proof.status == "ResourceLimit"
        except ResourceLimit as exc:
            attempts.append({"kind": "proof", "status": "ResourceLimit", "detail": str(exc)})
            return None, maximum, True

    # A satisfiable witness-generating branch must not monopolize comparison
    # before even a one-object distinguishing model gets a chance. Easy proofs
    # run first; model search then precedes the remaining aggregate proof budget.
    result, spent, exhausted = proof_attempt(min(128, budgets.max_proof_steps))
    if result is not None:
        return result
    try:
        found = find_countermodel(env, (a,), b, **budgets.search_options())
        attempts.append({"kind": "search", "status": found.status,
                         "models_checked": found.models_checked, "detail": found.detail})
        if found.status == "Found":
            checked = check_countermodel(env, (a,), b, found.model,
                                         max_evaluations=budgets.max_evaluations)
            # check_countermodel evaluates BOTH formulas, under this environment.
            if checked.valid and checked.premise_values == (True,) and checked.conclusion_value is False:
                return DirectionResult("COUNTERMODEL", model=found.model, attempts=tuple(attempts))
            attempts.append({"kind": "model_replay", "status": checked.status})
    except ResourceLimit as exc:
        attempts.append({"kind": "search", "status": "ResourceLimit", "detail": str(exc)})
    if exhausted and spent < budgets.max_proof_steps:
        result, _, _ = proof_attempt(budgets.max_proof_steps - spent)
        if result is not None:
            return result
    return DirectionResult(UNKNOWN, reason="No checked proof or countermodel within budgets",
                           attempts=tuple(attempts))


@semantic_entry("compare")
def compare(env, a: Formula, b: Formula, budgets: Budgets | dict | None = None) -> ComparisonResult:
    """Compare closed formulas in all VE structures, including allowed empty sorts.

    DIFFERENT needs only one checked countermodel; `relation` can still be
    unknown when the other direction is unresolved. EQUIVALENT always carries
    two replayed certificates, even for alpha-identical ASTs. Invalid inputs
    raise; exhausted valid searches return UNKNOWN, with a reason.
    """
    budgets = _budgets(budgets)
    from .backends.dispatch import composed, execute

    def run():
        return _compare(env, a, b, budgets)

    payload = {"environment": env, "a": a, "b": b, **asdict(budgets)}
    return execute("compare", payload, run, lean=composed("lean", run),
                   rust=composed("rust-experimental", run))


def _compare(env, a, b, budgets) -> ComparisonResult:
    """Python's two-clause rule over checked constituents (trusted, narrowed:
    SEMANTICS-MIGRATION-PLAN.md section 1.2)."""
    check_formula(env, a)
    check_formula(env, b)
    forward, reverse = _direction(env, a, b, budgets), _direction(env, b, a, budgets)
    statuses = (forward.status, reverse.status)
    status = (DIFFERENT if "COUNTERMODEL" in statuses else
              EQUIVALENT if statuses == ("ENTAILED", "ENTAILED") else UNKNOWN)
    reason = "" if status != UNKNOWN else "At least one implication remains unproved; no distinguishing model found"
    sorts, certificates = (), {}
    witnesses = [direction.model for direction in (forward, reverse) if direction.model is not None]
    if status == DIFFERENT and all(any(not domain for domain in model.domains.values())
                                   for model in witnesses):
        # A model proves a difference; bounded failure to find an inhabited
        # model proves nothing. Only two replayed conditional proofs justify
        # this refinement. These are ordinary certificates over extra premises.
        sorts = tuple(sorted(env.sorts))
        conditions = tuple(Exists(sort, Top()) for sort in sorts)
        for label, left, right in (("a_implies_b", a, b), ("b_implies_a", b, a)):
            try:
                proof = prove_entailment(env, (left, *conditions), right,
                                         max_steps=budgets.max_proof_steps)
                if proof.certificate is not None and check_entailment_certificate(
                        env, (left, *conditions), right, proof.certificate,
                        max_steps=budgets.max_proof_steps).valid:
                    certificates[label] = proof.certificate
            except ResourceLimit:
                pass
        if len(certificates) != 2:
            sorts, certificates = (), {}
    return ComparisonResult(status, forward, reverse, env.environment_id,
                            meaning_id(env, a), meaning_id(env, b), reason, sorts, certificates)


def is_weaker(env, candidate, reference, budgets=None) -> bool | None:
    """Is candidate strictly weaker than reference? None means undecided."""
    result = compare(env, reference, candidate, budgets)
    if result.a_implies_b.status == "COUNTERMODEL" or result.b_implies_a.status == "ENTAILED":
        return False
    return True if result.relation == "weaker" else None


def is_stronger(env, candidate, reference, budgets=None) -> bool | None:
    """Is candidate strictly stronger than reference? None means undecided."""
    result = compare(env, reference, candidate, budgets)
    if result.b_implies_a.status == "COUNTERMODEL" or result.a_implies_b.status == "ENTAILED":
        return False
    return True if result.relation == "stronger" else None


def in_two_variable_fragment(f: Formula | Document) -> bool:
    """Syntactic FO2 up to capture-avoiding variable renaming, not equivalence.

    Count live binder identities, not total quantifiers or De Bruijn indices.
    A binder, even a vacuous one, needs a name distinct from outer variables
    used in its body. Closed input only; this does not replace env type checking.
    """
    nodes = 0

    def term(t, bound):
        nonlocal nodes
        nodes += 1
        if nodes > MAX_NODES:
            raise ValueError("Fragment check exceeds AST envelope")
        if type(t) is Const and type(t.name) is str:
            validate_identifier(t.name)
            return set()
        if type(t) is Var and type(t.index) is int and 0 <= t.index < bound:
            return {t.index}
        raise ValueError("Malformed or open term")

    def walk(node, bound=0, depth=1):
        nonlocal nodes
        nodes += 1
        if nodes > MAX_NODES or depth > MAX_DEPTH:
            raise ValueError("Fragment check exceeds AST envelope")
        kind = type(node)
        if kind in (Unary, Binary):
            validate_identifier(node.predicate)
        if kind in (Exists, Forall):
            validate_identifier(node.sort)
        if kind in (Top, Bottom):
            free = set()
        elif kind is Unary:
            free = term(node.term, bound)
        elif kind in (Binary, Eq):
            free = term(node.left, bound) | term(node.right, bound)
        elif kind is Not:
            free = walk(node.body, bound, depth + 1)
        elif kind in (And, Or, Implies):
            free = walk(node.left, bound, depth + 1) | walk(node.right, bound, depth + 1)
        elif kind in (Exists, Forall):
            body = walk(node.body, bound + 1, depth + 1)
            if len(body | {0}) > 2:
                raise ValueError("Binder requires a third variable name")
            free = {i - 1 for i in body if i != 0}
        else:
            raise ValueError("Not a relational formula")
        if len(free) > 2:
            raise ValueError("Three simultaneously live variables")
        return free

    try:
        formulas = f.formulas if type(f) is Document else (f,)
        return bool(formulas) and all(not walk(x) for x in formulas)
    except (ValueError, VEError, RecursionError):
        return False


def non_vacuity_conditions(env, *formulas) -> tuple[Formula, ...]:
    """Inhabited sorts + an activating assignment for every implication guard.

    This declared, syntax-sensitive coverage criterion is deliberately stronger
    than non-emptiness. It is not a claim to decide relevance of arbitrary FOL.
    """
    conditions = [Exists(sort, Top()) for sort in env.sorts]

    def walk(f, binders=()):
        if type(f) is Implies:
            guard = f.left
            for sort in reversed(binders):
                guard = Exists(sort, guard)
            conditions.append(guard)
        if type(f) is Reach and type(f.edge) is Body:
            walk(f.edge.formula, binders + (f.edge.sort, f.edge.sort))
        elif type(f) in (Forall, Exists):
            walk(f.body, binders + (f.sort,))
        elif type(f) is Not:
            walk(f.body, binders)
        elif type(f) in (And, Or, Implies):
            walk(f.left, binders)
            walk(f.right, binders)

    for formula in formulas:
        check_formula(env, formula)
        walk(formula)
    return tuple(conditions)


def witness_quality(env, model, *formulas, budgets=None) -> dict[str, Any]:
    """Check non-vacuity conditions independently; budget exhaustion is unknown."""
    budgets = _budgets(budgets)
    non_empty = all(model.domains[s] for s in env.sorts)
    work = 0
    try:
        for condition in non_vacuity_conditions(env, *formulas):
            result = evaluate(env, condition, model, max_evaluations=budgets.max_evaluations - work)
            work += result.evaluations
            if result.value is None:
                return {"non_empty": non_empty, "non_vacuous": None, "reason": "Coverage evaluation budget exhausted"}
            if result.value is False:
                return {"non_empty": non_empty, "non_vacuous": False, "reason": "Empty sort or inactive implication antecedent"}
    except ResourceLimit as exc:
        return {"non_empty": non_empty, "non_vacuous": None, "reason": str(exc)}
    return {"non_empty": non_empty, "non_vacuous": True, "reason": "All sorts inhabited and all implication guards activated"}


@dataclass(frozen=True, slots=True)
class ReferenceValidation:
    status: str
    reason: str
    satisfying_model: FiniteModel | None = None
    falsifying_model: FiniteModel | None = None
    certificates: dict = field(default_factory=dict)
    attempts: tuple[dict, ...] = ()

    @property
    def valid(self):
        return self.status == "VALID"

    def to_dict(self):
        return {"status": self.status, "valid": self.valid, "reason": self.reason,
                "satisfying_model": self.satisfying_model.to_dict() if self.satisfying_model else None,
                "falsifying_model": self.falsifying_model.to_dict() if self.falsifying_model else None,
                "certificates": self.certificates, "attempts": list(self.attempts)}


@semantic_entry("reference.validate")
def validate_reference(env, f: Formula, budgets=None) -> ReferenceValidation:
    """Require a checked non-vacuous satisfying model and a falsifying model.

    INVALID requires a proof of validity, unsatisfiability, or impossibility of
    the declared non-vacuity conditions. Bounded absence is only UNKNOWN.
    """
    budgets = _budgets(budgets)
    check_formula(env, f)
    sat = falsifying = None
    attempts = []
    try:
        conditions = non_vacuity_conditions(env, f)
        for label, premises, conclusion in (
            ("non_vacuous_satisfying", (f, *conditions), Bottom()),
            ("falsifying", (), f),
        ):
            found = find_countermodel(env, premises, conclusion, **budgets.search_options())
            attempts.append({"kind": label, **found.to_dict()})
            if found.model is not None and check_countermodel(env, premises, conclusion, found.model,
                    max_evaluations=budgets.max_evaluations).valid:
                if label == "non_vacuous_satisfying":
                    sat = found.model
                else:
                    falsifying = found.model
        if sat is not None and falsifying is not None:
            return ReferenceValidation("VALID", "Checked non-vacuous satisfaction and non-validity",
                                       sat, falsifying, attempts=tuple(attempts))
        for label, premises, conclusion in (
            ("valid", (), f), ("unsatisfiable", (f,), Bottom()),
            ("no_non_vacuous_model", (f, *conditions), Bottom()),
        ):
            proof = prove_entailment(env, premises, conclusion, max_steps=budgets.max_proof_steps)
            attempts.append({"kind": label, "status": proof.status, "detail": proof.detail})
            if proof.certificate is not None and check_entailment_certificate(
                    env, premises, conclusion, proof.certificate, max_steps=budgets.max_proof_steps).valid:
                return ReferenceValidation("INVALID", label, sat, falsifying,
                                           {label: proof.certificate}, tuple(attempts))
    except ResourceLimit as exc:
        attempts.append({"kind": "validation", "status": "ResourceLimit", "detail": str(exc)})
    return ReferenceValidation(UNKNOWN, "Required reference witnesses not established within budgets",
                               sat, falsifying, attempts=tuple(attempts))
