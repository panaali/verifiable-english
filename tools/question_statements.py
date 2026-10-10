"""Compare implemented Q1 theorem statements and predicates with the approved section 5.1 text.

Only statements that have an implementation are compared. Missing statements are
reported, so a partial proof pass cannot be mistaken for a complete one. The
predicates of 5.1 (`def ... : Prop`, review C1 of Fable) are compared whole,
their bodies included: a statement's text says nothing if a predicate it names
changes meaning.
"""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/spec/question-answering.md"
SOURCES = sorted((ROOT / "lean/VE/Question").glob("*.lean"))


def statements(text: str, source: bool) -> dict[str, str]:
    found = {}
    lines = text.splitlines()
    for i, line in enumerate(lines):
        match = re.match(r"^theorem (\w+)(?:\s|:)", line)
        if not match:
            continue
        name = match.group(1)
        parts = [line]
        for following in lines[i + 1 :]:
            if source and ":= by" in parts[-1]:
                break
            if not source and (not following or following.startswith(("theorem ", "/--", "end "))):
                break
            parts.append(following)
        statement = " ".join(parts).split(":= by", 1)[0]
        found[name] = re.sub(r"\s+", " ", statement).strip()
    return found


def definitions(text: str) -> dict[str, str]:
    """Every `def` of `text`, signature and body, whitespace collapsed: up to a blank line or the next declaration
    or doc comment."""
    found = {}
    lines = text.splitlines()
    for i, line in enumerate(lines):
        match = re.match(r"^def (\w+)(?:\s|:)", line)
        if not match:
            continue
        parts = [line]
        for following in lines[i + 1:]:
            if not following.strip() or following.startswith(("theorem ", "def ", "/--", "end ", "```")):
                break
            parts.append(following)
        found[match.group(1)] = re.sub(r"\s+", " ", " ".join(parts)).strip()
    return found


def main() -> None:
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
