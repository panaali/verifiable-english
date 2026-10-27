"""Seeded bugs of ap-1bc: one per claimed behaviour of `VE.Words.regulatedOf`, planted, run and restored.

    uv run python docs/act-phrases/ap-1bc/seed_bugs.py [--only ID ...]

As ap-1bb's: each mutant replaces one exact text in one file (it must occur once) and runs its check, a Lean module
build (killed when it fails; the first error line is recorded); the file is restored, and the touched Lean modules
are rebuilt. Results go to `mutants.json`. No Python or Rust product code changed.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
S, EX = "lean/VE/Words/Situation.lean", "lean:VE.Service.ActsExamples"
PS = "  let ps := VE.Norms.Wire.actsProfiles true E.source\n"

# (id, definition, file, old, new, check)
MUTANTS = [
    # the base decoder (ap-1bb review F3): `acts@0`'s plain, long and fixed-phrase acts are not regulated
    ("regulatedOf-base-decoder", "VE.Words.regulatedOf", S, "(VE.Norms.Wire.decodeRegulatedIn ps fx p d.args raw)",
     "(VE.Norms.Wire.decodeRegulated p d.args raw)", EX),
    # `acts@0` never read from the profiles
    ("regulatedOf-acts-unread", "VE.Words.regulatedOf", S, PS,
     "  let ps := VE.Norms.Wire.actsProfiles false E.source\n", EX),
    # `acts@0` read from a list that is not sorted and unique (`readsActs` skipped)
    ("regulatedOf-any-list", "VE.Words.regulatedOf", S, PS,
     "  let ps := (VE.Route.Gate.profilesOf E.source).toOption.getD []\n", EX),
    # the block's fixed phrases not read
    ("regulatedOf-block-unread", "VE.Words.regulatedOf", S, "(VE.Norms.Wire.actsFixed ps E.source).toOption",
     "(VE.Norms.Wire.actsFixed [] E.source).toOption", EX),
]
ENV = dict(os.environ, PATH=os.path.expanduser("~/.elan/bin") + ":" + os.environ["PATH"])


def run(check: str) -> tuple[bool, str]:
    if check.startswith("lean:"):
        done = subprocess.run(["lake", "build", check[5:]], cwd=ROOT / "lean", env=ENV, capture_output=True, text=True)
        first = next((m.group(0) for m in re.finditer(r"error: [^\s:]+\.lean:\d+:\d+[^\n]*", done.stdout + done.stderr)),
                     "")
        return done.returncode != 0, first[:200]
    sys.path.insert(0, str(ROOT))
    from tools.nested_pytest import command, environment
    done = subprocess.run(command(["-q", "-x", check], python=("uv", "run", "python")), cwd=ROOT,
                          env=environment(ENV), capture_output=True, text=True)
    failed = next((line for line in done.stdout.splitlines() if line.startswith("FAILED")), "")
    return done.returncode != 0, failed[:200]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", nargs="*")
    args = parser.parse_args()
    out = ROOT / "docs/act-phrases/ap-1bc/mutants.json"
    listed = {m[0] for m in MUTANTS}
    results = {k: v for k, v in (json.loads(out.read_text()) if out.exists() else {}).items() if k in listed}
    touched = set()
    for ident, definition, file, old, new, check in MUTANTS:
        if args.only and ident not in args.only:
            continue
        path = ROOT / file
        text = path.read_text()
        assert text.count(old) == 1, (ident, file, text.count(old))
        path.write_text(text.replace(old, new))
        try:
            killed, line = run(check)
        finally:
            path.write_text(text)
        if file.startswith("lean/"):
            touched.add(check[5:])
        results[ident] = {"definition": definition, "file": file, "test": check.removeprefix("lean:"),
                          "killed": killed, "first_failure": line}
        print(ident, "KILLED" if killed else "SURVIVED", line, flush=True)
        out.write_text(json.dumps(results, indent=1, ensure_ascii=False) + "\n")
    for module in sorted(touched):  # the restored sources' modules, so no stale build is left
        subprocess.run(["lake", "build", module], cwd=ROOT / "lean", env=ENV, capture_output=True, check=True)
    return 0 if all(r["killed"] for r in results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
