#!/usr/bin/env python3
"""Serial, reproducible whole-project build plus iceberg axiom audit.
Run from any directory: python3 experiments/obfuscated-arguments/iceberg/verify.py
Only one module target is requested at a time, dependencies first; native objects
are also completed before the next target. No assumption that Lake's scheduler
has a working -j flag. Final default-target build only aggregates cached modules.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LEAN = ROOT / 'lean'
records = []
env = dict(os.environ, LEAN_NUM_THREADS='1')


def run(command, cwd):
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    clock = time.perf_counter()
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True)
    record = dict(command=command, cwd=str(cwd.relative_to(ROOT)), start=start,
                  seconds=round(time.perf_counter()-clock, 6),
                  exit_code=result.returncode, output=result.stdout+result.stderr)
    records.append(record)
    (HERE / 'verification.json').write_text(json.dumps(dict(
        toolchain=(LEAN / 'lean-toolchain').read_text().strip(),
        lean_source_sha256=hashlib.sha256((LEAN / 'Iceberg.lean').read_bytes()).hexdigest(),
        serial_strategy=__doc__, records=records), indent=2)+'\n')
    print(' '.join(command), record['exit_code'], record['seconds'], flush=True)
    if result.returncode:
        print(record['output'], flush=True)
        raise SystemExit(result.returncode)
    return record['output']


sources = {str(p.relative_to(LEAN).with_suffix('')).replace('/', '.'): p
           for p in LEAN.rglob('*.lean') if '.lake' not in p.parts}
visited = set()
ordered = []


def visit(name):
    if name in visited:
        return
    visited.add(name)
    for dependency in re.findall(r'^import\s+(\S+)', sources[name].read_text(), re.M):
        if dependency in sources:
            visit(dependency)
    ordered.append(name)


for name in ('VE', 'Main', 'Iceberg'):
    visit(name)
for name in ordered:
    run(['lake', 'build', '+'+name+':o'], LEAN)
run(['lake', 'build'], LEAN)
output = run(['lake', 'env', 'lean', '-j1', 'Iceberg.lean'], LEAN)
assert 'sorryAx' not in output
lines = re.findall(r"'Iceberg\.(\w+)' depends on axioms: \[([^\]]*)\]", output)
expected = set(re.findall(r'^#print axioms (\w+)', (LEAN / 'Iceberg.lean').read_text(), re.M))
assert {name for name, _ in lines} == expected
assert all(set(axioms.split(', ')) <= {'propext', 'Classical.choice', 'Quot.sound'}
           for _, axioms in lines)
print(f'PASS: default targets, {len(ordered)} serial modules, {len(lines)} axiom audits', flush=True)
