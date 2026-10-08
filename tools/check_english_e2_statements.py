"""Check the twelve E2 theorem statements against the approved section 5.5 text, with Lean as the oracle.

    python tools/check_english_e2_statements.py

The approved block of docs/spec/english-lean-e2.md 5.5 is split into its twelve `theorem` statements (our own
spec's format: each starts a line with `theorem <name>`). For each, a scratch Lean file states the approved text
as a theorem proved by the built theorem of the same name, in the namespace the build declares it:
`theorem approved_<name> : <approved statement> := @<name>`. Lean elaborates the approved text and checks that the
built theorem proves it, so a statement that changed, weakened or vanished fails here, whatever its source
spelling. No Lean source is read as text (build checklist 11). Needs the built `VE` library.
"""

from pathlib import Path
import os
import re
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/spec/english-lean-e2.md"
LAKE = shutil.which("lake") or "lake"
# Where each approved theorem lives in the build, with the file's own `open` (the spec states them in
# `VE.EnglishGrammar` over `VE.Grammar`; the class table's theorem is `Run`'s, beside `codeClasses`, and the senses
# theorem is stated over `VE.Senses`).
PLACES = {"codeClasses_total": ("VE.EnglishGrammar.Run", "Lean VE.Grammar VE.EnglishGrammar"),
          "sensesRequest_policy": ("VE.EnglishGrammar", "VE.Senses")}
DEFAULT_PLACE = ("VE.EnglishGrammar", "VE.Grammar")


def approved() -> list[tuple[str, str]]:
    section = SPEC.read_text().split("### 5.5 The statements", 1)[1].split("### 5.6", 1)[0]
    block = section.split("```lean", 1)[1].split("```", 1)[0]
    starts = list(re.finditer(r"^theorem (\w+)\b", block, re.M))
    return [(m[1], block[m.end():(starts[k + 1].start() if k + 1 < len(starts) else len(block))].strip())
            for k, m in enumerate(starts)]


def lean_file(statements: list[tuple[str, str]]) -> str:
    out = ["import VE", ""]
    for name, statement in statements:
        namespace, opens = PLACES.get(name, DEFAULT_PLACE)
        out += [f"namespace {namespace}", f"open {opens}",
                f"theorem approved_{name} {statement} := @{name}", f"end {namespace}", ""]
    return "\n".join(out)


def lean_errors(statements: list[tuple[str, str]]) -> str:
    """Lean's output when some statement fails to elaborate or is not proved by its theorem; empty when all pass."""
    return lean_errors_of(lean_file(statements))


def lean_errors_of(source: str) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".lean", delete=False) as handle:
        handle.write(source)
    try:
        done = subprocess.run([LAKE, "env", "lean", handle.name], cwd=ROOT / "lean", capture_output=True,
                              text=True, timeout=1800)
    finally:
        os.unlink(handle.name)
    return "" if done.returncode == 0 else (done.stdout + done.stderr) or f"lean exited {done.returncode}"


def main() -> int:
    statements = approved()
    if len(statements) != 12:
        print(f"expected twelve approved E2 statements, found {len(statements)}")
        return 1
    errors = lean_errors(statements)
    print(f"checked {len(statements)} approved E2 statements")
    if errors:
        print(errors[-6000:])
        return 1
    print("PASS: Lean elaborates every approved statement and the built theorem proves it")
    return 0


if __name__ == "__main__":
    sys.exit(main())
