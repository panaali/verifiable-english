"""Compare implemented Q1 and Q2 theorem statements and predicates with the approved sections 5.1 and 5.2.

Only statements that have an implementation are compared. Missing statements are
reported, so a partial proof pass cannot be mistaken for a complete one. The
predicates of 5.1 (`def ... : Prop`, review C1 of Fable) are compared whole,
their bodies included: a statement's text says nothing if a predicate it names
changes meaning.

Q2 (`--q2`, section 5.2 against `lean/VE/Ask` and `lean/VE/Words`): the same text comparison, and then Lean is the
oracle (build checklist 11): a generated file states every approved theorem as `example : <approved statement> :=
@name` and every approved signature-only `def` as `example : <approved type> := name`, in the spec's namespace and
opens, and `lake env lean` must elaborate it. A text difference Lean accepts (a binder written as an arrow, a term
proof) is listed as such; one it rejects fails. The approved definitions that changed are listed with their
reasons in `DIFFERENCES` (each a DRI item of the batch's DELTA.md); any other change fails.
"""

import argparse
from pathlib import Path
import re
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/spec/question-answering.md"
SOURCES = sorted((ROOT / "lean/VE/Question").glob("*.lean"))
Q2_SOURCES = sorted((ROOT / "lean/VE/Ask").glob("*.lean")) + sorted((ROOT / "lean/VE/Words").glob("*.lean"))
Q2_PREAMBLE = """import VE
namespace VE.Ask
open Lean VE.Readings VE.NormDefaults
open VE.Norms (Sat restrictAll DocumentExpansion)
universe u
"""


def statements(text: str, source: bool, proof: str = ":= by") -> dict[str, str]:
    """`proof` ends a source statement: Q1's proofs are tactic blocks; Q2's may be terms (`:=` then).
    A spec statement ends at a blank line or the next declaration."""
    found = {}
    lines = text.splitlines()
    for i, line in enumerate(lines):
        match = re.match(r"^theorem (\w+)(?:\s|:)", line)
        if not match:
            continue
        name = match.group(1)
        parts = [line]
        for following in lines[i + 1 :]:
            if source and proof in parts[-1]:
                break
            if not source and (not following or following.startswith(("theorem ", "/--", "end "))):
                break
            parts.append(following)
        statement = " ".join(parts).split(proof, 1)[0]
        found[name] = re.sub(r"\s+", " ", statement).strip()
    return found


def definitions(text: str, name: str = r"\w+") -> dict[str, str]:
    """Every `def` of `text`, signature and body, whitespace collapsed: up to a blank line or the next declaration
    or doc comment."""
    found = {}
    lines = text.splitlines()
    for i, line in enumerate(lines):
        match = re.match(rf"^def ({name})(?:\s|:)", line)
        if not match:
            continue
        parts = [line]
        for following in lines[i + 1:]:
            if not following.strip() or following.startswith(("theorem ", "def ", "/--", "end ", "```")):
                break
            parts.append(following)
        found[match.group(1)] = re.sub(r"\s+", " ", " ".join(parts)).strip()
    return found


DEF_NAME = r"[\w.]+"

# Approved Q2 definitions whose implementation differs from the approved text, each with its reason; every entry is
# a DRI item of docs/spec/question-answering-q2/DELTA.md. A signature-only approved `def` is not listed: Lean checks
# its type.
DIFFERENCES = {
    "Asked": "`hnames` uses `NameReadsBackSame` (canonical JSON text, the relation `UnitBound` uses) for the "
             "approved `NameReadsBack` (kept as approved): Lean's `Json` has no decidable equality, so `=` on the "
             "read-back formula cannot be decided",
}


def types(text: str) -> dict[str, str]:
    """Every `structure` and `inductive` of `text`, whitespace collapsed, without `--` comments and `deriving`
    clauses: up to a blank line or the next declaration or doc comment."""
    found = {}
    lines = text.splitlines()
    for i, line in enumerate(lines):
        match = re.match(rf"^(?:structure|inductive) ({DEF_NAME})(?:\s|$)", line)
        if not match:
            continue
        parts = [line]
        for following in lines[i + 1:]:
            if not following.strip() or following.startswith(
                    ("theorem ", "def ", "structure ", "inductive ", "instance ", "/--", "end ", "```")):
                break
            parts.append(following)
        body = " ".join(part.split("--", 1)[0] for part in parts)
        body = re.sub(r"\bderiving\b.*$", "", re.sub(r"\s+", " ", body)).strip()
        found[match.group(1)] = body
    return found


def signature(block: str) -> str | None:
    """The type of a signature-only spec `def` (`def name : T -- comment`), or None for one with a body."""
    head = block.split(" -- ", 1)[0]
    if ":=" in head or "|" in head:
        return None
    match = re.match(rf"^def {DEF_NAME} : (.+)$", head.strip())
    return match.group(1).strip() if match else None


