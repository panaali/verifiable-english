from pathlib import Path
import signal

import pytest
from subprocesses import HANG_TIMEOUT
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
        self.host_timer_active = timer[0] > 0

    def getitimer(self, _kind):
        return self.timer

    def getsignal(self, _kind):
        return self.handler

    def signal(self, _kind, handler):
        self.handler = handler

    def setitimer(self, _kind, seconds, interval=0):
        if self.host_timer_active:
            pytest.fail("English parsing changed the active host alarm schedule")
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
    elapsed = [0.0]
    iterations = [0]
    class SlowParser:
        def parse(self, _source):
            for _ in range(100):
                iterations[0] += 1
                elapsed[0] += 0.25
            return Tree("start", [])
    monkeypatch.setattr(unambiguity, "_parser", lambda _grammar: SlowParser())
    monkeypatch.setattr(unambiguity, "EARLEY_SECONDS", 1)
    monkeypatch.setattr(unambiguity, "_monotonic", lambda: elapsed[0])
    with ThreadPoolExecutor(max_workers=1) as pool:
        with pytest.raises(ResourceLimit, match="Earley time budget"):
            pool.submit(parse_english, env, "This holds in all cases.").result(timeout=HANG_TIMEOUT)
    assert 0 < iterations[0] < 100


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
    elapsed = [0.0]
    iterations = [0]
    class SlowParser:
        def parse(self, _source):
            for _ in range(100):
                iterations[0] += 1
                elapsed[0] += 0.25
            return Tree("start", [])
    monkeypatch.setattr(unambiguity, "_parser", lambda _grammar: SlowParser())
    monkeypatch.setattr(unambiguity, "EARLEY_SECONDS", 1)
    monkeypatch.setattr(unambiguity, "_monotonic", lambda: elapsed[0])
    host_handler = object()
    alarm = FakeAlarm(timer=(30, 0), handler=host_handler)
    monkeypatch.setattr(unambiguity, "signal", alarm)
    with pytest.raises(ResourceLimit, match="Earley time budget"):
        parse_english(env, "This holds in all cases.")
    assert 0 < iterations[0] < 100
    assert alarm.handler is host_handler
    assert alarm.timer == (30, 0)


def _soft_env():
    """Use the admitted profile and its declared parties and ranks."""
    from tests.test_norms import environment, obligation, permission
    from ve.softnorms import SoftEnvironment
    raw = environment({"required": obligation(), "permitted": permission()}).to_dict()
    raw["profiles"] = sorted((*raw["profiles"], "soft-norms@0"))
    raw["vocabulary"]["soft"] = {"parties": ["operator", "user"],
                                  "ranks": ["helpfulness"], "outranks": [], "ties": [],
                                  "outranking": {"mode": "strict"}}
    return SoftEnvironment(raw)


def test_soft_modal_wordings_are_one_reading_and_profile_gated():
    from tests.test_norms import environment, obligation, permission
    from ve.norm_english import parse_english, render_english
    from ve.surface.softnorms import SoftNorm, modal_reading
    from ve.norms import NormDocument
    from ve.ast import Top

    env = _soft_env()
    cases = (("required", True, "should"),
             ("required", False, "generally need not"),
             ("permitted", True, "generally may"),
             ("permitted", False, "should not"))
    for predicate, sign, wording in cases:
        doc = NormDocument(env, [SoftNorm("soft", predicate, sign, Top(), mode="default",
                                          decided_by="assistant")])
        source, manifest = render_english(doc)
        assert f" {wording} " in source
        assert [r.to_dict() for r in parse_english(env, source, manifest).rules] == [r.to_dict() for r in doc.rules]
        assert modal_reading(wording)[0] == "default"
    w1 = environment({"required": obligation(), "permitted": permission()})
    for sentence in ("Every act should be done.", "Every act generally may be done."):
        with pytest.raises(SyntaxError, match="single declared reading"):
            parse_english(w1, "Rule 1. " + sentence)


