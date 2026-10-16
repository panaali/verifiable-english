"""Mutants of a genuine Lean answer, generated from the Lean shapes, each with the generic checker's predicted verdict.

`mutants(mode, case, row)` places every leaf of the answer (`ve.backends.shape_binding.classify`) and mutates
each one, each array and map, and several fields at once:

* a leaf: `flip` (its last letter or digit changed, keeping its format where the format allows, to a value
  the request does not hold), `plus` and `minus` (an integer moved by one), `exceed` (an integer far above any
  bound) and `swap` (the value of another leaf of the same pattern in this answer);
* an array of `items`: `drop` (its last element), `duplicate` (its first element repeated), `reverse`, and
  `replace` (its first element written over its last: the SOME-to-ALL fault of tests/test_discourse_answer.py);
* a map: `drop-entry` and `rename-key`;
* coordinated, several fields at once: `drop+count` and `duplicate+count` (an array and the integer that
  counts it, moved together: the counter a shape names by `x-count-where`, or a sibling integer equal to the
  array's length), and `rename` (one string the request names, changed to the same new value everywhere in
  the answer, keys included, so every internal agreement still holds).

Each mutant carries the verdict the shapes predict (`refuse`, `accept` or `either` when the shapes alone do
not decide it): a mutant of a bound or closed leaf, or one that breaks a leaf's format, an array's bound
length or a counter, is refused; a mutant that changes only leaves of no class is accepted. The prediction
reads the classification only; the verdict is `service_schema`'s (`tests/test_shape_binding_mutants.py`).
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
import re

from ve.backends import shape_binding
from ve.backends.service_schema import Invalid, check_row, same_json

REFUSE, ACCEPT, EITHER = "refuse", "accept", "either"
# Relations under which another value is refused: the leaf must equal one request value.
EXACT = {"echoes", "equals", "indexes", "counts"}
EXCEED = 10 ** 9


@dataclass
class Mutant:
    kind: str
    path: str        # the pattern of the mutated field (shape_binding paths)
    where: tuple     # its concrete path
    row: object      # the mutated answer
    expect: str
    why: str


def request_strings(value) -> set:
    found, pending = set(), [value]
    while pending:
        item = pending.pop()
        if type(item) is str:
            found.add(item)
        elif isinstance(item, list):
            pending.extend(item)
        elif isinstance(item, dict):
            found.update(item)
            pending.extend(item.values())
    return found


def _next(char: str) -> str:
    for low, high in (("0", "9"), ("a", "f"), ("g", "z"), ("A", "Z")):
        if low <= char <= high:
            return low if char == high else chr(ord(char) + 1)
    return ""


def flips(value: str):
    """Values that differ from `value` in one letter or digit, from the last one back."""
    for i in range(len(value) - 1, -1, -1):
        new = _next(value[i])
        if new:
            yield value[:i] + new + value[i + 1:]
    yield value + "x"


def violates(leaf, value) -> bool:
    """Whether `value` breaks the leaf's own format or closed domain."""
    if leaf.domain is not None and not any(same_json(value, option) for option in leaf.domain):
        return True
    for keyword, bound in leaf.format:
        if keyword == "pattern" and type(value) is str and re.fullmatch(bound, value, re.DOTALL) is None:
            return True
        if keyword == "minLength" and type(value) is str and len(value) < bound:
            return True
        if keyword == "maxLength" and type(value) is str and len(value) > bound:
            return True
        if keyword == "minimum" and type(value) is int and value < bound:
            return True
    return False


def _flip(value: str, leaf, avoid: set) -> str:
    """The first flip the request does not hold that keeps the leaf's format, else the first it does not hold."""
    candidates = [new for new in flips(value) if new not in avoid]
    return next((new for new in candidates if not violates(leaf, new)), candidates[0])


def _get(row, where):
    node = row
    for step in where:
        node = node[step]
    return node


def _set(row, where, value):
    out = deepcopy(row)
    parent = _get(out, where[:-1])
    if isinstance(where[-1], shape_binding._Key):
        items = list(parent.items())
        parent.clear()
        parent.update((value if k == where[-1] else k, v) for k, v in items)
    else:
        parent[where[-1]] = value
    return out


def leaf_expectation(leaf, old, new, kind: str = "flip") -> tuple[str, str]:
    """The verdict the shapes predict for a leaf changed from `old` to `new` by a mutation of `kind` (`swap`
    takes another value of this answer; every other kind, a value the request does not hold)."""
    if violates(leaf, new):
        return REFUSE, "breaks its format or domain"
    binding = leaf.binding
    if binding.cls == "closed domain":
        return EITHER, "another member of its closed domain"
    if binding.cls == "none" and binding.relation == "agrees":
        # One side of `x-equal-fields` changed alone no longer agrees; a rename changes both sides.
        return (ACCEPT, "both sides agree again") if kind == "rename" else (REFUSE, "its copy no longer agrees")
    if binding.cls == "none":
        return ACCEPT, "no class"
    relation = f"{binding.relation} ({binding.keyword})"
    if binding.relation == "is bounded by":
        return (REFUSE, "exceeds its bound") if kind == "exceed" else (EITHER, relation)
    if kind == "swap":
        if binding.relation == "references":
            return EITHER, "another member of the request set"
        if binding.at is not None:
            return EITHER, "an internal agreement may hold for another value"
    if binding.relation in EXACT or binding.relation == "references":
        return REFUSE, relation
    return EITHER, relation


