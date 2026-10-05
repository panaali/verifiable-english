"""Stage S3 of English in Lean, the Python side (docs/spec/english-lean-s3.md; S3 plan, S3.0 and S3.1).

S3.0: the fixed tables of `order@0` and `alternatives@0` as data. Each is compared with Python's own Lark
grammar under the spec's fixture environment, converted to tokens by the S0 conversion, under the tree
correspondence of spec 2.11: the spacing nonterminals `minus`, `lbracket`, `rbracket` and the nodes `numeral`
and `int_op` are Lark's inline terminals, and the guard's verb atom is Lark's `atom` headed by the guard's
own reference. The staged catalogue and certificate (spec 2.4), the list of tables `grammar_id` reads, and
`grammar_id` of a base-profile environment (ev1) are checked against their single sources.
"""
from __future__ import annotations

from collections import Counter
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import warnings

import pytest

from conformance import english_lean_engine as E
from conformance import english_lean_tokens as TK
from conformance import english_lean_s3_fixtures as X
from ve import english_grammar as EG
from ve.english import UnreviewedVocabularyWarning, english_lark_grammar
from ve.wire import digest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("english_grammar_gen_s3", ROOT / "tools/english_grammar_gen.py")
G = importlib.util.module_from_spec(spec)
sys.modules["english_grammar_gen_s3"] = G
spec.loader.exec_module(G)

ORDER, ALTERNATIVES = "order@0", "alternatives@0"
# The SHA-256 of the base table source at S2 (`main` at 1e68d6d6, LOCK.json): S3 edits no base source (D2).
S2_BASE_SOURCE_SHA256 = "de8bc6f7a338611879e5b7826f6f0f48c9b59e1defb549eac406602c13a032f7"


def rows(profile: str) -> list[dict]:
    source = G.PROFILES[profile][0]
    return G.table_rows(G.parse_source((ROOT / source).read_bytes(), source, profile in G.STAGED))


def sym_key(s) -> tuple:
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


def lark_rules(raw: dict) -> list[tuple]:
    from ve import Environment
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UnreviewedVocabularyWarning)
        grammar, names, _ = TK.convert(english_lark_grammar(Environment(raw)))
    out = []
    for rule in grammar.rules:
        rhs = tuple(("n", str(names[s.A])) if isinstance(s, E.N) else s.a for s in rule.rhs)
        out.append((str(names[rule.lhs]), rhs))
    return out


def inline(table: list[dict], units: dict[str, str]) -> Counter:
    """The table's rules with each nonterminal of `units` expanded into its alternatives (the rows of that
    nonterminal, each a single symbol) and each renamed nonterminal given Lark's name (spec 2.11)."""
    alternatives: dict[str, list[tuple]] = {}
    for row in table:
        if row["lhs"] in units and units[row["lhs"]] == "inline":
            assert len(row["rhs"]) == 1
            alternatives.setdefault(row["lhs"], []).append(sym_key(row["rhs"][0]))
    out: Counter = Counter()
    for row in table:
        if units.get(row["lhs"]) == "inline":
            continue
        expansions: list[tuple] = [()]
        for s in row["rhs"]:
            key = sym_key(s)
            if key[0] == "n" and units.get(key[1]) == "inline":
                expansions = [e + (alt,) for e in expansions for alt in alternatives[key[1]]]
            elif key[0] == "n" and key[1] in units:
                expansions = [e + (("n", units[key[1]]),) for e in expansions]
            else:
                expansions = [e + (key,) for e in expansions]
        lhs = units.get(row["lhs"], row["lhs"])
        for e in expansions:
            out[(lhs, e)] += 1
    return out


# ------------------------------------------------------------------ the tables against Python's grammar

ORDER_UNITS = {"minus": "inline", "lbracket": "inline", "rbracket": "inline", "numeral": "NUMERAL",
               "int_op": "INT_OP"}
ORDER_FIXED_LHS = {"int_term", "int_atom", "int_neg", "NUMERAL", "INT_OP"}


