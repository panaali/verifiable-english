"""The English of answers that hold unless an exception applies (docs/spec/defeasible-PLAN.md 2.8, spec
docs/spec/defeasible.md 4; batch DF-1b).

Lean selects every row (`lean/VE/Defaults/Wire.lean`): the verdict, the `basis`, the `form`, the kept `assumptions`,
the exceptions a situation `forced` and the deciders of a collision (`giveWayDeciders`). This module renders the row
`ve.defaults` bound, and chooses nothing: DE1 or DE1′ is Lean's `form`, DE6 or DE6′ is whether Lean's `forced` is
empty, DE12 is Lean's basis `unsettled`, and DE7's decider sentence is the shape of Lean's `deciders`. The conclusion,
the conditions, the situation and the effects are the existing renderers' (`canonical_sentence`, the soft rules'
condition text `norm_english._guard_text`, Lean's `words` lines). An assumption is read from Lean's label
(`lean/VE/Defaults/Premises.lean`, `dfltLabelled`: its kind, then the rule, party or ranks it names), and every name
it gives is bound to the request: a label the request cannot give is `CheckerUnavailable`.
"""
from __future__ import annotations

from .defaults import _decider, _rules, _unbound

UNSET = "unstated"


def _who(party):
    """Soft's decider phrase: "the assistant" for the party `assistant`."""
    return "the " + party


def _capital(text):
    return text[:1].upper() + text[1:]


class _Text:
    """The renderers for one request: its soft environment and the rules it names."""

    def __init__(self, case):
        from .norm_english import _words
        from .softnorms import SoftEnvironment
        self.case, self.rules = case, _rules(case)
        self.env = SoftEnvironment(case["environment"])
        self.words = _words(self.env)
        self.soft = case["environment"]["vocabulary"].get("soft") or {}

    def rule(self, name):
        if name not in self.rules:
            raise _unbound("rule")
        return self.rules[name]

    def conclusion(self):
        from .ast import formula_from_data
        from .readings_s2_english import canonical_sentence
        formula = formula_from_data(self.env, self.case["conclusion"])
        return canonical_sentence(self.env, formula, "the conclusion has no English", statement_layer=True
                                  ).rstrip(".")

    def condition(self, rule, index, values=None):
        """Condition `index` of a rule's exception: over the rule's own variables, or at the entity ids `values`."""
        from .ast import _Decoder
        from .norm_english import _bindings, _guard_text
        decl = self.env.predicates[rule["predicate"]]
        scope = (_bindings(decl, self.words)[0] if values is None else
                 tuple(reversed(list(zip(decl.arguments, values)))))
        formula = _Decoder().decode(rule["exception"]["sufficient"][index])
        return _guard_text(formula, self.env, self.words, scope)

    def act(self, predicate):
        """An act's phrase: its declared act without its argument slots (the readings route's `act_phrase`)."""
        decl = self.env.predicates.get(predicate)
        if decl is None or decl.regulated is None:
            raise _unbound("ranking act")
        phrase = decl.regulated.act or predicate
        return " ".join(word for word in phrase.split() if not (word.startswith("{") and word.endswith("}")))

    def situation(self, model):
        """Lean's situation line of a request's model: its elements and the true rows of the document's own
        predicates (the decision and unsaid tables are not facts of the situation)."""
        from . import words
        facts = [p for p in model["relations"] if p in self.env.predicates]
        return words.situation(self.env, model, facts)

    def effect(self, rule, values, model):
        """What a rule asks at a tuple: Lean's clause of its act with its sign."""
        from . import words
        return words.clause(self.env, words.constants_of(model), rule["predicate"], values, rule["sign"])


def _exception(text, name):
    """DE2, DE2·u, DE2′ and DE2′·u."""
    rule = text.rule(name)
    if rule.get("mode") != "default":
        raise _unbound("assumption rule")
    who, count = _decider(text.case, rule), len(rule["exception"].get("sufficient", ()))
    head = f"This assumes that the exception to rule {name} "
    if count == 0:
        return head + "does not apply. " + (
            "The text names no case where it applies, and no one who decides." if who == UNSET else
            f"{_capital(_who(who))} decides where it applies; the text names no case.")
    listed = ", or ".join(text.condition(rule, i) for i in range(count))
    return head + f"applies only where the text says it does: {listed}. " + (
        "The text names no one who decides any other case." if who == UNSET else
        f"{_capital(_who(who))} decides any other case.")


def _switch(text, name, party):
    """DE3."""
    if party not in text.rule(name).get("alterable", ()):
        raise _unbound("switch party")
    return f"This assumes that {_who(party)} has not turned rule {name} off."


def _ranking(text, low, high, act):
    """DE4 and DE4·u."""
    if not {low, high} <= set(text.soft.get("ranks", ())):
        raise _unbound("ranking ranks")
    who = (text.soft.get("outranking") or {}).get("decided_by") or UNSET
    return (f"This assumes that, on {text.act(act)}, the {low} consideration does not outweigh the {high} "
            "consideration. " + ("The text names no one who decides where it does." if who == UNSET else
                                 f"{_capital(_who(who))} decides where it does."))


