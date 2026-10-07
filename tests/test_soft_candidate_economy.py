"""Batch 6 latency: a document's candidates cost Lean a fixed number of soft requests, not one per candidate
(docs/lean-first/b6/DELTA.md, Latency; recheck finding B of 2026-10-07).

`ve document render` on the large UDHR translation sent 273 `soft-elaborate` and 116 `soft-rules` requests (base:
none) and spent 1.32 to 1.49 times the base CPU: every right candidate's display document and every readings side
was a whole soft document Lean was asked to elaborate, and each asked about its own line rules. The class is removed
in two places, each tested here against the same documents built eagerly:

* a soft document built for a candidate's wording or a readings side is deferred (`SoftNormDocument(deferred=True)`):
  it holds its Python-hydrated rules, and Lean is asked for it, with its diagnostic, when a field Lean supplies is
  first read;
* the line rules of every candidate document are asked of Lean in one request per lower source before the
  documents are built (`RightsDocument.warm_rules`), so building them one by one sends no rule request.
"""
from __future__ import annotations

from collections import Counter
import json

import pytest

from tests import lean_routes
from tests.test_readings_s1_lean import env_rights, norm_object
from tests.test_readings_s2_document import s2_document
from tests.test_rights import (_candidate_set, _q_candidates, _separating_model, _with_metadata, right,
                               rights_document_file)
from tests.test_soft_request_economy import should, wide_environment
from ve import softnorms
from ve.backends import relay, soft_relay
from ve.document import check_document, render_document
from ve.errors import CheckerUnavailable, VEError
from ve.norms import NormDocument
from ve.rights import RightsDocument, RightsEnvironment
from ve.softnorms import SoftEnvironment, SoftNormDocument

ARBITRARY = ["binary", "arbitrary_arrest", ["var", 1], ["var", 0]]


@pytest.fixture
def service():
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service has not been built")


@pytest.fixture
def sent(monkeypatch):
    """Empty answer and accepted-rule memos, and the kind of every soft request Lean is asked while the test runs."""
    monkeypatch.setattr(relay, "_answers", {})
    monkeypatch.setattr(soft_relay, "_accepted", type(soft_relay._accepted)())
    kinds = []
    real = relay.decide

    def recorded(mode, cases, **options):
        if mode == "soft-norms":
            kinds.extend(case.get("kind") for case in cases)
        return real(mode, cases, **options)

    monkeypatch.setattr(relay, "decide", recorded)
    return kinds


def eager(monkeypatch):
    """The documents built as before the fix: every soft document elaborated by Lean when it is built, and no rule
    asked about ahead of its document."""
    built = SoftNormDocument.__init__

    def init(self, env, units, *, deferred=False):
        built(self, env, units)

    monkeypatch.setattr(SoftNormDocument, "__init__", init)
    monkeypatch.setattr(RightsDocument, "warm_rules", classmethod(lambda cls, env, documents: None))


def claim(mode, index):
    return {"right": {"name": f"r{index}", "holder": "person", "guard": ["top"], "lines": [
        {"kind": "claim", "norm": norm_object(f"no-arrest-{index}", "arrest_permitted", False, mode,
                                              guard=ARBITRARY)}]}}


def twin_sets(tmp_path, sets):
    """`sets` open sets, each a strict and a default claim of its own right, under the rights chain."""
    items = [("set", f"rs{k}", f"u{k}", [("strict", claim("strict", k), "right", None),
                                         ("default", claim("default", k), "right", None)]) for k in range(sets)]
    return s2_document(tmp_path, items, raw=env_rights(), name=f"twins-{sets}.ve.md")


def requests(sent, run):
    """`run()` and the soft requests it asks Lean, from empty memos."""
    relay._answers.clear()
    soft_relay._accepted.clear()
    sent.clear()
    out = run()
    return out, Counter(sent)


# -- the document paths: Lean requests do not grow with the candidates, and the answers are the eager ones


@pytest.mark.parametrize("command", ["render", "check"])
def test_candidates_cost_no_soft_request_each(service, sent, tmp_path, command):
    """Seven and nine sets of two right candidates (past the 64 choices S2 checks one by one) ask Lean the same soft
    requests: neither a candidate's
    display document nor a readings side is elaborated by Lean for its rules alone, and their line rules are asked
    about together."""
    run = render_document if command == "render" else check_document
    counts = []
    for sets in (7, 9):
        path = twin_sets(tmp_path, sets)
        _, count = requests(sent, lambda: run(path))
        counts.append(count)
    assert counts[0] == counts[1], counts
    # Rights elaboration now validates each complete source, including its line
    # rules. There is no separate soft rule request to batch.
    assert counts[1]["soft-rules"] == 0, counts


