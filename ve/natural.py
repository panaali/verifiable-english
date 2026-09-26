"""Deterministic, audited English candidates for the untrusted natural view."""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import re

from lark import Lark

from . import ast
from .english import EnglishTraversal, EnglishVocabulary, english_lark_grammar, parse_english
from .errors import VEError


@dataclass(frozen=True)
class NaturalResult:
    text: str
    natural: bool
    reason: str | None = None
    fluent_text: str | None = None


def _symbol_free_fallback(formula, env, words):
    """Spell the explicit English fallback without display notation."""
    text = EnglishTraversal(env, words).render(formula)
    ordinals = ('first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth')
    for sort, letter in words.letters.items():
        noun = words.sorts[sort]
        pattern = r'\b' + re.escape(letter) + r'([1-9][0-9]*)\b'
        def replace(match):
            index = int(match[1])
            order = ordinals[index - 1] if index <= len(ordinals) else str(index) + 'th'
            return 'the ' + order + ' ' + noun
        text = re.sub(re.escape(noun) + r' named ' + pattern,
                      lambda match: replace(match).removeprefix('the '), text)
        text = re.sub(pattern, replace, text)
    for mark, word in (('(a)', 'first,'), ('(b)', 'second,'),
                       ('(i)', 'first,'), ('(ii)', 'second,')):
        text = text.replace(mark, word)
    text = text.replace('[', 'the quantity ').replace(']', ' end quantity')
    for mark, word in (('*', ' times '), ('+', ' plus '), ('<', ' less than '),
                       ('>', ' greater than '), ('=', ' equals '), ('@', '')):
        text = text.replace(mark, word)
    text = text.replace('(', '').replace(')', '')
    text = re.sub(r'"([A-Za-z0-9_-]+)"', lambda m: 'the named ' + m[1].replace('_', ' '), text)
    return re.sub(r'\s+', ' ', text).strip()


def _adjective(words, value, sort):
    if type(value) is not ast.Unary or value.term != ast.Var(0):
        return None
    if value.predicate not in words.predicates:
        return None
    template = words.predicates[value.predicate]
    if not template.startswith('{0} is '):
        return None
    adjective = template[len('{0} is '):]
    if (not re.fullmatch('[a-z]+', adjective)
            or words.env.predicates[value.predicate].arguments != (sort,)):
        return None
    return adjective


def _owner(words, value, sort):
    if type(value) is not ast.Exists or type(value.body) is not ast.Binary:
        return False
    atom = value.body
    return (atom.predicate == 'owns' and words.predicates.get('owns') == '{0} owns {1}'
            and atom.left == ast.Var(0) and atom.right == ast.Var(1)
            and words.env.predicates['owns'].arguments[1] == sort)


def _candidate(formula, env, words):
    noun = None
    if type(formula) in (ast.Le, ast.Lt) and type(formula.left) is ast.Num:
        if type(formula.right) is ast.Const and env.constants[formula.right.name].sort == ast.INT_SORT:
            right = words.constants[formula.right.name]
            return right.capitalize() + (' is at least ' if type(formula) is ast.Le else ' is more than ') + str(formula.left.value)
    if type(formula) is ast.Exists:
        noun = words.sorts[formula.sort]
        if type(formula.body) is ast.Unary and formula.body.term == ast.Var(0):
            relative = words.predicates[formula.body.predicate].removeprefix('{0} ')
            if relative != words.predicates[formula.body.predicate]:
                return 'Some ' + noun + ' ' + relative
    if type(formula) is ast.Not and type(formula.body) is ast.Exists:
        quantified = formula.body
        noun = words.sorts[quantified.sort]
        body = quantified.body
        if type(body) is ast.Unary and body.term == ast.Var(0):
            return 'No ' + noun + ' ' + words.predicates[body.predicate].removeprefix('{0} ')
        if type(body) is ast.Binary and body.left == ast.Var(0) and type(body.right) is ast.Const:
            template = words.predicates[body.predicate]
            if template.startswith('{0} ') and template.endswith(' {1}'):
                object_name = words.constants[body.right.name]
                if re.fullmatch('[a-z]+', object_name):
                    object_name = 'the ' + object_name
                return 'No ' + noun + ' ' + template[len('{0} '):-len(' {1}')] + ' ' + object_name
    if type(formula) is ast.Forall and type(formula.body) is ast.Implies:
        guard, consequent = formula.body.left, formula.body.right
        adjective = _adjective(words, guard, formula.sort)
        if adjective:
            prefix = 'Every ' + adjective + ' ' + words.sorts[formula.sort] + ' '
            if _owner(words, consequent, formula.sort):
                return prefix + 'has an owner'
            if type(consequent) is ast.And and _owner(words, consequent.right, formula.sort):
                unary = consequent.left
                if type(unary) is ast.Unary and unary.term == ast.Var(0):
                    template = words.predicates[unary.predicate]
                    if template.startswith('{0} '):
                        return prefix + template[len('{0} '):] + ' and has an owner'
            if type(consequent) is ast.Unary and consequent.term == ast.Var(0):
                template = words.predicates[consequent.predicate]
                if template.startswith('{0} '):
                    return prefix + template[len('{0} '):]
    return EnglishTraversal(env, words).render(formula)


@lru_cache(maxsize=32)
def _earley(grammar):
    return Lark(grammar, parser='earley', lexer='dynamic_complete', ambiguity='explicit')


def render_natural_sentence(formula, env, *, vocabulary=None, accept_suggested_vocabulary=False):
    """Return an audited sentence or the fluent sentence and a rejection reason."""
    ast.check_formula(env, formula)
    options = dict(vocabulary=vocabulary, accept_suggested_vocabulary=accept_suggested_vocabulary)
    words = EnglishVocabulary(env, **options)
    candidate = _candidate(formula, env, words)
    reason = None
    if re.search(r'[@()\[\]*<=>+]|\b[A-Z][0-9]*\b', candidate):
        reason = 'symbols_or_variable_names'
    elif len(candidate.encode('utf-8')) + 2 > 4096:
        reason = 'earley_4096_byte_budget'
    else:
        sentence = candidate + '.\n'
        try:
            parsed = parse_english(env, sentence, **options)
            if parsed != ast.Document((formula,)):
                reason = 'different_ast'
            else:
                tree = _earley(english_lark_grammar(env, **options)).parse(sentence[0].lower() + sentence[1:])
                if any(True for _ in tree.find_data('_ambig')):
                    reason = 'multiple_derivations'
        except Exception as exc:
            reason = 'english_audit_' + type(exc).__name__
    if reason is None:
        return NaturalResult(candidate, True)
    from .printer import render
    fluent = render(formula, env, 've_fluent')
    return NaturalResult(_symbol_free_fallback(formula, env, words), False, reason, fluent)


def natural_coverage(formulas, env, **options):
    results = [render_natural_sentence(f, env, **options) for f in formulas]
    reasons = {}
    for result in results:
        if result.reason:
            reasons[result.reason] = reasons.get(result.reason, 0) + 1
    return {'statements': len(results), 'natural': sum(r.natural for r in results),
            'fallback': sum(not r.natural for r in results),
            'natural_fraction': sum(r.natural for r in results) / len(results) if results else 0.0,
            'fallback_reasons': reasons}
