"""Thin interface between the experiment harness and the `ve` language package.

The harness needs three operations:

    render(ast, view) -> str                      view in {"strict", "fol"} (the real package adds "natural")
    evaluate(ast, model) -> bool                  truth of a closed formula in a finite model
    find_countermodel(premises, conclusion, ...)  a finite model of the premises that falsifies the conclusion, or None

ASTs and models use the wire formats of docs/spec/v0-language.md (tagged JSON arrays; model with
`domains`, `constants`, `relations`). `get_backend(environment)` returns `VeBackend`, an adapter
over the real `ve` package bound to one environment. It never falls back silently: if `ve` is not
importable it raises, unless the caller passes `allow_stub=True`. `StubBackend` is a small
untrusted reference implementation (no type checking, brute-force search) kept for harness tests
and for cross-checking the adapter; `runner.run` refuses a scored run when the backend is a stub.
"""

from __future__ import annotations

import itertools
from typing import Any, Protocol

Ast = list
Model = dict


class VEBackend(Protocol):
    name: str

    def render(self, ast: Ast, view: str = "strict") -> str: ...
    def evaluate(self, ast: Ast, model: Model) -> bool: ...
    def find_countermodel(
        self, premises: list[Ast], conclusion: Ast, vocabulary: dict, max_domain: int = 2
    ) -> Model | None: ...


class StubBackend:
    name = "stub"

    # -- rendering

    def render(self, ast: Ast, view: str = "strict") -> str:
        if view == "strict":
            return self._strict(ast, [], [0]) + "."
        if view == "fol":
            return self._fol(ast, [], [0])
        raise ValueError(f"stub backend has no view {view!r}")

    def _term(self, t: Ast, names: list[str], strict: bool) -> str:
        if t[0] == "var":
            return names[t[1]]
        if t[0] == "const":
            return ("@" if strict else "") + t[1]
        raise ValueError(f"bad term {t!r}")

    def _strict(self, f: Ast, names: list[str], counter: list[int]) -> str:
        tag = f[0]
        r = lambda g, n=names: self._strict(g, n, counter)  # noqa: E731
        t = lambda x: self._term(x, names, True)  # noqa: E731
        match tag:
            case "top":
                return "true"
            case "bottom":
                return "false"
            case "unary":
                return f"{t(f[2])} is {f[1]}"
            case "binary":
                return f"{t(f[2])} {f[1]} {t(f[3])}"
            case "eq":
                return f"{t(f[1])} equals {t(f[2])}"
            case "not":
                return f"not ({r(f[1])})"
            case "and" | "or":
                return f"({r(f[1])}) {tag} ({r(f[2])})"
            case "implies":
                return f"if ({r(f[1])}), then ({r(f[2])})"
            case "forall" | "exists":
                name = f"x{counter[0]}"
                counter[0] += 1
                head = "for every" if tag == "forall" else "there exists"
                return f"{head} {f[1]} {name}, ({self._strict(f[2], [name, *names], counter)})"
        raise ValueError(f"unknown tag {tag!r}")

    def _fol(self, f: Ast, names: list[str], counter: list[int]) -> str:
        tag = f[0]
        r = lambda g, n=names: self._fol(g, n, counter)  # noqa: E731
        t = lambda x: self._term(x, names, False)  # noqa: E731
        match tag:
            case "top":
                return "⊤"
            case "bottom":
                return "⊥"
            case "unary":
                return f"{f[1]}({t(f[2])})"
            case "binary":
                return f"{f[1]}({t(f[2])}, {t(f[3])})"
            case "eq":
                return f"{t(f[1])} = {t(f[2])}"
            case "not":
                return f"¬({r(f[1])})"
            case "and":
                return f"({r(f[1])} ∧ {r(f[2])})"
            case "or":
                return f"({r(f[1])} ∨ {r(f[2])})"
            case "implies":
                return f"({r(f[1])} → {r(f[2])})"
            case "forall" | "exists":
                name = f"x{counter[0]}"
                counter[0] += 1
                q = "∀" if tag == "forall" else "∃"
                return f"{q}{name}:{f[1]}. {self._fol(f[2], [name, *names], counter)}"
        raise ValueError(f"unknown tag {tag!r}")

    # -- evaluation

    def evaluate(self, ast: Ast, model: Model) -> bool:
        relations = {p: {tuple(t) for t in tuples} for p, tuples in model["relations"].items()}
        return self._eval(ast, model, relations, [])

    def _eval(self, f: Ast, model: Model, rel: dict, env: list[tuple[str, str]]) -> bool:
        def val(t: Ast) -> Any:
            # entities are (sort, id); constants carry no sort in the AST, so compare ids within
            # the sort of the position. The stub compares ids only, which is sound when ids are
            # unique across sorts (true for all harness-generated models).
            return env[t[1]][1] if t[0] == "var" else model["constants"][t[1]]

        e = lambda g: self._eval(g, model, rel, env)  # noqa: E731
        match f[0]:
            case "top":
                return True
            case "bottom":
                return False
            case "unary":
                return (val(f[2]),) in rel[f[1]]
            case "binary":
                return (val(f[2]), val(f[3])) in rel[f[1]]
            case "eq":
                return val(f[1]) == val(f[2])
            case "not":
                return not e(f[1])
            case "and":
                return e(f[1]) and e(f[2])
            case "or":
                return e(f[1]) or e(f[2])
            case "implies":
                return (not e(f[1])) or e(f[2])
            case "forall":
                return all(self._eval(f[2], model, rel, [(f[1], d), *env]) for d in model["domains"][f[1]])
            case "exists":
                return any(self._eval(f[2], model, rel, [(f[1], d), *env]) for d in model["domains"][f[1]])
        raise ValueError(f"unknown tag {f[0]!r}")

    # -- countermodels

    def find_countermodel(
        self, premises: list[Ast], conclusion: Ast, vocabulary: dict, max_domain: int = 2, max_models: int = 200_000
    ) -> Model | None:
        """Brute force over all models with at most `max_domain` elements per sort.

        Returns None both when no countermodel exists within the bound and when `max_models` is
        exhausted; None is never evidence of entailment.
        """
        sorts = sorted(vocabulary["sorts"])
        preds = sorted(vocabulary["predicates"].items())
        consts = sorted(vocabulary["constants"].items())
        tried = 0
        for sizes in itertools.product(range(0, max_domain + 1), repeat=len(sorts)):
            domains = {s: [f"{s}{i}" for i in range(n)] for s, n in zip(sorts, sizes)}
            if any(not domains[c["sort"]] for _, c in consts):
                continue
            const_choices = [domains[c["sort"]] for _, c in consts]
            tuple_spaces = [list(itertools.product(*(domains[a] for a in p["arguments"]))) for _, p in preds]
            for const_vals in itertools.product(*const_choices):
                for subsets in itertools.product(*(_powerset(ts) for ts in tuple_spaces)):
                    tried += 1
                    if tried > max_models:
                        return None
                    model = {
                        "complete": True,
                        "domains": domains,
                        "constants": {name: v for (name, _), v in zip(consts, const_vals)},
                        "relations": {name: [list(t) for t in sub] for (name, _), sub in zip(preds, subsets)},
                    }
                    if all(self.evaluate(p, model) for p in premises) and not self.evaluate(conclusion, model):
                        return model
        return None


