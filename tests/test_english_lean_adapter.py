"""The Lean side of `english.admission` (docs/spec/english-lean-s2.md 2.10, 2.11, 4.2, 4.5; S2 plan S2.5).

The Lean answers here come from a fake transport: the honest one answers what Python reads (as
`english.read` does on agreement), and the others are that answer with one field changed; the real reader is
exercised in `tests/test_english_lean_route.py`. The tests show that nothing changes under the default
authority, that every call is recorded under shadow with the fields of 4.5 and the class map of 4.2, that a
malformed answer or a producer fault is `CheckerUnavailable`, and that the lexicon export lives under `ve/`.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from ve import Environment
from ve import english as EN
from ve import english_grammar as EG
from ve.backends import english_lean as L
from ve.backends import lean as lean_backend
from ve.errors import (AmbiguousDerivation, CheckerUnavailable, ResourceLimit, SyntaxError, UnsupportedProfile,
                       VEError)

ENV = Environment({
    "language": "ve.core@0", "profile": "relational-fol@0", "spec_revision": "ve-v0-draft-2026-09-20",
    "vocabulary": {
        "sorts": {"item": {"description": "Item", "verbalisation": {"singular": "service", "plural": "services"}},
                  "agent": {"description": "Agent", "verbalisation": {"singular": "person", "plural": "people"}}},
        "predicates": {
            "active": {"arguments": ["item"], "description": "Deployed", "verbalisation": "{0} is deployed"},
            "reviewed": {"arguments": ["item"], "description": "Reviewed", "verbalisation": "{0} is reviewed"},
            "owns": {"arguments": ["agent", "item"], "description": "Owner", "verbalisation": "{0} owns {1}"}},
        "constants": {"legacy": {"sort": "item", "description": "Legacy"},
                      "alice": {"sort": "agent", "description": "Alice"}}}})
ACCEPTED = ("Every service is reviewed.", "Legacy is deployed. It is reviewed.",
            "Legacy is deployed. Therefore legacy is deployed.", "Alice owns legacy.")
REJECTED = ("Every sevice is reviewed.", "Every service is reviewed")


def honest(env=ENV, **options):
    """A fake `english.read`: Python's own reading of the case, in the response shape of base 4.3."""
    calls = []

    def transport(case):
        calls.append(case)
        source = case["source"]
        words = EN.EnglishVocabulary(env, **options)
        response = {"identities": L.identities(env, source, words, case["lexicon"])}
        try:
            reading = EN._python_reading(env, source, words, options)
        except AmbiguousDerivation as exc:
            return {**response, "status": "many", "code": "Ambiguous", "text": str(exc), "sentence": 0,
                    "witnesses": [[["a", 0, 1]], [["b", 0, 1]]]}
        except UnsupportedProfile as exc:
            return {**response, "status": "rejected", "code": "IllTyped", "text": str(exc)}
        except SyntaxError as exc:
            return {**response, "status": "none", "code": "NoDerivation", "text": str(exc), "sentence": 0}
        found = reading.comparison()
        return {**response, "status": "one", "ast": found["formulas"], "conclusions": found["conclusions"],
                "derivation": [[["sentence.plain", 0, 2], ["formula.atom", 0, 2]]] * len(found["formulas"])}

    transport.calls = calls
    return transport


