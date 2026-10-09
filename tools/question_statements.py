"""Compare implemented Q1 theorem statements with the approved section 5.1 text.

Only statements that have an implementation are compared. Missing statements are
reported, so a partial proof pass cannot be mistaken for a complete one.
"""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/spec/question-answering.md"
SOURCE = ROOT / "lean/VE/Question/Properties.lean"


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


def main() -> None:
    spec = SPEC.read_text().split("### 5.1 Q1", 1)[1].split("### 5.2 Q2", 1)[0]
    approved = statements(spec, source=False)
    actual = {name: stmt for name, stmt in statements(SOURCE.read_text(), source=True).items()
              if name in approved}
    different = [name for name in actual if approved.get(name) != actual[name]]
    missing = [name for name in approved if name not in actual]
    print(f"Q1 statements: {len(actual)} of {len(approved)} implemented; {len(missing)} missing")
    if different:
        print("Mismatched statements:", ", ".join(different))
    if missing:
        print("Missing statements:", ", ".join(missing))
    if different or missing:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
