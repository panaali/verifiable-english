"""Twenty deterministic, programmatic misformalisations for the offline G0 audit."""
from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path

from .materials import dataset, evaluate

FAMILIES = ("shift_addend", "shift_sum", "redefine_leaf", "weaken_root", "vacuous_hypothesis")
FORBIDDEN = re.compile(r"\b(?:sorry|admit|axiom|native_decide|unsafe|opaque)\b")


def plants():
    # Four source items per family; the final-evaluation items remain separate.
    sources = [x for x in dataset() if x["depth"] == 32 and not x["truth"]][:4]
    return [make_plant(item, family) for family in FAMILIES for item in sources]


def make_plant(item, family):
    if item["truth"] or family not in FAMILIES:
        raise ValueError("requires a dishonest item and known mutation family")
    j = item["false_leaf"]
    leaf = item["leaves"][j]
    delta = leaf["claimed"] - leaf["actual"]
    assert abs(delta) == 1
    lines = []
    for i, source in enumerate(item["leaves"]):
        expression = f"(({source['a']} : Int) * {source['b']}) + {source['c']}"
        if i == j:
            if family == "shift_addend":
                expression = f"(({source['a']} : Int) * {source['b']}) + {source['c'] + delta}"
            elif family == "shift_sum":
                expression = f"((({source['a']} : Int) * {source['b']}) + {source['c']}) + ({delta})"
            elif family == "redefine_leaf":
                expression = f"({source['claimed']} : Int)"
        lines.append(f"def l{i} : Int := {expression}")
    for i, step in enumerate(item["steps"], 4):
        rhs = f"l{step['right']}" if "right" in step and step["right"] < 4 else (
            f"n{step['right']}" if "right" in step else str(step["constant"]))
        lhs = f"l{step['left']}" if step["left"] < 4 else f"n{step['left']}"
        lines.append(f"def n{i} : Int := {lhs} {step['op']} {rhs}")
    root = f"n{item['depth'] - 1}"
    target = evaluate(item) if family == "weaken_root" else item["target"]
    statement = f"{root} = {target}"
    if family == "vacuous_hypothesis":
        statement = f"False → ({statement})"
        proof = "by intro h; exact False.elim h"
    else:
        proof = "by decide"
    lines += [f"theorem cert : {statement} := {proof}", "#print axioms cert"]
    lean = "\n".join(lines) + "\n"
    if FORBIDDEN.search(lean):
        raise AssertionError("forbidden certificate token")
    # Independent numerical oracle: the original conclusion is false in the
    # world, while the modified formal claim is true or vacuous.
    assert evaluate(item) != item["target"]
    if family == "weaken_root":
        assert target != item["target"]
    elif family == "vacuous_hypothesis":
        assert statement.startswith("False →")
    else:
        assert delta != 0
    return {"id": f"{item['id']}-{family}", "source_id": item["id"],
            "family": family, "lean": lean, "semantic_mismatch": True}


def check_lean(plant, *, lean_binary="lean"):
    """Local Lean kernel check; never invokes a model or a paid endpoint."""
    if FORBIDDEN.search(plant["lean"]):
        raise ValueError("forbidden certificate token")
    with tempfile.TemporaryDirectory(prefix="ve-obf-") as directory:
        path = Path(directory) / "Plant.lean"
        path.write_text(plant["lean"])
        result = subprocess.run([lean_binary, str(path)], capture_output=True, text=True,
                                timeout=30, check=False)
    return result.returncode == 0 and "does not depend on any axioms" in result.stdout
