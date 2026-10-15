"""English for norm-defaults@0 (docs/spec/norm-defaults.md section 4).

The legend gives each regulated predicate its completion sentence and each
declared pair with an unspecified member the profile premise. Every legend
sentence has one derivation in the legend grammar, which holds the sentences
of all three completions for every predicate at once, so a legend sentence can
be read back as exactly one predicate and completion. The paraphrases of 4.2
render statuses, witnesses and carve-outs; the synthetic rule `F_p` is never
shown as a rule, and a filling is rendered as "this situation answers".

Lean owns every answer these sentences state. A status, a reached default and a
CONFLICT witness are rendered only from the fields of Lean's row (the deciding
`rules`, the `differs` atoms, the completed `value`, the conflict `kind` and its
deciding assignment `under`); nothing here evaluates a formula, enumerates fillings
or applies a work limit (`tests/test_norm_defaults_relay_english.py` scans the call
graph of every public function).
"""
from __future__ import annotations

import json

from .words import clauses as _lean_clauses, constants_of, lines as _lean_lines, pair_item
from .errors import CheckerUnavailable, SyntaxError, VEError
from .norm_english import UNSPECIFIED_KEYWORD, _bindings, _words, default_sentence, unspecified_clause
from .surface.unambiguity import require_unique_derivation

COMPLETIONS = ("deny", "allow", "unspecified")
PAIR_PREMISE = "whatever must be done may be done"


def legend(env):
    """The completion sentence of every regulated predicate, in declaration
    order, then the pair sentence of every declared pair with an unspecified
    member (render-only; the dual declaration is its source)."""
    sentences = [default_sentence(env, p) for p, d in env.predicates.items() if d.regulated is not None]
    pairs = []
    for required, decl in env.predicates.items():
        reg = decl.regulated
        if reg is None or reg.permission is None:
            continue
        if "unspecified" in (reg.default, env.predicates[reg.permission].regulated.default):
            pairs.append(required)
    return tuple(sentences + _pair_sentences(env, pairs))


def _pair_sentences(env, required):
    """Lean's pair sentence (norm-defaults 4.1, `VE.Words.pairSentence`) of each obligation of `required`."""
    return _lean_lines(env, [pair_item(r) for r in required])


def _candidates(env):
    """Every legend sentence the environment's vocabulary can form, with its reading."""
    result, pairs = [], []
    for name, decl in env.predicates.items():
        reg = decl.regulated
        if reg is None:
            continue
        for completion in COMPLETIONS:
            result.append((default_sentence(env, name, completion), ("completion", name, completion)))
        if reg.permission is not None:
            pairs.append((name, reg.permission))
    return result + [(text, ("pair", name, permission))
                     for text, (name, permission) in zip(_pair_sentences(env, [n for n, _ in pairs]), pairs,
                                                         strict=True)]


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


def constant_name(env, name):
    """A constant in the silence sentence's words (`silence_sentence`, which stays Python's with the legend): its
    verbalisation, else its spelling."""
    return env.constants[name].verbalisation or _words(env).constants.get(name, name)


def _clauses(env, situation, points):
    """Lean's clause (`VE.Words.clauseAt`) of each `(predicate, values, value)` point of `situation`: the positive
    clause where `value` holds, else its negation (`must not` for a permission, `need not` for an obligation); each
    element named by the first of the situation's constants that denotes it."""
    return _lean_clauses(env, constants_of(situation), points)


def _clause(env, situation, predicate, values, value=True):
    return _clauses(env, situation, [(predicate, values, value)])[0]


def _rule_numbers(document):
    return {rule.name: i for i, rule in enumerate(document.author.rules, 1)}


def _author_rules(document, names):
    """The author rules Lean named, in Lean's order; an unknown name is Lean's fault."""
    rules = {rule.name: rule for rule in document.author.rules}
    if type(names) is not list or any(type(name) is not str or name not in rules for name in names):
        raise CheckerUnavailable("CheckerUnavailable: Lean named a rule the document does not have")
    return [rules[name] for name in names]


def _row_tuple(row):
    values = row.get("tuple")
    if type(values) is not list or any(type(v) is not str for v in values):
        raise CheckerUnavailable("CheckerUnavailable: Lean's row has no tuple")
    return tuple(values)


def status_sentence(document, situation, row):
    """4.2's status paraphrases of Lean's `norm-defaults-status` row: by rule, by
    default, by the pair premise, silent, or inherited. Only author rules are named,
    and only the rules Lean found deciding (`rules`)."""
    env = document.env
    predicate, values = row["predicate"], _row_tuple(row)
    numbers = _rule_numbers(document)
    rules = _author_rules(document, row.get("rules", []))
    state = row["point_status"]
    if state.startswith("SETTLED "):
        value = state == "SETTLED yes"
        own = [r for r in rules if r.predicate == predicate]
        clause = _clause(env, situation, predicate, values, value)
        if own:
            cited = ", ".join(f"rule {numbers[r.name]}" for r in own)
            return f"The text says {clause} ({cited})."
        pair = _pair_reason(document, situation, predicate, values, value, rules)
        if pair is not None:
            return pair
        return f"The text says {clause} (by default)."
    if state == "UNDECIDED":
        clause = _clause(env, situation, predicate, values)
        if predicate in document.unspec and not rules:
            return f"The text does not say whether {clause}: no rule decides this situation."
        return f"The text does not say whether {clause}: {_inherited_reason(document, situation, row)}."
    return (f"The checker could not settle whether {_clause(env, situation, predicate, values)} "
            "with the evidence it was given.")


