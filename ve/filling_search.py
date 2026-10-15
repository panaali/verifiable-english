"""The one untrusted flip search (plan Q2.5): candidate fillings that split a target formula.

A target formula's value in a base situation can turn on filled gaps (the points the text leaves open). `split`
proposes the two fillings of an UNDECIDED or *not settled* witness: a start filling, and the same filling changed at
exactly the points the target's value turns on. Every caller is an instance of it:

* a question (`ve ask`): the target is the asked formula ψ, the start is the checked countermodel's filling (ψ fails
  there) and the points are Lean's `gaps` of the row (`gapsOf ψ`);
* a norm-defaults point (`point_statuses`): the target is the reached outcome of the point, the start is the empty
  filling and the points are every point of every filled table over the situation (`points`), so the flipped
  filling is the full one, which keeps every pair premise of `Fill_T` true.

Lean checks every proposed filling (`splitOk_sound`, `undecided_witness_sound`) and owns the answer. This module
only builds assignments to the open ``unsaid__`` relations.
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


def split(start: dict, gaps) -> dict:
    """The split of a target formula: `{"true": start flipped at gaps, "false": start}`, for a start filling under
    which the target fails and the points (`[predicate, tuple, value under start]`) its value turns on."""
    return {"true": flip(start, gaps), "false": {name: [list(row) for row in rows] for name, rows in start.items()}}


def points(unsaid: list[dict], domains: dict) -> tuple[dict, list]:
    """The empty filling of the filled tables and every point of every table over the situation's elements, each
    false there: the start and the points of a target whose gaps are not named."""
    empty = {item["name"]: [] for item in unsaid}
    gaps = [[item["name"].removeprefix("unsaid__"), list(values), False]
            for item in unsaid for values in product(*(domains[s] for s in item["sorts"]))]
    return empty, gaps


def point_statuses(document, model):
    """Ask Lean for each point; its undecided method gets the target's split from `split`."""
    from .norm_defaults_route import run_case, source_case

    states = {}
    start, gaps = points(document.elaboration["unsaid"], model["domains"])
    candidate = split(start, gaps) if gaps else None
    for item in document.elaboration["reached"]:
        for values in product(*(model["domains"][sort] for sort in item["sorts"])):
            case = source_case(document, "norm-defaults-status", model=model,
                               predicate=item["predicate"], tuple=list(values), method="enumerate")
            state = run_case(case)["point_status"]
            if state == "UNKNOWN" and candidate is not None:
                state = run_case({**case, "method": "undecided", "yes": candidate["true"],
                                  "no": candidate["false"]})["point_status"]
            states[(item["predicate"], values)] = state
    return states
