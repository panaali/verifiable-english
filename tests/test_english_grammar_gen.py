"""The fixed rules of English in Lean as data (docs/spec/english-lean-s2.md 2.5, 2.9, 4.5; S2 plan S2.0).

The JSON source is compared with Python's own Lark grammar, converted to tokens by the S0 conversion
(`conformance.english_lean_tokens.convert`), rule for rule; `tools/english_grammar_gen.py --check` is shown
to fail on fixtures t1 (an edited generated rule), t5 (a proposed row in the table) and i5 (a trusted file
changed with `actions_version` unchanged), and the source reader to refuse malformed rows with
`GrammarSourceError` only.
"""
from __future__ import annotations

from collections import Counter
import copy
import importlib.util
import json
from pathlib import Path
import sys
import warnings

import pytest

from ve import Environment
from ve.english import UnreviewedVocabularyWarning, english_lark_grammar

from conformance import english_lean_engine as E
from conformance import english_lean_tokens as TK

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("english_grammar_gen", ROOT / "tools/english_grammar_gen.py")
G = importlib.util.module_from_spec(spec)
sys.modules["english_grammar_gen"] = G
spec.loader.exec_module(G)

PROFILE = "relational-fol@0"
SOURCE, TARGET, _ = G.PROFILES[PROFILE]
# Lark's names for the nonterminals that the catalogue of spec 2.4 renames.
LARK_NAMES = {"conclusion_marker": "marker", "marker": "list_marker", "LABEL": "label"}
# Nonterminals whose rules are lexical (spec 2.6), and so not in the fixed table.
LEXICAL = {"noun", "label", "constant", "relation", "relative", "object_relative", "adjective",
           "copula_relative", "copula_adjective", "natural_subject", "owner_clause"}


def environment(predicates=None, constants=None) -> Environment:
    return Environment({
        "language": "ve.core@0", "profile": "relational-fol@0", "spec_revision": "ve-v0-draft-2026-09-20",
        "vocabulary": {
            "sorts": {"item": {"description": "Item", "verbalisation": {"singular": "service", "plural": "services"}},
                      "agent": {"description": "Agent", "verbalisation": {"singular": "person", "plural": "people"}}},
            "predicates": predicates or {}, "constants": constants or {}}})


def source_rows() -> list[dict]:
    return G.parse_source((ROOT / SOURCE).read_bytes(), SOURCE)


def row_key(row: dict) -> tuple:
    def sym(s):
        if type(s) is str:
            return ("kw", s)
        if "n" in s:
            return ("n", s["n"])
        if "c" in s:
            return ("content", s["c"])
        if "p" in s:
            return ("exact", ("punct", s["p"], s.get("before", False), s.get("after", False)))
        if "q" in s:
            return ("exact", ("quoted", s["q"]))
        return ("cls", ("numeral",) if s["cls"] == "numeral" else ("label", s["letter"]))
    return (row["lhs"], tuple(sym(s) for s in row["rhs"]))


def lark_rules(env: Environment) -> list[tuple]:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UnreviewedVocabularyWarning)
        grammar, names, _ = TK.convert(english_lark_grammar(env))
    name = lambda i: LARK_NAMES.get(str(names[i]), str(names[i]))
    out = []
    for rule in grammar.rules:
        rhs = tuple(("n", name(s.A)) if isinstance(s, E.N) else s.a for s in rule.rhs)
        out.append((name(rule.lhs), rhs))
    return out


def test_the_table_is_pythons_grammar_rule_for_rule():
    """Under a vocabulary with sorts only, every rule of Python's converted Lark grammar whose left side is
    not lexical is a row of the table, and every row is such a rule, with the same multiplicity."""
    python = Counter(r for r in lark_rules(environment()) if r[0] not in LEXICAL)
    table = Counter(row_key(row) for row in G.table_rows(source_rows()))
    assert table == python, (sorted(table - python), sorted(python - table))
    assert sum(table.values()) == 98


def test_the_fixed_rules_agree_under_a_full_vocabulary():
    """With predicates, constants and the natural-view families present, the fixed rules are unchanged:
    every non-lexical rule other than a wording's atom is a table row, and the table's atoms are Python's."""
    env = environment(
        {"active": {"arguments": ["item"], "description": "Deployed", "verbalisation": "{0} is deployed"},
         "owns": {"arguments": ["agent", "item"], "description": "Owner", "verbalisation": "{0} owns {1}"},
         "links": {"arguments": ["item", "item"], "description": "Link", "verbalisation": "{0} depends on {1}"}},
        {"api": {"sort": "item", "description": "API"}, "alice": {"sort": "agent", "description": "Alice"}})
    rules = lark_rules(env)
    table = Counter(row_key(row) for row in G.table_rows(source_rows()))
    python = Counter(r for r in rules if r[0] not in LEXICAL | {"atom"})
    assert Counter({k: v for k, v in table.items() if k[0] != "atom"}) == python
    atoms = Counter(r for r in rules if r[0] == "atom")
    assert all(atoms[k] == v for k, v in table.items() if k[0] == "atom")
    assert {r[0] for r in rules} <= set(G.NONTERMINAL)


