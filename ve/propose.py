"""Untrusted authoring proposals. Only adoption writes loadable environments.

The proposal wire envelope deliberately fails Environment's existing schema;
no proposal status is added to identities, checking, proofs, or certificates.
"""
from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path
import re

from . import ast
from .environment import Environment, RESERVED, valid_identifier
from .english import EnglishParser, EnglishVocabulary, parse_english_with_metadata
from .english_phrases import distance, lexical, nearest, phrase_end, unary_phrase, wording_key, BLOCKED, PREPOSITIONS
from .errors import ResourceLimit, Span, SyntaxError, VEError
from .limits import MAX_SOURCE_BYTES
from .lexicon import TOKEN as LEXICON_TOKEN, classify, describe
from .wire import canonical_json, digest


class _ProposalParser(EnglishParser):
    def __init__(self, env, source, vocabulary):
        self.overlay = deepcopy(vocabulary) if vocabulary is not None else {
            'format': 've.english-vocabulary@1', 'environment_id': env.environment_id,
            'sorts': {}, 'predicates': {}}
        super().__init__(env, source, EnglishVocabulary(env, vocabulary=self.overlay,
                                                     accept_suggested_vocabulary=True))
        self.introduced = []
        declared = [*env.sorts, *env.predicates, *env.constants,
                    *self.words.sorts.values(), *self.words.predicates.values(),
                    *self.words.negatives.values(), *self.words.constants.values()]
        for decl in env.sorts.values():
            if decl.verbalisation:
                declared.extend((decl.verbalisation.singular, decl.verbalisation.plural))
        declared.extend(decl.verbalisation for decl in env.predicates.values() if decl.verbalisation)
        self.declared_tokens = {token.casefold() for text in declared
                                for token in LEXICON_TOKEN.findall(text)}
        self.declared_tokens.update(part for token in tuple(self.declared_tokens) for part in token.split('_'))

    def unknown_atom(self, scope, relative=False, object_allowed=False):
        start = self.i
        term = ast.Var(0) if relative and scope else None
        if not relative:
            for ref, value in sorted(self.term_options(scope).items(), key=lambda row: -len(row[0])):
                match = re.compile(self.reference_pattern(ref, scope) + r'\s+').match(self.source, start)
                if match:
                    term, start = value, match.end()
                    break
        # A binder supplies the sort. Unknown constants and constant-subject
        # proposals have no binder noun and are deliberately out of scope.
        if type(term) is not ast.Var:
            return super().unknown_atom(scope, relative, object_allowed)
        head = re.compile(r'is\s+(not\s+)?', re.I).match(self.source, start)
        if not head:
            return super().unknown_atom(scope, relative, object_allowed)
        end = phrase_end(self.source, head.end())
        complement = ' '.join(self.source[head.end():end].split())
        template = '{0} is ' + complement
        # Reject equivalence before inventing a suffixed symbol, including
        # spellings whose hyphens differ from the stored display wording.
        for symbol, wording in self.words.predicates.items():
            if wording_key(template) == wording_key(wording):
                raise SyntaxError(f'Phrase {template!r} is existing wording {wording!r} for {symbol!r}.',
                                  span=self._span(start, end))
        tokens = re.findall(r'[A-Za-z][A-Za-z0-9_]*', complement)
        normalized_content = wording_key(complement)
        nouns = set(self.env.sorts) | set(self.words.sorts.values())
        for decl in self.words.env.sorts.values():
            if decl.verbalisation:
                nouns.update((decl.verbalisation.singular, decl.verbalisation.plural))
        for reference in sorted({*self.env.constants, *self.words.constants.values(), *nouns}):
            if re.search(r'(?<![a-z0-9_])' + re.escape(wording_key(reference)) + r'(?![a-z0-9_])', normalized_content, re.I):
                raise SyntaxError(f'Phrase {complement!r} contains declared constant or sort noun {reference!r}; '
                                  'a relation must be declared by hand.', span=self._span(start, end))
        if (set(re.findall(r'[a-z0-9_]+', complement.lower())) & BLOCKED
                or re.search(r'\b(?:un|non)-', complement, re.I)
                # A bare prepositional object is relational regardless of case.
                # Keep the existing opaque article-led phrases (of the guild).
                or any(t.casefold() in PREPOSITIONS and tokens[i + 1].casefold() not in {'a', 'an', 'the'}
                       for i, t in enumerate(tokens[:-1]))):
            raise SyntaxError(f'Phrase {complement!r} contains blocked relational or negative content; '
                              'a relation must be declared by hand, and negation must use is not.',
                              span=self._span(start, end))
        phrase = unary_phrase(template)
        if phrase is None:
            return super().unknown_atom(scope, relative, object_allowed)
        # A closed reference inside this slot is not part of a new unary word.
        # Also catch misspelled constants, rather than absorbing them as words.
        for ref in self.term_options(scope):
            ref_words = re.findall(r'[a-z0-9_]+', ref.lower())
            tokens = re.findall(r'[a-z0-9_]+', phrase.lower())
            for i in range(len(tokens) - len(ref_words) + 1):
                fragment = ' '.join(tokens[i:i + len(ref_words)])
                reference = ' '.join(ref_words)
                near = (min(len(fragment), len(reference)) >= 2
                        and abs(len(fragment) - len(reference)) <= 1
                        and distance(fragment, reference) <= (1 if min(len(fragment), len(reference)) <= 2 else 2))
                if fragment == reference or near:
                    raise SyntaxError('A declared reference (or its typo) cannot be inferred as a unary predicate; a relation must be declared by hand.',
                                      span=self._span(start, end))
        # A known binary frame with an unknown/misspelled object or wording
        # must remain an error. No flag can turn it into a unary declaration.
        for name, decl in self.env.predicates.items():
            if len(decl.arguments) != 2:
                continue
            for wording in (self.words.predicates[name], self.words.negatives.get(name, ''), decl.verbalisation or ''):
                frame = lexical(wording.split('{1}')[0].removeprefix('{0} '))
                tokens = lexical(complement).split()
                n = len(frame.split())
                if frame and len(tokens) >= n and distance(' '.join(tokens[:n]), frame) <= 2:
                    raise SyntaxError(f'Possible binary wording for {name!r}; binary predicates and constants are not inferred.',
                                      span=self._span(start, end))
        name = re.sub(r'[^a-z0-9]+', '_', phrase.lower()).strip('_')[:64]
        if not valid_identifier(name) or name in RESERVED or re.fullmatch(r'x[0-9]+', name):
            name = ('predicate_' + name)[:64]
        taken = {*self.env.sorts, *self.env.predicates, *self.env.constants}
        root, suffix = name, 2
        while name in taken:
            tail = '_' + str(suffix)
            name = root[:64 - len(tail)] + tail
            suffix += 1
        sort = scope[term.index][0]
        evidence = classify(phrase, self.declared_tokens)
        description = (describe(evidence) + f'. Unreviewed unary predicate: {phrase}. '
                       'No meaning beyond this declared symbol is inferred.')
        neighbors = nearest(phrase, self.words)
        if any(row['kind'] == 'constant' and row['near_duplicate'] for row in neighbors):
            raise SyntaxError('A near-duplicate of a declared constant cannot become a unary predicate.',
                              span=self._span(start, end))
        self.introduced.append({'symbol': name, 'source_span': asdict(self._span(start, end)),
                                'source_text': self.source[start:end], 'signature': [sort],
                                'description': description, 'verbalisation': template,
                                'lexicon': evidence,
                                'nearest_existing': [r for i, r in enumerate(neighbors) if i < 3 or r['near_duplicate']],
                                'near_duplicates': [r['symbol'] for r in neighbors if r['near_duplicate']],
                                'review_status': 'unreviewed'})
        data = self.env.to_dict()
        data['vocabulary']['predicates'][name] = {'arguments': [sort], 'description': description}
        self.env = Environment(data)
        self.overlay['environment_id'] = self.env.environment_id
        self.overlay['predicates'][name] = {'verbalisation': template,
                                          'negative_verbalisation': template.replace(' is ', ' is not ', 1),
                                          'suggested': True}
        previous_words = self.words
        try:
            self.words = EnglishVocabulary(self.env, vocabulary=self.overlay, accept_suggested_vocabulary=True)
        except VEError as exc:
            # Adding a lexical owner can invalidate an older template. Attribute
            # that collision to both wordings, rather than blaming the old entry.
            affected = [f'{n!r}: {w!r}' for n, w in previous_words.predicates.items()
                        if f'predicates/{n}' in str(exc)]
            detail = '; existing wording ' + '; '.join(affected) if affected else ''
            raise VEError(f'Proposed phrase {template!r} ({name!r}) fails the template linter{detail}: {exc}') from exc
        self.i = end
        self.farthest = max(self.farthest, end)
        node = ast.Unary(name, term)
        return ast.Not(node) if head[1] else node

    def _span(self, start, end):
        return Span(start, end, self.source.count('\n', 0, start) + 1,
                    start - self.source.rfind('\n', 0, start))


