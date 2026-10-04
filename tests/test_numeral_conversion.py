"""Decimal text from input never reaches a bare `int(` (english-lean looprecheck1, finding 1).

Python's `int(str)` and `str(int)` raise a bare ValueError past `sys.get_int_max_str_digits()` digits
(4,300 by default, 640 at the least). A numeral is converted by `ve.ast.numeral_value`, which checks
the 40-character bound first, and an index Lean reads as an unbounded Nat by `ve.ast.decimal_value`.
The lint below holds every other `int(` call in `ve/` to a reviewed list, so a new conversion of
input text fails here until it uses one of the two or is shown to be bounded.
"""
import ast as pyast
from pathlib import Path
import sys

import pytest

from conformance import order
from ve import ast
from ve.admission import parse_label
from ve.english import parse_english
from ve.errors import ResourceLimit
from ve.norm_english import parse_english as parse_norm_english
from ve.order import parse_token
from ve.surface.softnorms import parse_header_options
from tests.test_english_unambiguity import _soft_env
from tests.test_norms import environment, permission

ROOT = Path(__file__).resolve().parents[1]
# 41: one past the bound; 641: past Python's lowest digit limit; 4301: past the default; 9990: near
# the 10,000-character text limit.
LONG = (41, 641, 4301, 9990)


@pytest.fixture(params=['default', 'lowest'])
def digit_limit(request):
    """Run at the default digit limit and at Python's lowest (640)."""
    before = sys.get_int_max_str_digits()
    sys.set_int_max_str_digits(640 if request.param == 'lowest' else before)
    yield
    sys.set_int_max_str_digits(before)


ENGLISH = {
    'numeral': lambda d: f'n is at most {d}.',
    'negative': lambda d: f'n is at most -{d}.',
    'coefficient': lambda d: f'n is at most [{d} * n].',
    'sum': lambda d: f'n is at most [n + {d}].',
}


@pytest.mark.parametrize('route', sorted(ENGLISH))
def test_english_numerals_at_the_bound_parse(route):
    env = order.environment()
    digits = '9' * (ast.MAX_NUMERAL_CHARS - (route == 'negative'))
    assert parse_english(env, ENGLISH[route](digits)).formulas


@pytest.mark.parametrize('digits', LONG)
@pytest.mark.parametrize('route', sorted(ENGLISH))
def test_english_long_numerals_are_resource_limits(route, digits, digit_limit):
    with pytest.raises(ResourceLimit):
        parse_english(order.environment(), ENGLISH[route]('9' * digits))


@pytest.mark.parametrize('digits', LONG)
def test_formal_long_numerals_are_resource_limits(digits, digit_limit):
    from ve.parser import parse
    env = order.environment()
    for source in (f"{'9' * digits} < 0.\n", f"-{'9' * digits} < 0.\n", f"[{'9' * digits} * @n] < 0.\n"):
        with pytest.raises(ResourceLimit):
            parse(env, source)


def test_integer_values_of_any_size_are_resource_limits(digit_limit):
    assert ast.integer_value(10 ** 40 - 1) == 10 ** 40 - 1
    assert ast.integer_value(-(10 ** 39 - 1)) == -(10 ** 39 - 1)
    for value in (10 ** 40, -(10 ** 39), 10 ** 5000, -(10 ** 5000)):
        with pytest.raises(ResourceLimit):
            ast.integer_value(value)
    for value in (0, 7, -7, 10 ** 40 - 1, -(10 ** 39 - 1), 10 ** 40, -(10 ** 39)):
        assert (len(str(value)) <= ast.MAX_NUMERAL_CHARS) == ast._fits_numeral(value)


@pytest.mark.parametrize('digits', (1, 599, 600, 601, 641, 4301, 9990))
def test_decimal_value_and_text_are_inverse_at_any_length(digits, digit_limit):
    text = '9' * digits
    assert ast.decimal_text(ast.decimal_value(text)) == text
    assert ast.decimal_text(-ast.decimal_value(text)) == '-' + text


@pytest.mark.parametrize('digits', LONG)
def test_reading_labels_read_indices_as_lean_does(digits, digit_limit):
    """Lean's `parseLabel` reads both numbers with `String.toNat?` (any length) and renders back."""
    for label in (f"readings:s1@{'9' * digits}:0", f"readings:s1@1:{'9' * digits}",
                  f"readings:s1@{'9' * digits}:all"):
        parsed = parse_label(label)
        assert parsed is not None and parsed.render() == label
    assert parse_label(f"readings:s1@0{'9' * digits}:0") is None


@pytest.mark.parametrize('digits', LONG)
def test_witness_tokens_of_any_length_are_out_of_scope(digits, digit_limit):
    from ve.order import Branch, token_sort
    token = 'w:' + '9' * digits
    assert parse_token(token) == token
    assert token_sort(order.environment(), Branch([]), token) is None