def _pair_reason(document, situation, predicate, values, value, rules):
    """A point settled by the profile premise: a required act is permitted, and
    an act not permitted is not required. `rules` are the rules Lean found deciding."""
    env = document.env
    if predicate not in document.unspec:
        return None
    numbers = _rule_numbers(document)
    for required, permission, _ in document.pairs():
        if (predicate, value) == (permission, True):
            other, verb, default = required, "requires", "it is required by default"
            head = _clause(env, situation, permission, values)
        elif (predicate, value) == (required, False):
            other, verb, default = permission, "forbids", "it is not permitted by default"
            head = _clause(env, situation, required, values, False)
        else:
            continue
        deciding = [r for r in rules if r.predicate == other and r.sign == (verb == "requires")]
        reason = f"rule {numbers[deciding[0].name]} {verb} it" if deciding else default
        return f"{_capital(head)}: {reason}, and {PAIR_PREMISE}."
    return None


def _capital(text):
    return text[0].upper() + text[1:]


def _inherited_reason(document, situation, row):
    """Name the rules whose decision waits on an undecided lower point (Lean's `differs`)."""
    from .ast import Unary, Binary
    env = document.env
    numbers = _rule_numbers(document)
    parts = []
    for atom in row.get("differs", []):
        q, atom_values = atom["predicate"], _row_tuple(atom)
        clause = _clause(env, situation, q, atom_values)
        rules = [r for r in document.author.rules if r.predicate == row["predicate"]
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
    """The predicates a rule's guard names (its text, not its value)."""
    from .search import _used_predicates
    return set(_used_predicates(formula))


def _latent(row):
    """Lean's CONFLICT row with a latent witness: its tuple, rules and deciding assignment."""
    if not isinstance(row, dict) or row.get("verdict") != "CONFLICT":
        raise VEError("InvalidInput: not a conflict")
    if row.get("kind") != "latent":
        raise VEError("InvalidInput: not a latent conflict")
    under = row.get("under")
    if type(under) is not list or not under:
        raise CheckerUnavailable("CheckerUnavailable: Lean gave no deciding assignment for this conflict")
    return _row_tuple(row), [(atom["predicate"], _row_tuple(atom), atom["value"]) for atom in under]


def latent_conflict_sentence(document, situation, row):
    """4.2's latent conflict of Lean's CONFLICT row: which rules contradict, under which answer."""
    env = document.env
    _, under = _latent(row)
    numbers = _rule_numbers(document)
    selected = _author_rules(document, row.get("rules"))
    found = _clauses(env, situation, [(q, values, value) for q, values, value in under]
                     + [(q, values, True) for q, values, _ in under])
    conditions, silent = found[:len(under)], found[len(under):]
    fix = ("make one rule an exception to the other" if len({r.predicate for r in selected}) == 1
           else "add a condition to one of the rules")
    named = " and ".join(str(n) for n in sorted({numbers[r.name] for r in selected}))
    return (f"Rules {named} contradict each other if {' and '.join(conditions)}, and the text does not say "
            f"whether {' or whether '.join(silent)}. To settle it, add a rule about whether "
            f"{' and whether '.join(silent)}, or {fix}.")


def gap_sentence(document, situation, line):
    """A `gaps: reachable` or `default reached` line of Lean's report, in English."""
    env = document.env
    if not isinstance(line, dict) or line.get("reached") != "reachable" or "witness" not in line:
        raise VEError("InvalidInput: a reachable gap witness is required")
    values = _row_tuple(line["witness"])
    predicate, completion = line["predicate"], line["completion"]
    if completion == "unspecified":
        clause = _clause(env, situation, predicate, values)
        return f"The text does not say whether {clause}: no rule decides this situation."
    value = line.get("value")
    if value not in ("yes", "no"):
        raise CheckerUnavailable("CheckerUnavailable: Lean's reached default has no completed value")
    clause, decided = _clauses(env, situation, [(predicate, values, True), (predicate, values, value == "yes")])
    return f"No rule decides whether {clause}; the default decides that {decided}."


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


def latent_conflict_finding(document, situation, row):
    """Spec 8's report finding for Lean's latent CONFLICT row: `LatentConflict: <rules> under <p>(<situation>)`."""
    _, under = _latent(row)
    rules = sorted({r.name for r in _author_rules(document, row.get("rules"))})
    shown = ", ".join(f"{q}({', '.join(values)}) = {'yes' if value else 'no'}" for q, values, value in under)
    return f"LatentConflict: {', '.join(rules)} under {shown}"


def completion_question(document, predicate, found):
    """Spec 5's authoring question: the three legend sentences, unranked and with
    none preselected, beside a checked situation that no rule on `predicate` decides.
    `found` is the situation Lean replayed (`norm_defaults.search_reached`), or None."""
    env = document.env
    options = [default_sentence(env, predicate, completion) for completion in COMPLETIONS]
    situation = None
    if found is not None:
        model, values, _ = found
        situation = "No rule decides whether " + _clause(env, model, predicate, values) + "."
    return {"predicate": predicate, "options": options, "selected": None, "situation": situation}
