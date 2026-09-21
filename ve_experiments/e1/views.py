"""The four deterministic views of one AST, plus plain-text vocabulary and finite-model listings.

    fol_symbols   ∀x0:service. (deployed(x0) → ∃x1:engineer. (maintains(x1, x0)))
    fol_keywords  forall x0:service. (deployed(x0) implies exists x1:engineer. (maintains(x1, x0)))
    ve_strict     canonical VE text from `ve.printer.print_formula`
    ve_natural    read-only natural view from `ve.printer.natural_formula`

All four use the same binder names (x0, x1, ... in preorder) and the same predicate identifiers, so
cells differ only in notation.

TEMPORARY: the two FOL renderers here exist only for the dev pilot. The scored run must use the four
views that `ve` renders from one shared traversal (branch codex/views); `render` is the single
switch point. Likewise `ve_natural` is currently strict VE with longer keywords.
"""

from __future__ import annotations

from functools import lru_cache
import json

from ve import Environment, formula_from_data
from ve.printer import natural_formula, print_formula

VIEWS = ("fol_symbols", "fol_keywords", "ve_strict", "ve_natural")

_SYMBOLS = {"forall": "∀", "exists": "∃", "not": "¬", "and": "∧", "or": "∨", "implies": "→", "top": "⊤", "bottom": "⊥"}
_KEYWORDS = {"forall": "forall ", "exists": "exists ", "not": "not ", "and": "and", "or": "or", "implies": "implies",
             "top": "true", "bottom": "false"}  # fmt: skip


def _fol(f: list, names: list[str], counter: list[int], tok: dict) -> str:
    tag = f[0]
    term = lambda t: names[t[1]] if t[0] == "var" else t[1]  # noqa: E731
    if tag in ("top", "bottom"):
        return tok[tag]
    if tag == "unary":
        return f"{f[1]}({term(f[2])})"
    if tag == "binary":
        return f"{f[1]}({term(f[2])}, {term(f[3])})"
    if tag == "eq":
        return f"{term(f[1])} = {term(f[2])}"
    if tag == "not":
        return f"{tok['not']}({_fol(f[1], names, counter, tok)})"
    if tag in ("and", "or", "implies"):
        return f"({_fol(f[1], names, counter, tok)} {tok[tag]} {_fol(f[2], names, counter, tok)})"
    name = f"x{counter[0]}"
    counter[0] += 1
    body = _fol(f[2], [name, *names], counter, tok)
    if f[2][0] not in ("and", "or", "implies"):  # binary connectives already carry their parentheses
        body = f"({body})"
    return f"{tok[tag]}{name}:{f[1]}. {body}"


@lru_cache(maxsize=256)
def _env(env_json: str) -> Environment:
    return Environment.from_dict(json.loads(env_json))


def check(environment: dict, f: list):
    """Type-check under the real `ve` checker; raises ve.VEError on failure."""
    env = _env(json.dumps(environment, sort_keys=True))
    return env, formula_from_data(env, f)


def render(environment: dict, f: list, view: str) -> str:
    env, formula = check(environment, f)
    if view == "fol_symbols":
        return _fol(f, [], [0], _SYMBOLS)
    if view == "fol_keywords":
        return _fol(f, [], [0], _KEYWORDS)
    if view == "ve_strict":
        return print_formula(env, formula) + "."
    if view == "ve_natural":
        return natural_formula(env, formula).text
    raise ValueError(f"unknown view {view!r}")


def vocabulary_text(environment: dict) -> str:
    voc = environment["vocabulary"]
    lines = ["Sorts:"]
    lines += [f"  {s}: {d['description']}" for s, d in voc["sorts"].items()]
    lines.append("Predicates (argument sorts in order):")
    lines += [f"  {p}({', '.join(d['arguments'])}): {d['description']}" for p, d in voc["predicates"].items()]
    return "\n".join(lines)


def model_text(model: dict) -> str:
    lines = [f"  {s}s: {', '.join(d) if d else '(none)'}" for s, d in model["domains"].items()]
    for p, tuples in model["relations"].items():
        shown = ", ".join(t[0] if len(t) == 1 else "(" + ", ".join(t) + ")" for t in tuples)
        lines.append(f"  {p}: {shown if tuples else '(nothing)'}")
    return "\n".join(lines)
