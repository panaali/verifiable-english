"""Bounded finite countermodel search (an untrusted convenience).

Rust's search proposes (lean-first batch 15b: Rust keeps search only); Lean checks every
reported witness, its non-vacuity included, before it is reported.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from .assurance import semantic_entry
from .ast import (Reach, Named, Body, And, Atom, Binary, Exists, Forall, Implies, Not, Or, Unary,
                  check_formula)
from .evaluate import _evaluate_validated, _validate_model
from .model import FiniteModel
from .identity import meaning_id
from .limits import MAX_ENTITIES, MAX_EVALUATIONS, MAX_NODES
from .errors import CheckerUnavailable, ResourceLimit, VEError


def _node_count(root: Any) -> int:
    """Formula and term nodes as the type checker counts them: a Reach body
    edge's formula counts, the edge wrapper itself does not (Lean
    `formulaNodes`, Rust's shared checker)."""
    total, stack = 0, [root]
    while stack:
        node = stack.pop(); total += 1
        if total > MAX_NODES: break
        for field in ("body", "left", "right", "term"):
            child = getattr(node, field, None)
            if child is not None: stack.append(child)
        stack.extend(getattr(node, "terms", ()))
        edge = getattr(node, "edge", None)
        if type(edge) is Body:
            stack.append(edge.formula)
    return total


def _check_aggregate_ast(premises: Sequence[Any], conclusion: Any) -> None:
    if len(premises) > MAX_NODES:
        raise ResourceLimit("Premise count exceeds aggregate AST limit")
    if sum(_node_count(x) for x in (*premises, conclusion)) > MAX_NODES:
        raise ResourceLimit(f"premises and conclusion exceed aggregate {MAX_NODES}-node search limit")


def _premises(value):
    if not isinstance(value, Sequence):
        raise VEError("Premises must be an ordered sequence, not a consumable iterator")
    if len(value) > MAX_NODES:
        raise ResourceLimit("Premise count exceeds aggregate AST limit")
    return tuple(value)


@dataclass(frozen=True, slots=True)
class CountermodelResult:
    status: str
    model: FiniteModel | None
    models_checked: int
    evaluations: int
    max_domain_size: int
    max_models: int
    detail: str = ""
    min_domain_size: int = 0
    nonempty_domains: bool = False
    max_evaluations: int = MAX_EVALUATIONS
    nonvacuous_for_meaning_id: str | None = None
    semantic_nonvacuity: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {"status": self.status, "model": None if self.model is None else self.model.to_dict(),
                "models_checked": self.models_checked, "evaluations": self.evaluations,
                "min_domain_size": self.min_domain_size, "max_domain_size": self.max_domain_size,
                "nonempty_domains": self.nonempty_domains,
                "max_models": self.max_models, "max_evaluations": self.max_evaluations,
                "nonvacuous_for_meaning_id": self.nonvacuous_for_meaning_id,
                "semantic_nonvacuity": self.semantic_nonvacuity,
                "detail": self.detail}


@dataclass(frozen=True, slots=True)
class CountermodelCheck:
    valid: bool
    premise_values: tuple[bool, ...]
    conclusion_value: bool | None
    evaluations: int
    environment_id: str
    model_id: str
    status: str
    premise_meaning_ids: tuple[str, ...]
    conclusion_meaning_id: str


def _check_countermodel_values(premises: tuple[Any, ...], conclusion: Any,
                               model: FiniteModel, maximum: int):
    values: list[bool] = []
    work = 0
    for formula in premises:
        result = _evaluate_validated((formula,), model, max_evaluations=maximum - work)
        work += result.evaluations
        if result.status == "ResourceLimit":
            return False, tuple(values), None, work, "ResourceLimit"
        values.append(bool(result.value))
        if not result.value:
            return False, tuple(values), None, work, "NotCountermodel"
    result = _evaluate_validated((conclusion,), model, max_evaluations=maximum - work)
    work += result.evaluations
    if result.status == "ResourceLimit":
        return False, tuple(values), None, work, "ResourceLimit"
    valid = result.value is False
    return valid, tuple(values), bool(result.value), work, ("Valid" if valid else "NotCountermodel")


