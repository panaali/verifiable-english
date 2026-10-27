"""Seeded bugs of ap-1be: one per claimed behaviour of the norm-defaults route's `wordings`, planted, run and restored.

    uv run python docs/act-phrases/ap-1be/seed_bugs.py [--only ID ...]

As ap-1bc's: each mutant replaces one exact text in one file (it must occur once) and runs its check, a Lean module
build (killed when it fails; the first error line is recorded) or a pytest node (killed when it fails; the first
FAILED line). The file is restored, and the touched Lean modules are rebuilt. Results go to `mutants.json`. No Rust
code changed.
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
RUN, NR = "lean/VE/NormDefaults/Run.lean", "lean/VE/Norms/Run.lean"
SHAPE, NORMS, ND = "lean/ResponseShape/Schemas/NormDefaults.lean", "ve/norms.py", "ve/norm_defaults.py"
EX, ENC = "lean:VE.Service.ActsExamples", "lean:ResponseShape.Encoders.NormDefaults"
TESTS = "tests/test_acts_profile.py::"
READS = TESTS + "test_a_norm_defaults_environment_reads_with_the_wording_lean_selected"
BOUND = TESTS + "test_norm_defaults_wordings_not_bound_to_the_request_are_unavailable"
MEMBER = '("document_hash", .str documentHash),\n       ("wordings", VE.Norms.Run.wordingsJson s.src.ne)])'
ASK = '    mode = "norm-defaults" if NORM_DEFAULTS_PROFILE in env.profiles else "norms"\n'

# (id, definition, file, old, new, check)
MUTANTS = [
    # Lean (1): the row gives the source's wordings, typed by its closed shape and the encoder theorem
    ("nd-wordings-dropped", "VE.NormDefaults.Run.runOtherCase", RUN, MEMBER,
     '("document_hash", .str documentHash)])', EX),
    ("nd-wordings-renamed", "VE.NormDefaults.Run.runOtherCase", RUN, MEMBER,
     MEMBER.replace('("wordings"', '("wording"'), ENC),
    ("wordingsJson-names", "VE.Norms.Run.wordingsJson", NR, "fun (p, w) => (p, .str w)", "fun (p, _) => (p, .str p)",
     EX),
    ("shape-wordings-strings", "ResponseShape.Schemas.NormDefaults.elaborate", SHAPE,
     '[ref "common.json#/$defs/string_map"])])]', '[ref "common.json#/$defs/strings"])])]', ENC),
    # Python (1): a norm-defaults@0 environment asks norm-defaults-elaborate, and both readers bind it (R8)
    ("py-nd-not-asked", "ve.norms.plain_wordings", NORMS, "    if not _plain_acts(env):\n",
     "    if not _plain_acts(env) or NORM_DEFAULTS_PROFILE in env.profiles:\n", READS),
    ("py-nd-norms-mode", "ve.norms.plain_wordings", NORMS, ASK, '    mode = "norms"\n', READS),
    ("py-nd-document-unbound", "ve.norm_defaults.UnspecifiedDocument", ND,
     '        _bind_wordings(self.env, row, "norm-defaults-elaborate")\n', "", BOUND),
    ("py-bind-subset", "ve.norms._bind_wordings", NORMS, "if set(wordings) != _plain_acts(env) or",
     "if not set(wordings) <= _plain_acts(env) or", BOUND),
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
    out = ROOT / "docs/act-phrases/ap-1be/mutants.json"
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
