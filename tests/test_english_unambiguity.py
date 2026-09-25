from pathlib import Path

import pytest
from lark import Tree

from ve.english import parse_english
from ve.environment import Environment
from ve.errors import ResourceLimit, SyntaxError
from ve.limits import MAX_NODES
from ve.surface import unambiguity


ROOT = Path(__file__).resolve().parents[1]


def test_existing_english_fixture_has_one_derivation():
    env = Environment.from_json((ROOT / "examples/fluent/environment.json").read_bytes())
    source = (ROOT / "examples/fluent/requirements.ve.english").read_text() if (
        ROOT / "examples/fluent/requirements.ve.english").exists() else None
    if source is None:
        from ve.ast import Document, Top
        from ve.printer import render
        source = render(Document((Top(),)), env, "ve_english")
    assert parse_english(env, source)


def test_two_derivations_reject_before_ast_admission(monkeypatch):
    env = Environment.from_json((ROOT / "examples/environment.json").read_bytes())
    monkeypatch.setattr("ve.english.english_lark_grammar",
        lambda _env, **_options: 'start: a | b\na: "this holds in all cases."\nb: "this holds in all cases."')
    with pytest.raises(SyntaxError, match="two derivations") as exc:
        parse_english(env, "This holds in all cases.")
    assert "---" in str(exc.value)


def test_derivation_node_budget_rejects(monkeypatch):
    env = Environment.from_json((ROOT / "examples/environment.json").read_bytes())
    class FakeParser:
        def parse(self, _source):
            return Tree("start", [Tree("x", []) for _ in range(MAX_NODES)])
    monkeypatch.setattr(unambiguity, "_parser", lambda _grammar: FakeParser())
    with pytest.raises(ResourceLimit, match="MAX_NODES"):
        parse_english(env, "This holds in all cases.")
