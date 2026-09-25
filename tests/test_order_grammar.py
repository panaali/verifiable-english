"""Order grammar export is typed in full mode and covers canonical terms."""

import json

import pytest
from lark import Lark

from conformance.order import environment
from ve.grammar import export_grammar, structured_output_spec
from ve.parser import parse
from ve.printer import print_document


ENV = environment()


def accepts(grammar, source):
    try:
        (grammar if isinstance(grammar, Lark) else Lark(grammar, parser="earley")).parse(source)
        return True
    except Exception:
        return False


@pytest.mark.parametrize("mode", ["full", "syntax"])
def test_order_lark_accepts_canonical_comparisons_and_predicates(mode):
    grammar = export_grammar(ENV, mode=mode, max_binder_depth=2)
    for source in (
        "@n < [2 * @m].\n",
        "[-1 * 2] <= -@n.\n",
        "[@n - -3] equals [1 + @m].\n",
        "for every item x0, (x0 value [@n + -2]).\n",
        "@n is marked.\n",
    ):
        assert accepts(grammar, source), source
        assert print_document(ENV, parse(ENV, source)) == source
    for source in ("-2 <= -0.\n", "@n < [2 * @a].\n", "[01 * @n] < @m.\n"):
        assert not accepts(grammar, source), source


def test_order_full_grammar_restricts_scope_and_sort():
    full = export_grammar(ENV, mode="full", max_binder_depth=2)
    syntax = export_grammar(ENV, mode="syntax", max_binder_depth=2)
    wrong_sort = "for every item x0, (x0 < 2).\n"
    assert not accepts(full, wrong_sort)
    assert accepts(syntax, wrong_sort)
    assert not accepts(full, "x0 < 2.\n")
    assert accepts(syntax, "x0 < 2.\n")


def test_order_wrapper_and_gbnf_export():
    for dialect in ("lark", "gbnf"):
        grammar = export_grammar(ENV, dialect=dialect, wrapper=True, max_binder_depth=1)
        assert "numeral" in grammar and "coefficient" in grammar
    spec = structured_output_spec(ENV, max_binder_depth=1)
    payload = json.dumps({"ve": "@n <= 3.\n", "explanation": "checked"})
    assert accepts(spec["grammar"], payload)


@pytest.mark.parametrize("mode", ["full", "syntax"])
@pytest.mark.parametrize("wrapper", [False, True])
@pytest.mark.parametrize("dialect", ["lark", "gbnf", "ebnf"])
def test_order_coefficient_families_round_trip_all_exports(mode, wrapper, dialect):
    grammar = export_grammar(ENV, dialect=dialect, mode=mode, wrapper=wrapper,
                             max_binder_depth=1)
    parser = Lark(grammar, parser="earley") if dialect == "lark" else None
    for coefficient in ("-2", "-9", "-20", "-99", "-100", "-12345678901234567890",
                        "0", "1", "2", "99", "12345678901234567890"):
        source = f"[{coefficient} * @n] < -99.\n"
        assert print_document(ENV, parse(ENV, source)) == source
        candidate = json.dumps({"ve": source, "explanation": "ok"}) if wrapper else source
        if parser is not None:
            assert accepts(parser, candidate), (dialect, mode, wrapper, source)
        else:
            assert 'coefficient ::=' in grammar
            assert '[1-9] [0-9]+' in grammar
