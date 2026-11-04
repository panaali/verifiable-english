"""Compare PC-2a's Lean declarations with the approved Lean block of docs/spec/profile-composition.md 3.2 (build
checklist 17), read as tools/check_pc3_statements.py reads PC-3's (its `declarations`), after whitespace normalization: a
theorem up to its proof's `:=`, anything else in full. `requestOf`, which the spec gives without a body, is compared up
to its `:=`. PC-2b's and PC-2c's declarations of the same section are not PC-2a's and are not compared."""

from pathlib import Path
import re

from check_pc3_statements import declarations

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/spec/profile-composition.md"
SOURCES = [ROOT / "lean/VE/Service/Document.lean", ROOT / "lean/VE/Service/DocumentChain.lean"]
NAMES = [("def", "requestOf"), ("def", "layeredOf"), ("theorem", "layeredOf_ids"), ("theorem", "layeredOf_entails")]


def approved() -> dict[tuple[str, str], list[str]]:
    section = SPEC.read_text().split("### 3.2 ", 1)[1].split("### 3.3 ", 1)[0]
    return declarations("\n".join(re.findall(r"```lean\n(.*?)```", section, re.S)))


def main(sources=SOURCES) -> int:
    lean: dict[tuple[str, str], list[str]] = {}
    for source in sources:
        for key, texts in declarations(Path(source).read_text()).items():
            lean.setdefault(key, []).extend(texts)
    spec, errors = approved(), []
    for key in NAMES:
        found = lean.get(key, [])
        if key == ("def", "requestOf"):
            found = [f.split(" :=", 1)[0] for f in found]
        if found != spec.get(key):
            errors.append(f"{key[1]}: spec {spec.get(key)!r}, Lean {found!r}")
    print("\n".join(errors) or f"{len(NAMES)} statements equal the spec")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