def test_soft_synonyms_canonicalize_and_frequency_wordings_remain_open():
    from ve.norm_english import parse_english, render_english
    from ve.surface.softnorms import frequency_readings, normalize_modal

    env = _soft_env()
    for input_word, canonical in (("generally must", "should"),
                                  ("generally must not", "should not")):
        source = "Rule 1. Every act " + input_word + " be done."
        doc = parse_english(env, source)
        assert " " + canonical + " " in render_english(doc)[0]
        assert normalize_modal(input_word) == canonical
    for word in ("normally", "typically", "usually", "as a rule"):
        readings = frequency_readings(word, "doing the act")
        assert len(readings) == 2 and "frequency claim" in readings[1]
        with pytest.raises(SyntaxError, match="Frequency wording has two readings"):
            parse_english(env, "Rule 1. Every act " + word + " may be done.")
    for phrase in ("should generally", "should generally not"):
        with pytest.raises(SyntaxError):
            parse_english(env, "Rule 1. Every act " + phrase + " be done.")


def test_soft_rule_options_exception_conditions_and_manifest():
    from ve.ast import Top
    from ve.norm_english import parse_english, render_english
    from ve.norms import NormDocument
    from ve.surface.softnorms import SoftNorm

    env = _soft_env()
    rules = [SoftNorm("hard", "required", True, Top(), mode="default", decided_by="assistant", alterable=("user",)),
             SoftNorm("default", "required", False, Top(), over=("hard",),
                      mode="default", rank="helpfulness", alterable=("operator", "user"),
                      decided_by="assistant", sufficient=(Top(),), necessary=(Top(),),
                      factors=("safety", "the user's wishes"))]
    doc = NormDocument(env, rules)
    source, manifest = render_english(doc, handles={"hard": "h", "default": "d"})
    assert "Rule 1 (user may turn off)." in source
    assert "Rule 2 (exception to rule 1; operator and user may turn off)." in source
    assert "Rule 2 serves helpfulness." in source
    assert "is excepted when this holds in all cases" in source
    assert "is excepted only when this holds in all cases" in source
    assert [r.to_dict() for r in parse_english(env, source, manifest).rules] == [r.to_dict() for r in rules]
    assert parse_english(env, source).rules[1].core.over == ("rule-1",)
    stale = dict(manifest, text_digest="0" * 64)
    with pytest.raises(Exception, match="IdentityMetadataMismatch"):
        parse_english(env, source, stale)


def test_soft_declarations_and_registry_have_single_canonical_readings():
    from ve.surface import softnorms
    from ve.surface.registry import by_tag, dispatch

    cases = (("Safety outranks ethics.", "outranks", ("safety", "ethics")),
             ("Safety and ethics are not ranked.", "tie", ("safety", "ethics")),
             ("Outranking in this document is strict.", "outranking", {"mode": "strict"}),
             ("Outranking in this document is holistic; assistant decides when a lower-ranked rule "
              "outweighs a higher-ranked one in a situation.", "outranking",
              {"mode": "holistic", "decided_by": "assistant"}),
             ("Exceptions to rules in this document are decided by assistant, unless a rule "
              "says otherwise.", "exception_decider", "assistant"),
             ('"An operator request records an instruction of operator."',
              "instruction_of", ("An operator request", "operator")))
    for source, kind, value in cases:
        assert softnorms.parse_declaration(source) == (kind, value)
        assert softnorms.render_declaration(kind, value) == source
    assert dispatch("Outranking in this document is strict.", _soft_env())[1].wire_tag == "soft-document-outranking"
    from tests.test_norms import environment, permission
    assert dispatch("Outranking in this document is strict.",
                    environment({"permitted": permission()})) is None
    assert by_tag("soft-should").profiles == ("soft-norms@0",)


def test_rights_incident_prefix_reuses_one_reading_soft_grammar():
    from tests.test_rights import claim, rights_env
    from ve.rights import RightsEnvironment
    from ve.surface.rights import parse_line, render_line

    env = RightsEnvironment(rights_env())
    source = render_line(env, "life", "claim", claim()["norm"])
    assert parse_line(env, source, name="protect")["norm"] == claim()["norm"]
    with pytest.raises(Exception, match="expected Claim, Liberty or Immunity"):
        parse_line(env, source.replace("Claim of right", "Rule", 1), name="protect")
    with pytest.raises(Exception, match="Norm consequence has no single declared reading"):
        parse_line(env, source.replace("must protect", "should generally protect"), name="protect")