def propose(env, source, vocabulary=None, *, acknowledge=()):
    """Return a preview/envelope, never a usable Environment or a verdict."""
    if isinstance(source, bytes):
        source = source.decode('utf-8')
    if len(source.encode('utf-8')) > MAX_SOURCE_BYTES:
        raise ResourceLimit(f'English source exceeds {MAX_SOURCE_BYTES} bytes')
    # Materialize an absent overlay so proposal files stay within the existing
    # null-free JSON wire envelope and work through the CLI loader too.
    if vocabulary is None:
        vocabulary = {'format': 've.english-vocabulary@1', 'environment_id': env.environment_id,
                      'sorts': {}, 'predicates': {}}
    parser = _ProposalParser(env, source, vocabulary)
    document = parser.document()
    ast.check_document(parser.env, document)
    if not parser.introduced:
        names = ', '.join(sorted(env.predicates))
        raise VEError('No new unary predicate to propose; wording resolves to existing vocabulary (' + names + '); use parse --surface english.')
    for category in ('sorts', 'predicates'):
        for entry in parser.overlay[category].values():
            entry['suggested'] = True
    # Reparse the whole text using ONLY the resulting finite lexicon. This
    # catches segmentation changes or interactions with previously used words.
    parsed = parse_english_with_metadata(parser.env, source, vocabulary=parser.overlay,
                                         accept_suggested_vocabulary=True)
    if parsed.document != document:
        raise VEError('Proposed wordings change the sentence segmentation.')
    required = {n for row in parser.introduced for n in row['near_duplicates']}
    acknowledgements = set(acknowledge)
    if acknowledgements - required:
        raise VEError('Acknowledgement must name a flagged near-duplicate: ' + ', '.join(sorted(acknowledgements - required)))
    missing = sorted(required - acknowledgements)
    # Wrapping each candidate prevents accidental use through ANY existing
    # Environment loader, even if a candidate file is moved or renamed.
    def candidate(kind, value):
        return {'format': f've.proposed-{kind}@1', 'status': 'proposed',
                'review_status': 'unreviewed', 'candidate': value}
    preview = {'format': 've.vocabulary-proposal@1', 'status': 'blocked' if missing else 'proposed',
            'review_status': 'unreviewed', 'source': source,
            'base_environment': env.to_dict(), 'base_overlay': deepcopy(vocabulary),
            'source_digest': digest('ve-proposal-source-v1\n', source),
            'base_environment_digest': digest('ve-proposal-environment-v1\n', env.to_dict()),
            'base_overlay_digest': digest('ve-proposal-overlay-v1\n', vocabulary),
            'acknowledged': sorted(acknowledgements), 'requires_acknowledgement': missing,
            'introduced': parser.introduced, 'paraphrase': parsed.paraphrase(),
            'candidate_environment': candidate('environment', parser.env.to_dict()),
            'candidate_overlay': candidate('english-vocabulary', parser.overlay)}
    preview['proposal_digest'] = digest('ve-vocabulary-proposal-v1\n', preview)
    return preview


