"""Executable contract for bounded constrained-decoding grammars.

The random derivation sampler deliberately caps derivation height.  Generated
grammars are recursive, so an uncapped uniform rule walk need not terminate and
is not representative of a decoder's finite token budget.
"""

from __future__ import annotations

import random
import re

import pytest
from hypothesis import assume, given, settings, strategies as st
from lark import Lark
from lark.lexer import PatternStr

from ve import ast
from ve.environment import Environment
from ve.grammar import export_grammar, structured_output_spec
from ve.parser import _Parser, parse
from ve.printer import print_document

from test_properties import ENV, closed_formula


MIXED_ENV = Environment.from_dict(
    {
        "language": "ve.core@0",
        "profile": "relational-fol@0",
        "spec_revision": "ve-v0-draft-2026-09-20",
        "vocabulary": {
            "sorts": {"item": {"description": "An item."}, "place": {"description": "A place."}},
            "predicates": {
                "marked": {"arguments": ["item"], "description": "Is marked."},
                "near": {"arguments": ["item", "place"], "description": "Is near."},
                "linked": {"arguments": ["place", "place"], "description": "Is linked."},
            },
            "constants": {
                "token": {"sort": "item", "description": "An item token."},
                "home": {"sort": "place", "description": "A home place."},
            },
        },
    }
)


def _lark(grammar: str) -> Lark:
    return Lark(grammar, parser="earley", lexer="dynamic_complete")


def _accepts(parser: Lark, text: str) -> bool:
    try:
        parser.parse(text)
    except Exception:
        return False
    return True


class _SyntaxParser(_Parser):
    """Run the production syntax parser without name resolution/checking."""

    def term(self):
        if self.s.startswith("@", self.i):
            self.i += 1
            name, _ = self.identifier("constant identifier")
            return ast.Const(name)
        name, _ = self.identifier("term")
        # The value is immaterial: document() does not invoke the AST checker.
        return ast.Var(int(name[1:]) if name.startswith("x") and name[1:].isdigit() else 0)


def _syntax_parse(env: Environment, text: str) -> ast.Document:
    return _SyntaxParser(env, text).document()


class _CompiledSampler:
    """Sample literal-only Lark productions, bounded by derivation height."""

    def __init__(self, parser: Lark, seed: int):
        self.random = random.Random(seed)
        inner = parser.parser.parser
        self.rules = {}
        for rule in inner.parser_conf.rules:
            self.rules.setdefault(rule.origin.name, []).append(rule)
        self.terminals = {terminal.name: terminal.pattern for terminal in parser.terminals}
        self.min_height = {name: 10**9 for name in self.rules}
        changed = True
        while changed:
            changed = False
            for name, rules in self.rules.items():
                for rule in rules:
                    heights = []
                    possible = True
                    for symbol in rule.expansion:
                        if symbol.is_term:
                            heights.append(0)
                        elif self.min_height.get(symbol.name, 10**9) < 10**9:
                            heights.append(self.min_height[symbol.name])
                        else:
                            possible = False
                    height = 1 + max(heights, default=0)
                    if possible and height < self.min_height[name]:
                        self.min_height[name] = height
                        changed = True

    def sample(self, max_height: int = 18) -> str:
        return self._symbol("start", max_height)

    def _symbol(self, name: str, height: int) -> str:
        eligible = []
        for rule in self.rules[name]:
            needed = max(
                (self.min_height.get(s.name, 10**9) for s in rule.expansion if not s.is_term),
                default=0,
            )
            if needed < height:
                eligible.append(rule)
        if not eligible:
            raise AssertionError(f"no finite production for {name!r} at height {height}")
        rule = self.random.choice(eligible)
        pieces = []
        for symbol in rule.expansion:
            if symbol.is_term:
                pattern = self.terminals[symbol.name]
                assert isinstance(pattern, PatternStr), f"non-literal terminal {symbol.name}: {pattern!r}"
                pieces.append(pattern.value)
            else:
                pieces.append(self._symbol(symbol.name, height - 1))
        return "".join(pieces)


@pytest.mark.parametrize("mode", ["full", "syntax"])
def test_200_random_lark_derivations_are_accepted(mode):
    grammar = export_grammar(MIXED_ENV, dialect="lark", mode=mode, max_binder_depth=3, max_binders=4)
    sampler = _CompiledSampler(_lark(grammar), seed=731 + (mode == "syntax"))
    samples = [sampler.sample() for _ in range(200)]
    accepted = 0
    for text in samples:
        if mode == "full":
            document = parse(MIXED_ENV, text)
            assert text == print_document(MIXED_ENV, document)
        else:
            _syntax_parse(MIXED_ENV, text)
        accepted += 1
    assert accepted == len(samples), f"acceptance {accepted}/{len(samples)}"


def _binder_count(node) -> int:
    if isinstance(node, (ast.Forall, ast.Exists)):
        return 1 + _binder_count(node.body)
    if isinstance(node, (ast.And, ast.Or, ast.Implies)):
        return _binder_count(node.left) + _binder_count(node.right)
    if isinstance(node, ast.Not):
        return _binder_count(node.body)
    return 0