def test_proposed_rows_are_out_of_the_table_and_python_has_none_of_them():
    rows = source_rows()
    proposed = [row for row in rows if row.get("status") == "proposed"]
    assert [row["tag"] for row in proposed] == ["widen.or-both.adjectives", "widen.or-both.relative",
                                                "widen.if-and-then"]
    python = set(lark_rules(environment()))
    assert not {row_key(row) for row in proposed} & python
    generated = (ROOT / TARGET).read_text()
    for row in proposed:
        assert f'tag := "{row["tag"]}"' not in generated
    assert len(G.table_rows(rows)) == len(rows) - 3


def test_act_texts_follow_the_export_encoding():
    texts = {row["tag"]: G.act_text(row) for row in source_rows()}
    assert texts["sentence.plain"] == "sentence false"
    assert texts["listing.if.markers"] == "listMarkers implies"
    assert texts["term.the-first"] == 'termRef "the first"'
    assert texts["declaration.eighth"] == "declOrdinal eighth"
    assert texts["count.zero"] == "count true"
    assert texts["reach.body.listed"] == "reachBody true"
    assert texts["formula.natural"] == "nest"


def test_the_repository_is_in_sync():
    assert G.check(G.file_reader(ROOT), G.file_listing(ROOT)) == []


# ------------------------------------------------------------------ the --check fixtures, on a copy

@pytest.fixture
def tree(tmp_path: Path) -> Path:
    for path in [*G.hashed_files(), G.LOCK, G.VERSION_TARGET, *G.UNTRUSTED]:
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / path).read_bytes())
    return tmp_path


def run_check(root: Path, base: bytes | None = None) -> list[str]:
    return G.check(G.file_reader(root), G.file_listing(root), base)


def test_copy_passes(tree):
    assert run_check(tree) == []
    assert run_check(tree, (tree / G.LOCK).read_bytes()) == []


def test_t1_an_edited_generated_rule_names_the_profile_and_the_tag(tree):
    target = tree / TARGET
    text = target.read_text()
    line = next(l for l in text.splitlines() if 'tag := "compact.or"' in l)
    target.write_text(text.replace(line, line.replace('.kw "both"', '.kw "all"')))
    errors = run_check(tree)
    assert any(e.startswith(f"{PROFILE}: {TARGET} differs from its source at rule compact.or") for e in errors)


def test_t1_an_edited_catalogue_is_drift_outside_the_rules(tree):
    target = tree / TARGET
    target.write_text(target.read_text().replace('"guard_relative"', '"guard_rel"'))
    assert any("outside the rules" in e and PROFILE in e for e in run_check(tree))


def test_t5_a_proposed_row_in_the_table_is_named(tree):
    rows = source_rows()
    row = next(r for r in rows if r["tag"] == "widen.if-and-then")
    target = tree / TARGET
    text = target.read_text()
    last = next(l for l in text.splitlines() if 'tag := "count.zero"' in l)
    target.write_text(text.replace(last, last + ",\n  " + G.lean_rule(row)))
    assert f"{PROFILE}: proposed row widen.if-and-then is in the generated table {TARGET}" in run_check(tree)


@pytest.mark.parametrize("path", ["lean/VE/EnglishGrammar/Token.lean", "lean/VE/EnglishGrammar/Lexer.lean",
                                  "lean/VE/EnglishGrammar/Lexicon.lean", "lean/VE/EnglishGrammar/Syntax.lean",
                                  "lean/VE/Grammar/Derives.lean", SOURCE])
