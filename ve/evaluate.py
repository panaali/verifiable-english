"""Small trusted finite-model evaluator with bounded explanatory traces."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .assurance import semantic_entry
from .ast import (And, Atom, Binary, Bottom, Const, Document, Eq, Exists, Forall,
                  Implies, Not, Or, Top, Unary, Var, Reach, Named, Body, check_document, check_formula,
                  Num, Add, Scale, Lt, Le)
from .model import FiniteModel
from .errors import CheckerUnavailable, InvalidModel, ResourceLimit, VEError
from .limits import MAX_EVALUATIONS


@dataclass(frozen=True, slots=True)
class Explanation:
    kind: str
    value: bool | None
    bindings: tuple[tuple[str, str], ...] = ()
    detail: str = ""
    children: tuple["Explanation", ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "value": self.value,
                "bindings": [{"debruijn_index": i, "sort": sort, "local_id": value}
                             for i, (sort, value) in enumerate(self.bindings)],
                "detail": self.detail, "children": [x.to_dict() for x in self.children]}


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    status: str
    value: bool | None
    explanation: Explanation | None
    evaluations: int

    def to_dict(self) -> dict[str, Any]:
        return {"status": self.status, "value": self.value, "evaluations": self.evaluations,
                "explanation": None if self.explanation is None else self.explanation.to_dict()}


class _Exhausted(Exception):
    pass


class _Evaluator:
    def __init__(self, env: Any, model: FiniteModel, maximum: int, trace: bool = True):
        self.env, self.model, self.maximum, self.work, self.trace = env, model, maximum, 0, trace
        self.closures = {}  # scoped to this exact model; outer bindings are part of each key

    def explanation(self, kind: str, value: bool | None, bindings=(), detail: str = "", children=()):
        if not self.trace:
            return None
        return Explanation(kind, value, bindings, detail, tuple(x for x in children if x is not None))

    def tick(self) -> None:
        if self.work >= self.maximum:
            raise _Exhausted
        self.work += 1

    def term(self, term: Any, bindings: tuple[tuple[str, str], ...]) -> str:
        if isinstance(term, Var):
            return bindings[term.index][1]
        if isinstance(term, Const):
            return self.model.constants[term.name]
        if isinstance(term, Num):
            return term.value
        if isinstance(term, Add):
            return self.term(term.left, bindings) + self.term(term.right, bindings)
        if isinstance(term, Scale):
            return term.coefficient * self.term(term.term, bindings)
        raise TypeError(f"unknown term node {type(term).__name__}")

    def formula(self, f: Any, bindings: tuple[tuple[str, str], ...] = ()) -> tuple[bool, Explanation | None]:
        self.tick()
        shown = bindings
        if isinstance(f, Top): return True, self.explanation("top", True, shown)
        if isinstance(f, Bottom): return False, self.explanation("bottom", False, shown)
        if isinstance(f, Unary):
            row = (self.term(f.term, bindings),); value = row in self.model.relations[f.predicate]
            return value, self.explanation("unary", value, shown, f"{f.predicate}{row}")
        if isinstance(f, Binary):
            row = (self.term(f.left, bindings), self.term(f.right, bindings)); value = row in self.model.relations[f.predicate]
            return value, self.explanation("binary", value, shown, f"{f.predicate}{row}")
        if isinstance(f, Atom):
            row = tuple(self.term(t, bindings) for t in f.terms)
            value = row in self.model.relations[f.predicate]
            return value, self.explanation("atom", value, shown, f"{f.predicate}{row}")
        if isinstance(f, Reach):
            key = (f.edge, bindings)
            if key not in self.closures:
                if type(f.edge) is Named:
                    edges = set()
                    for row in self.model.relations[f.edge.relation]:
                        self.tick()
                        edges.add(row)
                    domain = sorted({x for pair in edges for x in pair})
                else:
                    domain = self.model.domains[f.edge.sort]
                    edges = set()
                    for x in domain:
                        for y in domain:
                            value, _ = self.formula(f.edge.formula,
                                ((f.edge.sort, y), (f.edge.sort, x)) + bindings)
                            if value:
                                edges.add((x, y))
                # Materialize each Warshall pivot; identity is never seeded for plus.
                for pivot in domain:
                    incoming, outgoing = [], []
                    for x in domain:
                        self.tick()
                        if (x, pivot) in edges:
                            incoming.append(x)
                        if (pivot, x) in edges:
                            outgoing.append(x)
                    for x in incoming:
                        for y in outgoing:
                            self.tick()
                            edges.add((x, y))
                self.closures[key] = edges
            left, right = self.term(f.left, bindings), self.term(f.right, bindings)
            value = (f.kind == "star" and left == right) or (left, right) in self.closures[key]
            return value, self.explanation("reach", value, shown,
                f"{f.kind}: {left} to {right}; finite directed paths")
        if isinstance(f, (Lt, Le)):
            left, right = self.term(f.left, bindings), self.term(f.right, bindings)
            value = left < right if isinstance(f, Lt) else left <= right
            return value, self.explanation("comparison", value, shown,
                f"{left} {'<' if isinstance(f, Lt) else '<='} {right}")
        if isinstance(f, Eq):
            left, right = self.term(f.left, bindings), self.term(f.right, bindings); value = left == right
            return value, self.explanation("equality", value, shown, f"{left} equals {right}")
        if isinstance(f, Not):
            v, c = self.formula(f.body, bindings); return not v, self.explanation("not", not v, shown, children=(c,))
        if isinstance(f, (And, Or, Implies)):
            lv, le = self.formula(f.left, bindings)
            if isinstance(f, And) and not lv:
                return False, self.explanation("and", False, shown, "right branch not needed", (le,))
            if isinstance(f, Or) and lv:
                return True, self.explanation("or", True, shown, "right branch not needed", (le,))
            if isinstance(f, Implies) and not lv:
                return True, self.explanation("implies", True, shown, "vacuously true: antecedent is false", (le,))
            rv, re = self.formula(f.right, bindings)
            value = (lv and rv) if isinstance(f, And) else ((lv or rv) if isinstance(f, Or) else rv)
            return value, self.explanation(type(f).__name__.lower(), value, shown, children=(le, re))
        if isinstance(f, (Forall, Exists)):
            domain = self.model.domains[f.sort]
            kind = "forall" if isinstance(f, Forall) else "exists"
            if not domain:
                value = isinstance(f, Forall)
                detail = "vacuously true: domain is empty" if value else "false: domain is empty"
                return value, self.explanation(kind, value, shown, detail)
            children: list[Explanation] = []
            for entity in domain:
                value, child = self.formula(f.body, ((f.sort, entity),) + bindings)
                if child is not None:
                    children.append(child)
                if isinstance(f, Forall) and not value:
                    return False, self.explanation(kind, False, shown, f"counterexample {entity}", children)
                if isinstance(f, Exists) and value:
                    return True, self.explanation(kind, True, shown, f"witness {entity}", children)
            value = isinstance(f, Forall)
            return value, self.explanation(kind, value, shown, "all entities checked" if value else "no witness", children)
        raise TypeError(f"unknown formula node {type(f).__name__}")


def _validate_model(env: Any, model: FiniteModel) -> FiniteModel:
    if type(model) is not FiniteModel:
        raise InvalidModel("expected a validated FiniteModel")
    try:
        # The selected authority decides the model's validity, Background
        # included, and whether its claimed identities are the recomputed ones.
        return FiniteModel.from_dict(env, model.to_dict(), _claimed={
            "environment_id": model.environment_id, "model_id": model.model_id})
    except VEError:
        raise
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        raise InvalidModel("malformed FiniteModel object") from exc


def _evaluate_validated(formulas: tuple[Any, ...], model: FiniteModel, *,
                        max_evaluations: int, max_trace_nodes: int = 10_000,
                        trace: bool = False) -> EvaluationResult:
    """Evaluate already-checked formulas against an already-validated model."""
    evaluator = _Evaluator(None, model, min(max_evaluations, max_trace_nodes) if trace else max_evaluations, trace)
    children: list[Explanation] = []
    try:
        for index, formula in enumerate(formulas):
            result, child_trace = evaluator.formula(formula)
            if child_trace is not None:
                children.append(child_trace)
            if not result:
                root = (Explanation("document", False, detail=f"statement {index + 1} violated", children=tuple(children))
                        if trace else None)
                return EvaluationResult("Violated", False, root, evaluator.work)
        root = Explanation("document", True, detail="all statements satisfied", children=tuple(children)) if trace else None
        return EvaluationResult("Satisfied", True, root, evaluator.work)
    except _Exhausted:
        detail = ("trace-node budget exhausted" if trace and max_trace_nodes < max_evaluations
                  else "formula-node evaluation budget exhausted")
        root = Explanation("resource_limit", None, detail=detail, children=tuple(children)) if trace else None
        return EvaluationResult("ResourceLimit", None, root, evaluator.work)


@semantic_entry("evaluate")
def evaluate(env: Any, value: Document | Any, model: FiniteModel, *, max_evaluations: int = 1_000_000,
             max_trace_nodes: int = 10_000, trace: bool = True) -> EvaluationResult:
    """Evaluate under the selected authority while keeping the public schema."""
    if getattr(env, "alternatives", None) is not None:
        raise CheckerUnavailable("alternatives@0 requires the Lean checker")
    if not isinstance(max_evaluations, int) or isinstance(max_evaluations, bool) or max_evaluations < 0:
        raise ValueError("max_evaluations must be a nonnegative integer")
    if max_evaluations > MAX_EVALUATIONS:
        raise ResourceLimit("Evaluation budget exceeds the v0 limit of 1,000,000 nodes")
    if type(trace) is not bool:
        raise ValueError("trace must be a boolean")
    if type(max_trace_nodes) is not int or max_trace_nodes < 0:
        raise ValueError("max_trace_nodes must be a nonnegative integer")
    if isinstance(value, Document):
        check_document(env, value)
        formulas = value.formulas
    else:
        check_formula(env, value)
        formulas = (value,)
    model = _validate_model(env, model)
    from .ast import _to_data
    from .backends.dispatch import execute
    from .backends.lean_runner import evaluation_case, run as lean_run
    from .backends.rust_jsonl import run as rust_run, rust_environment, soft_case

    case = {"id": "evaluate", "kind": "evaluate-budgeted", "environment": rust_environment(env), **soft_case(env),
            "model": model.to_dict(), "ast": [_to_data(f) for f in formulas],
            "max_evaluations": max_evaluations,
            "max_trace_nodes": min(max_evaluations, max_trace_nodes),
            "trace": trace}

    def python():
        return _evaluate_validated(formulas, model, max_evaluations=max_evaluations,
                                   max_trace_nodes=max_trace_nodes, trace=trace)

    def rust():
        row = rust_run(case)
        def explanation(wire):
            if not isinstance(wire, dict) or set(wire) != {"kind", "value", "bindings", "detail", "children"}:
                raise CheckerUnavailable("CheckerUnavailable: malformed Rust evaluation trace")
            bindings = wire["bindings"]
            if not isinstance(bindings, list) or any(
                not isinstance(item, dict) or item.get("debruijn_index") != index
                or set(item) != {"debruijn_index", "sort", "local_id"}
                for index, item in enumerate(bindings)
            ):
                raise CheckerUnavailable("CheckerUnavailable: malformed Rust trace bindings")
            return Explanation(wire["kind"], wire["value"],
                               tuple((item["sort"], item["local_id"]) for item in bindings),
                               wire["detail"], tuple(explanation(child) for child in wire["children"]))
        return EvaluationResult(row["status"], row["value"],
                                explanation(row["explanation"]) if trace else None,
                                row["evaluations"])

    def lean():
        result = rust()
        if result.status == "ResourceLimit":
            return result
        mode, request = evaluation_case(env, "evaluate", case["ast"], model.to_dict())
        value = all(lean_run(mode, [request])[0]["values"])
        if value != result.value:
            raise CheckerUnavailable("CheckerUnavailable: Lean and Rust evaluation disagree")
        return result

    return execute("evaluate", case, python, lean=lean, rust=rust)
