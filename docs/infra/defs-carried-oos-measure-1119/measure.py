#!/usr/bin/env python3
"""Out-of-sample measurement of tools/defs_carried.py (defs-carried-oos-measure-1119): report only, 0 model calls.

The tool is read as a library and run through its own command line; nothing here changes what it computes.

  fixture  Build tests/data/defs_carried/oos_cases.json from the three audit row files copied verbatim under
           tests/data/defs_carried/oos_audit/ (PF, FSF, RSP; written at VE e53db4e8fc after the 61-case fixture).
           One case per (row, rule), the term and passages resolved mechanically at the rows' pin with the
           known-case builder's own functions (tools/defs_carried_known.py: rule wildcards, carrier keys, term choice,
           verbatim re-cut). A case whose (document, rule, term) is a key of tests/data/defs_carried/known_cases.json is
           in-sample: it is listed in `excluded_in_sample` and is not a case.
  recall   Tabulate the tool's answers on those cases from its own --json reports (one per tree): a case is a hit when
           the tool reaches it (reach `parsed` or `unparsed-rule`) and its verdict is below CARRIED-ASSUMED, the same
           definition as the in-sample T1 count; every other case is a miss, with its reason.
  draw     The false-alarm sample: every pair flag (verdict other than CARRIED / CARRIED-ASSUMED) of the tool's run over
           all documents, minus the known-case keys, drawn uniformly without replacement with a stated seed.
  packets  The judge's inputs: per document, the drawn flags (id, document, rule, term; never the tool's verdict), each
           flag's source passage and the rule's carrier surface (the reader-visible text the tool reads).
  tally    Count the judge's verdicts (CARRIED / NOT CARRIED / UNSURE) per flag; nothing is edited. With
           --definition-dir it also counts the supplementary pass (packets --question definition: does the passage
           define the term at all?), which the main question cannot see because it presents the passage as the
           definition.

Usage:
  python3 docs/infra/defs-carried-oos-measure-1119/measure.py fixture --repo . --pin e53db4e8fc --out FILE
  python3 docs/infra/defs-carried-oos-measure-1119/measure.py recall --fixture FILE --report LABEL=JSON ... --out FILE
  python3 docs/infra/defs-carried-oos-measure-1119/measure.py draw --report JSON --n 120 --seed S --out FILE
  python3 docs/infra/defs-carried-oos-measure-1119/measure.py packets --flags FILE --repo . --ref C --out-dir DIR
  python3 docs/infra/defs-carried-oos-measure-1119/measure.py tally --flags FILE --judge-dir DIR --out FILE
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import defs_carried as dc  # noqa: E402
import defs_carried_known as dk  # noqa: E402

OOS_AUDIT = 'tests/data/defs_carried/oos_audit'
KNOWN = 'tests/data/defs_carried/known_cases.json'
ROW_FILES = {  # copied file -> (document, the audit's original path under manage-agents)
    'rows-openai-preparedness.tsv': ('openai-preparedness', 'reviews/defs-carried-1119/rows-openai-preparedness.tsv'),
    'rows-safety-framework-x.tsv': ('safety-framework', 'reviews/defs-carried-1119/rows-safety-framework-x.tsv'),
    'rows-anthropic-rsp-x.tsv': ('anthropic-rsp', 'reviews/defs-carried-1119/rows-anthropic-rsp-x.tsv'),
}
IDENT = re.compile(r'[a-z][a-z0-9]*(?:_[a-z0-9]+)+')
VERDICTS = ('CARRIED', 'NOT CARRIED', 'UNSURE')


def wilson(k, n, z=1.959964):
    """The 95% Wilson score interval of k successes in n trials, as (low, high); (None, None) when n is 0."""
    if n == 0:
        return None, None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def known_keys(path=ROOT / KNOWN):
    """The matching key of the known-case fixture: every (document, rule, term) it holds (all 389 cases: the 61 known
    findings, the P2 rows and D7; the wider set, so that nothing the tool was built against counts as out of sample)."""
    cases = json.loads(Path(path).read_text(encoding='utf-8'))['cases']
    return {(c['doc'], c['rule'], c['term']) for c in cases}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# --------------------------------------------------------------------------------------------------------- fixture ---
def read_rows(audit):
    out = []
    for name in ROW_FILES:
        with open(Path(audit) / name, encoding='utf-8', newline='') as fh:
            out += [dict(r, _file=name) for r in csv.DictReader(fh, delimiter='\t', quoting=csv.QUOTE_NONE)]
    return out


def rule_tokens(spec):
    """The rows' rules column: ids separated by commas or spaces (PF/FSF/RSP rows use both)."""
    return [t for t in re.split(r'[,;\s]+', spec.strip()) if t]