def test_i5_a_trusted_change_with_the_version_unchanged_fails(tree, path):
    """Base fixture i5 over the lock file of spec 2.9: the stale hash is named with both values; after
    `--write` refuses a lock with the old version, a hand-updated lock with the old version still fails
    against the base lock; a raised version passes."""
    base = (tree / G.LOCK).read_bytes()
    old = json.loads(base)["files"][path]
    target = tree / path
    target.write_bytes(target.read_bytes() + (b"\n-- changed\n" if path.endswith(".lean") else b"\n"))
    new = G.sha256(target.read_bytes())
    errors = run_check(tree, base)
    assert f"{path}: SHA-256 {old} in {G.LOCK}, {new} now; raise actions_version and run --write" in errors
    with pytest.raises(G.GrammarSourceError, match="give a new --actions-version"):
        G.write(tree)
    lock = json.loads(base)
    lock["files"][path] = new
    if path == SOURCE:  # the generated table follows its source
        rows = G.parse_source(target.read_bytes(), SOURCE)
        (tree / TARGET).write_bytes(G.render_table(PROFILE, rows, new)[0])
        lock["files"][TARGET] = G.sha256((tree / TARGET).read_bytes())
    (tree / G.LOCK).write_bytes(G.render_lock(lock["actions_version"], lock["files"]))
    assert run_check(tree) == []
    errors = run_check(tree, base)
    unchanged = f"with actions_version {lock['actions_version']!r} unchanged"
    assert any(e.startswith(f"{path}: SHA-256 {old} at the base, {new} now, {unchanged}") for e in errors), errors
    assert G.write(tree, lock["actions_version"] + ".1") == [G.VERSION_TARGET, G.LOCK]
    assert run_check(tree, base) == []


def test_a_new_english_grammar_lean_file_must_be_classified(tree):
    (tree / "lean/VE/EnglishGrammar/Unclassified.lean").write_text("-- lexRules\n")
    assert run_check(tree) == ["lean/VE/EnglishGrammar/Unclassified.lean: neither a trusted file of "
                               f"{G.LOCK} nor listed as untrusted in tools/english_grammar_gen.py; classify it"]


def test_every_lean_file_of_the_two_directories_is_classified():
    found = set(G.file_listing(ROOT)())
    classified = (set(G.TRUSTED) | set(G.UNTRUSTED) | {target for _, target, _ in G.PROFILES.values()}
                  | set(G.generated_extras()))
    assert found == classified


def test_actions_version_has_one_literal_and_it_is_generated():
    """Review B1: `Actions.lean` held `actionsVersion := "1"` beside the generated "3". The only string literal
    given to an `actionsVersion` is the generated module's; every other definition names it."""
    import re
    literal = re.compile(r'\bactionsVersion\s*:\s*String\s*:=\s*"')
    found = sorted(str(path.relative_to(ROOT)) for path in (ROOT / "lean").rglob("*.lean")
                   if ".lake" not in path.parts and literal.search(path.read_text()))
    assert found == [G.VERSION_TARGET]
    actions = (ROOT / "lean/VE/EnglishGrammar/Actions.lean").read_text()
    assert "def actionsVersion : String := Fixed.actionsVersion" in actions


def test_the_version_module_follows_the_lock(tree):
    lock = json.loads((tree / G.LOCK).read_bytes())
    (tree / G.LOCK).write_bytes(G.render_lock("7", lock["files"]))
    assert run_check(tree) == [f"{G.VERSION_TARGET}: does not hold actions_version '7' of {G.LOCK}; run --write"]


def test_write_reproduces_the_committed_files(tree):
    assert G.write(tree) == []
    with pytest.raises(G.GrammarSourceError, match="actions_version"):
        G.write(tree, "not a version")


# ------------------------------------------------------------------ malformed sources

REPLACEMENTS = [7, True, None, [], {}, "word", "deep"]


def _nodes(value, path=()):
    yield path
    if type(value) is dict:
        for key, item in value.items():
            yield from _nodes(item, (*path, key))
    elif type(value) is list:
        for k, item in enumerate(value):
            yield from _nodes(item, (*path, k))


def _replace(value, path, new):
    if not path:
        return new
    out = copy.deepcopy(value)
    node = out
    for step in path[:-1]:
        node = node[step]
    node[path[-1]] = new
    return out


# Rows that between them carry every symbol kind and every kind of action data.
SAMPLE_TAGS = ("sentence.marked", "listing.if.markers", "declaration.first", "term.the-second", "reach.body.listed",
               "count.zero", "widen.if-and-then")


def _dump(rows) -> bytes:
    text = json.dumps(rows)
    return text.replace('"deep"', "[" * 10000 + "]" * 10000).encode()