def assumption(text, label):
    """The sentence of one kept assumption, by the kind its label names (`dfltLabelled`)."""
    _, kind, *parts = label.split(":")
    kinds = {"exception": (_exception, 1), "switch": (_switch, 2), "ranking": (_ranking, 3)}
    if kind not in kinds or len(parts) != kinds[kind][1]:
        raise _unbound("assumption")
    return kinds[kind][0](text, *parts)


def follows(case, row):
    """DE1 or DE1′ (Lean's `form`), one sentence per kept assumption, then DE12 when Lean's basis is `unsettled`.
    Basis `strict` renders DE5 from Lean's `decidersOf`."""
    if row["basis"] == "strict":
        return [strict_sentence(row["deciders"])] if row["deciders"] else []
    text = _Text(case)
    head = {"short": "Unless an exception applies", "long": "Under the assumptions listed below"}[row["form"]]
    out = [f"{head}, the conclusion follows: {text.conclusion()}."]
    out += [assumption(text, label) for label in row["assumptions"]]
    if row["basis"] == "unsettled":
        out.append("Whether it also holds without these assumptions was not checked.")
    return out


def strict_sentence(deciders):
    """DE5 and DE5·u, by Lean's ordered, distinct decider names."""
    named = [who for who in deciders if who != UNSET]
    if not named:
        return "This holds whatever is decided where the text names no decider."
    who = (_who(named[0]) if len(named) == 1 else
           ", ".join(_who(party) for party in named[:-1]) + " and " + _who(named[-1]))
    suffix = ", and whatever is decided where the text names no decider" if UNSET in deciders else ""
    return f"This holds whatever {who} {'decides' if len(named) == 1 else 'decide'}{suffix}."


def fails(case, row):
    """DE6 when Lean's `forced` is empty, otherwise DE6′ and one DE11 per entry, in Lean's order."""
    text = _Text(case)
    model = case["model"]["model"]
    head = "Even if no exception applies" + (" beyond those the text states" if row["forced"] else "")
    out = [f"{head}, the conclusion does not follow. It fails here: {text.situation(model)}."]
    for entry in row["forced"]:
        condition = text.condition(text.rule(entry["rule"]), entry["condition"], entry["tuple"])
        out.append(f"The text's own exception to rule {entry['rule']} applies here: {condition}.")
    return out


def collision(case, row):
    """DE7 with its decider sentence (DE7a, DE7a·u, DE7b or DE7b·u) by Lean's `deciders`, for a COLLISION row."""
    if row["verdict"] != "COLLISION":
        return []
    text, found = _Text(case), row["collision"]
    m, n = found["rules"]
    model = case["collision"]["model"]
    effects = [text.effect(text.rule(name), found["tuple"], model) for name in (m, n)]
    out = [f"Rules {m} and {n} conflict here unless one of them gives way: {effects[0]}, and {effects[1]}. "
           "The text ranks neither above the other, and names no exception that applies here."]
    deciders = found["deciders"]
    if deciders == [UNSET]:
        out.append("The text names no one who decides which rule gives way.")
    elif len(deciders) == 1:
        out.append(f"Which rule gives way is left to {_who(deciders[0])}.")
    elif UNSET not in deciders:
        out.append(f"Whether rule {m} gives way is left to {_who(deciders[0])}, and whether rule {n} gives way is "
                   f"left to {_who(deciders[1])}.")
    else:
        (k, who), (j, _) = sorted(zip((m, n), deciders), key=lambda pair: pair[1] == UNSET)
        out.append(f"Whether rule {k} gives way is left to {_who(who)}; the text names no one who decides whether "
                   f"rule {j} gives way.")
    return out


def sentences(case, row):
    """The English of one bound `defaults-certificate`, `defaults-model` or `defaults-coherence` row."""
    if row.get("verdict") == "FOLLOWS":
        return follows(case, row)
    if row.get("verdict") == "DOES-NOT-FOLLOW":
        return fails(case, row)
    if case.get("kind") == "defaults-coherence":
        return collision(case, row)
    return []


def readings(member, under, choice_case):
    """The English of the `default` member of a readings answer (DF-3), Lean's rows in Lean's order: DE8 alone; a
    reading's assumption sentences (DE2 to DE4) after `Under <reading>:`; DE12; DE7 with its decider sentence after
    `Under <reading>:`. `under(choice)` is the reading slot, `choice_case(choice)` the choice's own `defaults-*`
    request with the collision the request sent for it; every name a sentence gives is bound there."""
    import json
    entries = {json.dumps(entry["choice"]): entry for entry in member["per_choice"]}
    out = []
    for line in member["english"]:
        if line["row"] == "DE8":
            out.append("Under every reading, the conclusion follows under the assumptions listed for that reading.")
            continue
        entry, case = entries[json.dumps(line["choice"])], choice_case(line["choice"])
        if line["row"] == "DE7":
            sentences = collision(case, {"verdict": "COLLISION", "collision": entry["collision"]})
        elif line["row"] == "assumptions":
            text = _Text(case)
            sentences = [assumption(text, label) for label in entry["assumptions"]]
        else:
            out.append("Whether it also holds without these assumptions was not checked.")
            continue
        out += [f"Under {under(line['choice'])}: {sentences[0]}", *sentences[1:]]
    return out