def row_keys(row, doc):
    """Carrier keys of a row: identifiers written inside the carrier_key cell (e.g. `stage0.py harms["harm_of_x"]`,
    `(R5: plans_in_place, rows T1)`) that the pin declares, then the known-case builder's own carrier_keys."""
    keys = [k for k in IDENT.findall(row['carrier_key']) if k in doc.declared]
    for k in dk.carrier_keys(row, doc):
        if k not in keys:
            keys.append(k)
    return keys


def build_fixture(repo, pin, audit):
    tree = dc.GitTree(repo, pin)
    known = known_keys()
    docs, cases, excluded, recuts, wild = {}, [], [], [], []
    rows = read_rows(audit)
    for row in rows:
        if row['doc'] not in docs:
            docs[row['doc']] = dc.build_doc(row['doc'], tree)
        doc = docs[row['doc']]
        rules = []
        for tok in rule_tokens(row['rules']):
            got = dk.expand_rules(tok, doc, {})
            if got != [tok]:
                wild.append({'row': row['id'], 'token': tok, 'resolved': got})
            rules += [r for r in got if r not in rules]
        keys = row_keys(row, doc)
        phrases = dk.row_phrases(row['term'])
        passages, change = dk.recut(row['quote'], doc.sources, dk.prefer_paths(doc, row['source_loc']))
        if change:
            recuts.append(dict(change, row=row['id'], doc=row['doc'], source_loc=row['source_loc']))
        for rid in rules:
            term, why = dk.choose_term(keys, doc.rules.get(rid), doc, phrases)
            case = {'case': f'{row["id"]}:{rid}', 'row': row['id'], 'doc': row['doc'], 'prio': row['prio'],
                    'kind': 'OOS', 'rule': rid, 'term': term, 'term_from': why, 'terms_listed': keys,
                    'phrases': phrases, 'audit_verdict': row['verdict'], 'cover': row['cover'],
                    'entry': row['source_loc'], 'passages': passages, 'tree': 'rows-pin'}
            if (row['doc'], rid, term) in known:
                excluded.append({'case': case['case'], 'doc': row['doc'], 'rule': rid, 'term': term,
                                 'reason': 'its (document, rule, term) is a known case'})
            else:
                cases.append(case)
    oos_rows = sorted({c['row'] for c in cases})
    return {
        'about': ('Out-of-sample cases of tools/defs_carried.py (defs-carried-oos-measure-1119): the PF, FSF and RSP '
                  'audit rows written after tests/data/defs_carried/known_cases.json, one case per (row, rule), minus '
                  'every (document, rule, term) that fixture holds. Built by docs/infra/defs-carried-oos-measure-1119/'
                  'measure.py fixture; do not edit by hand. Mechanical only: the term, the rules and the verbatim '
                  're-cuts use tools/defs_carried_known.py.'),
        'pin': tree.commit,
        'matching_key': ['doc', 'rule', 'term'],
        'row_files': {n: {'doc': d, 'origin': f'manage-agents {o}', 'sha256': sha256(Path(audit) / n)}
                      for n, (d, o) in ROW_FILES.items()},
        'counts': {'rows': len(rows), 'rows_with_oos_cases': len(oos_rows),
                   'rows_all_in_sample': len({r['id'] for r in rows}) - len(oos_rows),
                   'pairs': len(cases) + len(excluded), 'cases': len(cases), 'excluded_in_sample': len(excluded),
                   'distinct_keys': len({(c['doc'], c['rule'], c['term']) for c in cases}),
                   'wildcards_resolved': len(wild), 'recut_quotes': len(recuts),
                   'by_doc': {d: sum(1 for c in cases if c['doc'] == d) for d in sorted(docs)}},
        'wildcards': wild,
        'recut': recuts,
        'excluded_in_sample': excluded,
        'cases': cases,
    }


