"""Run every stop of the tour and record what it printed: tour/expected/<stop>.txt, and the same output in the
page's blocks (tour/README.md, between "<!-- output <stop> -->" and "<!-- /output -->"). Also writes each stop's
seconds to tour/expected/seconds.json (not compared by the test: times vary).

Run from the repository root after sh tour/install.sh:  uv run --frozen python tour/make_expected.py
tests/test_tour.py fails when a stop's output, or the page, drifts from these files.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys
import time

TOUR = Path(__file__).resolve().parent
ROOT = TOUR.parent
STOPS = ("01-yes", "02-not-necessarily", "03-two-readings", "04-date", "05-sum", "06-checker", "07-company-policy",
         "08-outside-the-text", "09-planted-mistake", "10-not-yet")
AFTER_RELEASE = {"04-date", "05-sum", "07-company-policy", "09-planted-mistake", "10-not-yet"}
# The page shows these lines (1-based, inclusive) of a long output; the file under tour/expected/ has all of it.
EXCERPTS = {"06-checker": ((1, 29), (173, 176), (228, 228), (330, 330), (357, 357), (374, 374))}
# uv's own progress lines (it may rebuild the project's package on the first run in a checkout): not the stop's output
UV_NOISE = re.compile(r"^\s*(Building|Built|Uninstalled|Installed|Resolved|Prepared|Audited|Using) ")


def run_stop(stop: str, env: dict | None = None) -> tuple[str, float]:
    started = time.monotonic()
    done = subprocess.run(["sh", str(TOUR / "stops" / f"{stop}.sh")], cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=1800)
    lines = [line for line in done.stdout.splitlines() if not UV_NOISE.match(line)]
    if done.returncode:
        lines.append(f"[the stop script itself exited with code {done.returncode}]")
    return "\n".join(lines) + "\n", time.monotonic() - started


def shown(stop: str, output: str) -> str:
    """What the page shows of a stop's output."""
    if stop not in EXCERPTS:
        return output
    lines, parts = output.splitlines(), []
    for first, last in EXCERPTS[stop]:
        if parts:
            parts.append("...")
        parts.extend(lines[first - 1:last])
    parts.append(f"... ({len(lines)} lines in all: tour/expected/{stop}.txt)")
    return "\n".join(parts) + "\n"


def page_blocks(page: str) -> dict:
    return {m[1]: m[2] for m in re.finditer(r"<!-- output (\S+) -->\n```text\n(.*?)```\n<!-- /output -->", page, re.S)}


def with_blocks(page: str, outputs: dict) -> str:
    def block(m):
        stop = m[1]
        return f"<!-- output {stop} -->\n```text\n{shown(stop, outputs[stop])}```\n<!-- /output -->"
    return re.sub(r"<!-- output (\S+) -->\n```text\n.*?```\n<!-- /output -->", block, page, flags=re.S)


def main(argv):
    stops = argv or STOPS
    outputs, seconds = {}, {}
    expected = TOUR / "expected"
    expected.mkdir(exist_ok=True)
    for stop in stops:
        outputs[stop], seconds[stop] = run_stop(stop)
        (expected / f"{stop}.txt").write_text(outputs[stop], encoding="utf-8")
        print(f"{stop}: {seconds[stop]:.1f} s")
    for stop in STOPS:
        if stop not in outputs:
            outputs[stop] = (expected / f"{stop}.txt").read_text(encoding="utf-8")
    old = json.loads((expected / "seconds.json").read_text()) if (expected / "seconds.json").exists() else {}
    (expected / "seconds.json").write_text(json.dumps({**old, **{k: round(v, 1) for k, v in seconds.items()}},
                                                      indent=1) + "\n")
    page = TOUR / "README.md"
    page.write_text(with_blocks(page.read_text(encoding="utf-8"), outputs), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1:])
