"""Render batch 16d metrics from committed evidence only."""
from __future__ import annotations

from collections import Counter
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"


def data(name: str):
    path = EVIDENCE / name
    if name.endswith(".gz"):
        return json.loads(gzip.decompress(path.read_bytes()))
    return json.loads(path.read_text())


def metrics() -> str:
    scope = data("scope.json")
    cases = data("cases.json.gz")
    ab = data("ab.json")
    gate = data("gate.json")
    mutants = data("mutants.json")
    lines = [f"- Saved scope: `{scope['base'][:8]}..{scope['head'][:8]} --no-merges`, "
             f"{len(scope['commits'])} commit(s): " +
             ", ".join(f"`{c['hash'][:8]}`" for c in scope["commits"]) + "."]
    for name, label in (("norm_defaults", "norm-defaults"), ("document", "document-corpus"),
                        ("pilots", "pilots")):
        group = [r for r in cases if r["corpus"] == name]
        count = Counter(r["decision"] for r in group)
        lines.append(f"- {label}: Lean decided {count['ok'] + count['error']}/{len(group)}; "
                     f"{count['retained']} saved invalid-input residues.")
    lines.append(f"- Nine-corpus A/B: {sum(ab['records'].values())} records per side; "
                 f"{ab['unlisted']} unlisted differences.")
    lines.append(f"- Seeded faults caught: {len(mutants)}/{len(mutants)}. "
                 f"Clean gate: {gate['status']}, {gate['counts']['passed']} passed, "
                 f"{gate['counts']['skipped']} skipped, {gate['counts']['failed']} failed.")
    return "\n".join(lines)


if __name__ == "__main__":
    print(metrics())
