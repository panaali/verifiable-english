"""Writable, scoped English. Canonical serialization remains in printer.py.

The grammar uses prefix clauses, binary drafting lists and a finite, checked
lexicon. No pronouns, implicit witnesses, reassociation or semantic rewriting.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
import re

from . import ast
from .errors import ResourceLimit, Span, SyntaxError, VEError
from .limits import MAX_DEPTH, MAX_NODES, MAX_SOURCE_BYTES
from .printer import (_NaturalVocabulary, _LOGICAL_WORDS, _negative_template,
                      _fluent_variable_letters, VocabularyLint)

# These are lexical noun/adjective complements, not extra semantic operators.
# They are deliberately finite: a linter cannot establish arbitrary English meaning.
_COMPLEMENTS = (
    r"is (?:subject to the jurisdiction of|a citizen of) the United States",
    r"was (?:born|naturalized) in the United States",
    r"is (?:fully|newly|currently|publicly) [a-z]+",
    r"is [a-z]+ (?:in|under) (?:good standing|review)",
)
_ACTIVE = (
    r"affords due process of law to",
    r"denies the equal protection of the laws to",
    r"(?:reports|contributes|responds) to",
    r"(?:communicates|collaborates) with",
)
_EXTRA_RESERVED = frozenset("this it holds impossible classified recorded relation property entity sort named first second following hold who where step steps source destination from reachable using starting ending definition end".split())
_RESERVED = _LOGICAL_WORDS | _EXTRA_RESERVED


def quote(name):
    return json.dumps(name, ensure_ascii=True)


class EnglishVocabulary:
    """Versioned precision pass; leaves the five historical views byte-stable."""
    def __init__(self, env):
        old = _NaturalVocabulary(env)
        self.env = env
        self.sorts = {}
        for name, noun in old.sorts.items():
            if re.fullmatch(r"[a-z]+(?: [a-z]+)*", noun) and not set(noun.split()) & _RESERVED:
                self.sorts[name] = noun
            else:
                self.sorts[name] = 'entity of sort ' + quote(name)
        # Reject aliases equal to ANY other selected noun, including fallbacks.
        counts = Counter(self.sorts.values())
        for name, noun in list(self.sorts.items()):
            if counts[noun] > 1:
                self.sorts[name] = 'entity of sort ' + quote(name)
        self.predicates, self.negatives = {}, {}
        issues = set(old.issues)
        for name, decl in env.predicates.items():
            template = decl.verbalisation
            path = f"/vocabulary/predicates/{name}/verbalisation"
            codes = {i.code for i in issues if i.path == path}
            accepted = template is not None and old.predicates[name] == template
            if template and not accepted:
                phrase = template.removeprefix('{0} ')
                unary = len(decl.arguments) == 1
                if not unary:
                    phrase = phrase.removesuffix(' {1}')
                patterns = _COMPLEMENTS if unary else _ACTIVE
                shaped = template == '{0} ' + phrase + ('' if unary else ' {1}')
                # Fixed idioms may contain articles/proper nouns and a sort noun.
                # Predicate/constant collisions and negative heads still reject.
                eligible = codes <= {'LOGICAL_WORD', 'PHRASE_SYNTAX', 'UNARY_MODIFIER',
                                      'TEMPLATE_SHAPE', 'TEMPLATE_LENGTH', 'SORT_NOUN',
                                      'SYMBOL_COLLISION', 'BINARY_CONVERSE'}
                collision = any(re.search(r'\b' + re.escape(other) + r'\b', phrase)
                                for other in (*env.predicates, *env.constants) if other != name)
                heads = [p.verbalisation.split()[2] for p in env.predicates.values()
                         if p.verbalisation and p.verbalisation.startswith('{0} is ')
                         and len(p.verbalisation.split()) > 2]
                negated = any(word in {'un' + h, 'non' + h} for h in (*env.predicates, *heads)
                              for word in phrase.split())
                accepted = bool(shaped and eligible and not collision and not negated
                                and len(template) <= 80
                                and any(re.fullmatch(p, phrase) for p in patterns))
            if template is None and re.fullmatch('[a-z]+', name) and name not in _RESERVED:
                if len(decl.arguments) == 1 or (name.endswith('s') and name not in {'is', 'has', 'belongs'}):
                    self.predicates[name] = old.predicates[name]
                    continue
            if accepted and set(re.findall(r'[a-z]+', template)) & _EXTRA_RESERVED:
                accepted = False
                issues.add(VocabularyLint(path, 'ENGLISH_STRUCTURE_WORD'))
            if accepted:
                self.predicates[name] = template
                issues = {i for i in issues if i.path != path}
            else:
                self.predicates[name] = ('{0} is classified as ' + quote(name) if len(decl.arguments) == 1
                                         else '{0} has the recorded relation ' + quote(name) + ' to {1}')
            negative = decl.negative_verbalisation
            if (accepted and negative and (len(decl.arguments) == 2 or template.startswith('{0} is '))
                    and negative == _negative_template(template, len(decl.arguments))):
                # Old negative length limits continue to apply.
                if len(negative) <= 80 and len(negative.split()) <= 8:
                    self.negatives[name] = negative
        self.issues = tuple(sorted(issues, key=lambda i: (i.path, i.code)))
        self.letters = _fluent_variable_letters(self.sorts, env)
        self.constants = {name: (name if re.fullmatch('[a-z]+', name)
                                and name not in _RESERVED and name not in {'is', 'has'} else quote(name))
                          for name in env.constants}

    def atom(self, name, terms, negative=False):
        text = (self.negatives if negative else self.predicates)[name]
        for i, term in enumerate(terms):
            text = text.replace('{' + str(i) + '}', term)
        return text


def lint_english_vocabulary(env):
    return EnglishVocabulary(env).issues


def _max_scope(value, scope=(), counts=None):
    counts = Counter() if counts is None else counts
    if type(value) in (ast.Forall, ast.Exists):
        scope = (value.sort, *scope)
        counts[value.sort] = max(counts[value.sort], scope.count(value.sort))
        _max_scope(value.body, scope, counts)
    elif type(value) is ast.Reach and type(value.edge) is ast.Body:
        scope = (value.edge.sort, value.edge.sort, *scope)
        counts[value.edge.sort] = max(counts[value.edge.sort], scope.count(value.edge.sort))
        _max_scope(value.edge.formula, scope, counts)
    elif type(value) is ast.Not:
        _max_scope(value.body, scope, counts)
    elif type(value) in (ast.And, ast.Or, ast.Implies):
        _max_scope(value.left, scope, counts)
        _max_scope(value.right, scope, counts)
    return counts


def _article(noun):
    return 'an' if noun[0] in 'aeiou' else 'a'


def _markers(depth):
    return ('(a)', '(b)') if depth % 2 == 0 else ('(i)', '(ii)')


class EnglishTraversal:
    def __init__(self, env, words=None):
        self.env = env
        self.words = words or EnglishVocabulary(env)

    def binding(self, sort, scope):
        noun = self.words.sorts[sort]
        index = sum(s == sort for s, _ in scope)
        mode = self.maximum[sort]
        if mode <= 1:
            return (sort, 'that ' + noun), noun
        if mode == 2:
            noun = ('first ' if index == 0 else 'second ') + noun
            return (sort, 'the ' + noun), noun
        label = self.words.letters[sort] + str(index + 1)
        return (sort, label), noun + ' named ' + label

    def term(self, value, scope):
        return scope[value.index][1] if type(value) is ast.Var else self.words.constants[value.name]

    def simple(self, value):
        return type(value) in (ast.Top, ast.Bottom, ast.Unary, ast.Binary, ast.Eq) or (
            type(value) is ast.Not and type(value.body) in (ast.Unary, ast.Binary)
            and value.body.predicate in self.words.negatives)

    def relative(self, value, scope):
        negative = type(value) is ast.Not
        atom = value.body if negative else value
        if type(atom) not in (ast.Unary, ast.Binary):
            return None
        if negative and atom.predicate not in self.words.negatives:
            return None
        if (atom.term if type(atom) is ast.Unary else atom.left) != ast.Var(0):
            return None
        # No contraction for quoted formal fallback atoms.
        if self.words.predicates[atom.predicate] != self.env.predicates[atom.predicate].verbalisation:
            return None
        return self.formula(value, scope)[len(scope[0][1]) + 1:]

    def formula(self, value, scope=(), depth=0):
        kind = type(value)
        if kind is ast.Top: return 'this holds in all cases'
        if kind is ast.Bottom: return 'this is impossible'
        if kind in (ast.Unary, ast.Binary):
            terms = (value.term,) if kind is ast.Unary else (value.left, value.right)
            return self.words.atom(value.predicate, [self.term(t, scope) for t in terms])
        if kind is ast.Eq:
            return self.term(value.left, scope) + ' is the same as ' + self.term(value.right, scope)
        if kind is ast.Not:
            if type(value.body) in (ast.Unary, ast.Binary) and value.body.predicate in self.words.negatives:
                atom = value.body
                terms = (atom.term,) if type(atom) is ast.Unary else (atom.left, atom.right)
                return self.words.atom(atom.predicate, [self.term(t, scope) for t in terms], True)
            return 'it is not the case that ' + self.formula(value.body, scope, depth)
        if kind in (ast.Forall, ast.Exists):
            binding, noun = self.binding(value.sort, scope)
            inner = (binding, *scope)
            if kind is ast.Forall:
                if type(value.body) is ast.Implies:
                    guard = self.relative(value.body.left, inner)
                    if guard:
                        consequent = self.relative(value.body.right, inner)
                        if consequent:
                            return 'every ' + noun + ' that ' + guard + ' ' + consequent
                        return ('for every ' + noun + ' that ' + guard + ', '
                                + self.formula(value.body.right, inner, depth))
                consequent = self.relative(value.body, inner)
                if consequent:
                    return 'every ' + noun + ' ' + consequent
                return 'for every ' + noun + ', ' + self.formula(value.body, inner, depth)
            relative = self.relative(value.body, inner)
            if relative:
                return 'there is ' + _article(noun) + ' ' + noun + (' who ' if self.words.sorts[value.sort] == 'person' else ' that ') + relative
            return ('there is ' + _article(noun) + ' ' + noun + ' such that '
                    + self.formula(value.body, inner, depth))
        if kind in (ast.And, ast.Or, ast.Implies):
            if self.simple(value.left) and self.simple(value.right):
                left = self.formula(value.left, scope, depth)
                right = self.formula(value.right, scope, depth)
                if kind is ast.And: return 'both ' + left + ' and ' + right
                if kind is ast.Or: return 'either ' + left + ' or ' + right + ', or both'
                return 'if ' + left + ', then ' + right
            a, b = _markers(depth)
            indent = '  ' * (depth + 1)
            left = self.formula(value.left, scope, depth + 1)
            right = self.formula(value.right, scope, depth + 1)
            if kind is ast.Implies:
                return (f'if the following holds:\n{indent}{a} {left};\n'
                        + '  ' * depth + f'then the following holds:\n{indent}{b} {right}')
            header = 'all of the following hold' if kind is ast.And else 'at least one of the following holds'
            return f'{header}:\n{indent}{a} {left};\n{indent}{b} {right}'
        if kind is ast.Reach:
            # The source comes first, preserving endpoint order even in closure prose.
            left, right = self.term(value.left, scope), self.term(value.right, scope)
            count = 'one' if value.kind == 'plus' else 'zero'
            prefix = f'starting from {left}, {right} is reachable by {count} or more '
            if type(value.edge) is ast.Named:
                return prefix + quote(value.edge.relation) + ' steps'
            src, srcnoun = self.binding(value.edge.sort, scope)
            dst, dstnoun = self.binding(value.edge.sort, (src, *scope))
            body = self.formula(value.edge.formula, (dst, src, *scope), depth + 1)
            return (prefix + f'steps, where a step from {_article(srcnoun)} {srcnoun} to '
                    + f'{_article(dstnoun)} {dstnoun} satisfies the following:\n'
                    + '  ' * (depth + 1) + '(a) ' + body)
        raise TypeError('Unknown checked formula')

    def render(self, formula):
        self.maximum = _max_scope(formula)
        text = self.formula(formula)
        return text[0].upper() + text[1:]


def render_english(value, env):
    if type(value) is ast.Document:
        ast.check_document(env, value)
    else:
        ast.check_formula(env, value)
    traversal = EnglishTraversal(env)
    text = (''.join(traversal.render(f) + '.\n' for f in value.formulas)
            if type(value) is ast.Document else traversal.render(value))
    if len(text.encode('utf-8')) + (0 if type(value) is ast.Document else 2) > MAX_SOURCE_BYTES:
        raise ResourceLimit(f'Rendered ve_english text exceeds its {MAX_SOURCE_BYTES}-byte limit')
    return text


@dataclass(frozen=True)
class EnglishParseResult:
    document: ast.Document
    original: str
    english_text: str
    canonical_text: str

    def paraphrase(self):
        return {'input_text': self.original, 'english_text': self.english_text,
                'canonical_text': self.canonical_text,
                'changed': self.original != self.english_text}


def _literal_pattern(text):
    return r'\s+'.join(re.escape(part) for part in text.split(' '))


class EnglishParser:
    def __init__(self, env, source, words=None):
        self.env, self.source, self.i = env, source, 0
        self.words = words or EnglishVocabulary(env)
        self.nodes = 0
        self.farthest = 0

    def error(self, message, cls=SyntaxError):
        pos = max(self.i, self.farthest)
        raise cls(message, span=Span(pos, min(pos + 1, len(self.source)),
                                   self.source.count('\n', 0, pos) + 1,
                                   pos - self.source.rfind('\n', 0, pos)))

    def take(self, text):
        match = re.compile(_literal_pattern(text)).match(self.source, self.i)
        if match is None:
            return False
        # A literal word cannot consume just a prefix of a longer word.
        if text[-1:].isalnum() and match.end() < len(self.source) and re.match(r'[A-Za-z0-9_]', self.source[match.end()]):
            return False
        self.i = match.end()
        self.farthest = max(self.farthest, self.i)
        return True

    def need(self, text):
        if not self.take(text):
            self.error(f'Expected {text!r} here. Use the English paraphrase as a writing example.')

    def space(self):
        match = re.compile(r'\s+').match(self.source, self.i)
        if match is None:
            self.error('Expected a space between these words.')
        self.i = match.end()

    def declaration(self, scope):
        candidates = []
        for sort, noun in self.words.sorts.items():
            candidates.extend([(noun, (sort, 'that ' + noun)),
                               ('first ' + noun, (sort, 'the first ' + noun)),
                               ('second ' + noun, (sort, 'the second ' + noun))])
            # Names are bound in lexical scope; numbering is checked by paraphrase.
            prefix = noun + ' named '
            match = re.compile(_literal_pattern(prefix) + r'([A-Z]+[0-9]+)').match(self.source, self.i)
            if match:
                candidates.append((match.group(), (sort, match[1])))
        for text, binding in sorted(candidates, key=lambda item: -len(item[0])):
            start = self.i
            if self.take(text):
                if any(ref == binding[1] for _, ref in scope):
                    self.error('This name is already in scope. Use first and second, or distinct numbered names.')
                return binding
            self.i = start
        self.error('Expected a declared sort noun, optionally first, second, or a numbered name.')

    def term_options(self, scope):
        terms = {ref: ast.Var(index) for index, (_, ref) in reversed(list(enumerate(scope)))}
        terms.update({text: ast.Const(name) for name, text in self.words.constants.items()})
        return terms

    def atom(self, scope, relative=False):
        start = self.i
        terms = self.term_options(scope)
        term_pattern = '(?:' + '|'.join(_literal_pattern(t) for t in sorted(terms, key=lambda t: -len(t))) + ')'
        if not terms:
            term_pattern = r'(?!)'
        choices = []
        if not relative:
            for text, node in [('this holds in all cases', ast.Top()), ('this is impossible', ast.Bottom())]:
                if self.take(text): choices.append((self.i, node))
                self.i = start
        templates = []
        for name, template in self.words.predicates.items():
            decl = self.env.predicates[name]
            if relative and template != decl.verbalisation:
                continue
            templates.append((name, template, False))
        templates += [(name, template, True) for name, template in self.words.negatives.items()]
        if not relative:
            templates.append((None, '{0} is the same as {1}', False))
        for name, template, negative in templates:
            if relative:
                template = template.removeprefix('{0} ')
            parts = re.split(r'(\{[01]\})', template)
            pattern = ''.join(('(' + term_pattern + ')') if part in ('{0}', '{1}')
                              else _literal_pattern(part) for part in parts)
            match = re.compile(pattern).match(self.source, start)
            if not match:
                continue
            end = match.end()
            if end < len(self.source) and re.match(r'[A-Za-z0-9_]', self.source[end]):
                continue
            # Whitespace in a term can be edited; its binding is lexical, not textual.
            args = ([ast.Var(0)] if relative else []) + [terms[re.sub(r'\s+', ' ', t)] for t in match.groups()]
            if name is None:
                node = ast.Eq(*args)
            else:
                node = (ast.Unary if len(args) == 1 else ast.Binary)(name, *args)
                if negative: node = ast.Not(node)
            choices.append((end, node))
        if not choices:
            self.error('Expected a clause using a declared predicate and an in-scope noun reference or constant name.')
        # The lexicon is prefix-free at clause boundaries. Retain an explicit
        # ambiguity guard rather than silently selecting a competing template.
        longest = max(end for end, _ in choices)
        nodes = {node for end, node in choices if end == longest}
        if len(nodes) != 1:
            self.error('The vocabulary gives this clause more than one meaning. Use distinct predicate templates.')
        self.i = longest
        self.farthest = max(self.farthest, longest)
        return nodes.pop()

    def term(self, scope):
        for text, value in sorted(self.term_options(scope).items(), key=lambda item: -len(item[0])):
            if self.take(text): return value
        self.error('Expected a constant name or a definite reference to an entity already introduced.')

    def formula(self, scope=(), depth=0, nesting=1):
        if nesting > MAX_DEPTH:
            self.error(f'This statement exceeds the {MAX_DEPTH}-level nesting limit.', ResourceLimit)
        self.nodes += 1
        if self.nodes > MAX_NODES:
            self.error(f'This document exceeds the {MAX_NODES}-node limit.', ResourceLimit)
        def child(inner=scope, listed=False):
            return self.formula(inner, depth + int(listed), nesting + 1)
        if self.take('it is not the case that '):
            return ast.Not(child())
        for prefix, cls in [('all of the following hold:', ast.And),
                            ('at least one of the following holds:', ast.Or),
                            ('if the following holds:', ast.Implies)]:
            if self.take(prefix):
                a, b = _markers(depth)
                self.space(); self.need(a + ' ')
                left = child(listed=True)
                self.need(';'); self.space()
                if cls is ast.Implies:
                    self.need('then the following holds:'); self.space()
                self.need(b + ' ')
                return cls(left, child(listed=True))
        for prefix, cls, between, suffix in [('both ', ast.And, ' and ', ''),
                                               ('either ', ast.Or, ' or ', ', or both'),
                                               ('if ', ast.Implies, ', then ', '')]:
            if self.take(prefix):
                left = self.atom(scope)
                self.need(between)
                right = self.atom(scope)
                if suffix: self.need(suffix)
                return cls(left, right)
        if self.take('for every '):
            binding = self.declaration(scope)
            inner = (binding, *scope)
            guard = None
            if self.take(' that '): guard = self.atom(inner, relative=True)
            self.need(', ')
            body = child(inner)
            return ast.Forall(binding[0], ast.Implies(guard, body) if guard is not None else body)
        if self.take('every '):
            binding = self.declaration(scope)
            inner = (binding, *scope)
            guard = None
            if self.take(' that '): guard = self.atom(inner, relative=True)
            self.space()
            body = self.atom(inner, relative=True)
            return ast.Forall(binding[0], ast.Implies(guard, body) if guard is not None else body)
        if self.take('there is '):
            if not (self.take('an ') or self.take('a ')): self.error('Expected a or an before the sort noun.')
            binding = self.declaration(scope)
            inner = (binding, *scope)
            if self.take(' who ') or self.take(' that '):
                body = self.atom(inner, relative=True)
            else:
                self.need(' such that '); body = child(inner)
            return ast.Exists(binding[0], body)
        if self.take('starting from '):
            left = self.term(scope); self.need(', '); right = self.term(scope)
            self.need(' is reachable by ')
            if self.take('one '): kind = 'plus'
            else: self.need('zero '); kind = 'star'
            self.need('or more ')
            for name, decl in self.env.predicates.items():
                if len(decl.arguments) == 2 and decl.arguments[0] == decl.arguments[1] and self.take(quote(name) + ' steps'):
                    return ast.Reach(kind, ast.Named(name), left, right)
            self.need('steps, where a step from ')
            if not (self.take('an ') or self.take('a ')): self.error('Expected a or an before the step source.')
            src = self.declaration(scope); self.need(' to ')
            if not (self.take('an ') or self.take('a ')): self.error('Expected a or an before the step destination.')
            dst = self.declaration((src, *scope))
            if src[0] != dst[0]: self.error('The source and destination of a step must have the same sort.')
            self.need(' satisfies the following:'); self.space(); self.need('(a) ')
            return ast.Reach(kind, ast.Body(src[0], child((dst, src, *scope), listed=True)), left, right)
        return self.atom(scope)

    def document(self):
        formulas = []
        while self.i < len(self.source):
            # Only sentence-initial capitalization is optional. Preserve proper nouns.
            if self.source[self.i].isupper():
                self.source = self.source[:self.i] + self.source[self.i].lower() + self.source[self.i+1:]
            formulas.append(self.formula())
            self.need('.')
            if self.i < len(self.source): self.space()
        if not formulas: self.error('Write at least one statement ending with a period.')
        return ast.Document(tuple(formulas))


def parse_english_with_metadata(env, source):
    if isinstance(source, bytes):
        try: source = source.decode('utf-8')
        except UnicodeDecodeError as exc:
            raise SyntaxError('English input must be UTF-8.', span=Span(exc.start, exc.end, 1, exc.start + 1)) from exc
    if not isinstance(source, str): raise TypeError('source must be str or bytes')
    if len(source.encode('utf-8')) > MAX_SOURCE_BYTES:
        raise ResourceLimit(f'English source exceeds {MAX_SOURCE_BYTES} bytes')
    parser = EnglishParser(env, source)
    document = parser.document()
    try:
        ast.check_document(env, document)
    except VEError as exc:
        if exc.span is None: exc.span = Span(0, len(source), 1, 1)
        raise
    english = render_english(document, env)
    from .printer import print_document
    return EnglishParseResult(document, source, english, print_document(env, document))


def parse_english(env, source):
    return parse_english_with_metadata(env, source).document


def english_legend(env, style='json'):
    words = EnglishVocabulary(env)
    record = {
        'format': 've.english-legend@1', 'environment_id': env.environment_id,
        'reference_rule': 'A unique sort uses that noun. Two simultaneous entities of a sort use '
                          'first and second throughout the statement. Beyond two, all entities of '
                          'that sort use numbered letters. Scope is lexical and restarts per statement.',
        'letters_by_sort': words.letters,
        'constant_rule': 'Constants use their identifier names; reserved or compound names are quoted.',
        'closure_rule': 'Starting from the first endpoint, the second is reachable. '
                        'A step body binds source first and destination second; outer references stay fixed.',
        'sorts': {name: {'noun': words.sorts[name], 'description': d.description} for name, d in sorted(env.sorts.items())},
        'predicates': {name: {'arguments': list(d.arguments), 'template': words.predicates[name],
                             'declared_template': d.verbalisation, 'negative_template': words.negatives.get(name),
                             'declared_negative_template': d.negative_verbalisation,
                             'description': d.description} for name, d in sorted(env.predicates.items())},
        'constants': {name: {'name': words.constants[name], 'sort': d.sort, 'description': d.description}
                      for name, d in sorted(env.constants.items())},
        'lint': [i.to_dict() for i in words.issues],
    }
    if style == 'json': return json.dumps(record, ensure_ascii=False, sort_keys=True, indent=2) + '\n'
    lines = [f"English vocabulary: {record['format']}; environment: {env.environment_id}",
             record['reference_rule'], record['constant_rule'], record['closure_rule'],
             'Numbered letters: ' + ', '.join(f'{s} = {l}' for s, l in sorted(words.letters.items()))]
    for name, entry in record['sorts'].items(): lines.append(f'Sort {name}: {json.dumps(entry, ensure_ascii=False)}')
    for name, entry in record['predicates'].items(): lines.append(f'Predicate {name}: {json.dumps(entry, ensure_ascii=False)}')
    for name, entry in record['constants'].items(): lines.append(f'Constant {name}: {json.dumps(entry, ensure_ascii=False)}')
    lines.extend(f'Lint {i.path}: {i.code}' for i in words.issues)
    return '\n'.join(lines) + '\n'


def english_lark_grammar(env):
    """Independent context-free syntax envelope for all-derivations auditing.

    Scope, sorts, article choice, indentation and canonical contraction selection
    are checked separately. Removing those constraints can only add derivations;
    a unique parse here therefore also has at most one well-typed derivation.
    Literal templates are expanded as productions, never hidden in a catch-all
    atom token or a prioritized lexer.
    """
    words = EnglishVocabulary(env)
    lit = lambda s: json.dumps(s)
    rules = [
        'start: formula "."',
        '?formula: atom | negation | compact | listing | universal | existential | reach',
        'negation: "it is not the case that" formula',
        'compact: "both" atom "and" atom -> conjunction\n'
        '       | "either" atom "or" atom ", or both" -> disjunction\n'
        '       | "if" atom ", then" atom -> implication',
        'listing: "all of the following hold:" marker formula ";" marker formula -> conjunction_list\n'
        '       | "at least one of the following holds:" marker formula ";" marker formula -> disjunction_list\n'
        '       | "if the following holds:" marker formula ";" "then the following holds:" marker formula -> implication_list',
        'marker: "(a)" | "(b)" | "(i)" | "(ii)"',
        'universal: "for every" declaration "," formula -> universal_global\n'
        '         | "for every" declaration "that" relative "," formula -> universal_guard\n'
        '         | "every" declaration relative -> universal_relative\n'
        '         | "every" declaration "that" relative relative -> universal_guard_relative',
        'existential: "there is" article declaration "such that" formula -> existential_global\n'
        '           | "there is" article declaration "who" relative -> existential_relative\n'
        '           | "there is" article declaration "that" relative -> existential_relative',
        'article: "a" | "an"',
        'declaration: noun | "first" noun | "second" noun | noun "named" LABEL',
        'term: constant | "that" noun | "the first" noun | "the second" noun | LABEL',
        'reach: "starting from" term "," term "is reachable by" count "or more" relation "steps" -> named_reach\n'
        '     | "starting from" term "," term "is reachable by" count "or more steps, where a step from" article declaration "to" article declaration "satisfies the following:" "(a)" formula -> body_reach',
        'count: "one" | "zero"',
        'noun: ' + ' | '.join(lit(n) for n in words.sorts.values()),
        'LABEL: /(?:' + '|'.join(re.escape(l) for l in words.letters.values()) + ')[1-9][0-9]*/',
    ]
    constants = [lit(v) for v in words.constants.values()]
    # An impossible terminal keeps grammars valid for empty vocabularies.
    rules.append('constant: ' + (' | '.join(constants) or 'IMPOSSIBLE'))
    relations = [lit(quote(n)) for n, p in env.predicates.items()
                 if len(p.arguments) == 2 and p.arguments[0] == p.arguments[1]]
    rules.append('relation: ' + (' | '.join(relations) or 'IMPOSSIBLE'))
    atoms = ['"this holds in all cases"', '"this is impossible"', 'term "is the same as" term']
    relatives = []
    for templates in (words.predicates, words.negatives):
        for name, template in templates.items():
            parts = re.split(r'(\{[01]\})', template)
            rule = ' '.join('term' if p in ('{0}', '{1}') else lit(p.strip())
                            for p in parts if p.strip())
            atoms.append(rule)
            if templates is words.negatives or template == env.predicates[name].verbalisation:
                relatives.append(rule.removeprefix('term '))
    rules.append('atom: ' + ' | '.join(atoms))
    rules.append('relative: ' + (' | '.join(relatives) or 'IMPOSSIBLE'))
    rules.extend(['IMPOSSIBLE: /[^\\s\\S]/', '%import common.WS', '%ignore WS'])
    return '\n'.join(rules) + '\n'
