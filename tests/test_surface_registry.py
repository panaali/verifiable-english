import re

import pytest

from ve.surface.registry import KEYWORDS, SurfaceRecord, dispatch, keywords, register


@pytest.fixture(autouse=True)
def isolated_registry():
    from ve.surface import registry
    records, by_type, old_keywords = registry._records.copy(), registry._by_type.copy(), registry.KEYWORDS
    yield
    registry._records.clear(); registry._records.update(records)
    registry._by_type.clear(); registry._by_type.update(by_type)
    registry.KEYWORDS = old_keywords


def test_keywords_cover_statement_initial_literals():
    source = open("ve/english.py").read()
    region = source[source.index("    def formula(self, scope="):source.index("    def document(self):")]
    expected = {"it is not the case that ", "all of the following hold:",
                "both of the following hold:", "at least one of the following holds:",
                "if the following holds:", "both ", "either ", "if ",
                "for every ", "every ", "there is ", "starting from "}
    assert expected <= {keyword for keyword, _ in KEYWORDS}
    # Statement-layer profiles may register additional initial keywords; the
    # historical formula grammar's set and ordering remain fixed within them.
    historical = tuple(keyword for keyword, _ in KEYWORDS if keyword in expected)
    assert historical == tuple(sorted(expected, key=lambda s: (-len(s), s)))
    for keyword in expected:
        assert keyword in region
        assert dispatch(keyword + "x")[0] == keyword


def test_duplicate_keyword_refused():
    with pytest.raises(ValueError, match="Duplicate English keyword"):
        register(SurfaceRecord("test-duplicate", "", ("both ",), "", ""))


def test_overlapping_registration_uses_longest_match():
    register(SurfaceRecord("test-both-x", "", ("both x",), "", ""))
    ordered = [keyword for keyword, _ in keywords()]
    assert ordered.index("both of the following hold:") < ordered.index("both x")
    assert ordered.index("both x") < ordered.index("both ")
    assert dispatch("both x test")[0] == "both x"


def test_profile_gates_new_keyword():
    from conformance.p0 import environment
    from ve.environment import Environment
    register(SurfaceRecord("test-norm-keyword", "", ("under a rule ",), "", "",
                           profiles=("norms@0",)))
    base = Environment(environment())
    assert dispatch("under a rule x", base) is None
    raw = environment()
    raw["profiles"] = ["norms@0", "relational-fol@0"]
    assert dispatch("under a rule x", Environment(raw))[0] == "under a rule "