def write_proposal(preview, output):
    if preview['status'] != 'proposed':
        raise VEError('Near-duplicates require --acknowledge SYMBOL before candidate files can be written.')
    _write_new_directory(output, {'proposal.json': preview,
                                 'environment.proposed.json': preview['candidate_environment'],
                                 'environment.english.proposed.json': preview['candidate_overlay']})


def adopt(preview, output, *, acknowledge=()):
    """Verify and rebuild the preview; adoption requires fresh acknowledgements."""
    canonical_json(preview)
    if type(preview) is not dict or preview.get('format') != 've.vocabulary-proposal@1':
        raise VEError('Expected a vocabulary proposal, not an environment.')
    try:
        for key, domain in [('source', 'source'), ('base_environment', 'environment'), ('base_overlay', 'overlay')]:
            if preview[key + '_digest'] != digest(f've-proposal-{domain}-v1\n', preview[key]):
                raise VEError(f'Proposal {key} digest changed; generate it again.')
        payload = {k: v for k, v in preview.items() if k != 'proposal_digest'}
        if preview['proposal_digest'] != digest('ve-vocabulary-proposal-v1\n', payload):
            raise VEError('Proposal digest changed; generate it again.')
        rebuilt = propose(Environment(preview['base_environment']), preview['source'],
                          preview['base_overlay'], acknowledge=preview['acknowledged'])
    except (KeyError, TypeError) as exc:
        raise VEError('Malformed vocabulary proposal.') from exc
    if rebuilt != preview:
        raise VEError('Proposal changed or lacks near-duplicate acknowledgements; generate it again.')
    rebuilt = propose(Environment(preview['base_environment']), preview['source'],
                      preview['base_overlay'], acknowledge=acknowledge)
    if rebuilt['status'] != 'proposed':
        raise VEError('Adoption requires its own explicit --acknowledge flags; missing acknowledgements: '
                      + ', '.join(rebuilt['requires_acknowledgement']))
    data = rebuilt['candidate_environment']['candidate']
    overlay = rebuilt['candidate_overlay']['candidate']
    env = Environment(data)
    # Adoption is not a wording review. All outputs retain unreviewed status.
    from .english_vocabulary import overlay_provenance
    record = {'status': 'adopted', 'environment_id': env.environment_id,
              **overlay_provenance(overlay), 'introduced': rebuilt['introduced'],
              'acknowledged': rebuilt['acknowledged']}
    _write_new_directory(output, {'environment.json': data, 'environment.english.json': overlay,
                                 'adoption.json': record})
    return record


def _write_new_directory(output, files):
    # Refuse overwrites, including partial reuse of a previous output directory.
    encoded = {name: json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
               for name, value in files.items()}
    path = Path(output)
    path.mkdir(parents=True, exist_ok=False)
    for name, content in encoded.items():
        (path / name).write_text(content, encoding='utf-8')
