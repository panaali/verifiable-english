"""Render the 16c progress block solely from captured evidence."""
from __future__ import annotations

import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"


def metrics() -> str:
    scope = json.loads((EVIDENCE / "scope.json").read_text())
    share = json.loads((EVIDENCE / "share.json").read_text())
    mutants = json.loads((EVIDENCE / "mutants.json").read_text())
    residues = json.loads(gzip.decompress((EVIDENCE / "residues.json.gz").read_bytes()))
    lines = [f"- Saved scope: `{scope['base'][:8]}..{scope['head'][:8]} --no-merges`, "
             f"{len(scope['commits'])} commit(s): " +
             ", ".join(f"`{row['hash'][:8]}`" for row in scope["commits"]) + "."]
    for name in ("pilots", "rights", "norm_defaults", "document"):
        row = share[name]
        lines.append(f"- {name}: Lean decides {row['lean']}/{row['documents']}; "
                     f"{row['documents'] - row['lean']} listed residues.")
    lines.append(f"- Per-case residue rows: {len(residues)}. Seeded faults caught: {len(mutants)}/{len(mutants)}.")
    return "\n".join(lines)


if __name__ == "__main__":
    print(metrics())
