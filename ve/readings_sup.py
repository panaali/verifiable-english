"""S2a's deterministic choice encoding and compatible-choice search.

These are elaboration inputs, not verdicts.  A verdict needs the S2 Lean replay
and its checked evidence; callers must not infer ALL from this module alone.
The order here is the source order of ``Document.sets`` and candidate order.
"""

from __future__ import annotations

MAX_CHOICES = 64
READING_SORT = "ve__reading"
HERE = "ve__here"


def bits_of(count: int) -> int:
    """The least number of bits representing every index below ``count``."""
    if count < 1:
        raise ValueError("a reading set needs at least one candidate")
    return (count - 1).bit_length()


def bit_name(position: int, bit: int) -> str:
    return f"ve__bit__{position}__{bit}"


def _fold(tag: str, empty: str, formulas: list) -> list:
    if not formulas:
        return [empty]
    result = formulas[-1]
    for formula in reversed(formulas[:-1]):
        result = [tag, formula, result]
    return result


def conj(formulas: list) -> list:
    return _fold("and", "top", formulas)


def disj(formulas: list) -> list:
    return _fold("or", "bottom", formulas)


def pattern(position: int, count: int, index: int) -> list:
    """The choice atom, least significant bit first, in Lean's tree shape."""
    if position < 1 or index < 0 or index >= 1 << bits_of(count):
        raise ValueError("invalid choice pattern")
    return conj([(["unary", bit_name(position, bit), ["const", HERE]] if index & (1 << bit)
                  else ["not", ["unary", bit_name(position, bit), ["const", HERE]]])
                 for bit in range(bits_of(count))])


def choice_atom(sets, set_id: str, index: int) -> list:
    for position, reading_set in enumerate(sets, 1):
        if reading_set.id == set_id:
            return (pattern(position, len(reading_set.candidates), index)
                    if 0 <= index < len(reading_set.candidates) else ["bottom"])
    return ["bottom"]


def choice_vocabulary(sets) -> dict:
    """The one added sort and constant, and bit predicates in source order."""
    if not sets:
        return {"sorts": [], "constants": {}, "predicates": {}}
    return {"sorts": [READING_SORT], "constants": {HERE: READING_SORT},
            "predicates": {bit_name(position, bit): [READING_SORT]
                           for position, reading_set in enumerate(sets, 1)
                           for bit in range(bits_of(len(reading_set.candidates)))}}


def in_force(reading_set, narrowing: dict) -> bool:
    return reading_set.id == narrowing["set"] and reading_set.version == narrowing["version"]


def compatible(sets, choice: dict[str, int], couplings=(), narrowings=()) -> bool:
    """Exactly one valid index per active set, with all active restrictions."""
    if list(choice) != [reading_set.id for reading_set in sets]:
        return False
    by_id = {reading_set.id: reading_set for reading_set in sets}
    if any(type(choice[reading_set.id]) is not int or
           not 0 <= choice[reading_set.id] < len(reading_set.candidates)
           for reading_set in sets):
        return False
    for coupling in couplings:
        labels = [by_id[ref["set"]].candidates[choice[ref["set"]]].labels.get(coupling["axis"])
                  for ref in coupling["sets"]]
        if any(label is None or label != labels[0] for label in labels):
            return False
    for narrowing in narrowings:
        reading_set = by_id.get(narrowing["set"])
        if reading_set is not None and in_force(reading_set, narrowing):
            if reading_set.candidates[choice[reading_set.id]].id not in narrowing["keeps"]:
                return False
    return True


def choices(sets, couplings=(), narrowings=(), *, limit=MAX_CHOICES):
    """Return at most ``limit + 1`` compatible choices and an over-budget flag.

    The extra choice distinguishes exactly 64 from more than 64.  A stale
    narrowing is ignored, as required by S2 1.2.
    """
    if limit < 0:
        raise ValueError("negative choice limit")
    result: list[dict[str, int]] = []
    selected: dict[str, int] = {}

    def visit(position: int):
        if len(result) > limit:
            return
        if position == len(sets):
            if compatible(sets, selected, couplings, narrowings):
                result.append(dict(selected))
            return
        reading_set = sets[position]
        for index in range(len(reading_set.candidates)):
            selected[reading_set.id] = index
            visit(position + 1)
            if len(result) > limit:
                break
        selected.pop(reading_set.id, None)

    visit(0)
    return result, len(result) > limit


def one_premises(sets):
    """Exclude unused bit patterns, omitting labels with no formula."""
    labelled = []
    for position, reading_set in enumerate(sets, 1):
        count = len(reading_set.candidates)
        unused = [["not", pattern(position, count, index)]
                  for index in range(count, 1 << bits_of(count))]
        if unused:
            labelled.append((f"readings:{reading_set.id}@{reading_set.version}:one", conj(unused)))
    return labelled


def coupling_premises(sets, couplings):
    by_id = {reading_set.id: reading_set for reading_set in sets}
    labelled = []
    for coupling in couplings:
        forbidden = []
        refs = coupling["sets"]
        for left_ref, right_ref in zip(refs, refs[1:]):
            left, right = by_id[left_ref["set"]], by_id[right_ref["set"]]
            for i, a in enumerate(left.candidates):
                for j, b in enumerate(right.candidates):
                    if a.labels[coupling["axis"]] != b.labels[coupling["axis"]]:
                        forbidden.append(["not", ["and", choice_atom(sets, left.id, i),
                                                  choice_atom(sets, right.id, j)]])
        if forbidden:
            labelled.append((f"coupling:{coupling['id']}", conj(forbidden)))
    return labelled


def narrowing_premises(sets, narrowings):
    labelled = []
    for narrowing in narrowings:
        for reading_set in sets:
            if in_force(reading_set, narrowing):
                dropped = [["not", choice_atom(sets, reading_set.id, i)]
                           for i, a in enumerate(reading_set.candidates) if a.id not in narrowing["keeps"]]
                if dropped:
                    labelled.append((f"narrowing:{narrowing['id']}", conj(dropped)))
                break
    return labelled


def choice_core(sets, couplings=(), narrowings=()):
    """Labelled closed formulas over the bits; quiescence is added separately."""
    return (one_premises(sets) + coupling_premises(sets, couplings) +
            narrowing_premises(sets, narrowings))


def unsatisfiable_ids(sets, couplings=(), narrowings=()):
    """The diagnostic's restriction ids, if bottom is later certified by Lean."""
    active = {(reading_set.id, reading_set.version) for reading_set in sets}
    return ", ".join(sorted([item["id"] for item in couplings] +
                            [item["id"] for item in narrowings
                             if (item["set"], item["version"]) in active]))