def _leaf_mutants(row, placed, named):
    by_path: dict = {}
    for where, value, leaf in placed:
        by_path.setdefault((leaf.path, leaf.kind), []).append(value)
    seen = set()
    for where, value, leaf in placed:
        if (leaf.path, leaf.kind, "first") in seen and (leaf.path, leaf.kind, "last") in seen:
            continue
        seen.add((leaf.path, leaf.kind, "first" if (leaf.path, leaf.kind, "first") not in seen else "last"))
        changes = []
        if leaf.kind in ("string", "key"):
            new = _flip(value, leaf, named | {value})
            changes.append(("flip", new))
        else:
            changes += [("plus", value + 1), ("minus", value - 1), ("exceed", value + EXCEED)]
        others = [v for v in by_path[(leaf.path, leaf.kind)] if not same_json(v, value)]
        if others and leaf.kind != "key":
            changes.append(("swap", others[0]))
        for kind, new in changes:
            expect, why = leaf_expectation(leaf, value, new, kind)
            yield Mutant(kind, leaf.path, where, _set(row, where, new), expect, why)


def _containers(value, where=()):
    """(concrete path, value) of every array and object of the answer."""
    pending = [(value, where)]
    while pending:
        node, at = pending.pop()
        if isinstance(node, (list, dict)):
            yield at, node
            items = enumerate(node) if isinstance(node, list) else node.items()
            pending.extend((child, at + (key,)) for key, child in items)


def _structure_mutants(row, placed, census):
    """Array and map mutants, alone and with their counters."""
    arrays = {}
    for node in census.arrays:
        # Conjuncts at one path (a `$ref`'d list and the bounds its referrer adds) bind together.
        old = arrays.get(node.path)
        if old is not None:
            lows = [n for n in (old.items[0], node.items[0]) if n is not None]
            highs = [n for n in (old.items[1], node.items[1]) if n is not None]
            node = replace(node, length=old.length or node.length, positional=old.positional or node.positional,
                           fixed=old.fixed or node.fixed, agrees=old.agrees or node.agrees,
                           unique=old.unique or node.unique,
                           items=(max(lows) if lows else None, min(highs) if highs else None))
        arrays[node.path] = node
    # The pattern of each concrete container: the parent pattern of its leaves.
    patterns: dict = {}
    for where, value, leaf in placed:
        steps = leaf.path.split("/")[1:]
        if len(steps) == len(where):
            for depth in range(len(where)):
                patterns.setdefault(where[:depth], "/" + "/".join(steps[:depth]) if depth else "/")
    leaves_under: dict = {}
    for where, value, leaf in placed:
        for depth in range(len(where)):
            leaves_under.setdefault(where[:depth], []).append(leaf)
    counters = _counters(row, placed)
    key_leaves: dict = {}
    for where, value, leaf in placed:
        if leaf.kind == "key":
            key_leaves.setdefault(where[:-1], []).append((value, leaf))
    for at, node in _containers(row):
        path = patterns.get(at)
        if path is None:
            continue
        under = leaves_under.get(at, [])
        touched = any(leaf.binding.cls == "bound" and leaf.binding.at is not None
                      and leaf.binding.keyword != "x-count-where" for leaf in under)
        if isinstance(node, list) and node and path in arrays and "~" not in path.rsplit("/", 1)[-1]:
            array = arrays[path]
            if array.fixed:
                continue
            variants = {"drop": node[:-1], "duplicate": [node[0], *node]}
            if len(node) > 1 and not same_json(node[0], node[-1]):
                variants["reverse"] = node[::-1]
                variants["replace"] = [*node[:-1], node[0]]
            low, high = array.items
            for kind, new in variants.items():
                length_changed = len(new) != len(node)
                if low is not None and len(new) < low or high is not None and len(new) > high:
                    expect, why = REFUSE, "breaks its minItems or maxItems"
                elif array.unique and kind in ("duplicate", "replace"):
                    expect, why = REFUSE, "its strings are distinct (x-unique-strings)"
                elif array.agrees and (length_changed or array.agrees == "x-equal-fields"):
                    expect, why = REFUSE, f"no longer agrees with its sibling ({array.agrees})"
                elif length_changed and array.length:
                    expect, why = REFUSE, f"length bound by {array.length}"
                elif array.positional in ("x-equals", "x-echo"):
                    expect, why = REFUSE, f"equal to a request list ({array.positional})"
                elif array.positional:
                    expect, why = EITHER, f"positions bound by {array.positional}"
                elif touched:
                    expect, why = EITHER, "an ancestor keyword binds its elements"
                elif length_changed and any(leaf.binding.cls == "bound" for _, leaf in counters.get(at, [])):
                    expect, why = REFUSE, "its counter no longer counts it"
                else:
                    expect, why = ACCEPT, "neither its length nor its order is bound"
                yield Mutant(kind, path, at, _set(row, at, new) if at else new, expect, why)
                for counter in counters.get(at, []) if length_changed else []:
                    count_where, count_leaf = counter
                    mutated = _set(_set(row, at, new) if at else new, count_where, len(new))
                    if low is not None and len(new) < low or high is not None and len(new) > high:
                        expect, why = REFUSE, "breaks its minItems or maxItems"
                    elif array.unique and kind == "duplicate":
                        expect, why = REFUSE, "its strings are distinct (x-unique-strings)"
                    elif array.agrees:
                        expect, why = REFUSE, f"no longer agrees with its sibling ({array.agrees})"
                    elif array.length:
                        expect, why = REFUSE, f"length bound by {array.length}"
                    elif violates(count_leaf, len(new)):
                        expect, why = REFUSE, "its counter breaks its format"
                    elif count_leaf.binding.relation in EXACT and count_leaf.binding.at is None:
                        expect, why = REFUSE, f"its counter is bound by {count_leaf.binding.keyword}"
                    elif touched or array.positional:
                        expect, why = EITHER, "an ancestor keyword binds its elements"
                    else:
                        expect, why = ACCEPT, "the array and its counter agree; neither is bound to the request"
                    yield Mutant(f"{kind}+count", path, at, mutated, expect, why)
        elif isinstance(node, dict) and node and key_leaves.get(at):
            victim, key_leaf = key_leaves[at][-1]
            dropped = {k: v for k, v in node.items() if k != victim}
            expect, why = (ACCEPT, "map keys are bound by no keyword") if key_leaf.binding.cls == "none" and \
                not touched else (EITHER, "its keys are bound")
            yield Mutant("drop-entry", path, at, _set(row, at, dropped) if at else dropped, expect, why)


