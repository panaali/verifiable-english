"""No docs/premise-packs/pk-1c/ record calls a `#guard` or `#eval` check a kernel check: those run in the compiled
evaluator, not the kernel (pk-1c-cfr-2). A line that cites Lean lines holding `#guard`/`#eval`, or names such a
check, must not say "kernel"."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORDS = ROOT / "docs/premise-packs/pk-1c"
CITE = re.compile(r"`?([A-Za-z]\w*\.lean):(\d+)(?:[–-](\d+))?")
EVALUATED = re.compile(r"^\s*#(?:guard|eval)\b")


def _lean_lines(name: str) -> list[str]:
    paths = sorted((ROOT / "lean").rglob(name))
    assert len(paths) == 1, f"{name} resolves to {paths}"
    return paths[0].read_text(encoding="utf-8").splitlines()


def cites_evaluated(line: str) -> bool:
    """The line cites a Lean line range in which some line is a `#guard` or `#eval` command."""
    for name, start, end in CITE.findall(line):
        lines = _lean_lines(name)[int(start) - 1 : int(end or start)]
        if any(EVALUATED.match(text) for text in lines):
            return True
    return False


def kernel_problems(records: dict[str, str]) -> list[str]:
    return [
        f"{name}:{n} calls a #guard/#eval check a kernel check: {line.strip()[:160]}"
        for name, text in records.items()
        for n, line in enumerate(text.splitlines(), 1)
        if "kernel" in line.lower() and (re.search(r"#(?:guard|eval)", line) or cites_evaluated(line))
    ]


def _records() -> dict[str, str]:
    return {p.name: p.read_text(encoding="utf-8") for p in sorted(RECORDS.iterdir()) if p.is_file()}


def test_pk1c_fixture_assurance_claim() -> None:
    records = _records()
    assert "REPORT.md" in records
    assert kernel_problems(records) == []
    row = next(line for line in records["REPORT.md"].splitlines() if line.startswith("| (2c) "))
    assert row.startswith("| (2c) #guard fixtures (compiled evaluator) ") and cites_evaluated(row)


def test_pk1c_fixture_assurance_claim_refuses() -> None:
    """The base (2c) row and a "kernel" word beside a named `#guard` are refused; an uncited "kernel" is not."""
    records = _records()
    old = records["REPORT.md"].replace("| (2c) #guard fixtures (compiled evaluator) ", "| (2c) kernel fixtures ")
    assert old != records["REPORT.md"]
    assert any("REPORT.md:" in p and "(2c)" in p for p in kernel_problems({**records, "REPORT.md": old}))
    assert kernel_problems({"x.md": "The `#eval` checks are kernel-checked."})
    assert not kernel_problems({"x.md": "The theorem is checked by the kernel."})