# ---------------------------------------------------------------------------------------------------------- recall ---
def tabulate_recall(fixture, report):
    """Per case: hit or miss at one tree, from the tool's own --json report run with --known <fixture>."""
    res = {}
    for name, d in report['documents'].items():
        for k in d['known']:
            res[k['case']] = k
    per = []
    for c in fixture['cases']:
        k = res.get(c['case'])
        if k is None:
            per.append({'case': c['case'], 'row': c['row'], 'doc': c['doc'], 'rule': c['rule'], 'term': c['term'],
                        'hit': False, 'reach': 'not in the report', 'verdict': None, 'reason': 'not in the report'})
            continue
        # The tool's own `hit` is (verdict not passing and reached). A case with no passage gets verdict None, which the
        # tool's test counts as a hit; here a hit also needs a verdict, so a case the tool compared nothing for is a miss.
        hit = bool(k['hit']) and k['verdict'] is not None
        reason = None
        if not hit:
            if k['verdict'] is None:
                reason = 'no passage: the row quotes no source text (a pointer), the tool compares nothing'
            elif k['reach'] not in ('parsed', 'unparsed-rule'):
                reason = f'never reached: {k["reach"]}'
            else:
                reason = f'tool verdict {k["verdict"]}'
        per.append({'case': c['case'], 'row': c['row'], 'doc': c['doc'], 'rule': c['rule'], 'term': c['term'],
                    'hit': hit, 'tool_hit': k['hit'], 'reach': k['reach'], 'verdict': k['verdict'], 'reason': reason,
                    'verdict_below_carried': k['verdict'] is not None and k['verdict'] not in dc.PASSING,
                    'best_run': k['best_run'], 'tokens': k['tokens'], 'where': k['where']})
    rows = {}
    for p in per:
        rows.setdefault(p['row'], []).append(p)
    nh = sum(1 for p in per if p['hit'])
    rh = sum(1 for v in rows.values() if any(p['hit'] for p in v))
    vb = sum(1 for p in per if p['verdict_below_carried'])
    vr = sum(1 for v in rows.values() if any(p['verdict_below_carried'] for p in v))
    return {'tree': report['tree'], 'tool_seconds': report['seconds'],
            'cases': len(per), 'hits': nh, 'misses': len(per) - nh, 'recall_pairs_wilson95': wilson(nh, len(per)),
            'findings': len(rows), 'findings_detected': rh, 'recall_findings_wilson95': wilson(rh, len(rows)),
            'verdict_only': {'note': ('the passage verdict on the rule surface alone, reach ignored: not the recall '
                                      'definition, shown to separate the term-link misses from the verdict misses'),
                             'pairs_below_carried': vb, 'findings_with_one': vr},
            'tool_hit_count': sum(1 for p in per if p['tool_hit']),
            'by_doc': {d: {'cases': sum(1 for p in per if p['doc'] == d),
                           'hits': sum(1 for p in per if p['doc'] == d and p['hit']),
                           'findings': sum(1 for r, v in rows.items() if v[0]['doc'] == d),
                           'findings_detected': sum(1 for r, v in rows.items()
                                                    if v[0]['doc'] == d and any(p['hit'] for p in v))}
                       for d in sorted({p['doc'] for p in per})},
            'miss_reasons': _count(p['reason'] for p in per if not p['hit']),
            'verdicts': _count(p['verdict'] for p in per),
            'missed_findings': sorted(r for r, v in rows.items() if not any(p['hit'] for p in v)),
            'per_case': per}


def _count(it):
    out = {}
    for x in it:
        out[x] = out.get(x, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: (-kv[1], str(kv[0]))))


# ------------------------------------------------------------------------------------------------------------ draw ---
def flag_population(report, known):
    """Every pair flag of the run (the auto inventory; known-case rows are the tool's input, not its findings), minus
    the known-case keys. Document-level findings (VISIBILITY-UNESTABLISHED, UNPARSED) name no term and no passage."""
    pop = []
    for name, d in sorted(report['documents'].items()):
        ent = {e['id']: e for e in d['marker_entries']}
        for p in d['pairs']:
            if p['verdict'] in dc.PASSING or (name, p['rule'], p['term']) in known:
                continue
            e = ent[p['entry']]
            pop.append({'doc': name, 'entry': p['entry'], 'rule': p['rule'], 'term': p['term'],
                        'verdict': p['verdict'], 'phrase': p['phrase'], 'via': p['via'],
                        'source': f'{e["file"]}:{e["line"]}', 'marker': e['marker'], 'passage': e['passage'],
                        'best_run': p['best_run'], 'tokens': p['tokens']})
    return pop


