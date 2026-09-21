import json
import subprocess
import sys

from ve.ast import And, Exists, Forall, Not, Top
from ve.attacks import validate_attack
from ve.equivalence import Budgets, DIFFERENT, UNKNOWN
from ve.evaluate import evaluate
from ve.model import FiniteModel
from ve.ast import formula_to_data
from test_equivalence import ENV, P, Q, F


def test_reject_alpha_and_nontrivial_logical_fake_attacks():
    for other in (F, Not(Not(F)), And(F, Top())):
        result = validate_attack(ENV, F, other)
        assert not result.accepted and result.status == 'REJECTED'
        assert 'fake_attack' in result.reason
    assert validate_attack(ENV, F, F, Budgets(0, 0, 0, 0)).status == 'REJECTED'


def test_valid_attack_classifications_replay_and_prefer_nonvacuous_models():
    for a, b, label in ((Exists('item', And(P, Q)), Exists('item', P), 'weakening'),
                        (Exists('item', P), Exists('item', And(P, Q)), 'strengthening'),
                        (Exists('item', P), Exists('item', Q), 'incomparable'),
                        (F, Top(), 'weakening')):
        result = validate_attack(ENV, a, b)
        assert result.accepted and result.classification == label
        assert result.comparison.status == DIFFERENT
        assert len(result.witnesses) == (2 if label == 'incomparable' else 1)
        for witness in result.witnesses:
            model = FiniteModel.from_dict(ENV, witness['model'])
            assert evaluate(ENV, a, model).value == witness['faithful_value']
            assert evaluate(ENV, b, model).value == witness['attacked_value']
            assert witness['faithful_value'] != witness['attacked_value']
            assert witness['quality']['non_empty'] is True
            assert witness['quality']['non_vacuous'] is True
        assert not result.warnings


def test_empty_only_witness_is_retained_with_explicit_warning():
    # forall p -> exists p fails only at the empty domain.
    result = validate_attack(ENV, Forall('item', P), Exists('item', P))
    assert result.accepted and result.classification == 'incomparable'
    empty = next(w for w in result.witnesses if w['direction'] == 'a_not_implies_b')
    assert not empty['quality']['non_empty']
    assert result.warnings


def test_nonempty_preference_is_separate_from_guard_coverage():
    a = And(Forall('item', Not(P)), F)
    result = validate_attack(ENV, a, Top())
    assert result.accepted
    # F's antecedent may be activated where a is false; the witness search must
    # check coverage on BOTH input formulas, independently of truth short-circuit.
    assert result.witnesses[0]['quality']['non_empty']
    assert result.witnesses[0]['quality']['non_vacuous']


def test_checked_difference_without_direction_classification_is_unknown():
    result = validate_attack(ENV, Exists('item', P), Top(), Budgets(max_proof_steps=0))
    assert result.status == UNKNOWN and not result.accepted
    assert result.comparison.status == DIFFERENT
    assert result.witnesses and result.classification is None


def test_jsonl_cli_continues_after_bad_row_and_stores_models(tmp_path):
    rows = [
        {'id': 'good', 'environment': ENV.to_dict(), 'faithful': formula_to_data(ENV, F),
         'attacked': 'true.\n'},
        {'id': 'fake', 'environment': ENV.to_dict(), 'faithful': formula_to_data(ENV, F),
         'attacked': formula_to_data(ENV, Not(Not(F)))},
    ]
    input_path = tmp_path / 'input.jsonl'
    output_path = tmp_path / 'output.jsonl'
    input_path.write_text(json.dumps(rows[0]) + '\n{broken\n' + json.dumps(rows[1]) + '\n')
    process = subprocess.run([sys.executable, '-m', 've.attacks', str(input_path), '--output', str(output_path)],
                             capture_output=True, text=True)
    assert process.returncode == 2, process.stderr
    output = [json.loads(x) for x in output_path.read_text().splitlines()]
    assert [x['status'] for x in output] == ['VALID', 'InvalidInput', 'REJECTED']
    assert output[0]['id'] == 'good' and output[0]['witnesses'][0]['model']
    assert json.loads(process.stderr)['rows'] == 3
    process = subprocess.run([sys.executable, '-m', 've.attacks', str(input_path), '--output', str(input_path)],
                             capture_output=True, text=True)
    assert process.returncode == 2
    assert input_path.read_text().startswith(json.dumps(rows[0]))
