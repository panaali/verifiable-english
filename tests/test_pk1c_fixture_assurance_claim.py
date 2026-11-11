"""No docs/premise-packs/pk-1c/ record calls a `#guard` or `#eval` check a kernel check: those run in the compiled
evaluator, not the kernel (pk-1c-cfr-2). A line that cites Lean lines holding `#guard`/`#eval`, or names such a
check, must not say "kernel" (saying "not the kernel" is allowed)."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORDS = ROOT / "docs/premise-packs/pk-1c"
# `[lean/…/]X.lean:a[–b]`, or a bare `:a[–b]` continuing the last cited file.
CITE = re.compile(r"((?:lean/[\w/]+/)?[A-Za-z]\w*\.lean)?:(\d+)(?:[–-](\d+))?")
EVALUATED = re.compile(r"^\s*#(?:guard|eval)\b")
NOT_KERNEL = re.compile(r"\bnot (?:in |as )?(?:the |a )?kernel\b", re.IGNORECASE)


def _lean_lines(name: str) -> list[str]:
    paths = [ROOT / name] if name.startswith("lean/") else sorted((ROOT / "lean").rglob(name))
    assert len(paths) == 1 and paths[0].is_file(), f"{name} resolves to {paths}"
    return paths[0].read_text(encoding="utf-8").splitlines()


def cites_evaluated(line: str) -> bool:
    """The line cites a Lean line range in which some line is a `#guard` or `#eval` command."""
    name = ""
    for m in CITE.finditer(line):
        if m.group(1) is None and (not name or line[m.start() - 1] not in "`, "):
            continue
        name = m.group(1) or name
        lines = _lean_lines(name)
        start, end = int(m.group(2)), int(m.group(3) or m.group(2))
        assert 1 <= start <= end <= len(lines), f"{m.group(0)} lies outside {name}"
        if any(EVALUATED.match(text) for text in lines[start - 1 : end]):
            return True
    return False


def kernel_problems(records: dict[str, str]) -> list[str]:
    return [
        f"{name}:{n} calls a #guard/#eval check a kernel check: {line.strip()[:160]}"
        for name, text in records.items()
        for n, line in enumerate(text.splitlines(), 1)
        if "kernel" in NOT_KERNEL.sub("", line).lower()
        and (re.search(r"#(?:guard|eval)", line) or cites_evaluated(line))
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
    """Both directions: kernel claims about `#guard` lines are refused; kernel claims about theorems are not."""
    records = _records()
    old = records["REPORT.md"].replace("| (2c) #guard fixtures (compiled evaluator) ", "| (2c) kernel fixtures ")
    assert old != records["REPORT.md"]
    assert any("REPORT.md:" in p and "(2c)" in p for p in kernel_problems({**records, "REPORT.md": old}))
    assert kernel_problems({"x.md": "The `#eval` checks are kernel-checked."})
    assert kernel_problems({"x.md": "Kernel checks: `lean/VE/Bridge.lean:70`, `PacksLegacyExamples.lean:120`, `:134`."})
    assert not kernel_problems({"x.md": "The theorem is checked by the kernel."})
    theorem = "`legacy_labels_nodup_of_identifiers` (`PacksLabels.lean:392`) is checked by the kernel."
    assert not kernel_problems({"x.md": theorem})
    assert not kernel_problems({"x.md": "The #guard fixtures run in the compiled evaluator, not the kernel."})
