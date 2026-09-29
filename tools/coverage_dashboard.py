"""Rebuild the use-case baseline table without changing historical audits.

The per-use-case coverage.md files are immutable evidence for their own audit
date. Later verified closure results are recorded separately below.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
START = "<!-- W2-COVERAGE-START -->"
END = "<!-- W2-COVERAGE-END -->"
AUDITS = {
    "claude-constitution-excerpt": (0, 6, 5, 12, 23),
    "news-article": (1, 11, 3, 11, 26),
    "us-constitution-14th-s1": (0, 1, 3, 0, 4),
}
# Later audits of the same rows, recorded beside the dated originals.
REFRESHED = {
    "news-article": ("coverage-w6a.md", "W6a, 2026-09-28", (6, 4, 5, 12, 27)),
}


def baseline(root: Path = ROOT) -> str:
    rows = ["| Use case | DIRECT | REIFIED | OPAQUE | NO | Total |",
            "|---|---:|---:|---:|---:|---:|"]
    for name, counts in AUDITS.items():
        audit = (root / "usecases" / name / "coverage.md").read_text()
        found = re.search(r"(\d+) DIRECT, (\d+) REIFIED, (\d+) OPAQUE, (\d+) NO", audit)
        if not found or tuple(map(int, found.groups())) != counts[:4] or sum(counts[:4]) != counts[4]:
            raise ValueError(f"stale or inconsistent coverage audit: {name}")
        rows.append(f"| {name} | {' | '.join(map(str, counts))} |")
    rows.extend(["", "Later refreshed audits (the dated files above stay unchanged):", "",
                 "| Use case (refresh) | DIRECT | REIFIED | OPAQUE | NO | Total |",
                 "|---|---:|---:|---:|---:|---:|"])
    for name, (file, date, counts) in REFRESHED.items():
        audit = (root / "usecases" / name / file).read_text()
        found = re.search(r"(\d+) DIRECT,\s+(\d+) REIFIED, (\d+) OPAQUE, (\d+) NO", audit)
        if not found or tuple(map(int, found.groups())) != counts[:4] or sum(counts[:4]) != counts[4]:
            raise ValueError(f"stale or inconsistent refreshed audit: {name}")
        rows.append(f"| {name} ({date}) | {' | '.join(map(str, counts))} |")
    pilots = sorted((root / "usecases").glob("*/coverage.json"))
    debate = (root / "usecases/birthright-citizenship-debate/coverage.md").read_text()
    if "9 claims identified. 4 have a direct VE statement" not in debate:
        raise ValueError("stale birthright debate audit")
    rows.extend([
        "",
        "Other denominators: birthright debate has **4/9** claims with a direct VE statement "
        "and **5/9** unformalised; US Constitution Art. I §7 has no audited pilot yet.",
        "Math mini paper: **17/19** current verified outcomes (15 tableau certificates "
        "plus T9 and T9e by closure induction); its older `coverage.md` records the 15 tableau results. "
        "C1 is false, with a countermodel; T7mono remains resource-limited.",
        "These are claim/section labels, not source-byte coverage."
        + ("" if pilots else " The `.ve.md` pilot partition measurements are pending."),
    ])
    if pilots:
        rows.extend(["", "Measured `.ve.md` pilot partitions:", "",
                     "| Document | Accounted bytes | Source bytes | Residual |",
                     "|---|---:|---:|---:|"])
    for path in pilots:
        data = json.loads(path.read_text())
        source = data.get("source_bytes")
        accounted = data.get("accounted_bytes")
        residual = data.get("residual_total")
        if (type(source) is not int or source <= 0 or accounted != source
                or type(residual) is not int or residual < 0):
            raise ValueError(f"invalid partition coverage: {path}")
        rows.append(f"| {path.parent.name} | {accounted} | {source} | {residual} |")
    return "\n".join(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="update the marked ROADMAP table")
    args = parser.parse_args()
    table = baseline()
    if not args.write:
        print(table)
        return
    path = ROOT / "ROADMAP.md"
    old = path.read_text()
    replacement = START + "\n" + table + "\n" + END
    if START in old:
        if old.count(START) != 1 or old.count(END) != 1:
            raise ValueError("invalid ROADMAP coverage markers")
        updated = old[:old.index(START)] + replacement + old[old.index(END) + len(END):]
    else:
        marker = "## 3. Wrap-up state"
        updated = old.replace(marker, "## 2a. W2 use-case baseline (2026-09-26)\n\n" + replacement + "\n\n" + marker, 1)
    path.write_text(updated)


if __name__ == "__main__":
    main()
