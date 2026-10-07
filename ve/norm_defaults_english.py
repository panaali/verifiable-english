"""English for norm-defaults@0 (docs/spec/norm-defaults.md section 4).

The legend gives each regulated predicate its completion sentence and each
declared pair with an unspecified member the profile premise. Every legend
sentence has one derivation in the legend grammar, which holds the sentences
of all three completions for every predicate at once, so a legend sentence can
be read back as exactly one predicate and completion. The paraphrases of 4.2
render statuses, witnesses and carve-outs; the synthetic rule `F_p` is never
shown as a rule, and a filling is rendered as "this situation answers".
"""
from __future__ import annotations

import json

from .environment import UNSAID_PREFIX
from .errors import SyntaxError, VEError
from .norm_english import (UNSPECIFIED_KEYWORD, _bindings, _words, default_sentence, pair_sentence,
                           unspecified_clause)
from .surface.unambiguity import require_unique_derivation

COMPLETIONS = ("deny", "allow", "unspecified")
PAIR_PREMISE = "whatever must be done may be done"


def legend(env):
    """The completion sentence of every regulated predicate, in declaration
    order, then the pair sentence of every declared pair with an unspecified
    member (render-only; the dual declaration is its source)."""
    sentences = [default_sentence(env, p) for p, d in env.predicates.items() if d.regulated is not None]
    for required, decl in env.predicates.items():
        reg = decl.regulated
        if reg is None or reg.permission is None:
            continue
        if "unspecified" in (reg.default, env.predicates[reg.permission].regulated.default):
            sentences.append(pair_sentence(env, required))
    return tuple(sentences)


def _candidates(env):
    """Every legend sentence the environment's vocabulary can form, with its reading."""
    result = []
    for name, decl in env.predicates.items():
        reg = decl.regulated
        if reg is None:
            continue
        for completion in COMPLETIONS:
            result.append((default_sentence(env, name, completion), ("completion", name, completion)))
        if reg.permission is not None:
            result.append((pair_sentence(env, name), ("pair", name, reg.permission)))
    return result


def legend_grammar(env):
    """The P0 grammar with the legend sentences as its only statements."""
    from .english import english_lark_grammar
    candidates = _candidates(env)
    completion = [json.dumps(text[len("By default, "):-1]) + "i" for text, (kind, _, c) in candidates
                  if kind == "completion" and c != "unspecified"]
    unspecified = [json.dumps(text[len(UNSPECIFIED_KEYWORD + "the text does not say whether "):-1]) + "i"
                   for text, (kind, _, c) in candidates if kind == "completion" and c == "unspecified"]
    pairs = [json.dumps(text[len("Whenever "):-1]) + "i" for text, (kind, _, _) in candidates if kind == "pair"]
    lines = english_lark_grammar(env).splitlines()
    lines[0] = ('start: default_sentence | unspecified_sentence | pair_sentence\n'
                'default_sentence: "By default,"i default_body "."\n'
                'unspecified_sentence: "When nothing else in the text decides,"i '
                '"the text does not say whether"i unspecified_body "."\n'
                'pair_sentence: "Whenever"i pair_body "."\n'
                'default_body: ' + (' | '.join(dict.fromkeys(completion)) or '"IMPOSSIBLE"') + '\n'
                'unspecified_body: ' + (' | '.join(dict.fromkeys(unspecified)) or '"IMPOSSIBLE"') + '\n'
                'pair_body: ' + (' | '.join(dict.fromkeys(pairs)) or '"IMPOSSIBLE"'))
    return "\n".join(lines) + "\n"


def parse_legend_sentence(env, text):
    """`(kind, predicate, completion or permission)` of one legend sentence.

    The sentence must have one derivation in `legend_grammar` and match exactly
    one declared reading; a completion sentence is admitted only when its
    profile is enabled."""
    if type(text) is not str:
        raise SyntaxError("A legend sentence must be text")
    require_unique_derivation(env, text, grammar=legend_grammar(env))
    matches = [reading for candidate, reading in _candidates(env) if " ".join(text.split()).casefold() ==
               candidate.casefold()]
    if len(matches) != 1:
        raise SyntaxError("The legend sentence has no single declared reading")
    kind, predicate, value = matches[0]
    if kind == "completion" and value == "unspecified" and "norm-defaults@0" not in env.profiles:
        raise VEError("UnsupportedProfile: unspecified completion requires norm-defaults@0")
    return matches[0]