@pytest.fixture
def shadow(monkeypatch, tmp_path):
    log = tmp_path / "ve-shadow.jsonl"
    monkeypatch.setenv("VE_AUTHORITY_OVERRIDES", "english.admission=shadow")
    monkeypatch.setenv("VE_SHADOW_LOG", str(log))

    def records():
        return [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []
    return records


def use(monkeypatch, transport):
    monkeypatch.setattr(L, "TRANSPORT", transport)


def outcome(source, env=ENV):
    try:
        result = EN.parse_english_with_metadata(env, source)
        return ("ok", [EN.ast._to_data(f) for f in result.document.formulas], result.canonical_text,
                result.english_text, result.conclusions)
    except VEError as exc:
        return (type(exc).__name__, str(exc))


# ------------------------------------------------------------------ the default authority

def test_the_default_authority_never_calls_lean(monkeypatch, tmp_path):
    monkeypatch.delenv("VE_AUTHORITY_OVERRIDES", raising=False)
    monkeypatch.delenv("VE_AUTHORITY", raising=False)
    monkeypatch.setenv("VE_SHADOW_LOG", str(tmp_path / "log.jsonl"))
    fake = honest()
    use(monkeypatch, fake)
    for source in ACCEPTED + REJECTED:
        outcome(source)
    assert fake.calls == []
    assert not (tmp_path / "log.jsonl").exists()


@pytest.mark.parametrize("setting", ["VE_AUTHORITY=lean", "VE_AUTHORITY=shadow", "pinned lean",
                                     "VE_AUTHORITY_OVERRIDES=parse=lean"])
def test_only_a_named_override_dispatches_the_english_reading(monkeypatch, tmp_path, setting):
    """The reader is not built, so the global authority and a composing adapter's pin leave English on Python."""
    from ve.backends import dispatch
    monkeypatch.delenv("VE_AUTHORITY_OVERRIDES", raising=False)
    monkeypatch.setenv("VE_SHADOW_LOG", str(tmp_path / "log.jsonl"))
    expected = {source: outcome(source) for source in ACCEPTED + REJECTED}
    fake = honest()
    use(monkeypatch, fake)
    if setting.startswith("VE_"):
        monkeypatch.setenv(*setting.split("=", 1))
        found = {source: outcome(source) for source in ACCEPTED + REJECTED}
    else:
        with dispatch.pinned("lean"):
            found = {source: outcome(source) for source in ACCEPTED + REJECTED}
    assert found == expected
    assert fake.calls == [] and not (tmp_path / "log.jsonl").exists()
    assert not dispatch.overridden("english.admission")
    monkeypatch.setenv("VE_AUTHORITY_OVERRIDES", "parse=lean,english.admission=python")
    assert dispatch.overridden("english.admission") and dispatch.authority_for("english.admission") == "python"


# ------------------------------------------------------------------ shadow

def test_shadow_records_every_call_and_returns_pythons_result(monkeypatch, shadow):
    """Every dispatched call (the admission re-reads its rendering, so a text can make two) is one record."""
    monkeypatch.setenv("VE_AUTHORITY_OVERRIDES", "english.admission=python")
    expected = {source: outcome(source) for source in ACCEPTED + REJECTED}
    monkeypatch.setenv("VE_AUTHORITY_OVERRIDES", "english.admission=shadow")
    fake = honest()
    use(monkeypatch, fake)
    assert {source: outcome(source) for source in ACCEPTED + REJECTED} == expected
    records = shadow()
    assert len(records) == len(fake.calls) >= len(ACCEPTED) + len(REJECTED)
    digests = {hashlib.sha256(source.encode()).hexdigest() for source in ACCEPTED + REJECTED}
    assert digests <= {record["identities"]["source_sha256"] for record in records}
    for record in records:
        assert record["op"] == "english.admission"
        assert record["classes"] == [], record
        assert set(record) >= {"identities", "python", "lean", "classes", "input_digest", "python_ms", "backend_ms"}
        assert set(record["identities"]) == {"source_sha256", "environment_id", "lexicon_id", "grammar_id",
                                             "actions_version"}  # no overlay: no overlay_digest (i6)
    assert {(r["python"]["class"], r["lean"]["status"]) for r in records} == {("accepted", "one"),
                                                                             ("SyntaxError", "none")}


def test_shadow_without_the_reader_records_unavailability_and_changes_nothing(monkeypatch, shadow, tmp_path):
    monkeypatch.setattr(L, "TRANSPORT", None)
    monkeypatch.setenv("VE_ENGLISH_ROUTE", str(tmp_path / "missing"))
    EN._parse_english_document(ENV, ACCEPTED[0])
    [record] = shadow()
    assert record["lean"]["status"] == "unavailable" and "not built" in record["lean"]["message"]
    assert record["classes"] == ["diagnostic-code", "schema", "verdict"]


def test_a_formula_difference_is_recorded(monkeypatch, shadow):
    fake = honest()

    def lying(case):
        response = fake(case)
        response["ast"] = [["top"]]
        return response
    use(monkeypatch, lying)
    EN._parse_english_document(ENV, ACCEPTED[0])
    [record] = shadow()
    assert record["classes"], record
    assert record["lean"]["formulas"] == [["top"]] != record["python"]["formulas"]


@pytest.mark.parametrize("code, python_error, agrees", [
    ("IllTyped", UnsupportedProfile, True), ("RelativeForm", SyntaxError, True),
    ("RelativeForm", UnsupportedProfile, True), ("CoordinationForm", SyntaxError, True),
    ("CoordinationForm", UnsupportedProfile, False), ("NestingLimit", ResourceLimit, True),
    ("IllTyped", SyntaxError, False),
])
def test_the_class_map_of_spec_4_2(monkeypatch, shadow, code, python_error, agrees):
    def python(env, source, words, options):
        raise python_error("planted")
    monkeypatch.setattr(EN, "_python_reading", python)

    def rejecting(case):
        found = L.identities(ENV, case["source"], EN.EnglishVocabulary(ENV), case["lexicon"])
        return {"identities": found, "status": "rejected", "code": code, "text": "Lean's text."}
    use(monkeypatch, rejecting)
    with pytest.raises(python_error, match="planted"):
        EN.parse_english(ENV, ACCEPTED[0])
    [record] = shadow()
    assert record["lean"]["code"] == code and record["python"]["class"] == python_error.__name__
    assert (record["classes"] == []) is agrees, record


def test_conclusion_rejected_is_recorded_and_not_a_difference(monkeypatch, shadow):
    source = "Legacy is deployed. Therefore legacy is reviewed."
    calls = []
    real = EN._check_conclusions

    def counted(*args):
        calls.append(args)
        return real(*args)
    monkeypatch.setattr(EN, "_check_conclusions", counted)
    use(monkeypatch, honest())
    with pytest.raises(SyntaxError, match="marked conclusion"):
        EN.parse_english(ENV, source)
    [record] = shadow()
    assert record["conclusion_rejected"] is True and record["classes"] == []
    assert len(calls) == 1  # the record and the admission share one conclusion check


def test_the_wall_clock_limit_is_excluded_and_listed(monkeypatch, shadow):
    def python(env, source, words, options):
        raise ResourceLimit(L.WALL_CLOCK)
    monkeypatch.setattr(EN, "_python_reading", python)
    use(monkeypatch, honest())
    with pytest.raises(ResourceLimit):
        EN.parse_english(ENV, ACCEPTED[0])
    [record] = shadow()
    assert record["excluded"] == "wall-clock ResourceLimit" and record["classes"] == []


# ------------------------------------------------------------------ Lean authority (not in S2: refused)

def lean_leg(source, env=ENV):
    """The Lean leg of the shadow comparison: Lean's checked reading, or the exception it gives."""
    return EN._lean_reading(env, source, EN.EnglishVocabulary(env), {})


def lying(case):
    """A well-formed answer for the case that reads every text as `Alice owns legacy.`, whatever it says."""
    return {**honest()({**case, "source": "Alice owns legacy."}), "identities": honest()(case)["identities"]}


@pytest.mark.parametrize("authority", ["lean", "rust-experimental"])
def test_no_named_override_makes_the_english_reader_the_authority(monkeypatch, tmp_path, authority):
    """DRI ruling 6 (review A2): the reader stays outside admission. Selecting it is refused, before Lean is
    called, instead of replacing Python's verdict (`Legacy is deployed .` was accepted that way)."""
    monkeypatch.setenv("VE_SHADOW_LOG", str(tmp_path / "log.jsonl"))
    fake = honest()
    use(monkeypatch, fake)
    monkeypatch.setenv("VE_AUTHORITY_OVERRIDES", f"english.admission={authority}")
    for source in (*ACCEPTED, *REJECTED, "Legacy is deployed ."):
        with pytest.raises(CheckerUnavailable, match="only the python or shadow authority"):
            EN.parse_english_with_metadata(ENV, source)
    assert fake.calls == [] and not (tmp_path / "log.jsonl").exists()


@pytest.mark.parametrize("setting", ["english.admission=shadow", "english.admission=shadow pinned lean",
                                     "english.admission=python pinned lean"])
def test_a_lying_reader_never_changes_the_admitted_document(monkeypatch, shadow, setting):
    """Under shadow, and under a composing adapter's pin, Python's outcome is returned even when Lean's answer
    differs: the difference is only recorded."""
    from ve.backends import dispatch
    monkeypatch.setenv("VE_AUTHORITY_OVERRIDES", "english.admission=python")
    expected = {source: outcome(source) for source in ACCEPTED + REJECTED}
    use(monkeypatch, lying)
    monkeypatch.setenv("VE_AUTHORITY_OVERRIDES", setting.split()[0])
    if "pinned" in setting:
        with dispatch.pinned("lean"):
            found = {source: outcome(source) for source in ACCEPTED + REJECTED}
    else:
        found = {source: outcome(source) for source in ACCEPTED + REJECTED}
    assert found == expected
    if setting.split()[0].endswith("shadow"):
        assert any(record["classes"] for record in shadow())


def test_execute_refuses_a_shadow_only_operation():
    """A sibling caller cannot route english.admission through `execute`, where a selection could make the
    reader the authority; and `shadowed` serves only the shadow-only operations."""
    from ve.backends import dispatch
    with pytest.raises(ValueError, match="shadow-only"):
        dispatch.execute("english.admission", {}, lambda: 1, lean=lambda: 2)
    with pytest.raises(ValueError, match="not a shadow-only"):
        dispatch.shadowed("parse", {}, lambda: 1, lambda: 2, lambda a, b: None)


def test_invalid_grammar_is_checker_unavailable(monkeypatch):
    fake = honest()

    def invalid(case):
        return {"identities": fake(case)["identities"], "status": "invalidGrammar", "code": "InvalidGrammar",
                "text": "The grammar is not valid.", "fault": "lexicon", "failure": ["V5", "negative", "owns"]}
    use(monkeypatch, invalid)
    with pytest.raises(CheckerUnavailable, match="invalidGrammar lexicon: V5 negative owns"):
        lean_leg(ACCEPTED[0])


def test_a_missing_reader_is_checker_unavailable(monkeypatch, tmp_path):
    monkeypatch.setattr(L, "TRANSPORT", None)
    monkeypatch.setenv("VE_ENGLISH_ROUTE", str(tmp_path / "missing"))
    with pytest.raises(CheckerUnavailable, match="not built"):
        lean_leg(ACCEPTED[0])


# ------------------------------------------------------------------ malformed answers (checklist 4, 5)

def genuine(source=ACCEPTED[1]):
    case = L.request(ENV, source, EN.EnglishVocabulary(ENV), {})
    return case, honest()(case)


def mutants(response):
    """Each field dropped, emptied, retyped (7, true, null, [], {}), and each number given as a Boolean."""
    for key in list(response):
        yield f"drop {key}", {k: v for k, v in response.items() if k != key}
        for label, value in (("7", 7), ("true", True), ("null", None), ("[]", []), ("{}", {}), ("''", "")):
            if value != response[key] or type(value) is not type(response[key]):
                yield f"{key}={label}", {**response, key: value}
    for name in response["identities"]:
        changed = copy.deepcopy(response)
        changed["identities"][name] = "0" * 64
        yield f"identity {name}", changed
        dropped = copy.deepcopy(response)
        del dropped["identities"][name]
        yield f"drop identity {name}", dropped
    with_overlay = copy.deepcopy(response)
    with_overlay["identities"]["overlay_digest"] = "0" * 64
    yield "overlay_digest without an overlay (i6)", with_overlay
    yield "conclusion as a Boolean", {**response, "conclusions": [True]}
    yield "conclusion out of range", {**response, "conclusions": [5]}
    yield "conclusions repeated", {**response, "conclusions": [1, 1]}
    yield "derivation short", {**response, "derivation": response["derivation"][:1]}
    tree = response["derivation"][0]
    for label, bad in (("a node as a string", ["sentence.plain", *tree[1:]]),
                       ("an empty tag", [["", 0, 2], *tree[1:]]),
                       ("an empty span", [["sentence.plain", 1, 1], *tree[1:]]),
                       ("a root not at 0", [["sentence.plain", 1, 2], ["formula.atom", 1, 2]]),
                       ("a child outside its parent", [tree[0], ["formula.atom", 1, 3]]),
                       ("a span as a Boolean", [["sentence.plain", False, 2], *tree[1:]]),
                       ("a node with four fields", [["sentence.plain", 0, 2, 0], *tree[1:]]),
                       ("an empty tree", [])):
        yield f"derivation: {label}", {**response, "derivation": [bad, *response["derivation"][1:]]}
    yield "a canonical text from Lean", {**response, "canonical": "Legacy is deployed."}
    yield "an unknown field", {**response, "steps": 3}
    yield "a nested null", {**response, "ast": [response["ast"][0], ["const", None]]}
    yield "a formula that does not decode", {**response, "ast": [response["ast"][0], ["unary", "nowhere"]]}
    yield "too deep", {**response, "ast": [json.loads("[" * 5000 + "]" * 5000)]}
    yield "rejected with an unknown code", {"identities": response["identities"], "status": "rejected",
                                            "code": "Internal", "text": "x"}
    yield "many with one witness", {"identities": response["identities"], "status": "many", "code": "Ambiguous",
                                    "text": "x", "sentence": 0, "witnesses": [[["a", 0, 1]]]}
    yield "many with a malformed witness", {"identities": response["identities"], "status": "many",
                                            "code": "Ambiguous", "text": "x", "sentence": 0,
                                            "witnesses": [[["a", 0, 1]], [["b", 0, 0]]]}
    yield "sentence as a Boolean", {"identities": response["identities"], "status": "none", "code": "NoDerivation",
                                    "text": "x", "sentence": False}
    yield "an unknown fault", {"identities": response["identities"], "status": "invalidGrammar",
                               "code": "InvalidGrammar", "text": "x", "fault": "other"}
    for status, code in (("none", "Ambiguous"), ("many", "NoDerivation"), ("budget", "SortMismatch"),
                         ("invalidGrammar", "IllTyped")):
        extra = {"many": {"sentence": 0, "witnesses": [[["a", 0, 1]], [["b", 0, 1]]]},
                 "invalidGrammar": {"fault": "lexicon"}}.get(status, {"sentence": 0})
        yield f"{status} with the code {code}", {"identities": response["identities"], "status": status,
                                                 "code": code, "text": "x", **extra}
    yield "rejected with a status code", {"identities": response["identities"], "status": "rejected",
                                          "code": "NoDerivation", "text": "x"}


def test_the_genuine_answer_is_well_formed():
    case, response = genuine()
    expected = L.identities(ENV, case["source"], EN.EnglishVocabulary(ENV), case["lexicon"])
    assert L.response_problem(response, expected, ENV) is None


def test_every_malformed_answer_is_checker_unavailable(monkeypatch):
    case, response = genuine()
    seen = 0
    for label, mutated in mutants(response):
        use(monkeypatch, lambda _case, mutated=mutated: mutated)
        try:
            lean_leg(case["source"])
        except CheckerUnavailable:
            seen += 1
            continue
        pytest.fail(f"{label}: accepted")
    assert seen > 60


def test_a_formula_outside_the_environment_is_checker_unavailable(monkeypatch):
    case, response = genuine()
    response["ast"][0] = ["unary", "nowhere", ["const", "legacy"]]
    use(monkeypatch, lambda _case: response)
    with pytest.raises(CheckerUnavailable):
        lean_leg(case["source"])


def test_the_request(monkeypatch):
    overlay = {"format": "ve.english-vocabulary@1", "sorts": {}, "predicates": {}, "constants": {}}
    case = L.request(ENV, "Alice owns legacy.", EN.EnglishVocabulary(ENV), {})
    assert set(case) == {"id", "environment", "lexicon", "source", "mode", "cap"}
    assert case["mode"] == "authoring" and case["cap"] == 2 and case["lexicon"] == EG.export(EN.EnglishVocabulary(ENV))
    assert L.request(ENV, "x.", EN.EnglishVocabulary(ENV), {"vocabulary": overlay})["overlay"] == overlay


# ------------------------------------------------------------------ the transport

def fake_route(tmp_path: Path, body: str) -> Path:
    script = tmp_path / "ve_english_route"
    script.write_text("#!/bin/sh\ncat > /dev/null\n" + body)
    script.chmod(0o755)
    return script


def test_the_route_transport_reads_one_row_per_case(tmp_path):
    route = fake_route(tmp_path, """printf '[{"id":"english.read","status":"ok","result":{}}]'\n""")
    assert lean_backend.run_english_cases(route, "english.read", [{"id": "english.read"}]) == [
        {"id": "english.read", "status": "ok", "result": {}}]


@pytest.mark.parametrize("body", ["exit 3\n", "printf 'not json'\n", "printf '[]'\n",
                                  """printf '[{"id":"other","status":"ok"}]'\n""",
                                  """printf '[{"id":"english.read","status":"ok"}]'; exit 1\n"""])
def test_a_route_without_an_answer_is_checker_unavailable(tmp_path, body):
    route = fake_route(tmp_path, body)
    with pytest.raises(CheckerUnavailable):
        lean_backend.run_english_cases(route, "english.read", [{"id": "english.read"}])


def test_a_route_row_without_a_result_is_checker_unavailable(monkeypatch, tmp_path):
    monkeypatch.setattr(L, "TRANSPORT", None)
    monkeypatch.setenv("VE_ENGLISH_ROUTE", str(fake_route(
        tmp_path, """printf '[{"id":"english.read","status":"ok","other":1}]'\n""")))
    with pytest.raises(CheckerUnavailable, match="did not read the case"):
        lean_leg(ACCEPTED[0])


# ------------------------------------------------------------------ identities under ve/

def test_the_lexicon_export_moved_under_ve():
    from conformance import english_lean_lexicon as X
    assert X.export is EG.export and X.lexicon_id is EG.lexicon_id


def test_grammar_id_covers_the_table_sources_of_the_profiles():
    base = EG.grammar_id(["relational-fol@0"])
    assert base == EG.grammar_id(["relational-fol@0", "closure@0"])  # closure@0 has no table (spec 2.5)
    assert base != EG.grammar_id([]) and len(base) == 64
    digest = hashlib.sha256((EG.HERE / "relational-fol@0.json").read_bytes()).hexdigest()
    assert base == EG.digest(EG.GRAMMAR_DOMAIN, [["relational-fol@0", digest]])
    assert EG.digest("ve-english-lexicon-v1\n", [["relational-fol@0", digest]]) != base


def test_actions_version_is_the_lock_files():
    assert EG.actions_version() == json.loads((EG.HERE / "LOCK.json").read_text())["actions_version"]


def test_the_class_map_covers_the_codes_lean_gives():
    """The adapter's map (spec 4.2) has every code of Lean's `Reject.code` that the base profile reaches, and
    `IllTyped`, the code of the typed check's outcome, and `CoefficientNotNumeral`, which `order@0` reaches
    (S3 2.8); `Internal` (never constructed, spec 5.7) stays outside it, so an answer naming it fails closed.
    The status codes are the ones `VE.EnglishGrammar.Run` writes. Spec 5.7's text search, on the Lean
    source."""
    import re
    root = Path(__file__).resolve().parents[1] / "lean/VE/EnglishGrammar"
    syntax = (root / "Syntax.lean").read_text()
    body = syntax[syntax.index("def Reject.code"):syntax.index("structure DState")]
    codes = set(re.findall(r'=> "(\w+)"', body))
    assert codes - set(L.CLASSES) == {"Internal"}
    assert L.CLASSES["CoefficientNotNumeral"] == ("SyntaxError",)
    assert set(L.CLASSES) - codes == {"IllTyped"}
    run = (root / "Run.lean").read_text()
    assert all(f'coded "{code}"' in run for code in [*L.STATUS_CODES.values(), "IllTyped"])