def draw(report, n, seed, known):
    pop = flag_population(report, known)
    excluded = sum(1 for d in report['documents'].values() for p in d['pairs']
                   if p['verdict'] not in dc.PASSING) - len(pop)
    idx = sorted(random.Random(seed).sample(range(len(pop)), n))
    flags = [dict(pop[i], id=f'F{j + 1:03d}', population_index=i) for j, i in enumerate(idx)]
    return {'about': ('Flags drawn for the independent false-alarm judgement (defs-carried-oos-measure-1119): '
                      'uniform without replacement (random.Random(seed).sample over the population in its listed order).'),
            'tree': report['tree'], 'seed': seed, 'population': len(pop), 'excluded_known_keys': excluded,
            'drawn': n, 'by_doc': _count(f['doc'] for f in flags), 'by_verdict': _count(f['verdict'] for f in flags),
            'population_by_doc': _count(p['doc'] for p in pop), 'flags': flags}


# --------------------------------------------------------------------------------------------------------- packets ---
QUESTION = ('For each flag below, decide: is this term\'s definition (the source passage given for the flag) shown to '
            'the reader of the rule, in the rule\'s carrier surface (the reader-visible text listed for that rule)? '
            'Answer CARRIED, NOT CARRIED or UNSURE, with one line of evidence (quote the surface words that carry it, '
            'or name what is missing).')

FORMAT = ('Reply with exactly one line per flag and nothing else, in this form:\n'
          '<flag id> | <CARRIED or NOT CARRIED or UNSURE> | <one line of evidence>')


def packets(flags, repo, ref, per_packet=40):
    tree = dc.GitTree(repo, ref)
    by_doc = {}
    for f in flags['flags']:
        by_doc.setdefault(f['doc'], []).append(f)
    out = {}
    for name, fl in by_doc.items():
        doc = dc.build_doc(name, tree)
        for part in range(0, len(fl), per_packet):
            chunk = fl[part:part + per_packet]
            uses = {}
            for f in chunk:
                for lab, txt in doc.rules[f['rule']]['shown']:
                    uses.setdefault((lab, txt), set()).add(f['rule'])
            shared = {k: f'S{i + 1}' for i, k in enumerate(k for k, v in uses.items() if len(v) > 1)}
            lines = [f'Document: {name}', '', QUESTION, '', FORMAT, '',
                     'A rule\'s carrier surface is the list of texts under its name in RULE SURFACES; a shared text '
                     '(used by more than one rule here) is printed once under SHARED SURFACE TEXTS and named by its '
                     'id. Judge only from the texts given here.', '']
            if shared:
                lines.append('== SHARED SURFACE TEXTS ==')
                for (lab, txt), sid in shared.items():
                    lines += [f'--- {sid} ({lab}) ---', txt, '']
            lines.append('== RULE SURFACES ==')
            for rid in dict.fromkeys(f['rule'] for f in chunk):
                lines.append(f'--- rule {rid} ---')
                for lab, txt in doc.rules[rid]['shown']:
                    sid = shared.get((lab, txt))
                    lines.append(f'[{lab}] (see {sid})' if sid else f'[{lab}] {txt}')
                lines.append('')
            lines.append('== FLAGS ==')
            for f in chunk:
                lines += [f'{f["id"]} | rule {f["rule"]} | term {f["term"]} | source {f["source"]}',
                          f'  source passage: {f["passage"]}', '']
            key = f'{name}-{part // per_packet + 1}'
            out[key] = {'ids': [f['id'] for f in chunk], 'text': '\n'.join(lines) + '\n'}
    return out


# Supplementary pass (not the task's question; added because the main question presents each flag's passage as the
# term's definition, so it cannot count a flag whose passage defines nothing): does the passage define the term at all?
DEF_QUESTION = ('For each item below, decide: does the source passage state what the matched phrase means (a '
                'definition of it, whole or in part, including introducing an abbreviation for it), as opposed to only '
                'using it, mentioning it, amending another text\'s definition of it, or pointing to a definition '
                'elsewhere? Answer DEFINES, DOES NOT DEFINE or UNSURE, with one line of evidence.')
