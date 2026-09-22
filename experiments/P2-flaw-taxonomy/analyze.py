"""Tally P2 flaw labels per corpus with Wilson 95% intervals. Run: python3 analyze.py"""
import csv, json, math, os, collections
HERE = os.path.dirname(os.path.abspath(__file__))
CORPORA = ["processbench", "bbm_ld", "matharena", "opc", "logicclimate"]

def wilson(k, n, z=1.96):
    if n == 0: return (float("nan"),)*3
    p = k/n; d = 1+z*z/n; c = (p+z*z/(2*n))/d; h = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return p, max(0, c-h), min(1, c+h)

def fmt(k, n):
    p, lo, hi = wilson(k, n); return f"{k}/{n} = {p:.0%} [{lo:.0%}-{hi:.0%}]"

def top(code):  # D* counts as its own bucket
    return code.split("-")[0] if code.startswith(("S", "O")) else code

rows_out = []
agg = collections.Counter(); aggn = 0
for c in CORPORA:
    rows = list(csv.DictReader(open(os.path.join(HERE, "labels", f"{c}.tsv")), delimiter="\t"))
    assert len(rows) == 50, (c, len(rows))
    codes = collections.Counter(r["code"] for r in rows)
    loc = [r for r in rows if r["code"] not in ("N", "U")]
    n = len(loc)
    cnt = collections.Counter(r["code"] for r in loc)
    D = cnt["D"]; Ds = cnt["D*"]
    P = cnt["P"]; S = cnt["S-premise"]+cnt["S-goal"]+cnt["S"]
    O = sum(v for k, v in cnt.items() if k.startswith("O-"))
    eq = cnt["O-equiv"]
    strict = D + eq
    broad = strict + cnt["O-circ"] + cnt["O-case"] + cnt["O-arith"]
    # sensitivity: count unsure items whose alt is D as D (upper) / unsure primary-D items as non-D (lower)
    D_hi = D + sum(1 for r in loc if r["code"] != "D" and r["alt"] == "D" and r["sure"] == "n")
    D_lo = D - sum(1 for r in loc if r["code"] == "D" and r["sure"] == "n")
    print(f"\n== {c}: 50 sampled; N (no flaw under rubric)={codes['N']}, U (not localised)={codes['U']}, localised n={n}")
    print("  codes:", dict(sorted(cnt.items())))
    print("  D        ", fmt(D, n), f" sensitivity D in [{D_lo/n:.0%}, {D_hi/n:.0%}]")
    if Ds: print("  D* (valid from all premises; annotated as jump)", fmt(Ds, n))
    print("  P        ", fmt(P, n)); print("  S        ", fmt(S, n), f" (S-premise {cnt['S-premise']}, S-goal {cnt['S-goal']+cnt['S']})")
    print("  O        ", fmt(O, n), f" (equiv {eq}, arith {cnt['O-arith']}, case {cnt['O-case']}, circ {cnt['O-circ']}, incomplete {cnt['O-incomplete']}, ambig {cnt['O-ambig']})")
    print("  VE strict (D+equiv)       ", fmt(strict, n))
    print("  VE broad (+circ,case,arith)", fmt(broad, n))
    print("  + S-premise if premises formalised independently", fmt(broad+cnt["S-premise"], n))
    print("  unsure items:", sum(r["sure"] == "n" for r in loc), "/", n)
    rows_out.append(dict(corpus=c, n=n, N=codes["N"], U=codes["U"], D=D, Dstar=Ds, P=P, S=S, O=O, equiv=eq, arith=cnt["O-arith"], case=cnt["O-case"], circ=cnt["O-circ"], incomplete=cnt["O-incomplete"], ambig=cnt["O-ambig"], strict=strict, broad=broad, Spremise=cnt["S-premise"]))
    for k in ("D", "P", "S", "O", "strict", "broad"): agg[k] += rows_out[-1][k if k not in ("S",) else "S"]
    aggn += n
print("\n== pooled (unweighted across corpora, not a population estimate):")
for k in ("D", "P", "S", "O", "strict", "broad"): print(f"  {k:7s}", fmt(agg[k], aggn))
json.dump(rows_out, open(os.path.join(HERE, "summary.json"), "w"), indent=1)
