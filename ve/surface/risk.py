"""Risk English forms and their single, profile-scoped readings.

The policy parser receives these as profile words. Record conditions retain
their W6 condition text for the annotated condition decoder; this module never
interprets a condition or decides a risk cell.
"""
from __future__ import annotations

from ..errors import SyntaxError, UnsupportedProfile
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


def parse_wording(text, env, *, actions=(), harms=(), classes=(), context="guard"):
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
    if type(actions) is not dict or type(harms) is not dict or type(classes) is not dict:
        raise SyntaxError("Risk wording names must be label-to-name maps")
    possibilities = []
    for action_label, action in actions.items():
        for harm_label, harm in harms.items():
            for tag, phrase in (("might", "might lead to"), ("cannot", "cannot lead to"),
                                ("leads", "leads to"), ("might-not", "might not lead to")):
                if sentence == f"{action_label} {phrase} {harm_label}":
                    if context == "guard" or tag != "might-not":
                        possibilities.append({"form": tag, "action": action, "harm": harm})
            if context == "record":
                for harm_label, harm in harms.items():
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
