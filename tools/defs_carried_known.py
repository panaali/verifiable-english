#!/usr/bin/env python3
"""Build the known-case fixture of tools/defs_carried.py from the definitions-carried audit (defs-carried-gate-stage1-1119).

Inputs (all read-only): the audit's candidate rows (rows-<doc>.tsv, one line per row) and two of its pages
(udhr-pilot.md for the rowless finding D7, claude-constitution-pilot.md for that page's rule numbers R1-R19), a copy of
which is committed under tests/data/defs_carried/audit/; the VE repository at the audit's pin; and the FSF/RSP repair
branches (their legend or code appends name the predicate and the source passage of each repair).

Mechanical only. Each row becomes one case per (rule, term): wildcards (`R5b.*`), ranges (`R14.1-R14.3`), "all 49",
`claims.ve:5` and the pilot's R<n> are resolved against the pin; the term is the row's carrier key when the pin declares
it, else the identifier the row's term column names, else the term of the rule that the lexical matcher links to the
row's defined phrase. A quote that is not in the source as written (under source_norm) is re-cut: its maximal runs of at
least 3 words that the source holds are cut from the source verbatim, adjacent runs joined, every other word dropped,
and the change listed in the fixture's `recut` list. Nothing here judges meaning.

Usage: python3 tools/defs_carried_known.py --audit DIR --repo VE_REPO [--pin 3d6b459df4] --out FILE
"""
from __future__ import annotations

import argparse
import ast
import csv
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import defs_carried as dc  # noqa: E402

PIN = '3d6b459df4'
REPAIRS = [   # (case id, branch, document): the 9 FSF/RSP repair rows the design lists (F1-F3, F5-F9, R1)
    ('F1', 'feature/fsf-repair-f1-leveldefs-1119', 'safety-framework'),
    ('F2', 'feature/fsf-repair-f2-glossary-1119', 'safety-framework'),
    ('F3', 'feature/fsf-repair-f3-safetycase-1119', 'safety-framework'),
    ('F5', 'feature/fsf-repair-f5-lowrisk-1119', 'safety-framework'),
    ('F6', 'feature/fsf-repair-f6-sl2plus-1119', 'safety-framework'),
    ('F7', 'feature/fsf-repair-f7-govadequacy-1119', 'safety-framework'),
    ('F8', 'feature/fsf-repair-f8-disclosure-1119', 'safety-framework'),
    ('F9', 'feature/fsf-repair-f9-mcca-1119', 'safety-framework'),
    ('R1', 'feature/rsp-repair-r1-catastrophic-1119', 'anthropic-rsp'),
]
MIN_RUN = 3          # words: a shorter run shared with the source is not a cut (a wrapper's "Rule 1" is not a quote)
MIN_REPAIR_RUN = 10  # words: a repair append's source passage (a shorter shared run is a label or a citation)


def git(repo, *args):
    x = subprocess.run(['git', '-C', str(repo), *args], capture_output=True, text=True)
    if x.returncode != 0:
        raise SystemExit(f'git {" ".join(args)}: {x.stderr.strip()}')
    return x.stdout.strip()


# ------------------------------------------------------------------------------------------------------- re-cutting ---
def raw_tokens(text):
    """[(normalised word, start, end)] of a raw text; the same tokenizer reads quotes and sources."""
    return [(dc.counter.omit_norm(m.group(0)), m.start(), m.end()) for m in re.finditer(r'[^\W_]+', text)]


def _longest(q, c, pos):
    best, at_q, at_c, prev = 0, 0, 0, {}
    for i, t in enumerate(q):
        cur = {}
        for j in pos.get(t, ()):
            n = prev.get(j - 1, 0) + 1
            cur[j] = n
            if n > best:
                best, at_q, at_c = n, i - n + 1, j - n + 1
        prev = cur
    return best, at_q, at_c