@given(closed_formula(max_depth=3))
@settings(max_examples=100, deadline=None, derandomize=True)
def test_canonical_property_formulas_are_in_full_grammar(formula):
    # Preorder names have a statement-wide counter, so total binders (not merely
    # nesting depth) must fit the grammar's finite x0..x(k-1) vocabulary.
    assume(_binder_count(formula) <= 3)
    grammar = export_grammar(ENV, dialect="lark", mode="full", max_binder_depth=3, max_binders=3)
    text = print_document(ENV, ast.Document((formula,)))
    assert _accepts(_lark(grammar), text)


@st.composite
def mixed_typed_formula(draw):
    """Recursive, context-sorted formulas with at most three total binders."""

    constants = {"item": [ast.Const("token")], "place": [ast.Const("home")]}

    def term(sort, context):
        choices = list(constants[sort])
        choices += [ast.Var(index) for index, active in enumerate(context) if active == sort]
        return draw(st.sampled_from(choices))

    def formula(context=(), depth=0, binder_budget=3):
        leaves = [ast.Top(), ast.Bottom()]
        leaves.append(ast.Unary("marked", term("item", context)))
        leaves.append(ast.Binary("near", term("item", context), term("place", context)))
        leaves.append(ast.Binary("linked", term("place", context), term("place", context)))
        equal_sort = draw(st.sampled_from(["item", "place"]))
        leaves.append(ast.Eq(term(equal_sort, context), term(equal_sort, context)))
        if depth >= 3:
            return draw(st.sampled_from(leaves)), 0
        kind = draw(st.sampled_from(["leaf", "not", "binary", "binder"]))
        if kind == "leaf":
            return draw(st.sampled_from(leaves)), 0
        if kind == "not":
            child, used = formula(context, depth + 1, binder_budget)
            return ast.Not(child), used
        if kind == "binder" and binder_budget:
            sort = draw(st.sampled_from(["item", "place"]))
            child, used = formula((sort, *context), depth + 1, binder_budget - 1)
            quantifier = draw(st.sampled_from([ast.Forall, ast.Exists]))
            return quantifier(sort, child), used + 1
        split = draw(st.integers(min_value=0, max_value=binder_budget))
        left, left_used = formula(context, depth + 1, split)
        right, right_used = formula(context, depth + 1, binder_budget - split)
        connective = draw(st.sampled_from([ast.And, ast.Or, ast.Implies]))
        return connective(left, right), left_used + right_used

    return formula()[0]


@given(mixed_typed_formula())
@settings(max_examples=100, deadline=None, derandomize=True)
def test_mixed_canonical_formulas_are_in_full_grammar(formula):
    text = print_document(MIXED_ENV, ast.Document((formula,)))
    parser = _lark(export_grammar(MIXED_ENV, dialect="lark", mode="full", max_binder_depth=3))
    assert _accepts(parser, text)


def test_full_scope_and_sort_discipline_while_syntax_mode_is_cheaper():
    full = _lark(export_grammar(MIXED_ENV, dialect="lark", mode="full", max_binder_depth=3))
    syntax = _lark(export_grammar(MIXED_ENV, dialect="lark", mode="syntax", max_binder_depth=3))
    examples = [
        "(for every item x0, (x0 is marked)) and (x0 is marked).\n",  # sibling leak
        "for every place x0, (x0 is marked).\n",  # unary argument sort
        "for every item x0, (x0 near x0).\n",  # binary second argument sort
        "for every item x0, (x0 equals @home).\n",  # equality variable sort
    ]
    for text in examples:
        assert not _accepts(full, text)
        assert _accepts(syntax, text)


@pytest.mark.parametrize(
    "text",
    [
        "@token near.\n",  # arity
        "@token missing @home.\n",  # predicate vocabulary
        "@missing is marked.\n",  # constant vocabulary
        "for every missing x0, (true).\n",  # sort vocabulary
        "@token equals @home.\n",  # constants retain their declared sorts
        "for every item x1, (true).\n",  # noncanonical first binder
        " true.\n",
        "true. \n",
        "true.",
        "TRUE.\n",
    ],
)
def test_both_modes_reject_invalid_closed_language_or_layout(text):
    for mode in ("full", "syntax"):
        parser = _lark(export_grammar(MIXED_ENV, dialect="lark", mode=mode, max_binder_depth=3))
        assert not _accepts(parser, text), (mode, text)


def test_preorder_numbering_resets_per_statement_and_tracks_siblings():
    parser = _lark(export_grammar(MIXED_ENV, dialect="lark", mode="full", max_binder_depth=2, max_binders=3))
    valid = (
        "(for every item x0, (x0 is marked)) and "
        "(there exists place x1, (@token near x1)).\n"
        "for every item x0, (x0 is marked).\n"
    )
    assert _accepts(parser, valid)
    assert not _accepts(parser, valid.replace("place x1", "place x0"))


