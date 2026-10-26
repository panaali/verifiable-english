"""Build each trust mutant of this branch against the uncut proofs and examples; record what breaks.
Usage: proofkill.py ROOT OUT.json [ID ...]  (runs in a scratch copy of ROOT/lean; ROOT is only read)"""
import json, re, shutil, subprocess, sys, os, tempfile
from pathlib import Path
root = Path(sys.argv[1]); out = Path(sys.argv[2]); only = set(sys.argv[3:])
sys.path[:0] = [str(root), str(root / 'tools'), str(root / 'lean')]
os.chdir(root)
import trust_mutants as tm
base = subprocess.run(['git', 'merge-base', 'HEAD', 'main'], capture_output=True, text=True, cwd=root).stdout.strip()
muts, tree, fatal = tm.plan(root, base)
assert not fatal, fatal
scratch = Path(tempfile.mkdtemp(prefix='me12a-pk-'))
lean = scratch / 'lean'
shutil.copytree(root / 'lean', lean, symlinks=True)
env = dict(os.environ, PATH=os.path.expanduser('~/.elan/bin') + ':' + os.environ['PATH'])
def decl_at(text, line):
    lines = text.split('\n')[:line]
    for l in reversed(lines):
        m = re.match(r'(?:theorem|example|def|noncomputable def|#guard)\s*([^\s:(]*)', l)
        if m: return (l.split()[0] + ' ' + m.group(1)).strip() + f' (line {lines.index(l) + 1})'
    return '?'
results = []
for m in muts:
    if only and m.id not in only: continue
    path = lean / m.file
    orig = path.read_text()
    path.write_text(orig[:m.start] + m.edit[1] + orig[m.edit[0]:])
    try:
        r = subprocess.run(['timeout', '600', 'lake', 'build', 'VE.Arith.Examples'], cwd=lean, env=env,
                           capture_output=True, text=True)
    finally:
        path.write_text(orig)
    errs = sorted({(f, int(l)) for f, l in re.findall(r'error: (VE/[\w/]+\.lean):(\d+):', r.stdout + r.stderr)})
    texts = {}
    broken = []
    for f, l in errs:
        t = texts.setdefault(f, (lean / f).read_text())
        broken.append(f + ': ' + decl_at(t, l))
    own = [b for b in broken if b.startswith(m.file) and m.lines[0] <= int(b.rsplit('line ', 1)[1].rstrip(')')) <= m.lines[1]]
    status = 'BUILDS' if r.returncode == 0 else ('OWN-ERROR' if own and len(own) == len(broken) else 'BREAKS')
    results.append({'id': m.id, 'file': m.file, 'line': m.line, 'definition': m.definition, 'operator': m.operator,
                    'before': m.before[:120], 'after': m.after[:120], 'status': status, 'breaks': sorted(set(broken))})
    print(m.id, status, m.definition, m.operator, '|', '; '.join(sorted(set(broken)))[:200], flush=True)
out.write_text(json.dumps(results, indent=1, ensure_ascii=False) + '\n')
shutil.rmtree(scratch)
