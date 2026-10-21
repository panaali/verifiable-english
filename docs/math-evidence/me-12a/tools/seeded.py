"""Plant each seeded bug in a scratch copy of lean/, build VE.Arith.Examples under timeout 600, list the errors."""
import json, re, shutil, subprocess, sys, os, tempfile
from pathlib import Path
root = Path(sys.argv[1]); out = Path(sys.argv[2])
BUGS = [
 ("S1", "VE/Arith/Holds.lean", "plan's seeded bug in the meaning: a bounded ∃ from lo to hi ranges up to hi + 1",
  "∃ i : Int, l ≤ i ∧ i ≤ h ∧ Holds E (i :: ρ) φ", "∃ i : Int, l ≤ i ∧ i ≤ h + 1 ∧ Holds E (i :: ρ) φ"),
 ("S1b", "VE/Arith/Holds.lean", "the same for a bounded ∀",
  "∀ i : Int, l ≤ i → i ≤ h → Holds E (i :: ρ) φ", "∀ i : Int, l ≤ i → i ≤ h + 1 → Holds E (i :: ρ) φ"),
 ("S2", "VE/Arith/Defs.lean", "RecursiveDefinition: a call of itself or a later definition admitted",
  "| none => some (.recursiveDefinition f)", "| none => none"),
 ("S3", "VE/Arith/Defs.lean", "UnscopedVariable: a variable one past the scope admitted",
  "if j < depth then none", "if j ≤ depth then none"),
 ("S4", "VE/Arith/Defs.lean", "Bounded: \"for every whole number\" counted as bounded",
  "  | .allNat _ => false\n  | .exNat _ => false", "  | .allNat _ => true\n  | .exNat _ => false"),
 ("S5", "VE/Arith/Defs.lean", "ArityMismatch: extra arguments admitted",
  "if d.arity = argc then none", "if d.arity ≤ argc then none"),
 ("S6", "VE/Arith/Defs.lean", "the decoder's order: the first refusal in the list, whatever its class",
  "(rs.filter fun r => rs.all fun s => r.rank ≤ s.rank).head?", "rs.head?"),
 ("S7", "VE/Arith/Defs.lean", "DuplicateName: a name defined twice admitted",
  "if (D.take k).any (·.name == d.name)", "if (D.take k).any (fun _ => false)"),
 ("S8", "VE/Arith/Defs.lean", "UnboundedCount: an unbounded count condition admitted",
  "| some B => if Formula.bnd B φ then none", "| some B => if true then none"),
 ("S9", "VE/Arith/Defs.lean", "UnknownDefinition: the kind of a call ignored",
  "D.any (fun d => d.name == f && d.isPred == pred)", "D.any (fun d => d.name == f)"),
]
scratch = Path(tempfile.mkdtemp(prefix='me12a-sb-')); lean = scratch / 'lean'
shutil.copytree(root / 'lean', lean, symlinks=True)
env = dict(os.environ, PATH=os.path.expanduser('~/.elan/bin') + ':' + os.environ['PATH'])
res = []
for bid, f, what, before, after in BUGS:
    p = lean / f; orig = p.read_text()
    assert orig.count(before) == 1, (bid, orig.count(before))
    p.write_text(orig.replace(before, after))
    try:
        r = subprocess.run(['timeout', '600', 'lake', 'build', 'VE.Arith.Examples'], cwd=lean, env=env, capture_output=True, text=True)
    finally:
        p.write_text(orig)
    errs = sorted(set(re.findall(r'error: (VE/[\w/]+\.lean:\d+):\d+: ([^\n]{0,60})', r.stdout + r.stderr)))
    res.append({"id": bid, "file": "lean/" + f, "bug": what, "before": before, "after": after,
                "build_exit": r.returncode, "fails": [e[0] + ": " + e[1] for e in errs]})
    print(bid, r.returncode, errs[:6], flush=True)
out.write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
shutil.rmtree(scratch)
