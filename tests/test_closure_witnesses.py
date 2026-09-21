"""Every selected E0 item has two checked, provenance-bound closure witnesses."""
from experiments.E0.closure_witnesses.validate import validate


def test_all_e0_closure_witnesses():
    report = validate()
    assert report['status'] == 'PASS'
    assert (report['cedar_items'], report['alloy_items'], report['python_lean_agree']) == (10, 5, 30)
