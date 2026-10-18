"""Historical request provenance stays separate from current checker identity."""
from copy import deepcopy

import pytest

from experiments import p1, p1_history
from tests import p1_findings
from ve.argument import _checker_build
from ve_experiments.paid import PreflightError


def test_historical_finding_is_reused_only_after_exact_semantic_replay():
    historical = next(iter(p1_history.retained_findings().values()))
    current = {**deepcopy(historical), 'checker_build': _checker_build()}
    assert current['checker_build'] != historical['checker_build']
    assert p1_history.replayed_historical_finding(current) == historical
    for field in ('query_sha256', 'artifact_sha256', 'checker_version', 'graph_id'):
        with pytest.raises(PreflightError, match='current replay differs'):
            p1_history.replayed_historical_finding({**current, field: 'changed'})
    changed = deepcopy(current)
    changed['obligations'][0]['finding'] = ['changed']
    with pytest.raises(PreflightError, match='current replay differs'):
        p1_history.replayed_historical_finding(changed)
    assert p1_history.replayed_historical_finding({'item_id': 'new', 'checker_build': 'new'}) == {
        'item_id': 'new', 'checker_build': 'new'}


def test_p1_historical_output_does_not_change_current_checker_fingerprint():
    before = _checker_build()
    # The findings are computed after `before` is read, several at a time (tests/p1_findings.py).
    p1_findings.warm('dev')
    for item in p1.materials('dev'):
        assert p1.finding(item) == p1_history.retained_findings()[item['id']]
    assert _checker_build() == before