def test_every_node_replaced_is_refused_with_the_source_error_only():
    rows = json.loads((ROOT / SOURCE).read_text())
    picked = [k for k, row in enumerate(rows) if row["tag"] in SAMPLE_TAGS]
    assert len(picked) == len(SAMPLE_TAGS)
    checked = 0
    for k in picked:
        for path in _nodes(rows[k], (k,)):
            for new in REPLACEMENTS:
                mutated = _replace(rows, path, new)
                if mutated == rows:
                    continue
                checked += 1
                try:
                    G.parse_source(_dump(mutated), SOURCE)
                except G.GrammarSourceError:
                    continue
                # Accepted only when the replacement leaves a valid row that differs in a harmless value.
                assert (new is True and path[-1] in {"before", "after", "marked", "listed", "reflexive"}) or \
                    (new == "word" and (path[-1] in {"tag", "c"} or path[1:2] == ("rhs",) and len(path) == 3)), \
                    (path, new)
    assert checked > 500


@pytest.mark.parametrize("text, message", [
    (b"", "not JSON"), (b"{}", "non-empty array"), (b"[]", "non-empty array"), (b"[1]", "a row is an object"),
    (b'[{"tag": "a", "tag": "b"}]', "duplicate key"), (b"[NaN]", "NaN is not JSON"), (b"\xff", "not JSON"),
    (("[" * 100000).encode(), "not JSON"),
])
def test_malformed_documents(text, message):
    with pytest.raises(G.GrammarSourceError, match=message):
        G.parse_source(text, SOURCE)


def _one(**changes) -> bytes:
    row = {"tag": "x.y", "lhs": "atom", "act": "top", "rhs": ["this", "is", "true"], **changes}
    return json.dumps([{k: v for k, v in row.items() if v is not None}]).encode()


@pytest.mark.parametrize("changes, message", [
    ({"rhs": [{"kwMid": "The"}]}, "kwMid occurs in no fixed row"),
    ({"rhs": [{"p": "."}]}, "not a punctuation token"),
    ({"rhs": [{"p": ",", "before": 1}]}, "not true or false"),
    ({"rhs": ["Both"]}, "not one lower-case word"),
    ({"rhs": ["two words"]}, "not one lower-case word"),
    ({"rhs": [{"n": "sentence"}]}, "not well-founded"),
    ({"rhs": [{"n": "atom"}, "x"]}, "not well-founded"),
    ({"rhs": [{"n": "nowhere"}]}, "unknown nonterminal"),
    ({"rhs": []}, "non-empty list"),
    ({"lhs": "Atom"}, "unknown nonterminal"),
    ({"act": "sentence"}, "fields missing \\['marked'\\]"),
    ({"act": "sentence", "marked": 0}, "not true or false"),
    ({"act": "listWords", "kind": "xor"}, "is not one of"),
    ({"act": "coordSubjects", "kind": "implies"}, "is not one of"),
    ({"act": "top", "kind": "and"}, "unknown \\['kind'\\]"),
    ({"act": "internal"}, "unknown action"),
    ({"act": "impliesAnd"}, "belongs to a proposed rule"),
    ({"act": "orAdjectives"}, "belongs to a proposed rule"),
    ({"status": "accepted"}, "only"),
    ({"tag": "X"}, "tag"),
    ({"rhs": [{"cls": "label", "letter": "s"}]}, "label letter"),
    ({"rhs": [{"q": "aé"}]}, "printable ASCII"),
])
def test_malformed_rows(changes, message):
    with pytest.raises(G.GrammarSourceError, match=message):
        G.parse_source(_one(**changes), SOURCE)


@pytest.mark.parametrize("text", ["re viewed", "Key", "İt", "a\tb", "a\rb", "a b", "\x07",
                                  "“owns”", "Reviewed", "deployed "])
@pytest.mark.parametrize("form", ["kw", "c", "q", "tag"])
def test_respaced_and_lookalike_text_is_refused(text, form):
    """A keyword, content word, quoted name or tag with a no-break space, the Kelvin sign, dotted capital I,
    a tab, a carriage return, a space, a control character, curly quotes or a capital is refused: the table
    names lexer tokens exactly (a quoted name keeps its spaces and capitals, as the lexer does)."""
    if form == "q" and text in ("a b", "Reviewed", "deployed "):
        G.parse_source(_one(rhs=[{"q": text}]), SOURCE)
        return
    changes = {"kw": {"rhs": [text]}, "c": {"rhs": [{"c": text}]}, "q": {"rhs": [{"q": text}]},
               "tag": {"tag": text}}[form]
    with pytest.raises(G.GrammarSourceError):
        G.parse_source(_one(**changes), SOURCE)


def test_a_repeated_tag_is_refused():
    rows = json.loads((ROOT / SOURCE).read_text())
    rows.append(dict(rows[0]))
    with pytest.raises(G.GrammarSourceError, match="rule sentence.plain: repeated tag"):
        G.parse_source(json.dumps(rows).encode(), SOURCE)
