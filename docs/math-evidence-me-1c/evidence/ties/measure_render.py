"""ties-me-1c: per-declaration trust of VE/Calc/Render.lean and every dumped theorem naming one."""
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
sys.path.insert(0, str(root / "tools"))
import trust_map
decls, lines, problems = trust_map.walk(root)
rows = [{"declaration": c.decl.name, "class": c.cls, "tied": c.tied, "trusted": c.trusted,
         "lines": c.decl.lines, "start": c.decl.start, "end": c.decl.end}
        for c in decls if c.module == "VE/Calc/Render.lean" and c.decl.name]
names = {r["declaration"] + "@VE.Calc.Render" for r in rows}
text = (root / "lean/statements.txt").read_text().split("\n")
theorem, naming = None, []
for line in text:
    if line.startswith("theorem "):
        theorem = line.split()[1]
    elif line.strip().startswith("-- uses") and theorem:
        hit = sorted(names & set(line.split()[2:]))
        if hit:
            naming.append({"theorem": theorem, "names": hit})
print(json.dumps({"problems": problems, "file_lines": lines.get("VE/Calc/Render.lean"),
                  "declarations": rows, "trusted_total": sum(r["lines"] for r in rows if r["trusted"]),
                  "theorems_naming_one": naming,
                  "theorems_in_dump": sum(1 for l in text if l.startswith("theorem "))}, indent=1))