def test_the_order_table_is_pythons_integer_grammar_rule_for_rule():
    """Spec 2.5 and 2.11: with the spacing nonterminals inlined, the `order@0` table is exactly Lark's integer
    grammar under `FO`, rule for rule and with the same multiplicity: the term rules, the numeral and
    operator terminals, and the five comparison atoms. Lark's other atoms are the lexical wordings."""
    table = inline(rows(ORDER), ORDER_UNITS)
    lark = lark_rules(X.FO())
    python = Counter(r for r in lark if r[0] in ORDER_FIXED_LHS)
    comparisons = Counter(r for r in lark if r[0] == "atom" and r[1][0] == ("n", "int_term")
                          and r[1][1] == ("content", "is"))
    assert len(comparisons) == 5
    assert table == python + comparisons, (sorted(table - python - comparisons), sorted(python + comparisons - table))
    # Every other Lark rule that names an integer nonterminal is lexical: a wording's atom or relative, or
    # one of the two integer-constant families.
    lexical = {r for r in lark if r[0] not in ORDER_FIXED_LHS and r not in comparisons
               and any(s[0] == "n" and s[1] in {"int_term", "int_constant", "int_plain_constant"}
                       for s in r[1])}
    assert {r[0] for r in lexical} == {"atom", "relative"}


def test_the_order_table_has_no_numeral_or_twice_under_a_sign():
    """Spec 2.5: `int_neg` has no numeral and no `twice` row, as in Lark (or20, or21)."""
    neg = [row for row in rows(ORDER) if row["lhs"] == "int_neg"]
    assert {row["tag"] for row in neg} == {"int-neg.constant", "int-neg.bracket", "int-neg.minus"}
    assert not any(sym_key(s) == ("n", "numeral") or s == "twice" for row in neg for s in row["rhs"])


def test_the_spacing_of_the_integer_marks_is_the_hand_parsers():
    """Spec 2.2 (DRI ruling 1): `[` and a sign are glued after and free before, `]` glued before and free
    after, an operator free on both sides; each free flag has its two rows."""
    flags = {(row["lhs"], sym_key(row["rhs"][0])[1]) for row in rows(ORDER)
             if row["lhs"] in {"minus", "lbracket", "rbracket", "int_op"}}
    assert flags == {("minus", ("punct", "-", False, True)), ("minus", ("punct", "-", True, True)),
                     ("lbracket", ("punct", "[", False, True)), ("lbracket", ("punct", "[", True, True)),
                     ("rbracket", ("punct", "]", True, False)), ("rbracket", ("punct", "]", True, True)),
                     ("int_op", ("punct", "+", False, False)), ("int_op", ("punct", "-", False, False)),
                     ("int_op", ("punct", "*", False, False))}


def test_the_alternatives_table_is_pythons_guard_grammar_under_the_correspondence():
    """Spec 2.5 and 2.11: the formula row and the three compound verb phrases are Lark's rules exactly;
    Lark's `alt_verb_phrase: relative | atom` is `verb-phrase.one` over `alt_verb_atom`, whose relative row
    is Lark's; Lark's `alt_verb_atom: atom` is the two head rows, an atom headed by the guard's own
    reference (D7). The guard rows themselves are lexical (2.6): Lark's five, and none in the table."""
    table = Counter((row["lhs"], tuple(sym_key(s) for s in row["rhs"])) for row in rows(ALTERNATIVES))
    lark = Counter(r for r in lark_rules(X.FA()) if r[0] in {"alt_verb_phrase", "alt_verb_atom"}
                   or r == ("formula", (("n", "alt_available_guard"),)))
    replaced_lark = Counter({("alt_verb_phrase", (("n", "relative"),)): 1,
                             ("alt_verb_phrase", (("n", "atom"),)): 1,
                             ("alt_verb_atom", (("n", "atom"),)): 1})
    added_lean = Counter({("alt_verb_phrase", (("n", "alt_verb_atom"),)): 1,
                          ("alt_verb_atom", (("n", "alt_head"), ("n", "relative"))): 1,
                          ("alt_verb_atom", (("n", "alt_head"), ("content", "is"), ("content", "the"),
                                             ("content", "same"), ("content", "as"), ("n", "term"))): 1})
    assert table - added_lean == lark - replaced_lark
    assert table & added_lean == added_lean and lark & replaced_lark == replaced_lark
    guards = [r for r in lark_rules(X.FA()) if r[0] == "alt_available_guard"]
    assert len(guards) == 5 and not any(row["lhs"] == "alt_available_guard" for row in rows(ALTERNATIVES))


def test_sz1_the_sizes_of_the_two_tables():
    assert (len(rows(ORDER)), len(rows(ALTERNATIVES))) == (25, 8)


