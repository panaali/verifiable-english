"""S2a's deterministic choice encoding and compatible-choice search.

These are elaboration inputs, not verdicts.  A verdict needs the S2 Lean replay
and its checked evidence; callers must not infer ALL from this module alone.
The order here is the source order of ``Document.sets`` and candidate order.
"""

from __future__ import annotations

from copy import deepcopy

from .errors import VEError
from .readings_s1 import Content, decode_content

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


def sup_ready(sets, couplings=(), narrowings=()) -> bool:
    """The shape conjuncts of S2 1.8, including the active-version checks.

    The decoder has further checks, notably a shared coupling label value.
    This predicate deliberately mirrors only ``supReady`` in the spec.
    """
    ids = [reading_set.id for reading_set in sets]
    if len(ids) != len(set(ids)) or any(
            not reading_set.candidates or any(a.content is None for a in reading_set.candidates)
            for reading_set in sets):
        return False
    by_version = {(reading_set.id, reading_set.version): reading_set for reading_set in sets}
    if len({item["id"] for item in couplings}) != len(couplings):
        return False
    for coupling in couplings:
        refs = [(ref["set"], ref["version"]) for ref in coupling["sets"]]
        if (len(refs) < 2 or len({set_id for set_id, _ in refs}) != len(refs)
                or any(ref not in by_version for ref in refs)):
            return False
        if any(coupling["axis"] not in candidate.labels
               for ref in refs for candidate in by_version[ref].candidates):
            return False
    if len({item["id"] for item in narrowings}) != len(narrowings):
        return False
    for narrowing in narrowings:
        reading_set = by_version.get((narrowing["set"], narrowing["version"]))
        if reading_set is not None:
            candidate_ids = {a.id for a in reading_set.candidates}
            if not narrowing["keeps"] or not set(narrowing["keeps"]) <= candidate_ids:
                return False
    return True


def position(sets, set_id: str, index: int) -> int:
    """The 1-based candidate position across all open sets."""
    before = 0
    for reading_set in sets:
        if reading_set.id == set_id:
            if 0 <= index < len(reading_set.candidates):
                return before + index + 1
            break
        before += len(reading_set.candidates)
    raise ValueError("candidate outside active reading sets")


def qualify(number: int, name: str) -> str:
    return f"rd-{number}-{name}"


def copies(doc, name: str) -> list[str]:
    """All qualified copies of an interface rule, or the fixed rule name."""
    for reading_set in doc.sets:
        if ("rule", name) in doc.interface_of(reading_set):
            return [qualify(position(doc.sets, reading_set.id, index), name)
                    for index in range(len(reading_set.candidates))]
    return [name]


def uniform_precedence(doc) -> bool:
    """S2 1.8's protection against an unchosen copy yielding to a fixed child."""
    for _, fixed in doc.fixed_units():
        if fixed.kind != "norm":
            continue
        for name in fixed.body.get("over", []):
            for reading_set in doc.sets:
                if ("rule", name) not in doc.interface_of(reading_set):
                    continue
                parents = [frozenset(a.content.body.get("over", [])) for a in reading_set.candidates
                           if a.content is not None and a.content.kind == "norm"
                           and a.content.body.get("name") == name]
                if len(parents) != len(reading_set.candidates) or len(set(parents)) != 1:
                    return False
    return True


def choice_contents(doc, choice):
    """Every fixed unit and chosen candidate at its source position, own names."""
    if list(choice) != [reading_set.id for reading_set in doc.sets] or any(
            type(choice[R.id]) is not int or not 0 <= choice[R.id] < len(R.candidates)
            for R in doc.sets):
        raise VEError("InvalidInput: incomplete reading choice")
    return doc.build(lambda _: True, lambda R: R.candidates[choice[R.id]])


def superposed_contents(doc):
    """S2a's gated assertions and norms in S1's source order.

    This is a raw content transformation. A caller must extend the frame with
    ``choice_vocabulary`` and run the lower chain's well-formedness check before
    treating the result as superposable.
    """
    if any(a.content is None for R in doc.sets for a in R.candidates):
        raise VEError("InvalidInput: pending reading cannot be superposed")
    out = []
    for item in doc.items:
        if item[0] == "bar":
            raise VEError("UnsupportedProfile: rights superposition is S2b")
        if item[0] == "fixed":
            content = item[2]
            if content.kind != "norm":
                out.append(content)
                continue
            raw = deepcopy(content.raw)
            raw["norm"]["over"] = [copy for name in content.body.get("over", [])
                                    for copy in copies(doc, name)]
            if "cites" in raw:
                cites = {}
                for key, value in raw["cites"].items():
                    if key.startswith("over:"):
                        for name in copies(doc, key[5:]):
                            cites["over:" + name] = value
                    else:
                        cites[key] = value
                raw["cites"] = cites
            out.append(decode_content(raw))
            continue
        reading_set = item[2]
        number = next(i for i, R in enumerate(doc.sets, 1) if R.id == reading_set.id)
        for index, candidate in enumerate(reading_set.candidates):
            content = candidate.content
            atom = pattern(number, len(reading_set.candidates), index)
            if content.kind == "assertion":
                out.append(decode_content(["implies", atom, deepcopy(content.body)]))
            elif content.kind == "norm":
                raw = deepcopy(content.raw)
                rule = raw["norm"]
                rule["name"] = qualify(position(doc.sets, reading_set.id, index), rule["name"])
                rule["guard"] = ["and", rule.get("guard", ["top"]), atom]
                exception = rule.get("exception")
                if isinstance(exception, dict) and isinstance(exception.get("sufficient"), list):
                    exception["sufficient"] = [["and", formula, atom]
                                               for formula in exception["sufficient"]]
                out.append(decode_content(raw))
            else:
                raise VEError("UnsupportedProfile: rights superposition is S2b")
    return out


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
