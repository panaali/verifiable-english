"""Durable, token-scoped writing desk over Z3's revisioned recovery ledger."""
from __future__ import annotations

from dataclasses import asdict
from copy import deepcopy
import hashlib
import json
import re
import secrets
import sqlite3
from pathlib import Path

from ve import Environment, VEError, meaning_id
from ve.assist.recovery import RecoveryService
from ve.assist.ambiguity_patterns import PATTERNS
from ve.english import parse_english_with_metadata
from ve.ast import Not
from ve.search import find_countermodel
from ve.surface.definitions import adopt as adopt_glossary
from ve.profiles import LANGUAGE as MODERN_LANGUAGE, SPEC_REVISION as MODERN_REVISION
from .examples import BY_ID

MAX_SOURCE = 6000
MAX_DOCUMENTS = 100
MAX_EVENTS = 300


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


class StaleDraft(ValueError):
    pass


class DraftStore:
    def __init__(self, state: Path, token: str):
        self.path = state / 'drafts.sqlite3'
        self.owner = digest(token)
        with self._db() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS drafts (
                id TEXT PRIMARY KEY, owner TEXT NOT NULL, example TEXT NOT NULL,
                environment TEXT NOT NULL, revision INTEGER NOT NULL,
                ledger TEXT NOT NULL, head TEXT NOT NULL)''')
            db.execute('''CREATE TABLE IF NOT EXISTS draft_events (
                draft TEXT NOT NULL, revision INTEGER NOT NULL, request_id TEXT NOT NULL,
                action TEXT NOT NULL, payload TEXT NOT NULL, previous TEXT NOT NULL,
                hash TEXT NOT NULL, PRIMARY KEY(draft, revision), UNIQUE(draft, request_id))''')
        self.path.chmod(0o600)

    def _db(self):
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        return db

    def _service(self, row):
        env = Environment(json.loads(row['environment']))
        ledger = json.loads(row['ledger'])
        return RecoveryService.from_ledger(env, ledger)

    def _read(self, db, draft_id):
        if not isinstance(draft_id, str) or not re.fullmatch(r'[A-Za-z0-9_-]{30,60}', draft_id):
            raise ValueError('Unknown document.')
        row = db.execute('SELECT * FROM drafts WHERE id=? AND owner=?', (draft_id, self.owner)).fetchone()
        if row is None:
            raise ValueError('Unknown document.')
        # The database is trusted storage, but detect damage and edited rows at every read.
        events = db.execute('SELECT * FROM draft_events WHERE draft=? ORDER BY revision', (draft_id,)).fetchall()
        previous = digest('ve-draft@1:' + draft_id + ':' + self.owner)
        for n, event in enumerate(events, 1):
            if event['revision'] != n or event['previous'] != previous:
                raise ValueError('Document history failed replay.')
            data = [draft_id, n, event['request_id'], event['action'], json.loads(event['payload']), previous]
            if digest(canonical(data)) != event['hash']:
                raise ValueError('Document history failed replay.')
            previous = event['hash']
        if row['revision'] != len(events) or row['head'] != previous:
            raise ValueError('Document history failed replay.')
        service = self._service(row)
        if events and json.loads(events[-1]['payload'])['ledger_hash'] != digest(row['ledger']):
            raise ValueError('Document ledger differs from history.')
        return row, service

    def _view(self, row, service):
        units = [asdict(unit) for unit in service.units.values()]
        for unit in units:
            if unit['state'] in {'needs_word', 'needs_repair', 'exhausted'}:
                reason = next((p.get('reason', '') for p in unit['pending'] if p.get('reason')), '')
                match = re.search(r"Unknown English phrase '([^']+)'", reason)
                registered = [*service.env.sorts, *service.env.predicates, *service.env.constants]
                unit['word_prompt'] = service.word_prompt(
                    term=match[1] if match else unit['source'].split()[0],
                    accepted_prefix='', expected=reason or 'A declared English sentence',
                    registered=registered)
            unit['cards'] = []
            for result in unit['catalogue_results'].values():
                for card in result.get('cards', []):
                    unit['cards'].append({**card, 'situation_text': self._situation(service.env, card['model'])})
            unit['suggestions'] = [e['text'] for e in service.events[-20:]
                                   if e['action'] == 'proposer_suggested' and e['unit'] == unit['id']]
        return {'id': row['id'], 'revision': row['revision'], 'example': row['example'],
                'environment': json.loads(row['environment']), 'units': units,
                'versions': service.versions, 'limits': service.limits,
                'history': [{'revision': e['revision'], 'action': e['action']}
                            for e in service.events[-20:]]}

    @staticmethod
    def _situation(env, model):
        lines = []
        for sort, entities in model['domains'].items():
            lines.append(f"This situation has {len(entities)} {sort.replace('_', ' ')}" +
                         ('' if len(entities) == 1 else 's') + '.')
        for predicate, rows in model['relations'].items():
            decl = env.predicates[predicate]
            template = decl.verbalisation
            for row in rows[:10]:
                labels = []
                for sort, entity in zip(decl.arguments, row):
                    labels.append(f"{sort.replace('_', ' ').capitalize()} " +
                                  str(model['domains'][sort].index(entity) + 1))
                lines.append((template.format(*labels) if template else
                              f"{' and '.join(labels)}: {decl.description}").rstrip('.') + '.')
        return lines

    def list(self):
        with self._db() as db:
            rows = db.execute('SELECT id FROM drafts WHERE owner=? ORDER BY rowid DESC LIMIT 20', (self.owner,)).fetchall()
            return [self.get(row['id']) for row in rows]

    def get(self, draft_id):
        with self._db() as db:
            row, service = self._read(db, draft_id)
            return self._view(row, service)

    def create(self, example='policy'):
        if example not in BY_ID:
            raise ValueError('Choose a known example vocabulary.')
        env_json = BY_ID[example]['environment']
        env = Environment(env_json)
        service = RecoveryService(env, grammar_version='ve.english@1',
                                  glossary_version=env.environment_id, reading_set_version='ve.readings@1')
        draft_id = secrets.token_urlsafe(24)
        ledger = canonical(service.to_ledger())
        genesis = digest('ve-draft@1:' + draft_id + ':' + self.owner)
        with self._db() as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT count(*) FROM drafts WHERE owner=?', (self.owner,)).fetchone()[0] >= MAX_DOCUMENTS:
                raise ValueError('Document limit reached.')
            db.execute('INSERT INTO drafts VALUES (?,?,?,?,?,?,?)',
                       (draft_id, self.owner, example, canonical(env_json), 0, ledger, genesis))
        return self.get(draft_id)

    def change(self, draft_id, expected, request_id, action, args):
        if type(expected) is not int or expected < 0:
            raise ValueError('A document revision is required.')
        if type(request_id) is not str or not re.fullmatch(r'[A-Za-z0-9_-]{8,100}', request_id):
            raise ValueError('Invalid request ID.')
        if type(args) is not dict or len(canonical(args)) > 20000:
            raise ValueError('Invalid document command.')
        with self._db() as db:
            db.execute('BEGIN IMMEDIATE')
            row, service = self._read(db, draft_id)
            prior = db.execute('SELECT revision FROM draft_events WHERE draft=? AND request_id=?',
                               (draft_id, request_id)).fetchone()
            if prior:
                return self._view(row, service)
            if expected != row['revision']:
                raise StaleDraft('This document changed in another tab. Reload its latest revision.')
            if expected >= MAX_EVENTS:
                raise ValueError('Document history limit reached.')
            env_json = json.loads(row['environment'])
            result = self._apply(service, action, args, env_json)
            if result is not None:
                service, env_json = result
            ledger = canonical(service.to_ledger())
            version = expected + 1
            payload = {'args': args, 'environment_hash': digest(canonical(env_json)),
                       'ledger_hash': digest(ledger)}
            history = [draft_id, version, request_id, action, payload, row['head']]
            head = digest(canonical(history))
            db.execute('INSERT INTO draft_events VALUES (?,?,?,?,?,?,?)',
                       (draft_id, version, request_id, action, canonical(payload), row['head'], head))
            db.execute('UPDATE drafts SET environment=?, revision=?, ledger=?, head=? WHERE id=? AND owner=?',
                       (canonical(env_json), version, ledger, head, draft_id, self.owner))
            fresh = db.execute('SELECT * FROM drafts WHERE id=?', (draft_id,)).fetchone()
            return self._view(fresh, service)

    def _apply(self, service, action, args, env_json):
        unit = service.units.get('main')
        if action == 'save':
            source = args.get('source')
            if type(source) is not str or not source.strip() or len(source) > MAX_SOURCE:
                raise ValueError('Enter up to 6000 characters of English.')
            if unit is None:
                service.add('main', source, {'start': 0, 'end': len(source)})
            else:
                service.edit('main', source=source, anchor={'start': 0, 'end': len(source)})
        elif action == 'analyze':
            self._needs_unit(unit)
            if unit.state not in {'draft', 'stale', 'unresolved', 'exhausted'}:
                service.cancel('main')
            service.start('main')
            source = unit.source.strip()
            try:
                parsed = parse_english_with_metadata(service.env, source + ('\n' if not source.endswith('\n') else ''))
                outcome = 'one' if len(parsed.document.formulas) == 1 else 'multiple'
            except (VEError, SyntaxError, ValueError) as exc:
                outcome = 'zero'
                error = str(exc)
            else:
                error = ''
            vocabulary = 'unknown' if 'Unknown English phrase' in error or 'declared' in error else 'known'
            reviewed_rewrite = any(
                source == candidate.get('wording')
                for event in service.events for result in event.get('unit_snapshot', {}).get('catalogue_results', {}).values()
                for candidate in result.get('candidates', []))
            dispositions = ({pattern.id: {'disposition': 'not_applicable', 'actor': 'workspace author',
                             'reason': 'Explicit checked paraphrase selected after reading review'}
                            for pattern in PATTERNS if pattern.matches(source)} if reviewed_rewrite else {})
            service.classify('main', parse_outcome=outcome, vocabulary=vocabulary,
                             pending=([{'reason': error[:300]}] if outcome == 'zero' and error else []),
                             catalogue_bindings=self._bindings(row_example=env_json, source=source),
                             catalogue_dispositions=dispositions)
        elif action == 'reply':
            self._needs_unit(unit)
            text = args.get('text')
            if type(text) is not str or not text.strip() or len(text) > MAX_SOURCE:
                raise ValueError('Enter a clarification or restatement.')
            service.reply('main', text, rejected=args.get('rejected', []))
            service.edit('main', source=text)
        elif action == 'cancel':
            self._needs_unit(unit)
            service.cancel('main')
        elif action == 'unresolved':
            self._needs_unit(unit)
            reason = args.get('reason')
            if type(reason) is not str or not reason.strip() or len(reason) > 500:
                raise ValueError('Enter a reason to keep this unit unresolved.')
            service.unresolved('main', reason)
        elif action == 'undo':
            self._needs_unit(unit)
            target = args.get('target_revision')
            if type(target) is not int:
                raise ValueError('Choose a unit revision to restore.')
            prior = next((event['unit_snapshot'] for event in service.events
                          if event['unit'] == 'main' and event['revision'] == target), None)
            if prior and prior['state'] == 'draft' and unit.state in {'unresolved', 'exhausted'}:
                service.cancel('main')
            service.undo('main', target)
        elif action == 'proposer_reserve':
            self._needs_unit(unit)
            service._command('request_proposer', unit_id='main', expected_revision=None)
        elif action == 'proposer_finish':
            self._needs_unit(unit)
            outcome = args.get('outcome')
            if type(outcome) is not dict or len(canonical(outcome)) > MAX_SOURCE + 100:
                raise ValueError('Invalid proposer outcome.')
            service._command('proposer_result', unit_id='main', reserved_revision=service.revision,
                             outcome=outcome)
        elif action == 'approve':
            self._needs_unit(unit)
            wording = args.get('wording')
            if type(wording) is not str or len(wording) > MAX_SOURCE:
                raise ValueError('Choose a checked English reading.')
            parsed = parse_english_with_metadata(service.env, wording.rstrip() + '\n')
            if len(parsed.document.formulas) != 1:
                raise ValueError('Approve one reading at a time.')
            formula = parsed.document.formulas[0]
            if unit.readings and meaning_id(service.env, formula) not in {r['meaning_id'] for r in unit.readings}:
                raise ValueError('Reading is outside the considered set.')
            search = find_countermodel(service.env, (), Not(formula), max_domain_size=2,
                                       max_models=10000, max_evaluations=1000000)
            if search.model is None:
                raise ValueError('No checked example situation was found within budget.')
            service.approve('main', formula, actor='workspace author', paraphrase=wording,
                            presentation=wording, situation=search.model.to_dict(),
                            rejected=args.get('rejected', []))
        elif action in {'define', 'glossary'}:
            self._needs_unit(unit)
            raw = deepcopy(env_json)
            if 'profile' in raw:
                raw['profiles'] = [raw.pop('profile')]
                raw['language'] = MODERN_LANGUAGE
                raw['spec_revision'] = MODERN_REVISION
            if action == 'glossary':
                sentence = args.get('sentence')
                if type(sentence) is not str or len(sentence) > 1000:
                    raise ValueError('Enter one glossary sentence.')
                new_json = adopt_glossary(raw, sentence)
            else:
                word, kind = args.get('word'), args.get('kind')
                if type(word) is not str or not re.fullmatch(r'[a-z][a-z-]{0,40}', word):
                    raise ValueError('Use one lower-case word for the new term.')
                if kind not in {'person', 'property', 'relation'}:
                    raise ValueError('Choose person, property, or relation.')
                vocabulary = raw['vocabulary']
                if word in vocabulary['sorts'] or word in vocabulary['predicates']:
                    raise ValueError('This term is already declared.')
                if kind == 'person':
                    vocabulary['sorts'][word] = {'description': args.get('description') or word}
                else:
                    sorts = args.get('sorts')
                    count = 1 if kind == 'property' else 2
                    if type(sorts) is not list or len(sorts) != count or any(s not in vocabulary['sorts'] for s in sorts):
                        raise ValueError('Choose declared kinds of things for the new word.')
                    vocabulary['predicates'][word] = {
                        'arguments': sorts, 'description': args.get('description') or word,
                        'verbalisation': ('{0} is ' + word if count == 1 else '{0} ' + word + ' {1}')}
                new_json = raw
            new_env = Environment(new_json)
            replacement = RecoveryService(new_env, grammar_version='ve.english@1',
                                          glossary_version=new_env.environment_id,
                                          reading_set_version='ve.readings@1')
            replacement.add('main', unit.source, unit.anchor, mode=unit.mode)
            return replacement, new_json
        else:
            raise ValueError('Unknown document action.')

    @staticmethod
    def _needs_unit(unit):
        if unit is None:
            raise ValueError('Write a sentence first.')

    @staticmethod
    def _bindings(row_example, source):
        # Only known, typed fixture bindings are offered. Other catalogue matches
        # remain pending until a reviewed binding is available.
        predicates = row_example['vocabulary']['predicates']
        sorts = row_example['vocabulary']['sorts']
        if ('engineer' in sorts and 'server' in sorts and 'checks_pair' in predicates
                and source.casefold().startswith('every engineer checks a server')):
            return {'scope.every_some@1': {'every_sort': 'engineer',
                     'some_sort': 'server', 'relation': 'checks_pair'}}
        return {}

    def export(self, draft_id):
        with self._db() as db:
            row, service = self._read(db, draft_id)
            return {'format': 've-web-draft@1', 'document': self._view(row, service),
                    'ledger': service.to_ledger(), 'head': row['head'],
                    'authorship': 'Unsigned copy; access to this export does not prove authorship.'}

    def import_copy(self, value):
        if type(value) is not dict or value.get('format') != 've-web-draft@1' or type(value.get('document')) is not dict:
            raise ValueError('Invalid document export.')
        source = value['document']
        example, env_json = source.get('example'), source.get('environment')
        if example not in BY_ID or type(env_json) is not dict or type(value.get('ledger')) is not dict:
            raise ValueError('Invalid document export.')
        env = Environment(env_json)
        service = RecoveryService.from_ledger(env, value['ledger'])
        if len(service.units) > 20 or any(len(u.source) > MAX_SOURCE for u in service.units.values()):
            raise ValueError('Document export exceeds limits.')
        draft_id = secrets.token_urlsafe(24)
        ledger = canonical(service.to_ledger())
        genesis = digest('ve-draft@1:' + draft_id + ':' + self.owner)
        payload = {'args': {'unsigned_import': True}, 'environment_hash': digest(canonical(env_json)),
                   'ledger_hash': digest(ledger)}
        request_id = secrets.token_urlsafe(16)
        head = digest(canonical([draft_id, 1, request_id, 'import', payload, genesis]))
        with self._db() as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT count(*) FROM drafts WHERE owner=?', (self.owner,)).fetchone()[0] >= MAX_DOCUMENTS:
                raise ValueError('Document limit reached.')
            db.execute('INSERT INTO drafts VALUES (?,?,?,?,?,?,?)',
                       (draft_id, self.owner, example, canonical(env_json), 1, ledger, head))
            db.execute('INSERT INTO draft_events VALUES (?,?,?,?,?,?,?)',
                       (draft_id, 1, request_id, 'import', canonical(payload), genesis, head))
        return self.get(draft_id)
