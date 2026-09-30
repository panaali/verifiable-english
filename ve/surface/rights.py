"""Rights incident English, reusing the audited soft rule grammar."""
from __future__ import annotations

import json
import re

from ..errors import VEError
from ..norm_english import render_rule_sentence
from ..softnorms import SoftEnvironment, SoftNormDocument, decode_rule


def _soft_env(env):
    if "rights@0" not in env.profiles:
        raise VEError("UnsupportedProfile: rights@0 is required")
    raw = env.to_dict()
    raw["profiles"].remove("rights@0")
    raw["vocabulary"].pop("rights")
    return SoftEnvironment(raw)


def render_line(env, right, kind, raw, *, rights=None):
    """Render a single claim, liberty or immunity with one audited rule body.
    With the checked rights document, guards may name its generated predicates."""
    if kind not in ("claim", "liberty", "immunity") or type(right) is not str:
        raise VEError("InvalidInput: rights incident English")
    from ..norm_english import render_english
    document = SoftNormDocument(_soft_env(env) if rights is None else rights.environment,
                                [{"norm": raw}])
    source, _manifest = render_english(document)
    if "\n" in source or not source.startswith("Rule 1. "):
        raise VEError("InvalidInput: rights incident must have one rule")
    return f"{kind.title()} of right {right}. " + source[len("Rule 1. "):]


def parse_line(env, source, *, name, rights=None):
    """Parse one incident; the W1/soft parser checks every derivation, including
    the generated wordings of `rights` (a checked rights document) in guards."""
    match = re.fullmatch(r"(Claim|Liberty|Immunity) of right ([1-9][0-9]*|[a-z][a-z0-9-]*)\. (.+)", source, re.S)
    if match is None:
        raise VEError("SyntaxError: expected Claim, Liberty or Immunity of right")
    from ..norm_english import parse_english
    from ..rights import _name
    _name(name)
    document = parse_english(_soft_env(env) if rights is None else rights.environment,
                             "Rule 1. " + match[3])
    if len(document.rules) != 1:
        raise VEError("SyntaxError: incident needs one rule")
    raw = document.rules[0].to_dict()["norm"]
    raw["name"] = name
    return {"right": match[2], "kind": match[1].lower(), "norm": raw}


_PLURAL = {"claim": "claims", "liberty": "liberties", "immunity": "immunities", "power": "powers"}


def _number(document, right):
    """A right's display number: its position in document order (1.2)."""
    return list(document.rights).index(right) + 1


def _limitation_number(document, name):
    return next(number for number, limit in enumerate(document.limitations, 1) if limit["name"] == name)


