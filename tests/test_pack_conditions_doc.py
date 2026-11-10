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

OLD_DOC = "Each stated sufficient condition and its decision (profile-composition 1.9; no reader yet)."


def conditions_docstring(packs: str) -> str:
    """The doc comment right before the `conditions` field of `structure Pack`."""
    structure = re.search(r"^structure Pack where\n(.*?)(?=^\S)", packs, re.MULTILINE | re.DOTALL)
    assert structure, "structure Pack not found in Packs.lean"
    doc = re.search(r"/--((?:(?!-/).)*)-/\s*conditions\s*:", structure.group(1), re.DOTALL)
    assert doc, "Pack.conditions has no docstring"
    return " ".join(doc.group(1).split())


def reader_doc_problems(doc: str, uniform: str) -> list[str]:
    """What is wrong with `doc` as the docstring of `Pack.conditions`, given Uniform.lean's text."""
    problems = []
    if re.search(r"no reader|not read yet", doc, re.IGNORECASE):
        problems.append(f"the docstring says it has no reader: {doc}")
    if "profile-composition 1.9" not in doc:
        problems.append(f"the docstring lost its profile-composition 1.9 reference: {doc}")
    for name in READERS:
        if f"`{name}`" not in doc:
            problems.append(f"the docstring does not name {name}: {doc}")
        if not re.search(rf"^def {re.escape(name)}\b", uniform, re.MULTILINE):
            problems.append(f"{name} is not defined in lean/VE/Defaults/Uniform.lean")
    return problems


def test_pack_conditions_reader_documentation() -> None:
    doc = conditions_docstring(PACKS.read_text(encoding="utf-8"))
    assert reader_doc_problems(doc, UNIFORM.read_text(encoding="utf-8")) == []


def test_pack_conditions_reader_documentation_refuses() -> None:
    """The opposite direction: the old docstring, and a reader renamed in Uniform.lean, are refused."""
    uniform = UNIFORM.read_text(encoding="utf-8")
    doc = conditions_docstring(PACKS.read_text(encoding="utf-8"))
    named = OLD_DOC + " Read by `packConditions` and `providerConditions`."
    assert reader_doc_problems(named, uniform) == [f"the docstring says it has no reader: {named}"]
    assert len(reader_doc_problems(OLD_DOC, uniform)) == 3
    renamed = uniform.replace("def providerConditions ", "def providerConditionsOld ")
    assert reader_doc_problems(doc, renamed) == [
        "providerConditions is not defined in lean/VE/Defaults/Uniform.lean"]
