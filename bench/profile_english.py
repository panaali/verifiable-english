"""Offline, measurement-only English/user-path benchmark. Writes raw JSON."""
import cProfile
import hashlib
import json
import platform
import pstats
import re
from pathlib import Path

from timing import DEFAULT_REPEATS, DEFAULT_WARMUPS, measure, stats
from ve.ast import Document, formula_from_data
from ve.document import check_document, load_document
from ve.english import parse_english, render_english
from ve.natural import render_natural_sentence
from ve.assist.ambiguity_patterns import review, checked_wording
from ve.assist.recovery import RecoveryService
from ve.environment import Environment, LANGUAGE, PROFILE, SPEC_REVISION
from ve.ast import Unary, Const
from ve.parser import parse as parse_strict

ROOT = Path(__file__).resolve().parents[1]
EDITOR_CATALOGUE_REPEATS = 20
DOCS = {
    "claude": sorted(Path('/home/seyran/code').glob('ve-pilot-*/usecases/claude-constitution-pilot/run-*/translation.ve.md'))[-1],
    "udhr": sorted(Path('/home/seyran/code').glob('ve-udhr-*/usecases/udhr-pilot/run-*/translation.ve.md'))[-1],
    "bluedot": Path('/home/seyran/code/ve-bluedot/usecases/bluedot-grant/document.ve.md'),
}
CORPORA = ('claude-constitution-excerpt', 'news-article',
           'birthright-citizenship-debate', 'us-constitution-14th-s1')
SOURCES = {
    'claude': Path('/home/seyran/code/manage-agents/pilots/claude-constitution/source/claude-constitution.md'),
    'udhr': Path('/home/seyran/code/manage-agents/pilots/udhr/source/udhr.md'),
}

def profile(fn, n=18):
    p = cProfile.Profile()
    p.enable()
    try:
        fn()
    finally:
        p.disable()
    rows = []
    for (file, line, name), s in pstats.Stats(p).stats.items():
        cc, nc, own, cum, _ = s
        if '/ve/' in file or '/lark/' in file:
            rows.append({'function': f'{Path(file).name}:{line}:{name}', 'calls': nc,
                         'own_s': round(own, 6), 'cum_s': round(cum, 6)})
    return sorted(rows, key=lambda x: x['cum_s'], reverse=True)[:n]

def tokens(s):
    return len(re.findall(r"\w+|[^\w\s]", s))

