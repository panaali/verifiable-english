"""The docstring of `Pack.conditions` names its readers (pk-1-conditions-b-cfr-1; finding pkcb-F3).

`lean/VE/NormDefaults/Packs.lean` said the field had "no reader yet", while `packConditions` reads it into decision
premises and `providerConditions` checks it on the defaults route. This test fails while the docstring says it has no
reader, and passes only when it names each reader below and each one is still defined in `Defaults/Uniform.lean`, so a
rename of a reader makes it fail.
"""
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
PACKS = ROOT / "lean/VE/NormDefaults/Packs.lean"
UNIFORM = ROOT / "lean/VE/Defaults/Uniform.lean"

# The functions that read `Pack.conditions` (both in `lean/VE/Defaults/Uniform.lean`).
READERS = ("packConditions", "providerConditions")


def conditions_docstring() -> str:
    """The doc comment right before the `conditions` field of `structure Pack`."""
    text = PACKS.read_text(encoding="utf-8")
    structure = re.search(r"^structure Pack where\n(.*?)(?=^\S)", text, re.MULTILINE | re.DOTALL)
    assert structure, "structure Pack not found in Packs.lean"
    doc = re.search(r"/--((?:(?!-/).)*)-/\s*conditions\s*:", structure.group(1), re.DOTALL)
    assert doc, "Pack.conditions has no docstring"
    return " ".join(doc.group(1).split())


def test_pack_conditions_reader_documentation() -> None:
    doc = conditions_docstring()
    assert not re.search(r"no reader|not read yet", doc, re.IGNORECASE), doc
    assert "profile-composition 1.9" in doc, doc
    uniform = UNIFORM.read_text(encoding="utf-8")
    for name in READERS:
        assert f"`{name}`" in doc, f"the docstring does not name {name}: {doc}"
        assert re.search(rf"^def {re.escape(name)}\b", uniform, re.MULTILINE), \
            f"{name} is not defined in lean/VE/Defaults/Uniform.lean"
