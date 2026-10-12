"""Untrusted candidate fillings for question splits and norm-defaults point searches.

Lean checks every proposed filling and owns the answer.  This module only constructs
alternative assignments to the open ``unsaid__`` relations.
"""
from __future__ import annotations

from itertools import product


def flip(filling: dict, gaps) -> dict:
    """Change exactly the named gap tuples to their other Boolean value."""
    out = {name: [list(row) for row in rows] for name, rows in filling.items()}
    for predicate, ids, value in gaps:
        rows = out.setdefault("unsaid__" + predicate, [])
        if value:
            rows[:] = [row for row in rows if row != list(ids)]
        elif list(ids) not in rows:
            rows.append(list(ids))
    return out


def extremes(unsaid: list[dict], domains: dict) -> tuple[dict, dict]:
    """The all-true and all-false fillings of the admitted finite situation."""
    no = {item["name"]: [] for item in unsaid}
    yes = {item["name"]: [list(values) for values in product(*(domains[s] for s in item["sorts"]))]
           for item in unsaid}
    return yes, no


def point_statuses(document, model):
    """Ask Lean for each point; give its undecided method the shared candidate fillings."""
    from .norm_defaults_route import run_case, source_case

    states = {}
    yes, no = extremes(document.elaboration["unsaid"], model["domains"])
    for item in document.elaboration["reached"]:
        for values in product(*(model["domains"][sort] for sort in item["sorts"])):
            case = source_case(document, "norm-defaults-status", model=model,
                               predicate=item["predicate"], tuple=list(values), method="enumerate")
            state = run_case(case)["point_status"]
            if state == "UNKNOWN" and yes:
                state = run_case({**case, "method": "undecided", "yes": yes, "no": no})["point_status"]
            states[(item["predicate"], values)] = state
    return states
