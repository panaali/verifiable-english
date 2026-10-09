"""The E2.5 records, saved: the readability failure that kept Python authority then (E2.6 replays it in
`test_english_e26_evidence.py`), the directed coverage and the corpus A/B, never a moving checkout."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/lean-first/e2/evidence'


def saved(name):
    return json.loads((EVIDENCE / name).read_text())


def test_e25_readability_records_failed_at_the_reviewed_merge():
    comparison = saved('readability-comparison.json')
    assert comparison['reading_items'] == 30
    assert comparison['writing_attempts'] == 36
    assert comparison['writing_verdict_changes'] == 0
    assert comparison['writing_message_changes'] == 6
    assert comparison['reading_newly_unavailable'] == ['R23', 'R24', 'R25', 'R29', 'R30']
    assert comparison['reading_unavailable_both'] == []
    assert comparison['shadow_writing_differences'] == 0


def test_directed_coverage_records_reach_all_45_rules():
    coverage = saved('coverage-directed.json')
    assert len(coverage['target_rules']) == coverage['covered'] == 45
    assert coverage['uncovered'] == [] and coverage['different'] == 0
    for tag, index in coverage['rule_record'].items():
        assert tag in coverage['records'][index]['fixed_rules']
        assert coverage['records'][index]['classes'] == []


def test_corpus_ab_is_reported_from_saved_comparisons():
    conformance = saved('ab-conformance-compare.json')
    other = saved('ab-other-compare.json')
    assert conformance['totals'] == {'same': 39564, 'wording': 48}
    assert other['totals'] == {
        'same': 54178, 'wording': 319, 'order': 192, 'verdict': 196, 'availability': 1,
    }
    assert len(other['differences']) == 708
    assert other['unlisted'] == 708
    assert conformance['unlisted'] == 0
