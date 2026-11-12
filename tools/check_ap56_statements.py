"""Compare AP-2's Lean declarations with the Lean block of docs/spec/act-phrases.md 5.6 (build checklist 17), read as
tools/check_pc3_statements.py reads PC-3's (its `declarations`).

Each declaration of 5.6's block must be the one Lean declaration of that kind and name in lean/VE/Acts/*.lean, equal
after whitespace normalization (a theorem up to its proof's `:=`). None may be missing, so a theorem of the spec cannot
be cut from a batch without this check failing (ap-2bc review F1: `read_normal` was missing). Two are held in the form
Lean writes them (`FORMS`): `Derived`, defined through the generic `DerivedIn` (lean/VE/Acts/Read.lean), which unfolds
by its definition to 5.6's text; and `listing_ok`, whose `α` and `DecidableEq α` are its section's `variable`s and
whose `Tree` is opened from `VE.Grammar`.

A module's first docstring sentence (its code map entry) that names a theorem of the block in backticks must name one
that Lean declares, so no header presents an unproved result as proved (ap-2bc review F2).
"""

from pathlib import Path
import re

from check_pc3_statements import declarations

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/spec/act-phrases.md"
SOURCES = sorted((ROOT / "lean/VE/Acts").glob("*.lean"))

FORMS = {
    "Derived": "def Derived (V : Vocab) (ts : List Tok) (A : Act) : Prop := DerivedIn (grammar V) (meaning V) ts A",
    "listing_ok": "theorem listing_ok (N L : Nat) (parsed : Option (List (Tree Tok))) (μ : Tree Tok → Option α) "
                  "(xs : List α) : listing N L parsed μ = .ok xs ↔ ∃ ts, parsed = some ts ∧ ts.length < N ∧ "
                  "xs = firsts (ts.filterMap μ) ∧ xs.length ≤ L",
}


def approved() -> dict[tuple[str, str], list[str]]:
    section = SPEC.read_text().split("### 5.6 ", 1)[1].split("\n## ", 1)[0].split("\n### ", 1)[0]
    return declarations("\n".join(re.findall(r"```lean\n(.*?)```", section, re.S)))


def first_sentence(text: str) -> str:
    """The first sentence of a module's docstring, as the code map reads it."""
    if "/-!" not in text:
        return ""
    return re.split(r"\.\s", text.split("/-!", 1)[1].strip(), maxsplit=1)[0]


def main(sources=SOURCES) -> int:
    lean: dict[tuple[str, str], list[str]] = {}
    for source in sources:
        for key, texts in declarations(Path(source).read_text()).items():
            lean.setdefault(key, []).extend(texts)
    errors, exact = [], 0
    theorems = {name for kind, name in approved() if kind == "theorem"}
    for source in sources:
        named = set(re.findall(r"`(?:[\w.]*\.)?(\w+)`", first_sentence(Path(source).read_text()))) & theorems
        for name in sorted(named):
            if ("theorem", name) not in lean:
                errors.append(f"{Path(source).name}: its first sentence names `{name}`, which Lean does not declare")
    for (kind, name), texts in sorted(approved().items()):
        found = lean.get((kind, name), [])
        text = FORMS.get(name, texts[0])
        if not found:
            errors.append(f"{name}: {kind} missing from lean/VE/Acts")
        elif len(texts) != 1 or found != [text]:
            errors.append(f"{name}: {kind} differs\n  approved: {text}\n  Lean:     {found}")
        else:
            exact += 1
    print(f"AP-2 5.6: {exact} declarations equal the approved text ({', '.join(FORMS)} in their held form)")
    print("\n".join(errors))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
