"""A valid sugar expansion may exceed the public printer's output limit."""
from __future__ import annotations

import pytest

from tests.probe_matrix import raw_environment
from ve import Environment
from ve.errors import ResourceLimit
from ve.parser import parse, parse_with_metadata
from ve.printer import print_document


@pytest.mark.parametrize("family", [
    ("definitions@0",),
    ("closure@0", "definitions@0"),
    ("closure@0", "nary@0", "definitions@0"),
    ("definitions@0", "norms@0"),
    ("data@0", "definitions@0"),
])
def test_f1_sugar_expansion_does_not_bound_parse(family):
    env = Environment(raw_environment(family))
    source = "no item is base.\n" * 1800
    document = parse(env, source)
    assert len(document.formulas) == 1800
    assert parse_with_metadata(env, source).document == document
    # The public printer's existing limit remains a limit on output.
    with pytest.raises(ResourceLimit):
        print_document(env, document)

