"""The deterministic views of one AST, all rendered by the `ve` package from one shared traversal
(`ve.printer.render`): fol_symbols, fol_keywords, ve_strict, ve_natural, ve_fluent. Binder naming is
per statement in every view. `legend` is `ve.printer.render_vocabulary`, which is byte-identical
across views and is shown in every cell. This module adds only plain-text listings of finite models
and a plain vocabulary listing used in generation prompts (never in a judge cell).
"""

from __future__ import annotations

import json
from functools import lru_cache

from ve import Environment, formula_from_data
from ve.printer import VIEWS as _VE_VIEWS
from ve.printer import render as _render
from ve.printer import render_vocabulary

VIEWS = tuple(_VE_VIEWS)
NAMING = "per_statement"


@lru_cache(maxsize=256)
def _env(env_json: str) -> Environment:
    return Environment.from_dict(json.loads(env_json))


def check(environment: dict, f: list):
    """Type-check under the real `ve` checker; raises ve.VEError on failure."""
    env = _env(json.dumps(environment, sort_keys=True))
    return env, formula_from_data(env, f)


def render(environment: dict, f: list, view: str) -> str:
    env, formula = check(environment, f)
    return _render(formula, env, view, NAMING)


def legend(environment: dict) -> str:
    env = _env(json.dumps(environment, sort_keys=True))
    texts = {render_vocabulary(env, v, NAMING) for v in VIEWS}
    if len(texts) != 1:
        raise RuntimeError("vocabulary legend differs between views")
    return texts.pop()


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
