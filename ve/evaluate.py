"""Small trusted finite-model evaluator with bounded explanatory traces."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .ast import (And, Binary, Bottom, Const, Document, Eq, Exists, Forall,
                  Implies, Not, Or, Top, Unary, Var, check_document, check_formula)
from .model import FiniteModel
from .errors import InvalidModel, ResourceLimit, VEError
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
    explanation: Explanation
    evaluations: int

    def to_dict(self) -> dict[str, Any]:
        return {"status": self.status, "value": self.value, "evaluations": self.evaluations,
                "explanation": self.explanation.to_dict()}


class _Exhausted(Exception):
    pass


class _Evaluator:
    def __init__(self, env: Any, model: FiniteModel, maximum: int):
        self.env, self.model, self.maximum, self.work = env, model, maximum, 0

    def tick(self) -> None:
        if self.work >= self.maximum:
            raise _Exhausted
        self.work += 1

    def term(self, term: Any, bindings: tuple[tuple[str, str], ...]) -> str:
        if isinstance(term, Var):
            return bindings[term.index][1]
        if isinstance(term, Const):
            return self.model.constants[term.name]
        raise TypeError(f"unknown term node {type(term).__name__}")

    def formula(self, f: Any, bindings: tuple[tuple[str, str], ...] = ()) -> tuple[bool, Explanation]:
        self.tick()
        shown = bindings
        if isinstance(f, Top): return True, Explanation("top", True, shown)
        if isinstance(f, Bottom): return False, Explanation("bottom", False, shown)
        if isinstance(f, Unary):
            row = (self.term(f.term, bindings),); value = row in self.model.relations[f.predicate]
            return value, Explanation("unary", value, shown, f"{f.predicate}{row}")
        if isinstance(f, Binary):
            row = (self.term(f.left, bindings), self.term(f.right, bindings)); value = row in self.model.relations[f.predicate]
            return value, Explanation("binary", value, shown, f"{f.predicate}{row}")
        if isinstance(f, Eq):
            left, right = self.term(f.left, bindings), self.term(f.right, bindings); value = left == right
            return value, Explanation("equality", value, shown, f"{left} equals {right}")
        if isinstance(f, Not):
            v, c = self.formula(f.body, bindings); return not v, Explanation("not", not v, shown, children=(c,))
        if isinstance(f, (And, Or, Implies)):
            lv, le = self.formula(f.left, bindings)
            if isinstance(f, And) and not lv:
                return False, Explanation("and", False, shown, "right branch not needed", (le,))
            if isinstance(f, Or) and lv:
                return True, Explanation("or", True, shown, "right branch not needed", (le,))
            if isinstance(f, Implies) and not lv:
                return True, Explanation("implies", True, shown, "vacuously true: antecedent is false", (le,))
            rv, re = self.formula(f.right, bindings)
            value = (lv and rv) if isinstance(f, And) else ((lv or rv) if isinstance(f, Or) else rv)
            return value, Explanation(type(f).__name__.lower(), value, shown, children=(le, re))
        if isinstance(f, (Forall, Exists)):
            domain = self.model.domains[f.sort]
            kind = "forall" if isinstance(f, Forall) else "exists"
            if not domain:
                value = isinstance(f, Forall)
                detail = "vacuously true: domain is empty" if value else "false: domain is empty"
                return value, Explanation(kind, value, shown, detail)
            children: list[Explanation] = []
            for entity in domain:
                value, child = self.formula(f.body, ((f.sort, entity),) + bindings)
                children.append(child)
                if isinstance(f, Forall) and not value:
                    return False, Explanation(kind, False, shown, f"counterexample {entity}", tuple(children))
                if isinstance(f, Exists) and value:
                    return True, Explanation(kind, True, shown, f"witness {entity}", tuple(children))
            value = isinstance(f, Forall)
            return value, Explanation(kind, value, shown, "all entities checked" if value else "no witness", tuple(children))
        raise TypeError(f"unknown formula node {type(f).__name__}")


def evaluate(env: Any, value: Document | Any, model: FiniteModel, *, max_evaluations: int = 1_000_000,
             max_trace_nodes: int = 10_000) -> EvaluationResult:
    """Validate the public inputs and evaluate a closed formula or document."""
    if type(model) is not FiniteModel:
        raise InvalidModel("expected a validated FiniteModel")
    if model.environment_id != env.environment_id:
        raise InvalidModel("model belongs to a different environment")
    # FiniteModel has a public constructor. Revalidate its wire projection rather
    # than trusting that callers used from_dict/from_json.
    try:
        validated = FiniteModel.from_dict(env, model.to_dict())
    except VEError:
        raise
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        raise InvalidModel("malformed FiniteModel object") from exc
    if validated.model_id != model.model_id:
        raise InvalidModel("model identity does not match its contents")
    model = validated
    if not isinstance(max_evaluations, int) or isinstance(max_evaluations, bool) or max_evaluations < 0:
        raise ValueError("max_evaluations must be a nonnegative integer")
    if max_evaluations > MAX_EVALUATIONS:
        raise ResourceLimit("Evaluation budget exceeds the v0 limit of 1,000,000 nodes")
    if type(max_trace_nodes) is not int or max_trace_nodes < 0:
        raise ValueError("max_trace_nodes must be a nonnegative integer")
    if isinstance(value, Document):
        check_document(env, value)
        formulas = value.formulas
    else:
        check_formula(env, value)
        formulas = (value,)
    # Every evaluated node can contribute one trace node. Treat trace exhaustion
    # as a resource result instead of building an independently unbounded tree.
    evaluator = _Evaluator(env, model, min(max_evaluations, max_trace_nodes))
    children: list[Explanation] = []
    try:
        for index, formula in enumerate(formulas):
            result, trace = evaluator.formula(formula)
            children.append(trace)
            if not result:
                root = Explanation("document", False, detail=f"statement {index + 1} violated", children=tuple(children))
                return EvaluationResult("Violated", False, root, evaluator.work)
        root = Explanation("document", True, detail="all statements satisfied", children=tuple(children))
        return EvaluationResult("Satisfied", True, root, evaluator.work)
    except _Exhausted:
        detail = ("trace-node budget exhausted" if max_trace_nodes < max_evaluations
                  else "formula-node evaluation budget exhausted")
        root = Explanation("resource_limit", None, detail=detail, children=tuple(children))
        return EvaluationResult("ResourceLimit", None, root, evaluator.work)
