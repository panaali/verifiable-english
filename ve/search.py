"""Bounded exhaustive finite countermodel search (an untrusted convenience)."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product
import math
from typing import Any, Iterator, Sequence

from .assurance import semantic_entry
from .ast import (Reach, Named, Body, And, Atom, Binary, Eq, Exists, Forall, Implies, Not, Or, Unary,
                  check_formula)
from .evaluate import (_Evaluator, _Exhausted, _evaluate_validated,
                       _validate_model)
from .model import FiniteModel
from .identity import meaning_id
from .limits import MAX_ENTITIES, MAX_EVALUATIONS, MAX_NODES, MAX_TUPLES
from .errors import InvalidModel, ResourceLimit, VEError


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
        stack.extend(getattr(node, "terms", ()))
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
    valid, values, conclusion_value, work, status = _check_countermodel_values(
        premises, conclusion, model, max_evaluations)
    return CountermodelCheck(valid, values, conclusion_value, work, env.environment_id,
                             model.model_id, status,
                             tuple(meaning_id(env, x) for x in premises),
                             meaning_id(env, conclusion))


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


def _subsets(domains: dict[str, list[str]], signature: tuple[str, ...]) -> Iterator[list[list[str]]]:
    """Stream relation subsets by increasing tuple count, then given domain order."""
    atoms = tuple(product(*(domains[s] for s in signature)))
    for size in range(min(len(atoms), MAX_TUPLES) + 1):
        for subset in combinations(atoms, size):
            yield [list(row) for row in subset]


def _relation_assignments(env: Any, domains: dict[str, list[str]],
                          used: frozenset[str]) -> Iterator[dict[str, list[list[str]]]]:
    # Tag atoms across relations so sparsity is GLOBAL, rather than exhausting
    # a dense final relation before trying the first atom of an earlier one.
    possible = sum(math.prod(len(domains[s]) for s in env.predicates[name].arguments)
                   for name in used)
    if possible > MAX_TUPLES:
        raise _SearchSpaceLimit
    atoms = tuple((name, row) for name in sorted(used)
                  for row in product(*(domains[s] for s in env.predicates[name].arguments)))
    for size in range(len(atoms) + 1):
        for subset in combinations(atoms, size):
            relations = {name: [] for name in sorted(env.predicates) if name not in env.definition_entries}
            for name, row in subset:
                relations[name].append(list(row))
            yield relations


def _domain_sizes(minima: list[int], maximum: int) -> Iterator[tuple[int, ...]]:
    """Stream bounded vectors by total entities, then lexicographically."""
    suffix_min = [0] * (len(minima) + 1)
    for index in range(len(minima) - 1, -1, -1):
        suffix_min[index] = minima[index] + suffix_min[index + 1]

    def walk(index, remaining, prefix):
        if index == len(minima):
            if remaining == 0:
                yield prefix
            return
        low = max(minima[index], remaining - maximum * (len(minima) - index - 1))
        high = min(maximum, remaining - suffix_min[index + 1])
        for size in range(low, high + 1):
            yield from walk(index + 1, remaining - size, (*prefix, size))

    for total in range(sum(minima), len(minima) * maximum + 1):
        yield from walk(0, total, ())


ORDER_SEARCH_MAGNITUDE = 3


def _int_terms(formulas, int_constants) -> tuple[list[Any], set[int]]:
    """Integer terms used as predicate arguments, and every numeral occurring."""
    from .ast import Num, Add, Scale, Lt, Le, Const, Var
    arguments, numerals, stack = [], set(), [f for f in formulas if f is not None]
    def term(t, argument):
        if argument and type(t) is not Var and not (type(t) is Const and t.name not in int_constants):
            arguments.append(t)
        inner = [t]
        while inner:
            node = inner.pop()
            if type(node) is Num:
                numerals.add(node.value)
            elif type(node) is Add:
                inner.extend((node.left, node.right))
            elif type(node) is Scale:
                numerals.add(node.coefficient)
                inner.append(node.term)
    while stack:
        node = stack.pop()
        if isinstance(node, Unary):
            term(node.term, True)
        elif isinstance(node, Binary):
            term(node.left, True); term(node.right, True)
        elif isinstance(node, Atom):
            for argument in node.terms:
                term(argument, True)
        elif isinstance(node, (Eq, Lt, Le)):
            term(node.left, False); term(node.right, False)
        elif isinstance(node, (And, Or, Implies)):
            stack.extend((node.left, node.right))
        elif isinstance(node, (Not, Forall, Exists)):
            stack.append(node.body)
    return arguments, numerals


def _int_value(term, numbers):
    from .ast import Num, Add, Scale
    if type(term) is Num:
        return term.value
    if type(term) is Add:
        return _int_value(term.left, numbers) + _int_value(term.right, numbers)
    if type(term) is Scale:
        return term.coefficient * _int_value(term.term, numbers)
    return numbers[term.name]


def _order_models(env: Any, minimum_size: int, maximum: int, used: frozenset[str],
                  formulas) -> Iterator[FiniteModel]:
    """order@0 candidates. Numerals are never enumerated or reassigned; integer
    constants range over a finite SEARCH set ([-B, B] plus every numeral and its
    neighbours), and integer relation cells over the values of the integer
    argument terms actually occurring. These are search bounds, not semantic
    integer bounds: exhaustion is NotFound, never entailment."""
    from .ast import INT_SORT
    sorts = sorted(env.model_sorts)
    constants = sorted(env.constants)
    int_constants = [c for c in constants if env.constants[c].sort == INT_SORT]
    object_constants = [c for c in constants if env.constants[c].sort != INT_SORT]
    arguments, numerals = _int_terms(formulas, frozenset(int_constants))
    values = set(range(-ORDER_SEARCH_MAGNITUDE, ORDER_SEARCH_MAGNITUDE + 1))
    for k in numerals:
        values.update((k - 1, k, k + 1))
    values = sorted(values, key=lambda v: (abs(v), v))
    minimum = {sort: minimum_size for sort in sorts}
    for name in object_constants:
        minimum[env.constants[name].sort] = max(minimum[env.constants[name].sort], 1)
    if "$string" in minimum:
        minimum["$string"] = max(minimum["$string"],
                                 sum(d.sort == "$string" for d in env.constants.values()))
    for sizes in _domain_sizes([minimum[s] for s in sorts], maximum):
        domains = {sort: [f"e{i}" for i in range(size)] for sort, size in zip(sorts, sizes, strict=True)}
        for assignment in product(values, repeat=len(int_constants)):
            numbers = dict(zip(int_constants, assignment, strict=True))
            cells = sorted({_int_value(t, numbers) for t in arguments}, key=lambda v: (abs(v), v))
            pools = {INT_SORT: cells, **domains}
            possible = sum(math.prod(len(pools[s]) for s in env.predicates[name].arguments)
                           for name in used)
            if possible > MAX_TUPLES:
                raise _SearchSpaceLimit
            atoms = tuple((name, row) for name in sorted(used)
                          for row in product(*(pools[s] for s in env.predicates[name].arguments)))
            choices = [domains[env.constants[name].sort] for name in object_constants]
            for size in range(len(atoms) + 1):
                for subset in combinations(atoms, size):
                    relations = {name: [] for name in sorted(env.predicates) if name not in env.definition_entries}
                    for name, row in subset:
                        relations[name].append([str(x) if type(x) is int else x for x in row])
                    for denotations in product(*choices):
                        constant_map = {name: str(value) for name, value in numbers.items()}
                        constant_map.update(zip(object_constants, denotations, strict=True))
                        try:
                            yield FiniteModel.from_dict(env, {"complete": True, "domains": domains,
                                                              "constants": constant_map,
                                                              "relations": relations})
                        except InvalidModel as exc:
                            if exc.generator is None:
                                raise


def _models(env: Any, minimum_size: int, maximum: int,
            used: frozenset[str], formulas=()) -> Iterator[FiniteModel]:
    used = used | frozenset(name for name, decl in env.predicates.items()
                            if decl.functional or decl.total)
    if env.definition_entries:
        from .definitions import _mentions
        from .ast import _Decoder
        relevant = set(used)
        pending = list(used)
        while pending:
            name = pending.pop()
            if name in env.definition_entries:
                for dependency in _mentions(_Decoder().decode(env.definition_entries[name]["body"])):
                    if dependency not in relevant:
                        relevant.add(dependency)
                        pending.append(dependency)
        used = frozenset(relevant - env.definition_entries.keys())
    if getattr(env, "order", False):
        yield from _order_models(env, minimum_size, maximum, used, formulas)
        return
    sorts = sorted(env.model_sorts)
    constants = sorted(env.constants)
    minimum = {sort: minimum_size for sort in sorts}
    for declaration in env.constants.values():
        minimum[declaration.sort] = max(minimum[declaration.sort], 1)
    if "$string" in minimum:
        minimum["$string"] = max(minimum["$string"],
                                 sum(d.sort == "$string" for d in env.constants.values()))
    for sizes in _domain_sizes([minimum[s] for s in sorts], maximum):
        domains = {sort: [f"e{i}" for i in range(size)] for sort, size in zip(sorts, sizes, strict=True)}
        choices = [domains[env.constants[name].sort] for name in constants]
        for relations in _relation_assignments(env, domains, used):
            for denotations in product(*choices):
                constant_map = dict(zip(constants, denotations, strict=True))
                try:
                    yield FiniteModel.from_dict(env, {"complete": True, "domains": domains,
                                                      "constants": constant_map, "relations": relations})
                except InvalidModel as exc:
                    if exc.generator is None:
                        raise


def _nonvacuous(env: Any, formula: Any, model: FiniteModel, maximum: int, *,
               semantic: bool = False) -> tuple[bool, int, bool]:
    """Check the conservative non-vacuity condition.

    Every encountered quantifier must have a nonempty domain.  Every implication
    occurrence must have a true antecedent for at least one assignment induced by
    its enclosing quantifiers.  An impossible antecedent therefore rejects the
    model rather than being guessed to be exempt. Semantic mode also recognizes
    maximal disjunctions under a universal: their negated disjuncts together
    form a guard, whose positive bodies must jointly hold at some assignment.
    """
    evaluator = _Evaluator(env, model, maximum, trace=False)
    guard_hits: dict[tuple[int, ...], bool] = {}
    ok = True

    def hit(guards, bindings, path):
        guard_hits.setdefault(path, False)
        value = True
        for guard in guards:
            result, _ = evaluator.formula(guard, bindings)
            value &= result
            if not value:
                break
        guard_hits[path] |= value

    def clause_guards(node):
        guards, stack = [], [node]
        while stack:
            disjunct = stack.pop()
            evaluator.tick()
            if isinstance(disjunct, Or):
                stack.extend((disjunct.right, disjunct.left))
            elif isinstance(disjunct, Not):
                guards.append(disjunct.body)
        return guards

    def walk(node: Any, bindings=(), path=(), universal=False, in_clause=False) -> None:
        nonlocal ok
        evaluator.tick()
        if isinstance(node, Implies):
            hit((node.left,), bindings, path)
            walk(node.left, bindings, path + (0,), universal)
            walk(node.right, bindings, path + (1,), universal)
        elif isinstance(node, (And, Or)):
            if semantic and universal and isinstance(node, Or) and not in_clause:
                guards = clause_guards(node)
                if guards:
                    hit(guards, bindings, path)
            for index, child in enumerate((node.left, node.right)):
                walk(child, bindings, path + (index,), universal, isinstance(node, Or))
        elif isinstance(node, Not):
            walk(node.body, bindings, path + (0,), universal)
        elif isinstance(node, (Forall, Exists)):
            domain = model.domains[node.sort]
            if not domain:
                ok = False
            for entity in domain:
                walk(node.body, ((node.sort, entity),) + bindings, path + (0,),
                     universal or isinstance(node, Forall))
        elif isinstance(node, (Unary, Binary, Atom, Eq)):
            return

    try:
        walk(formula)
    except _Exhausted:
        return False, evaluator.work, True
    return ok and all(guard_hits.values()), evaluator.work, False


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
    """Search used-relation interpretations; fix all unused predicates to empty."""
    premises = _premises(premises)
    from .profiles import require_checker
    require_checker(env)
    minimum_size = _validate_options(min_domain_size, max_domain_size, max_models,
                                     max_evaluations, nonempty_domains,
                                     nonvacuous_for, semantic_nonvacuity)
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
                                  max_evaluations, nonvacuous_id, semantic_nonvacuity)
    checked = work = 0
    iterator = _models(env, minimum_size, max_domain_size,
                       _used_predicates(*premises, conclusion, nonvacuous_for),
                       (*premises, conclusion, nonvacuous_for))
    while checked < max_models:
        try:
            model = next(iterator)
        except StopIteration:
            detail = ("all used-relation interpretations satisfying the non-vacuity constraints within the domain bound were exhausted"
                      if nonvacuous_for is not None else
                      "all used-relation interpretations within the domain bound were exhausted (unused predicates fixed empty)")
            return finish("NotFound", None, checked, work, detail)
        except _SearchSpaceLimit:
            return finish("ResourceLimit", None, checked, work,
                          "search relation atom space exceeds runtime limit")
        if work >= max_evaluations:
            return finish("ResourceLimit", None, checked, work, "evaluation budget exhausted")
        if nonvacuous_for is not None:
            suitable, used, exhausted = _nonvacuous(env, nonvacuous_for, model, max_evaluations - work,
                                                 semantic=semantic_nonvacuity)
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
        detail = ("all used-relation interpretations satisfying the non-vacuity constraints within the domain bound were exhausted"
                  if nonvacuous_for is not None else
                  "all used-relation interpretations within the domain bound were exhausted (unused predicates fixed empty)")
        return finish("NotFound", None, checked, work, detail)
    except _SearchSpaceLimit:
        return finish("ResourceLimit", None, checked, work,
                      "search relation atom space exceeds runtime limit")
    return finish("ResourceLimit", None, checked, work, "model-attempt budget exhausted")


@semantic_entry("countermodel.search")
def find_distinguishing_model(env: Any, a: Any, b: Any, *, max_domain_size: int = 2,
                              min_domain_size: int = 0, nonempty_domains: bool = False,
                              nonvacuous_for: Any | None = None, semantic_nonvacuity: bool = False,
                              max_models: int = 10_000,
                              max_evaluations: int = 1_000_000) -> CountermodelResult:
    """Find a bounded finite model on which two closed formulas differ."""
    from .profiles import require_checker
    require_checker(env)
    minimum_size = _validate_options(min_domain_size, max_domain_size, max_models,
                                     max_evaluations, nonempty_domains,
                                     nonvacuous_for, semantic_nonvacuity)
    if _node_count(a) + _node_count(b) > MAX_NODES:
        raise ResourceLimit(f"formula pair exceeds aggregate {MAX_NODES}-node search limit")
    check_formula(env, a); check_formula(env, b)
    if nonvacuous_for is not None:
        check_formula(env, nonvacuous_for)
    nonvacuous_id = meaning_id(env, nonvacuous_for) if nonvacuous_for is not None else None
    def finish(status, model, checked, work, detail=""):
        return CountermodelResult(status, model, checked, work, max_domain_size, max_models,
                                  detail, min_domain_size, nonempty_domains,
                                  max_evaluations, nonvacuous_id, semantic_nonvacuity)

    checked = work = 0
    iterator = _models(env, minimum_size, max_domain_size,
                       _used_predicates(a, b, nonvacuous_for), (a, b, nonvacuous_for))
    while checked < max_models:
        try:
            model = next(iterator)
        except StopIteration:
            detail = ("all used-relation interpretations satisfying the non-vacuity constraints within the domain bound were exhausted"
                      if nonvacuous_for is not None else
                      "all used-relation interpretations within the domain bound were exhausted (unused predicates fixed empty)")
            return finish("NotFound", None, checked, work, detail)
        except _SearchSpaceLimit:
            return finish("ResourceLimit", None, checked, work,
                          "search relation atom space exceeds runtime limit")
        if work >= max_evaluations:
            return finish("ResourceLimit", None, checked, work, "evaluation budget exhausted")
        if nonvacuous_for is not None:
            suitable, used, exhausted = _nonvacuous(env, nonvacuous_for, model, max_evaluations - work,
                                                 semantic=semantic_nonvacuity)
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
        detail = ("all used-relation interpretations satisfying the non-vacuity constraints within the domain bound were exhausted"
                  if nonvacuous_for is not None else
                  "all used-relation interpretations within the domain bound were exhausted (unused predicates fixed empty)")
        return finish("NotFound", None, checked, work, detail)
    except _SearchSpaceLimit:
        return finish("ResourceLimit", None, checked, work,
                      "search relation atom space exceeds runtime limit")
    return finish("ResourceLimit", None, checked, work, "model-attempt budget exhausted")
