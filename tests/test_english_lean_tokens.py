"""Python's English grammar converted to word tokens reads like Python (plan section 4, S0 first cut)."""
from ve import Environment, ast, render
from ve.english import english_lark_grammar

from conformance import english_lean_engine as E
from conformance import english_lean_lexer as LX
from conformance import english_lean_tokens as K

ROOT = K.ROOT


def test_phrase_conversion_keeps_canonical_punctuation_spacing():
    exact = lambda token: E.T(('exact', token))
    assert K._phrase_symbols('non-compliant', False) == [
        E.T(('kw', 'non')), exact(('punct', '-', True, True)), E.T(('kw', 'compliant'))]
    assert K._phrase_symbols(',', False) == [exact(('punct', ',', True, False))]
    assert K._phrase_symbols('holds:', False) == [E.T(('kw', 'holds')), exact(('punct', ':', True, False))]
    assert K._phrase_symbols('[', False) == [exact(('punct', '[', False, True))]
    assert K._phrase_symbols(']', False) == [exact(('punct', ']', True, False))]


def test_converted_fluent_grammar_is_well_formed_and_reads_renderings_once():
    env = Environment.from_json((ROOT / 'examples/fluent/environment.json').read_bytes())
    G, names, record = K.convert(english_lark_grammar(env))
    assert E.grammar_wf(G) and E.terminator_free(G)
    assert names[G.start] == 'sentence' and 'LABEL' in names
    owns = ast.Binary('owns', ast.Const('alice'), ast.Const('legacy'))
    formulas = [ast.Forall('service', ast.Unary('reviewed', ast.Var(0))), owns, ast.Not(owns),
                ast.Exists('person', ast.Forall('service', ast.Implies(ast.Unary('deployed', ast.Var(0)),
                                                                       ast.Binary('owns', ast.Var(1), ast.Var(0)))))]
    for formula in formulas:
        text = render(ast.Document((formula,)), env, 've_english')
        (w,) = LX.lex(text)
        assert len(E.parse(G, E.terminal_accepts, 2, None, w)) == 1, text


def test_pythons_two_derivation_fixture_is_ambiguous_over_tokens():
    for row in K.ambiguity_probe():
        assert row['python'].startswith('AmbiguousDerivation')
        assert row['tokens'] == 'many' and len(set(row['witnesses'])) == 2