# 4.2 paraphrases.

def _completion_clause(env, predicate):
    """What decides where no rule does: the declared completion, in legend words."""
    reg = env.predicates[predicate].regulated
    if reg.default == "unspecified":
        return "the text does not say whether " + unspecified_clause(env, predicate)
    sentence = default_sentence(env, predicate)
    return "by default, " + sentence[len("By default, "):-1]


def carve_out_paraphrase(env, predicate):
    """norms 2.5's carve-out paraphrase, naming the completion (4.2)."""
    return ("When this condition holds, this rule is silent; other rules may decide; if none does, "
            + _completion_clause(env, predicate) + ".")


def soft_default_paraphrase(env, predicate, rule_number):
    """A default `should not` on a permission (soft 2.3) with its completion (4.2)."""
    reg = env.predicates[predicate].regulated
    if reg is None or reg.role != "permission":
        raise VEError(f"InvalidInput: {predicate} is not a permission")
    forbidden = reg.act.replace("{0} ", "{0} must not ", 1).format(
        *(("an " if n[0].lower() in "aeiou" else "a ") + n
          for n in (_words(env).sorts[s] for s in env.predicates[predicate].arguments)))
    return (forbidden[0].upper() + forbidden[1:] + f" unless rule {rule_number}'s exception applies there; "
            "where it applies and no other rule decides, " + _completion_clause(env, predicate) + ".")


def element_name(env, situation, value):
    """A situation element: the verbalisation or description of a constant
    naming it, or the element itself."""
    for name, element in sorted(situation.constants.items()):
        if element == value:
            return constant_name(env, name)
    return value


def constant_name(env, name):
    return env.constants[name].verbalisation or _words(env).constants.get(name, name)


def point_clause(env, situation, predicate, values, modal=None):
    """`Sol may generate …` at a situation tuple."""
    names = [element_name(env, situation, v) for v in values]
    reg = env.predicates[predicate].regulated
    if reg.role == "plain":
        return _words(env).predicates[predicate].format(*names)
    modal = modal or ("may" if reg.role == "permission" else "must")
    return reg.act.replace("{0} ", "{0} " + modal + " ", 1).format(*names)


def _rule_numbers(document):
    return {rule.name: i for i, rule in enumerate(document.author.rules, 1)}


def _selected_author_rules(document, situation, filling, predicate, values):
    from .evaluate import _Evaluator
    from .norm_defaults import _bindings as bindings
    sorts = document.env.predicates[predicate].arguments
    selected = document.filled.selection(predicate)[2]
    model = document.with_filling(situation, filling, checked=False)
    evaluator = _Evaluator(document._raw_base(), model, 1_000_000, trace=False)
    return tuple(rule for rule in document.author.rules if rule.predicate == predicate and
                 evaluator.formula(document.filled._expand(selected[rule.name], predicate),
                                   bindings(sorts, values))[0])


def status_sentence(document, situation, status):
    """4.2's status paraphrases: by rule, by default, by the pair premise,
    silent, or inherited. Only author rules are named."""
    env = document.env
    predicate, values = status.predicate, status.values
    numbers = _rule_numbers(document)
    if status.status == "SETTLED":
        filling = document.canonical_filling(situation)
        rules = _selected_author_rules(document, situation, filling, predicate, values)
        clause = point_clause(env, situation, predicate, values,
                              None if status.value else _negative_modal(env, predicate))
        if rules:
            cited = ", ".join(f"rule {numbers[r.name]}" for r in rules)
            return f"The text says {clause} ({cited})."
        pair = _pair_reason(document, situation, predicate, values, status.value)
        if pair is not None:
            return pair
        return f"The text says {clause} (by default)."
    if status.status == "UNDECIDED":
        clause = point_clause(env, situation, predicate, values)
        if predicate in document.unspec and not any(
                _selected_author_rules(document, situation, f, predicate, values) for f in status.fillings):
            return f"The text does not say whether {clause}: no rule decides this situation."
        return f"The text does not say whether {clause}: {_inherited_reason(document, situation, status)}."
    return (f"The checker could not settle whether {point_clause(env, situation, predicate, values)} "
            f"within {status.evidence}.")


