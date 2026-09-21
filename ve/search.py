"""Bounded exhaustive finite countermodel search (an untrusted convenience)."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import math
from typing import Any, Iterator, Sequence

from .ast import (And, Binary, Eq, Exists, Forall, Implies, Not, Or, Unary,
                  check_formula)
from .evaluate import (_Evaluator, _Exhausted, _evaluate_validated,
                       _validate_model)
from .model import FiniteModel
from .identity import meaning_id
from .limits import MAX_ENTITIES, MAX_EVALUATIONS, MAX_NODES, MAX_TUPLES
from .errors import ResourceLimit, VEError


class _SearchSpaceLimit(Exception):
    pass


def _node_count(root: Any) -> int:
    total, stack = 0, [root]
    while stack:
        node = stack.pop(); total += 1
        if total > MAX_NODES: break
        for field in ("body", "left", "right", "term"):
            child = getattr(node, field, None)
            if child is not None: stack.append(child)
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

    def to_dict(self) -> dict[str, Any]:
        return {"status": self.status, "model": None if self.model is None else self.model.to_dict(),
                "models_checked": self.models_checked, "evaluations": self.evaluations,
                "min_domain_size": self.min_domain_size, "max_domain_size": self.max_domain_size,
                "nonempty_domains": self.nonempty_domains,
                "max_models": self.max_models, "max_evaluations": self.max_evaluations,
                "nonvacuous_for_meaning_id": self.nonvacuous_for_meaning_id,
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
    valid, values, conclusion_value, work, status = _check_countermodel_values(
        premises, conclusion, model, max_evaluations)
    return CountermodelCheck(valid, values, conclusion_value, work, env.environment_id,
                             model.model_id, status,
                             tuple(meaning_id(env, x) for x in premises),
                             meaning_id(env, conclusion))


def _subsets(domains: dict[str, list[str]], signature: tuple[str, ...]) -> Iterator[list[list[str]]]:
    """Stream every subset, regenerating polynomial atoms for each bit mask."""
    atom_count = 1
    for sort in signature:
        atom_count *= len(domains[sort])
    for mask in range(1 << atom_count):
        if mask.bit_count() > MAX_TUPLES:
            continue
        rows: list[list[str]] = []
        bits = mask
        while bits:
            low = bits & -bits
            index = low.bit_length() - 1
            row = [""] * len(signature)
            for position in range(len(signature) - 1, -1, -1):
                domain = domains[signature[position]]
                index, offset = divmod(index, len(domain))
                row[position] = domain[offset]
            rows.append(row)
            bits ^= low
        yield rows


def _relation_assignments(env: Any, domains: dict[str, list[str]]) -> Iterator[dict[str, list[list[str]]]]:
    names = sorted(env.predicates)
    current: dict[str, list[list[str]]] = {}
    def walk(index: int) -> Iterator[dict[str, list[list[str]]]]:
        if index == len(names):
            yield {k: v for k, v in current.items()}
            return
        name = names[index]
        signature = env.predicates[name].arguments
        prior_total = sum(len(rows) for key, rows in current.items() if key != name)
        for subset in _subsets(domains, signature):
            if len(subset) + prior_total > MAX_TUPLES:
                continue
            current[name] = subset
            yield from walk(index + 1)
        current.pop(name, None)
    yield from walk(0)


def _models(env: Any, minimum_size: int, maximum: int) -> Iterator[FiniteModel]:
    sorts = sorted(env.sorts)
    constants = sorted(env.constants)
    minimum = {sort: minimum_size for sort in sorts}
    for declaration in env.constants.values():
        minimum[declaration.sort] = max(minimum[declaration.sort], 1)
    ranges = [range(minimum[s], maximum + 1) for s in sorts]
    for sizes in product(*ranges):
        domains = {sort: [f"e{i}" for i in range(size)] for sort, size in zip(sorts, sizes, strict=True)}
        possible_atoms = sum(math.prod(len(domains[s]) for s in p.arguments)
                             for p in env.predicates.values())
        if possible_atoms > MAX_TUPLES:
            raise _SearchSpaceLimit
        choices = [domains[env.constants[name].sort] for name in constants]
        for denotations in product(*choices):
            constant_map = dict(zip(constants, denotations, strict=True))
            for relations in _relation_assignments(env, domains):
                yield FiniteModel.from_dict(env, {"complete": True, "domains": domains,
                                                  "constants": constant_map, "relations": relations})


def _nonvacuous(env: Any, formula: Any, model: FiniteModel, maximum: int) -> tuple[bool, int, bool]:
    """Check the conservative non-vacuity condition.

    Every encountered quantifier must have a nonempty domain.  Every implication
    occurrence must have a true antecedent for at least one assignment induced by
    its enclosing quantifiers.  An impossible antecedent therefore rejects the
    model rather than being guessed to be exempt.
    """
    evaluator = _Evaluator(env, model, maximum, trace=False)
    implication_hits: dict[tuple[int, ...], bool] = {}
    ok = True

    def walk(node: Any, bindings=(), path=()) -> None:
        nonlocal ok
        evaluator.tick()
        if isinstance(node, Implies):
            key = path
            implication_hits.setdefault(key, False)
            value, _ = evaluator.formula(node.left, bindings)
            implication_hits[key] |= value
            walk(node.left, bindings, path + (0,)); walk(node.right, bindings, path + (1,))
        elif isinstance(node, (And, Or)):
            walk(node.left, bindings, path + (0,)); walk(node.right, bindings, path + (1,))
        elif isinstance(node, Not):
            walk(node.body, bindings, path + (0,))
        elif isinstance(node, (Forall, Exists)):
            domain = model.domains[node.sort]
            if not domain:
                ok = False
            for entity in domain:
                walk(node.body, ((node.sort, entity),) + bindings, path + (0,))
        elif isinstance(node, (Unary, Binary, Eq)):
            return

    try:
        walk(formula)
    except _Exhausted:
        return False, evaluator.work, True
    return ok and all(implication_hits.values()), evaluator.work, False


def find_countermodel(env: Any, premises: Sequence[Any], conclusion: Any, *, max_domain_size: int = 2,
                      min_domain_size: int = 0, nonempty_domains: bool = False,
                      nonvacuous_for: Any | None = None, max_models: int = 10_000,
                      max_evaluations: int = 1_000_000) -> CountermodelResult:
    """Enumerate all models in the size bound until a countermodel or budget limit."""
    premises = _premises(premises)
    if any(type(x) is not int or isinstance(x, bool) or x < 0
           for x in (min_domain_size, max_domain_size, max_models, max_evaluations)):
        raise ValueError("search bounds must be nonnegative integers")
    if type(nonempty_domains) is not bool:
        raise ValueError("nonempty_domains must be a boolean")
    minimum_size = max(min_domain_size, 1 if nonempty_domains else 0)
    if minimum_size > max_domain_size:
        raise ValueError("min_domain_size cannot exceed max_domain_size")
    if max_evaluations > MAX_EVALUATIONS:
        raise ResourceLimit("Evaluation budget exceeds the v0 limit of 1,000,000 nodes")
    if max_domain_size > MAX_ENTITIES:
        raise ResourceLimit(f"max_domain_size cannot exceed {MAX_ENTITIES}")
    _check_aggregate_ast(premises, conclusion)
    for formula in premises:
        check_formula(env, formula)
    check_formula(env, conclusion)
    if nonvacuous_for is not None:
        check_formula(env, nonvacuous_for)
    nonvacuous_id = meaning_id(env, nonvacuous_for) if nonvacuous_for is not None else None
    def finish(status, model, checked, work, detail=""):
        return CountermodelResult(status, model, checked, work, max_domain_size, max_models,
                                  detail, min_domain_size, nonempty_domains,
                                  max_evaluations, nonvacuous_id)
    checked = work = 0
    iterator = _models(env, minimum_size, max_domain_size)
    while checked < max_models:
        try:
            model = next(iterator)
        except StopIteration:
            detail = ("all finite models satisfying the non-vacuity constraints within the domain bound were exhausted"
                      if nonvacuous_for is not None else
                      "all finite models within the domain bound were exhausted")
            return finish("NotFound", None, checked, work, detail)
        except _SearchSpaceLimit:
            return finish("ResourceLimit", None, checked, work,
                          "search relation atom space exceeds runtime limit")
        if work >= max_evaluations:
            return finish("ResourceLimit", None, checked, work, "evaluation budget exhausted")
        if nonvacuous_for is not None:
            suitable, used, exhausted = _nonvacuous(env, nonvacuous_for, model, max_evaluations - work)
            work += used
            if exhausted:
                return finish("ResourceLimit", None, checked + 1, work, "evaluation budget exhausted")
            if not suitable:
                checked += 1
                continue
        valid, _, _, used, status = _check_countermodel_values(
            premises, conclusion, model, max_evaluations - work)
        checked += 1; work += used
        if status == "ResourceLimit":
            return finish("ResourceLimit", None, checked, work, "evaluation budget exhausted")
        if valid:
            return finish("Found", model, checked, work)
    # Probe exhaustion once more; this validates but does not evaluate another model.
    try:
        next(iterator)
    except StopIteration:
        detail = ("all finite models satisfying the non-vacuity constraints within the domain bound were exhausted"
                  if nonvacuous_for is not None else
                  "all finite models within the domain bound were exhausted")
        return finish("NotFound", None, checked, work, detail)
    except _SearchSpaceLimit:
        return finish("ResourceLimit", None, checked, work,
                      "search relation atom space exceeds runtime limit")
    return finish("ResourceLimit", None, checked, work, "model-attempt budget exhausted")


def find_distinguishing_model(env: Any, a: Any, b: Any, *, max_domain_size: int = 2,
                              min_domain_size: int = 0, nonempty_domains: bool = False,
                              nonvacuous_for: Any | None = None, max_models: int = 10_000,
                              max_evaluations: int = 1_000_000) -> CountermodelResult:
    """Find a bounded finite model on which two closed formulas differ."""
    if any(type(x) is not int or isinstance(x, bool) or x < 0
           for x in (min_domain_size, max_domain_size, max_models, max_evaluations)):
        raise ValueError("search bounds must be nonnegative integers")
    if type(nonempty_domains) is not bool:
        raise ValueError("nonempty_domains must be a boolean")
    minimum_size = max(min_domain_size, 1 if nonempty_domains else 0)
    if minimum_size > max_domain_size:
        raise ValueError("min_domain_size cannot exceed max_domain_size")
    if max_evaluations > MAX_EVALUATIONS:
        raise ResourceLimit("Evaluation budget exceeds the v0 limit of 1,000,000 nodes")
    if max_domain_size > MAX_ENTITIES:
        raise ResourceLimit(f"max_domain_size cannot exceed {MAX_ENTITIES}")
    if _node_count(a) + _node_count(b) > MAX_NODES:
        raise ResourceLimit(f"formula pair exceeds aggregate {MAX_NODES}-node search limit")
    check_formula(env, a); check_formula(env, b)
    if nonvacuous_for is not None:
        check_formula(env, nonvacuous_for)
    nonvacuous_id = meaning_id(env, nonvacuous_for) if nonvacuous_for is not None else None
    def finish(status, model, checked, work, detail=""):
        return CountermodelResult(status, model, checked, work, max_domain_size, max_models,
                                  detail, min_domain_size, nonempty_domains,
                                  max_evaluations, nonvacuous_id)

    checked = work = 0
    iterator = _models(env, minimum_size, max_domain_size)
    while checked < max_models:
        try:
            model = next(iterator)
        except StopIteration:
            detail = ("all finite models satisfying the non-vacuity constraints within the domain bound were exhausted"
                      if nonvacuous_for is not None else
                      "all finite models within the domain bound were exhausted")
            return finish("NotFound", None, checked, work, detail)
        except _SearchSpaceLimit:
            return finish("ResourceLimit", None, checked, work,
                          "search relation atom space exceeds runtime limit")
        if work >= max_evaluations:
            return finish("ResourceLimit", None, checked, work, "evaluation budget exhausted")
        if nonvacuous_for is not None:
            suitable, used, exhausted = _nonvacuous(env, nonvacuous_for, model, max_evaluations - work)
            work += used
            if exhausted:
                return finish("ResourceLimit", None, checked + 1, work, "evaluation budget exhausted")
            if not suitable:
                checked += 1
                continue
        left = _evaluate_validated((a,), model, max_evaluations=max_evaluations - work)
        work += left.evaluations
        if left.status == "ResourceLimit":
            return finish("ResourceLimit", None, checked + 1, work, "evaluation budget exhausted")
        right = _evaluate_validated((b,), model, max_evaluations=max_evaluations - work)
        work += right.evaluations; checked += 1
        if right.status == "ResourceLimit":
            return finish("ResourceLimit", None, checked, work, "evaluation budget exhausted")
        if left.value != right.value:
            return finish("Found", model, checked, work)
    try:
        next(iterator)
    except StopIteration:
        detail = ("all finite models satisfying the non-vacuity constraints within the domain bound were exhausted"
                  if nonvacuous_for is not None else
                  "all finite models within the domain bound were exhausted")
        return finish("NotFound", None, checked, work, detail)
    except _SearchSpaceLimit:
        return finish("ResourceLimit", None, checked, work,
                      "search relation atom space exceeds runtime limit")
    return finish("ResourceLimit", None, checked, work, "model-attempt budget exhausted")
