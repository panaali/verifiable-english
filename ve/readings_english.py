"""Report-only English for the S1 reading wrapper.

These sentences describe checked metadata. They are never document input.
"""

from __future__ import annotations

from .errors import VEError

SOURCE_WORDS = frozenset({"shall", "shall not", "should", "should not", "shouldn't",
                          "must", "must not", "always", "never"})


E22 = ("Where this sentence applies and a rule that says must, must not, may or need not "
       "decides the same act the other way, (1) contradicts that rule and (2) gives way to it.")
E23 = ("Under (1), a rule on the same act that says should, should not, generally may or "
       "generally need not gives way wherever (1) applies. Under (2), it gives way only "
       "as the ranks of the two rules decide.")
E24 = "These two readings differ in a checked situation that VE cannot yet show in words."


def subject(values):
    """The element names of a typed probe tuple, in its declared slot order."""
    return _series(values)


def outcome_sentence(role, value, subject_name):
    if type(value) is not bool or role not in {"obligation", "permission"}:
        raise VEError("InvalidInput: outcome wording needs a checked deontic value")
    if role == "obligation":
        return f"{subject_name} still must" if value else f"{subject_name} is not required to"
    return f"{subject_name} is permitted to" if value else f"{subject_name} is not permitted to"


def force_twin_sentence(source_word, strict_paraphrase, default_paraphrase,
                        decider, tuple_values, role, strict_value, default_value):
    """E14, after its four semantic gates and the source-word gate pass."""
    if source_word not in SOURCE_WORDS:
        raise VEError("InvalidInput: E14 needs a source word")
    who = "the decider" if decider == "unstated" else decider
    names = subject(tuple_values)
    first = outcome_sentence(role, strict_value, tuple_values[0])
    second = outcome_sentence(role, default_value, tuple_values[0])
    return (f"This sentence says *{source_word}*. (1) *{strict_paraphrase}* "
            f"(2) *{default_paraphrase}* They differ here: suppose {who} decides "
            f"the exception applies to {names}. Under (1) {first}. Under (2) {second}.")


def decision_only_sentence(decider):
    """E25, shown for the finding `SeparatedByDecisionOnly` in place of E15.

    E15 states what `decision_only_sound` would prove, and that theorem is not
    proved yet (DRI ruling 2 of 2026-10-02): the finding is not certified, and
    the sentence says so instead of stating the claim as checked.
    """
    who = "the decider" if decider == "unstated" else decider
    return (f"It is not certified that these two readings differ only where {who} "
            "decides that the exception applies.")


def act_only_sentence(first_act, second_act):
    """E16, emitted only when each reading regulates one different act."""
    return (f"These two readings are about different acts: *{first_act}* / *{second_act}*. "
            "No situation separates them on a shared act.")


def outcome_pair_sentence(situation, witness, other, role, subject_name, value,
                          *, other_admissible, other_value=None):
    """E19. `other_value` is present only after a single checked evaluation."""
    first = f"Under {witness}, {outcome_sentence(role, value, subject_name)}."
    if not other_admissible:
        second = f"Under {other}, this situation is ruled out, whatever is decided."
    elif other_value is not None:
        second = f"Under {other}, {outcome_sentence(role, other_value, subject_name)}."
    else:
        second = f"Under {other} that is not so, whatever is decided."
    return f"These two readings differ here: {situation}. {first} {second}"


def assertion_pair_sentence(situation, true_reading, false_reading):
    """E21 is only for two assertion candidates with checked opposite values."""
    return (f"These two readings differ here: {situation}. Under {true_reading}, "
            f"the sentence is true there. Under {false_reading}, it is false there.")


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
