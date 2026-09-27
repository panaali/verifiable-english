"""Deterministic, local VE cross-runtime timing. No model or network calls."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
RUST = ROOT / 'rust/target/release/ve'
LEAN = ROOT / 'lean/.lake/build/bin'
REPEATS = 5


def percentile(xs, q):
    values = sorted(xs)
    k = (len(values) - 1) * q
    lo = int(k)
    return values[lo] + (values[min(lo + 1, len(values) - 1)] - values[lo]) * (k - lo)


def stats(xs):
    return {'median_ms': round(statistics.median(xs) * 1000, 4),
            'p95_ms': round(percentile(xs, .95) * 1000, 4), 'samples_ms': [round(x * 1000, 4) for x in xs]}


def corpus(quick=True):
    from ve.ast import Top, Not, And
    from ve.entailment import prove_entailment
    from conformance import certificates, closure_certificates, order
    from conformance.p0 import definitions_envelope, DEF_MODEL, LEAD_A
    from tests.test_norms import environment as norm_environment, permission, rule
    from ve.norms import NormDocument, _bind
    from tests.test_bundle import bundle
    from conformance.english_surface import vocabularies
    from conformance.english_lean import lexicon, environment as lean_environment, tokenize, wire
    from ve.english import EnglishVocabulary
    from ve import render

    env = certificates.environment()
    proof = prove_entailment(env, (Top(),), Top())
    assert proof.certificate
    tableau = certificates.envelope('tableau', env, (Top(),), Top(), proof.certificate)
    def balanced_tops(n):
        return Top() if n == 1 else And(
            balanced_tops(n // 2), balanced_tops(n - n // 2))
    leaves = 64 if quick else 1024
    big_goal = balanced_tops(leaves)
    big_proof = prove_entailment(env, (), big_goal, max_steps=20000)
    assert big_proof.certificate
    big = certificates.envelope('tableau-large', env, (), big_goal, big_proof.certificate)
    big['certificate_nodes'] = big_proof.steps
    closure = closure_certificates.positive_cases()[0][0]
    oenv = order.environment()
    ps, goal = order.gen_farkas(__import__('random').Random(42))
    op = prove_entailment(oenv, ps, goal, max_steps=4000)
    assert op.certificate
    farkas = order.envelope('farkas', oenv, ps, goal, op.certificate)
    evaluation = json.loads((ROOT / 'conformance/evaluation.json').read_text())[0]
    evaluation.pop('source', None)
    evaluation.pop('expected', None)
    evaluation['kind'] = 'evaluate'
    search = next(c for c in json.loads((ROOT / 'conformance/search.json').read_text())
                  if c['expected_search']['status'] == 'Found')
    search = {k: v for k, v in search.items() if k not in ('expected_search', 'expected')}
    search['kind'] = 'search'
    from ve.profiles import LANGUAGE, SPEC_REVISION
    search['environment'] = {**search['environment'], 'language': LANGUAGE,
                             'spec_revision': SPEC_REVISION, 'profiles': ['relational-fol@0']}
    search['environment'].pop('profile', None)
    nenv = norm_environment({'permitted': permission()})
    doc = NormDocument(nenv, [rule('allow', 'permitted', True)])
    norm = {'id': 'norm', 'environment': nenv.to_dict(), 'norms': [r.to_dict() for r in doc.rules]}
    packages = {}
    for target, sorts, formula in doc.conflict_targets():
        result = prove_entailment(doc.base_environment(), (), _bind(Not(formula), sorts))
        assert result.certificate
        packages[target] = {'environment_id': nenv.environment_id,
                            'document_hash': doc.document_hash, 'target': target,
                            'certificate': result.certificate}
    definitions = {'id': 'definitions', 'kind': 'evaluate', 'environment': definitions_envelope(),
                   'model': DEF_MODEL, 'ast': [LEAD_A]}
    b = bundle()
    english_env = next(v for name, v in vocabularies() if name == 'ordinary')
    words = EnglishVocabulary(english_env)
    source = render(Top(), english_env, 've_english') + '.\n'
    english = {'id': 'english', 'environment': english_env.to_dict(), 'source': source,
               'lean_environment': lean_environment(english_env), 'lexicon': lexicon(english_env, words),
               'tokens': tokenize(source.lower()), 'formulas': [wire(Top())]}
    return {
        'certificate/tableau': (tableau, ('python', 'lean_cert')),
        'certificate/tableau-large': (big, ('python', 'lean_cert')),
        'certificate/closure': (closure, ('python', 'lean_cert')),
        'certificate/order-farkas': (farkas, ('python', 'lean_order')),
        'finite-model/evaluation': (evaluation, ('python', 'rust', 'lean')),
        'countermodel/search': (search, ('python', 'rust')),
        'W1/norm-elaboration': ({**norm, 'kind': 'norms-elaborate'}, ('python', 'lean_norms')),
        'W1/conflict-check': ({**norm, 'kind': 'norms-conflict', 'packages': packages}, ('python', 'lean_norms')),
        'W3/definitions': (definitions, ('python', 'lean_route')),
        'W3/bundle': ({'id': 'bundle', 'kind': 'bundle', 'environment': b['environment'],
                       'lemmas': b['lemmas'], 'bundle': b}, ('python', 'lean_route')),
        'English/parse': (english, ('python', 'lean_english')),
        'English/admission': ({**english, 'id': 'english-admission'}, ('python', 'lean_english')),
    }


def command(implementation):
    return {
        'python': [sys.executable, '-m', 'bench.worker'],
        'rust': [str(RUST), 'jsonl', '-', '--flush'],
        'lean': [str(LEAN / 've_conformance')],
        'lean_cert': [str(LEAN / 've_conformance'), 'check-certificate'],
        'lean_order': [str(LEAN / 've_conformance'), 'order'],
        'lean_route': [str(LEAN / 've_conformance'), 'route'],
        'lean_norms': [str(LEAN / 've_norms_route')],
        'lean_english': [str(LEAN / 've_english_run')],
    }[implementation]


def wire(case, implementation):
    x = {k: v for k, v in case.items() if k not in ('bundle', 'lean_environment', 'lexicon', 'tokens', 'formulas', 'source')}
    if implementation == 'python':
        x['bench_kind'] = ('bundle' if case.get('kind') == 'bundle' else 'english-admission' if case['id'] == 'english-admission'
                           else 'english' if case['id'] == 'english'
                           else 'definitions' if case['id'] == 'definitions' else 'certificate' if 'certificate' in case
                           else case.get('kind', 'english'))
        if case['id'] in ('english', 'english-admission'):
            x['source'] = case['source']
        if case.get('kind') == 'bundle':
            x['bundle'] = case['bundle']
        return x
    if implementation == 'rust':
        x.pop('kind', None)
        return x
    if implementation == 'lean' and case.get('kind') == 'evaluate':
        x.pop('kind', None)
    if implementation == 'lean_english':
        return {'tokens': case['tokens'], 'formulas': case['formulas']}
    return x


def input_bytes(case, implementation, count):
    if implementation == 'lean_english':
        payload = {'environment': case['lean_environment'], 'lexicon': case['lexicon'],
                   'cases': [wire(case, implementation) for _ in range(count)]}
    elif implementation in ('python', 'rust'):
        return b''.join(json.dumps(wire(case, implementation), separators=(',', ':')).encode() + b'\n'
                        for _ in range(count))
    else:
        payload = [wire(case, implementation) for _ in range(count)]
    return json.dumps(payload, separators=(',', ':')).encode()


def execute(case, implementation, count, timeout):
    payload = input_bytes(case, implementation, count)
    if len(payload) > 16_000_000:
        raise ValueError('batch exceeds the route 16 MiB input limit')
    started = time.perf_counter()
    proc = subprocess.run(command(implementation), input=payload, cwd=ROOT,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    elapsed = time.perf_counter() - started
    if proc.returncode not in (0, 1):
        raise RuntimeError(f'{implementation}: {proc.stderr.decode(errors="replace")[-1000:]}')
    try:
        rows = ([json.loads(line) for line in proc.stdout.splitlines()]
                if implementation in ('python', 'rust') else json.loads(proc.stdout))
        if implementation == 'lean_english':
            rows = rows['results']
    except (ValueError, KeyError) as exc:
        raise RuntimeError(f'{implementation}: malformed output {proc.stdout[:300]!r}') from exc
    if len(rows) != count or any(row.get('status') == 'error' for row in rows):
        raise RuntimeError(f'{implementation}: {len(rows)}/{count} outputs; first={rows[:1]} stderr={proc.stderr[-300:]!r}')
    return elapsed, rows


def interactive_call(case, implementation, timeout):
    """One warmed request in a live JSON-lines process; excludes process startup."""
    import select
    proc = subprocess.Popen(command(implementation), cwd=ROOT, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
    payload = input_bytes(case, implementation, 1)
    try:
        for warm in (True, False):
            started = time.perf_counter()
            proc.stdin.write(payload)
            proc.stdin.flush()
            if not select.select([proc.stdout], [], [], timeout)[0]:
                raise TimeoutError(f'{implementation} interactive response')
            row = json.loads(proc.stdout.readline())
            if row.get('status') == 'error':
                raise RuntimeError(f'{implementation}: {row}')
            if not warm:
                return time.perf_counter() - started, row
    finally:
        proc.stdin.close()
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()


def semantic(name, row):
    if name.startswith('certificate/'):
        return row.get('valid')
    if name in ('finite-model/evaluation', 'W3/definitions'):
        return row.get('values')
    if name == 'countermodel/search':
        return row.get('status')
    if name == 'W1/norm-elaboration':
        return row.get('layers', len(row.get('premises', [])))
    if name == 'W1/conflict-check':
        return row.get('verdict')
    if name == 'W3/bundle':
        return row.get('checked')
    if name == 'English/parse':
        return bool(row.get('parsed'))
    if name == 'English/admission':
        return bool(row.get('admitted', row.get('checked')))

    return None

def startup(implementation, case, timeout):
    if implementation == 'lean_english':
        payload = json.dumps({'environment': case['lean_environment'], 'lexicon': case['lexicon'], 'cases': []}).encode()
    else:
        payload = b'{"ping":true}\n' if implementation == 'python' else b'' if implementation == 'rust' else b'[]'
    times = []
    for _ in range(REPEATS):
        t = time.perf_counter()
        proc = subprocess.run(command(implementation), input=payload, cwd=ROOT,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        if proc.returncode != 0:
            raise RuntimeError(f'{implementation} startup: {proc.stderr[-500:]!r}')
        times.append(time.perf_counter() - t)
    return stats(times)


def sizes(name, quick):
    if name == 'certificate/tableau-large':
        return [1, 2] if quick else [1, 2, 4, 8]
    if quick:
        return [1, 4]
    if name.startswith('W3/bundle') or name.startswith('W1/conflict'):
        return [1, 8, 64, 256]
    if name.startswith('English'):
        return [1, 16, 128, 512]
    return [1, 16, 256, 2048]


def metadata():
    def version(cmd):
        try:
            return subprocess.run(cmd, capture_output=True, text=True, timeout=10).stdout.strip().splitlines()[0]
        except (OSError, IndexError, subprocess.TimeoutExpired):
            return 'unavailable'
    cpu = 'unknown'
    try:
        cpu = next(line.split(':', 1)[1].strip() for line in Path('/proc/cpuinfo').read_text().splitlines()
                   if line.startswith('model name'))
    except (OSError, StopIteration):
        cpu = platform.processor() or 'unknown'
    return {'utc': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
            'commit': version(['git', 'rev-parse', 'HEAD']), 'cpu_model': cpu,
            'logical_cpus': os.cpu_count(), 'loadavg': list(os.getloadavg()),
            'python': sys.version.split()[0], 'rustc': version(['rustc', '--version']),
            'lean': version([str(Path.home() / '.elan/bin/lean'), '--version']),
            'platform': platform.platform(), 'repeats': REPEATS}


def report(data):
    lines = ['# VE benchmark', '', f"Mode: **{'quick smoke' if data['quick'] else 'full'}**; 5 repetitions per measurement.",
             '', 'Times include runtime JSON decode/encode and IPC (input serialization by the harness is excluded). Batch throughput counts completed cases per wall second.',
             'Python and Rust per-call figures use a persistent JSON-lines process; Lean per-call is one-shot.',
             'Lean batch figures are amortized throughput in a single process, not interactive latency. Batch rates include process startup; interactive Python/Rust call latency follows one warm request.',
             '', '| Workload | Cases | Proof nodes | Runtime | Startup median/p95 ms | Call median/p95 ms | Batch cases/s median/p95 |',
             '|---|---:|---:|---|---:|---:|---:|']
    for row in data['measurements']:
        s, c, t = row['startup'], row['call'], row['throughput']
        nodes = (row.get('certificate_nodes_per_case') or 0) * row['cases']
        lines.append(f"| {row['workload']} | {row['cases']} | {nodes or '—'} | {row['implementation']} | {s['median_ms']}/{s['p95_ms']} | {c['median_ms']}/{c['p95_ms']} | {t['median_per_s']}/{t['p95_per_s']} |")
    lines += ['', 'Unsupported routes are omitted from the table: Rust has no certificate, norm, definition, bundle, or English checker; Lean has no interactive JSON-lines mode. Lean exposes countermodel checking but no search.',
              '', '## Full measurement', '', '```sh',
              'PATH="$HOME/.elan/bin:$PATH" UV_CACHE_DIR=/tmp/ve-uv-cache uv run --frozen python -m bench.run --out bench-results',
              '```', '', 'Expected duration: roughly 1–3 hours on an otherwise quiet workstation; the large certificate and 2,048-case search batches dominate. Build time is separate.',
              'Build first: `PATH="$HOME/.elan/bin:$PATH" lake build` in `lean/`, and `cargo build --release --locked` in `rust/`.',
              '', 'These fixtures are deterministic development cases, not a representative workload sample. Batch size counts cases; each certificate case contains its own proof tree. Raw timings and input bytes are in `results.json`.', '']
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--quick', action='store_true')
    args = parser.parse_args(argv)
    cases = corpus(args.quick)
    needed = {i for _, (_, impls) in cases.items() for i in impls}
    missing = [str(command(i)[0]) for i in needed if i != 'python' and not Path(command(i)[0]).exists()]
    if missing:
        parser.error('build executables first: ' + ', '.join(missing))
    timeout = 60 if args.quick else 900
    starts = {i: startup(i, next(c for c, impls in cases.values() if i in impls), timeout) for i in sorted(needed)}
    before_load = list(os.getloadavg())
    data = {'quick': args.quick, 'metadata': metadata(), 'startup': starts, 'measurements': []}
    args.out.mkdir(parents=True, exist_ok=True)
    for name, (case, impls) in cases.items():
        baseline = {i: semantic(name, execute(case, i, 1, timeout)[1][0]) for i in impls}
        if len({json.dumps(value, sort_keys=True) for value in baseline.values()}) != 1:
            raise RuntimeError(f'{name}: implementations disagree: {baseline}')
        for n in sizes(name, args.quick):
            samples = {i: {'call': [], 'batch': []} for i in impls}
            for rep in range(REPEATS):
                order = list(impls)
                if rep % 2:
                    order.reverse()
                for i in order:
                    call, _ = (interactive_call(case, i, timeout) if i in ('python', 'rust')
                               else execute(case, i, 1, timeout))
                    batch, _ = execute(case, i, n, timeout)
                    samples[i]['call'].append(call)
                    samples[i]['batch'].append(batch)
            for i in impls:
                throughput = [n / x for x in samples[i]['batch']]
                data['measurements'].append({'workload': name, 'cases': n, 'implementation': i,
                    'input_bytes': len(input_bytes(case, i, n)),
                    'certificate_nodes_per_case': case.get('certificate_nodes'), 'startup': starts[i],
                    'call': stats(samples[i]['call']), 'batch': stats(samples[i]['batch']),
                    'throughput': {'median_per_s': round(statistics.median(throughput), 2),
                                   'p95_per_s': round(percentile(throughput, .95), 2),
                                   'samples_per_s': [round(x, 2) for x in throughput]}})
            print(f'{name}: {n} cases complete', flush=True)
    data['metadata']['loadavg_before'] = before_load
    data['metadata']['loadavg_after'] = list(os.getloadavg())
    (args.out / 'results.json').write_text(json.dumps(data, indent=2) + '\n')
    (args.out / 'REPORT.md').write_text(report(data))


if __name__ == '__main__':
    main()
