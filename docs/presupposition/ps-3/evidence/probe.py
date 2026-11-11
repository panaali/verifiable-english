"""ps-3 statement probe: each declaration of Couple.lean (and the statements of Couple/Statements.lean) against the
PS-S stub's 4.8 section and spec 4.8's block; comments stripped, whitespace-normalised. A spec entry without a body
is compared up to its `:=` (the signature). Usage: python3 -I probe.py <stub.lean>"""
import re, sys
KW = r'^(?:theorem|def|abbrev|structure|instance|noncomputable def)\s+'
def decls(text):
    text = re.sub(r'/-.*?-/', '', text, flags=re.S)
    text = re.sub(r'--[^\n]*', '', text)
    out, cur = {}, None
    for line in text.splitlines():
        m = re.match(KW + r'([^\s(:]+)', line)
        if m:
            cur = m.group(1).removeprefix('stmt_'); out[cur] = line
        elif cur and line.startswith((' ', '\t')) and line.strip():
            out[cur] += ' ' + line
        elif not line.strip() or not line.startswith((' ', '\t')):
            cur = None if not line.strip() or re.match(r'^(end|namespace|open|universe|#|import|set_option)', line) else cur
    return {k: ' '.join(v.split()) for k, v in out.items()}
def sig(s): return s.split(' :=')[0]
spec = open('docs/spec/presupposition.md').read()
spec48 = decls(re.search(r'### 4\.8.*?```lean\n(.*?)```', spec, re.S).group(1))
stub = open(sys.argv[1]).read(); stub48 = decls(stub[stub.index('## 4.8 Couple.lean'):stub.index('end VE.Presupposition', stub.index('## 4.8 Couple.lean'))])
ours = decls(open('lean/VE/Presupposition/Couple.lean').read())
ours.update({k: v for k, v in decls(open('lean/VE/Presupposition/Couple/Statements.lean').read()).items()
             if k in ('coupling_complete', 'coupled_uniform', 'coupled_subset')})
bad = []
for name, ref in [(n, spec48[n]) for n in spec48] :
    o = ours.get(name)
    same = o is not None and (o == ref if ' :=' in ref else sig(o) == ref)
    print(f"spec {name}: {'equal' if same else 'DIFFERS'}"); same or bad.append(('spec', name))
for name, ref in stub48.items():
    if name in ('coupling_complete', 'coupled_uniform', 'coupled_subset'): continue  # Prop forms; spec's text checked
    o = ours.get(name)
    print(f"stub {name}: {'equal' if o == ref else 'DIFFERS'}"); o == ref or bad.append(('stub', name))
print('differing', bad)