@semantic_entry("countermodel.check")
def check_countermodel(env: Any, premises: Sequence[Any], conclusion: Any, model: FiniteModel,
                       *, max_evaluations: int = 1_000_000) -> CountermodelCheck:
    """Independently validate and check a purported finite countermodel."""
    premises = _premises(premises)
    if type(max_evaluations) is not int or max_evaluations < 0:
        raise ValueError("max_evaluations must be a nonnegative integer")
    if max_evaluations > MAX_EVALUATIONS:
        raise ResourceLimit("Evaluation budget exceeds the v0 limit of 1,000,000 nodes")
    for formula in premises:
        check_formula(env, formula)
    check_formula(env, conclusion)
    _check_aggregate_ast(premises, conclusion)
    model = _validate_model(env, model)
    from .ast import _to_data
    from .backends.dispatch import execute
    from .backends.lean_service import CheckerUnavailable
    from .backends.lean_runner import lean_mode, cached_route_environment
    from .backends.relay import decide
    from .backends.rust_jsonl import run as rust_run, cached_rust_environment, soft_case

    case = {"id": "countermodel", "environment": cached_rust_environment(env), **soft_case(env),
            "premises": [_to_data(f) for f in premises], "conclusion": _to_data(conclusion),
            "model": model.to_dict(), "max_evaluations": max_evaluations}

    def python():
        valid, values, conclusion_value, work, status = _check_countermodel_values(
            premises, conclusion, model, max_evaluations)
        return CountermodelCheck(valid, values, conclusion_value, work, env.environment_id,
                                 model.model_id, status,
                                 tuple(meaning_id(env, x) for x in premises),
                                 meaning_id(env, conclusion))

    def rust():
        row = rust_run(case)
        # Rust binds its answer to the environment it was sent: `env` itself, or
        # without the statement-layer blocks Rust does not read (`rust_environment`).
        bound_env, bound_model = env, model
        if case["environment"] != env.to_dict():
            from .environment import Environment
            bound_env = Environment(case["environment"])
            bound_model = FiniteModel.from_dict(bound_env, model.to_dict())
        if (row["environment_id"] != bound_env.environment_id or row["model_id"] != bound_model.model_id
                or tuple(row["premise_meaning_ids"]) != tuple(meaning_id(bound_env, f) for f in premises)
                or row["conclusion_meaning_id"] != meaning_id(bound_env, conclusion)):
            raise CheckerUnavailable("CheckerUnavailable: Rust countermodel identity mismatch")
        return CountermodelCheck(row["valid"], tuple(row["premise_values"]),
                                 row["conclusion_value"], row["evaluations"],
                                 env.environment_id, model.model_id, row["status"],
                                 tuple(meaning_id(env, f) for f in premises), meaning_id(env, conclusion))

    def lean():
        result = rust()
        if result.status == "ResourceLimit":
            return result
        request = {**case, "kind": "countermodel", "environment": cached_route_environment(env)}
        row = decide(lean_mode(env), [request])[0]
        if row["refutes"] != result.valid:
            raise CheckerUnavailable("CheckerUnavailable: Lean and Rust countermodel checks disagree")
        return result

    return execute("countermodel_check", case, python, lean=lean, rust=rust)


def _used_predicates(*formulas: Any) -> frozenset[str]:
    from .surface.registry import by_node
    names, stack = set(), [f for f in formulas if f is not None]
    while stack:
        node = stack.pop()
        record = by_node(node)
        if record is not None and record.traversal_hooks is not None:
            hook = record.traversal_hooks.get("predicates")
            if hook is not None:
                found, children = hook(node)
                names.update(found)
                stack.extend(children)
                continue
        if isinstance(node, (Unary, Binary, Atom)):
            names.add(node.predicate)
        elif isinstance(node, Reach):
            if type(node.edge) is Named:
                names.add(node.edge.relation)
            else:
                stack.append(node.edge.formula)
        elif isinstance(node, (And, Or, Implies)):
            stack.extend((node.left, node.right))
        elif isinstance(node, (Not, Forall, Exists)):
            stack.append(node.body)
    return frozenset(names)