def test_the_tags_of_the_spec_tables():
    """Spec 2.5's tags, in table order."""
    assert [row["tag"] for row in rows(ORDER)] == [
        "int-term.atom", "int-term.minus", "int-atom.constant", "int-atom.numeral", "int-atom.bracket",
        "int-atom.twice", "int-neg.constant", "int-neg.bracket", "int-neg.minus", "numeral.plain",
        "numeral.signed", "int-op.plus", "int-op.minus", "int-op.times", "minus.free", "minus.glued",
        "lbracket.free", "lbracket.glued", "rbracket.free", "rbracket.glued", "atom.int-eq", "atom.less",
        "atom.at-most", "atom.more", "atom.at-least"]
    assert [row["tag"] for row in rows(ALTERNATIVES)] == [
        "formula.alternatives", "verb-phrase.one", "verb-phrase.either", "verb-phrase.either-both",
        "verb-phrase.both", "verb-atom.relative", "verb-atom.subject", "verb-atom.same"]


def test_the_comparison_actions_swap_more_and_at_least():
    """Spec 2.5: `more than` and `at least` are `lt` and `le` with the terms exchanged (`english.py:50–51`)."""
    acts = {row["tag"]: G.act_text(row) for row in rows(ORDER)}
    assert {t: acts[t] for t in acts if t.startswith("atom.")} == {
        "atom.int-eq": "intCmp eq false", "atom.less": "intCmp lt false", "atom.at-most": "intCmp le false",
        "atom.more": "intCmp lt true", "atom.at-least": "intCmp le true"}
    from ve import english
    assert [(w, cls.__name__, swapped) for w, cls, swapped in english._COMPARISONS] == [
        ("{0} is less than {1}", "Lt", False), ("{0} is at most {1}", "Le", False),
        ("{0} is more than {1}", "Lt", True), ("{0} is at least {1}", "Le", True)]
    assert acts["numeral.plain"] == "numeral false" and acts["numeral.signed"] == "numeral true"
    rendered = {row["tag"]: G.lean_act(row) for row in rows(ORDER)}
    assert rendered["atom.more"] == "(.intCmp .lt true)" and rendered["numeral.signed"] == "(.numeral true)"


# ------------------------------------------------------------------ catalogue, certificate, identities

def test_the_staged_catalogue_appends_fourteen_nonterminals_and_keeps_s2s():
    """Spec 2.4: 0 to 36 unchanged, 37 to 50 appended in the spec's order; `ranksStaged` has 51 entries and
    is W3 for every fixed table, the base table included (sz7)."""
    names = list(G.NONTERMINAL)
    assert names[:37] == [n for n, _ in G.CATALOGUE] and len(names) == len(G.RANKS_STAGED) == 51
    assert names[37:] == ["int_term", "int_atom", "int_neg", "int_constant", "int_plain_constant", "numeral",
                          "int_op", "minus", "lbracket", "rbracket", "alt_available_guard", "alt_verb_phrase",
                          "alt_verb_atom", "alt_head"]
    for profile in G.PROFILES:
        for row in rows(profile):
            first = row["rhs"][0]
            if type(first) is dict and "n" in first:
                assert G.RANK_STAGED[first["n"]] < G.RANK_STAGED[row["lhs"]], (profile, row["tag"])
    staged = (ROOT / G.STAGED_TARGET).read_text()
    literal = re.search(r"def ranksStaged : Array Nat := #\[([0-9, ]+)\]", staged)
    assert literal and tuple(int(x) for x in literal[1].split(", ")) == G.RANKS_STAGED


def test_s2s_certificate_does_not_fit_the_integer_rows():
    """sz7: under S2's `ranks` extended with zeros the `order@0` rows are not well-founded."""
    zeros = {name: (G.RANK.get(name, 0)) for name in G.NONTERMINAL}
    bad = [row["tag"] for row in rows(ORDER) if type(row["rhs"][0]) is dict and "n" in row["rhs"][0]
           and not zeros[row["rhs"][0]["n"]] < zeros[row["lhs"]]]
    assert "int-term.atom" in bad and "int-atom.bracket" in bad