def _powerset(items: list) -> list[tuple]:
    return [c for r in range(len(items) + 1) for c in itertools.combinations(items, r)]


class BackendUnavailable(RuntimeError):
    pass


class VeBackend:
    """Adapter over the real `ve` package, bound to one environment (wire dict)."""

    name = "ve"

    def __init__(self, environment: dict):
        import ve

        self._ve = ve
        self.environment = environment
        self.env = ve.Environment.from_dict(environment)

    def _formula(self, ast: Ast):
        return self._ve.formula_from_data(self.env, ast)

    def render(self, ast: Ast, view: str = "strict") -> str:
        formula = self._formula(ast)
        if view == "strict":
            return self._ve.print_formula(self.env, formula) + "."
        if view == "natural":
            return self._ve.natural_formula(self.env, formula).text
        if hasattr(self._ve, "render"):  # codex/views: render(ast, env, view) for fol_symbols / fol_keywords
            return self._ve.render(formula, self.env, view)
        raise ValueError(f"the installed ve package has no view {view!r}")

    def evaluate(self, ast: Ast, model: Model) -> bool:
        result = self._ve.evaluate(self.env, self._formula(ast), self._ve.FiniteModel.from_dict(self.env, model))
        if result.value is None:
            raise RuntimeError(f"evaluation did not finish: {result.status}")
        return result.value

    def find_countermodel(self, premises: list[Ast], conclusion: Ast, vocabulary: dict | None = None,
                          max_domain: int = 2, max_models: int = 10_000) -> Model | None:  # fmt: skip
        result = self._ve.find_countermodel(self.env, [self._formula(p) for p in premises], self._formula(conclusion),
                                            max_domain_size=max_domain, max_models=max_models)  # fmt: skip
        return None if result.model is None else result.model.to_dict()

    def find_distinguishing_model(self, a: Ast, b: Ast, max_domain: int = 2, max_models: int = 10_000) -> Model | None:
        """A model on which a and b disagree: a countermodel to `a iff b`."""
        iff = ["and", ["implies", a, b], ["implies", b, a]]
        return self.find_countermodel([], iff, max_domain=max_domain, max_models=max_models)


def backend_name() -> str:
    try:
        import ve  # noqa: F401
    except ImportError:
        return "stub"
    return "ve"


def get_backend(environment: dict | None = None, allow_stub: bool = False) -> VEBackend:
    """The real adapter. The stub is returned only on explicit request and only when `ve` is missing."""
    if backend_name() == "ve":
        if environment is None:
            raise ValueError("the ve backend is bound to an environment; pass the environment wire dict")
        return VeBackend(environment)
    if allow_stub:
        return StubBackend()
    raise BackendUnavailable("the `ve` package is not importable and allow_stub is False")
