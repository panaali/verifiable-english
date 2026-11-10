"""Each "0 differences" claim of a premise-pack REPORT.md or DELTA.md cites a valid, passing differential record.

pk-1-cfr-1: a claim is a list item, paragraph or table row holding "0 differences". Each evidence file it cites
exists and has no "INVALID" on its first line, each cited differential record (a file mentioning "differences") ends
"exit 0", and at least one such passing record is cited.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKS = ROOT / "docs" / "premise-packs"
CLAIM = re.compile(r"(?<![\d,.])0\s+differences")
CITE = re.compile(r"(?:docs/premise-packs/[\w.-]+/)?evidence/[\w.-]+")
ITEM = re.compile(r"\s*([-*]|\d+\.)\s|\|")
# Exact records the scan flags that wording cannot fix (no exit line), each left to the named item.
FOLLOW_UPS = {"docs/premise-packs/pk-1b/evidence/ab_full.txt": "pk-1b-cfr-1"}


def _blocks(text: str) -> list[str]:
    blocks: list[list[str]] = [[]]
    for line in text.splitlines():
        if not line.strip() or ITEM.match(line):
            blocks.append([])
        blocks[-1].append(line)
    return ["\n".join(b) for b in blocks if "".join(b).strip()]


def _faults(pack: Path, follow_ups: dict[str, str]) -> list[tuple[Path | None, str]]:
    faults: list[tuple[Path | None, str]] = []
    exempt = {(ROOT / k).resolve() for k in follow_ups}
    for md in (pack / "REPORT.md", pack / "DELTA.md"):
        blocks = _blocks(md.read_text(encoding="utf-8")) if md.is_file() else []
        for block in filter(CLAIM.search, blocks):
            where, passing, n = f"{pack.name}/{md.name}: {block.strip()[:60]!r}", False, len(faults)
            for cited in sorted(set(CITE.findall(block))):
                path = (ROOT if cited.startswith("docs/") else pack).joinpath(cited).resolve()
                text = path.read_text(encoding="utf-8").strip() if path.is_file() else ""
                lines = text.splitlines() or [""]
                if path in exempt:
                    passing = True
                elif not text:
                    faults.append((path, f"{where} cites missing or empty {cited}"))
                elif "INVALID" in lines[0]:
                    faults.append((path, f"{where} cites {cited}, whose first line says INVALID"))
                elif "differences" in text and lines[-1].strip() != "exit 0":
                    faults.append((path, f"{where} cites {cited}, which ends {lines[-1][:40]!r}"))
                elif "differences" in text:
                    passing = True
            if not passing and len(faults) == n:
                faults.append((None, f"{where} cites no passing differential record"))
    return faults


def test_pk1_route_case_evidence_validity() -> None:
    dirs = sorted(p for p in PACKS.iterdir() if p.is_dir())
    assert PACKS / "pk-1" in dirs
    assert [m for d in dirs for _, m in _faults(d, FOLLOW_UPS)] == []


def test_follow_up_exemptions_are_still_needed() -> None:
    """Each exempt record is still flagged without its exemption, so it leaves FOLLOW_UPS once fixed."""
    for rel in FOLLOW_UPS:
        path = (ROOT / rel).resolve()
        assert path in {p for p, _ in _faults(path.parents[1], {})}, rel


def test_scan_refuses_and_accepts(tmp_path: Path) -> None:
    (ev := tmp_path / "evidence").mkdir()
    (ev / "ok.txt").write_text("baseline x\n9 invocations; 0 differences\nexit 0\n")
    (ev / "bad.txt").write_text("INVALID differential: no invocation\n0 differences\nexit 1\n")
    (ev / "exit1.txt").write_text("baseline x\n0 differences\nexit 1\n")
    (ev / "kinds.txt").write_text("recorded invocations 3\n")
    other = f"docs/premise-packs/{tmp_path.name}/evidence/bad.txt"
    cases = {
        "- run: **0 differences**\n  (`evidence/ok.txt`, `evidence/kinds.txt`).\n": [],
        "- run: 10 differences (`evidence/exit1.txt`).\n": [],
        "1. PASS: `evidence/bad.txt` (0 differences).\n": ["first line says INVALID"],
        "- run: **0\n  differences** (`evidence/exit1.txt`).\n": ["which ends 'exit 1'"],
        "- run: 0 differences (`evidence/kinds.txt`).\n": ["no passing differential record"],
        "- run: 0 differences.\n- `evidence/ok.txt`\n": ["no passing differential record"],
        "| T | 0 differences | `evidence/gone.txt` |\n| U | 0 differences | `evidence/ok.txt` |\n": ["missing"],
        f"- run: 0 differences (`{other}`).\n": ["missing or empty docs/premise-packs/"],
    }
    for text, expected in cases.items():
        (tmp_path / "REPORT.md").write_text(text)
        faults = [m for _, m in _faults(tmp_path, {})]
        assert len(faults) == len(expected) and all(e in f for e, f in zip(expected, faults)), (text, faults)
