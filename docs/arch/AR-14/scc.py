import ast, os, sys
root = sys.argv[1]
mods = {}
for dp, dn, fn in os.walk(os.path.join(root, "ve")):
    for f in fn:
        if f.endswith(".py"):
            p = os.path.join(dp, f); rel = os.path.relpath(p, root)[:-3].replace(os.sep, ".")
            if rel.endswith(".__init__"): rel = rel[:-9]
            mods[rel] = p
def resolve(name):
    while name and name not in mods:
        name = name.rpartition(".")[0]
    return name or None
g = {m: set() for m in mods}
for m, p in mods.items():
    try: t = ast.parse(open(p).read())
    except Exception: continue
    pkg = m if p.endswith("__init__.py") else m.rpartition(".")[0]
    for n in ast.walk(t):
        if isinstance(n, ast.Import):
            for a in n.names:
                r = resolve(a.name); 
                if r and r != m: g[m].add(r)
        elif isinstance(n, ast.ImportFrom):
            base = n.module or ""
            if n.level:
                parts = pkg.split(".")
                parts = parts[:len(parts)-(n.level-1)]
                base = ".".join(parts + ([base] if base else []))
            for a in n.names:
                r = resolve(base + "." + a.name) if base else None
                if r == base or r is None: r = resolve(base)
                if r and r != m: g[m].add(r)
sys.setrecursionlimit(100000)
idx = {}; low = {}; st = []; on = set(); out = []; c = [0]
def sc(v):
    idx[v] = low[v] = c[0]; c[0] += 1; st.append(v); on.add(v)
    for w in g[v]:
        if w not in idx: sc(w); low[v] = min(low[v], low[w])
        elif w in on: low[v] = min(low[v], idx[w])
    if low[v] == idx[v]:
        comp = []
        while True:
            w = st.pop(); on.discard(w); comp.append(w)
            if w == v: break
        if len(comp) > 1: out.append(sorted(comp))
for v in g:
    if v not in idx: sc(v)
out.sort(key=len, reverse=True)
print(len(mods), "modules;", "SCC sizes:", [len(x) for x in out])
for x in out[:3]: print(len(x), x[:60])
