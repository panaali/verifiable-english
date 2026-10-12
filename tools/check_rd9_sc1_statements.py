"""Compare the implemented SC-1 declarations against RD-9's approved Lean blocks.

The one theorem still awaiting a proof is reported explicitly as unbuilt. This
checker becomes an acceptance check when that entry is removed.
"""

from pathlib import Path
import re

from check_readings_defaults_statements import compare, declarations, lean_of


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/spec/rd-9-soft-chain.md"
SECTIONS = (
    ("SC-1 entailment", "### 6.3", "### 6.4", ROOT / "lean/VE/NormDefaults/LayeredEntail.lean",
     {"theorem": 9, "def": 5, "structure": 0}, set()),
    ("SC-1 documents", "### 6.4", "### 6.5", ROOT / "lean/VE/Readings/SoftDefaults.lean",
     {"theorem": 4, "def": 9, "structure": 0}, {"softX_wellFormed"}),
    ("SC-1 fold", "### 6.5", "### 6.6", ROOT / "lean/VE/Readings/Verdicts.lean",
     {"theorem": 14, "def": 7, "structure": 1}, set()),
)


def main() -> int:
    text = SPEC.read_text()
    errors = []
    for title, start, stop, source, expected, later in SECTIONS:
        section = text.split(start, 1)[1].split(stop, 1)[0]
        code = section.split("```lean", 1)[1].split("```", 1)[0]
        code = re.sub(r"--[^\n]*", "", code)
        approved = declarations(code, statements_only=True)
        if later:
            for name in later:
                key = ("theorem", name)
                if key not in approved or key in lean_of(source):
                    errors.append(f"{name}: unbuilt marker is stale")
                approved.pop(key, None)
            expected = {**expected, "theorem": expected["theorem"] - len(later)}
        e, _ = compare(title, approved, source, expected, {}, set())
        errors.extend(e)
        if later:
            print(f"unbuilt in this batch: {', '.join(sorted(later))}")
    if errors:
        print("\n".join(errors))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