def _counters(row, placed) -> dict:
    """{array path: [(concrete path, leaf)]}: the integers that count each array of the answer, the ones a
    shape binds by `x-count-where` and the sibling integers equal to its length."""
    found: dict = {}
    by_where = {where: (value, leaf) for where, value, leaf in placed}
    # The counters a shape binds (`x-count-where` over every element), matched to the arrays they count.
    arrays: dict = {}
    for at, node in _containers(row):
        if isinstance(node, list):
            arrays.setdefault(_concrete_pattern(at), []).append(at)
    for where, value, leaf in placed:
        if leaf.binding.of is not None and len(arrays.get(leaf.binding.of, [])) == 1:
            found.setdefault(arrays[leaf.binding.of][0], []).append((where, leaf))
    for at, node in _containers(row):
        if not isinstance(node, dict):
            continue
        for name, item in node.items():
            if not isinstance(item, list):
                continue
            for other, value in node.items():
                where = at + (other,)
                if other != name and type(value) is int and value == len(item) and where in by_where:
                    found.setdefault(at + (name,), []).append((where, by_where[where][1]))
    return found


def _concrete_pattern(where) -> str:
    return "/" + "/".join("*" if type(step) is int else str(step) for step in where) if where else "/"


def _rename_mutants(row, placed, named):
    """One request-named string changed to the same new value everywhere in the answer."""
    occurrences: dict = {}
    for where, value, leaf in placed:
        if type(value) is str and value in named and value:
            occurrences.setdefault(value, []).append((where, leaf))
    for value, places in sorted(occurrences.items()):
        if len(places) < 2:
            continue
        new = _flip(value, places[0][1], named | {value})
        mutated = row
        for where, leaf in sorted(places, key=lambda p: len(p[0]), reverse=True):
            mutated = _set(mutated, where, new)
        verdicts = [leaf_expectation(leaf, value, new, "rename") for _, leaf in places]
        if any(v == REFUSE for v, _ in verdicts):
            expect, why = REFUSE, next(w for v, w in verdicts if v == REFUSE)
        elif all(v == ACCEPT for v, _ in verdicts):
            expect, why = ACCEPT, "every occurrence is a leaf of no class"
        else:
            expect, why = EITHER, "an occurrence is in a closed domain or a set"
        yield Mutant("rename", ",".join(sorted({leaf.path for _, leaf in places})), places[0][0], mutated, expect, why)


def mutants(mode: str, case, row, index: int = 0) -> list[Mutant]:
    """Every mutant of `row` (an answer to `case`) with the verdict the shapes predict."""
    placed, census = shape_binding.classify(mode, case, row, index)
    named = request_strings(case)
    out = list(_leaf_mutants(row, placed, named))
    out += list(_structure_mutants(row, placed, census))
    out += list(_rename_mutants(row, placed, named))
    return out


def verdict(mode: str, case, row, index: int = 0) -> str:
    """The generic checker's verdict on an answer: `accept` or `refuse`."""
    try:
        check_row(mode, row, case, index)
    except Invalid:
        return REFUSE
    return ACCEPT
