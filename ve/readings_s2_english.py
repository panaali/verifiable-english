"""Closed S2a report sentences (composition-s2.md, section 2).

The caller supplies checked evidence and the existing English surface's
``<conclusion>`` and ``<situation>``.  These functions never inspect raw rule
names, generated predicates or model tables.
"""

from __future__ import annotations

from .errors import VEError


def _clean(value: str) -> str:
    if type(value) is not str or any(x in value for x in ("ve__", "rd-", "soft__", "rights__", "may not")):
        raise VEError("InvalidInput: S2 wording needs checked English")
    return value


def _series(parts):
    parts = list(parts)
    if not parts:
        raise VEError("InvalidInput: S2 wording needs a reading")
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return " and ".join(parts)
    return ", ".join(parts[:-1]) + " and " + parts[-1]


def result_sentence(kind: str, *, conclusion=None, situation=None) -> str:
    """R1 to R6. The calling route gates proof and model kinds before use."""
    if kind == "conflict_free":
        return "no two rules on the same act contradict each other."
    if kind == "follows":
        return f"the conclusion follows: {_clean(conclusion)}"
    if kind == "countermodel":
        return f"the conclusion does not follow. It fails here: {_clean(situation)}."
    if kind == "conflict":
        return f"two rules contradict each other here: {_clean(situation)}."
    if kind == "premise_model":
        return f"the sentences of this document can all be true together, as here: {_clean(situation)}."
    if kind == "inconsistent":
        return "the sentences of this document cannot all be true together."
    raise VEError("InvalidInput: unknown S2 result sentence")


def every_result(open_count: int, kind: str, *, conclusion=None, nonempty_fallback=False) -> str:
    """E26, E10, or E11. E11 is reserved for the documented lifting fallback."""
    if type(open_count) is not int or open_count < 1:
        raise VEError("InvalidInput: S2 needs an open sentence")
    if kind not in {"conflict_free", "follows", "inconsistent"}:
        raise VEError("InvalidInput: every-reading wording needs certificates")
    result = result_sentence(kind, conclusion=conclusion)
    if nonempty_fallback:
        return f"Under every reading with at least one individual, {result}"
    if open_count == 1:
        return f"Under every reading of the open sentence, {result}"
    return f"Under every reading of the {open_count} open sentences, {result}"


def named_result(readings, result: str) -> str:
    """E12. A model caller must pass its complete encoded choice."""
    readings = list(readings)
    subjects = [f"sentence {number} as {_clean(name)}" for number, name in readings]
    if any(type(number) is not int or number < 1 for number, _ in readings):
        raise VEError("InvalidInput: invalid S2 sentence number")
    return f"Read {_series(subjects)}: {_clean(result)}"


def one_reading(number: int, count: int) -> str:
    """E4, justified by a used :one premise."""
    if type(number) is not int or number < 1 or type(count) is not int or count < 1:
        raise VEError("InvalidInput: invalid S2 reading count")
    return f"Sentence {number} is read in exactly one of its {count} listed ways."


QUIET = ("A way of reading a sentence that is not taken adds nothing: its exception, switch, "
         "limitation and bar conditions hold nowhere.")


def narrowed(number: int, reading: str, citation: str) -> str:
    """E7, once per candidate dropped by a used narrowing premise."""
    return f"Sentence {number} is not read as {_clean(reading)}, because of {_clean(citation)}."


def independent(number: int) -> str:
    """E13, only when no used certificate leaf mentions this set's bits."""
    if type(number) is not int or number < 1:
        raise VEError("InvalidInput: invalid S2 sentence number")
    return f"This does not depend on how sentence {number} is read."


def dead_reading(number: int, reading: str) -> str:
    """E17, only after a checked dead-reading certificate; not for narrowing drops."""
    return f"No compatible way of reading the open sentences reads sentence {number} as {_clean(reading)}."


def none_result(open_count: int) -> str:
    """E27, only after a checked countermodel for every compatible choice."""
    if type(open_count) is not int or open_count < 2:
        raise VEError("InvalidInput: E27 needs at least two open sentences")
    return f"Under no reading of the {open_count} open sentences does the conclusion follow."


OVER_BUDGET = "VE did not check every way of reading the open sentences: there are more than 64."


def not_superposed(citation: str) -> str:
    """E29, for the enumerated soft or norms fallback finding."""
    return f"The readings of {_clean(citation)} were checked one way at a time, not together."