def _series(items):
    items = list(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def _plain(formula):
    """Drop the ⊤ and ⊥ units correlation leaves in a conjoined holder guard and
    the packed carve-out (`⊤ ∧ H`, `⊥ ∨ lim`); for display only, the checked rule
    keeps its exact formula."""
    from ..ast import And, Bottom, Or, Top
    if isinstance(formula, And):
        left, right = _plain(formula.left), _plain(formula.right)
        return right if isinstance(left, Top) else left if isinstance(right, Top) else And(left, right)
    if isinstance(formula, Or):
        left, right = _plain(formula.left), _plain(formula.right)
        return right if isinstance(left, Bottom) else left if isinstance(right, Bottom) else Or(left, right)
    return formula


def _displayed(rule):
    from dataclasses import replace
    core = rule.core
    return replace(rule, core=replace(core, guard=_plain(core.guard),
                                      unless=tuple(_plain(u) for u in core.unless)))


def _citation(key):
    """What a `cites` key licenses (3.3, the 4.5 licensing table), in words."""
    if key == "guard":
        return "the distinction in its guard"
    if key == "exception":
        return "its exception"
    if key == "rank":
        return "its rank"
    kind, _, target = key.partition(":")
    return {"unless": f"its carve-out {target}", "alterable": f"the switch of {target}",
            "over": f"its precedence over rule {target}",
            "narrows": f"its effect on line {target}"}.get(kind, key)


def citation_notes(cites):
    """One sentence per `cites` entry: the units cited and what they license."""
    return [("It cites unit " if len(targets) == 1 else "It cites units ") +
            _series(targets) + f" for {_citation(key)}."
            for key, targets in (cites or {}).items()]


def rule_notes(rule, env, *, switches=True):
    """The fields of a soft rule its one-sentence rendering leaves out, one sentence
    each: precedence, switches and rank (`switches`), and the exception's conditions
    and factors. Two rules differing in any of them render differently."""
    from ..ast import _Decoder
    from ..norm_english import _guard_text, _soft_consequence, _words
    words = _words(env)
    _, scope = _soft_consequence(rule, env, words)
    notes = []
    if rule.core.over:
        notes.append(("It is an exception to rule " if len(rule.core.over) == 1 else
                      "It is an exception to rules ") + _series(rule.core.over) + ".")
    if switches and rule.alterable:
        notes.append(_series(rule.alterable) + " may turn it off for this situation.")
    if switches and rule.rank:
        notes.append(f"It serves {rule.rank} where default rules collide." if rule.mode == "default" else
                     f"It records rank {rule.rank}, but a strict rule is never weighed.")
    exception = rule.exception or {}
    for role, qualifier in (("sufficient", "when"), ("necessary", "only when")):
        for condition in exception.get(role, ()):
            notes.append(f"Its exception applies {qualifier} " +
                         _guard_text(_Decoder().decode(condition), env, words, scope) + ".")
    if exception.get("factors"):
        notes.append("Its exception takes account of " +
                     _series(json.dumps(f, ensure_ascii=False) for f in exception["factors"]) + ".")
    return notes


def _line(document, right, line):
    """Every instance of a line as it elaborates: the holder guard at the holder
    slot and the packed limitation carve-out are part of the rendered rule."""
    kind = line["kind"]
    explanations = []
    for index, instance in enumerate(document.instances):
        if instance["right"] != right or instance["source_line"] is not line:
            continue
        rule = document.soft_document.rules[index]
        sentence = render_rule_sentence(_displayed(rule), document.environment)
        if rule.mode == "default":
            decider = (rule.exception or {}).get("decided_by") or document.env.soft.get("exception_decider") or "unstated"
            sentence += (f" This is a default line; {decider} decides its exception."
                         if decider != "unstated" else
                         " This is a default line; the source names no exception decider.")
        explanations.append(" ".join((sentence, *rule_notes(rule, document.environment))))
    if explanations:
        explanations.extend(citation_notes(line.get("cites")))
    if instance_kinds := {i["kind"] for i in document.instances if i["source_line"] is line}:
        if instance_kinds & {"powerLiberty", "powerRecognition"}:
            explanations.append("Recognition required; later effects not modelled.")
        elif "immunity" in instance_kinds:
            explanations.append("Prohibition on the act; its effect on status not modelled.")
    if not explanations:
        raise VEError("InvalidInput: rights line is not in the checked document")
    label = kind[0].upper() + kind[1:]
    return f"{label} of right {_number(document, right)}. " + " ".join(explanations)


def _holder_guard(document, body):
    from ..ast import Top
    guard = document.rights[body["name"]]["guard_formula"]
    if isinstance(guard, Top):
        return ""
    from ..norm_english import _guard_text, _words
    env = document.environment
    words = _words(env)
    noun = words.sorts[body["holder"]]
    return (" Every line of this right applies only where " +
            _guard_text(guard, env, words, ((body["holder"], "that " + noun),)) + ".")


def render_unit(document, content):
    if document is None or type(content) is not dict or len(content) != 1:
        raise VEError("InvalidInput: rights English unit")
    kind, body = next(iter(content.items()))
    if kind == "right":
        from ..norm_english import _words
        noun = _words(document.environment).sorts[body["holder"]]
        header = (f"Right {_number(document, body['name'])}. Every {noun} has the right described "
                  "by its incident lines; the right requires or permits nothing by itself." +
                  _holder_guard(document, body))
        return " ".join((header, *(_line(document, body["name"], line) for line in body["lines"])))
    if kind == "right_lines":
        return " ".join((f"Right {_number(document, body['right'])} includes:",
                         *(_line(document, body["right"], line) for line in body["lines"])))
    if kind == "limitation":
        number = _limitation_number(document, body["name"])
        rights = ("every right" if body["scope"] == "all" else
                  ("right " if len(body["scope"]) == 1 else "rights ") +
                  _series(str(_number(document, r)) for r in body["scope"]))
        scope = (rights if body["kinds"] == "all" else
                 "the " + _series(_PLURAL[k] for k in body["kinds"]) + " of " + rights)
        sentences = [f"Limitation {number} (on {scope}). A right in this document is limited in a "
                     f"situation only where limitation {number} holds."]
        for condition in body["conditions"]:
            qualifier = "only where" if condition["role"] == "necessary" else "where"
            sentences.append(f"Limitation {number} holds {qualifier} {condition['verbalisation']}.")
        if body["factors"]:
            sentences.append(f"Limitation {number} takes account of " + _series(body["factors"]) + ".")
        sentences.append(f"Limitation {number} is decided by {body['decided_by']}."
                         if body["decided_by"] != "unstated" else
                         f"The source names no decider of limitation {number}.")
        for condition in body["conditions"]:
            if condition["decided_by"] not in (None, body["decided_by"]):
                sentences.append(f"Whether {condition['verbalisation']} is decided by "
                                 f"{condition['decided_by']}.")
        return " ".join(sentences)
    if kind == "bar":
        decider = (f" Whether an act is so aimed is decided by {body['decided_by']}."
                   if body["decided_by"] != "unstated" else
                   " The source names no decider of whether an act is so aimed.")
        if body["reading"] == "rule":
            return ("Nothing in this document gives any bearer a right to perform any act aimed at the "
                    "destruction of a right." + decider)
        return ("Whether any right in this document permits an act aimed at the destruction of a right "
                "is checked, not ruled." + decider)
    raise VEError(f"InvalidInput: rights English unit {kind}")