@pytest.mark.parametrize("command", ["render", "check"])
def test_deferred_documents_answer_as_eager_ones(service, tmp_path, monkeypatch, command):
    """The rendered text and the report are those of the documents built eagerly (before the fix)."""
    path = twin_sets(tmp_path, 3)
    run = render_document if command == "render" else check_document
    deferred = run(path)
    with monkeypatch.context() as patch:
        eager(patch)
        assert run(path) == deferred


def test_eager_documents_cost_a_request_per_candidate(service, sent, tmp_path, monkeypatch):
    """The economy test above can fail: with the documents built eagerly, nine sets ask more than seven."""
    eager(monkeypatch)
    counts = []
    for sets in (7, 9):
        path = twin_sets(tmp_path, sets)
        _, count = requests(sent, lambda: render_document(path))
        counts.append(count)
    assert counts[1]["soft-elaborate"] > counts[0]["soft-elaborate"]
    assert counts[1]["soft-rules"] == counts[0]["soft-rules"] == 0


def q_document(tmp_path, sets):
    """A rights document without readings@1 with `sets` units, each read by a set of two q-guarded right
    candidates whose rules are named after their set: admission checks every candidate alone
    (`validate_reading_sets`)."""
    raw, contents = _q_candidates()
    env = RightsEnvironment(raw)
    units = {f"u{k}" for k in range(sets)}
    path = rights_document_file(tmp_path, [right() for _ in range(sets)], env=raw)
    reading_sets = []
    for k in range(sets):
        renamed = json.loads(json.dumps(contents))
        for content in renamed:
            content["right"]["lines"][0]["norm"]["name"] += f"-{k}"
        model = _separating_model(env, *renamed, units)
        assert model is not None
        reading_sets.append(_candidate_set(env, f"rs{k}", f"u{k}", renamed, model))

    def change(metadata):
        for item in metadata["units"]:
            del item["content"]
        metadata["reading_sets"] = reading_sets

    return _with_metadata(path, change)


def test_candidates_checked_alone_ask_about_their_line_rules_together(service, sent, tmp_path, monkeypatch):
    """Admission still checks each candidate's whole document (one `soft-elaborate` each); its line rules are asked
    about in one request, however many candidates there are. The rendered text is the eager one."""
    counts = []
    for sets in (1, 3):
        (tmp_path / str(sets)).mkdir()
        path = q_document(tmp_path / str(sets), sets)
        rendered, count = requests(sent, lambda: render_document(path))
        counts.append(count)
    assert counts[0]["soft-rules"] == counts[1]["soft-rules"], counts
    assert counts[1]["soft-elaborate"] > counts[0]["soft-elaborate"], counts
    with monkeypatch.context() as patch:
        eager(patch)
        assert render_document(path) == rendered


# -- a deferred soft document


def public(document):
    """Every field a document holds: an environment by its identity-bearing dictionary, a norm document by its
    environment and rules, anything else by its value's text."""
    def value(item):
        if isinstance(item, NormDocument):
            return item.env.to_dict(), repr(item.rules)
        return item.to_dict() if hasattr(item, "to_dict") and not isinstance(item, type) else repr(item)
    return {name: value(item) for name, item in vars(document).items() if not name.startswith("_")}


def test_a_deferred_document_asks_lean_once_when_a_field_lean_supplies_is_read(service, monkeypatch):
    raw, names = wide_environment()
    env = SoftEnvironment(raw)
    units = [should("a", f"{names[0]}_required"), should("b", f"{names[0]}_permitted", False)]
    eager_document = SoftNormDocument(env, units)
    asked = []
    real = softnorms.check_soft_source

    def recorded(environment, norms=None, **options):
        if norms:
            asked.append(norms)
        return real(environment, norms, **options)

    monkeypatch.setattr(softnorms, "check_soft_source", recorded)
    document = SoftNormDocument(env, units, deferred=True)
    assert [rule.core.name for rule in document.rules] == ["a", "b"] and document.env is env
    assert document.core is not None and asked == []
    # Every field eager construction sets (none of them listed by hand) is Lean's, read through one request.
    lean_fields = sorted(set(public(eager_document)) - set(public(document)))
    assert lean_fields, "the deferred document already holds every field"
    for name in lean_fields:
        getattr(document, name)
    assert asked == [units]
    assert public(document) == public(eager_document)


def test_a_deferred_document_lean_rejects_raises_lean_diagnostic_on_every_read(service):
    """A default rule over a strict one (`SoftOverHard`): built deferred, its rules are held; the first read of a
    field Lean supplies raises the diagnostic and code eager construction raises, and so does every later read."""
    raw, names = wide_environment()
    env = SoftEnvironment(raw)
    strict = {"norm": {"name": "s", "predicate": f"{names[0]}_required", "sign": True, "guard": ["top"],
                       "unless": [], "over": []}}
    over = should("d", f"{names[0]}_required", False)
    over["norm"]["over"] = ["s"]
    with pytest.raises(VEError) as eager_error:
        SoftNormDocument(env, [strict, over])
    document = SoftNormDocument(env, [strict, over], deferred=True)
    assert [rule.core.name for rule in document.rules] == ["s", "d"]
    for _ in range(2):
        with pytest.raises(VEError) as raised:
            document.decisions
        assert (type(raised.value), str(raised.value), getattr(raised.value, "code", None)) == (
            type(eager_error.value), str(eager_error.value), getattr(eager_error.value, "code", None))