def test_pythons_tables_are_the_generators():
    """One list of tables: Python's `TABLES` (which `grammar_id` reads) names exactly the generator's sources,
    and Lean's generated `tableSources` lists the same profiles, in the same order, with each source's hash."""
    assert {p: "ve/english_grammar/" + f for p, f in EG.TABLES.items()} == \
        {p: source for p, (source, _, _) in G.PROFILES.items()}
    tables = (ROOT / G.TABLES_TARGET).read_text()
    listed = re.findall(r'\("([^"]+)", (\w+)Sha256\)', tables)
    assert [p for p, _ in listed] == list(G.PROFILES)
    for profile, name in listed:
        source, target, lean_name = G.PROFILES[profile]
        assert name == lean_name
        module = (ROOT / target).read_text()
        assert f'def {name}Sha256 : String := "{hashlib.sha256((ROOT / source).read_bytes()).hexdigest()}"' in module
    assert "def tables : List (String × String) := tableSources" in \
        (ROOT / "lean/VE/EnglishGrammar/Run.lean").read_text()


@pytest.mark.parametrize("profiles", [["relational-fol@0"], ["closure@0", "relational-fol@0"],
                                      ["norms@0", "relational-fol@0"], ["data@0", "relational-fol@0"],
                                      ["norms@0", "relational-fol@0", "time@0"]])
def test_ev1_grammar_id_without_the_staged_tables_is_s2s(profiles):
    """ev1: S3 edits no base source, so the `grammar_id` of an environment that names neither `order@0` nor
    `alternatives@0` is S2's (`data@0` has no table)."""
    assert hashlib.sha256((EG.HERE / "relational-fol@0.json").read_bytes()).hexdigest() == S2_BASE_SOURCE_SHA256
    s2 = digest(EG.GRAMMAR_DOMAIN, [["relational-fol@0", S2_BASE_SOURCE_SHA256]])
    assert EG.grammar_id(profiles) == s2


def test_grammar_id_covers_a_staged_table_in_the_environments_order():
    sha = lambda f: hashlib.sha256((EG.HERE / f).read_bytes()).hexdigest()
    got = EG.grammar_id(["alternatives@0", "norms@0", "order@0", "relational-fol@0"])
    assert got == digest(EG.GRAMMAR_DOMAIN, [["alternatives@0", sha("alternatives@0.json")],
                                             ["order@0", sha("order@0.json")],
                                             ["relational-fol@0", sha("relational-fol@0.json")]])
    assert len({EG.grammar_id(p) for p in (["relational-fol@0"], ["order@0", "relational-fol@0"],
                                           ["alternatives@0", "relational-fol@0"])}) == 3


def test_the_lock_hashes_every_generated_module_and_both_new_sources():
    lock = json.loads((ROOT / G.LOCK).read_text())
    for path in ("ve/english_grammar/order@0.json", "ve/english_grammar/alternatives@0.json",
                 "lean/VE/EnglishGrammar/Fixed/Order.lean", "lean/VE/EnglishGrammar/Fixed/Alternatives.lean",
                 G.STAGED_TARGET, G.TABLES_TARGET):
        assert lock["files"][path] == hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def test_the_staged_constructors_are_unfit_until_their_actions_exist():
    """S3.0 adds the `FixedAct` constructors the tables name; their actions are S3.3's. Until then each is
    `unfit` (refused by `Grammar.typed`), never an action that computes, and no fixed table of a profile
    list holds a staged row (`fixedTable` is S2's)."""
    actions = (ROOT / "lean/VE/EnglishGrammar/Actions.lean").read_text()
    staged = [a for a in G.ACTIONS if a in {"intNegate", "intConst", "intTwice", "numeral", "intBracket", "op",
                                           "intCmp", "relOr", "verbSubject", "verbSame"}]
    arm = re.search(r"\n  \| (\.intNegate[^=]*)=> unfit\n", actions)
    assert arm, "the staged constructors' arm"
    named = re.findall(r"\.(\w+)", arm[1])
    assert sorted(named) == sorted(staged)
    rules = (ROOT / "lean/VE/EnglishGrammar/Rules.lean").read_text()
    assert "if profiles.contains baseProfile then relationalFolRows else #[]" in rules


# ------------------------------------------------------------------ the generator's refusals for staged rows

def _staged_one(**changes) -> bytes:
    row = {"tag": "x.y", "lhs": "int_atom", "act": "through", "rhs": [{"n": "numeral"}], **changes}
    return json.dumps([{k: v for k, v in row.items() if v is not None}]).encode()