def recut(quote, sources, prefer=(), min_run=MIN_RUN):
    """(passages, change): passages = [{'file', 'text'}] cut verbatim from the source; change = None when the quote is in
    the source as written (under source_norm), else a dict naming what the cut dropped or split."""
    nq = dc.source_norm(quote)
    order = sorted(sources, key=lambda p: (p not in prefer, p))
    for p in order:
        if nq and nq in dc.source_norm(sources[p]):
            return [{'file': p, 'text': quote}], None
    qt = raw_tokens(quote)
    q = [t for t, _a, _b in qt]
    st = {p: raw_tokens(sources[p]) for p in order}
    pos = {p: {} for p in order}
    for p in order:
        for j, (t, _a, _b) in enumerate(st[p]):
            pos[p].setdefault(t, []).append(j)
    runs = []

    def solve(lo, hi):
        if hi - lo < min_run:
            return
        best = (0, 0, 0, None)
        for p in order:
            n, aq, ac = _longest(q[lo:hi], [t for t, _a, _b in st[p]], pos[p])
            if n > best[0]:
                best = (n, aq + lo, ac, p)
        n, aq, ac, p = best
        if n < min_run:
            return
        runs.append((aq, n, p, ac))
        solve(lo, aq)
        solve(aq + n, hi)
    solve(0, len(q))
    runs.sort()
    merged = []
    for aq, n, p, ac in runs:
        if merged and merged[-1][2] == p and merged[-1][3] + merged[-1][1] == ac:
            m = merged[-1]
            merged[-1] = (m[0], m[1] + n, p, m[3])
        else:
            merged.append((aq, n, p, ac))
    passages, kept = [], 0
    for aq, n, p, ac in merged:
        toks = st[p]
        passages.append({'file': p, 'text': _span(sources[p], toks[ac][1], toks[ac + n - 1][2])})
        kept += n
    dropped = []
    covered = set()
    for aq, n, _p, _ac in merged:
        covered |= set(range(aq, aq + n))
    i = 0
    while i < len(qt):
        if i not in covered:
            j = i
            while j < len(qt) and j not in covered:
                j += 1
            dropped.append(quote[qt[i][1]:qt[j - 1][2]])
            i = j
        else:
            i += 1
    change = {'quote': quote, 'passages': [x['text'] for x in passages], 'dropped_words': dropped,
              'words_kept': kept, 'words_total': len(q),
              'kind': ('not found' if not passages else 'split into %d passages' % len(passages)
                       if len(passages) > 1 else 'cut to the source passage')}
    return passages, change


# --------------------------------------------------------------------------------------------------- the audit rows ---
def _span(text, a, b):
    """text[a:b] widened over the opening and closing quote, bracket and emphasis marks next to it (at most 3 each
    side), with a leading header line of at most 3 words and a leading list number dropped: the verbatim passage."""
    a0 = a
    while a > 0 and text[a - 1] in '“"‘\'*_([' and a0 - a < 3:
        a -= 1
    b0 = b
    while b < len(text) and text[b] in '.,;:!?”’")]*_' and b - b0 < 3:
        b += 1
    out = text[a:b]
    lines = out.split('\n')
    while len(lines) > 1 and len(re.findall(r'[^\W_]+', lines[0])) <= 3 and not re.search(r'[.;:]\s*$', lines[0]):
        lines.pop(0)
    out = '\n'.join(lines).strip()
    return re.sub(r'^(?:\d+\.|\(\d+\))\s+', '', out)


def read_rows(audit):
    rows = []
    for f in sorted(Path(audit).glob('rows-*.tsv')):
        with open(f, encoding='utf-8', newline='') as fh:
            rows += list(csv.DictReader(fh, delimiter='\t', quoting=csv.QUOTE_NONE))
    return rows


def pilot_aliases(page):
    """R<n> -> unit id, from the pilot page's 'Rules (unit id = rule)' list ('R10-R16 u0165.s01-s07' expanded)."""
    text = Path(page).read_text(encoding='utf-8')
    sec = text.split('**Rules (unit id = rule).**', 1)[1].split('**Source definitions inventory**', 1)[0]
    out = {}
    for a, b, unit in re.findall(r'\bR(\d+)(?:-R(\d+))?\s+(u\S+)', sec):
        unit = unit.rstrip(',.:;')
        if b:
            stem, rng = unit.rsplit('.', 1)
            first = int(re.match(r's(\d+)', rng).group(1))
            for k in range(int(a), int(b) + 1):
                out[f'R{k}'] = f'{stem}.s{first + k - int(a):02d}'
        else:
            out[f'R{a}'] = unit
    return out