_RUST_DETAILS = frozenset({"search relation atom space exceeds runtime limit",
                           "evaluation budget exhausted", "model-attempt budget exhausted"})


def _witness_checked(env: Any, premises: tuple[Any, ...], conclusion: Any, model: FiniteModel,
                     max_evaluations: int) -> bool:
    """Search is untrusted generation: a candidate is reported as `Found` only
    once the countermodel.check verdict entry accepts it, so the witness carries
    that operation's authority (and a migrated check refuses rather than being
    bypassed). The entry is asked under Lean's authority whatever the run's
    authority: Lean checks every reported witness (lean-first batch 15b). The
    check re-evaluates what the search already evaluated, within the caller's
    budget; its work is not charged to the public search counters.
    """
    from .backends.dispatch import pinned
    with pinned("lean"):
        return check_countermodel(env, premises, conclusion, model, max_evaluations=max_evaluations).valid


def _nonvacuous(env: Any, formula: Any, model: FiniteModel, maximum: int, *,
                semantic: bool = False) -> bool:
    """Whether a search witness satisfies the non-vacuity condition, as Lean's
    `VE.Route.NonVacuity` decides it (`ve_metered`, case kind `non-vacuity`).

    Every encountered quantifier must have a nonempty domain and every
    implication a true antecedent at some assignment its enclosing quantifiers
    induce; semantic mode also treats the negated disjuncts of a maximal
    disjunction under a universal as a guard. An exhausted check is not a yes.
    """
    from .ast import _to_data
    from .backends import lean as lean_backend
    from .backends.lean_runner import METERED_EXECUTABLE, route_environment
    case = {"id": "non-vacuity", "kind": "non-vacuity", "environment": route_environment(env),
            "model": model.to_dict(), "formula": _to_data(formula), "max_evaluations": maximum,
            "semantic_nonvacuity": semantic}
    row = lean_backend.run("countermodel.search", METERED_EXECUTABLE, [case], runner="ve_metered",
                           timeout=lean_backend.configured_timeout(lean_backend.ROUTE_TIMEOUT))[0]
    if row["status"] != "ok":
        raise CheckerUnavailable(f"CheckerUnavailable: Lean refused a search witness's non-vacuity check: "
                                 f"{row['error']}")
    if not 0 <= row["evaluations"] <= maximum or row["suitable"] and row["exhausted"]:
        raise CheckerUnavailable("CheckerUnavailable: malformed Lean non-vacuity result")
    return row["suitable"] and not row["exhausted"]


def _validate_options(min_domain_size, max_domain_size, max_models, max_evaluations,
                      nonempty_domains, nonvacuous_for, semantic_nonvacuity):
    if any(type(x) is not int or x < 0
           for x in (min_domain_size, max_domain_size, max_models, max_evaluations)):
        raise ValueError("search bounds must be nonnegative integers")
    if type(nonempty_domains) is not bool or type(semantic_nonvacuity) is not bool:
        raise ValueError("nonempty_domains and semantic_nonvacuity must be booleans")
    if semantic_nonvacuity and nonvacuous_for is None:
        raise ValueError("semantic_nonvacuity requires nonvacuous_for")
    minimum_size = max(min_domain_size, 1 if nonempty_domains else 0)
    if minimum_size > max_domain_size:
        raise ValueError("min_domain_size cannot exceed max_domain_size")
    if max_evaluations > MAX_EVALUATIONS:
        raise ResourceLimit("Evaluation budget exceeds the v0 limit of 1,000,000 nodes")
    if max_domain_size > MAX_ENTITIES:
        raise ResourceLimit(f"max_domain_size cannot exceed {MAX_ENTITIES}")
    return minimum_size


