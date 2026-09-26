"""Deterministic, audited English candidates for the untrusted natural view."""
from __future__ import annotations

from dataclasses import dataclass
import re

from . import ast
from .english import EnglishTraversal, EnglishVocabulary, parse_english

_NOTATION = re.compile(r'[@()\[\]*<=>+{}|^_\\"-]|\b[A-Z][0-9]*\b')


@dataclass(frozen=True)
class NaturalResult:
    text: str
    natural: bool
    reason: str | None = None
    fluent_text: str | None = None
    form: str = 'natural'


PRESENTATION_VERSION = 've.prose@1'


@dataclass(frozen=True)
class ProsePresentation:
    """An admitted, editable prose snapshot bound to one checked meaning."""
    text: str
    document: ast.Document
    environment_id: str
    meaning_id: str
    sentences: tuple[dict, ...]
    paragraphs: tuple[dict, ...]
    vocabulary_digest: str | None
    version: str = PRESENTATION_VERSION

    def to_dict(self):
        return {'format': self.version, 'text': self.text,
                'environment_id': self.environment_id, 'meaning_id': self.meaning_id,
                'vocabulary_digest': self.vocabulary_digest,
                'sentences': list(self.sentences), 'paragraphs': list(self.paragraphs)}


def parse_presentation(env, text, *, version=PRESENTATION_VERSION, **options):
    """Admit exactly one derivation and retain the author's exact wording.

    The returned spans refer to the original UTF-8-decoded source string. A
    conclusion's dependencies are all earlier unmarked premises, matching the
    checked claim graph; a conclusion is never turned into an assumption.
    """
    if version != PRESENTATION_VERSION:
        raise ValueError('Unsupported prose presentation version')
    from .english import _parse_english_document
    from .identity import meaning_id
    document, source, words, conclusions, spans, breaks = _parse_english_document(
        env, text, _with_structure=True, **options)
    marked = set(conclusions)
    sentences = tuple({
        'text': source[start:end], 'start': start, 'end': end,
        'role': 'conclusion' if index in marked else 'premise',
        'dependencies': tuple(j for j in range(index) if j not in marked)
        if index in marked else (),
    } for index, (start, end) in enumerate(spans))
    boundaries = (0, *breaks, len(sentences))
    paragraphs = tuple({'start': a, 'end': b} for a, b in zip(boundaries, boundaries[1:]))
    return ProsePresentation(source, document, env.environment_id,
                             meaning_id(env, document), sentences, paragraphs,
                             words.overlay_digest)


def render_presentation(env, document, *, version=PRESENTATION_VERSION,
                        conclusions=(), paragraph_breaks=(), **options):
    """Render the new versioned default with the same parser as author input."""
    if version != PRESENTATION_VERSION:
        raise ValueError('Unsupported prose presentation version')
    from .printer import natural_document
    view = natural_document(env, document, conclusions=conclusions,
                            paragraph_breaks=paragraph_breaks, **options)
    parsed = parse_presentation(env, view.text, version=version, **options)
    if (parsed.document != document or
            tuple(i for i, s in enumerate(parsed.sentences) if s['role'] == 'conclusion') != tuple(conclusions) or
            tuple(p['start'] for p in parsed.paragraphs[1:]) != tuple(sorted(paragraph_breaks))):
        raise ValueError('Rendered prose changed the document structure')
    return parsed


def migrate_presentation(env, legacy_text, *, version=PRESENTATION_VERSION, **options):
    """Preview an audited prose migration; the caller must renew approval.

    Meaning identity is retained and can key certificate reuse. Presentation
    approval is intentionally never inferred from the old wording.
    """
    previous = parse_presentation(env, legacy_text, version=version, **options)
    conclusions = tuple(i for i, s in enumerate(previous.sentences)
                        if s['role'] == 'conclusion')
    breaks = tuple(p['start'] for p in previous.paragraphs[1:])
    proposed = render_presentation(env, previous.document, version=version,
                                   conclusions=conclusions, paragraph_breaks=breaks,
                                   **options)
    return {'previous': previous, 'proposed': proposed,
            'meaning_unchanged': previous.meaning_id == proposed.meaning_id,
            'presentation_approval_required': True}


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


def _relative_phrase(words, value):
    if type(value) is ast.Unary and value.term == ast.Var(0):
        template = words.predicates[value.predicate]
        return template[len('{0} '):] if template.startswith('{0} ') else None
    if type(value) is ast.Binary and value.left == ast.Var(0) and type(value.right) is ast.Const:
        template = words.predicates[value.predicate]
        if template.startswith('{0} ') and template.endswith(' {1}'):
            object_name = words.constants[value.right.name]
            if re.fullmatch('[a-z]+', object_name):
                object_name = 'the ' + object_name
            return template[len('{0} '):-len(' {1}')] + ' ' + object_name
    return None


