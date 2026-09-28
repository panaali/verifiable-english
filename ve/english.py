"""Writable, scoped English. Canonical serialization remains in printer.py.

The grammar uses prefix clauses, binary drafting lists and a finite, checked
lexicon. Audited natural forms add a few fixed contractions; no reassociation
or semantic rewriting is admitted.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
import re
import warnings

from . import ast
from .errors import ResourceLimit, Span, SyntaxError, VEError
from .limits import MAX_DEPTH, MAX_NODES, MAX_SOURCE_BYTES
from .english_phrases import nearest, phrase_end, unary_phrase, wording_key, BOUNDARIES
from .printer import (_NaturalVocabulary, _LOGICAL_WORDS, render_int_term,
                      _fluent_variable_letters, _template_head, _AUXILIARIES, VocabularyLint)
from .english_vocabulary import IDIOMS, negative_template, display_environment, overlay_provenance
from .surface import registry as surface_registry

# These are lexical noun/adjective complements, not extra semantic operators.
# They are deliberately finite: a linter cannot establish arbitrary English meaning.
_COMPLEMENTS = (
    r"is (?:subject to the jurisdiction of|a citizen of) the United States",
    r"was (?:born|naturalized) in the United States",
    r"is (?:fully|newly|currently|publicly) (?P<adjective>[a-z]+)",
    r"is (?P<adjective>[a-z]+) (?:in good standing|under review)",
)
_ACTIVE = (
    r"affords due process of law to",
    r"denies the equal protection of the laws to",
    r"(?:reports|contributes|responds) to",
    r"(?:communicates|collaborates) with",
    r"has (?:access to|authority over|responsibility for)",
)
_EXTRA_RESERVED = frozenset("this it holds impossible classified recorded relation entity sort named first second following hold who where step steps source destination from reachable using starting ending definition end therefore so hence".split())
_ORDINALS = ('first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth')
_EXTRA_RESERVED |= frozenset(_ORDINALS)
_RESERVED = _LOGICAL_WORDS | _EXTRA_RESERVED
# order@0 comparison wording ("at least n" is a comparison, never a counting quantifier).
_COMPARISON_WORDS = frozenset('less more than least most same'.split())
_COMPARISONS = (('{0} is less than {1}', ast.Lt, False), ('{0} is at most {1}', ast.Le, False),
                ('{0} is more than {1}', ast.Lt, True), ('{0} is at least {1}', ast.Le, True))
# Integer slots match any bracket depth: outermost bracket groups are masked
# (length-preserving) before regex matching, and the exact term text is then
# checked by `int_syntax` and parsed by `int_term`, which budgets term depth
# exactly as the type checker does (MAX_DEPTH), so every renderable integer
# term of a valid AST parses back.
_INT_MASK = '\x00'
_CONCLUSION_MARKERS = ('therefore ', 'so ', 'hence ', 'it follows that ')


def _mentioned_constants(value):
    """Collect explicit constant references, including those under binders."""
    found = set()
    stack = [value]
    while stack:
        node = stack.pop()
        if type(node) is ast.Const:
            found.add(node.name)
        for field in ('term', 'left', 'right', 'body', 'edge', 'formula'):
            child = getattr(node, field, None)
            if child is not None:
                stack.append(child)
    return found


def _has_discourse_binder(value):
    """A prior quantified mention prevents automatic constant-only anaphora.

    A binder does not introduce a named constant. Its witness may nevertheless
    be what an ordinary reader takes a later ``it`` to denote. Until a scoped
    discourse representation exists, the author must repeat an explicit name.
    """
    stack = [value]
    while stack:
        node = stack.pop()
        if type(node) in (ast.Exists, ast.Forall):
            return True
        for field in ('body', 'left', 'right', 'edge', 'formula'):
            child = getattr(node, field, None)
            if child is not None:
                stack.append(child)
    return False


def _fold_sentence_initials(source, words):
    quoted_positions = set()
    quoted = escaped = False
    for index, char in enumerate(source):
        if quoted:
            quoted_positions.add(index)
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
            quoted_positions.add(index)

    def initial(word, tail):
        for name, value in words.constants.items():
            if name not in words.declared_constants or value.startswith('"'):
                continue
            # Only a genuinely capitalized declared name needs its case kept.
            # A lowercase alias such as "api" must accept sentence-initial Api.
            if value[0].isupper() and re.match(
                    _literal_pattern(value) + r'(?![A-Za-z0-9_])', tail):
                return word
        return word[0].lower() + word[1:]

    def fold(match):
        if match.start(2) in quoted_positions:
            return match[0]
        return match[1] + initial(match[2], source[match.start(2):])

    source = re.sub(r'(^|(?<=\.)\s+)([A-Z][A-Za-z]*)', fold, source)
    # A conclusion marker begins a second sentence-initial position. The
    # marker itself is folded above, but the claim's first word also needs it.
    def fold_conclusion(match):
        if match.start(3) in quoted_positions:
            return match[0]
        return match[1] + match[2] + initial(match[3], source[match.start(3):])
    return re.sub(r'(^|(?<=\.)\s+)((?:therefore|so|hence|it\s+follows\s+that)\s+)([A-Z][A-Za-z]*)',
                  fold_conclusion, source)


def _normalise_english_source(source, words):
    """Give every English reader the same editable whitespace and initial case.

    Keep quoted identifiers byte-for-byte. The boundary map lets presentation
    spans continue to refer to the author's original text after whitespace is
    collapsed for parsing and the independent derivation check.
    """
    chars, boundaries = [], [0]
    quoted = escaped = False
    i = 0
    while i < len(source):
        char = source[i]
        if not quoted and char.isspace():
            end = i + 1
            while end < len(source) and source[end].isspace():
                end += 1
            chars.append(' ')
            boundaries.append(end)
            i = end
            continue
        chars.append(char)
        boundaries.append(i + 1)
        if quoted:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        i += 1
    return _fold_sentence_initials(''.join(chars), words), boundaries


def _mask_brackets(source):
    """Replace the interior of each balanced outermost [...] group by _INT_MASK."""
    chars, stack = list(source), []
    for index, char in enumerate(source):
        if char == '[':
            stack.append(index)
        elif char == ']' and stack:
            open_ = stack.pop()
            if not stack:
                chars[open_ + 1:index] = _INT_MASK * (index - open_ - 1)
    return ''.join(chars)


# Function words cannot establish a semantic connection to a declaration.
_CONTENT_STOP = frozenset("a an the is was are be been being has have its in on at to of for from by with and or as that this recorded predicate first second".split())


def _content_words(text):
    words = set(re.findall(r'[a-z]+', text.lower())) - _CONTENT_STOP
    return {re.sub(r'(?:ing|ed|s)$', '', w) for w in words}


def quote(name):
    return json.dumps(name, ensure_ascii=True)


class UnreviewedVocabularyWarning(UserWarning):
    """A claim-only API rendering uses an overlay without a pinned review."""


class EnglishVocabulary:
    """Versioned precision pass; leaves the five historical views byte-stable."""
    def __init__(self, env, vocabulary=None, accept_suggested_vocabulary=False):
        env, self.overlay_digest, self.overlay = display_environment(env, vocabulary, accept_suggested_vocabulary)
        self.provenance = overlay_provenance(vocabulary)
        self.review_status = self.provenance["review_status"]
        old = _NaturalVocabulary(env)
        self.env = env
        self.sorts = {}
        for name, noun in old.sorts.items():
            if env.sorts[name].verbalisation:
                noun = env.sorts[name].verbalisation.singular
            if (re.fullmatch(r"[A-Za-z]+(?: [A-Za-z]+)*", noun)
                    and not set(noun.lower().split()) & _RESERVED
                    and noun.lower() not in {*env.predicates, *env.constants}):
                self.sorts[name] = noun
            else:
                self.sorts[name] = 'entity of sort ' + quote(name)
        # Reject aliases equal to ANY other selected noun, including fallbacks.
        counts = Counter(wording_key(n) for n in self.sorts.values())
        for name, noun in list(self.sorts.items()):
            if counts[wording_key(noun)] > 1:
                self.sorts[name] = 'entity of sort ' + quote(name)
        self.predicates, self.negatives = {}, {}
        issues = set(old.issues)
        for name, noun in self.sorts.items():
            decl = env.sorts[name]
            if decl.verbalisation and noun == decl.verbalisation.singular:
                issues = {i for i in issues if not i.path.startswith(f'/vocabulary/sorts/{name}/')}
        template_owners = {}
        for name, decl in env.predicates.items():
            for template in (decl.verbalisation or old.predicates[name], decl.negative_verbalisation):
                if template:
                    template_owners.setdefault(wording_key(template), set()).add(name)
        for name, decl in env.predicates.items():
            template = decl.verbalisation
            path = f"/vocabulary/predicates/{name}/verbalisation"
            codes = {i.code for i in issues if i.path == path}
            accepted = template is not None and not codes
            if len(decl.arguments) > 2:
                self.predicates[name] = template if accepted else old.predicates[name]
                if accepted:
                    issues = {i for i in issues if i.path != path}
                continue
            if template and (not accepted or template in IDIOMS[len(decl.arguments)]):
                phrase = template.removeprefix('{0} ')
                unary = len(decl.arguments) == 1
                if not unary:
                    phrase = phrase.removesuffix(' {1}')
                patterns = _COMPLEMENTS if unary else _ACTIVE
                shaped = template == '{0} ' + phrase + ('' if unary else ' {1}')
                # Fixed idioms may contain articles/proper nouns and a sort noun.
                # Predicate/constant collisions and negative heads still reject.
                eligible_codes = {'LOGICAL_WORD', 'PHRASE_SYNTAX', 'UNARY_MODIFIER',
                                      'TEMPLATE_SHAPE', 'TEMPLATE_LENGTH', 'SORT_NOUN',
                                      'SYMBOL_COLLISION', 'BINARY_CONVERSE', 'BINARY_AUXILIARY', 'BINARY_VERB'}
                eligible = codes <= eligible_codes
                collision = any(re.search(r'\b' + re.escape(other) + r'\b', phrase)
                                for other in (*env.predicates, *env.constants) if other != name)
                # Auxiliary/article heads from rejected templates are not lexical heads.
                collision |= any(head and head not in {'is', 'was', 'a', 'an'} and re.search(r'\b' + re.escape(head) + r'\b', phrase)
                                 for other, decl2 in env.predicates.items() if other != name
                                 for head in [_template_head(decl2.verbalisation or '', len(decl2.arguments))])
                heads = [p.verbalisation.split()[2] for p in env.predicates.values()
                         if p.verbalisation and p.verbalisation.startswith('{0} is ')
                         and len(p.verbalisation.split()) > 2]
                negated = any(word in {'un' + h, 'non' + h} for h in (*env.predicates, *heads)
                              for word in phrase.split())
                matches = [m for pattern in patterns if (m := re.fullmatch(pattern, phrase))]
                lexical_adjectives = [m.groupdict().get('adjective') for m in matches]
                noun_words = set(env.sorts)
                for sort_decl in env.sorts.values():
                    if sort_decl.verbalisation:
                        noun_words.update(sort_decl.verbalisation.singular.split())
                        noun_words.update(sort_decl.verbalisation.plural.split())
                safe_adjectives = all(a is None or a not in (_RESERVED | _AUXILIARIES | noun_words)
                                      for a in lexical_adjectives)
                accepted = bool(shaped and eligible and not collision and not negated
                                and len(template) <= 80
                                and matches and safe_adjectives)
                if template in IDIOMS[len(decl.arguments)]:
                    # An idiom licenses syntax only. Check its lexical ownership
                    # and direction against this declaration and every other entry.
                    content = _content_words(template)
                    anchored = bool(content & _content_words(name + ' ' + decl.description))
                    idiom_collision = any(
                        re.search(r'\b' + re.escape(other) + r'\b', phrase)
                        for other in env.constants)
                    for other, other_decl in env.predicates.items():
                        if other == name:
                            continue
                        head = _template_head(other_decl.verbalisation or '', len(other_decl.arguments))
                        for token in (other, head):
                            if not token or token in {'is', 'was', 'a', 'an', 'has'}:
                                continue
                            # Shared lexical families (undermines/undermines_check)
                            # require explicit ownership in BOTH predicate names.
                            shared = token in name.split('_') and token in other.split('_')
                            # Longer fixed complements distinguish shared heads.
                            head_collision = (token == head and content <= _content_words(other_decl.verbalisation or ''))
                            if not shared and (token == other or head_collision) and re.search(r'\b' + re.escape(token) + r'\b', phrase):
                                idiom_collision = True
                    # Passive "by" is admissible only with an explicitly passive
                    # predicate name; a matching generic gloss cannot reverse it.
                    converse = phrase.endswith(' by') and not name.endswith('_by')
                    if not anchored:
                        issues.add(VocabularyLint(path, 'IDIOM_UNRELATED'))
                    if idiom_collision:
                        issues.add(VocabularyLint(path, 'SYMBOL_COLLISION'))
                    accepted = (codes <= (eligible_codes | {'VARIABLE_TOKEN'}) and anchored and not idiom_collision and not converse
                                and not negated and 'DUPLICATE_TEMPLATE' not in codes)
            if template is None and re.fullmatch('[a-z]+', name) and name not in _RESERVED:
                if len(decl.arguments) == 1 or name in {'owns', 'audits', 'undermines', 'performs', 'follows', 'benefits', 'outranks', 'exceeds'}:
                    self.predicates[name] = old.predicates[name]
                    continue
            # Explicitly accepted finite unary phrases from the proposal workflow.
            # The ordinary environment linter and historical views stay unchanged.
            entry = self.overlay['predicates'].get(name, {})
            if (entry.get('suggested') and len(decl.arguments) == 1 and template
                    and unary_phrase(template) is not None):
                phrase = unary_phrase(template)
                collision = any(re.search(r'\b' + re.escape(n) + r'\b', phrase, re.I)
                                for n in env.constants)
                duplicate = any(n != name and d.verbalisation and wording_key(d.verbalisation) == wording_key(template)
                                for n, d in env.predicates.items())
                heads = set(env.predicates) | {_template_head(d.verbalisation or '', len(d.arguments))
                                                for d in env.predicates.values()}
                negated_heads = {prefix + h.lower() for h in heads if h
                                 for prefix in ('un', 'non', 'un-', 'non-')}
                negated = bool(negated_heads & set(re.findall(r'[a-z][a-z0-9_-]*', phrase.lower())))
                if not collision and not duplicate and not negated and 'NEGATED_HEAD' not in codes:
                    accepted = True
            if accepted and template not in IDIOMS[len(decl.arguments)] and set(re.findall(r'[a-z]+', template)) & _EXTRA_RESERVED:
                accepted = False
                issues.add(VocabularyLint(path, 'ENGLISH_STRUCTURE_WORD'))
            if accepted and getattr(env, 'order', False) and set(re.findall(r'[a-z]+', template.lower())) & _COMPARISON_WORDS:
                accepted = False
                issues.add(VocabularyLint(path, 'ENGLISH_STRUCTURE_WORD'))
            duplicates = set().union(*(template_owners.get(wording_key(t), set())
                                       for t in (template, decl.negative_verbalisation) if t)) - {name}
            if duplicates:
                accepted = False
                issues.add(VocabularyLint(path, 'DUPLICATE_TEMPLATE'))
                if name in self.overlay['predicates']:
                    raise VEError(f'Duplicate English wording {template!r} for {name!r}; '
                                  f'existing symbol(s): {", ".join(sorted(duplicates))}')
            if accepted:
                self.predicates[name] = template
                issues = {i for i in issues if i.path != path}
            else:
                self.predicates[name] = ('{0} is classified as ' + quote(name) if len(decl.arguments) == 1
                                         else '{0} has the recorded relation ' + quote(name) + ' to {1}')
            negative = decl.negative_verbalisation
            if (accepted and negative
                    and negative == negative_template(template, len(decl.arguments))):
                # Old negative length limits continue to apply.
                if len(negative) <= 120 and len(negative.split()) <= 18:
                    self.negatives[name] = negative
                    negative_path = path.replace("/verbalisation", "/negative_verbalisation")
                    issues = {i for i in issues if i.path != negative_path}
        # alternatives@0 fixes these exact forms as part of its declaration
        # contract. Generic vocabulary lint is deliberately more restrictive
        # about auxiliary verbs and common words.
        if getattr(env, 'alternatives', None) is not None:
            from .wire import loads_json
            block = loads_json(env.alternatives)
            for role in ('available', 'leads_to', 'inaction', 'taken', 'proximate'):
                if role in block:
                    name = block[role]
                    self.predicates[name] = env.predicates[name].verbalisation
                    issues = {i for i in issues if not i.path.startswith(f'/vocabulary/predicates/{name}/')}
            self.predicates.update({
                'avoidable': '{0} is avoidable by {1}',
                'unavoidable': '{0} is unavoidable by {1}',
                'allows': '{0} allows {1} to happen',
                'prevents': '{0} prevents {1}',
            })
        self.issues = tuple(sorted(issues, key=lambda i: (i.path, i.code)))
        self.letters = _fluent_variable_letters(self.sorts, env)
        self.constants = {name: (name if re.fullmatch('[a-z]+', name)
                                and name not in _RESERVED and name not in {'is', 'has'} else quote(name))
                          for name in env.constants}
        # Names are declared display data, never inferred from descriptions.
        # A rejected or colliding form retains its exact quoted identifier.
        aliases = {}
        self.declared_constants = {name: entry['verbalisation']
                                   for name, entry in self.overlay['constants'].items()}
        for name in env.constants:
            form = self.declared_constants.get(name)
            if form is None:
                continue
            self.constants[name] = quote(name)
            if (re.fullmatch(r'(?:the )?[A-Za-z][A-Za-z]*(?: [A-Za-z][A-Za-z]*)*', form)
                    and not set(form.lower().split()) & (_RESERVED - {'the'})
                    and not any(wording_key(form) == wording_key(noun) for noun in self.sorts.values())):
                aliases.setdefault(wording_key(form), []).append(name)
        for names in aliases.values():
            if len(names) == 1:
                name = names[0]
                self.constants[name] = self.declared_constants[name]
        # The parser also accepts sentence-initial and definite-article forms.
        # Compare every such spelling before selecting an alias: a declared
        # "the api" otherwise shadows the generated "the api" for plain api.
        def spellings(value):
            forms = {value}
            if value.startswith('the '):
                forms.add(value[0].upper() + value[1:])
            if re.fullmatch('[a-z]+', value):
                forms.add('the ' + value)
            return {wording_key(form) for form in forms}

        while True:
            owners = {}
            for name, value in self.constants.items():
                for form in spellings(value):
                    owners.setdefault(form, set()).add(name)
            collided = {name for names in owners.values() if len(names) > 1 for name in names
                        if name in self.declared_constants and self.constants[name] != quote(name)}
            if not collided:
                break
            for name in collided:
                self.constants[name] = quote(name)
        for category in ('sorts', 'predicates'):
            for name, entry in self.overlay[category].items():
                expected = entry['verbalisation']
                selected = self.sorts[name] if category == 'sorts' else self.predicates[name]
                if (selected != (expected['singular'] if category == 'sorts' else expected)
                        or any(i.path.startswith(f'/vocabulary/{category}/{name}/') for i in self.issues)):
                    raise VEError(f'English vocabulary entry fails the template linter: {category}/{name}')
        # A regulated atom in a norm guard has one deontic spelling. The norm
        # consequence parser handles must not / need not separately; ordinary
        # formula parsing and the independent Earley grammar share these atoms.
        if 'norms@0' in env.profiles:
            for name, decl in env.predicates.items():
                reg = decl.regulated
                if reg is not None and reg.role in ('permission', 'obligation'):
                    modal = 'may' if reg.role == 'permission' else 'must'
                    self.predicates[name] = reg.act.replace('{0} ', '{0} ' + modal + ' ', 1)
                    self.negatives.pop(name, None)

    def atom(self, name, terms, negative=False):
        text = (self.negatives if negative else self.predicates)[name]
        for i, term in enumerate(terms):
            text = text.replace('{' + str(i) + '}', term)
        return text

    def natural_constants(self):
        """Identifiers remain exact: spacing aliases lose repeated underscores."""
        return {}


def lint_english_vocabulary(env, **options):
    return EnglishVocabulary(env, **options).issues


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
    def __init__(self, env, words=None, *, word_markers=False,
                 avoid_negative_universal=False):
        self.env = env
        self.words = words or EnglishVocabulary(env)
        self.word_markers = word_markers
        self.avoid_negative_universal = avoid_negative_universal

    def binding(self, sort, scope):
        noun = self.words.sorts[sort]
        index = sum(s == sort for s, _ in scope)
        mode = self.maximum[sort]
        if mode <= 1:
            return (sort, 'that ' + noun), noun
        if mode == 2 or (self.word_markers and index < len(_ORDINALS)):
            noun = _ORDINALS[index] + ' ' + noun
            return (sort, 'the ' + noun), noun
        label = self.words.letters[sort] + str(index + 1)
        return (sort, label), noun + ' named ' + label

    def term(self, value, scope):
        if type(value) is ast.Var:
            return scope[value.index][1]
        if type(value) is ast.Const:
            return self.words.constants[value.name]
        # order@0 integer terms keep the frozen bracketed canonical spelling.
        return render_int_term(value, lambda leaf: self.term(leaf, scope))

    def simple(self, value):
        return type(value) in (ast.Top, ast.Bottom, ast.Unary, ast.Binary, ast.Eq, ast.Lt, ast.Le) or (
            type(value) is ast.Not and type(value.body) in (ast.Unary, ast.Binary)
            and value.body.predicate in self.words.negatives)

    def relative(self, value, scope, object_allowed=False):
        negative = type(value) is ast.Not
        atom = value.body if negative else value
        if type(atom) not in (ast.Unary, ast.Binary):
            return None
        if negative and atom.predicate not in self.words.negatives:
            return None
        if (atom.term if type(atom) is ast.Unary else atom.left) == ast.Var(0):
            return self.formula(value, scope)[len(scope[0][1]) + 1:]
        if object_allowed and type(atom) is ast.Binary and atom.right == ast.Var(0):
            template = (self.words.negatives if negative else self.words.predicates)[atom.predicate]
            return template.replace('{0}', self.term(atom.left, scope)).replace(' {1}', '')
        return None

    def guard(self, value, scope):
        """At most three atoms; a comma preserves the binary tree for triples."""
        relative = lambda value: self.relative(value, scope, object_allowed=True)
        if type(value) is not ast.And:
            return relative(value)
        left, right = relative(value.left), relative(value.right)
        if left and right:
            return left + ' and ' + right
        if type(value.left) is ast.And and right:
            a, b = relative(value.left.left), relative(value.left.right)
            if a and b: return a + ' and ' + b + ', and ' + right
        if left and type(value.right) is ast.And:
            b, c = relative(value.right.left), relative(value.right.right)
            if b and c: return left + ', and ' + b + ' and ' + c
        return None

    def alternatives_guard(self, value, scope):
        if getattr(self.env, 'alternatives', None) is None or type(value) not in (ast.Forall, ast.Exists):
            return None
        from .wire import loads_json
        block = loads_json(self.env.alternatives)
        if value.sort != block['action']:
            return None
        if type(value) is ast.Forall and type(value.body) is ast.Implies:
            condition, body = value.body.left, value.body.right
            quantifier = 'every'
        elif type(value) is ast.Exists and type(value.body) is ast.And:
            condition, body = value.body.left, value.body.right
            quantifier = 'another'
        else:
            return None
        other = False
        if type(condition) is ast.And:
            first, difference = condition.left, condition.right
            if (type(difference) is not ast.Not or type(difference.body) is not ast.Eq
                    or difference.body.left != ast.Var(0)
                    or type(difference.body.right) is not ast.Var):
                return None
            outer = difference.body.right.index - 1
            if (outer < 0 or outer >= len(scope) or scope[outer][0] != block['action']):
                return None
            condition, other = first, True
        if (type(condition) is not ast.Binary or condition.predicate != block['available']
                or condition.left != ast.Var(0)):
            return None
        if quantifier == 'another' and not other:
            return None
        owner = condition.right
        if type(owner) is ast.Var:
            if owner.index == 0 or owner.index > len(scope):
                return None
            owner = ast.Var(owner.index - 1)
        inner = ((block['action'], 'that other ' + self.words.sorts[block['action']]
                  if other else 'that ' + self.words.sorts[block['action']]), *scope)

        def vp(atom):
            return self.relative(atom, inner)

        verbal = vp(body)
        if verbal is None and type(body) in (ast.And, ast.Or):
            left, right = vp(body.left), vp(body.right)
            if left is not None and right is not None:
                verbal = ('both ' + left + ' and ' + right if type(body) is ast.And else
                          'either ' + left + ' or ' + right)
        if verbal is None:
            return None
        noun = self.words.sorts[block['action']]
        prefix = ('another ' if quantifier == 'another' else
                  'every other ' if other else 'every ')
        return prefix + noun + ' available to ' + self.term(owner, scope) + ' ' + verbal

    def formula(self, value, scope=(), depth=0):
        kind = type(value)
        if kind is ast.Exists and 'data@0' in self.env.profiles and type(value.body) is ast.And:
            relation, property_atom = value.body.left, value.body.right
            if (type(relation) is ast.Binary and type(property_atom) is ast.Unary
                    and relation.right == ast.Var(0) and property_atom.term == ast.Var(0)
                    and relation.predicate in self.env.predicates
                    and property_atom.predicate in self.env.predicates):
                declaration = self.env.predicates[relation.predicate]
                if (declaration.functional and declaration.total and declaration.arguments[1] == value.sort
                        and self.env.predicates[property_atom.predicate].arguments == (value.sort,)
                        and (type(relation.left) is ast.Const or
                             type(relation.left) is ast.Var and relation.left.index > 0)):
                    source = (ast.Var(relation.left.index - 1) if type(relation.left) is ast.Var
                              else relation.left)
                    return ('the ' + relation.predicate + ' of ' + self.term(source, scope)
                            + ' is ' + property_atom.predicate)
        special = self.alternatives_guard(value, scope)
        if special is not None:
            return special
        record = surface_registry.by_node(value)
        if record is not None and record.english_renderer is not None and surface_registry.enabled(record, self.env):
            return record.english_renderer(self, value, scope, depth)
        if kind is ast.Top: return 'this holds in all cases'
        if kind is ast.Bottom: return 'this is impossible'
        if kind in (ast.Unary, ast.Binary):
            terms = (value.term,) if kind is ast.Unary else (value.left, value.right)
            if kind is ast.Binary and 'data@0' in self.env.profiles:
                declaration = self.env.predicates[value.predicate]
                if declaration.functional and declaration.total:
                    return ('the ' + value.predicate + ' of ' + self.term(value.left, scope)
                            + ' is ' + self.term(value.right, scope))
            return self.words.atom(value.predicate, [self.term(t, scope) for t in terms])
        if kind is ast.Eq:
            return self.term(value.left, scope) + ' is the same as ' + self.term(value.right, scope)
        if kind in (ast.Lt, ast.Le):
            # Comparisons only: "at least"/"more than" are accepted when parsing
            # (swapping the operands); rendering always uses these two forms.
            return (self.term(value.left, scope) + (' is less than ' if kind is ast.Lt else ' is at most ')
                    + self.term(value.right, scope))
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
                    guard = self.guard(value.body.left, inner)
                    if guard:
                        pronoun = ' who ' if self.words.sorts[value.sort] == 'person' else ' that '
                        consequent = (None if self.avoid_negative_universal and type(value.body.right) is ast.Not
                                      else self.relative(value.body.right, inner))
                        if consequent:
                            return 'every ' + noun + pronoun + guard + ' ' + consequent
                        explicit_body = ('it is not the case that ' + self.formula(value.body.right.body, inner, depth)
                                         if self.avoid_negative_universal and type(value.body.right) is ast.Not
                                         else self.formula(value.body.right, inner, depth))
                        return ('for every ' + noun + pronoun + guard + ', '
                                + explicit_body)
                consequent = (None if self.avoid_negative_universal and type(value.body) is ast.Not
                              else self.relative(value.body, inner))
                if consequent:
                    return 'every ' + noun + ' ' + consequent
                if self.avoid_negative_universal and type(value.body) is ast.Not:
                    return ('for every ' + noun + ', it is not the case that '
                            + self.formula(value.body.body, inner, depth))
                return 'for every ' + noun + ', ' + self.formula(value.body, inner, depth)
            relative = self.relative(value.body, inner)
            if relative:
                return 'there is ' + _article(noun) + ' ' + noun + (' who ' if self.words.sorts[value.sort] == 'person' else ' that ') + relative
            return ('there is ' + _article(noun) + ' ' + noun + ' such that '
                    + self.formula(value.body, inner, depth))
        if kind in (ast.And, ast.Or, ast.Implies):
            if kind is ast.Implies:
                return ('if ' + self.formula(value.left, scope, depth) + ', then '
                        + self.formula(value.right, scope, depth))
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
            header = 'all of the following hold' if kind is ast.And else 'at least one of the following holds'
            if kind is ast.And and not any(type(v) in (ast.And, ast.Or, ast.Implies) for v in (value.left, value.right)):
                header = 'both of the following hold'
            if self.word_markers:
                return (f'{header}: first clause: {left}; end first clause; '
                        f'second clause: {right}; end second clause')
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
            body = self.formula(value.edge.formula, (dst, src, *scope), depth)
            return (prefix + f'steps, where a step from {_article(srcnoun)} {srcnoun} to '
                    + f'{_article(dstnoun)} {dstnoun} satisfies this condition: ' + body)
        raise TypeError('Unknown checked formula')

    def render(self, formula):
        self.maximum = _max_scope(formula)
        text = self.formula(formula)
        return text[0].upper() + text[1:]


def render_english(value, env, *, conclusions=(), **options):
    if type(value) is ast.Document:
        ast.check_document(env, value)
    else:
        ast.check_formula(env, value)
    words = EnglishVocabulary(env, **options)
    if words.review_status == 'unreviewed':
        warnings.warn('English overlay ' + words.overlay_digest + ': unreviewed',
                      UnreviewedVocabularyWarning, stacklevel=2)
    formulas = value.formulas if type(value) is ast.Document else (value,)
    conclusions = tuple(conclusions)
    if (type(value) is not ast.Document and conclusions
            or len(set(conclusions)) != len(conclusions)
            or any(type(i) is not int or not 0 <= i < len(formulas) for i in conclusions)):
        raise ValueError('Conclusion indices must identify distinct document statements')
    marked = set(conclusions)
    sentences = []
    for index, formula in enumerate(formulas):
        for settings in ({}, {'avoid_negative_universal': True},
                         {'avoid_negative_universal': True, 'word_markers': True}):
            sentence = EnglishTraversal(env, words, **settings).render(formula)
            try:
                if _parse_english_document(env, sentence + '.', **options)[0] == ast.Document((formula,)):
                    if index in marked:
                        proper_name = any(
                            name in words.declared_constants and display[0].isupper()
                            and sentence.startswith(display)
                            and (len(sentence) == len(display) or
                                 not re.match(r'[A-Za-z0-9_]', sentence[len(display)]))
                            for name, display in words.constants.items() if display)
                        sentence = 'Therefore ' + (sentence if proper_name else sentence[0].lower() + sentence[1:])
                    sentences.append(sentence)
                    break
            except VEError:
                continue
        else:
            raise ValueError('No writable English form passed the one-reading check')
    text = (''.join(sentence + '.\n' for sentence in sentences)
            if type(value) is ast.Document else sentences[0])
    if len(text.encode('utf-8')) + (0 if type(value) is ast.Document else 2) > MAX_SOURCE_BYTES:
        raise ResourceLimit(f'Rendered ve_english text exceeds its {MAX_SOURCE_BYTES}-byte limit')
    if type(value) is ast.Document:
        if len(text) > MAX_NODES:
            raise ResourceLimit(f'Rendered ve_english text exceeds the derivation budget MAX_NODES ({MAX_NODES})')
        parsed, _, _, parsed_conclusions = _parse_english_document(env, text, **options)
        if parsed != value or parsed_conclusions != tuple(sorted(marked)):
            raise ValueError('Rendered ve_english document has a different reading')
    return text


@dataclass(frozen=True)
class EnglishParseResult:
    document: ast.Document
    original: str
    english_text: str
    canonical_text: str
    overlay_digest: str | None
    review_status: str
    conclusions: tuple[int, ...] = ()

    def paraphrase(self):
        return {'overlay_digest': self.overlay_digest, 'review_status': self.review_status,
                'input_text': self.original, 'english_text': self.english_text,
                'canonical_text': self.canonical_text,
                'changed': self.original != self.english_text}


def _content_pattern(text):
    # Quoted fallback symbols retain exact identity; only display words fold case.
    return ''.join(_literal_pattern(p) if p.startswith('"') else '(?i:' + _literal_pattern(p) + ')'
                   for p in re.split(r'("(?:[^"\\]|\\.)*")', text) if p)


def _literal_pattern(text):
    return r'\s+'.join(re.escape(part) for part in text.split(' '))


class EnglishParser:
    def __init__(self, env, source, words=None):
        self.env, self.source, self.i = env, source, 0
        self.words = words or EnglishVocabulary(env)
        self.nodes = 0
        self.extension_readings = []
        self.conclusions = []
        self.referents = set()
        self.incomplete_discourse = False
        self.sentence_spans = []
        self.paragraph_breaks = []
        self.farthest = 0

    def _span(self, start, end):
        return Span(start, end, self.source.count('\n', 0, start) + 1,
                    start - self.source.rfind('\n', 0, start))

    def error(self, message, cls=SyntaxError):
        pos = max(self.i, self.farthest)
        raise cls(message, span=self._span(pos, min(pos + 1, len(self.source))))

    def take(self, text, *, content=False):
        match = re.compile(_content_pattern(text) if content else _literal_pattern(text)).match(self.source, self.i)
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
            candidates.append((noun, (sort, 'that ' + noun)))
            candidates.extend((ordinal + ' ' + noun, (sort, 'the ' + ordinal + ' ' + noun))
                              for ordinal in _ORDINALS)
            # Names are bound in lexical scope; the paraphrase shows canonical numbering.
            prefix = noun + ' named '
            match = re.compile(_content_pattern(prefix) + '(' + re.escape(self.words.letters[sort]) + r'[1-9][0-9]*)').match(self.source, self.i)
            if match:
                candidates.append((match.group(), (sort, match[1])))
        for text, binding in sorted(candidates, key=lambda item: -len(item[0])):
            start = self.i
            if self.take(text, content=True):
                if any(ref == binding[1] for _, ref in scope):
                    self.error('This name is already in scope. Use first and second, or distinct numbered names.')
                return binding
            self.i = start
        self.error('Expected a declared sort noun, optionally first, second, or a numbered name.')

    def term_options(self, scope):
        terms = {ref: ast.Var(index) for index, (_, ref) in reversed(list(enumerate(scope)))}
        terms.update({text: ast.Const(name) for name, text in self.words.constants.items()})
        terms.update({text[0].upper() + text[1:]: ast.Const(name)
                      for name, text in self.words.constants.items()
                      if text.startswith('the ')})
        terms.update({'the ' + text: ast.Const(name) for name, text in self.words.constants.items()
                      if re.fullmatch('[a-z]+', text)})
        terms.update({text: ast.Const(name) for name, text in self.words.natural_constants().items()})
        # Without a scoped discourse model, only a sentence-initial pronoun
        # can inherit the preceding sentence's sole explicit referent.
        if (len(self.referents) == 1 and not scope and not self.incomplete_discourse
                and self.i == self.sentence_formula_start):
            terms['it'] = ast.Const(next(iter(self.referents)))
        return terms

    def reference_pattern(self, ref, scope):
        scoped = {name for _, name in scope if name.startswith(('that ', 'the '))}
        return _content_pattern(ref) if ref in scoped else _literal_pattern(ref)

    def atom(self, scope, relative=False, object_allowed=False):
        start = self.i
        order = getattr(self.env, 'order', False)
        terms = self.term_options(scope)
        if order:
            # Integer constants fill only integer slots; objects only object slots.
            terms = {ref: value for ref, value in terms.items()
                     if not (type(value) is ast.Const and self.env.constants[value.name].sort == ast.INT_SORT)}
        term_literal = lambda t: self.reference_pattern(t, scope)
        term_pattern = '(?:' + '|'.join(term_literal(t) for t in sorted(terms, key=lambda t: -len(t))) + ')'
        if not terms:
            term_pattern = r'(?!)'
        int_pattern = self.int_pattern() if order else None
        if order and getattr(self, '_masked_for', None) is not self.source:
            self._masked_for, self._masked = self.source, _mask_brackets(self.source)
        subject = self._masked if order else self.source

        if not relative and 'data@0' in self.env.profiles and self.source.startswith('the ', start):
            for name, declaration in sorted(self.env.predicates.items(), key=lambda item: -len(item[0])):
                if len(declaration.arguments) != 2:
                    continue
                pattern = (r'the ' + re.escape(name) + r' of (' + term_pattern +
                           r') is (' + term_pattern + r')(?![A-Za-z0-9_])')
                match = re.compile(pattern).match(self.source, start)
                if match is not None:
                    if not (declaration.functional and declaration.total):
                        self.error('The ' + name + ' of a term requires functional and total declarations.')
                    arguments = [next(value for ref, value in terms.items()
                                      if re.fullmatch(term_literal(ref), term))
                                 for term in match.groups()]
                    self.i = match.end()
                    self.farthest = max(self.farthest, self.i)
                    return ast.Binary(name, *arguments)
                for property_name, prop in self.env.predicates.items():
                    if prop.arguments != (declaration.arguments[1],):
                        continue
                    property_pattern = (r'the ' + re.escape(name) + r' of (' + term_pattern +
                                        r') is ' + re.escape(property_name) + r'(?![A-Za-z0-9_])')
                    property_match = re.compile(property_pattern).match(self.source, start)
                    if property_match is None:
                        continue
                    if not (declaration.functional and declaration.total):
                        self.error('The ' + name + ' of a term requires functional and total declarations.')
                    if declaration.arguments[1] == '$string':
                        self.error('String-valued attribute properties require data stage 2.')
                    source = next(value for ref, value in terms.items()
                                  if re.fullmatch(term_literal(ref), property_match[1]))
                    lifted = ast.Var(source.index + 1) if type(source) is ast.Var else source
                    self.i = property_match.end()
                    self.farthest = max(self.farthest, self.i)
                    return ast.Exists(declaration.arguments[1], ast.And(
                        ast.Binary(name, lifted, ast.Var(0)), ast.Unary(property_name, ast.Var(0))))

        def slots(name, omitted):
            """Per-placeholder patterns: integer slots take bracketed integer terms."""
            if name is None or not order:
                return None
            if type(name) is tuple:
                return (int_pattern, int_pattern)
            sorts = self.env.predicates[name].arguments
            if (omitted == 'subject' and sorts[0] == ast.INT_SORT) or (
                    omitted == 'object' and sorts[-1] == ast.INT_SORT):
                return False
            return tuple(int_pattern if sort == ast.INT_SORT else term_pattern for sort in sorts)
        choices = []
        if not relative:
            for text, node in [('this holds in all cases', ast.Top()), ('this is impossible', ast.Bottom())]:
                if self.take(text): choices.append((self.i, node))
                self.i = start
        templates = []
        for name, template in self.words.predicates.items():
            templates.append((name, template, False))
        templates += [(name, template, True) for name, template in self.words.negatives.items()]
        if not relative:
            templates.append((None, '{0} is the same as {1}', False))
            if order:
                templates.append((('eq', ast.Eq, False), '{0} is the same as {1}', False))
                templates += [(('cmp', kind, swap), text, False) for text, kind, swap in _COMPARISONS]
        alternatives = [(name, template, negative, 'subject' if relative else None)
                        for name, template, negative in templates]
        if relative and object_allowed:
            alternatives += [(name, template, negative, 'object') for name, template, negative in templates
                             if type(name) is str and len(self.env.predicates[name].arguments) == 2]
        for name, template, negative, omitted in alternatives:
            if omitted == 'subject':
                template = template.removeprefix('{0} ')
            elif omitted == 'object':
                template = template.replace(' {1}', '')
            slot = slots(name, omitted)
            if slot is False:
                continue
            parts = re.split(r'(\{[0-5]\})', template)
            pattern = ''.join(('(' + (term_pattern if slot is None else slot[int(part[1])]) + ')')
                              if re.fullmatch(r'\{[0-5]\}', part) else _content_pattern(part) for part in parts)
            match = re.compile(pattern).match(subject, start)
            if not match:
                continue
            end = match.end()
            if end < len(self.source) and re.match(r'[A-Za-z0-9_]', self.source[end]):
                continue
            # term_options is built at the start of the atom. An initial "it"
            # must not leak into a later argument slot of the same atom.
            if any(match.group(g) == 'it' and match.start(g) != self.sentence_formula_start
                   for g in range(1, len(match.groups()) + 1)):
                continue
            groups = [self.source[a:b] for a, b in (match.span(g) for g in range(1, len(match.groups()) + 1))]
            if slot not in (None, False):
                offset = 1 if omitted == 'subject' else 0
                if not all(self.int_syntax(t) for i, t in enumerate(groups)
                           if slot[i + offset] is int_pattern):
                    continue
            # Whitespace in a term can be edited; its binding is lexical, not textual.
            if slot is None:
                args = [next(value for ref, value in terms.items() if re.fullmatch(term_literal(ref), t))
                        for t in groups]
            else:
                offset = 1 if omitted == 'subject' else 0
                args = [self.int_term(t) if slot[i + offset] is int_pattern else
                        next(value for ref, value in terms.items() if re.fullmatch(term_literal(ref), t))
                        for i, t in enumerate(groups)]
            if omitted == 'subject': args.insert(0, ast.Var(0))
            elif omitted == 'object': args.append(ast.Var(0))
            if type(name) is tuple:
                node = (name[1](args[1], args[0]) if name[2] else name[1](*args))
            elif name is None:
                node = ast.Eq(*args)
            else:
                node = (ast.Unary(name, args[0]) if len(args) == 1 else
                        ast.Binary(name, *args) if len(args) == 2 else ast.Atom(name, tuple(args)))
                if negative: node = ast.Not(node)
            choices.append((end, node))
        if not choices:
            return self.unknown_atom(scope, relative, object_allowed)
        # The lexicon is prefix-free at clause boundaries. Retain an explicit
        # ambiguity guard rather than silently selecting a competing template.
        longest = max(end for end, _ in choices)
        nodes = {node for end, node in choices if end == longest}
        if len(nodes) != 1:
            self.error('The vocabulary gives this clause more than one meaning. Use distinct predicate templates.')
        tail = re.match(r'\s+([A-Za-z][A-Za-z0-9_-]*)', self.source[longest:])
        clause_heads = {t.split()[1].lower() for t in (*self.words.predicates.values(), *self.words.negatives.values())}
        if tail and tail[1].lower() not in BOUNDARIES | clause_heads:
            names = {n.predicate for _, n in choices if type(n) in (ast.Unary, ast.Binary)}
            names |= {n.body.predicate for _, n in choices if type(n) is ast.Not}
            if names:
                existing = '; '.join(f'{n!r}: {self.words.predicates[n]!r}' for n in sorted(names))
                end = phrase_end(self.source, longest)
                self.error(f'Phrase {self.source[start:end]!r} extends existing wording {existing}; '
                           'declare distinct wording by hand.')
        self.i = longest
        self.farthest = max(self.farthest, longest)
        return nodes.pop()

    def int_constants(self):
        return {text: name for name, text in self.words.constants.items()
                if self.env.constants[name].sort == ast.INT_SORT}

    def int_leaf(self):
        constants = sorted(self.int_constants(), key=lambda t: -len(t))
        twice = [name for name in constants if re.fullmatch('[a-z]+', name)]
        return r'(?:-?(?:0|[1-9][0-9]*)(?![0-9])' + ''.join(
            '|' + _literal_pattern(t) + (r'(?![A-Za-z0-9_])' if t[-1:].isalnum() or t[-1:] == '_' else '')
            for t in constants) + ''.join('|twice\\s+the\\s+' + re.escape(t) + r'(?![A-Za-z0-9_])'
                                            for t in twice) + ')'

    def int_pattern(self):
        """An integer term over the bracket-masked source: a leaf or one masked bracket group."""
        return '-*(?:' + self.int_leaf() + r'|\[' + _INT_MASK + r'*\])'

    def int_syntax(self, text):
        """The exact integer-term shape (any depth) that the frozen grammar admits."""
        leaf = re.compile(self.int_leaf())
        position = 0

        def term(depth):
            # depth is the AST term depth int_term will build (Scale(-1, t) per
            # prefix minus, Add(t, Scale(-1, u)) for [t - u]), bounded as in the checker.
            nonlocal position
            while text.startswith('-', position) and not text[position + 1:position + 2].isdigit():
                position += 1
                depth += 1
            if depth > MAX_DEPTH:
                self.error(f'Arithmetic term exceeds {MAX_DEPTH} nesting levels.', ResourceLimit)
            match = leaf.match(text, position)
            if match:
                position = match.end()
                return True
            if not text.startswith('[', position):
                return False
            position += 1
            if not term(depth + 1):
                return False
            operator = text[position:position + 3]
            if operator not in (' + ', ' - ', ' * '):
                return False
            position += 3
            if not term(depth + (2 if operator == ' - ' else 1)) or not text.startswith(']', position):
                return False
            position += 1
            return True
        return term(1) and position == len(text)

    def int_term(self, text):
        """Parse an integer term with the canonical (frozen) term grammar."""
        constants = self.int_constants()
        position = 0

        def term():
            nonlocal position
            if text.startswith('twice the ', position):
                position += len('twice the ')
                for display, name in sorted(constants.items(), key=lambda item: -len(item[0])):
                    if re.fullmatch('[a-z]+', display) and text.startswith(display, position):
                        end = position + len(display)
                        if end == len(text) or not re.match(r'[A-Za-z0-9_]', text[end]):
                            position = end
                            return ast.Scale(2, ast.Const(name))
            if text.startswith('-', position) and not text[position + 1:position + 2].isdigit():
                position += 1
                return ast.Scale(-1, term())
            match = re.compile(r'-?(?:0|[1-9][0-9]*)(?![0-9])').match(text, position)
            if match:
                position = match.end()
                return ast.Num(int(match.group()))
            if text.startswith('[', position):
                position += 1
                left = term()
                operator = text[position:position + 3]
                position += 3
                right = term()
                if not text.startswith(']', position) or operator not in (' + ', ' - ', ' * '):
                    self.error('Expected an integer term such as [n + 1].')
                position += 1
                if operator == ' * ':
                    if type(left) is not ast.Num:
                        self.error('A scaling coefficient must be an integer numeral.')
                    return ast.Scale(left.value, right)
                return ast.Add(left, ast.Scale(-1, right) if operator == ' - ' else right)
            for display in sorted(constants, key=lambda t: -len(t)):
                match = re.compile(_literal_pattern(display)).match(text, position)
                if match:
                    position = match.end()
                    return ast.Const(constants[display])
            self.error('Expected an integer term.')
        value = term()
        if position != len(text):
            self.error('Unexpected text in an integer term.')
        return value

    def unknown_atom(self, scope, relative=False, object_allowed=False):
        start = self.i
        # Remove a recognized subject from the diagnostic, but never invent one.
        if not relative:
            for ref in sorted(self.term_options(scope), key=len, reverse=True):
                match = re.compile(self.reference_pattern(ref, scope) + r'\s+').match(self.source, start)
                if match:
                    start = match.end()
                    break
        head = re.compile(r'is\s+(?:not\s+)?(?:a\s+|an\s+)?').match(self.source, start)
        content = head.end() if head else start
        end = phrase_end(self.source, content)
        end = min(len(self.source), max(end, content, start + 1))
        phrase = self.source[start:end]
        matches = nearest(phrase, self.words)[:3]
        suggestions = '; '.join(repr(row['wording']) for row in matches)
        raise SyntaxError(f'Unknown English phrase {phrase!r}. Nearest declared wordings: {suggestions}.',
                          span=self._span(start, end))

    def term(self, scope):
        for text, value in sorted(self.term_options(scope).items(), key=lambda item: -len(item[0])):
            if self.take(text, content=any(ref == text and ref.startswith(('that ', 'the '))
                                           for _, ref in scope)): return value
        self.error('Expected a constant name or a definite reference to an entity already introduced.')

    def guard(self, scope):
        def relative():
            # In an object relative, "that person" is the subject reference;
            # only consume a repeated relative pronoun outside such a term.
            term_prefix = any(re.compile(self.reference_pattern(ref, scope) + r'(?![A-Za-z0-9_])').match(self.source, self.i)
                              for ref in self.term_options(scope))
            if not term_prefix:
                self.take('who ') or self.take('that ')
            return self.atom(scope, relative=True, object_allowed=True)
        first = self.atom(scope, relative=True, object_allowed=True)
        if self.take(', and '):
            second = relative(); self.need(' and ')
            return ast.And(first, ast.And(second, relative()))
        if self.take(' and '):
            second = relative()
            if self.take(', and '):
                return ast.And(ast.And(first, second), relative())
            return ast.And(first, second)
        return first

    def alternatives_guard(self, scope):
        """Expand the three profile guard phrases to ordinary quantified FOL."""
        from .wire import loads_json
        block = loads_json(self.env.alternatives)
        noun = self.words.sorts[block['action']]
        forms = ((f'every other {noun} available to ', 'other'),
                 (f'every {noun} available to ', 'every'),
                 (f'another {noun} available to ', 'another'))
        mode = next((kind for prefix, kind in forms if self.take(prefix)), None)
        if mode is None:
            return None
        outer_action = next((index for index, (sort, _) in enumerate(scope)
                             if sort == block['action']), None)
        if mode != 'every' and outer_action is None:
            self.error('Another action needs a rule on an action as its reference.')
        chooser_ref = 'that ' + self.words.sorts[block['chooser']]
        if (self.source[self.i:].startswith(chooser_ref)
                and chooser_ref not in self.term_options(scope)):
            self.error('The chooser has no antecedent; write there is a ' +
                       self.words.sorts[block['chooser']] + ' such that that action is available '
                       'to that ' + self.words.sorts[block['chooser']] + ' and …')
        owner = self.term(scope)
        self.space()
        inner = ((block['action'], 'that other ' + noun if mode != 'every' else 'that ' + noun), *scope)

        def verb_atom():
            reference = inner[0][1]
            if self.source[self.i:].startswith(reference + ' '):
                return self.atom(inner)
            return self.atom(inner, relative=True)

        def verb_phrase():
            if self.take('either '):
                left = verb_atom()
                self.need(' or ')
                right = verb_atom()
                self.take(', or both')
                return ast.Or(left, right)
            if self.take('both '):
                left = verb_atom()
                self.need(' and ')
                return ast.And(left, verb_atom())
            return verb_atom()

        body = verb_phrase()
        lifted_owner = ast.Var(owner.index + 1) if type(owner) is ast.Var else owner
        available = ast.Binary(block['available'], ast.Var(0), lifted_owner)
        if mode != 'every':
            available = ast.And(available, ast.Not(ast.Eq(ast.Var(0), ast.Var(outer_action + 1))))
        self.farthest = max(self.farthest, self.i)
        return (ast.Exists(block['action'], ast.And(available, body)) if mode == 'another'
                else ast.Forall(block['action'], ast.Implies(available, body)))

    def formula(self, scope=(), depth=0, nesting=1):
        if nesting > MAX_DEPTH:
            self.error(f'This statement exceeds the {MAX_DEPTH}-level nesting limit.', ResourceLimit)
        self.nodes += 1
        if self.nodes > MAX_NODES:
            self.error(f'This document exceeds the {MAX_NODES}-node limit.', ResourceLimit)
        remainder = self.source[self.i:].lower()
        if not scope and remainder.startswith('it ') and not remainder.startswith('it is not the case that '):
            if 'it' not in self.term_options(scope):
                self.error('The referent of it is incomplete. Repeat the explicit name or confirm a scoped rewrite.')
        if not scope and re.match(r'(?:they|them|their|her|him|his)\b', remainder):
            word = remainder.split(maxsplit=1)[0]
            if word not in self.term_options(scope):
                self.error('Plural or possessive reference needs an explicit-name or scoped-referent confirmation.')
        if getattr(self.env, 'alternatives', None) is not None:
            alternative = self.alternatives_guard(scope)
            if alternative is not None:
                return alternative
        matched = surface_registry.dispatch(self.source[self.i:], self.env)
        if matched is not None and matched[1].parser_hook is not None:
            start = self.i
            result = matched[1].parser_hook(self, scope, depth, nesting)
            if result is not None:
                self.extension_readings.append((matched[1], result, start, self.i))
                return result
            self.i = start
        def child(inner=scope, listed=False):
            return self.formula(inner, depth + int(listed), nesting + 1)
        if self.take('it is not the case that '):
            return ast.Not(child())
        listing_types = {"and": ast.And, "or": ast.Or, "implies": ast.Implies}
        for prefix, record in surface_registry.KEYWORDS:
            if prefix not in ('all of the following hold:', 'both of the following hold:',
                              'at least one of the following holds:', 'if the following holds:'):
                continue
            cls = listing_types[record.wire_tag]
            if self.take(prefix):
                self.space()
                if self.take('first clause: '):
                    left = child(listed=True)
                    self.need('; end first clause; second clause: ')
                    right = child(listed=True)
                    self.need('; end second clause')
                    return cls(left, right)
                a, b = _markers(depth)
                self.need(a + ' ')
                left = child(listed=True)
                self.need(';'); self.space()
                if cls is ast.Implies:
                    self.need('then the following holds:'); self.space()
                self.need(b + ' ')
                return cls(left, child(listed=True))
        compact = {'both ': (ast.And, ' and ', ''), 'either ': (ast.Or, ' or ', ', or both'),
                   'if ': (ast.Implies, ', then ', '')}
        for prefix, _record in surface_registry.KEYWORDS:
            if prefix not in compact:
                continue
            cls, between, suffix = compact[prefix]
            if self.take(prefix):
                left = child() if cls is ast.Implies else self.atom(scope)
                self.need(between)
                right = child() if cls is ast.Implies else self.atom(scope)
                if suffix: self.need(suffix)
                return cls(left, right)
        if self.take('for every '):
            binding = self.declaration(scope)
            inner = (binding, *scope)
            guard = None
            if self.take(' that ') or self.take(' who '): guard = self.guard(inner)
            self.need(', ')
            body = child(inner)
            return ast.Forall(binding[0], ast.Implies(guard, body) if guard is not None else body)
        if self.take('every '):
            binding = self.declaration(scope)
            inner = (binding, *scope)
            guard = None
            if self.take(' that ') or self.take(' who '): guard = self.guard(inner)
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
            listed = not self.take(' satisfies this condition: ')
            if listed:
                self.need(' satisfies the following:'); self.space(); self.need('(a) ')
            return ast.Reach(kind, ast.Body(src[0], child((dst, src, *scope), listed=listed)), left, right)
        return self.coordination(scope) or self.atom(scope)

    def natural_clause(self):
        start = self.i
        if self.take('some '):
            binding = self.declaration(())
            self.space()
            first = self.atom((binding,), relative=True)
            if self.take(' and '):
                second = None
                if (type(first) is ast.Unary and first.term == ast.Var(0)
                        and self.words.predicates[first.predicate].startswith('{0} is ')):
                    start_second = self.i
                    matches = []
                    for name, template in self.words.predicates.items():
                        if (self.env.predicates[name].arguments == (binding[0],)
                                and template.startswith('{0} is ')):
                            adjective = template[len('{0} is '):]
                            if re.fullmatch('[a-z]+', adjective) and self.take(adjective, content=True):
                                matches.append((self.i, ast.Unary(name, ast.Var(0))))
                            self.i = start_second
                    if len(matches) == 1:
                        self.i, second = matches[0]
                first = ast.And(first, second if second is not None else self.atom((binding,), relative=True))
            return ast.Exists(binding[0], first)
        self.i = start
        if self.take('no '):
            binding = self.declaration(())
            self.space()
            return ast.Not(ast.Exists(binding[0], self.atom((binding,), relative=True)))
        self.i = start
        if not self.take('every '):
            return None
        subject_start = self.i
        try:
            binding = self.declaration(())
            self.space()
            owner = self.owner_clause(binding)
            if owner is not None:
                return ast.Forall(binding[0], owner)
        except VEError:
            pass
        self.i = subject_start
        for guard_name, template in self.words.predicates.items():
            decl = self.env.predicates[guard_name]
            if (len(decl.arguments) != 1 or decl.arguments[0] not in self.words.sorts
                    or not template.startswith('{0} is ')):
                continue
            adjective = template[len('{0} is '):]
            if not re.fullmatch('[a-z]+', adjective):
                continue
            noun = self.words.sorts[decl.arguments[0]]
            self.i = start + len('every ')
            if not self.take(adjective + ' ' + noun, content=True):
                continue
            self.space()
            binding = (decl.arguments[0], 'that ' + noun)
            guard = ast.Unary(guard_name, ast.Var(0))
            owner = self.owner_clause(binding)
            if owner is not None:
                return ast.Forall(binding[0], ast.Implies(guard, owner))
            body = self.atom((binding,), relative=True)
            if type(body) is ast.Not:
                self.error('Use an explicit for every clause for negation.')
            if self.take(' and '):
                owner = self.owner_clause(binding)
                if owner is None:
                    self.error('Expected a uniquely declared ownership clause.')
                body = ast.And(body, owner)
            return ast.Forall(binding[0], ast.Implies(guard, body))
        self.i = start
        return None

    def owner_clause(self, binding):
        """Finite inverse of `{0} owns {1}`; no inferred converse relation."""
        start = self.i
        matches = []
        for name, template in self.words.predicates.items():
            declaration = self.env.predicates[name]
            if (name != 'owns' or template != '{0} owns {1}'
                    or len(declaration.arguments) != 2 or declaration.arguments[1] != binding[0]):
                continue
            noun = self.words.sorts[declaration.arguments[0]]
            article = _article('owner')
            if self.take('has ' + article + ' owner'):
                matches.append((self.i, ast.Exists(declaration.arguments[0],
                                                  ast.Binary(name, ast.Var(0), ast.Var(1)))))
            self.i = start
        if len(matches) == 1:
            self.i = matches[0][0]
            return matches[0][1]
        return None

    def coordination(self, scope):
        """Parse a distributive three-item list with fixed right association."""
        if scope:
            return None
        names = {text: name for name, text in self.words.constants.items()
                 if re.fullmatch(r'(?:the )?[A-Za-z]+(?: [A-Za-z]+)*', text)}
        names.update({text[0].upper() + text[1:]: name for text, name in tuple(names.items())
                      if text.startswith('the ')})
        adjectives = {template[len('{0} is '):]: name for name, template in self.words.predicates.items()
                      if len(self.env.predicates[name].arguments) == 1
                      and template.startswith('{0} is ')
                      and re.fullmatch('[a-z]+', template[len('{0} is '):])}
        if not names or not adjectives:
            return None
        term = '(?:' + '|'.join(re.escape(t) for t in sorted(names, key=len, reverse=True)) + ')'
        adj = '(?:' + '|'.join(re.escape(t) for t in sorted(adjectives, key=len, reverse=True)) + ')'
        subject = re.compile(f'({term}),\\s+({term})\\s+(and|or)\\s+({term})\\s+(are|is)\\s+({adj})\\b',
                             re.I).match(self.source, self.i)
        if subject:
            a, b, join, c, verb, adjective = subject.groups()
            symbols = (names.get(a), names.get(b), names.get(c))
            predicate = adjectives.get(adjective.lower())
            if (all(symbols) and len(set(symbols)) == 3 and predicate
                    and verb.lower() == ('are' if join.lower() == 'and' else 'is')
                    and all(self.env.constants[n].sort == self.env.predicates[predicate].arguments[0]
                            for n in symbols)):
                self.i = subject.end()
                atoms = [ast.Unary(predicate, ast.Const(n)) for n in symbols]
                cls = ast.And if join.lower() == 'and' else ast.Or
                return cls(atoms[0], cls(atoms[1], atoms[2]))
        predicates = re.compile(f'({term})\\s+is\\s+({adj}),\\s+({adj})\\s+(and|or)\\s+({adj})\\b',
                                re.I).match(self.source, self.i)
        if predicates:
            name, a, b, join, c = predicates.groups()
            symbol = names.get(name)
            symbols = tuple(adjectives.get(x.lower()) for x in (a, b, c))
            if (symbol and all(symbols) and len(set(symbols)) == 3
                    and all(self.env.constants[symbol].sort == self.env.predicates[p].arguments[0]
                            for p in symbols)):
                self.i = predicates.end()
                atoms = [ast.Unary(p, ast.Const(symbol)) for p in symbols]
                cls = ast.And if join.lower() == 'and' else ast.Or
                return cls(atoms[0], cls(atoms[1], atoms[2]))
        return None

    def document(self):
        formulas = []
        while self.i < len(self.source):
            start = self.i
            if any(self.take(marker) for marker in _CONCLUSION_MARKERS):
                self.conclusions.append(len(formulas))
            self.sentence_formula_start = self.i
            formulas.append(self.formula())
            self.referents.update(_mentioned_constants(formulas[-1]))
            self.incomplete_discourse |= _has_discourse_binder(formulas[-1])
            self.need('.')
            self.sentence_spans.append((start, self.i))
            if self.i < len(self.source):
                gap_start = self.i
                self.space()
                if self.i < len(self.source) and re.search(r'\n\s*\n', self.source[gap_start:self.i]):
                    self.paragraph_breaks.append(len(formulas))
        if not formulas: self.error('Write at least one statement ending with a period.')
        return ast.Document(tuple(formulas))


def _parse_english_document(env, source, *, _with_structure=False, **options):
    if isinstance(source, bytes):
        try: source = source.decode('utf-8')
        except UnicodeDecodeError as exc:
            raise SyntaxError('English input must be UTF-8.', span=Span(exc.start, exc.end, 1, exc.start + 1)) from exc
    if not isinstance(source, str): raise TypeError('source must be str or bytes')
    if len(source.encode('utf-8')) > MAX_SOURCE_BYTES:
        raise ResourceLimit(f'English source exceeds {MAX_SOURCE_BYTES} bytes')
    words = EnglishVocabulary(env, **options)
    normalised, boundaries = _normalise_english_source(source, words)
    parser = EnglishParser(env, normalised, words)
    try:
        document = parser.document()
    except VEError as exc:
        if exc.span is not None:
            start = boundaries[exc.span.start]
            end = boundaries[exc.span.end]
            exc.span = Span(start, end, source.count('\n', 0, start) + 1,
                            start - source.rfind('\n', 0, start))
        raise
    from .surface.unambiguity import require_unique_derivation
    tree = require_unique_derivation(env, normalised, **options)
    from .surface.unambiguity import require_correspondence
    require_correspondence(tree, parser.extension_readings, env, parser.words, parser.source)
    try:
        ast.check_document(env, document)
    except VEError as exc:
        if exc.span is None: exc.span = Span(0, len(source), 1, 1)
        raise
    _check_conclusions(env, document, parser.conclusions)
    result = document, source, parser.words, tuple(parser.conclusions)
    if _with_structure:
        spans = tuple((boundaries[start], boundaries[end]) for start, end in parser.sentence_spans)
        breaks = tuple(index for index in range(1, len(spans))
                       if re.search(r'\n\s*\n', source[spans[index - 1][1]:spans[index][0]]))
        return (*result, spans, breaks)
    return result


def _check_conclusions(env, document, conclusions):
    """A marker uses every earlier unmarked premise in this document."""
    if not conclusions:
        return
    from .entailment import prove_entailment
    marked = set(conclusions)
    for index in conclusions:
        premises = tuple(formula for i, formula in enumerate(document.formulas[:index])
                         if i not in marked)
        if not premises:
            raise SyntaxError('A conclusion needs an earlier premise.')
        result = prove_entailment(env, premises, document.formulas[index])
        if result.status != 'Found':
            raise SyntaxError('The marked conclusion has no checked derivation from earlier premises: '
                              + result.status)


def parse_english_with_metadata(env, source, **options):
    document, source, words, conclusions = _parse_english_document(env, source, **options)
    try:
        english = render_english(document, env, **options)
        if conclusions:
            english = source
        if english != source and _parse_english_document(env, english, **options)[0] != document:
            english = source
    except (VEError, ValueError):
        # The input passed the complete audit. Never display an unchecked rewrite.
        english = source
    from .printer import print_document
    return EnglishParseResult(document, source, english, print_document(env, document),
                              **words.provenance, conclusions=conclusions)


def parse_english(env, source, **options):
    return _parse_english_document(env, source, **options)[0]


def parse_english_argument(env, source, **options):
    """Build checked claim-graph edges for marked conclusions.

    Every unmarked sentence is an asserted premise. An edge references all
    earlier unmarked premises in the document, including earlier paragraphs.
    Marked conclusions never become assumptions or premises of later edges.
    """
    from .argument import ArgumentGraph, Claim, Deduction, check_argument, deduction_identity
    from .entailment import prove_entailment
    from .printer import print_formula
    document, _, _, conclusions = _parse_english_document(env, source, **options)
    marked = set(conclusions)
    claims = tuple(Claim.create(env, f's{i + 1}', print_formula(env, formula) + '.\n',
                                candidate_ast=formula)
                   for i, formula in enumerate(document.formulas))
    edges = tuple(Deduction(f'd{i + 1}', tuple(f's{j + 1}' for j in range(i) if j not in marked),
                            f's{i + 1}') for i in conclusions)
    graph = ArgumentGraph(env, claims, edges, claims[-1].name)
    checked_edges = []
    for i, edge in zip(conclusions, edges):
        premises = tuple(document.formulas[j] for j in range(i) if j not in marked)
        proof = prove_entailment(env, premises, document.formulas[i])
        if proof.status != 'Found':
            raise SyntaxError('The marked conclusion has no checked derivation from earlier premises.')
        checked_edges.append(Deduction(edge.name, edge.premises, edge.conclusion,
                                       ({'edge_id': deduction_identity(graph, edge),
                                         'direction': 'follows', 'proof': proof.certificate},)))
    graph = ArgumentGraph(env, claims, tuple(checked_edges), claims[-1].name)
    result = check_argument(graph, search=False)
    if any('follows' not in result.findings.get(edge.name, ()) for edge in checked_edges):
        raise SyntaxError('The marked conclusion certificate did not replay in the claim graph.')
    return graph


def english_legend(env, style='json', **options):
    words = EnglishVocabulary(env, **options)
    record = {
        'format': 've.english-legend@1', 'environment_id': env.environment_id,
        **words.provenance,
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
    for category in ('sorts', 'predicates'):
        for name, entry in words.overlay[category].items():
            record[category][name]['suggested'] = entry['suggested']
            record[category][name]['review_status'] = words.review_status
            record[category][name]['overlay_verbalisation'] = entry['verbalisation']
    if style == 'json': return json.dumps(record, ensure_ascii=False, sort_keys=True, indent=2) + '\n'
    lines = [f"English vocabulary: {record['format']}; environment: {env.environment_id}",
             f"Display overlay digest: {words.overlay_digest or 'none'}; review status: {words.review_status}",
             record['reference_rule'], record['constant_rule'], record['closure_rule'],
             'Numbered letters: ' + ', '.join(f'{s} = {l}' for s, l in sorted(words.letters.items()))]
    for name, entry in record['sorts'].items(): lines.append(f'Sort {name}: {json.dumps(entry, ensure_ascii=False)}')
    for name, entry in record['predicates'].items(): lines.append(f'Predicate {name}: {json.dumps(entry, ensure_ascii=False)}')
    for name, entry in record['constants'].items(): lines.append(f'Constant {name}: {json.dumps(entry, ensure_ascii=False)}')
    lines.extend(f'Lint {i.path}: {i.code}' for i in words.issues)
    return '\n'.join(lines) + '\n'


def english_lark_grammar(env, **options):
    """Independent context-free syntax envelope for all-derivations auditing.

    Scope, sorts, article choice, indentation and canonical contraction selection
    are checked separately. Removing those constraints can only add derivations;
    a unique parse here therefore also has at most one well-typed derivation.
    Literal templates are expanded as productions, never hidden in a catch-all
    atom token or a prioritized lexer.
    """
    words = EnglishVocabulary(env, **options)
    lit = lambda s: json.dumps(s)
    constant_lit = lambda s: ('/' + _literal_pattern(s).replace('/', r'\/') + '/'
                              if ' ' in s and not s.startswith('"') else lit(s))
    # Each regex is one declared literal phrase with editable whitespace, never
    # an open atom token. Keep quoted symbols exact and avoid word-level lexer
    # proliferation in the all-derivations audit.
    content_lit = lambda s: ' '.join(lit(p) if p.startswith('"') else
                                    '/' + _literal_pattern(p.strip()).replace('/', r'\/') + '/i'
                                    for p in re.split(r'("(?:[^"\\]|\\.)*")', s) if p.strip())
    rules = [
        'start: (sentence ".")+',
        'sentence: formula | conclusion_marker formula',
        'conclusion_marker: "therefore" | "so" | "hence" | "it follows that"',
        '?formula: atom | negation | compact | listing | universal | existential | reach | coordination',
        'coordination: term "," term "and" term "are" adjective -> subject_and\n'
        '            | term "," term "or" term "is" adjective -> subject_or\n'
        '            | term "is" adjective "," adjective "and" adjective -> predicate_and\n'
        '            | term "is" adjective "," adjective "or" adjective -> predicate_or',
        'negation: "it is not the case that" formula',
        'compact: "both" atom "and" atom -> conjunction\n'
        '       | "either" atom "or" atom ", or both" -> disjunction\n'
        '       | "if" formula ", then" formula -> implication',
        'listing: "all of the following hold:" "first clause:" formula "; end first clause; second clause:" formula "; end second clause" -> conjunction_list\n'
        '       | "both of the following hold:" "first clause:" formula "; end first clause; second clause:" formula "; end second clause" -> conjunction_list\n'
        '       | "at least one of the following holds:" "first clause:" formula "; end first clause; second clause:" formula "; end second clause" -> disjunction_list\n'
        '       | "if the following holds:" "first clause:" formula "; end first clause; second clause:" formula "; end second clause" -> implication_list\n'
        '       | "all of the following hold:" marker formula ";" marker formula -> conjunction_list\n'
        '       | "both of the following hold:" marker formula ";" marker formula -> conjunction_list\n'
        '       | "at least one of the following holds:" marker formula ";" marker formula -> disjunction_list\n'
        '       | "if the following holds:" marker formula ";" "then the following holds:" marker formula -> implication_list',
        'guard: guard_atom | guard_atom "and" guard_relative | guard_atom "and" guard_relative ", and" guard_relative | guard_atom ", and" guard_relative "and" guard_relative',
        'guard_relative: guard_atom | "who" guard_atom | "that" guard_atom',
        'guard_atom: relative | object_relative',
        'relative_pronoun: \"who\" | \"that\"',
        'marker: "(a)" | "(b)" | "(i)" | "(ii)"',
        'universal: "for every" declaration "," formula -> universal_global\n'
        '         | "for every" declaration relative_pronoun guard "," formula -> universal_guard\n'
        '         | "every" declaration relative -> universal_relative\n'
        '         | "every" declaration relative_pronoun guard relative -> universal_guard_relative',
        'existential: "there is" article declaration "such that" formula -> existential_global\n'
        '           | "there is" article declaration "who" relative -> existential_relative\n'
        '           | "there is" article declaration "that" relative -> existential_relative',
        'article: "a" | "an"',
        'declaration: noun | ' + ' | '.join(lit(word) + 'i noun' for word in _ORDINALS) + ' | noun "named"i LABEL',
        'term: constant | "it" | "that"i noun | ' + ' | '.join(lit('the ' + word) + 'i noun' for word in _ORDINALS) + ' | LABEL',
        'reach: "starting from" term "," term "is reachable by" count "or more" relation "steps" -> named_reach\n'
        '     | "starting from" term "," term "is reachable by" count "or more steps, where a step from" article declaration "to" article declaration "satisfies the following:" "(a)" formula -> body_reach',
        '     | "starting from" term "," term "is reachable by" count "or more steps, where a step from" article declaration "to" article declaration "satisfies this condition:" formula -> body_reach',
        'count: "one" | "zero"',
        'noun: ' + (' | '.join(content_lit(n) for n in words.sorts.values()) or 'IMPOSSIBLE'),
        ('LABEL: /(?:' + '|'.join(re.escape(l) for l in words.letters.values()) + ')[1-9][0-9]*/'
         if words.letters else 'LABEL: /[^\\s\\S]/'),
    ]
    if getattr(env, 'alternatives', None) is not None:
        from .wire import loads_json
        block = loads_json(env.alternatives)
        action_noun = content_lit(words.sorts[block['action']])
        rules += [
            '%extend formula: alt_available_guard',
            '%extend term: ' + content_lit('that other ' + words.sorts[block['action']]),
            'alt_available_guard: "every" ' + action_noun + ' "available" "to" term alt_verb_phrase'
            ' | "every" "other" ' + action_noun + ' "available" "to" term alt_verb_phrase'
            ' | "another" ' + action_noun + ' "available" "to" term alt_verb_phrase',
            'alt_verb_phrase: relative | atom | "either" alt_verb_atom "or" alt_verb_atom'
            ' | "either" alt_verb_atom "or" alt_verb_atom ", or both"'
            ' | "both" alt_verb_atom "and" alt_verb_atom',
            'alt_verb_atom: relative | atom',
        ]
    order = getattr(env, 'order', False)
    is_int = lambda name: order and env.constants[name].sort == ast.INT_SORT
    constants = [constant_lit(v) for n, v in words.constants.items() if not is_int(n)]
    constants += [constant_lit(v[0].upper() + v[1:]) for n, v in words.constants.items()
                  if not is_int(n) and v.startswith('the ')]
    constants += [constant_lit('the ' + v) for n, v in words.constants.items()
                  if not is_int(n) and re.fullmatch('[a-z]+', v)]
    constants += [lit(v) for n, v in words.natural_constants().items() if not is_int(n)]
    # An impossible terminal keeps grammars valid for empty vocabularies.
    rules.append('constant: ' + (' | '.join(constants) or 'IMPOSSIBLE'))
    relations = [lit(quote(n)) for n, p in env.predicates.items()
                 if len(p.arguments) == 2 and p.arguments[0] == p.arguments[1]]
    rules.append('relation: ' + (' | '.join(relations) or 'IMPOSSIBLE'))
    atoms = ['"this holds in all cases"', '"this is impossible"', 'term "is the same as"i term']
    if 'data@0' in env.profiles:
        atoms.extend('"the" ' + lit(name) + ' "of" term "is" term'
                     for name, declaration in env.predicates.items()
                     if len(declaration.arguments) == 2 and declaration.functional and declaration.total)
        atoms.extend('"the" ' + lit(name) + ' "of" term "is" ' + lit(property_name)
                     for name, declaration in env.predicates.items()
                     if len(declaration.arguments) == 2 and declaration.functional and declaration.total
                     and declaration.arguments[1] != '$string'
                     for property_name, prop in env.predicates.items()
                     if prop.arguments == (declaration.arguments[1],))
    relatives = []
    object_relatives = []
    for templates in (words.predicates, words.negatives):
        for name, template in templates.items():
            sorts = env.predicates[name].arguments
            slot = lambda p: ('int_term' if order and sorts[int(p[1])] == ast.INT_SORT else 'term')
            parts = re.split(r'(\{[0-5]\})', template)
            rule = ' '.join(slot(p) if re.fullmatch(r'\{[0-5]\}', p) else content_lit(p.strip())
                            for p in parts if p.strip())
            atoms.append(rule)
            if slot('{0}') == 'term':
                relatives.append(rule.removeprefix('term '))
            if len(env.predicates[name].arguments) == 2 and slot('{1}') == 'term':
                object_template = template.replace(' {1}', '')
                object_relatives.append(' '.join(slot(p) if p == '{0}' else content_lit(p.strip())
                                                for p in re.split(r'(\{0\})', object_template) if p.strip()))
    if order:
        # Comparisons only; integer terms use the frozen bracketed spelling.
        atoms += ['int_term "is the same as"i int_term'] + [
            'int_term ' + content_lit(text.removeprefix('{0} ').removesuffix(' {1}')) + ' int_term'
            for text, _, _ in _COMPARISONS]
        ints = [constant_lit(v) for n, v in words.constants.items() if is_int(n)]
        rules += ['int_term: int_atom | "-" int_neg',
                  'int_atom: int_constant | NUMERAL | "[" int_term INT_OP int_term "]" | "twice" "the" int_plain_constant',
                  'int_neg: int_constant | "[" int_term INT_OP int_term "]" | "-" int_neg',
                  'int_constant: ' + (' | '.join(ints) or 'IMPOSSIBLE'),
                  'int_plain_constant: ' + (' | '.join(lit(v) for n, v in words.constants.items()
                                                     if is_int(n) and re.fullmatch('[a-z]+', v)) or 'IMPOSSIBLE'),
                  'NUMERAL: /-?(?:0|[1-9][0-9]*)(?![0-9])/',
                  'INT_OP: "+" | "-" | "*"']
    rules.append('atom: ' + ' | '.join(atoms))
    rules.append('relative: ' + (' | '.join(relatives) or 'IMPOSSIBLE'))
    rules.append('object_relative: ' + (' | '.join(object_relatives) or 'IMPOSSIBLE'))
    adjectives = sorted({template[len('{0} is '):] for name, template in words.predicates.items()
                         if len(env.predicates[name].arguments) == 1
                         and template.startswith('{0} is ')
                         and re.fullmatch('[a-z]+', template[len('{0} is '):])})
    rules.append('adjective: ' + (' | '.join(lit(a) + 'i' for a in adjectives) or 'IMPOSSIBLE'))
    for record in surface_registry.records():
        if record.grammar_hook is None or not surface_registry.enabled(record, env):
            continue
        extension = list(record.grammar_hook(env, words))
        if record.parser_hook is not None:
            production = record.grammar_production
            if (not re.fullmatch(r"[a-z][a-z0-9_]*", production) or
                    f"%extend formula: {production}" not in extension or
                    not any(line.startswith(production + ":") for line in extension)):
                raise SyntaxError(f"English grammar hook for {record.wire_tag} must extend formula via {production}")
        rules.extend(extension)
    rules.extend(['IMPOSSIBLE: /[^\\s\\S]/', '%import common.WS', '%ignore WS'])
    return '\n'.join(rules) + '\n'


def _natural_parser(parser, scope, _depth, _nesting):
    if scope:
        return None
    return parser.natural_clause()


def _natural_grammar(env, words):
    lit = lambda s: json.dumps(s)
    content_lit = lambda s: '/' + _literal_pattern(s).replace('/', r'\/') + '/i'
    modifiers = []
    copulas = []
    adjectives = []
    for name, template in words.predicates.items():
        decl = env.predicates[name]
        if (len(decl.arguments) == 1 and decl.arguments[0] in words.sorts
                and template.startswith('{0} is ')
                and re.fullmatch('[a-z]+', template[len('{0} is '):])):
            modifiers.append(content_lit(template[len('{0} is '):]) + ' '
                             + content_lit(words.sorts[decl.arguments[0]]))
            copulas.append(content_lit('is ' + template[len('{0} is '):]))
            adjectives.append(content_lit(template[len('{0} is '):]))
    owners = any(name == 'owns' and template == '{0} owns {1}'
                 and len(env.predicates[name].arguments) == 2
                 for name, template in words.predicates.items())
    return ('%extend formula: natural',
            'natural: natural_some | natural_no | natural_every',
            'natural_some: "some" declaration some_tail',
            'some_tail: relative | relative "and" relative | copula_relative "and" copula_adjective',
            'copula_relative: ' + (' | '.join(dict.fromkeys(copulas)) or 'IMPOSSIBLE'),
            'copula_adjective: ' + (' | '.join(dict.fromkeys(adjectives)) or 'IMPOSSIBLE'),
            'natural_no: "no" declaration relative',
            'natural_every: "every" natural_subject natural_tail | "every" declaration owner_clause',
            'natural_tail: relative | owner_clause | relative "and" owner_clause',
            'natural_subject: ' + (' | '.join(dict.fromkeys(modifiers)) or 'IMPOSSIBLE'),
            'owner_clause: ' + ('"has an owner"' if owners else 'IMPOSSIBLE'))


def _natural_derivation(tree, env, words, source):
    fragment = source[tree.meta.start_pos:tree.meta.end_pos]
    parser = EnglishParser(env, fragment, words)
    value = parser.natural_clause()
    if value is None or parser.i != len(fragment):
        raise SyntaxError('Natural registry derivation disagrees with its source span')
    return value


surface_registry.register(surface_registry.SurfaceRecord(
    'natural_clause', '', ('some ', 'no ', 'every '), '', 'natural',
    parser_hook=_natural_parser, grammar_hook=_natural_grammar,
    derivation_hook=_natural_derivation))
