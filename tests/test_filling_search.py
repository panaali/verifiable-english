"""F3: one flip search (`filling_search.split`) serves the asked sentence and the norm-defaults point search; the
point-only copy (`extremes`) is gone."""
import ast
from pathlib import Path

from ve import ask, filling_search
from ve.filling_search import flip, point_statuses, points, split

ROOT = Path(__file__).resolve().parents[1]


def test_flip_changes_only_named_gaps():
    filling = {"unsaid__p": [["a"], ["b"]], "unsaid__q": []}
    gaps = [["p", ["a"], True], ["q", ["b"], False]]
    expected = {"unsaid__p": [["b"]], "unsaid__q": [["b"]]}
    assert flip(filling, gaps) == expected
    assert split(filling, gaps) == {"true": expected, "false": filling}
    assert filling == {"unsaid__p": [["a"], ["b"]], "unsaid__q": []}


def test_the_asked_sentence_split_is_the_shared_split():
    counter = {"model": {"domains": {"person": ["a"]}}, "filling": {"unsaid__p": []}}
    gaps = [["p", ["a"], False]]
    assert ask._split_piece(counter, gaps) == {"kind": "split", "model": counter["model"],
                                               **split(counter["filling"], gaps)}
    assert ask._split_piece(counter, []) is None


def test_point_points_cover_exactly_the_finite_tuples():
    unsaid = [{"name": "unsaid__p", "sorts": ["person", "place"]}]
    start, gaps = points(unsaid, {"person": ["a", "b"], "place": ["c"]})
    assert start == {"unsaid__p": []}
    assert gaps == [["p", ["a", "c"], False], ["p", ["b", "c"], False]]
    assert split(start, gaps) == {"true": {"unsaid__p": [["a", "c"], ["b", "c"]]}, "false": {"unsaid__p": []}}


def test_point_search_sends_the_shared_split_to_lean(monkeypatch):
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


def test_one_flip_generator_and_no_point_only_copy():
    """The class, not the example: no module builds a filling's all-true or all-false copy, or flips gaps, outside
    `filling_search`; both searches call `split`."""
    tree = ast.parse((ROOT / "ve/filling_search.py").read_text())
    names = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
    assert "extremes" not in names and not hasattr(filling_search, "extremes")
    calls = {}
    for path in (ROOT / "ve").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if path.name != "filling_search.py":
            assert "def flip(" not in text and "def extremes(" not in text, path
        calls[path.name] = "split(" in text
    assert calls["ask.py"]
    source = (ROOT / "ve/filling_search.py").read_text()
    assert "split(start, gaps)" in source.split("def point_statuses", 1)[1]
