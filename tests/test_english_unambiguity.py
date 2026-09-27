from pathlib import Path
import signal

import pytest
from lark import Tree

from ve.english import parse_english
from ve.environment import Environment
from ve.errors import ResourceLimit, SyntaxError
from ve.limits import MAX_NODES
from ve.surface import unambiguity


ROOT = Path(__file__).resolve().parents[1]


class FakeAlarm:
    SIGALRM = signal.SIGALRM
    ITIMER_REAL = signal.ITIMER_REAL

    def __init__(self, timer=(0, 0), handler=None):
        self.timer = timer
        self.handler = handler

    def getitimer(self, _kind):
        return self.timer

    def getsignal(self, _kind):
        return self.handler

    def signal(self, _kind, handler):
        self.handler = handler

    def setitimer(self, _kind, seconds, interval=0):
        previous, self.timer = self.timer, (seconds, interval)
        return previous


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


def test_extension_readings_cannot_swap_source_spans():
    from ve.ast import Bottom, Top
    from ve.surface import registry
    from ve.surface.registry import SurfaceRecord, register
    original = registry._records.copy(), registry._by_type.copy(), registry.KEYWORDS
    swap = [True]
    def parser(parser, _scope, _depth, _nesting):
        if parser.take("this definitely holds"):
            return Bottom() if swap[0] else Top()
        parser.need("that definitely holds")
        return Top() if swap[0] else Bottom()
    def grammar(_env, _words):
        return ['%extend formula: hostile_rule',
                'hostile_rule: HOSTILE',
                'HOSTILE: "this definitely holds" | "that definitely holds"']
    def derivation(tree, _env, _words):
        return Top() if tree.children[0].value == "this definitely holds" else Bottom()
    for fn in (parser, grammar, derivation):
        fn.__module__ = "ve.english"
    try:
        register(SurfaceRecord("hostile", "", ("this definitely holds", "that definitely holds"),
                               "", "hostile_rule", parser_hook=parser,
                               grammar_hook=grammar, derivation_hook=derivation))
        env = Environment.from_json((ROOT / "examples/environment.json").read_bytes())
        with pytest.raises(SyntaxError, match="no matching grammar derivation"):
            parse_english(env, "This definitely holds. That definitely holds.")
        swap[0] = False
        assert parse_english(env, "This definitely holds. That definitely holds.").formulas == (
            Top(), Bottom())
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
            for _ in range(100):
                pass
            pytest.fail("trace did not enforce the Earley deadline")
    monkeypatch.setattr(unambiguity, "_parser", lambda _grammar: SlowParser())
    monkeypatch.setattr(unambiguity, "EARLEY_SECONDS", 1)
    ticks = iter(range(1000))
    monkeypatch.setattr(unambiguity, "_monotonic", lambda: next(ticks))
    with ThreadPoolExecutor(max_workers=1) as pool:
        with pytest.raises(ResourceLimit, match="Earley time budget"):
            pool.submit(parse_english, env, "This holds in all cases.").result(timeout=30)


def test_earley_alarm_budget_restores_signal_state(monkeypatch):
    env = Environment.from_json((ROOT / "examples/environment.json").read_bytes())
    original_handler = object()
    alarm = FakeAlarm(handler=original_handler)
    class InterruptedParser:
        def parse(self, _source):
            assert alarm.timer == (1, 0)
            alarm.handler(signal.SIGALRM, None)
            pytest.fail("Earley alarm did not enforce its budget")
    monkeypatch.setattr(unambiguity, "signal", alarm)
    monkeypatch.setattr(unambiguity, "_parser", lambda _grammar: InterruptedParser())
    monkeypatch.setattr(unambiguity, "EARLEY_SECONDS", 1)
    with pytest.raises(ResourceLimit, match="Earley time budget"):
        parse_english(env, "This holds in all cases.")
    assert alarm.timer == (0, 0)
    assert alarm.handler is original_handler


def test_host_alarm_remains_active_and_cancels_english_parse(monkeypatch):
    env = Environment.from_json((ROOT / "examples/environment.json").read_bytes())
    class HostAlarm(Exception):
        pass
    def cancel(_signum, _frame):
        raise HostAlarm()
    alarm = FakeAlarm(timer=(30, 0), handler=cancel)
    class InterruptedParser:
        def parse(self, _source):
            alarm.handler(signal.SIGALRM, None)
            pytest.fail("host alarm did not interrupt parsing")
    monkeypatch.setattr(unambiguity, "signal", alarm)
    monkeypatch.setattr(unambiguity, "_parser", lambda _grammar: InterruptedParser())
    with pytest.raises(HostAlarm):
        parse_english(env, "This holds in all cases.")
    assert alarm.handler is cancel
    assert alarm.timer == (30, 0)


def test_earley_time_budget_with_host_alarm(monkeypatch):
    env = Environment.from_json((ROOT / "examples/environment.json").read_bytes())
    class SlowParser:
        def parse(self, _source):
            for _ in range(100):
                pass
            pytest.fail("trace did not enforce the Earley deadline")
    monkeypatch.setattr(unambiguity, "_parser", lambda _grammar: SlowParser())
    monkeypatch.setattr(unambiguity, "EARLEY_SECONDS", 1)
    ticks = iter(range(1000))
    monkeypatch.setattr(unambiguity, "_monotonic", lambda: next(ticks))
    host_handler = object()
    alarm = FakeAlarm(timer=(30, 0), handler=host_handler)
    monkeypatch.setattr(unambiguity, "signal", alarm)
    with pytest.raises(ResourceLimit, match="Earley time budget"):
        parse_english(env, "This holds in all cases.")
    assert alarm.handler is host_handler
    assert alarm.timer == (30, 0)
