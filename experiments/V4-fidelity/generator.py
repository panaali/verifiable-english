"""Dependency-free adaptation of ProverGen's top-down skeleton algorithm.

Local rule truth tables are complete (<=3 propositions), replacing Prover9 for
this propositional stage. See PROVENANCE.md for distribution changes.
"""
from functools import lru_cache
from itertools import product
import json
from pathlib import Path
import random
import re

RULES = json.loads(Path(__file__).with_name("provergen_rules.json").read_text())
VALUES = ("True", "False", "Uncertain")


def parse_rule(text):
    tokens = re.findall(r"\[[^]]+\]|[()→∧∨⊕]", text)
    index = 0
    def expr():
        nonlocal index
        if tokens[index] == "(":
            index += 1
            left = expr()
            if tokens[index] != ")":
                raise ValueError("unbalanced rule")
            index += 1
        else:
            left = tokens[index][1:-1]
            index += 1
        if index < len(tokens) and tokens[index] != ")":
            op = tokens[index]
            index += 1
            return (op, left, expr())
        return left
    result = expr()
    if index != len(tokens):
        raise ValueError("trailing rule tokens")
    return result


def instantiate(text, names):
    for name in names:
        text = text.replace("[F]", f"[{name}]", 1)
    return parse_rule(text)


def atoms(f):
    if isinstance(f, str):
        return {f}
    return set().union(*(atoms(x) for x in f[1:]))


def evaluate(f, assignment):
    if isinstance(f, str):
        return assignment[f]
    if f[0] == "¬":
        return not evaluate(f[1], assignment)
    a, b = evaluate(f[1], assignment), evaluate(f[2], assignment)
    return {"→": (not a) or b, "∧": a and b, "∨": a or b, "⊕": a != b}[f[0]]


def literal(name, value):
    return name if value == "True" else ("¬", name)


@lru_cache(None)
def solutions(template, goal_index, goal_value):
    names = [f"v{i}" for i in range(template.count("[F]"))]
    formula = instantiate(template, names)
    others = [n for i, n in enumerate(names) if i != goal_index]
    valid = []
    for values in product(VALUES, repeat=len(others)):
        assignments = [dict(zip(names, bits)) for bits in product((False, True), repeat=len(names))]
        assignments = [a for a in assignments if all(v == "Uncertain" or a[n] == (v == "True")
                                                     for n, v in zip(others, values))]
        # Upstream's Uncertain normal rules must already follow from the other facts.
        if goal_index is not None and goal_value == "Uncertain" and not all(evaluate(formula, a) for a in assignments):
            continue
        models = assignments if goal_index is None else [a for a in assignments if evaluate(formula, a)]
        if not models:
            continue
        outcomes = {evaluate(formula, a) if goal_index is None else a[names[goal_index]] for a in models}
        label = "True" if outcomes == {True} else "False" if outcomes == {False} else "Uncertain"
        if label == goal_value:
            valid.append(values)
    return tuple(valid)


def skeleton(rng, label, depth):
    """Expand a random pending fact, with upstream's 0.4 direct-fact stopping rule."""
    next_id = 0
    def normal(goal, value, distractor=False):
        nonlocal next_id
        for _ in range(200):
            template = rng.choice(RULES["normal_rules"])
            count = template.count("[F]")
            position = (rng.choice((count-2, count-1)) if distractor and template in
                        ("[F] → ([F] ∧ [F])", "[F] → ([F] ∨ [F])", "[F] → ([F] ⊕ [F])")
                        else count-1 if distractor else rng.randrange(count))
            candidates = solutions(template, position, value)
            if candidates:
                break
        else:
            raise RuntimeError("No local rule")
        names = []
        for i in range(count):
            if i == position and goal is not None:
                names.append(goal)
            else:
                names.append(f"a{next_id}"); next_id += 1
        values = rng.choice(candidates)
        pending = list(zip([n for i, n in enumerate(names) if i != position], values))
        return instantiate(template, names), names[position], pending
    premises, steps, pending = [], [], []
    if rng.random() < .25:
        candidates = []
        while not candidates:
            template = rng.choice(RULES["goal_rules"])
            candidates = solutions(template, None, label)
        names = [f"a{i}" for i in range(template.count("[F]"))]
        next_id = len(names)
        goal = instantiate(template, names)
        pending = list(zip(names, rng.choice(candidates)))
        steps.append({"rule": None, "facts": pending.copy(), "conclusion": goal, "value": label})
        count = 0
    else:
        rule, goal, pending = normal(None, label)
        premises.append(rule)
        steps.append({"rule": rule, "facts": pending.copy(), "conclusion": goal, "value": label})
        count = 1
    while count < depth:
        index = rng.randrange(len(pending))
        target, value = pending.pop(index)
        if len(pending) >= 2 and rng.random() < .4:
            if value != "Uncertain":
                premises.append(literal(target, value))
            continue
        rule, _, new = normal(target, value)
        premises.append(rule)
        steps.insert(0, {"rule": rule, "facts": new.copy(), "conclusion": target, "value": value})
        pending.extend(new)
        distractor, _, facts = normal(target, "Uncertain", distractor=True)
        premises.append(distractor)
        premises.extend(literal(n, v) for n, v in facts if v != "Uncertain")
        count += 1
    premises.extend(literal(n, v) for n, v in pending if v != "Uncertain")
    return {"premises": premises, "query": goal, "label": label, "steps": steps, "depth": depth}


def sat(formulas):
    """Independent Tseitin CNF + DPLL, returning an assignment witness, never a timeout label."""
    ids, clauses = {}, []
    def fresh(key):
        if key not in ids:
            ids[key] = len(ids)+1
        return ids[key]
    def encode(f):
        if isinstance(f, str):
            return fresh(f)
        args = [encode(x) for x in f[1:]]
        key = json.dumps(f, sort_keys=True)
        if key in ids:
            return ids[key]
        out = fresh(key)
        for bits in product((False, True), repeat=len(args)):
            if f[0] == "¬": value = not bits[0]
            elif f[0] == "∧": value = bits[0] and bits[1]
            elif f[0] == "∨": value = bits[0] or bits[1]
            elif f[0] == "⊕": value = bits[0] != bits[1]
            elif f[0] == "→": value = not bits[0] or bits[1]
            else: raise ValueError(f[0])
            clauses.append([(-var if bit else var) for var, bit in zip(args, bits)] + [out if value else -out])
        return out
    for f in formulas:
        clauses.append([encode(f)])
    def solve(cs, assignment):
        while True:
            if not cs: return assignment
            if any(not c for c in cs): return None
            unit = next((c[0] for c in cs if len(c) == 1), None)
            if unit is None: break
            assignment = {**assignment, abs(unit): unit > 0}
            cs = [[x for x in c if x != -unit] for c in cs if unit not in c]
        choice = min(cs, key=len)[0]
        for value in (choice, -choice):
            answer = solve(cs+[[value]], assignment.copy())
            if answer is not None: return answer
        return None
    answer = solve(clauses, {})
    if answer is None: return None
    return {name: answer.get(number, False) for name, number in ids.items() if not name.startswith("[")}
