"""Report-only English for the S1 reading wrapper.

These sentences describe checked metadata. They are never document input.
"""

from __future__ import annotations


def _series(values):
    values = list(values)
    if len(values) == 1:
        return values[0]
    if len(values) == 2:
        return f"{values[0]} and {values[1]}"
    return ", ".join(values[:-1]) + " and " + values[-1]


def coupling_sentence(coupling, sets_by_id, units):
    """E5. Call only after the coupling has passed validation."""
    numbers = {unit["id"]: index for index, unit in enumerate(units, 1)}
    subjects = [str(numbers[sets_by_id[ref["set"]]["unit"]]) for ref in coupling["sets"]]
    citations = [str(numbers[unit]) for unit in coupling["reason_spans"]]
    axis = coupling["axis"]
    axis = axis if axis in {"bearer", "polarity", "incident", "force"} else f"label {axis}"
    citation = (f"sentence {citations[0]}" if len(citations) == 1 else
                f"sentences {_series(citations)}")
    return f"Sentences {_series(subjects)} are read with the same {axis}, because of {citation}."
