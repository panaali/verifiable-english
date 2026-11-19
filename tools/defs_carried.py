#!/usr/bin/env python3
"""Definitions carried, stage 1: report which source definitions a document's reader is never shown (report mode).

Design: manage-agents reviews/defs-carried-gate-1119/DESIGN.md r3, sections 1, 2 and 5 (stage 1 only: detection). The
tool reads a VE tree (a checkout, or a commit through git) and, per document, lists its rules and the terms each uses
(the per-format adapters of section 1), the surface each rule's reader is shown (section 2), and for every (rule, term,
source passage) pair a verdict:

    NOT CARRIED < FRAGMENT < PARTIAL < ELSEWHERE = UNSHOWN = OVERSIZE < CARRIED-ASSUMED < CARRIED

with the longest carried run (token-level longest common substring) as a diagnostic. The passages come from the
known-case fixture (tests/data/defs_carried/known_cases.json, built by tools/defs_carried_known.py) and from the marker
grep (detector b), linked to terms by the lexical matcher (detector c). Both detectors print their hits.

REPORT MODE. The exit code is 0 whatever the tool finds; only a usage error exits 2. Nothing here fails a build, a gate
or a merge, and there is no ledger, baseline or waiver (stage 2, not built). 0 model calls.

Usage:
  python3 tools/defs_carried.py [--root DIR | --ref COMMIT] [--doc NAME ...] [--known FILE | --no-known]
                                [--json OUT] [--summary-dir DIR] [--select PATH ...]
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
import time
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(1, str(Path(__file__).resolve().parents[1]))
import defs_carried_counter as counter  # noqa: E402  (the counter's own code, byte-pinned by a test)
from ve.errors import VEError  # noqa: E402
from ve.surface.softnorms import parse_header_options  # noqa: E402  (VE's rule-header grammar: one owner)

ROOT = Path(__file__).resolve().parents[1]
TOOL_VERSION = 'defs-carried-stage1-1'
KNOWN_DEFAULT = 'tests/data/defs_carried/known_cases.json'
ARG_LIMIT = counter.ARG_LIMIT
FRAGMENT_MIN = 4           # a carried run of at least this many tokens, short of the whole passage, is a FRAGMENT
RANK = {'NOT CARRIED': 0, 'FRAGMENT': 1, 'PARTIAL': 2, 'ELSEWHERE': 3, 'UNSHOWN': 3, 'OVERSIZE': 3,
        'CARRIED-ASSUMED': 4, 'CARRIED': 5}
PASSING = ('CARRIED', 'CARRIED-ASSUMED')
# Files whose change selects every document (section 7 "Selection"): the checker, the pinned counter code, the known cases.
SELECT_ALL = ('tools/defs_carried.py', 'tools/defs_carried_counter.py', KNOWN_DEFAULT)


# ----------------------------------------------------------------------------------------------------------- trees ---
class FsTree:
    """A VE checkout on disk."""

    def __init__(self, root):
        self.root = Path(root)
        self.key = f'fs:{self.root}'

    def read(self, path):
        p = self.root / path
        try:
            return p.read_text(encoding='utf-8').replace('\r\n', '\n')
        except (OSError, UnicodeDecodeError):
            return None

    def names(self, d):
        p = self.root / d
        return sorted(x.name for x in p.iterdir() if x.is_file()) if p.is_dir() else []

    def subdirs(self, d):
        p = self.root / d
        return sorted(x.name for x in p.iterdir() if x.is_dir()) if p.is_dir() else []

    def describe(self):
        return {'kind': 'checkout', 'root': str(self.root)}


class GitTree:
    """A VE commit, or a tree by its id (content-addressed), read with git (read-only)."""

    def __init__(self, repo, ref):
        self.repo = str(repo)
        out = subprocess.run(['git', '-C', self.repo, 'rev-parse', '--verify', f'{ref}^{{commit}}'],
                             capture_output=True, text=True)
        self.commit = out.stdout.strip() if out.returncode == 0 else None
        if self.commit is None:
            out = subprocess.run(['git', '-C', self.repo, 'rev-parse', '--verify', f'{ref}^{{tree}}'],
                                 capture_output=True, text=True)
            if out.returncode != 0:
                raise SystemExit(f'defs_carried: unknown commit or tree {ref!r}')
        self.tree = out.stdout.strip() if self.commit is None else None
        self.ref = self.commit or self.tree
        self.key = f'git:{self.ref}'
        ls = subprocess.run(['git', '-C', self.repo, 'ls-tree', '-r', '--name-only', self.ref, 'usecases/'],
                            capture_output=True, text=True)
        self._paths = set(ls.stdout.split('\n')) - {''}
        self._cache = {}

    def read(self, path):
        if path not in self._paths:
            return None
        if path not in self._cache:
            x = subprocess.run(['git', '-C', self.repo, 'cat-file', 'blob', f'{self.ref}:{path}'], capture_output=True)
            self._cache[path] = x.stdout.decode('utf-8', 'replace').replace('\r\n', '\n') if x.returncode == 0 else None
        return self._cache[path]

    def names(self, d):
        d = d.rstrip('/') + '/'
        return sorted(p[len(d):] for p in self._paths if p.startswith(d) and '/' not in p[len(d):])

    def subdirs(self, d):
        return _child_dirs(self._paths, d)

    def describe(self):
        return {'kind': 'commit', 'commit': self.commit} if self.commit else {'kind': 'tree', 'tree': self.tree}


class MemTree:
    """{path: text}; a path mapped to a dict {"blob": sha} is read from git by blob id (content-addressed)."""

    def __init__(self, files, key='mem', repo=None):
        self.files = dict(files)
        self.key = key
        self.repo = str(repo or ROOT)

    def read(self, path):
        v = self.files.get(path)
        if isinstance(v, dict):
            x = subprocess.run(['git', '-C', self.repo, 'cat-file', 'blob', v['blob']], capture_output=True)
            v = x.stdout.decode('utf-8', 'replace').replace('\r\n', '\n') if x.returncode == 0 else None
            self.files[path] = v
        return v

    def names(self, d):
        d = d.rstrip('/') + '/'
        return sorted(p[len(d):] for p in self.files if p.startswith(d) and '/' not in p[len(d):])

    def subdirs(self, d):
        return _child_dirs(self.files, d)

    def describe(self):
        return {'kind': 'files', 'key': self.key}


def _child_dirs(paths, d):
    d = d.rstrip('/') + '/'
    return sorted({p[len(d):].split('/', 1)[0] for p in paths if p.startswith(d) and '/' in p[len(d):]})


# --------------------------------------------------------------------------------------------------- normalisation ---
_CITE_PAREN = re.compile(r'\([^()]*(?:\d|section|appendix|table)[^()]*\)', re.I)
_CITE_LEAD = re.compile(r'^\s*[A-Z]?\d+(?:\.\d+)*[a-z]?\s*:', re.M)
_CITE_AT = re.compile(r'\b[A-Z]?\d+(?:\.\d+)*[a-z]?\s+at\s+\{\d\}')


def md_strip(s):
    """Markdown off: emphasis (** __ * _ `), list and quote markers, headers' '#', link and image syntax, math italics."""
    s = re.sub(r'!?\[([^\]]*)\]\([^)]*\)', r'\1', s)
    s = re.sub(r'(?m)^[ \t]*(?:>[ \t]?)+', '', s)
    s = re.sub(r'(?m)^[ \t]*(?:[-*+]|\d+[.)])[ \t]+', '', s)
    s = re.sub(r'(?m)^[ \t]*#{1,6}[ \t]+', '', s)
    s = re.sub(r'(\*\*|__)(.+?)\1', r'\2', s, flags=re.S)
    s = re.sub(r'(?<![\w*])\*(?!\s)([^*\n]+?)(?<!\s)\*(?![\w*])', r'\1', s)
    s = re.sub(r'(?<![\w])_(?!\s)([^_\n]+?)(?<!\s)_(?![\w])', r'\1', s)
    s = s.replace('`', '')
    s = re.sub(r'\$([^$\n]+)\$', r'\1', s)
    return s.replace('\\(', '').replace('\\)', '')


def cite_strip(s):
    """The counter's citation strips (uc-audit.py.reads-1119 _omit_legend_segments): a parenthesis holding a digit or
    'section' / 'appendix' / 'table', a leading '<n>:' and '<n> at {k}'."""
    return _CITE_AT.sub(' ', _CITE_LEAD.sub(' ', _CITE_PAREN.sub(' ', s)))


def source_norm(s):
    """omit_norm (byte-pinned) after markdown, list, link and math syntax and citations are stripped (DESIGN section 2)."""
    return counter.omit_norm(cite_strip(md_strip(s or '')))


def tokens(s):
    """Word tokens of an already normalised text."""
    return re.findall(r'[a-z0-9]+', s)


STOP = frozenset('a an the of to in on at by for and or nor but is are was were be been being as it its this that these '
                 'those with from into than then so such any all each every no not do does did has have had which who '
                 'whom whose what when where how their there them they he she his her our we us you your i'.split())


def content_tokens(toks):
    return [t for t in toks if t not in STOP]


def longest_run(q, c):
    """Length and start (in q) of the longest common contiguous token run of token lists q and c."""
    pos = {}
    for j, t in enumerate(c):
        pos.setdefault(t, []).append(j)
    best, at, prev = 0, 0, {}
    for i, t in enumerate(q):
        cur = {}
        for j in pos.get(t, ()):
            n = prev.get(j - 1, 0) + 1
            cur[j] = n
            if n > best:
                best, at = n, i - n + 1
        prev = cur
    return best, at


def split_ident(name):
    """Identifier split on '_', '-', '.', brackets and camelCase, lowercased."""
    s = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', name)
    return [t for t in re.split(r'[^A-Za-z0-9]+', s.lower()) if t]


def fold(t):
    """Plural fold of one token (the lexical matcher's only equivalence; no aliases)."""
    return t[:-1] if len(t) > 3 and t.endswith('s') and not t.endswith('ss') else t


# -------------------------------------------------------------------------------------------------------- documents ---
# name -> format, case directory, source files (path, how to read: 'file' whole or 'body' of a .ve.md), and adapter args.
DOCS = {
    'asimov-laws': {'format': 'rules.ve', 'dir': 'usecases/asimov-laws', 'rules': ['rules.ve'],
                    'env': 'environment.json', 'sources': [('usecases/asimov-laws/source.md', 'file')]},
    'asimov-extended': {'format': 'rules.ve', 'dir': 'usecases/asimov-extended', 'rules': ['rules.ve'],
                        'read_with': ['base.ve'], 'env': 'environment.json',
                        'sources': [('usecases/asimov-extended/source.md', 'file'),
                                    ('usecases/asimov-laws/source.md', 'file')]},
    'birthright-citizenship-debate': {'format': 'claims.ve', 'dir': 'usecases/birthright-citizenship-debate',
                                      'env': 'environment.json', 'countermodel': 'countermodel',
                                      'sources': [('usecases/birthright-citizenship-debate/source.md', 'file')]},
    'bluedot-grant': {'format': '.ve.md', 'dir': 'usecases/bluedot-grant', 'vemd': ['document.ve.md', 'causal.ve.md'],
                      'sources': [('usecases/bluedot-grant/source.md', 'file')]},
    'claude-constitution-excerpt': {'format': 'claims.ve', 'dir': 'usecases/claude-constitution-excerpt',
                                    'env': 'environment.json', 'unshown_env': ['definitions-environment.json'],
                                    'sources': [('usecases/claude-constitution-excerpt/source.md', 'file')]},
    'claude-constitution-pilot': {'format': '.ve.md', 'dir': 'usecases/claude-constitution-pilot/run-20261104T0716Z',
                                  'vemd': ['probe-translation.probe.md'],
                                  'sources': [('usecases/claude-constitution-pilot/run-20261104T0716Z/'
                                               'probe-translation.probe.md', 'body')]},
    'eligibility': {'format': 'rules.json', 'dir': 'usecases/eligibility', 'env': 'environment.json',
                    'code': ['translation.py'], 'sources_glob': ('usecases/eligibility/source', '.txt')},
    'math-mini-paper': {'format': 'theorems', 'dir': 'usecases/math-mini-paper',
                        'sources': [('usecases/math-mini-paper/paper.template.md', 'file')]},
    'news-article': {'format': 'claims.ve', 'dir': 'usecases/news-article', 'env': 'environment.json',
                     'vemd': ['news-w6a.ve.md'], 'sources': [('usecases/news-article/source.md', 'file')]},
    'question-answering': {'format': '.ve.md', 'dir': 'usecases/question-answering',
                           'vemd': ['group.ve.md', 'udhr-part07.ve.md'],
                           'sources': [('usecases/question-answering/group.ve.md', 'body'),
                                       ('usecases/question-answering/udhr-part07.ve.md', 'body')]},
    'udhr-pilot': {'format': '.ve.md', 'dir': 'usecases/udhr-pilot/run-20261010T1400Z', 'vemd': ['translation.ve.md'],
                   'sources': [('usecases/udhr-pilot/run-20261010T1400Z/translation.ve.md', 'body')]},
    'us-constitution-14th-s1': {'format': 'claims.ve', 'dir': 'usecases/us-constitution-14th-s1',
                                'env': 'environment.json',
                                'sources': [('usecases/us-constitution-14th-s1/source.md', 'file')]},
    'safety-framework': {'format': 'counter', 'dir': 'usecases/safety-framework', 'case': 'safety-framework'},
    'anthropic-rsp': {'format': 'counter', 'dir': 'usecases/anthropic-rsp', 'case': 'anthropic-rsp'},
    'openai-preparedness': {'format': 'counter', 'dir': 'usecases/openai-preparedness', 'case': 'openai-preparedness'},
}
COUNTER_DOCS = ('safety-framework', 'anthropic-rsp', 'openai-preparedness')
OUT_OF_SCOPE = {
    'agent-policy': 'an authored policy; its sources.md lists pages by hash that are not in the repository',
    'cedar-attributes': 'a fixture with no source document',
    'gatekeeper-exemption': 'a fixture with no source document',
    'webapp-commands': 'a fixture with no source document (a lexicon only, no VE text)',
    'closure-induction': 'its premises are math-mini-paper T9/T9e (checked there) plus two policy fixtures with no source',
}


def unscoped_use_cases(tree):
    """Use-case directories of the tree with no adapter (DOCS) and no out-of-scope reason. REPORT MODE: they are listed
    in the report and printed, never failed on, so a later item that adds a use case is not blocked by this tool."""
    scoped = {DOCS[n]['dir'].split('/')[1] for n in DOCS} | set(OUT_OF_SCOPE)
    return [d for d in tree.subdirs('usecases') if d not in scoped and not d.startswith(('_', '.'))]


NARROW_SURFACE = ('rule/fact lines with comments stripped, the code the check executes (comments, docstrings and the '
                  'vocabulary legend strings stripped), and the description of each predicate the rule uses; never sort '
                  'or constant legends, verbalisations, open-term factors or unused predicates\' legends')
COUNTER_SURFACE = ('the counter\'s omit_carrier_texts rule text and seq_unit_legends (the description of each predicate '
                   'the block uses), byte-pinned')


def _json(text):
    """A JSON object, or None for absent, unparsable or non-object text (every file the adapters read is an object)."""
    try:
        x = json.loads(text) if text else None
    except ValueError:
        return None
    return x if isinstance(x, dict) else None


def _vocab(env):
    v = env.get('vocabulary') if isinstance(env, dict) else None
    v = v if isinstance(v, dict) else {}
    out = {}
    for kind in ('sorts', 'predicates', 'constants'):
        x = v.get(kind) or {}
        if isinstance(x, list):
            x = {k: {} for k in x if isinstance(k, str)}
        if not isinstance(x, dict):
            x = {}
        out[kind] = {k: (d if isinstance(d, dict) else {}) for k, d in x.items()}
    return out


def _fields(d):
    """Every string field of a declaration, flattened: {field path: text}."""
    out = {}

    def walk(x, p):
        if isinstance(x, str):
            out[p] = x
        elif isinstance(x, dict):
            for k, y in x.items():
                walk(y, f'{p}.{k}' if p else k)
        elif isinstance(x, list):
            for i, y in enumerate(x):
                walk(y, f'{p}[{i}]')
    walk(d, '')
    return out


def front_matter(text):
    """(front matter dict, body text) of a .ve.md file."""
    if not text or not text.startswith('---\n'):
        return None, text or ''
    end = text.find('\n---\n', 4)
    if end < 0:
        return None, text
    return _json(text[4:end]), text[end + 5:]


_RULE_HEADER = re.compile(r'Rule ([1-9][0-9]*)(?: \(([^()]*)\))?\.(?=\s|\Z)')
_PRECEDENCE = re.compile(r'Rule ([1-9][0-9]*) takes precedence over rule ([1-9][0-9]*)\.')


def rule_header_refs(line):
    """The rules a rules.ve rule line's header names ("Rule 10 (exception to rules 8, 9)." -> ['R8', 'R9']), read by
    VE's own header grammar (ve.surface.softnorms.parse_header_options, the one owner of "exception to rule(s) ...");
    () for a header with no parentheses, None when the header is not one the grammar reads (the rule is UNPARSED)."""
    m = _RULE_HEADER.match(line)
    if m is None:
        return None
    try:
        refs, _parties = parse_header_options(m[2] or '')
    except VEError:
        return None
    return [f'R{n}' for n in refs]


def _strip_comment_lines(text):
    return '\n'.join(re.sub(r'\s+(#|--|//).*$', '', ln) for ln in text.split('\n')
                     if not ln.lstrip().startswith(('#', '--', '//')))


def _english_terms(text, voc):
    """Terms an English-surface rule text uses: predicates by the counter's used_predicates (verbalisation, act template,
    'classified as "<name>"'), constants by "<name>" or their verbalisation, sorts by their name or verbalisation."""
    env = {'vocabulary': {'predicates': voc['predicates']}}
    found = set(counter.used_predicates(text, env))
    low = text.lower()
    for k, d in voc['constants'].items():
        vb = d.get('verbalisation') if isinstance(d.get('verbalisation'), str) else None
        if f'"{k}"' in text or (vb and re.search(r'(?<![a-z])' + re.escape(vb.lower()) + r'(?![a-z])', low)):
            found.add(k)
    for k, d in voc['sorts'].items():
        words = {k.replace('_', ' ')}
        vb = d.get('verbalisation')
        if isinstance(vb, dict):
            words |= {w for w in vb.values() if isinstance(w, str)}
        elif isinstance(vb, str):
            words.add(vb)
        if any(re.search(r'(?<![a-z])' + re.escape(w.lower()) + r'(?![a-z])', low) for w in words if w):
            found.add(k)
    for k in voc['predicates']:
        if f'"{k}"' in text:
            found.add(k)
    return found


def _ident_terms(text, declared):
    """Terms a formal rule text uses: identifier tokens (and @constants) that are declared."""
    ids = set(re.findall(r'@?[A-Za-z_][A-Za-z0-9_]*', text))
    return {i.lstrip('@') for i in ids if i.lstrip('@') in declared}


def _ast_atoms(x, out):
    if isinstance(x, str):
        out.add(x)
    elif isinstance(x, dict):
        for v in x.values():
            _ast_atoms(v, out)
    elif isinstance(x, list):
        for v in x:
            _ast_atoms(v, out)
    return out


class Doc:
    """One document's adapter output: rules (id -> dict), declared terms, shown and unshown text, inputs."""

    def __init__(self, name, spec):
        self.name, self.spec = name, spec
        self.format = spec['format']
        self.counted = self.format == 'counter'
        self.rules = {}
        self.declared = {}        # term -> {'kind': ..., 'fields': {field: text}, 'shown': [field, ...]}
        self.unshown = []         # [(label, text)] document text the reader is never shown
        self.inputs = set()
        self.sources = {}         # path -> source text
        self.problems = []        # [(code, text)] e.g. a missing input
        self.lexical_labels = []  # [(label, text, rule id or None)] rule texts and rules.json labels for detector (c)

    def add_rule(self, rid, file, text, terms, shown, parsed=True, extra=None):
        r = {'id': rid, 'file': file, 'text': text, 'terms': sorted(terms), 'parsed': parsed, 'shown': shown}
        r.update(extra or {})
        self.rules[rid] = r

    def declare(self, term, kind, d, shown_fields=()):
        if term in self.declared:
            return
        self.declared[term] = {'kind': kind, 'fields': _fields(d), 'shown': list(shown_fields)}


def _read(doc, tree, path, required=True):
    doc.inputs.add(path)
    t = tree.read(path)
    if t is None and required:
        doc.problems.append(('MISSING-INPUT', path))
    return t


def _declare_vocab(doc, voc, open_terms=()):
    for k, d in voc['predicates'].items():
        doc.declare(k, 'predicate', d, ('description',))
    for k, d in voc['constants'].items():
        doc.declare(k, 'constant', d)
    for k, d in voc['sorts'].items():
        doc.declare(k, 'sort', d)
    for ot in open_terms or ():
        if isinstance(ot, dict) and ot.get('name'):
            doc.declare(ot['name'], 'open_term', ot)


def _with_arg_sorts(terms, voc, open_terms):
    out = set(terms)
    ots = {o.get('name'): o for o in open_terms or () if isinstance(o, dict)}
    for t in list(out):
        for a in (voc['predicates'].get(t) or {}).get('arguments') or (ots.get(t) or {}).get('arguments') or ():
            if isinstance(a, str) and a in voc['sorts']:
                out.add(a)
        s = (voc['constants'].get(t) or {}).get('sort')
        if isinstance(s, str) and s in voc['sorts']:
            out.add(s)
    return out


def _legend_runs(terms, voc):
    return [(f'legend:{k}', voc['predicates'][k].get('description') or '') for k in sorted(terms)
            if k in voc['predicates'] and isinstance(voc['predicates'][k].get('description'), str)]


def _finish_unshown(doc, voc, open_terms=(), label=''):
    """Everything in the vocabulary the narrow surface never shows; unused predicates' descriptions are added later."""
    for kind in ('sorts', 'constants'):
        for k, d in voc[kind].items():
            for f, t in _fields(d).items():
                doc.unshown.append((f'{label}{kind[:-1]}:{k}.{f}', t))
    for k, d in voc['predicates'].items():
        for f, t in _fields(d).items():
            if f != 'description':
                doc.unshown.append((f'{label}predicate:{k}.{f}', t))
    for ot in open_terms or ():
        if isinstance(ot, dict):
            for f, t in _fields(ot).items():
                doc.unshown.append((f'{label}open_term:{ot.get("name")}.{f}', t))


def adapt_rules_ve(doc, tree):
    s = doc.spec
    env = _json(_read(doc, tree, f'{s["dir"]}/{s["env"]}'))
    voc = _vocab(env)
    _declare_vocab(doc, voc)
    for f in s.get('read_with', ()):
        _read(doc, tree, f'{s["dir"]}/{f}', required=False)
    precedence = {}
    for f in s['rules']:
        text = _read(doc, tree, f'{s["dir"]}/{f}') or ''
        for i, line in enumerate(text.split('\n'), 1):
            p = _PRECEDENCE.fullmatch(line.strip())
            if p:
                precedence.setdefault(f'R{int(p[1])}', set()).add(f'R{int(p[2])}')
                continue
            m = re.match(r'^Rule (\d+)\b', line)
            if not m:
                if line.lstrip().startswith(('#', '--', '//')):
                    doc.unshown.append((f'comment:{f}:{i}', line))
                continue
            body = _strip_comment_lines(line)
            terms = _with_arg_sorts(_english_terms(body, voc), voc, ())
            refs = rule_header_refs(body)
            rid = f'R{int(m.group(1))}'
            doc.add_rule(rid, f'{f}:{i}', body, terms, [('rule', body)], parsed=refs is not None,
                         extra={'refs': sorted(set(refs or ()) - {rid})})
    for rid, targets in precedence.items():
        if rid in doc.rules:
            doc.rules[rid]['refs'] = sorted(set(doc.rules[rid]['refs']) | (targets - {rid}))
    # A rule's header that names other rules ("exception to rules 8, 9") and a precedence sentence ("Rule 3 takes
    # precedence over rule 5.") put those rules on its dependency path, read with VE's own header grammar; the path's
    # terms are the rule's terms (transitively), as a .ve.md unit's graph/uses path is. A header the grammar does not
    # read leaves the rule UNPARSED (its dependencies unknown), never silently short of a reference.
    own = {rid: set(r['terms']) for rid, r in doc.rules.items()}
    for rid, r in doc.rules.items():
        seen, todo, path = {rid}, list(r['refs']), []
        while todo:
            x = todo.pop(0)
            if x in seen or x not in doc.rules:
                continue
            seen.add(x)
            path.append(x)
            todo += doc.rules[x]['refs']
        terms = set(own[rid]).union(*(own[x] for x in path)) if path else set(own[rid])
        r['path'] = path
        r['terms'] = sorted(terms)
        r['shown'] = r['shown'] + _legend_runs(terms, voc)
    _finish_unshown(doc, voc)
    return voc, ()


def adapt_claims(doc, tree):
    s = doc.spec
    env = _json(_read(doc, tree, f'{s["dir"]}/{s["env"]}'))
    voc = _vocab(env)
    _declare_vocab(doc, voc)
    declared = set(voc['predicates']) | set(voc['constants']) | set(voc['sorts'])
    text = _read(doc, tree, f'{s["dir"]}/claims.ve') or ''
    n = 0
    for i, line in enumerate(text.split('\n'), 1):
        if not line.strip():
            continue
        if line.lstrip().startswith(('#', '--', '//')):
            doc.unshown.append((f'comment:claims.ve:{i}', line))
            continue
        n += 1
        body = _strip_comment_lines(line)
        terms = _with_arg_sorts(_ident_terms(body, declared), voc, ())
        doc.add_rule(f'C{i}', f'claims.ve:{i}', body, terms, [('rule', body)] + _legend_runs(terms, voc))
    cm = s.get('countermodel')
    if cm:
        for name in tree.names(f'{s["dir"]}/{cm}'):
            m = re.fullmatch(r'test(\d+)-premises\.ve', name)
            if not m:
                continue
            prem = _read(doc, tree, f'{s["dir"]}/{cm}/{name}') or ''
            concl = _read(doc, tree, f'{s["dir"]}/{cm}/test{m.group(1)}-conclusion.ve', required=False) or ''
            lines = [ln for ln in (prem + '\n' + concl).split('\n') if ln.strip()]
            body = _strip_comment_lines('\n'.join(lines))
            terms = _with_arg_sorts(_ident_terms(body, declared), voc, ())
            runs = [('rule', ln) for ln in body.split('\n') if ln.strip()]
            doc.add_rule(f'T{m.group(1)}', f'{cm}/{name}', body, terms, runs + _legend_runs(terms, voc))
    for f in s.get('unshown_env', ()):
        e2 = _vocab(_json(_read(doc, tree, f'{s["dir"]}/{f}')))
        for kind in ('sorts', 'predicates', 'constants'):
            for k, d in e2[kind].items():
                for fld, t in _fields(d).items():
                    doc.unshown.append((f'{f}:{kind[:-1]}:{k}.{fld}', t))
    _finish_unshown(doc, voc)
    if s.get('vemd'):
        adapt_vemd(doc, tree, prefix='')
    return voc, ()


def adapt_vemd(doc, tree, prefix=None):
    """.ve.md units: a unit with a VE body (ast, norm, quantity or a body fence) or an `open` meaning is a rule; a
    `specified` unit with no body is UNPARSED (its content is only in reading sets, which are not a dependency source)."""
    s = doc.spec
    vocs = []
    for f in s['vemd']:
        text = _read(doc, tree, f'{s["dir"]}/{f}') or ''
        fm, body = front_matter(text)
        if fm is None:
            doc.problems.append(('UNREADABLE-FRONT-MATTER', f'{s["dir"]}/{f}'))
            continue
        voc = _vocab(fm.get('environment'))
        ots = [o for o in (fm.get('open_terms') if isinstance(fm.get('open_terms'), list) else ())
               if isinstance(o, dict) and isinstance(o.get('name'), str)]
        _declare_vocab(doc, voc, ots)
        vocs.append(voc)
        declared = set(voc['predicates']) | set(voc['constants']) | set(voc['sorts']) | {o['name'] for o in ots if o.get('name')}
        fences = dict(re.findall(r'(?ms)^```ve (\S+)\n(.*?)^```', body))
        nodes = {}
        graph = fm.get('graph') if isinstance(fm.get('graph'), dict) else {}
        for nd in (graph.get('nodes') if isinstance(graph.get('nodes'), list) else ()):
            if isinstance(nd, dict):
                nodes.setdefault(nd.get('unit') or nd.get('name'), []).append(nd)
        for u in (fm.get('units') if isinstance(fm.get('units'), list) else ()):
            if not isinstance(u, dict) or not isinstance(u.get('id'), str):
                continue
            kind, meaning, content = u.get('kind'), u.get('meaning'), u.get('content')
            if kind == 'meta':
                continue
            opens = list(meaning.get('open') or ()) if isinstance(meaning, dict) else []
            rid = u.get('id')
            terms, text_runs, parsed = set(), [], True
            if isinstance(content, dict):
                if 'fence' in content:
                    ft = fences.get(content['fence'], '')
                    text_runs.append(('rule', _strip_comment_lines(ft)))
                    terms |= _english_terms(ft, voc)
                    for nd in nodes.get(rid, ()) + nodes.get(content['fence'], ()):
                        terms |= _ast_atoms(nd.get('ast'), set()) & declared
                else:
                    terms |= _ast_atoms(content, set()) & declared
            elif opens:
                pass
            elif meaning == 'specified':
                parsed = False
            else:
                continue
            terms |= {o for o in opens if o in declared}
            if isinstance(kind, list):   # an attributed unit names its speaker in its kind list
                terms |= {k for k in kind if isinstance(k, str) and (k in declared or k in doc.declared)}
            terms = _with_arg_sorts(terms, voc, ots)
            if rid in doc.rules:   # the same unit id in two files of one document: the later one is named by its file
                rid = f'{rid}@{f}'
            doc.add_rule(rid, f'{f}#{rid}', json.dumps(content, ensure_ascii=False) if content else '', terms,
                         text_runs + _legend_runs(terms, voc), parsed=parsed,
                         extra={'meaning': meaning if isinstance(meaning, str) else 'open' if opens else 'other'})
        _finish_unshown(doc, voc, ots, label=f'{f}:')
    return (vocs[0] if vocs else _vocab({})), ()


def _code_text(src, voc):
    """Executed code with comments, docstrings and the vocabulary's own legend strings stripped (a legend counts only
    through the legend rule: an unused predicate's legend never carries)."""
    legends = {source_norm(t) for kind in ('predicates', 'constants', 'sorts') for d in voc[kind].values()
               for t in _fields(d).values()}
    lines = src.split('\n')
    try:
        tree = ast.parse(src)
    except SyntaxError:
        tree = None
    if tree is not None:
        for nd in ast.walk(tree):
            if isinstance(nd, ast.Expr) and isinstance(getattr(nd, 'value', None), ast.Constant) \
                    and isinstance(nd.value.value, str):
                for i in range(nd.lineno - 1, nd.end_lineno):
                    lines[i] = ''
        for nd in ast.walk(tree):
            if isinstance(nd, ast.Constant) and isinstance(nd.value, str) and nd.lineno == nd.end_lineno \
                    and source_norm(nd.value) in legends and len(nd.value) > 12:
                ln = lines[nd.lineno - 1]
                lines[nd.lineno - 1] = ln[:nd.col_offset] + '""' + ln[nd.end_col_offset:] \
                    if len(ln) >= nd.end_col_offset else ln
    return '\n'.join(re.sub(r'\s+#.*$', '', ln) for ln in lines if not ln.lstrip().startswith('#'))


def adapt_rules_json(doc, tree):
    s = doc.spec
    env = _json(_read(doc, tree, f'{s["dir"]}/{s["env"]}'))
    voc = _vocab(env)
    _declare_vocab(doc, voc)
    declared = set(voc['predicates']) | set(voc['constants']) | set(voc['sorts'])
    code = []
    for f in s.get('code', ()):
        src = _read(doc, tree, f'{s["dir"]}/{f}') or ''
        code.append((f'code:{f}', _code_text(src, voc)))
    rj = _json(_read(doc, tree, f'{s["dir"]}/rules.json')) or {}
    for r in (rj.get('rules') if isinstance(rj.get('rules'), list) else ()):
        if not isinstance(r, dict) or not isinstance(r.get('id'), str):
            continue
        terms = _with_arg_sorts(_ast_atoms(r.get('formula'), set()) & declared, voc, ())
        gloss = r['gloss'] if isinstance(r.get('gloss'), str) else ''
        doc.add_rule(r['id'], 'rules.json', gloss, terms,
                     [('rule:gloss', gloss)] + _legend_runs(terms, voc) + code)
        doc.lexical_labels.append((f'rules.json:{r["id"]}.gloss', gloss, r['id']))
        if isinstance(r.get('source'), str):
            doc.unshown.append((f'rules.json:{r["id"]}.source', r['source']))
    _finish_unshown(doc, voc)
    return voc, ()


def adapt_theorems(doc, tree):
    s = doc.spec
    envs = {}
    for name in ('environment.json', 'environment-closure.json'):
        envs[name] = _vocab(_json(_read(doc, tree, f'{s["dir"]}/{name}')))
        _declare_vocab(doc, envs[name])
    theorems = sorted({p.split('/')[0] for p in _subdirs(tree, f'{s["dir"]}/theorems')})
    for t in theorems:
        base = f'{s["dir"]}/theorems/{t}'
        v = _json(_read(doc, tree, f'{base}/verdict.json', required=False)) or {}
        voc = envs.get(v.get('environment') or 'environment.json') or envs['environment.json']
        declared = set(voc['predicates']) | set(voc['constants']) | set(voc['sorts'])
        lines = []
        for part in ('premises.ve', 'conclusion.ve'):
            lines += [ln for ln in (_read(doc, tree, f'{base}/{part}', required=False) or '').split('\n') if ln.strip()]
        body = _strip_comment_lines('\n'.join(lines))
        terms = _with_arg_sorts(_ident_terms(body, declared), voc, ())
        doc.add_rule(t, f'theorems/{t}', body, terms,
                     [('rule', ln) for ln in body.split('\n') if ln.strip()] + _legend_runs(terms, voc),
                     extra={'environment': v.get('environment') or 'environment.json'})
    for name, voc in envs.items():
        _finish_unshown(doc, voc, label=f'{name}:')
    return envs['environment.json'], ()


def _subdirs(tree, d):
    """Names of the subdirectories of d that hold a premises.ve (GitTree and MemTree list files, not directories)."""
    if isinstance(tree, FsTree):
        p = tree.root / d
        return sorted(x.name for x in p.iterdir() if x.is_dir() and (x / 'premises.ve').is_file()) if p.is_dir() else []
    pref = d.rstrip('/') + '/'
    paths = tree._paths if isinstance(tree, GitTree) else set(tree.files)
    return sorted({p[len(pref):].split('/')[0] for p in paths
                   if p.startswith(pref) and p.endswith('/premises.ve') and p[len(pref):].count('/') == 1})


def _pinned_source_bytes(tree, case):
    ps = _json(tree.read('usecases/pinned_sources.json')) or {}
    e = (ps.get('sources') or {}).get(case) or {}
    return e.get('text_bytes'), e.get('path'), e.get('text_sha256')


def adapt_counter(doc, tree):
    """FSF/RSP/PF: the counter's own carrier code (omit_carrier_texts, seq_unit_legends), byte-pinned."""
    case = doc.spec['case']
    key = f'{tree.key}#{doc.name}'
    counter.bind_tree(key, tree)
    show = (lambda n: tree.read(f'usecases/{case}/{n}'))
    for n in ('rules.d1.ve', 'facts.d1.ve', 'environment.d1.json', 'cases.json'):
        _read(doc, tree, f'usecases/{case}/{n}', required=n != 'cases.json')
    for n in tree.names(f'usecases/{case}'):
        if n.endswith('vocabulary.py'):
            doc.inputs.add(f'usecases/{case}/{n}')
    for n in counter.OMIT_CODE.get(case, ()):
        doc.inputs.add(f'usecases/{case}/{n}')
    for n, _h in counter.OMIT_CODE_SECTION.get(case, ()):
        doc.inputs.add(f'usecases/{case}/{n}')
    doc.inputs.add('usecases/pinned_sources.json')
    env = _json(show('environment.d1.json')) or {}
    voc = _vocab(env)
    _declare_vocab(doc, voc)
    rules, facts = show('rules.d1.ve') or '', show('facts.d1.ve') or ''
    oct_ = counter.omit_carrier_texts(case, key)
    src_bytes, src_path, _sha = _pinned_source_bytes(tree, case)
    doc.pinned_source = {'path': src_path, 'text_bytes': src_bytes}
    code_names = set()
    for _label, t in counter.omit_code_parts(case, show):
        if t:
            try:
                for nd in ast.walk(ast.parse(t)):
                    if isinstance(nd, ast.Dict):
                        code_names |= {k.value for k in nd.keys if isinstance(k, ast.Constant) and isinstance(k.value, str)
                                       and re.fullmatch(r'[a-z][a-z0-9_]+', k.value)}
            except SyntaxError:
                pass
    for name in sorted(code_names - set(doc.declared)):
        doc.declare(name, 'code_name', {})
    blocks = {**counter.rule_blocks(rules), **counter.rule_blocks(facts)}
    for uid, (full, body) in blocks.items():
        used = counter.used_predicates(body, env)
        legends = counter.seq_unit_legends(case, uid, rules, facts, show)
        runs = [('rule', (oct_.get(uid) or {}).get('rule', ''))]
        for ln in legends.split('\n')[1:]:
            m = re.match(r'- ([^:]+): (.*)$', ln)
            if m:
                runs.append((f'legend:{m.group(1)}', m.group(2)))
        terms = set(used) | {k for k in voc['constants'] if f'"{k}"' in body}
        terms = _with_arg_sorts(terms, voc, ())
        render = f'block {uid}:\n' + full.strip() + '\n\n' + legends
        size = len(render.encode()) + (src_bytes or 0)
        doc.add_rule(uid, 'rules.d1.ve' if uid in counter.rule_blocks(rules) else 'facts.d1.ve', body, terms, runs,
                     extra={'header': full.split('\n')[0], 'prompt_bytes_lower_bound': size,
                            'oversize': size > ARG_LIMIT, 'source_bytes_known': src_bytes is not None})
        doc.unshown.append((f'header:{uid}', full.split('\n')[0]))
    code_txt = (oct_.get('D2D3') or {}).get('code', '')
    if code_txt:
        terms = {k for k in set(voc['predicates']) | set(voc['constants']) | code_names
                 if re.search(r'["\']' + re.escape(k) + r'["\']', ' '.join(t or '' for _l, t in
                                                                          counter.omit_code_parts(case, show)))}
        size = len(code_txt.encode()) + (src_bytes or 0)
        doc.add_rule('D2D3', 'code', code_txt, terms, [('code', code_txt)],
                     extra={'prompt_bytes_lower_bound': size, 'oversize': size > ARG_LIMIT,
                            'source_bytes_known': src_bytes is not None})
    _finish_unshown(doc, voc)
    for n in tree.names(f'usecases/{case}'):
        if n.endswith('vocabulary.py'):
            doc.unshown.append((f'file:{n}', tree.read(f'usecases/{case}/{n}') or ''))
    return voc, ()


ADAPTERS = {'rules.ve': adapt_rules_ve, 'claims.ve': adapt_claims, '.ve.md': adapt_vemd, 'rules.json': adapt_rules_json,
            'theorems': adapt_theorems, 'counter': adapt_counter}


def load_sources(doc, tree):
    s = doc.spec
    if doc.counted:
        _n, path, sha = _pinned_source_bytes(tree, s['case'])
        p = Path.home() / path if path else None
        if p and p.is_file():
            import hashlib
            raw = p.read_bytes()
            if hashlib.sha256(raw).hexdigest() == sha:
                doc.sources[f'~/{path}'] = raw.decode('utf-8', 'replace')
            else:
                doc.problems.append(('PINNED-SOURCE-HASH', f'~/{path}'))
        else:
            doc.problems.append(('PINNED-SOURCE-ABSENT', f'~/{path}'))
        return
    items = list(s.get('sources', ()))
    if s.get('sources_glob'):
        d, ext = s['sources_glob']
        items += [(f'{d}/{n}', 'file') for n in tree.names(d) if n.endswith(ext)]
    for path, how in items:
        t = _read(doc, tree, path)
        if t is None:
            continue
        doc.sources[path] = front_matter(t)[1] if how == 'body' else t


def build_doc(name, tree):
    """The document's adapter output. An input the adapter cannot read (malformed JSON of an unexpected shape inside the
    copied counter code, say) is reported as an ADAPTER-FAILED problem with the rules read so far, never a crash and
    never a silent pass: the summary names it."""
    doc = Doc(name, DOCS[name])
    try:
        ADAPTERS[doc.format](doc, tree)
    except (AttributeError, TypeError, KeyError, ValueError, IndexError) as e:
        doc.problems.append(('ADAPTER-FAILED', f'{type(e).__name__}: {e}'))
    load_sources(doc, tree)
    used = {t for r in doc.rules.values() for t in r['terms']}
    for t, d in doc.declared.items():
        if d['kind'] == 'predicate' and t not in used and 'description' in d['fields']:
            doc.unshown.append((f'unused-predicate:{t}.description', d['fields']['description']))
    doc.unshown_norm = [(lab, source_norm(t)) for lab, t in doc.unshown if t]
    doc.unshown_tokens = {lab: ' ' + ' '.join(tokens(t)) + ' ' for lab, t in doc.unshown_norm}
    for r in doc.rules.values():
        r['shown_norm'] = [(lab, source_norm(t)) for lab, t in r['shown'] if t]
        r['shown_tokens'] = {lab: ' ' + ' '.join(tokens(t)) + ' ' for lab, t in r['shown_norm']}
    return doc


# ------------------------------------------------------------------------------------------------- detector (b) ------
MARKER_RE = re.compile(
    r'means|meaning|defined|definition|refers? to|includes?|does not include|excludes?|for the purposes? of|'
    r'in this (?:Act|Part|Schedule|regulation|section|document)|by "|by “|we (?:call|use|mean)|what we call|i\.e\.|'
    r'that is,|known as|\(([A-Z]{2,})\)|has the meaning|construed|treated as|counts? as|qualif', re.I)
LEAD_RE = re.compile(r'^\s*(?:[-*]\s+|\d+\.\s+)?\*\*([^*]+?):?\*\*\s*:?\s|^\s*(?:[-*]\s+)?([A-Z][A-Za-z’\'\- ]{1,60}):\s+\S')
MARKER_VERSION = 'amendment-2 + bold/numbered lead-ins + table rows (r3)'


def _sentences(line):
    out, start = [], 0
    for m in re.finditer(r'(?<=[.!?;])["”’)]*\s+(?=[A-Z“"(])', line):
        out.append((start, line[start:m.start()].strip()))
        start = m.end()
    out.append((start, line[start:].strip()))
    return [(a, s) for a, s in out if s]


def marker_grep(path, text):
    """Detector (b): every marker hit of the source, as {file, line, marker, passage}; a passage is the sentence holding
    the marker, a lead-in line whole, or a table row."""
    hits, seen = [], set()
    for i, line in enumerate(text.split('\n'), 1):
        if not line.strip():
            continue
        if line.lstrip().startswith('|') and line.count('|') >= 3:
            if not re.fullmatch(r'[\s|:\-]+', line):
                hits.append({'file': path, 'line': i, 'marker': 'table-row', 'passage': line.strip()})
            continue
        lead = LEAD_RE.match(line)
        if lead:
            hits.append({'file': path, 'line': i, 'marker': 'lead-in', 'passage': line.strip()})
            seen.add((i, line.strip()))
            continue
        for _a, sent in _sentences(line):
            m = MARKER_RE.search(sent)
            if m and (i, sent) not in seen:
                seen.add((i, sent))
                hits.append({'file': path, 'line': i, 'marker': m.group(0), 'passage': sent})
    return hits


def defined_phrases(passage, marker):
    """Candidate defined phrases of a passage: quoted or bold phrases, a lead-in label, all-caps acronyms in
    parentheses, a table row's first cell, and (at least two content words) the words just before a marker other
    than 'qualif...' (that marker is printed as a hit; the word it starts names no defined phrase by itself)."""
    marked = []
    for m in re.finditer(r'[“"]([^”"]{2,80})[”"]', passage):
        marked.append(m.group(1))
    marked += re.findall(r'\*\*([^*]{2,80})\*\*', passage)
    marked += re.findall(r'\(([A-Z][A-Z0-9/&\-]{1,12})\)', passage)
    lm = LEAD_RE.match(passage)
    if lm:
        marked.append(lm.group(1) or lm.group(2))
    if marker == 'table-row':
        cells = [c.strip() for c in passage.strip('|').split('|')]
        if cells and cells[0]:
            marked.append(cells[0])
    guessed = []
    if marker not in ('table-row', 'lead-in'):
        m = re.search(re.escape(marker), passage, re.I)
        if m and not marker.lower().startswith('qualif'):
            before = re.split(r'[,;:.()“”"]', passage[:m.start()])[-1]
            ws = [w for w in re.findall(r"[A-Za-z0-9’'\-]+", before)][-4:]
            while ws and ws[0].lower() in STOP:
                ws.pop(0)
            if ws:
                guessed.append(' '.join(ws))
    res = []
    for p, need in [(x, 1) for x in marked] + [(x, 2) for x in guessed]:
        toks = [fold(t) for t in tokens(source_norm(p))]
        while toks and toks[-1] in STOP:
            toks.pop()
        while toks and toks[0] in STOP:
            toks.pop(0)
        content = [t for t in toks if len(t) >= 3 and t not in STOP]
        if len(content) >= need and len(toks) <= 8 and toks not in res:
            res.append(toks)
    return res


# ------------------------------------------------------------------------------------------------- detector (c) ------
def lexical_index(doc):
    """[(term or None, rule id or None, where, folded tokens)] of every name, legend, factor and label text."""
    idx = []
    for t, d in doc.declared.items():
        idx.append((t, None, 'name', [fold(x) for x in split_ident(t)]))
        for f, txt in d['fields'].items():
            if f in ('sort', 'decided_by', 'jurisdiction', 'name') or f.startswith('arguments'):
                continue
            idx.append((t, None, f, [fold(x) for x in tokens(source_norm(txt))]))
    for lab, txt, rid in doc.lexical_labels:
        idx.append((None, rid, lab, [fold(x) for x in tokens(source_norm(txt))]))
    for rid, r in doc.rules.items():
        for lab, txt in r['shown']:
            if lab.startswith('rule') and txt:
                idx.append((None, rid, 'rule-text', [fold(x) for x in tokens(source_norm(txt))]))
    return idx


def _contains(hay, needle):
    n = len(needle)
    return n > 0 and any(hay[i:i + n] == needle for i in range(len(hay) - n + 1))


def lexical_match(idx, phrase, single_word_legends=True):
    """Detector (c), aliases off: every (term, rule, where) whose text holds the phrase's tokens contiguously (tokens
    plural-folded). With single_word_legends False a one-word phrase matches names only: the marker grep's guessed
    one-word phrases ("claim", "person") would otherwise hit most legends of a document."""
    hits = []
    single = len(phrase) == 1 and not single_word_legends
    for term, rid, where, toks in idx:
        if single and where != 'name':
            continue
        if _contains(toks, phrase):
            hits.append((term, rid, where))
        elif where == 'name' and len(toks) >= 2 and _contains(phrase, toks):
            hits.append((term, rid, 'name-in-phrase'))
    return hits


def phrase_tokens(p):
    return [fold(t) for t in tokens(source_norm(p))]


def lexical_recall(doc, cases):
    """The section 5 bar on known cases: per (entry, term), whether a phrase of the entry occurs as tokens in the term's
    identifier or legend, or a multi-word identifier occurs in the phrase (eligible), and whether detector (c) links the entry to the term. Pairs with no such phrase
    can be found only through an alias (aliases are off): they are listed."""
    idx = lexical_index(doc)
    seen, out = set(), []
    for k in cases:
        t = k.get('term')
        if not t or t not in doc.declared or not k.get('phrases'):
            continue
        key = (k.get('row') or k['case'], t)
        if key in seen:
            continue
        seen.add(key)
        texts = [[fold(x) for x in split_ident(t)]] + [
            [fold(x) for x in tokens(source_norm(v))] for f, v in doc.declared[t]['fields'].items()
            if f in ('description', 'verbalisation') or f.startswith(('factors', 'verbalisation'))]
        eligible = found = False
        for ph in k['phrases']:
            pt = phrase_tokens(ph)
            if not pt:
                continue
            if any(_contains(x, pt) for x in texts) or (len(texts[0]) >= 2 and _contains(pt, texts[0])):
                eligible = True
            if any(term == t for term, _r, _w in lexical_match(idx, pt)):
                found = True
        out.append({'doc': doc.name, 'entry': key[0], 'term': t, 'phrases': k['phrases'], 'eligible': eligible,
                    'found': found})
    return out


# -------------------------------------------------------------------------------------------------------- verdicts ---
def _clauses(qn):
    parts = re.split(r'[;:,.—]| - | and | or ', qn)
    return [c for c in (content_tokens(tokens(p)) for p in parts) if c]


def verdict(doc, rule, passage):
    """The section 2 verdict of one passage on one rule's shown surface, with its diagnostics."""
    q = source_norm(passage)
    qt = tokens(q)
    out = {'verdict': None, 'where': None, 'best_run': 0, 'tokens': len(qt), 'best_run_at': None}
    if rule is None:
        out['verdict'] = 'NOT CARRIED'
        out['where'] = 'rule not found'
        return out
    for lab, txt in rule['shown_norm']:
        n, _a = longest_run(qt, tokens(txt))
        if n > out['best_run']:
            out['best_run'], out['best_run_at'] = n, lab
    if q and any(q in txt for _l, txt in rule['shown_norm']):
        lab = next(lab for lab, txt in rule['shown_norm'] if q in txt)
        out['where'] = lab
        out['best_run'], out['best_run_at'] = len(qt), lab
        if doc.counted:
            out['verdict'] = 'OVERSIZE' if rule.get('oversize') else 'CARRIED'
        else:
            out['verdict'] = 'CARRIED-ASSUMED'
        return out
    # Off the rule's surface the passage counts as present when its words occur whole and in order (punctuation
    # ignored): the diagnosis is ELSEWHERE or UNSHOWN, never a pass. On the surface only CARRIED passes.
    qj = ' ' + ' '.join(qt) + ' '
    if qt and any(qj in ' ' + ' '.join(tokens(txt)) + ' ' for _l, txt in rule['shown_norm']):
        out['where'] = 'words whole on the rule surface, punctuation differs'
    own = {lab for lab, _t in rule['shown_norm']}
    for rid, r in doc.rules.items():
        if rid == rule['id']:
            continue
        for lab, txt in r['shown_norm']:
            if qt and lab not in own and qj in r['shown_tokens'][lab]:
                out['verdict'], out['where'] = 'ELSEWHERE', f'{rid}:{lab}'
                return out
    for lab, txt in doc.unshown_norm:
        if qt and qj in doc.unshown_tokens[lab]:
            out['verdict'], out['where'] = 'UNSHOWN', lab
            return out
    cl = _clauses(q)
    shown_ct = [content_tokens(tokens(txt)) for _l, txt in rule['shown_norm']]
    if cl and len(cl) > 1 and all(any(_contains(s, c) for s in shown_ct) for c in cl):
        out['verdict'] = 'PARTIAL'
        return out
    out['verdict'] = 'FRAGMENT' if out['best_run'] >= FRAGMENT_MIN else 'NOT CARRIED'
    return out


def worst(vs):
    return min(vs, key=lambda v: RANK[v]) if vs else None


# ------------------------------------------------------------------------------------------------------ the report ---
def evaluate_known(doc, known):
    """The known cases of this document: each (rule, term, passages) pair's verdict and whether the adapter reaches it."""
    out = []
    for k in known:
        r = doc.rules.get(k['rule'])
        term = k.get('term')
        if r is None:
            reach = 'rule-missing'
        elif not r['parsed']:
            reach = 'unparsed-rule'
        elif term is None:
            reach = 'no-ve-term'
        elif term not in doc.declared:
            reach = 'term-not-declared'
        elif term in r['terms']:
            reach = 'parsed'
        else:
            reach = 'term-not-in-rule'
        per = [verdict(doc, r, p['text']) for p in k['passages']]
        v = worst([x['verdict'] for x in per])
        out.append({'case': k['case'], 'entry': k.get('entry'), 'rule': k['rule'], 'term': term, 'reach': reach,
                    'verdict': v, 'best_run': [x['best_run'] for x in per], 'tokens': [x['tokens'] for x in per],
                    'where': [x['where'] for x in per], 'audit_verdict': k.get('audit_verdict'),
                    'hit': v not in PASSING and reach in ('parsed', 'unparsed-rule')})
    return out


def auto_inventory(doc):
    """Detector (b) over the document's sources, each hit linked to terms by detector (c)."""
    idx = lexical_index(doc)
    entries, pairs = [], []
    for path, text in doc.sources.items():
        for h in marker_grep(path, text):
            phrases = defined_phrases(h['passage'], h['marker'])
            links = []
            for ph in phrases:
                for term, rid, where in lexical_match(idx, ph, single_word_legends=False):
                    links.append({'phrase': ' '.join(ph), 'term': term, 'rule': rid, 'where': where})
            e = dict(h, id=f'M{len(entries) + 1}', phrases=[' '.join(p) for p in phrases], links=links)
            entries.append(e)
            done = set()
            for ln in links:
                rules = [ln['rule']] if ln['rule'] else [rid for rid, r in doc.rules.items() if ln['term'] in r['terms']]
                for rid in rules:
                    key = (rid, ln['term'])
                    if key in done:
                        continue
                    done.add(key)
                    v = verdict(doc, doc.rules[rid], h['passage'])
                    pairs.append({'entry': e['id'], 'rule': rid, 'term': ln['term'], 'phrase': ln['phrase'],
                                  'via': ln['where'], 'verdict': v['verdict'], 'where': v['where'],
                                  'best_run': v['best_run'], 'tokens': v['tokens'], 'best_run_at': v['best_run_at']})
    return entries, pairs


def run_document(name, tree, known=()):
    t0 = time.perf_counter()
    doc = build_doc(name, tree)
    mine = [k for k in known if k['doc'] == name]
    kres = evaluate_known(doc, mine)
    if doc.counted:
        entries, pairs = [], []
    else:
        entries, pairs = auto_inventory(doc)
    unparsed = [rid for rid, r in doc.rules.items() if not r['parsed']]
    reached = {t for r in doc.rules.values() if r['parsed'] for t in r['terms']}
    candidates = sorted(t for t in doc.declared if t not in reached and doc.declared[t]['kind'] != 'code_name')
    findings = {}
    for p in pairs:
        if p['verdict'] not in PASSING:
            findings[p['verdict']] = findings.get(p['verdict'], 0) + 1
    rep = {
        'doc': name, 'format': doc.format,
        'visibility': ('COUNTED' if doc.counted else 'VISIBILITY-UNESTABLISHED'),
        'surface': COUNTER_SURFACE if doc.counted else NARROW_SURFACE,
        'coverage': ('PARTIAL (the 9 repair terms only)' if doc.counted else 'COMPLETE'),
        'inputs': sorted(doc.inputs), 'sources': sorted(doc.sources), 'problems': doc.problems,
        'rules': len(doc.rules), 'declared_terms': len(doc.declared),
        'unparsed': [{'rule': rid, 'finding': 'UNPARSED',
                      'dependencies': f'unknown: any of the document\'s {len(doc.declared)} declared terms',
                      'candidates': candidates} for rid in unparsed],
        'oversize': sorted(rid for rid, r in doc.rules.items() if r.get('oversize')),
        'max_prompt_bytes_lower_bound': max((r.get('prompt_bytes_lower_bound') or 0 for r in doc.rules.values()),
                                            default=0) if doc.counted else None,
        'known': kres,
        'marker_hits': len(entries), 'marker_entries': entries,
        'unlinked_marker_hits': sum(1 for e in entries if not e['links']),
        'pairs': pairs, 'findings_by_verdict': findings,
        'pairs_by_verdict': _count(p['verdict'] for p in pairs),
        'rule_table': {rid: {'file': r['file'], 'terms': r['terms'], 'parsed': r['parsed'],
                             'shown': [lab for lab, _t in r['shown']]} for rid, r in doc.rules.items()},
    }
    rep['seconds'] = round(time.perf_counter() - t0, 3)
    return rep


def _count(it):
    out = {}
    for x in it:
        out[x] = out.get(x, 0) + 1
    return out


def summary_text(rep):
    lines = [f'{rep["doc"]} ({rep["format"]}): {rep["rules"]} rules, {rep["declared_terms"]} declared terms; '
             f'{rep["visibility"]}' + ('' if rep['visibility'] == 'COUNTED' else
                                       ' (narrow default surface assumed; pairs carried on it are CARRIED-ASSUMED)')]
    if rep['problems']:
        lines.append('  problems: ' + '; '.join(f'{c} {p}' for c, p in rep['problems']))
    if rep['unparsed']:
        u = rep['unparsed'][0]
        lines.append(f'  UNPARSED rules: {len(rep["unparsed"])} ({", ".join(x["rule"] for x in rep["unparsed"][:8])}'
                     f'{" ..." if len(rep["unparsed"]) > 8 else ""}); dependencies {u["dependencies"]}; candidates '
                     f'(terms no parsed rule reaches): {len(u["candidates"])}')
    if rep['oversize']:
        lines.append(f'  OVERSIZE rules (prompt lower bound > ARG_LIMIT {ARG_LIMIT}): {", ".join(rep["oversize"])}')
    k = rep['known']
    if k:
        hits = sum(1 for x in k if x['hit'])
        lines.append(f'  known cases: {len(k)} pairs, {hits} detected not carried, {len(k) - hits} not')
        for x in k:
            if not x['hit']:
                lines.append(f'    MISS {x["case"]} {x["rule"]} {x["term"]}: {x["verdict"]}, reach {x["reach"]}')
    if rep['visibility'] == 'COUNTED':
        lines.append(f'  marker grep not run: coverage {rep["coverage"]}; max prompt lower bound '
                     f'{rep["max_prompt_bytes_lower_bound"]} bytes (ARG_LIMIT {ARG_LIMIT})')
    else:
        lines.append(f'  marker hits {rep["marker_hits"]} ({rep["unlinked_marker_hits"]} link no term); pairs '
                     f'{len(rep["pairs"])}: ' + ', '.join(f'{v} {n}' for v, n in sorted(rep['pairs_by_verdict'].items())))
    lines.append(f'  run time {rep["seconds"]} s')
    return '\n'.join(lines)


def load_known(path):
    data = _json(Path(path).read_text(encoding='utf-8')) if Path(path).is_file() else None
    return (data or {}).get('cases') or []


def select_documents(paths, tree=None, docs=None):
    """Documents an edit to these paths can change (section 7 "Selection"): every document whose inputs or sources hold
    a path, and all of them when a path is the checker, its pinned counter code or the known-case fixture."""
    docs = list(docs or DOCS)
    paths = [p.strip('/') for p in paths]
    if any(p in SELECT_ALL for p in paths):
        return sorted(docs)
    tree = tree or FsTree(ROOT)
    cache = tree.__dict__.setdefault('_select_reads', {})
    out = set()
    for name in docs:
        if name not in cache:
            doc = build_doc(name, tree)
            cache[name] = set(doc.inputs) | set(doc.sources) | {DOCS[name]['dir']}
        reads = cache[name]
        for p in paths:
            if p in reads or any(p.startswith(r.rstrip('/') + '/') for r in reads if r == DOCS[name]['dir']):
                out.add(name)
    return sorted(out)


def run_known_trees(fixture, repo=None):
    """T1 raw detection: every known case evaluated at the tree the fixture records for it (the pin, or an FSF/RSP
    repair's merge base), read by blob id (content-addressed)."""
    t0 = time.perf_counter()
    out = []
    for tid, t in fixture['trees'].items():
        tree = MemTree(t['files'], key=f'blobs:{tid}', repo=repo)
        for name in t['docs']:
            cases = [k for k in fixture['cases'] if k['tree'] == tid and k['doc'] == name]
            for r in evaluate_known(build_doc(name, tree), cases):
                out.append(dict(r, doc=name, tree=tid, commit=t['commit']))
    return {'pairs': len(out), 'hits': sum(1 for x in out if x['hit']),
            'misses': [x for x in out if not x['hit']], 'results': out,
            'seconds': round(time.perf_counter() - t0, 3)}


def run(tree, names, known):
    t0 = time.perf_counter()
    reps = {n: run_document(n, tree, known) for n in names}
    allk = [x for r in reps.values() for x in r['known']]
    return {
        'tool': TOOL_VERSION, 'mode': 'report', 'tree': tree.describe(), 'arg_limit': ARG_LIMIT,
        'marker_version': MARKER_VERSION, 'out_of_scope': OUT_OF_SCOPE,
        'unscoped_use_cases': unscoped_use_cases(tree),
        'known_summary': {'pairs': len(allk), 'hits': sum(1 for x in allk if x['hit']),
                          'misses': [{k: x[k] for k in ('case', 'rule', 'term', 'verdict', 'reach')}
                                     for x in allk if not x['hit']]},
        'documents': reps, 'seconds': round(time.perf_counter() - t0, 3),
    }


def lexical_recall_trees(fixture, repo=None):
    out = []
    for tid, t in fixture['trees'].items():
        tree = MemTree(t['files'], key=f'blobs:{tid}', repo=repo)
        for name in t['docs']:
            cases = [k for k in fixture['cases'] if k['tree'] == tid and k['doc'] == name]
            out += lexical_recall(build_doc(name, tree), cases)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--root', default=str(ROOT), help='VE checkout to read (default: this one)')
    ap.add_argument('--ref', help='read this commit of --root with git instead of the working tree')
    ap.add_argument('--doc', action='append', help='a document (repeatable; default all 15)')
    ap.add_argument('--known', default=None, help=f'known-case fixture (default {KNOWN_DEFAULT} under --root)')
    ap.add_argument('--no-known', action='store_true')
    ap.add_argument('--json', help='write the machine-readable report here')
    ap.add_argument('--summary-dir', help='write one <doc>.txt summary per document here')
    ap.add_argument('--select', nargs='+', metavar='PATH', help='print the documents an edit to these paths selects')
    ap.add_argument('--known-trees', action='store_true',
                    help='T1: evaluate each known case at the tree the fixture records for it (by blob id)')
    a = ap.parse_args(argv)
    for d in a.doc or ():
        if d not in DOCS:
            ap.error(f'unknown document {d!r} (known: {", ".join(DOCS)})')
    if a.known_trees:
        fx = _json(Path(a.known or os.path.join(a.root, KNOWN_DEFAULT)).read_text(encoding='utf-8')) or {}
        res = run_known_trees(fx, repo=a.root)
        if a.json:
            Path(a.json).write_text(json.dumps(res, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
        for x in res['misses']:
            print(f'MISS {x["case"]} ({x["tree"]}): {x["verdict"]}, reach {x["reach"]}')
        print(f'known cases at their recorded trees: {res["pairs"]} pairs, {res["hits"]} detected not carried, '
              f'{len(res["misses"])} missed; {res["seconds"]} s; report mode: exit 0')
        return 0
    tree = GitTree(a.root, a.ref) if a.ref else FsTree(a.root)
    if a.select:
        for name in select_documents(a.select, tree, a.doc):
            print(name)
        return 0
    known = [] if a.no_known else load_known(a.known or os.path.join(a.root, KNOWN_DEFAULT))
    rep = run(tree, a.doc or list(DOCS), known)
    if a.json:
        Path(a.json).write_text(json.dumps(rep, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    if a.summary_dir:
        Path(a.summary_dir).mkdir(parents=True, exist_ok=True)
        for n, r in rep['documents'].items():
            (Path(a.summary_dir) / f'{n}.txt').write_text(summary_text(r) + '\n', encoding='utf-8')
    for r in rep['documents'].values():
        print(summary_text(r))
    if rep['unscoped_use_cases']:
        print(f'unscoped use cases (no adapter and no out-of-scope reason; reported, never failed): '
              f'{", ".join(rep["unscoped_use_cases"])}')
    ks = rep['known_summary']
    print(f'known cases: {ks["pairs"]} pairs, {ks["hits"]} detected not carried, {len(ks["misses"])} missed; '
          f'total {rep["seconds"]} s; report mode: exit 0')
    return 0


if __name__ == '__main__':
    sys.exit(main())
