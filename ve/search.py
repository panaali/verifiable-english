"""Bounded exhaustive finite countermodel search (an untrusted convenience)."""
from __future__ import annotations

from dataclasses import dataclass
from contextlib import contextmanager
from contextvars import ContextVar
from itertools import combinations, product, tee
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


_model_pool = ContextVar("ve_model_pool", default=None)


@dataclass(frozen=True, slots=True)
class _TerminalModelError:
    error: Exception


def _models_with_terminal_error(models):
    # tee buffers values but treats a source exception as exhaustion. Make the
    # failure a buffered value so every reader reaches the same terminal state.
    try:
        yield from models
    except Exception as exc:
        yield _TerminalModelError(exc)


def _read_shared_models(reader):
    for item in reader:
        if isinstance(item, _TerminalModelError):
            raise item.error
        yield item


@contextmanager
def model_search_scope():
    """Share an ordered model stream among queries in one document check."""
    token = _model_pool.set({})
    try:
        yield
    finally:
        _model_pool.reset(token)


def _query_models(env, minimum, maximum, used, formulas, *, defer_model_id):
    pool = _model_pool.get()
    if pool is None:
        return _models(env, minimum, maximum, used, formulas,
                       _defer_model_id=defer_model_id)
    # The formula key matters for order@0, whose candidate integer cells are
    # derived from the query. AST nodes are immutable value objects.
    key = (env.environment_id, minimum, maximum, used,
           formulas if getattr(env, "order", False) else (), defer_model_id)
    if key not in pool:
        pool[key] = _models_with_terminal_error(
            _models(env, minimum, maximum, used, formulas,
                    _defer_model_id=defer_model_id))
    pool[key], reader = tee(pool[key])
    return _read_shared_models(reader)


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
    from .backends.lean_runner import evaluation_case, lean_mode, run as lean_run
    from .backends.rust_jsonl import run as rust_run

    case = {"id": "countermodel", "environment": env.to_dict(),
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
        expected_premises = tuple(meaning_id(env, f) for f in premises)
        expected_conclusion = meaning_id(env, conclusion)
        if (row["environment_id"] != env.environment_id or row["model_id"] != model.model_id
                or tuple(row["premise_meaning_ids"]) != expected_premises
                or row["conclusion_meaning_id"] != expected_conclusion):
            raise CheckerUnavailable("CheckerUnavailable: Rust countermodel identity mismatch")
        return CountermodelCheck(row["valid"], tuple(row["premise_values"]),
                                 row["conclusion_value"], row["evaluations"],
                                 row["environment_id"], row["model_id"], row["status"],
                                 expected_premises, expected_conclusion)

    def lean():
        result = rust()
        if result.status == "ResourceLimit":
            return result
        request = {**case, "kind": "countermodel"}
        row = lean_run(lean_mode(env), [request])[0]
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
    base_predicates = set(env.predicates) - env.definition_entries.keys()
    regulated_pairs = tuple((name, decl.regulated.permission)
                            for name, decl in env.predicates.items()
                            if decl.regulated is not None and decl.regulated.permission is not None
                            and name in base_predicates and decl.regulated.permission in base_predicates)
    flagged = tuple((name, decl) for name, decl in env.predicates.items()
                    if name in base_predicates and (decl.functional or decl.total))
    for size in range(len(atoms) + 1):
        for subset in combinations(atoms, size):
            relations = {name: [] for name in sorted(env.predicates) if name not in env.definition_entries}
            for name, row in subset:
                relations[name].append(list(row))
            # These declarations are model-validity conditions. Filtering them
            # here preserves the order and count of models yielded by _models.
            if any(not {tuple(row) for row in relations[required]} <=
                   {tuple(row) for row in relations[permitted]}
                   for required, permitted in regulated_pairs):
                continue
            if any((decl.functional and len({row[0] for row in relations[name]}) != len(relations[name]))
                   or (decl.total and {row[0] for row in relations[name]} != set(domains[decl.arguments[0]]))
                   for name, decl in flagged):
                continue
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
# ResourceLimit details a Rust search reports exactly as Python does; other
# Rust details are reclassified from the counters.
_RUST_DETAILS = frozenset({"search relation atom space exceeds runtime limit",
                           "evaluation budget exhausted", "model-attempt budget exhausted"})


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
            used: frozenset[str], formulas=(), *, _defer_model_id=False) -> Iterator[FiniteModel]:
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
                                                      "constants": constant_map, "relations": relations},
                                                _defer_model_id=_defer_model_id)
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


def _witness_checked(env: Any, premises: tuple[Any, ...], conclusion: Any, model: FiniteModel,
                     max_evaluations: int) -> bool:
    """Search is untrusted generation: a candidate is reported as `Found` only
    once the countermodel.check verdict entry accepts it, so the witness carries
    that operation's authority (and a migrated check refuses rather than being
    bypassed). The check re-evaluates what the search already evaluated, within
    the caller's budget; its work is not charged to the public search counters.
    """
    return check_countermodel(env, premises, conclusion, model, max_evaluations=max_evaluations).valid


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