# Version 1 of this question asked about "the named term" and was answered against the VE identifier (a passage that
# defines a component phrase of the identifier was "DOES NOT DEFINE"); its replies are kept under
# judge/definition-v1-superseded/ and are not counted.
DEF_FORMAT = ('Reply with exactly one line per item and nothing else, in this form:\n'
              '<item id> | <DEFINES or DOES NOT DEFINE or UNSURE> | <one line of evidence>')


def def_packet(flags):
    lines = [DEF_QUESTION, '', DEF_FORMAT, '', 'Judge only from the texts given here.', '', '== ITEMS ==']
    for f in flags['flags']:
        lines += [f'{f["id"]} | document {f["doc"]} | matched phrase "{f["phrase"]}" | source {f["source"]}',
                  f'  source passage: {f["passage"]}', '']
    return {'definition-1': {'ids': [f['id'] for f in flags['flags']], 'text': '\n'.join(lines) + '\n'}}


# ----------------------------------------------------------------------------------------------------------- tally ---
LINE = re.compile(r'^\s*(F\d{3})\s*\|\s*(CARRIED|NOT CARRIED|UNSURE)\s*\|\s*(.*?)\s*$')
DEF_LINE = re.compile(r'^\s*(F\d{3})\s*\|\s*(DEFINES|DOES NOT DEFINE|UNSURE)\s*\|\s*(.*?)\s*$')


def parse_judge(text, line=LINE):
    """{flag id: (verdict, evidence)} from the judge's reply lines; a repeated id keeps its first line."""
    out = {}
    for ln in text.splitlines():
        m = line.match(ln.replace('`', '').strip('*- '))
        if m and m.group(1) not in out:
            out[m.group(1)] = (m.group(2), m.group(3))
    return out


def tally(flags, judged, defined=None):
    defined = defined or {}
    rows = []
    for f in flags['flags']:
        v, ev = judged.get(f['id'], (None, None))
        dv, dev = defined.get(f['id'], (None, None))
        rows.append({'id': f['id'], 'doc': f['doc'], 'rule': f['rule'], 'term': f['term'], 'tool_verdict': f['verdict'],
                     'judge': v, 'evidence': ev, 'defines': dv, 'defines_evidence': dev})
    n = sum(1 for r in rows if r['judge'])
    fa = sum(1 for r in rows if r['judge'] == 'CARRIED')
    un = sum(1 for r in rows if r['judge'] == 'UNSURE')
    nc = sum(1 for r in rows if r['judge'] == 'NOT CARRIED')
    return {'judged': n, 'unjudged': [r['id'] for r in rows if not r['judge']], 'carried': fa, 'unsure': un,
            'not_carried': nc,
            'false_alarm_rate': {'unsure_not_false_alarm': [fa, n, wilson(fa, n)],
                                 'unsure_as_false_alarm': [fa + un, n, wilson(fa + un, n)],
                                 'unsure_dropped': [fa, n - un, wilson(fa, n - un)]},
            'by_doc': {d: _count(r['judge'] for r in rows if r['doc'] == d) for d in sorted({r['doc'] for r in rows})},
            'by_tool_verdict': {v: _count(r['judge'] for r in rows if r['tool_verdict'] == v)
                                for v in sorted({r['tool_verdict'] for r in rows})},
            'supplementary_definition_pass': _broad(rows) if defined else None,
            'rows': rows}


def _broad(rows):
    """The supplementary count: a flag is a false alarm in the broad sense when the main judge says CARRIED or the
    definition pass says DOES NOT DEFINE; UNSURE in either pass is shown both ways."""
    both = [r for r in rows if r['judge'] and r['defines']]
    strict = sum(1 for r in both if r['judge'] == 'CARRIED' or r['defines'] == 'DOES NOT DEFINE')
    loose = sum(1 for r in both if r['judge'] in ('CARRIED', 'UNSURE') or r['defines'] in ('DOES NOT DEFINE', 'UNSURE'))
    return {'judged_both': len(both), 'defines': _count(r['defines'] for r in rows),
            'cross': _count(f'{r["judge"]} / {r["defines"]}' for r in both),
            'broad_false_alarm': [strict, len(both), wilson(strict, len(both))],
            'broad_false_alarm_unsure_as_false_alarm': [loose, len(both), wilson(loose, len(both))]}


