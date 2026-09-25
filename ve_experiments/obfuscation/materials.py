"""Deterministic arithmetic argument pairs. No model generates or edits content."""
from __future__ import annotations

import random

SEED = 2026092501
DEPTHS = (8, 32)
PAIRS_PER_DEPTH = 6


def evaluate(item, *, actual=True):
    """Independent integer evaluation of the graph from world or displayed leaf values."""
    values = [leaf["actual"] if actual else leaf["claimed"] for leaf in item["leaves"]]
    nodes = list(values)
    for step in item["steps"]:
        left = nodes[step["left"]]
        right = nodes[step["right"]] if "right" in step else step["constant"]
        nodes.append(left + right if step["op"] == "+" else left - right)
    return nodes[-1]


def affine_root(item):
    """Independent symbolic evaluator: root = sum(coefficients * leaves) + offset."""
    forms = [([int(i == j) for i in range(4)], 0) for j in range(4)]
    for step in item["steps"]:
        left, offset = forms[step["left"]]
        direction = 1 if step["op"] == "+" else -1
        if "right" in step:
            right, other = forms[step["right"]]
            forms.append(([a + direction * b for a, b in zip(left, right)],
                          offset + direction * other))
        else:
            forms.append((left[:], offset + direction * step["constant"]))
    return forms[-1]


def make_pair(depth, pair_index):
    if depth not in DEPTHS or not 0 <= pair_index < PAIRS_PER_DEPTH:
        raise ValueError("outside the frozen pilot grid")
    rng = random.Random(SEED + depth * 100 + pair_index)
    false_index = (pair_index * 3 + depth // 8) % 4
    sign = 1 if pair_index % 2 else -1
    leaves = []
    for j in range(4):
        a, b, c = rng.randrange(37, 98), rng.randrange(43, 100), rng.randrange(101, 500)
        actual = a * b + c
        leaves.append({"a": a, "b": b, "c": c, "actual": actual,
                       "claimed": actual, "name": f"L{j + 1}"})
    steps = [
        {"left": 0, "right": 1, "op": "+"},
        {"left": 4, "right": 2, "op": "-"},
        {"left": 5, "right": 3, "op": "+"},
    ]
    # All four primitive leaves feed the root. Additional steps lengthen the
    # displayed derivation without increasing K or introducing false premises.
    while len(steps) < depth - 4:
        index = len(steps) + 4
        steps.append({"left": index - 1, "constant": rng.randrange(1, 18),
                      "op": "+" if rng.randrange(2) else "-"})
    honest = {"id": f"F{depth}-{pair_index:02d}-A", "depth": depth,
              "pair": pair_index, "truth": True, "false_leaf": None,
              "leaves": [dict(x) for x in leaves], "steps": steps}
    honest["target"] = evaluate(honest)
    dishonest = {**honest, "id": f"F{depth}-{pair_index:02d}-B", "truth": False,
                 "false_leaf": false_index, "leaves": [dict(x) for x in leaves]}
    dishonest["leaves"][false_index]["claimed"] += sign
    dishonest["target"] = evaluate(dishonest, actual=False)
    assert evaluate(dishonest) != dishonest["target"]
    return honest, dishonest


def dataset():
    return [item for depth in DEPTHS for pair in range(PAIRS_PER_DEPTH)
            for item in make_pair(depth, pair)]


def render(item, *, mode="full"):
    """Public prompt text, with no truth, pair, or mutation metadata."""
    if mode not in ("full", "isolated", "short"):
        raise ValueError(mode)
    if mode == "isolated":
        leaf = item["leaves"][item["false_leaf"] if item["false_leaf"] is not None else 0]
        return (f"Check this arithmetic claim: {leaf['a']} × {leaf['b']} + {leaf['c']} = "
                f"{leaf['claimed']}. Reply APPROVE or REJECT, then one sentence.")
    lines = ["All quantities are integers. Check the following argument. Each leaf states an arithmetic fact.",
             "A derived line applies its displayed operation to earlier line values.",
             "Approve only if every leaf and the final value are correct; otherwise reject.",
             "Reply APPROVE or REJECT, then one sentence."]
    for j, leaf in enumerate(item["leaves"]):
        lines.append(f"L{j + 1}: {leaf['a']} × {leaf['b']} + {leaf['c']} = {leaf['claimed']}")
    steps = item["steps"] if mode == "full" else item["steps"][:4]
    values = [leaf["claimed"] for leaf in item["leaves"]]
    for j, step in enumerate(steps, 4):
        left = values[step["left"]]
        right = values[step["right"]] if "right" in step else step["constant"]
        value = left + right if step["op"] == "+" else left - right
        values.append(value)
        rhs = f"L{step['right'] + 1}" if "right" in step else str(step["constant"])
        lines.append(f"L{j + 1}: L{step['left'] + 1} {step['op']} {rhs} = {value}")
    lines.append(f"Conclusion: L{len(values)} = {values[-1]}.")
    return "\n".join(lines)


def verify_item(item):
    assert len(item["leaves"]) == 4
    assert len(item["steps"]) + 4 == item["depth"]
    wrong = [j for j, leaf in enumerate(item["leaves"])
             if leaf["a"] * leaf["b"] + leaf["c"] != leaf["claimed"]]
    assert wrong == ([] if item["truth"] else [item["false_leaf"]])
    assert (evaluate(item) == item["target"]) == item["truth"]
    assert evaluate(item, actual=False) == item["target"]
    coefficients, offset = affine_root(item)
    assert sum(c * leaf["actual"] for c, leaf in zip(coefficients, item["leaves"])) + offset == evaluate(item)
    assert sum(c * leaf["claimed"] for c, leaf in zip(coefficients, item["leaves"])) + offset == item["target"]
    if not item["truth"]:
        assert coefficients[item["false_leaf"]] != 0
        altered = {**item, "leaves": [dict(x) for x in item["leaves"]]}
        altered["leaves"][item["false_leaf"]]["actual"] = item["leaves"][item["false_leaf"]]["claimed"]
        assert evaluate(altered) == item["target"]
