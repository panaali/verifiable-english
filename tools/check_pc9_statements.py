"""Compare PC-9's Lean declarations with the approved Lean blocks of docs/spec/profile-composition.md 1.8 and 1.9
(build checklist 17), read as tools/check_pc3_statements.py reads PC-3's (its `declarations`).

Each declaration of those blocks is compared with the one Lean declaration of that kind and name in
lean/VE/Defaults/Uniform.lean, after whitespace normalization: a theorem up to its proof's `:=`, anything else in full.
PK-1's `structure Pack` lives in lean/VE/NormDefaults/Packs.lean and is not compared here (`ELSEWHERE`). One is
compared in another form (`FORMS`): `leastUniform`, which the spec gives without a body, up to its `:=`.
`dfltUniform_sound` is the theorem DF-U proves (sa-no-exception), compared as every theorem is.
"""

from pathlib import Path
import re

from check_pc3_statements import declarations

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/spec/profile-composition.md"
SOURCES = [ROOT / "lean/VE/Defaults/Uniform.lean"]
ELSEWHERE = {"Pack"}


FORMS = {"leastUniform": lambda text: (("def", "leastUniform"), text)}


def approved() -> dict[tuple[str, str], list[str]]:
    section = SPEC.read_text().split("### 1.8 ", 1)[1].split("### 1.10 ", 1)[0]
    return declarations("\n".join(re.findall(r"```lean\n(.*?)```", section, re.S)))


def main(sources=SOURCES) -> int:
    lean: dict[tuple[str, str], list[str]] = {}
    for source in sources:
        for key, texts in declarations(Path(source).read_text()).items():
            lean.setdefault(key, []).extend(texts)
    errors, exact = [], 0
    for (kind, name), texts in sorted(approved().items()):
        if name in ELSEWHERE:
            continue
        key, text = FORMS[name](texts[0]) if name in FORMS else ((kind, name), texts[0])
        found = lean.get(key, [])
        if name == "leastUniform":
            found = [f.split(" :=", 1)[0] for f in found]
        if len(texts) != 1 or found != [text]:
            errors.append(f"{name}: {kind} differs\n  approved: {text}\n  Lean:     {found}")
        else:
            exact += 1
    print(f"PC-9: {exact} declarations equal the approved text ({', '.join(FORMS)} in their held form)")
    print("\n".join(errors))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
