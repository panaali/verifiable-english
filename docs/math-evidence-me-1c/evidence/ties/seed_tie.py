"""Plant one seeded tie in the checkout, run trust_map --check, restore the file (git checkout).

Run from the checkout's root: python3 seed_tie.py SEED OUTPUT. S1's saved output also holds the
ratchet test (tests/test_trust_ratchet.py::test_committed_budget_passes_its_check) run with the seed
in place; this script no longer runs it (tests/test_nested_pytest.py lists every file that builds a
pytest command)."""
import json, subprocess, sys
from pathlib import Path
seed, out = sys.argv[1], Path(sys.argv[2])
table, stm = Path("tools/trust-classes.json"), Path("lean/statements.txt")
SEEDS = {
 "S1-unrelated": ("renderClaim tied to the unrelated VE.Calc.Claim.decide_holds", table),
 "S2-uses-decl": ("values_stated's -- uses line loses VE.Calc.values@VE.Calc.Decls", stm),
 "S3-not-dumped": ("renderClaim tied to spec 9's VE.Calc.English.read_render, which no Lean file states", table),
}
what, path = SEEDS[seed]
def tie(theorem):
    t = json.loads(table.read_text())
    g = t["modules"]["VE/Calc/Render.lean"]["G[V]"]
    i = g.index("VE.Calc.English.renderClaim")
    g[i] = {"name": "VE.Calc.English.renderClaim", "tied": [theorem]}
    table.write_text(json.dumps(t, indent=2) + "\n")
try:
    if seed == "S1-unrelated":
        tie("VE.Calc.Claim.decide_holds")
    elif seed == "S3-not-dumped":
        tie("VE.Calc.English.read_render")
    else:
        lines = stm.read_text().split("\n")
        i = lines.index("theorem VE.Calc.values_stated")
        j = next(k for k in range(i, len(lines)) if lines[k].lstrip().startswith("-- uses"))
        assert " VE.Calc.values@VE.Calc.Decls" in lines[j]
        lines[j] = lines[j].replace(" VE.Calc.values@VE.Calc.Decls", "")
        stm.write_text("\n".join(lines))
    r = subprocess.run([sys.executable, "tools/trust_map.py", "--check"], capture_output=True, text=True)
    out.write_text(f"$ python3 tools/trust_map.py --check   # seed {seed}: {what}\n{r.stdout}{r.stderr}exit {r.returncode}\n")
finally:
    subprocess.run(["git", "checkout", "--", str(path)], check=True)
