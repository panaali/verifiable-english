"""The S0 measurement helpers of English in Lean (plan section 5)."""
from ve import Environment
from ve.english import english_lark_grammar, _literal_pattern

from conformance import english_lean_s0 as S


def test_phrase_regex_is_recognised_and_open_classes_are_not():
    assert S._phrase_of_regex(_literal_pattern('is not the case')) == 'is not the case'
    assert S._phrase_of_regex(_literal_pattern('non-citizen')) == 'non-citizen'
    assert S._phrase_of_regex('(?:S|P)[1-9][0-9]*') is None
    assert S._phrase_of_regex('-?(?:0|[1-9][0-9]*)(?![0-9])') is None


def test_fluent_grammar_has_no_empty_rule_and_no_left_recursion():
    env = Environment.from_json((S.ROOT / 'examples/fluent/environment.json').read_bytes())
    inv = S.grammar_inventory(english_lark_grammar(env))
    assert inv['empty_rules'] == [] and inv['left_corner_cycles'] == []
    assert inv['document_level_cycles'] == ['__start_plus_0']
    assert [o['name'] for o in inv['open_regex_terminals']] == ['LABEL']
    assert inv['unlexable_phrases'] == [{'phrase': '.', 'reject': 'emptySentence'}]


def test_attribute_product_is_factored_into_a_sum():
    predicates = {f'r{k}': {'arguments': ['service', 'shade'], 'description': 'R.', 'functional': True, 'total': True}
                  for k in range(3)}
    predicates.update({f'p{k}': {'arguments': ['shade'], 'description': 'P.'} for k in range(4)})
    env = Environment({**S.DATA_HEADER, 'vocabulary': {
        'sorts': {'service': {'description': 'S.'}, 'shade': {'description': 'H.'}},
        'predicates': predicates, 'constants': {}}})
    assert S.attribute_product(env) == {'pairs': 12, 'relations': 3, 'properties': 4, 'factored_rules': 7}
