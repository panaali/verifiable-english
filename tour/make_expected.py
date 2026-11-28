"""Run every stop of the tour and record what it printed: tour/expected/<stop>.txt, and the same output in the
page's blocks (tour/README.md, between "<!-- output <stop> -->" and "<!-- /output -->"). Also writes each stop's
seconds to tour/expected/seconds.json (not compared by the test: times vary).

Run from the repository root after sh tour/install.sh:  uv run --frozen python tour/make_expected.py
tests/test_tour.py fails when a stop's output, or the page, drifts from these files.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

TOUR = Path(__file__).resolve().parent
ROOT = TOUR.parent
STOPS = ("01-yes", "02-not-necessarily", "03-every-or-some", "04-date", "05-sum", "06-checker", "07-company-policy",
         "08-outside-the-text", "09-planted-mistake", "10-not-yet", "11-longer-example",
         "12-write-your-own")
AFTER_RELEASE = {"04-date", "05-sum", "07-company-policy", "09-planted-mistake", "10-not-yet"}
# The page shows part of a long output (the file under tour/expected/ has all of it): its first lines, the first lines
# of its assumptions, and every "Lean check:" line (one per answer) with the "Translation:" line after it
# (tour/stops/status.py), chosen by content so a regenerated output keeps showing the same parts.
EXCERPT_START, ASSUMPTIONS, LEAN_CHECK, STATUS = 32, "Assumptions (taken as given", "Lean check:", "Translation:"
EXCERPTS = {"06-checker"}
# uv's own progress lines, in their exact shapes (it may rebuild the project's package on the first run in a
# checkout): not the stop's output
UV_NOISE = re.compile(r"^ *(?:(?:Building|Built) [\w.-]+ @ file://\S+$|(?:Uninstalled|Installed|Resolved|Prepared|Audited)"
                      r" \d+ packages? in [\d.]+m?s$|Using CPython \S+ interpreter at: \S+$)")


def run_stop(stop: str, env: dict | None = None) -> tuple[str, float]:
    # without the caller's VIRTUAL_ENV (`uv run` sets it): the after-release stops run uv in their own checkout, where
    # uv would warn that it does not match
    # `ve read` (stop 12) must not use this machine's reader settings: no reader program, VE's settings in an empty
    # directory of their own (VE_SETTINGS_DIR; not XDG_CONFIG_HOME, which uv reads too), and its one-time reader offer
    # counted as made (ve/word_senses.py first_run; tour/stops/common.sh sets it too)
    env = {k: v for k, v in (os.environ if env is None else env).items() if k not in ("VIRTUAL_ENV", "VE_WORD_READER")}
    env["VE_READER_OFFER"] = "off"
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="ve-tour-settings-") as settings:
        env["VE_SETTINGS_DIR"] = settings
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
    lines = output.splitlines()
    groups = [lines[:EXCERPT_START]]
    first = next(i for i, line in enumerate(lines) if line.startswith(ASSUMPTIONS))
    groups.append(lines[first:first + 4])
    groups.extend(lines[i:i + 2] if lines[i + 1:i + 2] and lines[i + 1].startswith(STATUS) else [line]
                  for i, line in enumerate(lines) if line.startswith(LEAN_CHECK))
    parts = []
    for group in groups:
        if parts:
            parts.append("...")
        parts.extend(group)
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
    merged = {**old, **{k: round(v, 1) for k, v in seconds.items()}}
    (expected / "seconds.json").write_text(json.dumps({k: merged[k] for k in STOPS if k in merged}, indent=1) + "\n")
    page = TOUR / "README.md"
    page.write_text(with_blocks(page.read_text(encoding="utf-8"), outputs), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1:])