def _candidate(formula, env, words):
    if type(formula) in (ast.And, ast.Or) and type(formula.right) is type(formula):
        items = (formula.left, formula.right.left, formula.right.right)
        if all(type(item) is ast.Unary and type(item.term) is ast.Const for item in items):
            join = 'and' if type(formula) is ast.And else 'or'
            predicates = [item.predicate for item in items]
            constants = [item.term.name for item in items]
            adjectives = []
            for predicate in predicates:
                template = words.predicates[predicate]
                adjective = template.removeprefix('{0} is ')
                adjectives.append(adjective if template == '{0} is ' + adjective
                                  and re.fullmatch('[a-z]+', adjective) else None)
            if len(set(constants)) == 3 and len(set(predicates)) == 1 and all(adjectives):
                names = [words.constants[name] for name in constants]
                if all(re.fullmatch(r'(?:the )?[A-Za-z]+(?: [A-Za-z]+)*', name) for name in names):
                    names[0] = names[0][0].upper() + names[0][1:]
                    verb = 'are' if join == 'and' else 'is'
                    return f'{names[0]}, {names[1]} {join} {names[2]} {verb} {adjectives[0]}'
            if len(set(predicates)) == 3 and len(set(constants)) == 1 and all(adjectives):
                name = words.constants[constants[0]]
                if re.fullmatch(r'(?:the )?[A-Za-z]+(?: [A-Za-z]+)*', name):
                    name = name[0].upper() + name[1:]
                    return f'{name} is {adjectives[0]}, {adjectives[1]} {join} {adjectives[2]}'
    noun = None
    if type(formula) in (ast.Le, ast.Lt) and type(formula.left) is ast.Scale:
        scale = formula.left
        if (scale.coefficient == 2 and type(scale.term) is ast.Const
                and type(formula.right) is ast.Const
                and env.constants[scale.term.name].sort == ast.INT_SORT
                and env.constants[formula.right.name].sort == ast.INT_SORT):
            amount = words.constants[scale.term.name]
            right = words.constants[formula.right.name]
            if re.fullmatch('[a-z]+', amount):
                return right.capitalize() + (' is at least ' if type(formula) is ast.Le else ' is more than ') + 'twice the ' + amount
    if type(formula) in (ast.Le, ast.Lt) and type(formula.left) is ast.Num:
        if type(formula.right) is ast.Const and env.constants[formula.right.name].sort == ast.INT_SORT:
            right = words.constants[formula.right.name]
            return right.capitalize() + (' is at least ' if type(formula) is ast.Le else ' is more than ') + str(formula.left.value)
    if type(formula) is ast.Exists:
        noun = words.sorts[formula.sort]
        relative = _relative_phrase(words, formula.body)
        if relative:
            return 'Some ' + noun + ' ' + relative
        if type(formula.body) is ast.And:
            left = _relative_phrase(words, formula.body.left)
            right = _relative_phrase(words, formula.body.right)
            if left and right:
                return 'Some ' + noun + ' ' + left + ' and ' + right
    if type(formula) is ast.Not and type(formula.body) is ast.Exists:
        quantified = formula.body
        noun = words.sorts[quantified.sort]
        body = quantified.body
        relative = _relative_phrase(words, body)
        if relative:
            return 'No ' + noun + ' ' + relative
    if type(formula) is ast.Forall and type(formula.body) is ast.Not:
        body = formula.body.body
        if type(body) is ast.Unary and body.term == ast.Var(0):
            return 'No ' + words.sorts[formula.sort] + ' ' + words.predicates[body.predicate].removeprefix('{0} ')
    if type(formula) is ast.Forall and _owner(words, formula.body, formula.sort):
        return 'Every ' + words.sorts[formula.sort] + ' has an owner'
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
    return EnglishTraversal(env, words, word_markers=True,
                            avoid_negative_universal=True).render(formula)


def render_natural_sentence(formula, env, *, vocabulary=None, accept_suggested_vocabulary=False):
    """Audit the exact displayed sentence through the writable English parser."""
    ast.check_formula(env, formula)
    options = dict(vocabulary=vocabulary, accept_suggested_vocabulary=accept_suggested_vocabulary)
    words = EnglishVocabulary(env, **options)
    candidate = _candidate(formula, env, words)
    reason = None
    if _NOTATION.search(candidate):
        reason = 'symbols_or_variable_names'
    else:
        try:
            parsed = parse_english(env, candidate + '.', **options)
            if parsed != ast.Document((formula,)):
                reason = 'different_ast'
        except Exception as exc:
            reason = ('multiple_derivations' if 'two derivations' in str(exc)
                      else 'english_audit_' + type(exc).__name__)
    if reason is None:
        return NaturalResult(candidate, True)
    from .printer import render
    fluent = render(formula, env, 've_fluent')
    for explicit in (EnglishTraversal(env, words, avoid_negative_universal=True).render(formula),
                     EnglishTraversal(env, words, word_markers=True,
                                      avoid_negative_universal=True).render(formula)):
        try:
            if parse_english(env, explicit + '.', **options) == ast.Document((formula,)):
                return NaturalResult(explicit, False, reason, fluent, 'explicit form')
        except Exception:
            continue
    raise ValueError('No writable English form passed the one-reading check')


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