def source_sentences(path):
    # A reproducible sentence splitter for ranking source prose. Headers and
    # markdown link targets are removed, but wording is not translated.
    source = path.read_text()
    source = re.sub(r'\]\([^)]*\)', ']', source)
    source = re.sub(r'(?m)^#{1,6} .*$', '', source)
    source = re.sub(r'(?m)^\s*[-*+]\s+', '', source)
    source = re.sub(r'\s+', ' ', source)
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+(?=[A-Z“"(])', source)
            if len(s.split()) > 3]

def service_env():
    return Environment({'language': LANGUAGE, 'profile': PROFILE, 'spec_revision': SPEC_REVISION,
        'vocabulary': {'sorts': {'service': {'description': 'service'},
                                 'engineer': {'description': 'engineer'},
                                 'server': {'description': 'server'}},
          'predicates': {'safe': {'arguments': ['service'], 'description': 'safe'},
                         'checks_pair': {'arguments': ['engineer','server'],
                                         'description': 'checks', 'verbalisation': '{0} checks {1}'}},
          'constants': {n: {'sort': 'service', 'description': n}
                        for n in ('api','carol','alice')}}})

def main():
    out = {'machine': {'platform': platform.platform(), 'python': platform.python_version(),
                        'cpus': __import__('os').cpu_count()},
           'sampling': {'default_repeats': DEFAULT_REPEATS,
                        'editor_catalogue_repeats': EDITOR_CATALOGUE_REPEATS,
                        'warmups': DEFAULT_WARMUPS},
           'documents': {}, 'sentences': [], 'raw_source': {}, 'editor': {},
           'method': (f'{DEFAULT_WARMUPS} untimed warm-up per case, then sequential timed runs; '
                      f'editor catalogues use {EDITOR_CATALOGUE_REPEATS} samples. '
                      'cProfile is separate; load is sampled before each timed call.')}
    loaded = {}
    cases = []
    for label, path in DOCS.items():
        loaded[label] = load_document(path)
        doc = loaded[label]
        formula_rows = [u for u in doc['units'] if u.get('content') is not None
                        and isinstance(u['content'], list)]
        for u in formula_rows:
            try:
                f = formula_from_data(doc['environment'], u['content'])
                wording = render_english(Document((f,)), doc['environment']).strip()
                if not wording.endswith('.'): wording += '.'
                if parse_english(doc['environment'], wording) == Document((f,)):
                    cases.append((label, u['id'], wording, f, doc['environment']))
            except Exception:
                continue
        print('loaded', label, 'checked', len(formula_rows), 'accepted', len([c for c in cases if c[0] == label]), flush=True)
    for label in CORPORA:
        directory = ROOT/'usecases'/label
        env = Environment.from_json((directory/'environment.json').read_bytes())
        for f in parse_strict(env,(directory/'claims.ve').read_text()).formulas:
            try:
                wording = render_english(Document((f,)),env).strip()
                if not wording.endswith('.'): wording += '.'
                if parse_english(env,wording) == Document((f,)):
                    cases.append((label,str(len(cases)),wording,f,env))
            except Exception:
                continue
        print('corpus',label,len([c for c in cases if c[0]==label]),flush=True)
    # Keep the longest accepted examples per source and short/mid bins for a length curve.
    cases.sort(key=lambda c: tokens(c[2]))
    chosen = {}
    for label in (*DOCS,*CORPORA):
        subset = [c for c in cases if c[0] == label]
        for index in (0, len(subset)//4, len(subset)//2, 3*len(subset)//4, len(subset)-1):
            if subset: chosen[(label, subset[index][1])] = subset[index]
    for label, uid, wording, f, env in chosen.values():
        def parse(): return parse_english(env, wording)
        def natural(): return render_natural_sentence(f, env)
        def combined():
            parsed = parse()
            assert parsed == Document((f,))
            return natural()
        p, pl = measure(parse)
        r, rl = measure(natural)
        c, cl = measure(combined)
        out['sentences'].append({'source': label, 'unit': uid, 'tokens': tokens(wording),
                                 'bytes': len(wording.encode()), 'english': wording,
                                 'parse_ms': p, 'parse_load': pl, 'parse_stats': stats(p),
                                 'natural_ms': r, 'natural_load': rl, 'natural_stats': stats(r),
                                 'combined_ms': c, 'combined_load': cl, 'combined_stats': stats(c),
                                 'combined_profile': profile(combined, 15)})
        print('sentence', label, uid, tokens(wording), stats(p), flush=True)
    for label, path in DOCS.items():
        vals, loads = measure(lambda: check_document(path))
        out['documents'][label] = {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'source_bytes': len(loaded[label]['source']), 'units': len(loaded[label]['units']),
            'wall_ms': vals, 'load': loads, 'stats': stats(vals), 'profile': profile(lambda: check_document(path))}
        print('document', label, stats(vals), flush=True)
    for label,path in SOURCES.items():
        rows = sorted(source_sentences(path), key=tokens, reverse=True)[:5]
        out['raw_source'][label] = {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'sentences': []}
        for rank, src in enumerate(rows, 1):
            def attempt():
                try: parse_english(loaded[label]['environment'], src)
                except Exception as exc: return type(exc).__name__
                return 'accepted'
            result = attempt(); vals, loads = measure(attempt)
            out['raw_source'][label]['sentences'].append({'rank': rank, 'text': src,
                'tokens': tokens(src), 'bytes': len(src.encode()), 'result': result,
                'wall_ms': vals, 'load': loads, 'stats': stats(vals),
                'profile': profile(attempt, 10)})
            print('raw source', label, rank, tokens(src), result, stats(vals), flush=True)
    # Z3 is the editor workstream name. The proposer is absent throughout.
    env = service_env()
    examples = [('scope', 'Every engineer checks a server.',
                 {'every_sort':'engineer','some_sort':'server','relation':'checks_pair'},'scope.every_some@1'),
                ('reference','It is safe.', {'predicate':'safe','antecedents':['api','carol']},'discourse.reference@1')]
    for label, src, bindings, pattern in examples:
        def editor_parse():
            try: parse_english(env, src)
            except Exception as exc: return type(exc).__name__
            return 'accepted'
        parse_result = editor_parse()
        pv, p_load = measure(editor_parse)
        def catalogue(): return review(env,src,bindings,pattern_id=pattern)
        vals, loads = measure(catalogue, repeats=EDITOR_CATALOGUE_REPEATS,
                              warmups=DEFAULT_WARMUPS)
        result = catalogue()
        out['editor'][label] = {'source': src, 'parse_result': parse_result,
                               'parse_ms': pv, 'parse_load': p_load, 'parse_stats': stats(pv),
                               'parse_profile': profile(editor_parse), 'cards': len(result['cards']),
                               'pending': len(result['pending']), 'catalogue_ms': vals,
                               'load': loads, 'stats': stats(vals), 'profile': profile(catalogue)}
        print('editor catalogue',label,stats(vals),flush=True)
    formula = Unary('safe',Const('api'))
    wording = 'Api is safe.'
    def validation(): return checked_wording(env,wording,formula)
    vals, loads = measure(validation)
    out['editor']['validation'] = {'wall_ms': vals,'load':loads,'stats':stats(vals),'profile':profile(validation)}
    def classify():
        service = RecoveryService(env,grammar_version='g1',glossary_version='v1',reading_set_version='r1')
        service.add('u','Every engineer checks a server.',{'start':0})
        service.start('u')
        return service.classify('u',parse_outcome='one',catalogue_bindings={'scope.every_some@1':examples[0][2]})
    vals, loads = measure(classify)
    out['editor']['classify'] = {'wall_ms': vals,'load':loads,'stats':stats(vals),'profile':profile(classify)}
    print('editor validation/classify',stats(out['editor']['validation']['wall_ms']),stats(vals),flush=True)
    outpath=ROOT/'bench/PROFILE-ENGLISH-AFTER.json'
    outpath.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    print('wrote',outpath,flush=True)

if __name__ == '__main__': main()