def expand_rules(spec, doc, aliases):
    ids = list(doc.rules)
    spec = spec.strip()
    if re.match(r'all \d+\b', spec):
        return ids
    out = []
    for tok in re.split(r'[,;]\s*', spec):
        tok = tok.strip()
        if not tok:
            continue
        m = re.fullmatch(r'claims\.ve:(\d+)', tok)
        if m:
            out.append(f'C{m.group(1)}')
        elif tok.endswith('.*'):
            out += [i for i in ids if i.startswith(tok[:-1])]
        elif re.fullmatch(r'R\d+(?:\.\d+)?-R\d+(?:\.\d+)?', tok):
            a, b = tok.split('-')
            pa, na = a.rsplit('.', 1) if '.' in a else ('', a[1:])
            _pb, nb = b.rsplit('.', 1) if '.' in b else ('', b[1:])
            out += [f'{pa}.{k}' if pa else f'R{k}' for k in range(int(na), int(nb) + 1)]
        elif doc.name == 'claude-constitution-pilot' and tok in aliases:
            out.append(aliases[tok])
        else:
            out.append(tok)
    return list(dict.fromkeys(out))


def carrier_keys(row, doc):
    keys = []
    for k in re.split(r'[,;]\s*', row['carrier_key']):
        k = re.sub(r'^(sort|constant|open_terms|predicate):', '', k.strip())
        if k in doc.declared:
            keys.append(k)
    for k in re.findall(r'\b([a-z][a-z0-9]*(?:_[a-z0-9]+)+|[a-z]{2,})\b', re.sub(r'^[^(]*', '', row['term'])):
        if k in doc.declared and k not in keys:
            keys.append(k)
    return keys


def row_phrases(term_col):
    """Defined phrases of a row's term column: the text outside parentheses, split on ' / ', ';' and ', '."""
    text = term_col
    while re.search(r'\([^()]*\)', text):
        text = re.sub(r'\([^()]*\)', ' ', text)
    out = []
    for p in re.split(r'\s/\s|;|,', text):
        p = re.sub(r'\s+', ' ', p.replace('(', ' ').replace(')', ' ')).strip()
        if p and p not in out:
            out.append(p)
    return out


def choose_term(keys, rule, doc, phrases):
    if rule is not None:
        for k in keys:
            if k in rule['terms']:
                return k, 'carrier key used by the rule'
    if keys:
        return keys[0], 'carrier key (the rule does not use it at the pin)'
    if rule is not None:
        idx = dc.lexical_index(doc)
        for ph in phrases:
            toks = [dc.fold(t) for t in dc.tokens(dc.source_norm(ph))]
            for term, _rid, _w in dc.lexical_match(idx, toks):
                if term and term in rule['terms']:
                    return term, f'lexical match of {ph!r}'
    return None, 'no declared term'


def source_files(loc):
    return [m for m in re.findall(r'([A-Za-z0-9_./-]+\.(?:md|txt))', loc)]


def prefer_paths(doc, loc):
    names = source_files(loc)
    out = []
    for p in doc.sources:
        if any(p.endswith('/' + n.split('/')[-1]) for n in names):
            out.append(p)
    return out


# -------------------------------------------------------------------------------------------------------- D7 (UDHR) ---
def d7_cases(page, doc):
    """The rowless UDHR finding D7: the table rows whose source-definition cell is D7; the passage is the Declaration's
    own rights, Articles 3-27, cut whole from the body (the page: 'The target is ... Articles 3-27')."""
    text = Path(page).read_text(encoding='utf-8')
    body = next(iter(doc.sources.values()))
    m = re.search(r'(?m)^(?:#+\s*)?Article 3\b.*?(?=^(?:#+\s*)?Article 28\b)', body, re.S)
    passage = m.group(0).strip() if m else None
    cases = []
    for line in text.split('\n'):
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) >= 4 and cells[2].startswith('D7'):
            rule = re.match(r'(u\d+[a-z]?)', cells[0]).group(1)
            for t in re.split(r';\s*', cells[1]):
                t = t.strip()
                if t:
                    cases.append((rule, t))
    return cases, passage