# ------------------------------------------------------------------------------------------------------------ main ---
def _write(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('fixture')
    a.add_argument('--repo', default=str(ROOT))
    a.add_argument('--pin', default='e53db4e8fc')
    a.add_argument('--audit', default=str(ROOT / OOS_AUDIT))
    a.add_argument('--out', required=True)
    a = sub.add_parser('recall')
    a.add_argument('--fixture', required=True)
    a.add_argument('--report', action='append', required=True, metavar='LABEL=JSON')
    a.add_argument('--out', required=True)
    a = sub.add_parser('draw')
    a.add_argument('--report', required=True)
    a.add_argument('--n', type=int, required=True)
    a.add_argument('--seed', type=int, required=True)
    a.add_argument('--out', required=True)
    a = sub.add_parser('packets')
    a.add_argument('--flags', required=True)
    a.add_argument('--repo', default=str(ROOT))
    a.add_argument('--ref', required=True)
    a.add_argument('--out-dir', required=True)
    a.add_argument('--question', choices=('carried', 'definition'), default='carried')
    a = sub.add_parser('tally')
    a.add_argument('--flags', required=True)
    a.add_argument('--judge-dir', required=True)
    a.add_argument('--definition-dir', help='replies of the supplementary definition pass')
    a.add_argument('--out', required=True)
    a = ap.parse_args(argv)
    if a.cmd == 'fixture':
        fx = build_fixture(a.repo, a.pin, a.audit)
        _write(a.out, fx)
        print(json.dumps(fx['counts']))
    elif a.cmd == 'recall':
        fx = json.loads(Path(a.fixture).read_text(encoding='utf-8'))
        out = {}
        for spec in a.report:
            label, path = spec.split('=', 1)
            out[label] = tabulate_recall(fx, json.loads(Path(path).read_text(encoding='utf-8')))
            t = out[label]
            print(f'{label}: pairs {t["hits"]}/{t["cases"]} {t["recall_pairs_wilson95"]}; findings '
                  f'{t["findings_detected"]}/{t["findings"]} {t["recall_findings_wilson95"]}; misses {t["miss_reasons"]}')
        lines = [json.dumps(dict(p, tree=label), ensure_ascii=False) for label, t in out.items() for p in t.pop('per_case')]
        _write(a.out, out)
        Path(a.out).with_suffix('.cases.jsonl').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    elif a.cmd == 'draw':
        d = draw(json.loads(Path(a.report).read_text(encoding='utf-8')), a.n, a.seed, known_keys())
        _write(a.out, d)
        print(f'population {d["population"]}, drawn {d["drawn"]}, seed {d["seed"]}: {d["by_doc"]} {d["by_verdict"]}')
    elif a.cmd == 'packets':
        fl = json.loads(Path(a.flags).read_text(encoding='utf-8'))
        out = Path(a.out_dir)
        out.mkdir(parents=True, exist_ok=True)
        got = def_packet(fl) if a.question == 'definition' else packets(fl, a.repo, a.ref)
        for key, p in got.items():
            (out / f'{key}.prompt.txt').write_text(p['text'], encoding='utf-8')
            print(f'{key}: {len(p["ids"])} flags, {len(p["text"].encode())} bytes')
    elif a.cmd == 'tally':
        fl = json.loads(Path(a.flags).read_text(encoding='utf-8'))
        judged = {}
        for f in sorted(Path(a.judge_dir).glob('*.reply.txt')):
            for k, v in parse_judge(f.read_text(encoding='utf-8')).items():
                judged.setdefault(k, v)
        defined = {}
        for f in sorted(Path(a.definition_dir).glob('*.reply.txt')) if a.definition_dir else ():
            for k, v in parse_judge(f.read_text(encoding='utf-8'), DEF_LINE).items():
                defined.setdefault(k, v)
        t = tally(fl, judged, defined)
        _write(a.out, t)
        print(json.dumps({k: t[k] for k in ('judged', 'carried', 'unsure', 'not_carried', 'false_alarm_rate',
                                            'supplementary_definition_pass')}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
