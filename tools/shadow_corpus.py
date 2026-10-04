"""Corpus commands of Stage 3 shadow mode that are not a pytest selection.

``tools/shadow_run.py`` runs each corpus command of ``conformance/shadow/corpora.json``
with ``VE_AUTHORITY=shadow``; the command reports how many cases it ran by
writing ``{"cases": N}`` to the file named by ``VE_SHADOW_CASES``
(docs/spec/mig3.md 2.8).  The pytest corpora do that through the plugin
``tools/shadow_pytest.py``; the others are subcommands here:

* ``baseline``: every cell of the Stage 0 probe matrix (``tests/probe_matrix.py``);
* ``fuzz --count N --seed S``: ``conformance/fuzz.py`` (5,000 core pairs);
* ``fuzz-closure --count N --seed S``: ``rust/fuzz_closure.py`` (3,000 closure pairs);
* ``english``: ``conformance/english_lean.py --full`` (85,000 pairs);
* ``pilots``: ``python -m ve document check`` on every ``usecases/**/*.ve.md``.

``--seed day`` takes the seed of the day the run started: the eight digits of
the UTC date (2.9).  Each subcommand exits 0 when its generator finished, and
with the generator's own status otherwise.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def report_cases(cases: int) -> None:
    target = os.environ.get("VE_SHADOW_CASES")
    if target:
        Path(target).write_text(json.dumps({"cases": cases}) + "\n")


def day_seed(text: str) -> int:
    if text == "day":
        started = os.environ.get("VE_SHADOW_STARTED")
        day = (datetime.strptime(started, "%Y-%m-%dT%H:%M:%SZ") if started
               else datetime.now(timezone.utc))
        return int(day.strftime("%Y%m%d"))
    return int(text)


def baseline() -> int:
    sys.path.insert(0, str(ROOT))
    from tests import probe_matrix
    data = probe_matrix.generate()
    report_cases(len(data["cells"]))
    return 0


def _script(argv: list[str], output: Path) -> int:
    completed = subprocess.run([sys.executable, *argv], cwd=ROOT)
    if completed.returncode != 0:
        return completed.returncode
    report_cases(sum(1 for _ in output.open()))
    return 0


def fuzz(count: int, seed: int, closure: bool) -> int:
    with tempfile.TemporaryDirectory() as scratch:
        output = Path(scratch) / ("closure-fuzz.jsonl" if closure else "fuzz.jsonl")
        script = "rust/fuzz_closure.py" if closure else "conformance/fuzz.py"
        return _script([script, "--count", str(count), "--seed", str(seed), "--output", str(output)], output)


def english() -> int:
    with tempfile.TemporaryDirectory() as scratch:
        output = Path(scratch) / "english-lean-report.json"
        completed = subprocess.run([sys.executable, "-m", "conformance.english_lean", "--per-vocabulary", "5000",
                                    "--full", "--output", str(output)], cwd=ROOT)
        if completed.returncode != 0:
            return completed.returncode
        report_cases(json.loads(output.read_text())["pairs"])
        return 0


def pilots() -> int:
    documents = sorted((ROOT / "usecases").rglob("*.ve.md"))
    crashed = 0
    for document in documents:
        completed = subprocess.run([sys.executable, "-m", "ve", "document", "check", str(document)],
                                   cwd=ROOT, stdout=subprocess.DEVNULL)
        # 0 and 1 are the command's verdicts; anything else is a crash of the check.
        if completed.returncode not in (0, 1):
            crashed += 1
            print(f"shadow corpus pilots: {document.relative_to(ROOT)} exited {completed.returncode}",
                  file=sys.stderr)
    report_cases(len(documents))
    return 1 if crashed else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("baseline")
    for name, count, seed in (("fuzz", 5000, "20260922"), ("fuzz-closure", 3000, "20260924")):
        sub = commands.add_parser(name)
        sub.add_argument("--count", type=int, default=count)
        sub.add_argument("--seed", default=seed)
    commands.add_parser("english")
    commands.add_parser("pilots")
    args = parser.parse_args(argv)
    if args.command == "baseline":
        return baseline()
    if args.command in ("fuzz", "fuzz-closure"):
        return fuzz(args.count, day_seed(args.seed), args.command == "fuzz-closure")
    return english() if args.command == "english" else pilots()


if __name__ == "__main__":
    raise SystemExit(main())