def _negative_modal(env, predicate):
    reg = env.predicates[predicate].regulated
    return "must not" if reg.role == "permission" else "need not"


def _pair_reason(document, situation, predicate, values, value):
    """A point settled by the profile premise: a required act is permitted, and
    an act not permitted is not required."""
    env = document.env
    if predicate not in document.unspec:
        return None
    numbers = _rule_numbers(document)
    filling = document.canonical_filling(situation)
    for required, permission, _ in document.pairs():
        if (predicate, value) == (permission, True):
            other, verb, default = required, "requires", "it is required by default"
            head = point_clause(env, situation, permission, values)
        elif (predicate, value) == (required, False):
            other, verb, default = permission, "forbids", "it is not permitted by default"
            head = point_clause(env, situation, required, values, "need not")
        else:
            continue
        rules = [r for r in _selected_author_rules(document, situation, filling, other, values)
                 if r.sign == (verb == "requires")]
        reason = f"rule {numbers[rules[0].name]} {verb} it" if rules else default
        return f"{_capital(head)}: {reason}, and {PAIR_PREMISE}."
    return None


def _capital(text):
    return text[0].upper() + text[1:]


def _inherited_reason(document, situation, status):
    """Name the rules whose decision waits on an undecided lower point."""
    from .ast import Unary, Binary
    env = document.env
    numbers = _rule_numbers(document)
    first, second = status.fillings
    lower = []
    for name in sorted(set(first) | set(second)):
        for row in sorted(first.get(name, frozenset()) ^ second.get(name, frozenset())):
            lower.append((name[len(UNSAID_PREFIX):], row))
    parts = []
    for q, row in lower:
        clause = point_clause(env, situation, q, row)
        rules = [r for r in document.author.rules if r.predicate == status.predicate
                 and q in _atoms(r.guard) | set().union(*(_atoms(u) for u in r.unless))]
        if rules:
            only_if = isinstance(rules[0].guard, (Unary, Binary)) and rules[0].guard.predicate == q
            link = "decides only if" if only_if else "depends on whether"
            parts.append(f"rule {numbers[rules[0].name]} {link} {clause}, and the text does not say whether "
                         f"{clause}")
        else:
            parts.append(f"it depends on whether {clause}, and the text does not say")
    return "; ".join(parts) if parts else "the answer depends on a point the text leaves open"


def _atoms(formula):
    from .search import _used_predicates
    return set(_used_predicates(formula))


def latent_conflict_sentence(document, situation, report):
    """4.2's latent conflict: which rules contradict, under which answer."""
    env = document.env
    if report.kind != "latent":
        raise VEError("InvalidInput: not a latent conflict")
    numbers = _rule_numbers(document)
    filling = {name: frozenset(tuple(row) for row in rows) for name, rows in report.filling.items()}
    predicates = (report.target.split("->") if "->" in report.target else [report.target])
    selected = [r for p in predicates
                for r in _selected_author_rules(document, situation, filling, p, report.tuple)]
    conditions = [point_clause(env, situation, q, row, None if value else _negative_modal(env, q))
                  for q, row, value in report.under]
    silent = [point_clause(env, situation, q, row) for q, row, _ in report.under]
    fix = ("make one rule an exception to the other" if len({r.predicate for r in selected}) == 1
           else "add a condition to one of the rules")
    named = " and ".join(str(n) for n in sorted({numbers[r.name] for r in selected}))
    return (f"Rules {named} contradict each other if {' and '.join(conditions)}, and the text does not say "
            f"whether {' or whether '.join(silent)}. To settle it, add a rule about whether "
            f"{' and whether '.join(silent)}, or {fix}.")


def gap_sentence(document, situation, line):
    """A `gaps: reachable` or `default reached` witness line, in English."""
    env = document.env
    values, filling = line.witness
    clause = point_clause(env, situation, line.predicate, values)
    if line.completion == "unspecified":
        return f"The text does not say whether {clause}: no rule decides this situation."
    value = document.value(situation, filling, line.predicate, values)
    decided = point_clause(env, situation, line.predicate, values,
                           None if value else _negative_modal(env, line.predicate))
    return f"No rule decides whether {clause}; the default decides that {decided}."


