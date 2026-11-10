"""A premise-pack report that claims "0 differences" cites a valid, passing differential record.

pk-1-cfr-1 (DRI 2026-11-10): pk-1's REPORT and DELTA cited the 33 route cases as "0 differences" while
`evidence/ab_route_cases.txt` says "INVALID differential" and ends "exit 1". A claim is a list item, paragraph
or table row of a docs/premise-packs/*/REPORT.md or DELTA.md holding "0 differences". Every evidence file the
claim cites must have no "INVALID" on its first line; every cited differential record (a file that mentions
"differences") must end "exit 0"; and the claim must cite at least one such passing record.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKS = ROOT / "docs" / "premise-packs"
CLAIM = re.compile(r"(?<![\d,.])0 differences")
CITE = re.compile(r"evidence/[\w.-]+")
ITEM = re.compile(r"\s*([-*]|\d+\.)\s|\|")
# Exact paths flagged by the scan and left to their own item (not a wording fix: the record has no exit line).
FOLLOW_UPS = {"docs/premise-packs/pk-1b/evidence/ab_full.txt": "pk-1b-cfr-1"}


def _blocks(text: str) -> list[str]:
    """Split markdown into list items, table rows and paragraphs."""
    blocks: list[list[str]] = []
    for line in text.splitlines():
        if not line.strip():
            blocks.append([])
        elif ITEM.match(line) or not blocks:
            blocks.append([line])
        else:
            blocks[-1].append(line)
    return ["\n".join(b) for b in blocks if b]


def _faults(pack_dir: Path, follow_ups: dict[str, str]) -> list[str]:
    faults, exempt = [], {(ROOT / k).resolve() for k in follow_ups}
    for md in (pack_dir / "REPORT.md", pack_dir / "DELTA.md"):
        if not md.is_file():
            continue
        for block in filter(CLAIM.search, _blocks(md.read_text(encoding="utf-8"))):
            where = f"{md.relative_to(pack_dir.parent)}: {block.strip()[:70]!r}"
            passing = False
            for cited in sorted(set(CITE.findall(block))):
                path = pack_dir / cited
                if path.resolve() in exempt:
                    passing = True
                    continue
                lines = path.read_text(encoding="utf-8").strip().splitlines() if path.is_file() else []
                if not lines:
                    faults.append(f"{where} cites missing or empty {cited}")
                elif "INVALID" in lines[0]:
                    faults.append(f"{where} cites {cited}, whose first line says INVALID")
                elif "differences" in "\n".join(lines):
                    if lines[-1].strip() != "exit 0":
                        faults.append(f"{where} cites {cited}, which ends {lines[-1].strip()[:40]!r}")
                    else:
                        passing = True
            if not passing and not any(where in f for f in faults):
                faults.append(f"{where} cites no passing differential record")
    return faults


def test_pk1_route_case_evidence_validity() -> None:
    dirs = sorted(p for p in PACKS.iterdir() if p.is_dir())
    assert PACKS / "pk-1" in dirs
    assert [f for d in dirs for f in _faults(d, FOLLOW_UPS)] == []


def test_follow_up_exemptions_are_still_needed() -> None:
    """Each exempted record is still flagged without its exemption, so it leaves the list when fixed."""
    for path in FOLLOW_UPS:
        assert _faults((ROOT / path).parents[1], {}) != [], path


def test_scan_refuses_and_accepts(tmp_path: Path) -> None:
    ev = tmp_path / "evidence"
    ev.mkdir()
    (ev / "ok.txt").write_text("baseline x\n9 invocations; 0 differences\nexit 0\n")
    (ev / "bad.txt").write_text("INVALID differential: no invocation\n0 differences\nexit 1\n")
    (ev / "exit1.txt").write_text("baseline x\n0 differences\nexit 1\n")
    (ev / "kinds.txt").write_text("recorded invocations 3\n")
    cases = {
        "- run: **0 differences**\n  (`evidence/ok.txt`, `evidence/kinds.txt`).\n": [],
        "- run: 10 differences (`evidence/exit1.txt`).\n": [],
        "1. PASS: `evidence/bad.txt` (0 differences).\n": ["first line says INVALID"],
        "- run: 0 differences (`evidence/exit1.txt`).\n": ["which ends 'exit 1'"],
        "- run: 0 differences (`evidence/kinds.txt`).\n": ["no passing differential record"],
        "- run: 0 differences.\n- `evidence/ok.txt`\n": ["no passing differential record"],
        "| T | 0 differences | `evidence/gone.txt` |\n": ["missing or empty"],
    }
    for text, expected in cases.items():
        (tmp_path / "REPORT.md").write_text(text)
        faults = _faults(tmp_path, {})
        assert len(faults) == len(expected) and all(e in f for e, f in zip(expected, faults)), (text, faults)
