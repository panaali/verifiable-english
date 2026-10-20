#!/usr/bin/env python3
"""speed-trustmut: run the probes of this directory (README) on this checkout and save their exit codes.

    uv run python docs/speed/trustmut/hunt/run.py [--jobs 4] [NAME ...]

Each `<name>.sh` runs from the checkout's root with Lean on PATH; its exit code, time and last output line go to
docs/speed/trustmut/evidence/probes.json with the commit and the sha256 of each of `SOURCES`, so a sentence that says
a probe passes cites this file, never a memory of a run (review F14, the DRI's note 2026-10-20). With names, only
those run, and the saved file keeps the other rows it had. `summary()` is the line the report and README quote.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

HUNT = Path(__file__).resolve().parent
ROOT = HUNT.parents[3]
SAVED = HUNT.parent / "evidence/probes.json"
# what a probe runs, and what F14-F16c read (the recheck of 4476e63a0: a saved exit code holds for these bytes only)
SOURCES = ("tools/trust_mutants.py", "tools/trust_map.py", "tests/test_trust_mutants.py", "docs/speed/trustmut/REPORT.md",
           "docs/speed/trustmut/claims.py", "docs/speed/trustmut/hunt/F15c.md")
# the report's quote of `summary()`, written from the saved runs after they ran, so not part of what they ran on
QUOTED = re.compile(rb"^ *> Probes on .*\n", re.M)
# not run: a mutant's build runs until --build-timeout (1,800 s by default), past the probe's own wait (README)
SKIP = {"T5w": "a mutant's build runs until --build-timeout", "T7": "a mutant's build runs until --build-timeout",
        "F14c": "it checks this file's sentences against this file: run after run.py"}
# exit non-zero by design: the hunt's decided boundaries (REPORT section 1e)
EXPECTED = {"N4": "boundary 1"}  # T6 (boundary 3) exits 0 since hunt 7: the fallback it reads is compared


def shas() -> dict[str, str]:
    return {s: hashlib.sha256(QUOTED.sub(b"", (ROOT / s).read_bytes())).hexdigest() for s in SOURCES}


def commit() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def one(name: str) -> dict:
    env = {**os.environ, "PATH": f"{Path.home() / '.elan/bin'}{os.pathsep}{os.environ.get('PATH', '')}"}
    started = time.monotonic()
    done = subprocess.run(["bash", str(HUNT / f"{name}.sh")], cwd=ROOT, env=env, capture_output=True, text=True)
    said = (done.stdout + done.stderr).strip().splitlines()
    return {"commit": commit(), "exit": done.returncode, "seconds": round(time.monotonic() - started),
            "last": (said or [""])[-1][-300:]}


def summary(data: dict | None = None) -> str:
    """One line from the saved runs: how many exit 0, which do not (and whether the README expects it), which were
    not run, and whether the sources they ran on (`SOURCES`) are this checkout's."""
    data = data or json.loads(SAVED.read_text())
    probes = data["probes"]
    ok = [n for n, p in probes.items() if p["exit"] == 0]
    bad = [f"{n} ({p['exit']}{', ' + EXPECTED[n] if n in EXPECTED else ', NOT EXPECTED'})" for n, p in probes.items()
           if p["exit"] != 0]
    now = "this checkout's" if data["sources"] == shas() else "NOT this checkout's"
    on = ", ".join(sorted({p["commit"][:9] for p in probes.values()}))
    return (f"Probes on {on} ({now} sources): {len(ok)} of {len(probes)} exit 0; non-zero: "
            f"{', '.join(bad) or 'none'}; not run: {', '.join(f'{n} ({why})' for n, why in data['skipped'].items())}.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("names", nargs="*")
    args = parser.parse_args()
    every = sorted(p.stem for p in HUNT.glob("*.sh"))
    names = [n for n in (args.names or every) if n not in SKIP]
    if missing := sorted(set(names) - set(every)):
        return print(f"no probe {missing}", file=sys.stderr) or 2
    dirty = subprocess.run(["git", "status", "--porcelain", "--", *SOURCES], cwd=ROOT, capture_output=True,
                           text=True).stdout.strip()
    if dirty:
        return print(f"the tool has uncommitted changes:\n{dirty}", file=sys.stderr) or 2
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        ran = dict(zip(names, executor.map(one, names)))
    old = json.loads(SAVED.read_text()) if args.names and SAVED.is_file() else {}
    if old and old["sources"] != shas():
        return print("the saved probes ran on another tool: run them all", file=sys.stderr) or 2
    data = {"sources": shas(), "skipped": {n: SKIP[n] for n in every if n in SKIP},
            "probes": dict(sorted({**old.get("probes", {}), **ran}.items()))}
    SAVED.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
    print(summary(data))
    return 0 if all(p["exit"] == 0 or n in EXPECTED for n, p in data["probes"].items()) else 1


if __name__ == "__main__":
    sys.exit(main())
