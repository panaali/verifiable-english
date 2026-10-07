"""Every call into Python's own English reader is a site the deletion ledger keeps (spec 2.9; recheck 1 of E2, B).

Recheck 1 found two definition renderings (`render_citation`, `wordings`) still asking Python's statement-layer
reader to check them, while `docs/lean-first/e2/LEDGER.md` says Lean owns definition and citation sentences; the
flag hid a Lean refusal. The class is a caller that reaches Python's reader without a ledger row, so this test
lists the callers from the source, with Python's own parser (`ast`, never a regex), and compares the list with
the sites the ledger keeps: a new caller fails here until the ledger names it.
"""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = (ROOT / "docs/lean-first/e2/LEDGER.md").read_text()
# Python's reader: the hand parser, its all-derivations audit, and the two functions that run them.
READERS = frozenset({"_python_reading", "parse_statement_english", "EnglishParser", "require_unique_derivation",
                     "require_correspondence"})
STATEMENT_FLAG = "_statement_layer"

# Each kept site, with the ledger text that keeps it.
KEPT = {
    ("ve/english.py", "_python_reading"): "`ve/english.py` `_python_reading`",
    ("ve/english.py", "parse_statement_english"): "`parse_statement_english`",
    ("ve/english.py", "_parse_english_document_uncached"): "comparator",
    ("ve/english.py", "render_english.check_rendering"): "the statement layer's own rendering check",
    ("ve/english.py", "_natural_derivation"): "`require_correspondence`",
    ("ve/norm_english.py", "_parse_guard"): "kept for `norm_english.py`",
    ("ve/norm_english.py", "parse_english"): "kept for `norm_english.py`",
    ("ve/norm_defaults_english.py", "parse_legend_sentence"): "`norm_defaults_english.py`",
    ("ve/readings_s2_wording.py", "S2Wording.conclusion"): "`ve/readings_s2_wording.py` `S2Wording.conclusion`",
}
# The only callers that may ask `render_english` for the statement layer's own check.
FLAGGED = {("ve/readings_s2_wording.py", "S2Wording.conclusion")}


def call_sites(path: str, source: str) -> tuple[set, set]:
    """The (file, enclosing function) of every call to a reader, and of every call passing the statement
    flag with any value but a literal False."""
    readers, flagged = set(), set()
    scope: list[str] = []

    class Visitor(ast.NodeVisitor):
        def scoped(self, node):
            scope.append(node.name)
            self.generic_visit(node)
            scope.pop()

        visit_FunctionDef = visit_AsyncFunctionDef = visit_ClassDef = scoped

        def visit_Call(self, node):
            f = node.func
            name = f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else None
            site = (path, ".".join(scope))
            if name in READERS:
                readers.add(site)
            # A `**options` splat cannot carry the flag: every admission entry point hands its options to
            # `EnglishVocabulary` first, which takes no such keyword.
            if any(keyword.arg == STATEMENT_FLAG and not (
                    isinstance(keyword.value, ast.Constant) and keyword.value.value is False)
                   for keyword in node.keywords):
                flagged.add(site)
            self.generic_visit(node)

    Visitor().visit(ast.parse(source))
    return readers, flagged


def tree_sites() -> tuple[set, set]:
    readers, flagged = set(), set()
    for file in sorted((ROOT / "ve").rglob("*.py")):
        r, f = call_sites(file.relative_to(ROOT).as_posix(), file.read_text())
        readers |= r
        flagged |= f
    return readers, flagged


def test_every_python_reader_call_is_a_kept_ledger_site():
    readers, flagged = tree_sites()
    assert readers == set(KEPT)
    assert flagged == FLAGGED
    for site, text in KEPT.items():
        assert text in LEDGER, site


def test_the_inventory_finds_a_definition_rendering_that_asks_python():
    """The finding itself, as a mutant of `ve/surface/definitions.py`: the inventory reports it."""
    path = "ve/surface/definitions.py"
    source = (ROOT / path).read_text().replace(
        "render_english(Document((conclusion,)), env)",
        "render_english(Document((conclusion,)), env, _statement_layer=True)")
    assert call_sites(path, source)[1] == {(path, "render_citation")}
    source = "def wordings(env):\n    return parse_statement_english(env, 'x')\n"
    assert call_sites(path, source)[0] == {(path, "wordings")}
