"""Per-file and per-declaration trust counts of kb-2a-b's files (kb-2a-b-cutback evidence).

    uv run python docs/kernel/kb-2a-b-cutback/trust_decls.py OUT.json

Reads the tree through `tools/trust_map.py`'s one validating pass (`walk`) and its per-file counts
(`measure`); writes, for each file below, the per-file counts and every declaration with its class, tie
flag, trusted flag and lines. The counted trusted lines are trust_map's `trusted` column (K + S + untied [V]).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import trust_map  # noqa: E402

FILES = ["VE/Service/CoreCheck.lean", "VE/Kernel/DocumentFold.lean", "VE/Service/Document.lean",
         "ResponseShape/Schemas/Document.lean", "ResponseShape/Schemas/SoftNorms.lean", "VE/Compose/SlotWire.lean",
         "VE/SoftNorms/Run.lean", "VE/Service/CoreDocument.lean"]


def main(out: Path) -> int:
    decls, _, problems = trust_map.walk()
    files, _ = trust_map.measure()
    rows = {f: {"counts": files[f], "declarations": []} for f in FILES}
    for d in decls:
        if d.module in rows:
            rows[d.module]["declarations"].append(
                {"name": d.decl.name, "class": d.cls, "tied": d.tied, "trusted": d.trusted, "lines": d.decl.lines})
    total = {k: sum(r["counts"][k] for r in rows.values()) for k in ("K", "S", "trusted", "tied")}
    json.dump({"files": rows, "total": total, "problems": problems}, out.open("w"), indent=1)
    out.open("a").write("\n")
    print(json.dumps(total), "problems:", len(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1])))