def q2(lean: bool) -> int:
    spec = SPEC.read_text().split("### 5.2 Q2", 1)[1].split("## 6. Limits", 1)[0]
    approved = statements(spec, source=False)
    actual = {name: stmt for source in Q2_SOURCES
              for name, stmt in statements(source.read_text(), source=True, proof=":=").items() if name in approved}
    missing = [name for name in approved if name not in actual]
    differ = [name for name in actual if approved[name] != actual[name]]
    print(f"Q2 statements: {len(actual)} of {len(approved)} implemented; {len(missing)} missing; "
          f"{len(differ)} differ in text")
    approved_defs = definitions(spec, DEF_NAME)
    actual_defs = {name: text for source in Q2_SOURCES for name, text in definitions(source.read_text(), DEF_NAME).items()
                   if name in approved_defs}
    sigs = {name: signature(block) for name, block in approved_defs.items()}
    bodies = [name for name in approved_defs if sigs[name] is None]
    absent = [name for name in approved_defs if name not in actual_defs]
    changed = [name for name in bodies if name in actual_defs and actual_defs[name] != approved_defs[name]]
    unlisted = [name for name in changed if name not in DIFFERENCES]
    print(f"Q2 definitions: {len(approved_defs)} approved, {len(bodies)} with bodies, "
          f"{len(bodies) - len(changed)} equal to the approved text, {len(changed)} changed "
          f"({len(changed) - len(unlisted)} listed with their reasons); {len(absent)} absent")
    for name in changed:
        print(f"  changed {name}: {DIFFERENCES.get(name, 'NOT LISTED')}")
    approved_types = types(spec)
    actual_types = {name: text for source in Q2_SOURCES for name, text in types(source.read_text()).items()
                    if name in approved_types}
    changed_types = [name for name in approved_types if actual_types.get(name) != approved_types[name]]
    unlisted += [name for name in changed_types if name not in DIFFERENCES]
    print(f"Q2 structures and inductives: {len(approved_types)} approved, "
          f"{len(approved_types) - len(changed_types)} equal to the approved text, {len(changed_types)} changed")
    for name in changed_types:
        print(f"  changed {name}: {DIFFERENCES.get(name, 'NOT LISTED')}")
    failed = bool(missing or absent or unlisted or differ)
    if differ:
        print("Statements differing in text:", ", ".join(differ))
    if missing:
        print("Missing statements:", ", ".join(missing))
    if absent:
        print("Absent definitions:", ", ".join(absent))
    if lean:
        checks = [f"example : {stmt.split(':', 1)[1].strip()} := @{name}" for name, stmt in approved.items()
                  if name in actual]
        checks += [f"example : {sigs[name]} := {name}" for name in approved_defs if sigs[name] and name in actual_defs]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "Q2Statements.lean"
            path.write_text(Q2_PREAMBLE + "\n".join(checks) + "\nend VE.Ask\n")
            done = subprocess.run(["lake", "env", "lean", str(path)], cwd=ROOT / "lean", capture_output=True,
                                  text=True)
        errors = [line for line in (done.stdout + done.stderr).splitlines() if "error" in line]
        print(f"Q2 Lean check: {len(checks)} approved statements and signatures elaborated against the "
              f"implementation; {'PASS' if done.returncode == 0 and not errors else 'FAIL'}")
        for line in errors[:20]:
            print("  " + line)
        failed = failed or done.returncode != 0 or bool(errors)
    return 1 if failed else 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--q2", action="store_true", help="compare section 5.2 with lean/VE/Ask and lean/VE/Words")
    parser.add_argument("--no-lean", action="store_true", help="Q2: the text comparison only")
    options = parser.parse_args()
    if options.q2:
        raise SystemExit(q2(not options.no_lean))
    spec = SPEC.read_text().split("### 5.1 Q1", 1)[1].split("### 5.2 Q2", 1)[0]
    approved = statements(spec, source=False)
    actual = {name: stmt for source in SOURCES for name, stmt in statements(source.read_text(), source=True).items()
              if name in approved}
    different = [name for name in actual if approved.get(name) != actual[name]]
    missing = [name for name in approved if name not in actual]
    print(f"Q1 statements: {len(actual)} of {len(approved)} implemented; {len(missing)} missing")
    if different:
        print("Mismatched statements:", ", ".join(different))
    if missing:
        print("Missing statements:", ", ".join(missing))
    approved_defs = definitions(spec)
    actual_defs = {name: text for source in SOURCES for name, text in definitions(source.read_text()).items()
                   if name in approved_defs}
    changed = [name for name in approved_defs if actual_defs.get(name) != approved_defs[name]]
    print(f"Q1 predicates: {len(approved_defs) - len(changed)} of {len(approved_defs)} equal to the approved text")
    if changed:
        print("Changed or missing predicates:", ", ".join(changed))
    if different or missing or changed or not approved_defs:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