@pytest.mark.parametrize('digits', LONG)
def test_norm_english_rule_numbers_are_resource_limits(digits, digit_limit):
    env = environment({'permitted': permission()})
    big = '9' * digits
    for text in (f'Rule {big}. Every act may be done.',
                 f'Rule 1. Every act may be done.\nRule {big} takes precedence over rule 1.',
                 f'Rule 1 (exception to rule {big}). Every act may be done.'):
        with pytest.raises(ResourceLimit):
            parse_norm_english(env, text)
    soft = _soft_env()
    for text in (f'Rule {big}. Every act should be done.',
                 f'Rule 1. Every act should be done. The exception to rule {big} takes account of care.',
                 f'Rule 1. Every act should be done. Rule {big} is excepted when every act is done.'):
        with pytest.raises(ResourceLimit):
            parse_norm_english(soft, text)
    with pytest.raises(ResourceLimit):
        parse_header_options(f'exception to rule {big}')


def test_assist_item_index_is_ascii_and_any_length(tmp_path):
    from ve.assist.sources import select_p5_item
    from ve.errors import VEError
    path = tmp_path / 'items.jsonl'
    path.write_text('{"id": "a"}\n{"id": "b"}\n')
    assert select_p5_item(path, '1') == {'id': 'b'}
    for item in ('²', '9' * 4301):
        with pytest.raises(VEError):
            select_p5_item(path, item)


# ------------------------------------------------------------------ the lint

# Every `int(` call in `ve/` whose argument may be text, with why it cannot exceed the digit limit.
# Calls on a comparison (`int(a == b)`) count a Boolean and are not listed.
REVIEWED = {
    ('ve/adapters/records.py', 'int(upper)'): 'a quantifier inside a pattern of at most 256 characters',
    ('ve/ast.py', 'int(text)'): 'numeral_value: after the 40-character bound',
    ('ve/ast.py', 'int(block)'): 'decimal_value: blocks of 600 digits, below the lowest limit (640)',
    ('ve/backends/lean_service.py', 'int(digits)'): "Lean's JSON integers; the ValueError falls back to Decimal",
    ('ve/backends/lean_service.py', 'int(line.split()[1])'): '/proc status, not input',
    ('ve/english.py', 'int(part[1])'): 'a slot {0}..{5} of a template',
    ('ve/english.py', 'int(p[1])'): 'a slot {0}..{5} of a template',
    ('ve/english.py', 'int(listed)'): 'a Boolean',
    ('ve/readings_route.py', 'int(x)'): "indices in Lean's own finding text",
    ('ve/softnorms_contract.py', 'int(token)'): 'a path the contract engine built from list positions',
    ('ve/softnorms_contract.py', 'int(items[1][-1])'): 'a path the contract engine built from list positions',
    ('ve/softnorms_contract.py', 'int(items[0][-1])'): 'a path the contract engine built from list positions',
    ('ve/speech_document.py', 'int(value)'): 'the JSON parse_int hook; its ValueError is caught as invalid front matter',
    ('ve/stream_audit.py', 'int(body[1:], 16)'): 'an escape of at most 8 hex digits; ValueError caught',
    ('ve/stream_audit.py', 'int(body, 8)'): 'an octal escape of at most 3 digits',
    ('ve/surface/time.py', 'int(long_date[1])'): 'a day of the month, 1 to 31',
    ('ve/surface/time.py', 'int(node[2])'): 'a decoded wire numeral, at most 40 characters',
    ('ve/surface/time.py', 'int(formula[2][2])'): 'a decoded wire numeral, at most 40 characters',
    ('ve/surface/time.py', 'int(constants[name])'): 'a model value, already an integer',
    ('ve/units.py', 'int(text)'): 'decodeScale: after the 40-character bound',
    ('ve/units.py', 'int(slot)'): 'a slot of at most two digits (_SLOT)',
    ('ve/units.py', "int(env.units[tag]['scale'])"): 'a scale decodeScale admitted (at most 40 characters)',
    ('ve/units.py', "int(''.join(digits))"): 'after the 40-digit bound of the decimal',
    ('ve/units.py', "int(record['scale'])"): 'a scale decodeScale admitted (at most 40 characters)',
    ('ve/wire.py', 'int(text)'): 'after the 16-character bound',
    ('ve/wire_contract/engine.py', 'int(head[1:] or 0)'): 'a level in a contract pattern',
    ('ve/wire_contract/engine.py', 'int(token)'): 'a path the contract engine built from list positions',
}


def int_calls():
    for path in sorted((ROOT / 've').rglob('*.py')):
        rel = str(path.relative_to(ROOT))
        for node in pyast.walk(pyast.parse(path.read_text(), rel)):
            if (isinstance(node, pyast.Call) and isinstance(node.func, pyast.Name) and node.func.id == 'int'
                    and node.args and not isinstance(node.args[0], pyast.Compare)):
                yield rel, pyast.unparse(node)


def test_every_int_conversion_in_ve_is_bounded_or_reviewed():
    found = set(int_calls())
    unreviewed = sorted(found - set(REVIEWED))
    assert not unreviewed, ('convert input text with ve.ast.numeral_value (a numeral) or decimal_value '
                            f'(an unbounded index), or add a reviewed bound: {unreviewed}')
    assert not set(REVIEWED) - found, f'stale entries: {sorted(set(REVIEWED) - found)}'