# ----------------------------------------------------------------------------------------------- FSF / RSP repairs ---
def repair_base(repo, branch):
    tip = git(repo, 'rev-parse', branch)
    merged = subprocess.run(['git', '-C', str(repo), 'merge-base', '--is-ancestor', tip, 'main']).returncode == 0
    if merged:
        for line in git(repo, 'log', '--first-parent', '--merges', '--format=%H %P', 'main').split('\n'):
            parts = line.split()
            if len(parts) >= 3 and parts[2] == tip:
                return parts[1], tip, parts[0]
        raise SystemExit(f'{branch}: merged, but no first-parent merge of its tip found on main')
    return git(repo, 'merge-base', tip, 'main'), tip, None


def _source_runs(added, src_tokens, pos, min_run, gap=3):
    """[(query token index, query token count, source token index, source token count)]: the maximal runs of the text
    that the source holds, runs that are near each other in both the text and the source (at most `gap` words apart in
    each) joined into one span, and spans shorter than min_run words dropped."""
    qt = raw_tokens(added)
    q = [t for t, _a, _b in qt]
    out = []

    def solve(lo, hi):
        if hi - lo < 3:
            return
        n, aq, ac = _longest(q[lo:hi], [t for t, _a, _b in src_tokens], pos)
        if n < 3:
            return
        out.append((aq + lo, n, ac, n))
        solve(lo, aq + lo)
        solve(aq + lo + n, hi)
    solve(0, len(q))
    out.sort()
    merged = []
    for aq, n, ac, m in out:
        if merged:
            pq, pn, pc, pm = merged[-1]
            if 0 <= aq - (pq + pn) <= gap and 0 <= ac - (pc + pm) <= gap:
                merged[-1] = (pq, aq + n - pq, pc, ac + m - pc)
                continue
        merged.append((aq, n, ac, m))
    return [(aq, n, ac, m, qt[aq][1]) for aq, n, ac, m in merged if m >= min_run]


def repair_cases(repo, rid, branch, docname, src_text):
    base, tip, merge = repair_base(repo, branch)
    case = dc.DOCS[docname]['case']
    st = raw_tokens(src_text)
    pos = {}
    for j, (t, _a, _b) in enumerate(st):
        pos.setdefault(t, []).append(j)

    def cut(ac, n):
        return _span(src_text, st[ac][1], st[ac + n - 1][2])
    out = []
    old = dc._vocab(dc._json(git(repo, 'show', f'{base}:usecases/{case}/environment.d1.json')))['predicates']
    new = dc._vocab(dc._json(git(repo, 'show', f'{tip}:usecases/{case}/environment.d1.json')))['predicates']
    for k in sorted(new):
        nd, od = new[k].get('description') or '', (old.get(k) or {}).get('description') or ''
        if nd == od:
            continue
        for _aq, _n, ac, m, at in _source_runs(nd, st, pos, MIN_REPAIR_RUN):
            p = cut(ac, m)
            if _in_tokens(p, od):
                continue
            if k in old:
                out.append({'term': k, 'term_kind': 'predicate', 'passage': p})
            else:   # a new predicate (F1 `defined`): each passage defines the constant the legend names just before it
                names = list(re.finditer(r'\b([a-z][a-z0-9]*_[a-z0-9_]+) is\b', nd[:at]))
                out.append({'term': names[-1].group(1) if names else None, 'term_kind': 'constant', 'passage': p})
    for n in dc.counter.OMIT_CODE.get(case, ()):
        a = subprocess.run(['git', '-C', str(repo), 'show', f'{base}:usecases/{case}/{n}'], capture_output=True, text=True)
        b = subprocess.run(['git', '-C', str(repo), 'show', f'{tip}:usecases/{case}/{n}'], capture_output=True, text=True)
        if a.returncode or b.returncode or a.stdout == b.stdout:
            continue
        olds, news = _dict_strings(a.stdout), _dict_strings(b.stdout)
        for key, val in sorted(news.items()):
            if olds.get(key) == val:
                continue
            for _aq, _nn, ac, m, _at in _source_runs(val, st, pos, MIN_REPAIR_RUN):
                p = cut(ac, m)
                if not _in_tokens(p, olds.get(key) or ''):
                    out.append({'term': key, 'term_kind': 'code_name', 'passage': p, 'rule': 'D2D3'})
    return {'id': rid, 'branch': branch, 'tip': tip, 'base': base, 'merge': merge}, out