@pytest.mark.parametrize("changes, message", [
    ({"rhs": [{"n": "int_term"}]}, "not well-founded"),               # int_term (3) under int_atom (2)
    ({"lhs": "int_neg", "rhs": [{"n": "int_atom"}]}, "not well-founded"),
    ({"act": "intCmp", "cmp": "gt", "swapped": False}, "is not one of"),
    ({"act": "intCmp", "cmp": "lt", "swapped": "yes"}, "not true or false"),
    ({"act": "intCmp", "cmp": "lt"}, "fields missing \\['swapped'\\]"),
    ({"act": "numeral"}, "fields missing \\['negative'\\]"),
    ({"act": "numeral", "negative": 1}, "not true or false"),
    ({"lhs": "property_0"}, "unknown nonterminal"),
    ({"rhs": [{"n": "int_constant"}, {"p": "-", "before": "x"}]}, "not true or false"),
])
def test_malformed_staged_rows(changes, message):
    with pytest.raises(G.GrammarSourceError, match=message):
        G.parse_source(_staged_one(**changes), "staged", staged=True)


def test_the_base_table_may_not_name_a_staged_nonterminal():
    with pytest.raises(G.GrammarSourceError, match="unknown nonterminal 'int_term'"):
        G.parse_source(_staged_one(lhs="atom", rhs=["x", {"n": "int_term"}]), "base")
    with pytest.raises(G.GrammarSourceError, match="unknown nonterminal 'int_atom'"):
        G.parse_source(_staged_one(), "base")


def test_every_s2_rule_shape_that_ranks_certifies_ranks_staged_certifies():
    """S3 2.4: an S2 grammar is well-founded under either certificate. Over every pair of S2 nonterminals,
    a first symbol below its left side under `ranks` is below it under `ranksStaged`, so the generator's
    check of the base table under both certificates refuses nothing `ranks` admits."""
    pairs = [(lhs, first) for lhs in G.RANK for first in G.RANK if G.RANK[first] < G.RANK[lhs]]
    assert len(pairs) > 100
    assert all(G.RANK_STAGED[first] < G.RANK_STAGED[lhs] for lhs, first in pairs)
    row = {"tag": "x.y", "lhs": "coordination", "act": "through", "rhs": [{"n": "atom"}]}
    with pytest.raises(G.GrammarSourceError, match="under ranks: not well-founded"):
        G.parse_source(json.dumps([row]).encode(), "base")


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


@pytest.mark.parametrize("profile", [ORDER, ALTERNATIVES])
def test_every_node_of_a_staged_source_replaced_is_refused_with_the_source_error_only(profile):
    """Checklist 5 on the staged sources: each JSON node replaced by 7, true, null, [], {}, a word or a
    10,000-deep array gives `GrammarSourceError` or a valid row that differs in a harmless value."""
    source = G.PROFILES[profile][0]
    original = json.loads((ROOT / source).read_text())
    checked = 0
    for k, row in enumerate(original):
        for path in _nodes(row, (k,)):
            for new in REPLACEMENTS:
                mutated = _replace(original, path, new)
                if mutated == original:
                    continue
                checked += 1
                text = json.dumps(mutated).replace('"deep"', "[" * 10000 + "]" * 10000).encode()
                try:
                    G.parse_source(text, source, staged=True)
                except G.GrammarSourceError:
                    continue
                assert (new is True and path[-1] in {"before", "after", "negative", "swapped"}) or \
                    (new == "word" and (path[-1] in {"tag", "c"} or path[1:2] == ("rhs",) and len(path) == 3)), \
                    (path, new)
    assert checked > 300


# ------------------------------------------------------------------ --check over the staged modules

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


def test_an_edited_staged_rule_names_the_profile_and_the_tag(tree):
    target = tree / G.PROFILES[ORDER][1]
    text = target.read_text()
    line = next(l for l in text.splitlines() if 'tag := "atom.more"' in l)
    target.write_text(text.replace(line, line.replace("(.intCmp .lt true)", "(.intCmp .lt false)")))
    errors = run_check(tree)
    assert any(e.startswith(f"{ORDER}: {G.PROFILES[ORDER][1]} differs from its source at rule atom.more")
               for e in errors), errors


