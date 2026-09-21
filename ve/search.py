"""Bounded exhaustive finite countermodel search (an untrusted convenience)."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import math
from typing import Any, Iterator, Sequence

from .ast import check_formula
from .evaluate import evaluate
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

    def to_dict(self) -> dict[str, Any]:
        return {"status": self.status, "model": None if self.model is None else self.model.to_dict(),
                "models_checked": self.models_checked, "evaluations": self.evaluations,
                "max_domain_size": self.max_domain_size, "max_models": self.max_models, "detail": self.detail}


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
    values: list[bool] = []
    work = 0
    for formula in premises:
        result = evaluate(env, formula, model, max_evaluations=max_evaluations - work)
        work += result.evaluations
        if result.status == "ResourceLimit":
            return CountermodelCheck(False, tuple(values), None, work, env.environment_id, model.model_id, "ResourceLimit",
                                     tuple(meaning_id(env, x) for x in premises), meaning_id(env, conclusion))
        values.append(bool(result.value))
        if not result.value:
            return CountermodelCheck(False, tuple(values), None, work, env.environment_id, model.model_id, "NotCountermodel",
                                     tuple(meaning_id(env, x) for x in premises), meaning_id(env, conclusion))
    result = evaluate(env, conclusion, model, max_evaluations=max_evaluations - work)
    work += result.evaluations
    if result.status == "ResourceLimit":
        return CountermodelCheck(False, tuple(values), None, work, env.environment_id, model.model_id, "ResourceLimit",
                                 tuple(meaning_id(env, x) for x in premises), meaning_id(env, conclusion))
    valid = result.value is False
    return CountermodelCheck(valid, tuple(values), bool(result.value), work, env.environment_id, model.model_id,
                             "Valid" if valid else "NotCountermodel", tuple(meaning_id(env, x) for x in premises),
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


def _models(env: Any, maximum: int) -> Iterator[FiniteModel]:
    sorts = sorted(env.sorts)
    constants = sorted(env.constants)
    minimum = {sort: 0 for sort in sorts}
    for declaration in env.constants.values():
        minimum[declaration.sort] = 1
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


def find_countermodel(env: Any, premises: Sequence[Any], conclusion: Any, *, max_domain_size: int = 2,
                      max_models: int = 10_000, max_evaluations: int = 1_000_000) -> CountermodelResult:
    """Enumerate all models in the size bound until a countermodel or budget limit."""
    premises = _premises(premises)
    if any(type(x) is not int or x < 0 for x in (max_domain_size, max_models, max_evaluations)):
        raise ValueError("search bounds must be nonnegative integers")
    if max_evaluations > MAX_EVALUATIONS:
        raise ResourceLimit("Evaluation budget exceeds the v0 limit of 1,000,000 nodes")
    if max_domain_size > MAX_ENTITIES:
        raise ResourceLimit(f"max_domain_size cannot exceed {MAX_ENTITIES}")
    _check_aggregate_ast(premises, conclusion)
    for formula in premises:
        check_formula(env, formula)
    check_formula(env, conclusion)
    checked = work = 0
    iterator = _models(env, max_domain_size)
    while checked < max_models:
        try:
            model = next(iterator)
        except StopIteration:
            return CountermodelResult("NotFound", None, checked, work, max_domain_size, max_models,
                                      "all finite models within the domain bound were exhausted")
        except _SearchSpaceLimit:
            return CountermodelResult("ResourceLimit", None, checked, work, max_domain_size, max_models,
                                      "search relation atom space exceeds runtime limit")
        if work >= max_evaluations:
            return CountermodelResult("ResourceLimit", None, checked, work, max_domain_size, max_models,
                                      "evaluation budget exhausted")
        result = check_countermodel(env, premises, conclusion, model, max_evaluations=max_evaluations - work)
        checked += 1; work += result.evaluations
        if result.status == "ResourceLimit":
            return CountermodelResult("ResourceLimit", None, checked, work, max_domain_size, max_models,
                                      "evaluation budget exhausted")
        if result.valid:
            return CountermodelResult("Found", model, checked, work, max_domain_size, max_models)
    # Probe exhaustion once more; this validates but does not evaluate another model.
    try:
        next(iterator)
    except StopIteration:
        return CountermodelResult("NotFound", None, checked, work, max_domain_size, max_models,
                                  "all finite models within the domain bound were exhausted")
    except _SearchSpaceLimit:
        return CountermodelResult("ResourceLimit", None, checked, work, max_domain_size, max_models,
                                  "search relation atom space exceeds runtime limit")
    return CountermodelResult("ResourceLimit", None, checked, work, max_domain_size, max_models,
                              "model-attempt budget exhausted")
