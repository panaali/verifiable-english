"""Scope spec section 11's statement stub (sc-5r): every placeholder it leaves to sc-5rb is pinned by a statement.

A placeholder is an `opaque` of `docs/spec/scope/SpecStubs_sc5r.lean`; nothing about it holds but what a statement
says. sc-5r's review F1 found the document mode `checkDocSets` pinned only on documents with a governed set: a
`withGoverned` that always copies `reading_sets` would change every `scope@0` answer with none. So each placeholder
that is a document-mode entry (`Json → Except String Json`) must be stated about on each of the three cases the
entry tells apart (no `scope@0`; `scope@0` with no governed set; `scope@0`), and every other placeholder must be
named by some statement. Spec 11.4 must cite the no-set statement where it keeps `scope_admission`'s text."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUB = ROOT / "docs/spec/scope/SpecStubs_sc5r.lean"
SPEC = ROOT / "docs/spec/scope.md"

# The three cases of a document-mode entry, each a hypothesis text a statement about it must carry.
ENTRY_CASES = {
    "no scope@0": '"scope@0" ∉',
    "no governed set": "governedSetUnits D = []",
    "scope@0": '"scope@0" ∈',
}


def placeholders(text: str) -> dict[str, str]:
    return dict(re.findall(r"^opaque (\w+) : (.+)$", text, re.M))


def statements(text: str) -> list[str]:
    """Each theorem's name and statement, up to its proof."""
    return [block.split(":= by")[0] for block in text.split("\ntheorem ")[1:]]


def names(statement: str, name: str) -> bool:
    return re.search(rf"\b{re.escape(name)}\b", statement) is not None


def test_the_stub_has_placeholders():
    found = placeholders(STUB.read_text())
    assert {"checkDocSets", "withGoverned"} <= set(found)


def test_every_entry_placeholder_is_stated_on_every_case():
    text = STUB.read_text()
    entries = [n for n, ty in placeholders(text).items() if ty.strip() == "Json → Except String Json"]
    assert entries
    missing = [(entry, case) for entry in entries for case, hyp in ENTRY_CASES.items()
               if not any(names(st, entry) and hyp in st for st in statements(text))]
    assert missing == []


def test_every_placeholder_is_named_by_a_statement():
    text = STUB.read_text()
    unnamed = [n for n in placeholders(text) if not any(names(st, n) for st in statements(text))]
    assert unnamed == []


def test_review_f1_probe():
    """PROBE F1 of the sc-5r review, as written."""
    bs = [b.split(":= by")[0] for b in STUB.read_text().split("theorem ")[1:]]
    assert any("governedSetUnits D = []" in b and ("checkDocSets" in b or "withGoverned" in b) for b in bs)


def test_spec_keeps_scope_admission_text_by_the_document_level_statement():
    section = SPEC.read_text().split("### 11.4 ", 1)[1].split("\n### ", 1)[0]
    bullet = next(b for b in section.split("\n- ") if b.startswith("**`scope_admission` is replaced"))
    assert "`checkDocSets_no_sets`" in bullet