def _lead_phrases(passage):
    """A repair passage's defined phrases: its lead-in label ("Safety Cases: are ...") and acronyms in parentheses."""
    out = []
    m = re.match(r'\W*([^:.;]{2,60}?)\s*:', passage)
    if m and len(m.group(1).split()) <= 6:
        out.append(m.group(1).strip(' "“”*'))
    out += [a for a in re.findall(r'\(([A-Z][A-Z0-9+]{1,8})\)', passage) if a not in out]
    return out


def _in_tokens(passage, text):
    """Whether the passage's words occur contiguously in text (a quote the legend already held before the repair)."""
    p = [t for t, _a, _b in raw_tokens(passage)]
    t = [x for x, _a, _b in raw_tokens(text)]
    return bool(p) and any(t[i:i + len(p)] == p for i in range(len(t) - len(p) + 1))


def _dict_strings(src):
    """{dict key: all string constants of its value joined} for every dict literal of a module."""
    out = {}
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return out
    for nd in ast.walk(tree):
        if isinstance(nd, ast.Dict):
            for k, v in zip(nd.keys, nd.values):
                if isinstance(k, ast.Constant) and isinstance(k.value, str):
                    s = ' '.join(x.value for x in ast.walk(v) if isinstance(x, ast.Constant) and isinstance(x.value, str))
                    if s:
                        out[k.value] = s
    return out


def tree_blobs(repo, commit, paths):
    out = {}
    for p in sorted(paths):
        x = subprocess.run(['git', '-C', str(repo), 'rev-parse', '--verify', '-q', f'{commit}:{p}'],
                           capture_output=True, text=True)
        if x.returncode == 0:
            out[p] = x.stdout.strip()
    return out


def all_paths(doc, tree):
    """Every file the adapter can read for this document at this tree (its directory's files and its sources)."""
    paths = set(doc.inputs) | {p for p in doc.sources if not p.startswith('~/')}
    d = dc.DOCS[doc.name]['dir']
    if isinstance(tree, dc.GitTree):
        paths |= {p for p in tree._paths if p.startswith(d + '/') and (
            p.endswith(('.ve', '.json', '.py', '.md', '.txt')) and '/answers/' not in p and '/reports/' not in p)}
    return paths