def test_depth_and_total_binder_limits_are_independent():
    parser = _lark(export_grammar(MIXED_ENV, dialect="lark", mode="full", max_binder_depth=2, max_binders=3))
    at_depth = "for every item x0, (there exists place x1, (@token near x1)).\n"
    too_deep = "for every item x0, (there exists place x1, (for every item x2, (true))).\n"
    three_siblings = (
        "((for every item x0, (true)) and (for every item x1, (true))) and "
        "(for every item x2, (true)).\n"
    )
    four_siblings = (
        "(((for every item x0, (true)) and (for every item x1, (true))) and "
        "(for every item x2, (true))) and (for every item x3, (true)).\n"
    )
    assert _accepts(parser, at_depth)
    assert not _accepts(parser, too_deep)
    assert _accepts(parser, three_siblings)
    assert not _accepts(parser, four_siblings)


def test_two_digit_preorder_names_in_sibling_scopes():
    source = "for every item x0, (x0 is marked)"
    for index in range(1, 12):
        source = f"({source}) and (for every item x{index}, (x{index} is marked))"
    source += ".\n"
    parser = _lark(export_grammar(MIXED_ENV, max_binder_depth=1, max_binders=12))
    parser.parse(source)
    assert print_document(MIXED_ENV, parse(MIXED_ENV, source)) == source


def test_structured_output_spec_carries_schema_and_matching_grammar():
    spec = structured_output_spec(MIXED_ENV, dialect="lark", mode="full", max_binder_depth=2)
    schema = spec["json_schema"]
    assert schema["type"] == "object"
    assert schema["required"] == ["ve", "explanation"]
    assert schema["properties"]["ve"]["type"] == "string"
    assert schema["properties"]["explanation"]["type"] == "string"
    assert schema["properties"]["ve"]["x-ve-grammar"]["grammar"] == export_grammar(
        MIXED_ENV, dialect="lark", mode="full", max_binder_depth=2
    )
    assert spec["grammar"] == export_grammar(
        MIXED_ENV, dialect="lark", mode="full", max_binder_depth=2, wrapper=True
    )


def test_wrapper_accepts_fixed_order_json_with_escaped_ve():
    grammar = export_grammar(
        MIXED_ENV, dialect="lark", mode="full", max_binder_depth=2, wrapper=True
    )
    parser = _lark(grammar)
    assert _accepts(parser, r'{"ve": "true.\n", "explanation": "why \"yes\""}')
    assert not _accepts(parser, r'{"explanation": "why", "ve": "true.\n"}')


@pytest.mark.parametrize("dialect", ["lark", "ebnf", "gbnf"])
def test_all_dialects_are_nonempty_and_closed_vocabulary(dialect):
    grammar = export_grammar(MIXED_ENV, dialect=dialect, mode="full", max_binder_depth=2)
    assert grammar.strip()
    assert "marked" in grammar and "near" in grammar and "token" in grammar
    assert "missing" not in grammar


def test_empty_vocabulary_and_zero_binder_bound_still_generate_booleans():
    empty = Environment.from_dict(
        {**MIXED_ENV.to_dict(), "vocabulary": {"sorts": {}, "predicates": {}, "constants": {}}}
    )
    parser = _lark(export_grammar(empty, max_binder_depth=0, max_binders=0))
    assert _accepts(parser, "true.\nfalse.\n")
    assert not _accepts(parser, "for every item x0, (true).\n")


@pytest.mark.parametrize(
    "options",
    [
        {"dialect": "peg"},
        {"mode": "almost"},
        {"max_binder_depth": -1},
        {"max_binder_depth": True},
        {"max_binders": -1},
        {"max_binders": False},
        {"max_rules": 0},
    ],
)
def test_invalid_configuration_is_rejected(options):
    with pytest.raises(ValueError):
        export_grammar(MIXED_ENV, **options)


def test_rule_budget_is_enforced():
    with pytest.raises(Exception, match="Grammar exceeds|budget exceeded"):
        export_grammar(MIXED_ENV, mode="full", max_binder_depth=3, max_rules=5)


def test_export_is_independent_of_declaration_insertion_order():
    data = MIXED_ENV.to_dict()
    vocabulary = data["vocabulary"]
    for key in ("sorts", "predicates", "constants"):
        vocabulary[key] = dict(reversed(list(vocabulary[key].items())))
    reordered = Environment.from_dict(data)
    assert export_grammar(reordered) == export_grammar(MIXED_ENV)


@pytest.mark.parametrize("dialect", ["gbnf", "ebnf"])
def test_plain_dialect_rules_have_lark_parity(dialect):
    """The current literal/rule subset differs only in assignment syntax."""
    native = export_grammar(MIXED_ENV, dialect=dialect, mode="full", max_binder_depth=2)
    translated = re.sub(r"^root ::=", "start :", native, count=1, flags=re.MULTILINE)
    translated = re.sub(r"^([a-z][a-z0-9]*) ::=", r"\1 :", translated, flags=re.MULTILINE)
    parser = _lark(translated)
    reference = _CompiledSampler(
        _lark(export_grammar(MIXED_ENV, dialect="lark", mode="full", max_binder_depth=2)),
        seed=991,
    )
    assert all(_accepts(parser, reference.sample()) for _ in range(50))