def filling_sentence(env, situation, predicate, values, value):
    """A filled gap in a countermodel: the situation's answer to a silence."""
    clause = point_clause(env, situation, predicate, values)
    return f"Here the text does not say whether {clause}; this situation answers '{'yes' if value else 'no'}'."


def _simplify(formula):
    """Remove the ⊤ and ⊥ units and double negations that selection formulas carry."""
    from .ast import And, Bottom, Not, Or, Top
    if isinstance(formula, Not):
        body = _simplify(formula.body)
        if isinstance(body, Top):
            return Bottom()
        if isinstance(body, Bottom):
            return Top()
        return body.body if isinstance(body, Not) else Not(body)
    if isinstance(formula, (And, Or)):
        left, right = _simplify(formula.left), _simplify(formula.right)
        unit, zero = (Top, Bottom) if isinstance(formula, And) else (Bottom, Top)
        if isinstance(left, zero) or isinstance(right, zero):
            return zero()
        if isinstance(left, unit):
            return right
        if isinstance(right, unit):
            return left
        return type(formula)(left, right)
    return formula


def silence_sentence(document, predicate):
    """The situations where no author rule on `predicate` decides, in English:
    "the text does not say whether an entity other than Claude may …" when the
    silence only excludes named individuals, else the condition in rule words."""
    from .ast import And, Bottom, Const, Eq, Not, Top, Var
    from .norm_english import _guard_text
    env = document.env
    decl = env.predicates[predicate]
    condition = _simplify(document.reached(predicate))
    words = _words(env)
    if isinstance(condition, Bottom):
        return None
    if isinstance(condition, Top):
        return "the text does not say whether " + unspecified_clause(env, predicate)
    excluded = {i: [] for i in range(len(decl.arguments))}
    pending, simple = [condition], True
    while pending and simple:
        node = pending.pop()
        if isinstance(node, And):
            pending.extend((node.right, node.left))
            continue
        eq = node.body if isinstance(node, Not) else None
        if isinstance(eq, Eq):
            var, const = ((eq.left, eq.right) if isinstance(eq.left, Var) else (eq.right, eq.left))
            if isinstance(var, Var) and isinstance(const, Const):
                excluded[len(decl.arguments) - 1 - var.index].append(constant_name(env, const.name))
                continue
        simple = False
    if simple:
        arguments = []
        for i, sort in enumerate(decl.arguments):
            noun = words.sorts[sort]
            text = ("an " if noun[0].lower() in "aeiou" else "a ") + noun
            if excluded[i]:
                text += " other than " + " and ".join(excluded[i])
            arguments.append(text)
        return "the text does not say whether " + unspecified_clause(env, predicate, arguments)
    scope, _ = _bindings(decl, words)
    return ("the text does not say whether " + unspecified_clause(env, predicate) + ", if "
            + _guard_text(condition, env, words, scope))


def latent_conflict_finding(document, situation, report):
    """Spec 8's report finding for a latent CONFLICT: `LatentConflict: <rules> under <p>(<situation>)`."""
    if report.kind != "latent":
        raise VEError("InvalidInput: not a latent conflict")
    filling = {name: frozenset(tuple(row) for row in rows) for name, rows in report.filling.items()}
    predicates = report.target.split("->") if "->" in report.target else [report.target]
    rules = sorted({r.name for p in predicates
                    for r in _selected_author_rules(document, situation, filling, p, report.tuple)})
    under = ", ".join(f"{q}({', '.join(row)}) = {'yes' if value else 'no'}" for q, row, value in report.under)
    return f"LatentConflict: {', '.join(rules)} under {under}"


def completion_question(document, predicate, *, max_domain_size=2):
    """Spec 5's authoring question: the three legend sentences, unranked and with
    none preselected, beside a checked situation that no rule on `predicate` decides."""
    from .norm_defaults import search_reached
    env = document.env
    options = [default_sentence(env, predicate, completion) for completion in COMPLETIONS]
    found = search_reached(document, predicate, max_domain_size=max_domain_size)
    situation = None
    if found is not None:
        model, values, _ = found
        situation = "No rule decides whether " + point_clause(env, model, predicate, values) + "."
    return {"predicate": predicate, "options": options, "selected": None, "situation": situation}
