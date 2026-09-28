"""One-reading English explanations for rights document units.

These sentences expose the source incident kind and the exact soft rule that
it contributes. They are read-only until the W7 inverse grammar is installed.
"""
from __future__ import annotations

from ..errors import VEError
from ..norm_english import render_rule_sentence
from ..softnorms import decode_rule


def _line(document, right, line):
    kind = line["kind"]
    if kind == "power":
        rules = (line["liberty"], line["recognition"])
    elif "fan_out" in line:
        rules = tuple({**line["norm"], "predicate": predicate,
                       "name": f"{line['norm']['name']}-{sort}"}
                      for sort, predicate in sorted(line["fan_out"].items()))
    else:
        rules = (line["norm"],)
    explanations = []
    for raw in rules:
        rule = decode_rule(document.env, {"norm": raw})
        sentence = render_rule_sentence(rule.core, document.env)
        if rule.mode == "default":
            decider = (rule.exception or {}).get("decided_by") or document.env.soft.get("exception_decider") or "unstated"
            sentence += (f" This is a default line; {decider} decides its exception."
                         if decider != "unstated" else
                         " This is a default line; the source names no exception decider.")
        explanations.append(sentence)
    label = kind[0].upper() + kind[1:]
    return f"{label} of right {right}. " + " ".join(explanations)


def render_unit(document, content):
    if document is None or type(content) is not dict or len(content) != 1:
        raise VEError("InvalidInput: rights English unit")
    kind, body = next(iter(content.items()))
    if kind == "right":
        holder = body["holder"]
        header = f"Right {body['name']}. Every {holder} has the right described by its incident lines."
        return " ".join((header, *(_line(document, body["name"], line) for line in body["lines"])))
    if kind == "right_lines":
        return " ".join((f"Right {body['right']} includes:",
                         *(_line(document, body["right"], line) for line in body["lines"])))
    if kind == "limitation":
        scope = ("every right" if body["scope"] == "all" else
                 "rights " + " and ".join(body["scope"]))
        sentences = [f"Limitation {body['name']} applies to {scope}."]
        for condition in body["conditions"]:
            qualifier = "only where" if condition["role"] == "necessary" else "where"
            sentences.append(f"Limitation {body['name']} holds {qualifier} {condition['verbalisation']}.")
        if body["factors"]:
            sentences.append(f"Limitation {body['name']} takes account of " +
                             ", ".join(body["factors"]) + ".")
        return " ".join(sentences)
    if kind == "bar":
        if body["reading"] == "rule":
            return "Nothing in this document gives any bearer a right to an act aimed at the destruction of a right."
        return "Whether any right permits an act aimed at the destruction of a right is checked, not ruled."
    raise VEError(f"InvalidInput: rights English unit {kind}")