def build(audit, repo, pin, src_override=None):
    pin_tree = dc.GitTree(repo, pin)
    rows = read_rows(audit)
    aliases = pilot_aliases(Path(audit) / 'claude-constitution-pilot.md')
    docs = {}

    def doc_at(name, tree):
        if (name, tree.key) not in docs:
            docs[(name, tree.key)] = dc.build_doc(name, tree)
        return docs[(name, tree.key)]
    cases, recuts, trees = [], [], {}
    for row in rows:
        doc = doc_at(row['doc'], pin_tree)
        rules = expand_rules(row['rules'], doc, aliases)
        keys = carrier_keys(row, doc)
        phrases = row_phrases(row['term'])
        passages, change = recut(row['quote'], doc.sources, prefer_paths(doc, row['source_loc']))
        if change:
            recuts.append(dict(change, row=row['id'], doc=row['doc'], source_loc=row['source_loc']))
        for rid in rules:
            term, why = choose_term(keys, doc.rules.get(rid), doc, phrases)
            cases.append({'case': f'{row["id"]}:{rid}', 'row': row['id'], 'doc': row['doc'], 'prio': row['prio'],
                          'kind': row['prio'], 'rule': rid, 'term': term, 'term_from': why, 'terms_listed': keys,
                          'phrases': phrases, 'audit_verdict': row['verdict'], 'entry': row['source_loc'],
                          'passages': passages, 'tree': 'pin'})
        trees.setdefault('pin', {'commit': pin_tree.commit, 'docs': set()})['docs'].add(row['doc'])
    udoc = doc_at('udhr-pilot', pin_tree)
    d7, d7_passage = d7_cases(Path(audit) / 'udhr-pilot.md', udoc)
    for rid, term in d7:
        cases.append({'case': f'udhr-D7:{rid}:{term}', 'row': None, 'doc': 'udhr-pilot', 'prio': 'rowless', 'kind': 'D7',
                      'rule': rid, 'term': term if term in udoc.declared else None,
                      'term_from': 'audit page table (D7)', 'terms_listed': [term],
                      'phrases': ['rights and freedoms set forth in this Declaration'],
                      'audit_verdict': 'NOT CARRIED', 'entry': 'udhr-pilot.md D7 (Articles 2, 29(3), 30 -> Articles 3-27)',
                      'passages': [{'file': next(iter(udoc.sources)), 'text': d7_passage}], 'tree': 'pin'})
    trees['pin']['docs'].add('udhr-pilot')
    repairs = []
    for rid, branch, docname in REPAIRS:
        case = dc.DOCS[docname]['case']
        ps = json.loads(git(repo, 'show', f'{pin}:usecases/pinned_sources.json'))['sources'][case]
        src = Path((src_override or {}).get(case) or (Path.home() / ps['path'])).read_text(encoding='utf-8')
        info, found = repair_cases(repo, rid, branch, docname, src)
        repairs.append(dict(info, passages=len(found)))
        btree = dc.GitTree(repo, info['base'])
        doc = doc_at(docname, btree)
        tid = f'base-{rid}'
        trees[tid] = {'commit': info['base'], 'docs': {docname}}
        for n, f in enumerate(found, 1):
            term = f['term']
            if f.get('rule'):
                rules = [f['rule']]
            elif f['term_kind'] == 'constant':
                rules = [r for r, x in doc.rules.items() if term and f'"{term}"' in x['text']]
            else:
                rules = [r for r, x in doc.rules.items() if term in x['terms']]
            for r in rules:
                cases.append({'case': f'{rid}:{r}:{term}:p{n}', 'row': info['branch'].split('/')[-1], 'doc': docname,
                              'prio': 'repair', 'kind': rid, 'rule': r, 'term': term,
                              'term_from': f'{f["term_kind"]} the repair appends to',
                              'terms_listed': [term], 'phrases': _lead_phrases(f['passage']),
                              'audit_verdict': 'TEXT (repair row)',
                              'entry': f'{case} pinned source', 'passages': [{'file': f'~/{ps["path"]}',
                                                                            'text': f['passage']}], 'tree': tid})
    for tid, t in trees.items():
        tr = pin_tree if tid == 'pin' else dc.GitTree(repo, t['commit'])
        paths = set()
        for name in t['docs']:
            paths |= all_paths(doc_at(name, tr), tr)
        t['files'] = {p: {'blob': b} for p, b in tree_blobs(repo, t['commit'], paths).items()}
        t['docs'] = sorted(t['docs'])
    ids = [c['case'] for c in cases]
    assert len(ids) == len(set(ids)), 'case ids are not unique'
    counts = {'rows': len(rows), 'rows_P1': sum(r['prio'] == 'P1' for r in rows),
              'rows_P2': sum(r['prio'] == 'P2' for r in rows), 'repairs': len(REPAIRS), 'd7_pairs': len(d7),
              'cases': len(cases), 'known_findings': sum(r['prio'] == 'P1' for r in rows) + len(REPAIRS),
              'recut_quotes': len(recuts)}
    return {'about': ('Known cases of the definitions-carried audit, one per (document, rule, term), built by '
                      'tools/defs_carried_known.py; do not edit by hand. The 61 known findings are the 52 P1 rows and '
                      'the 9 FSF/RSP repairs; the 20 P2 rows and the rowless UDHR D7 are included too.'),
            'pin': pin_tree.commit, 'counts': counts, 'repairs': repairs, 'recut': recuts, 'trees': trees,
            'cases': cases}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--audit', required=True)
    ap.add_argument('--repo', required=True)
    ap.add_argument('--pin', default=PIN)
    ap.add_argument('--out', required=True)
    a = ap.parse_args(argv)
    data = build(a.audit, a.repo, a.pin)
    Path(a.out).write_text(json.dumps(data, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    c = data['counts']
    print(f'{c["cases"]} cases from {c["rows"]} rows ({c["rows_P1"]} P1, {c["rows_P2"]} P2), {c["repairs"]} repairs, '
          f'{c["d7_pairs"]} D7 pairs; {c["recut_quotes"]} quotes re-cut')
    return 0


if __name__ == '__main__':
    sys.exit(main())
