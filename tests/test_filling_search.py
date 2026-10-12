"""F3: one candidate-filling generator is used by ask and point searches."""
from ve import ask
from ve.filling_search import extremes, flip, point_statuses


def test_flip_changes_only_named_gaps():
    filling = {"unsaid__p": [["a"], ["b"]], "unsaid__q": []}
    gaps = [["p", ["a"], True], ["q", ["b"], False]]
    expected = {"unsaid__p": [["b"]], "unsaid__q": [["b"]]}
    assert flip(filling, gaps) == expected
    assert ask._flipped(filling, gaps) == expected
    assert filling == {"unsaid__p": [["a"], ["b"]], "unsaid__q": []}


def test_point_extremes_cover_exactly_the_finite_tuples():
    unsaid = [{"name": "unsaid__p", "sorts": ["person", "place"]}]
    yes, no = extremes(unsaid, {"person": ["a", "b"], "place": ["c"]})
    assert yes == {"unsaid__p": [["a", "c"], ["b", "c"]]}
    assert no == {"unsaid__p": []}


def test_point_search_sends_the_extreme_fillings_to_lean(monkeypatch):
    from types import SimpleNamespace
    from ve import norm_defaults_route

    seen = []

    def run(case):
        seen.append(case)
        return {"point_status": "UNKNOWN" if case["method"] == "enumerate" else "UNDECIDED"}

    monkeypatch.setattr(norm_defaults_route, "source_case", lambda _document, _kind, **case: case)
    monkeypatch.setattr(norm_defaults_route, "run_case", run)
    document = SimpleNamespace(elaboration={"unsaid": [{"name": "unsaid__p", "sorts": ["person"]}],
                                            "reached": [{"predicate": "p", "sorts": ["person"]}]})
    assert point_statuses(document, {"domains": {"person": ["a"]}}) == {("p", ("a",)): "UNDECIDED"}
    assert seen[1]["yes"] == {"unsaid__p": [["a"]]}
    assert seen[1]["no"] == {"unsaid__p": []}