def test_a_deferred_document_python_cannot_hold_gives_lean_diagnostic_first(service):
    """A rule whose guard is no formula: the deferred document asks Lean at once, so the error is the eager one."""
    raw, names = wide_environment()
    env = SoftEnvironment(raw)
    bad = should("a", f"{names[0]}_required")
    bad["norm"]["guard"] = ["no-such-connective"]
    with pytest.raises(VEError) as eager_error:
        SoftNormDocument(env, [bad])
    with pytest.raises(VEError) as raised:
        SoftNormDocument(env, [bad], deferred=True)
    assert (type(raised.value), str(raised.value)) == (type(eager_error.value), str(eager_error.value))


def test_extended_attributes_reach_the_extended_environment_either_way(service):
    """`extend` sets its attributes on `extended_env` at once on an elaborated document, and when Lean's answer
    builds it on a deferred one: a rights document's limitation premises and wordings (`RightsDocument`)."""
    raw = env_rights()
    units = [{"source_units": ["u0"]}, claim("strict", 0)]
    eager_document = RightsDocument(RightsEnvironment(raw), units).soft_document
    deferred = RightsDocument(RightsEnvironment(raw), units, deferred=True).soft_document
    assert "extended_env" not in vars(deferred)
    for name in ("rights_premises", "rights_wordings"):
        assert getattr(deferred.extended_env, name) == getattr(eager_document.extended_env, name)


def test_a_missing_attribute_is_missing_after_elaboration(service):
    raw, names = wide_environment()
    document = SoftNormDocument(SoftEnvironment(raw), [should("a", f"{names[0]}_required")], deferred=True)
    with pytest.raises(AttributeError):
        document.no_such_field
    assert document._deferred is False
    with pytest.raises(AttributeError):
        document.__deepcopy_hook__


# -- asking about line rules ahead of their documents


MALFORMED = {"null": None, "number": 7, "no units": [], "number unit": [7], "number right": [{"right": 7}],
             "right without fields": [{"source_units": ["u0"]}, {"right": {"name": "r"}}]}


@pytest.mark.parametrize("units", MALFORMED.values(), ids=MALFORMED.keys())
def test_warming_raises_no_diagnostic_and_asks_about_no_rule(service, sent, units):
    env = RightsEnvironment(env_rights())
    RightsDocument.warm_rules(env, [units])
    RightsDocument.warm_rules(env_rights(), [[{"source_units": ["u0"]}, claim("strict", 0)]])
    assert "soft-rules" not in sent


def test_rights_route_failure_is_not_absorbed_by_candidate_warming(service, monkeypatch):
    """Candidate warming is a no-op after the rights route became the line-rule authority.
    A failure of that route is still raised when the document is built."""
    env = RightsEnvironment(env_rights())
    documents = [[{"source_units": ["u0"]}, claim("strict", 0)]]
    RightsDocument.warm_rules(env, documents)
    from ve import rights_route

    def down(*args, **kwargs):
        raise CheckerUnavailable("CheckerUnavailable: the Lean service is not running")
    monkeypatch.setattr(rights_route, "run_rights_case", down)
    with pytest.raises(CheckerUnavailable, match="not running"):
        RightsDocument(env, documents[0])


def test_warmed_documents_send_no_rule_request_and_keep_their_diagnostics(service, sent):
    """The rights route checks each source; no separate soft rule request is needed.
    A rejected source has the same diagnostic after candidate warming."""
    env = RightsEnvironment(env_rights())
    documents = [[{"source_units": ["u0"]}, claim(mode, k)] for k, mode in enumerate(("strict", "default", "strict"))]
    bad = claim("strict", 9)
    bad["right"]["lines"][0]["norm"]["guard"] = ["binary", "no_such_relation", ["var", 1], ["var", 0]]
    with pytest.raises(VEError) as cold:
        RightsDocument(env, [{"source_units": ["u0"]}, bad])
    sent.clear()
    RightsDocument.warm_rules(env, [*documents, [{"source_units": ["u0"]}, bad]])
    assert sent.count("soft-rules") == 0
    for units in documents:
        RightsDocument(env, units, deferred=True)
    assert sent.count("soft-rules") == 0 and "soft-elaborate" not in sent
    with pytest.raises(VEError) as warmed:
        RightsDocument(env, [{"source_units": ["u0"]}, bad])
    assert (type(warmed.value), str(warmed.value), getattr(warmed.value, "code", None)) == (
        type(cold.value), str(cold.value), getattr(cold.value, "code", None))
