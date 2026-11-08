"""Seeded bugs of pe-1: each mutant is applied in memory to its module's text; the mutated module(s) and
Examples.lean are elaborated as one file with `lake env lean`; the errors (broken proofs, failing #guards) are
printed. No repository file is written."""
import re, subprocess, sys, os
R = "/home/seyran/code/ve-pe-1/lean/"
def rd(p): return open(R + p).read()
def body(p):  # drop import lines
    return "\n".join(l for l in rd(p).splitlines() if not l.startswith("import "))
WF, IN, EX, WI = "VE/Purposes/WellFormed.lean", "VE/Route/Inert.lean", "VE/Purposes/Examples.lean", "VE/Purposes/Wire.lean"
BUGS = [
 ("slots-inOrderTo-unswapped", WF, "| .inOrderTo => (L.target, L.reason)", "| .inOrderTo => (L.reason, L.target)"),
 ("kind?-constant", WF, "(U.find? i).map (·.kind)", "(U.find? i).map (fun _ => Kind.asserted)"),
 ("shareOf-absent-sole", WI, "| .error _ => pure .plain", "| .error _ => pure .sole"),
 ("wordOf-refuses-known", WI, "| some x => pure x", "| some _ => throw (text s)"),
 ("control-no-mutation", WF, "def sidesAdjacent", "def sidesAdjacent"),
 ("shareOk-duplicate-rival", WF, "M.target == L.target && M.reason != L.reason", "M.target == L.target"),
 ("markerAgrees-slot-order", WF,
  "r == L.relation.wire && sideOfKind U L.slots.1 c && sideOfKind U L.slots.2 e",
  "r == L.relation.wire && ((sideOfKind U L.slots.1 c && sideOfKind U L.slots.2 e) || (sideOfKind U L.slots.1 e && sideOfKind U L.slots.2 c))"),
 ("nonfactive-only-asserted", WF, "| some p => p.kind.inert && p.candidates.all Kind.inert",
  "| some p => !(p.kind matches .asserted) && p.candidates.all Kind.inert"),
 ("nonfactive-ignores-candidates", WF, "| some p => p.kind.inert && p.candidates.all Kind.inert", "| some p => p.kind.inert"),
 ("markerHonest-always-true", WF,
  "U.parts.all fun p => p.status != \"LABELLED\" || !(B.links.any (·.marker == p.id)) ||\n    B.links.any fun L => L.marker == p.id && covered U L.reason && covered U L.target",
  "true"),
 ("inert-admits-norm", IN, "| .explanation | .exposition | .«example» | .analogy | .«meta» => true",
  "| .explanation | .exposition | .«example» | .analogy | .«meta» | .norm => true"),
 ("shareOk-ignores-other-share", WF,
  "| .sole => (rivals B L).isEmpty && B.links.all fun M => M.id == L.id || M.polarity != .affirmed ||\n      M.relation != L.relation || M.target != L.target || M.share == .plain || M.share == .sole",
  "| .sole => (rivals B L).isEmpty"),
 ("sideAdjacent-touching-only", WF, "| some ps => ps.all (fun p => p.span.1 ≤ p.span.2) && (ps.zip ps.tail).all fun (a, b) => a.span.2 == b.span.1",
  "| some ps => ps.all (fun p => p.span.1 ≤ p.span.2) && (ps.zip ps.tail).all fun (a, b) => a.span.2 == b.span.1 || b.span.2 == a.span.1"),
 ("sideAdjacent-order-only", WF, "| some ps => ps.all (fun p => p.span.1 ≤ p.span.2) && (ps.zip ps.tail).all fun (a, b) => a.span.2 == b.span.1",
  "| some ps => ps.all (fun p => p.span.1 ≤ p.span.2) && (ps.zip ps.tail).all fun (a, b) => decide (a.span.2 ≤ b.span.1)"),
]
only = sys.argv[1:]
for name, f, old, new in BUGS:
    if only and name not in only: continue
    src = rd(f); assert src.count(old) == 1, (name, src.count(old))
    mods = {f: src.replace(old, new)}
    chain = [IN, WF, EX] if f == IN else [f, EX]
    mod = lambda q: q[:-5].replace("/", ".")
    imports = []
    for q in chain:
        for l in rd(q).splitlines():
            if l.startswith("import ") and l[7:].strip() not in map(mod, chain) and l not in imports: imports.append(l)
    text = "\n".join(imports) + "\n"
    offs = []
    for p in chain:
        b = "\n".join(l for l in (mods.get(p) or rd(p)).splitlines() if not l.startswith("import "))
        offs.append((p, text.count("\n") + 1)); text += b + "\n"
    out = f"/tmp/pe1b/seed/{name}.lean"; open(out, "w").write(text)
    r = subprocess.run(["lake", "env", "lean", out], cwd=R, capture_output=True, text=True,
                       env={**os.environ, "PATH": os.path.expanduser("~/.elan/bin:") + os.environ["PATH"]})
    errs = []
    for m in re.finditer(r":(\d+):\d+: error: ([^\n]*)", r.stdout + r.stderr):
        ln = int(m.group(1)); where = max((o for o in offs if o[1] <= ln), key=lambda o: o[1])
        line = (mods.get(where[0]) or rd(where[0])).splitlines()
        nimp = sum(1 for l in line if l.startswith("import "))
        src_ln = ln - where[1] + 1 + nimp
        errs.append(f"{where[0]}:{src_ln}: {m.group(2)[:40]} | {line[src_ln-1].strip()[:110]}")
    print(f"== {name} ({f}): {len(errs)} errors"); [print("  ", e) for e in errs[:12]]
