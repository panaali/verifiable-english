"""The three independent rights/soft regeneration paths agree on the fixtures and on 1,000
generated documents (docs/spec/rights.md 10)."""

import pytest

from conformance.rights_differential import run as differential
from conformance.rights_three_way import run


def test_rights_three_way_fixtures():
    result = run()
    names = [row["fixture"] for row in result["fixtures"]]
    assert result["passed"] == 18
    assert {"epsilon", "kappa", "mu", "nu", "omicron", "sigma", "tau", "psi", "charged", "theta"} <= set(names)
    theta = next(row for row in result["fixtures"] if row["fixture"] == "theta")
    assert theta["wrapped_documents"] >= 30


SHAPES = {"claim", "liberty", "immunity", "powerLiberty", "powerRecognition", "fan-out", "right_lines",
          "limitation", "bar:rule", "bar:query"}


def test_rights_differential_on_one_hundred_generated_documents():
    """The first 100 accepted documents of the nightly 1,000 (the same seeds, in order), which
    already reach every shape."""
    result = differential(100)
    assert result["accepted_by_both"] == result["loaded_as_documents"] == 100
    assert result["rejected_by_both"] > 10
    assert result["rejections_with_the_same_text"] == result["rejected_by_both"]
    assert SHAPES <= set(result["shapes"])


@pytest.mark.nightly
def test_rights_differential_on_one_thousand_generated_documents():
    """docs/spec/rights.md 10 (about 5 minutes): runs with `-m nightly` and in tools/gate.py."""
    result = differential(1000)
    assert result["accepted_by_both"] == 1000
    assert result["loaded_as_documents"] == 1000
    assert result["rejected_by_both"] > 100
    assert result["rejections_with_the_same_text"] == result["rejected_by_both"]
    assert SHAPES <= set(result["shapes"])
