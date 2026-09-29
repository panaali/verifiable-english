"""Risk English forms and their single, profile-scoped readings.

The policy parser receives these as profile words. Record conditions retain
their W6 condition text for the annotated condition decoder; this module never
interprets a condition or decides a risk cell.
"""
from __future__ import annotations

from ..errors import SyntaxError, UnsupportedProfile, VEError
from .registry import SurfaceRecord, register


for tag, strict, wording, production in (
    ("might", "risk__might_lead_to", "{0} might lead to {1}", "action might lead to harm"),
    ("cannot", "not risk__might_lead_to", "{0} cannot lead to {1}", "action cannot lead to harm"),
    ("leads", "leads_to", "{0} leads to {1}", "action leads to harm"),
    ("might-not", "not leads_to", "{0} might not lead to {1}", "action might not lead to harm"),
    ("class", "risk__class", "{0} is {1}", "harm is severity class"),
    ("or-worse", "risk__or_worse", "{0} is {1} or worse", "harm is class or worse"),
    ("less-worst", "risk__less_worst", "{0} has a less severe worst case than {1}",
     "action has a less severe worst case than action"),
    ("necessary", "necessary", "{0} cannot lead to {1} unless {condition}",
     "record necessary condition"),
    ("exact", "exact", "{0} leads to {1} exactly when {condition}",
     "record exact condition"),
):
    register(SurfaceRecord(f"risk-{tag}", strict, (), wording, production,
                           profiles=("risk@0",)))


def parse_wording(text, env, *, actions=None, harms=None, classes=None, context="guard"):
    """Read one canonical risk atom or record statement.

    `actions` and `harms` are record-local label-to-name maps; a policy caller
    may pass constant spellings instead. Conditions are returned as text for
    W6's decoder. The pending sufficient form is deliberately not registered.
    """
    if "risk@0" not in env.profiles:
        raise UnsupportedProfile("risk@0 is required for risk wordings")
    if type(text) is not str or not text.endswith("."):
        raise SyntaxError("A risk wording is one complete sentence")
    sentence = text[:-1]
    if " may lead to " in sentence:
        raise SyntaxError("Use 'might lead to', because 'may' is permission")
    if " does not lead to " in sentence:
        raise SyntaxError("Choose 'cannot lead to' or 'might not lead to'")
    if " prevents " in sentence:
        raise SyntaxError("Use 'might prevent' in a risk environment")
    if " is safer than " in sentence:
        raise SyntaxError("Use 'has a less severe worst case than' for the declared severity order")
    if " leads to " in sentence and " if " in sentence:
        raise SyntaxError("Sufficient-condition wording is pending; use form sufficient in JSON")
    if context == "record" and " might not lead to " in sentence:
        raise SyntaxError("State a condition, or 'might lead to'; 'might not lead to' is computed")
    actions, harms, classes = ({} if m is None else m for m in (actions, harms, classes))
    if type(actions) is not dict or type(harms) is not dict or type(classes) is not dict:
        raise SyntaxError("Risk wording names must be label-to-name maps")
    possibilities = []
    # Each (action, harm) pair is tried once per wording: a reading is counted
    # once, so two harms never make one sentence ambiguous by themselves.
    for action_label, action in actions.items():
        for harm_label, harm in harms.items():
            for tag, phrase in (("might", "might lead to"), ("cannot", "cannot lead to"),
                                ("leads", "leads to"), ("might-not", "might not lead to")):
                if sentence == f"{action_label} {phrase} {harm_label}":
                    if context == "guard" or tag != "might-not":
                        possibilities.append({"form": tag, "action": action, "harm": harm})
            if context == "record":
                for tag, joiner in (("necessary", " cannot lead to " + harm_label + " unless "),
                                    ("exact", " leads to " + harm_label + " exactly when ")):
                    prefix = action_label + joiner
                    if sentence.startswith(prefix) and sentence[len(prefix):]:
                        possibilities.append({"form": tag, "action": action, "harm": harm,
                                              "condition_text": sentence[len(prefix):]})
        if context == "guard":
            for other_label, other in actions.items():
                if sentence == f"{action_label} has a less severe worst case than {other_label}":
                    possibilities.append({"form": "less-worst", "left": action, "right": other})
    if context == "guard":
        for harm_label, harm in harms.items():
            for class_label, klass in classes.items():
                if sentence == f"{harm_label} is {class_label}":
                    possibilities.append({"form": "class", "harm": harm, "class": klass})
                if sentence == f"{harm_label} is {class_label} or worse":
                    possibilities.append({"form": "or-worse", "harm": harm, "class": klass})
    if len(possibilities) != 1:
        raise SyntaxError("Risk wording has no unique registered reading")
    return possibilities[0]


def gap_lines(gaps):
    """Render Lean's structured decision gaps without inferring any new facts.

    The caller supplies only the gap categories of risk.md 5.2. In particular,
    a default decision is not presented as a risk classification, and a point
    estimate is flagged without asserting that the estimate is accurate.
    """
    fields = ("unexamined_possible", "assumed_ruled_out", "unranked_severities",
              "point_estimates", "default_decided", "dilemmas")
    if type(gaps) is not dict or set(gaps) - set(fields) or any(
            type(rows) is not list for rows in gaps.values()):
        raise VEError("InvalidInput: risk report gaps")
    def row(mapping, keys, path):
        if (type(mapping) is not dict or set(mapping) != keys
                or any(type(value) is not str or not value for value in mapping.values())):
            raise VEError(f"InvalidInput: risk.{path}")
    lines = []
    for cell in gaps.get("unexamined_possible", []):
        row(cell, {"action", "harm"}, "unexamined_possible")
        lines.append(f"Unexamined possible: {cell['action']} might lead to {cell['harm']}.")
    for cell in gaps.get("assumed_ruled_out", []):
        row(cell, {"action", "harm", "decider"}, "assumed_ruled_out")
        lines.append(f"Assumed ruled out by {cell['decider']}: {cell['action']} cannot lead to {cell['harm']}.")
    for pair in gaps.get("unranked_severities", []):
        row(pair, {"left", "right"}, "unranked_severities")
        lines.append(f"Unranked severities: {pair['left']} and {pair['right']} are not ranked.")
    for estimate in gaps.get("point_estimates", []):
        row(estimate, {"id", "result"}, "point_estimates")
        lines.append(f"Point estimate {estimate['id']}: {estimate['result']}.")
    for action in gaps.get("default_decided", []):
        if type(action) is not str:
            raise VEError("InvalidInput: risk.default_decided")
        lines.append(f"Default decided: {action}.")
    for diagnosis in gaps.get("dilemmas", []):
        if type(diagnosis) is not str:
            raise VEError("InvalidInput: risk.dilemmas")
        lines.append(f"Dilemma: {diagnosis}.")
    return tuple(lines)
