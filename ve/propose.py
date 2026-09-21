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
from .english import EnglishParser, EnglishVocabulary, _literal_pattern, parse_english_with_metadata
from .english_phrases import distance, lexical, nearest, phrase_end, unary_phrase
from .errors import ResourceLimit, Span, SyntaxError, VEError
from .limits import MAX_SOURCE_BYTES
from .wire import canonical_json


class _ProposalParser(EnglishParser):
    def __init__(self, env, source, vocabulary):
        self.overlay = deepcopy(vocabulary) if vocabulary is not None else {
            'format': 've.english-vocabulary@1', 'environment_id': env.environment_id,
            'sorts': {}, 'predicates': {}}
        super().__init__(env, source, EnglishVocabulary(env, vocabulary=self.overlay,
                                                     accept_suggested_vocabulary=True))
        self.introduced = []

    def unknown_atom(self, scope, relative=False, object_allowed=False):
        start = self.i
        term = ast.Var(0) if relative and scope else None
        if not relative:
            for ref, value in sorted(self.term_options(scope).items(), key=lambda row: -len(row[0])):
                match = re.compile(_literal_pattern(ref) + r'\s+').match(self.source, start)
                if match:
                    term, start = value, match.end()
                    break
        # A binder supplies the sort. Unknown constants and constant-subject
        # proposals have no binder noun and are deliberately out of scope.
        if type(term) is not ast.Var:
            return super().unknown_atom(scope, relative, object_allowed)
        head = re.compile(r'is\s+(not\s+)?').match(self.source, start)
        if not head:
            return super().unknown_atom(scope, relative, object_allowed)
        end = phrase_end(self.source, head.end())
        complement = ' '.join(self.source[head.end():end].split())
        template = '{0} is ' + complement
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
                    raise SyntaxError('A declared reference (or its typo) cannot be inferred as a unary predicate.',
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
        description = f'Machine-proposed, unreviewed unary predicate: {phrase}. No meaning beyond this declared symbol is inferred.'
        neighbors = nearest(phrase, self.words)
        if any(row['kind'] == 'constant' and row['near_duplicate'] for row in neighbors):
            raise SyntaxError('A near-duplicate of a declared constant cannot become a unary predicate.',
                              span=self._span(start, end))
        self.introduced.append({'symbol': name, 'source_span': asdict(self._span(start, end)),
                                'source_text': self.source[start:end], 'signature': [sort],
                                'description': description, 'verbalisation': template,
                                'nearest_existing': neighbors[:3],
                                'near_duplicates': [r['symbol'] for r in neighbors if r['near_duplicate']],
                                'review_status': 'unreviewed'})
        data = self.env.to_dict()
        data['vocabulary']['predicates'][name] = {'arguments': [sort], 'description': description}
        self.env = Environment(data)
        self.overlay['environment_id'] = self.env.environment_id
        self.overlay['predicates'][name] = {'verbalisation': template,
                                          'negative_verbalisation': template.replace(' is ', ' is not ', 1),
                                          'suggested': True}
        self.words = EnglishVocabulary(self.env, vocabulary=self.overlay, accept_suggested_vocabulary=True)
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
    parser = _ProposalParser(env, source, vocabulary)
    document = parser.document()
    ast.check_document(parser.env, document)
    if not parser.introduced:
        raise VEError('No new unary predicate to propose; use parse --surface english.')
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
    return {'format': 've.vocabulary-proposal@1', 'status': 'blocked' if missing else 'proposed',
            'review_status': 'unreviewed', 'source': source,
            'base_environment': env.to_dict(), 'base_overlay': vocabulary,
            'acknowledged': sorted(acknowledgements), 'requires_acknowledgement': missing,
            'introduced': parser.introduced, 'paraphrase': parsed.paraphrase(),
            'candidate_environment': candidate('environment', parser.env.to_dict()),
            'candidate_overlay': candidate('english-vocabulary', parser.overlay)}


def write_proposal(preview, output):
    if preview['status'] != 'proposed':
        raise VEError('Near-duplicates require --acknowledge SYMBOL before candidate files can be written.')
    _write_new_directory(output, {'proposal.json': preview,
                                 'environment.proposed.json': preview['candidate_environment'],
                                 'environment.english.proposed.json': preview['candidate_overlay']})


def adopt(preview, output):
    """Rebuild the preview, including its acknowledgements, before adoption."""
    canonical_json(preview)
    if type(preview) is not dict or preview.get('format') != 've.vocabulary-proposal@1':
        raise VEError('Expected a vocabulary proposal, not an environment.')
    try:
        rebuilt = propose(Environment(preview['base_environment']), preview['source'],
                          preview['base_overlay'], acknowledge=preview['acknowledged'])
    except (KeyError, TypeError) as exc:
        raise VEError('Malformed vocabulary proposal.') from exc
    if rebuilt != preview or rebuilt['status'] != 'proposed':
        raise VEError('Proposal changed or lacks near-duplicate acknowledgements; generate it again.')
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