@semantic_entry("countermodel.search")
def find_countermodel(env: Any, premises: Sequence[Any], conclusion: Any, *, max_domain_size: int = 2,
                      min_domain_size: int = 0, nonempty_domains: bool = False,
                      nonvacuous_for: Any | None = None, semantic_nonvacuity: bool = False,
                      max_models: int = 10_000,
                      max_evaluations: int = 1_000_000) -> CountermodelResult:
    """Search with a bounded Rust enumerator and Lean-checked witnesses."""
    from .ast import _to_data
    from .backends.dispatch import execute
    from .backends.rust_jsonl import run as rust_run, cached_rust_environment, soft_case
    from .profiles import require_checker

    premises = _premises(premises)
    require_checker(env)
    _validate_options(min_domain_size, max_domain_size, max_models, max_evaluations,
                      nonempty_domains, nonvacuous_for, semantic_nonvacuity)
    _check_aggregate_ast(premises, conclusion)
    for formula in premises:
        check_formula(env, formula)
    check_formula(env, conclusion)
    if nonvacuous_for is not None:
        check_formula(env, nonvacuous_for)
    case = {"id": "countermodel-search", "environment": cached_rust_environment(env), **soft_case(env),
            "premises": [_to_data(f) for f in premises], "conclusion": _to_data(conclusion),
            "max_domain_size": max_domain_size, "min_domain_size": min_domain_size,
            "nonempty_domains": nonempty_domains, "max_models": max_models,
            "max_evaluations": max_evaluations,
            **({} if nonvacuous_for is None else
               {"nonvacuous_for": _to_data(nonvacuous_for),
                "semantic_nonvacuity": semantic_nonvacuity})}

    def rust():
        row = rust_run(case)
        status = row.get("status")
        if (type(status) is not str or status not in {"Found", "NotFound", "ResourceLimit"}
                or type(row.get("models_checked")) is not int
                or type(row.get("evaluations")) is not int
                or not 0 <= row["models_checked"] <= max_models
                or not 0 <= row["evaluations"] <= max_evaluations):
            raise CheckerUnavailable("CheckerUnavailable: malformed Rust search result")
        model = None
        if status == "Found":
            if not isinstance(row.get("model"), dict):
                raise CheckerUnavailable("CheckerUnavailable: missing Rust search witness")
            try:
                model = FiniteModel.from_dict(env, row["model"])
            except VEError as exc:
                raise CheckerUnavailable(
                    f"CheckerUnavailable: invalid Rust search witness: {exc}") from exc
            if nonvacuous_for is not None and not _nonvacuous(
                    env, nonvacuous_for, model, max_evaluations,
                    semantic=semantic_nonvacuity):
                raise CheckerUnavailable("CheckerUnavailable: Rust witness violates non-vacuity")
            # A witness is published only through the countermodel.check entry
            # (_witness_checked), which carries that operation's authority.
            if not _witness_checked(env, premises, conclusion, model, max_evaluations):
                raise CheckerUnavailable("CheckerUnavailable: the countermodel check rejected "
                                         "the Rust search witness")
            detail = ""
        elif status == "NotFound":
            if row.get("model") is not None:
                raise CheckerUnavailable("CheckerUnavailable: unexpected Rust search witness")
            detail = ("all used-relation interpretations satisfying the non-vacuity constraints within the domain bound were exhausted"
                      if nonvacuous_for is not None else
                      "all used-relation interpretations within the domain bound were exhausted (unused predicates fixed empty)")
        elif row.get("detail") in _RUST_DETAILS:
            detail = row["detail"]
        elif row["models_checked"] >= max_models:
            detail = "model-attempt budget exhausted"
        elif row["evaluations"] >= max_evaluations:
            detail = "evaluation budget exhausted"
        else:
            detail = "model-attempt budget exhausted"
        return CountermodelResult(status, model, row["models_checked"], row["evaluations"],
                                  max_domain_size, max_models, detail, min_domain_size,
                                  nonempty_domains, max_evaluations,
                                  meaning_id(env, nonvacuous_for) if nonvacuous_for is not None else None,
                                  semantic_nonvacuity)

    # Python has no search of its own: every authority runs Rust's, with Lean-checked witnesses.
    return execute("countermodel_search", case, rust, lean=rust, rust=rust)