@pytest.mark.parametrize("target, old, new", [
    (G.STAGED_TARGET, "6, 5, 0]", "6, 4, 0]"),
    (G.STAGED_TARGET, '"alt_head"', '"alt_heads"'),
    (G.TABLES_TARGET, '("order@0", orderSha256),', ""),
])
def test_an_edited_generated_extra_is_drift(tree, target, old, new):
    path = tree / target
    text = path.read_text()
    assert old in text
    path.write_text(text.replace(old, new))
    errors = run_check(tree)
    assert f"{target}: differs from what tools/english_grammar_gen.py generates; run --write" in errors


def test_a_tag_shared_by_two_tables_is_refused(tree):
    source = tree / G.PROFILES[ALTERNATIVES][0]
    data = json.loads(source.read_text())
    data[0]["tag"] = "formula.atom"   # a tag of the base table
    source.write_text(json.dumps(data))
    assert "alternatives@0: rule formula.atom repeats a tag of relational-fol@0" in run_check(tree)
    with pytest.raises(G.GrammarSourceError, match="repeats a tag"):
        G.write(tree, "999")


def test_an_edited_staged_source_needs_a_new_version(tree):
    base = (tree / G.LOCK).read_bytes()
    source = tree / G.PROFILES[ORDER][0]
    data = json.loads(source.read_text())
    data[-1]["swapped"] = False       # `at least` read as `at most`
    source.write_text(json.dumps(data))
    with pytest.raises(G.GrammarSourceError, match="give a new --actions-version"):
        G.write(tree)
    version = json.loads(base)["actions_version"] + ".1"
    written = G.write(tree, version)
    assert G.PROFILES[ORDER][1] in written and G.TABLES_TARGET not in written
    assert run_check(tree, base) == []


# ------------------------------------------------------------------ S3.1, Python's part: DRI ruling 2

def _risk_env():
    from ve import Environment
    return Environment(X.FR())


def test_ri7_python_reads_and_renders_the_severity_order():
    """D9 (DRI ruling 2): `risk__more_severe` has the fixed wording `{0} is more severe than {1}`, so Python
    reads ri7 with one derivation and renders the atom with that wording, both directions."""
    from ve import ast
    from ve.english import parse_english, render_english
    env = _risk_env()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UnreviewedVocabularyWarning)
        for left, right in (("catastrophic", "minor"), ("minor", "catastrophic")):
            formula = ast.Binary("risk__more_severe", ast.Const(left), ast.Const(right))
            text = f"{left.capitalize()} is more severe than {right}"
            assert parse_english(env, text + ".").formulas == (formula,)
            assert render_english(formula, env) == text


def test_lx4_pythons_lexicon_now_has_the_severity_order():
    """lx4 is Python of S2: its lexicon had no entry for `risk__more_severe` (V1). The entry is now the
    profile's form, exported to Lean with the other risk wordings; no negative is added."""
    from ve.english import EnglishVocabulary
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UnreviewedVocabularyWarning)
        lexicon = EG.export(EnglishVocabulary(_risk_env()))
    wordings = dict(lexicon["wordings"])
    assert wordings["risk__more_severe"] == "{0} is more severe than {1}"
    assert "risk__more_severe" not in dict(lexicon["negatives"])
    assert {p for p in wordings if p.startswith("risk__")} == {
        "risk__might_lead_to", "risk__class", "risk__more_severe", "risk__or_worse", "risk__less_worst"}


def test_the_severity_order_wording_stays_reserved_for_its_symbol():
    """Spec 2.9, V6 part 3 (Python today): under `risk@0` a declared predicate worded like the severity order
    keeps its quoted fallback; only `risk__more_severe` takes the form."""
    from ve import Environment
    from ve.english import EnglishVocabulary
    raw = X.FR()
    raw["vocabulary"]["predicates"]["graver"] = {"arguments": ["harm", "harm"], "description": "graver",
                                                 "verbalisation": "{0} is more severe than {1}"}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UnreviewedVocabularyWarning)
        words = EnglishVocabulary(Environment(raw))
    assert words.predicates["graver"] == '{0} has the recorded relation "graver" to {1}'
    assert words.predicates["risk__more_severe"] == "{0} is more severe than {1}"


def test_the_severity_order_wording_is_absent_without_risk():
    from ve.english import EnglishVocabulary
    from ve import Environment
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UnreviewedVocabularyWarning)
        words = EnglishVocabulary(Environment(X.FA()))
    assert "risk__more_severe" not in words.predicates