def _find_countermodel_python(env: Any, premises: Sequence[Any], conclusion: Any, *, max_domain_size: int = 2,
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
    iterator = _query_models(env, minimum_size, max_domain_size,
                             _used_predicates(*premises, conclusion, nonvacuous_for),
                             (*premises, conclusion, nonvacuous_for), defer_model_id=True)
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
            if not model.model_id:
                model = FiniteModel.from_dict(env, model.to_dict())
            if _witness_checked(env, premises, conclusion, model, max_evaluations):
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
def find_countermodel(env: Any, premises: Sequence[Any], conclusion: Any, *, max_domain_size: int = 2,
                      min_domain_size: int = 0, nonempty_domains: bool = False,
                      nonvacuous_for: Any | None = None, semantic_nonvacuity: bool = False,
                      max_models: int = 10_000,
                      max_evaluations: int = 1_000_000) -> CountermodelResult:
    """Search with a bounded Rust enumerator and Lean-checked witnesses."""
    from .ast import _to_data
    from .backends.dispatch import authority_for, execute
    from .backends.lean_runner import evaluation_case, lean_mode, run as lean_run
    from .backends.lean_service import CheckerUnavailable
    from .backends.rust_jsonl import run as rust_run
    from .profiles import require_checker

    if authority_for("countermodel_search") == "python":
        return _find_countermodel_python(
            env, premises, conclusion, max_domain_size=max_domain_size,
            min_domain_size=min_domain_size, nonempty_domains=nonempty_domains,
            nonvacuous_for=nonvacuous_for, semantic_nonvacuity=semantic_nonvacuity,
            max_models=max_models, max_evaluations=max_evaluations)

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
    case = {"id": "countermodel-search", "environment": env.to_dict(),
            "premises": [_to_data(f) for f in premises], "conclusion": _to_data(conclusion),
            "max_domain_size": max_domain_size, "min_domain_size": min_domain_size,
            "nonempty_domains": nonempty_domains, "max_models": max_models,
            "max_evaluations": max_evaluations,
            **({} if nonvacuous_for is None else
               {"nonvacuous_for": _to_data(nonvacuous_for),
                "semantic_nonvacuity": semantic_nonvacuity})}

    def python():
        return _find_countermodel_python(
            env, premises, conclusion, max_domain_size=max_domain_size,
            min_domain_size=min_domain_size, nonempty_domains=nonempty_domains,
            nonvacuous_for=nonvacuous_for, semantic_nonvacuity=semantic_nonvacuity,
            max_models=max_models, max_evaluations=max_evaluations)

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
                    semantic=semantic_nonvacuity)[0]:
                raise CheckerUnavailable("CheckerUnavailable: Rust witness violates non-vacuity")
            request = {**case, "kind": "countermodel", "model": model.to_dict()}
            checked = lean_run(lean_mode(env), [request])[0]
            if checked.get("refutes") is not True:
                raise CheckerUnavailable("CheckerUnavailable: Lean rejected Rust search witness")
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

    return execute("countermodel_search", case, python, lean=rust, rust=rust)


def _find_distinguishing_model_python(env: Any, a: Any, b: Any, *, max_domain_size: int = 2,
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
    iterator = _query_models(env, minimum_size, max_domain_size,
                             _used_predicates(a, b, nonvacuous_for), (a, b, nonvacuous_for),
                             defer_model_id=True)
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
            if not model.model_id:
                model = FiniteModel.from_dict(env, model.to_dict())
            if _witness_checked(env, *(((a,), b) if left.value else ((b,), a)),
                                model, max_evaluations):
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


@semantic_entry("countermodel.search")
def find_distinguishing_model(env: Any, a: Any, b: Any, *, max_domain_size: int = 2,
                              min_domain_size: int = 0, nonempty_domains: bool = False,
                              nonvacuous_for: Any | None = None, semantic_nonvacuity: bool = False,
                              max_models: int = 10_000,
                              max_evaluations: int = 1_000_000) -> CountermodelResult:
    """Find a bounded distinguishing witness with Rust; verify it in Lean."""
    from .ast import _to_data
    from .backends.dispatch import authority_for, execute
    from .backends.lean_runner import evaluation_case, lean_mode, run as lean_run
    from .backends.lean_service import CheckerUnavailable
    from .backends.rust_jsonl import run as rust_run
    from .profiles import require_checker

    def python():
        return _find_distinguishing_model_python(
            env, a, b, max_domain_size=max_domain_size,
            min_domain_size=min_domain_size, nonempty_domains=nonempty_domains,
            nonvacuous_for=nonvacuous_for, semantic_nonvacuity=semantic_nonvacuity,
            max_models=max_models, max_evaluations=max_evaluations)

    if authority_for("distinguishing_model") == "python":
        return python()
    require_checker(env)
    _validate_options(min_domain_size, max_domain_size, max_models, max_evaluations,
                      nonempty_domains, nonvacuous_for, semantic_nonvacuity)
    if _node_count(a) + _node_count(b) > MAX_NODES:
        raise ResourceLimit(f"formula pair exceeds aggregate {MAX_NODES}-node search limit")
    check_formula(env, a); check_formula(env, b)
    if nonvacuous_for is not None:
        check_formula(env, nonvacuous_for)
    case = {"id": "distinguishing-model", "kind": "distinguishing-model",
            "environment": env.to_dict(), "a": _to_data(a), "b": _to_data(b),
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
                    semantic=semantic_nonvacuity)[0]:
                raise CheckerUnavailable("CheckerUnavailable: Rust witness violates non-vacuity")
            mode, request = evaluation_case(env, case["id"], [case["a"], case["b"]], model.to_dict())
            checked = lean_run(mode, [request])[0]
            values = checked.get("values")
            if (type(values) is not list or len(values) != 2
                    or any(type(v) is not bool for v in values) or values[0] == values[1]):
                raise CheckerUnavailable("CheckerUnavailable: Lean rejected Rust distinguishing witness")
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

    return execute("distinguishing_model", case, python, lean=rust, rust=rust)
