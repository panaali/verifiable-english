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
    from ve import parse, render
    source = render(parse(env, (ROOT / "examples/fluent/examples.ve").read_text()), env, "ve_english")
    assert parse_english(env, source)


def test_parser_extension_must_supply_grammar_and_correspondence():
    from ve.ast import Bottom
    from ve.surface.registry import SurfaceRecord, register
    def parser(parser, _scope, _depth, _nesting):
        parser.take("this holds ")
        parser.take("in all cases")
        return Bottom()
    parser.__module__ = "ve.english"
    with pytest.raises(ValueError, match="grammar and derivation"):
        register(SurfaceRecord("hostile", "", ("this holds ",), "", "hostile_rule",
                               parser_hook=parser))
    env = Environment.from_json((ROOT / "examples/environment.json").read_bytes())
    assert parse_english(env, "This holds in all cases.")


def test_extension_reading_must_match_grammar_tree(monkeypatch):
    from ve.ast import Bottom, Top
    from ve.surface import registry
    from ve.surface.registry import SurfaceRecord, register
    original = registry._records.copy(), registry._by_type.copy(), registry.KEYWORDS
    def parser(parser, _scope, _depth, _nesting):
        parser.need("this definitely holds")
        return Bottom()
    def grammar(_env, _words):
        return ['%extend formula: hostile_rule', 'hostile_rule: "this definitely holds"']
    def derivation(_tree, _env, _words):
        return Top()
    for fn in (parser, grammar, derivation):
        fn.__module__ = "ve.english"
    try:
        register(SurfaceRecord("hostile", "", ("this definitely holds",), "", "hostile_rule",
                               parser_hook=parser, grammar_hook=grammar, derivation_hook=derivation))
        env = Environment.from_json((ROOT / "examples/environment.json").read_bytes())
        with pytest.raises(SyntaxError, match="no matching grammar derivation"):
            parse_english(env, "This definitely holds.")
    finally:
        records, by_type, old_keywords = original
        registry._records.clear(); registry._records.update(records)
        registry._by_type.clear(); registry._by_type.update(by_type)
        registry.KEYWORDS = old_keywords


def test_extension_grammar_must_participate():
    from ve.ast import Bottom
    from ve.surface import registry
    from ve.surface.registry import SurfaceRecord, register
    original = registry._records.copy(), registry._by_type.copy(), registry.KEYWORDS
    def parser(parser, _scope, _depth, _nesting):
        parser.need("this definitely holds")
        return Bottom()
    def grammar(_env, _words):
        return []
    def derivation(_tree, _env, _words):
        return Bottom()
    for fn in (parser, grammar, derivation):
        fn.__module__ = "ve.english"
    try:
        register(SurfaceRecord("hostile", "", ("this definitely holds",), "", "hostile_rule",
                               parser_hook=parser, grammar_hook=grammar, derivation_hook=derivation))
        env = Environment.from_json((ROOT / "examples/environment.json").read_bytes())
        with pytest.raises(SyntaxError, match="must extend formula"):
            parse_english(env, "This definitely holds.")
    finally:
        records, by_type, old_keywords = original
        registry._records.clear(); registry._records.update(records)
        registry._by_type.clear(); registry._by_type.update(by_type)
        registry.KEYWORDS = old_keywords


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


def test_earley_time_budget_rejects_in_worker_thread(monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    env = Environment.from_json((ROOT / "examples/environment.json").read_bytes())
    class SlowParser:
        def parse(self, _source):
            while True:
                pass
    monkeypatch.setattr(unambiguity, "_parser", lambda _grammar: SlowParser())
    monkeypatch.setattr(unambiguity, "EARLEY_SECONDS", 0.01)
    with ThreadPoolExecutor(max_workers=1) as pool:
        with pytest.raises(ResourceLimit, match="Earley time budget"):
            pool.submit(parse_english, env, "This holds in all cases.").result(timeout=2)