@semantic_entry("countermodel.search")
def find_distinguishing_model(env: Any, a: Any, b: Any, *, max_domain_size: int = 2,
                              min_domain_size: int = 0, nonempty_domains: bool = False,
                              nonvacuous_for: Any | None = None, semantic_nonvacuity: bool = False,
                              max_models: int = 10_000,
                              max_evaluations: int = 1_000_000) -> CountermodelResult:
    """Find a bounded distinguishing witness with Rust; verify it in Lean."""
    from .ast import _to_data
    from .backends.dispatch import execute
    from .backends.rust_jsonl import run as rust_run, cached_rust_environment, soft_case
    from .profiles import require_checker

    require_checker(env)
    _validate_options(min_domain_size, max_domain_size, max_models, max_evaluations,
                      nonempty_domains, nonvacuous_for, semantic_nonvacuity)
    if _node_count(a) + _node_count(b) > MAX_NODES:
        raise ResourceLimit(f"formula pair exceeds aggregate {MAX_NODES}-node search limit")
    check_formula(env, a); check_formula(env, b)
    if nonvacuous_for is not None:
        check_formula(env, nonvacuous_for)
    case = {"id": "distinguishing-model", "kind": "distinguishing-model", **soft_case(env),
            "environment": cached_rust_environment(env), "a": _to_data(a), "b": _to_data(b),
            "max_domain_size": max_domain_size, "min_domain_size": min_domain_size,
            "nonempty_domains": nonempty_domains, "max_models": max_models,
            "max_evaluations": max_evaluations,
            **({} if nonvacuous_for is None else
               {"nonvacuous_for": _to_data(nonvacuous_for),
                "semantic_nonvacuity": semantic_nonvacuity})}

    def rust():
        row = rust_run(case)
        status = row.get("status")
        if (type(status) is not str or status not in {"Found", "NotFound", "ResourceLimit"}
                or type(row.get("models_checked")) is not int
                or type(row.get("evaluations")) is not int
                or not 0 <= row["models_checked"] <= max_models
                or not 0 <= row["evaluations"] <= max_evaluations):
            raise CheckerUnavailable("CheckerUnavailable: malformed Rust distinguishing result")
        model = None
        if status == "Found":
            if not isinstance(row.get("model"), dict):
                raise CheckerUnavailable("CheckerUnavailable: missing Rust distinguishing witness")
            try:
                model = FiniteModel.from_dict(env, row["model"])
            except VEError as exc:
                raise CheckerUnavailable(
                    f"CheckerUnavailable: invalid Rust distinguishing witness: {exc}") from exc
            if nonvacuous_for is not None and not _nonvacuous(
                    env, nonvacuous_for, model, max_evaluations,
                    semantic=semantic_nonvacuity):
                raise CheckerUnavailable("CheckerUnavailable: Rust witness violates non-vacuity")
            # Either direction, as a countermodel to the other, through the
            # countermodel.check entry.
            if not (_witness_checked(env, (a,), b, model, max_evaluations)
                    or _witness_checked(env, (b,), a, model, max_evaluations)):
                raise CheckerUnavailable("CheckerUnavailable: the countermodel check rejected "
                                         "the Rust distinguishing witness")
            detail = ""
        elif status == "NotFound":
            if row.get("model") is not None:
                raise CheckerUnavailable("CheckerUnavailable: unexpected Rust distinguishing witness")
            detail = ("all used-relation interpretations satisfying the non-vacuity constraints within the domain bound were exhausted"
                      if nonvacuous_for is not None else
                      "all used-relation interpretations within the domain bound were exhausted (unused predicates fixed empty)")
        elif row.get("detail") in _RUST_DETAILS:
            detail = row["detail"]
        elif row["models_checked"] >= max_models:
            detail = "model-attempt budget exhausted"
        else:
            detail = "evaluation budget exhausted"
        return CountermodelResult(status, model, row["models_checked"], row["evaluations"],
                                  max_domain_size, max_models, detail, min_domain_size,
                                  nonempty_domains, max_evaluations,
                                  meaning_id(env, nonvacuous_for) if nonvacuous_for is not None else None,
                                  semantic_nonvacuity)

    return execute("distinguishing_model", case, rust, lean=rust, rust=rust)
