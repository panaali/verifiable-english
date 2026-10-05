"""The English-in-Lean engine corpus (spec 8.1 to 8.3, 8.7) against the Python reference engine."""
import pytest

from conformance import english_lean_corpus as C
from conformance import english_lean_engine as E

CORPUS = C.load()


@pytest.mark.parametrize('case', CORPUS['cases'], ids=lambda c: c['id'])
def test_engine_corpus_case(case):
    assert C.run_case(CORPUS, case) == []


def test_corpus_lists_every_fixture_of_the_spec():
    ids = {c['id'] for c in CORPUS['cases']}
    expected = ({f'g{i}' for i in range(1, 21)} | {f'm{i}' for i in range(1, 6)}
                | {f'r{i}' for i in range(1, 11)} | {f'q{i}' for i in range(1, 5)})
    assert ids == expected


def test_budget_never_shortens_a_result():
    G, _ = C._grammar(CORPUS, 'G4')
    w = [('word', 'a', False)] * 4
    results = [E.parse(G, E.terminal_accepts, 4, b, w) for b in range(0, 400)]
    first = next(i for i, r in enumerate(results) if r is not None)
    assert all(r is None for r in results[:first])
    assert all(r == results[first] for r in results[first:])
    assert len(results[first]) == 3


def test_matching_of_the_english_terminals():
    acc = E.terminal_accepts
    word = lambda s, initial=False: ('word', s, initial)
    assert acc(('kw', 'every'), word('Every', True)) and not acc(('kw', 'every'), word('Every'))
    assert not acc(('kw', 'every'), word('EVERY', True))
    assert acc(('content', 'service'), word('SERVICE')) and acc(('content', 'service'), word('ſervice'))
    assert acc(('content', 'kin'), word('Kin')) and acc(('content', 'is'), word('İs'))
    assert not acc(('content', 'café'), word('CAFÉ'))   # folding is ASCII plus four characters
    assert acc(('exact', ('word', 'Legacy', False)), word('Legacy', True))
    assert acc(('exact', ('quoted', 'svc')), ('quoted', 'svc')) and not acc(('exact', ('quoted', 'svc')), word('svc'))
    assert acc(('cls', ('label', 'S')), ('label', 'S', 12)) and not acc(('cls', ('label', 'S')), ('label', 'T', 1))
    assert acc(('cls', ('numeral',)), ('numeral', -3))


def test_terminator_condition_w4():
    ok = E.Grammar((E.Rule(0, (E.T(('kw', 'x')),)),), 0, (0,))
    bad = E.Grammar((E.Rule(0, (E.T(('kw', 'x')), E.T(('exact', ('punct', '.'))))),), 0, (0,))
    assert E.grammar_wf(bad) and not E.terminator_free(bad)
    assert E.terminator_free(ok)


def test_trees_round_trip_through_json():
    G, _ = C._grammar(CORPUS, 'G6')
    w = [('word', 'every', False), ('label', 'S', 3)]
    (t,) = E.parse(G, E.terminal_accepts, 2, None, w)
    assert E.tree_from_json(G, E.tree_to_json(G, t)) == t
    assert E.show_tree(G, t) == 'r0(every, r3(S3))'
