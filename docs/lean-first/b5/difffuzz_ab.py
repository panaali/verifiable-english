"""Compare 14 date-seed differential fuzz samples against batch 5's base.

The head may remove findings: only signatures new at the head are a gate failure.
Each checkout runs its own source and locked native builds against the same seed.
"""
from concurrent.futures import ThreadPoolExecutor
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile

HEAD = Path(__file__).resolve().parents[3]
SEEDS = tuple(20260900 + day for day in range(23, 31)) + tuple(20261000 + day for day in range(1, 7))


def run(job):
    side, root, seed, scratch = job
    report = scratch / f'{side}-{seed}.json'
    env = {**os.environ, 'UV_CACHE_DIR': '/tmp/ve-lf-b5-uv-cache'}
    command = ['uv', 'run', '--frozen', 'python', 'tools/difffuzz.py', '--deep', '1',
               '--seed', str(seed), '--report', str(report)]
    proc = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True)
    if not report.exists():
        raise RuntimeError(f'{side} seed {seed} produced no report (exit {proc.returncode}): '
                           f'{proc.stderr[-1000:]}')
    data = json.loads(report.read_text())
    return {'side': side, 'seed': seed, 'new': sorted(e['signature'] for e in data['new']),
            'cpu_seconds': data['cpu_seconds'], 'baseline': data['baseline']}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    base_root = args.base.resolve()
    scratch = Path(tempfile.mkdtemp(prefix='b5-difffuzz-', dir='/tmp'))
    jobs = [(side, root, seed, scratch) for seed in SEEDS
            for side, root in (('base', base_root), ('head', HEAD))]
    with ThreadPoolExecutor(max_workers=4) as pool:
        reports = list(pool.map(run, jobs))
    rows = []
    for index, seed in enumerate(SEEDS):
        base, head = reports[2 * index:2 * index + 2]
        head_only = sorted(set(head['new']) - set(base['new']))
        rows.append({'seed': seed, 'base_new': len(base['new']), 'head_new': len(head['new']),
                     'head_only': head_only, 'base_baseline_seen': base['baseline']['seen_in_sample'],
                     'head_baseline_seen': head['baseline']['seen_in_sample'],
                     'base_cpu_seconds': base['cpu_seconds'], 'head_cpu_seconds': head['cpu_seconds']})
    result = {'base': str(base_root), 'head': str(HEAD), 'seed_count': len(SEEDS),
              'head_only_total': sum(len(row['head_only']) for row in rows), 'seeds': rows}
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'seed_count': result['seed_count'], 'head_only_total': result['head_only_total'],
                      'counts': [(r['seed'], r['base_new'], r['head_new']) for r in rows]}, indent=2))
    return 0 if result['head_only_total'] == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
