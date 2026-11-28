"""The line after each Lean line: stops 6, 7, 9 and 12 pass their output through this filter, which copies it and adds
one line starting "Translation:" after each Lean line (in stop 9, which has no Lean check, after each answer), so that
"15 of 15" or "CHECKED" is not read as a score of the translation. The line's words come from one place: the table
"The line after each Lean line" in tour/TEXTS.md (the line is "Translation: " and that stop's cells, joined by "; ").

Run:  <a stop's command> | python tour/stops/status.py <stop number>
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

TEXTS = Path(__file__).resolve().parents[1] / "TEXTS.md"
HEADING = "## The line after each Lean line"
PREFIX = "Translation: "
# Each stop's Lean line, matched after its indent. A Lean line's block (its following lines indented further, such as
# stop 12's sentence lines) stays together: the line goes after the block, with the Lean line's own indent.
LEAN_LINE = {
    "6": re.compile(r"Lean check: "),               # one per answer: its proof steps, each accepted by Lean
    "7": re.compile(r"(?:yes|no)$"),                # the policy program's answer, given only when Lean accepts each step
    "9": re.compile(r"policy alone: "),             # each answer compared (this stop's answers use no Lean)
    "12": re.compile(r"Lean read every sentence: "),  # then one indented line per sentence
}


def lines_by_stop(texts: str) -> dict:
    """{stop number: its line}, from the table under HEADING in tour/TEXTS.md."""
    section = texts.split(HEADING + "\n", 1)[1].split("\n## ", 1)[0]
    rows = [line for line in section.splitlines() if line.startswith("|")][2:]  # past the header and its rule
    found = {}
    for row in rows:
        stops, *cells = [cell.strip() for cell in row.strip("|").split("|")]
        for stop in re.split(r",\s*", stops):
            found[stop] = PREFIX + "; ".join(cell for cell in cells if cell)
    return found


def annotate(lines, stop: str, status: str):
    """Yield the lines, with `status` after each Lean line's block."""
    pattern, open_indent = LEAN_LINE[stop], None
    for line in lines:
        body = line.lstrip()
        indent = line[:len(line) - len(body)]
        if open_indent is not None and not (body and len(indent) > len(open_indent)):
            yield open_indent + status
            open_indent = None
        yield line
        if pattern.match(body):
            open_indent = indent
    if open_indent is not None:
        yield open_indent + status


def main(argv) -> int:
    if len(argv) != 1 or argv[0] not in LEAN_LINE:
        print(f"usage: <command> | python tour/stops/status.py <stop: {', '.join(LEAN_LINE)}>", file=sys.stderr)
        return 2
    stop = argv[0]
    status = lines_by_stop(TEXTS.read_text(encoding="utf-8")).get(stop)
    if status is None:
        print(f'tour/TEXTS.md has no row for stop {stop} under "{HEADING}"', file=sys.stderr)
        return 1
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    for line in annotate((line.rstrip("\n") for line in sys.stdin), stop, status):
        print(line, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
