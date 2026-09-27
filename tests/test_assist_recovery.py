import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from ve.assist.ambiguity_patterns import PATTERNS, review, candidates
from ve.assist.recovery import RecoveryService, nearest_wordings
from ve.ast import Unary, Const, Not
from ve.environment import Environment, LANGUAGE, PROFILE, SPEC_REVISION
from ve.search import find_countermodel
from ve.errors import InvalidModel
from ve.identity import meaning_id
from ve.english import render_english, parse_english_with_metadata


def environment():
    names = ("alice", "bob", "team", "api", "service_a", "carol")
    return Environment({"language": LANGUAGE, "profile": PROFILE, "spec_revision": SPEC_REVISION,
        "vocabulary": {"sorts": {"service": {"description": "service"},
                                  "engineer": {"description": "engineer"},
                                  "server": {"description": "server"}},
                       "predicates": {**{p: {"arguments": ["service"], "description": p}
                                          for p in ("safe", "reviews")},
                                      "checks_pair": {"arguments": ["engineer", "server"],
                                                      "description": "checks",
                                                      "verbalisation": "{0} checks {1}"}},
                       "constants": {name: {"sort": "service", "description": name} for name in names}}})


def test_catalogue_fixtures_match_and_negative_cases():
    env = environment()
    path = Path(__file__).resolve().parents[1] / "experiments/authoring-gates/ambiguity-patterns/catalogue-v1.json"
    fixture = json.loads(path.read_text())
    assert len(fixture["fixtures"]) == len(PATTERNS)
    for row in fixture["fixtures"]:
        payload = {k: row[k] for k in ("pattern_id", "source", "bindings", "boundary", "negative")}
        assert row["seal_sha256"] == hashlib.sha256(json.dumps(
            payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        pattern = next(p for p in PATTERNS if p.id == row["pattern_id"])
        assert pattern.matches(row["source"])
        assert not pattern.matches(row["negative"])
        bindings = dict(row["bindings"])
        if row["pattern_id"] == "scope.every_some@1":
            bindings["relation"] = "checks_pair"
        rows, residual = candidates(env, row["source"], bindings, pattern_id=row["pattern_id"])
        if row["pattern_id"] == "attachment.modifier@1":
            assert not rows and "no supported source reading" in residual
        else:
            assert not residual and len(rows) >= (1 if row["pattern_id"] in {
                "scope.negation@1", "coordination.list@1"} else 2)
        boundary_rows, boundary_residual = candidates(env, row["boundary"], bindings,
                                                       pattern_id=row["pattern_id"])
        assert boundary_residual or len(boundary_rows) <= len(rows)


def test_scope_card_requires_checked_distinction():
    env = environment()
    result = review(env, "Every engineer checks a server.",
        {"every_sort": "engineer", "some_sort": "server", "relation": "checks_pair"},
        pattern_id="scope.every_some@1")
    assert result["cards"] and result["cards"][0]["values"] in ([True, False], [False, True])
    assert not result["pending"]


def test_unproven_pair_remains_pending():
    env = environment()
    result = review(env, "It is safe.", {"predicate": "safe", "antecedents": ["api", "api"]},
                    pattern_id="discourse.reference@1")
    assert not result["cards"] and result["pending"]


def test_existential_reference_and_transitive_ellipsis_remain_residual():
    env = environment()
    rows, reason = candidates(env, "The API is deployed. Some service is reviewed. It is safe.",
                              {"predicate": "safe", "antecedents": ["api", "service_a"]},
                              pattern_id="discourse.reference@1")
    assert not rows and "scoped rewrite" in reason
    rows, reason = candidates(env, "Alice reviews the API. Carol does too.",
                              {"subject": "carol", "predicates": ["reviews", "checks"],
                               "transitive": True}, pattern_id="ellipsis.predicate_copy@1")
    assert not rows and "scoped completion" in reason


def test_revisioned_approval_and_invalidation():
    env = environment()
    situation = find_countermodel(env, (), Not(Unary("safe", Const("api")))).model.to_dict()
    carol_situation = find_countermodel(env, (), Not(Unary("safe", Const("carol")))).model.to_dict()
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    service.add("u1", "The API is safe.", {"start": 0, "end": 16})
    service.start("u1")
    assert service.classify("u1", parse_outcome="one") == "ready"
    service.approve("u1", Unary("safe", Const("api")), actor="author",
                    paraphrase="Api is safe.", presentation="Api is safe.", situation=situation)
    assert service.approval_valid("u1")
    approved_revision = service.units["u1"].revision
    ledger = service.to_ledger()
    assert service.verify_ledger(ledger)
    ledger["events"][-1]["unit_snapshot"]["source"] = "tampered"
    assert not service.verify_ledger(ledger)
    assert service.undo("u1", approved_revision).state == "approved"
    assert service.approval_valid("u1")
    service.add("u2", "Carol agrees.", {"start": 17, "end": 30}, dependencies=["u1"])
    service.start("u2")
    service.classify("u2", parse_outcome="one")
    service.approve("u2", Unary("safe", Const("carol")), actor="author",
                    paraphrase="Carol is safe.", presentation="Carol is safe.", situation=carol_situation)
    service.edit("u1", source="The API is reviewed.")
    assert not service.approval_valid("u1") and service.units["u2"].state == "stale"
    assert service.events[-1]["revision"] == service.revision
    assert service.verify_ledger()
    restored = service.undo("u1", approved_revision)
    assert restored.state == "approved" and service.approval_valid("u1")
    assert service.units["u2"].state == "stale"
    assert service.verify_ledger()


def test_recovery_pending_translation_and_adapter_stubs():
    env = environment()
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    service.add("u", "The API is safe.", {"start": 0}, mode="translation")
    service.start("u")
    assert service.classify("u", parse_outcome="one", discourse="incomplete") == "reading_review"
    service.resolve_pending("u", 0, actor="translator", reason="antecedent supplied",
                            disposition="resolved", wording="Api is safe.",
                            cited_spans=[{"start": 0, "end": 3}])
    service.set_readings("u", [{"meaning_id": meaning_id(env, Unary("safe", Const(c))),
                                "wording": render_english(Unary("safe", Const(c)), env) + "."}
                                   for c in ("api", "carol")])
    situation = find_countermodel(env, (), Not(Unary("safe", Const("api")))).model.to_dict()
    with pytest.raises(ValueError, match="narrowing"):
        service.approve("u", Unary("safe", Const("api")), actor="author",
            paraphrase="Api is safe.", presentation="Api is safe.", situation=situation)
    assert service.alias_prompt(source="staff", target="employees", argument_types=["person"],
                                direction="same", context="document")["status"] == "pending"
    with pytest.raises(RuntimeError, match="W2"):
        service.add_unit({}, anchor={})
    assert nearest_wordings("safe", ["safe", "reviewed", "deployed"])[0] == "safe"


def test_unique_parse_still_triggers_catalogue_review():
    env = environment()
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    service.add("u", "Every engineer checks a server.", {"start": 0})
    service.start("u")
    assert service.classify("u", parse_outcome="one") == "reading_review"
    assert service.units["u"].pending[0]["pattern_id"] == "scope.every_some@1"
    service.cancel("u")
    service.start("u")
    assert service.classify("u", parse_outcome="one", catalogue_bindings={
        "scope.every_some@1": {"every_sort": "engineer", "some_sort": "server",
                                "relation": "checks_pair"}}) == "ready"
    assert service.units["u"].catalogue_results["scope.every_some@1"]["cards"]


def test_invalid_situation_and_presentation_cannot_be_approved():
    env = environment()
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    service.add("u", "The API is safe.", {"start": 0})
    service.start("u")
    service.classify("u", parse_outcome="one")
    formula = Unary("safe", Const("api"))
    situation = find_countermodel(env, (), Not(formula)).model.to_dict()
    with pytest.raises(ValueError, match="correspondence"):
        service.approve("u", formula, actor="author", paraphrase="Api is safe.",
                        presentation="Carol is safe.", situation=situation)
    situation["relations"]["safe"] = []
    with pytest.raises(ValueError, match="does not satisfy"):
        service.approve("u", formula, actor="author", paraphrase="Api is safe.",
                        presentation="Api is safe.", situation=situation)


def test_proposer_reservation_and_explicit_retry():
    class Offline:
        def request(self, source, *, timeout_seconds):
            assert timeout_seconds == 50
            raise OSError("offline")
    env = environment()
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    service.add("u", "Unknown wording.", {"start": 0})
    service.start("u")
    service.classify("u", parse_outcome="zero")
    assert service.request_proposer("u", Offline())["status"] == "exhausted"
    assert service.units["u"].proposals == 1
    assert service.events[-2]["action"] == "proposer_reserved"
    assert service.request_proposer("u", Offline())["status"] == "exhausted"
    assert service.units["u"].proposals == 2
    assert service.request_proposer("u", Offline())["status"] == "unresolved"


def test_clarification_reply_cap_is_separate_from_proposer_cap():
    env = environment()
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    service.add("u", "Unknown wording.", {"start": 0})
    service.start("u")
    for _ in range(8):
        service.classify("u", parse_outcome="zero")
        assert service.reply("u", "Please try this wording") == "analysing"
    service.classify("u", parse_outcome="zero")
    assert service.reply("u", "One more") == "unresolved"
    assert service.units["u"].proposals == 0
    service.edit("u", source="Api is safe.")
    assert service.start("u") == "unresolved"


def test_authoring_requires_explicit_rejection_of_distinct_reading():
    env = environment()
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    service.add("u", "It is safe.", {"start": 0})
    service.start("u")
    assert service.classify("u", parse_outcome="one", catalogue_bindings={
        "discourse.reference@1": {"predicate": "safe", "antecedents": ["api", "carol"]}}) == "ready"
    formula = Unary("safe", Const("api"))
    situation = find_countermodel(env, (), Not(formula)).model.to_dict()
    with pytest.raises(ValueError, match="explicit rejection"):
        service.approve("u", formula, actor="author", paraphrase="Api is safe.",
                        presentation="Api is safe.", situation=situation)


def test_every_displayed_meaning_is_checked_again_at_approval():
    env = environment()
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    service.add("u", "Api is safe.", {})
    service.start("u")
    service.classify("u", parse_outcome="one")
    formula = Unary("safe", Const("api"))
    situation = find_countermodel(env, (), Not(formula)).model.to_dict()
    with pytest.raises(ValueError, match="displayed meaning fails"):
        service.approve("u", formula, actor="author", paraphrase="Api is not safe.",
                        presentation="Api is safe.", situation=situation)
    assert service.units["u"].state == "ready" and not service.units["u"].readings


def test_catalogue_wordings_are_writable_and_not_invented_readings():
    env = environment()
    for source, pattern, bindings in (
        ("Not all services are safe.", "scope.negation@1", {"sort": "service", "predicate": "safe"}),
        ("Alice and Bob are safe.", "coordination.list@1", {"predicate": "safe", "left": "alice", "right": "bob"}),
        ("The service with the API is safe.", "attachment.modifier@1",
         {"modifier": "safe", "left": "service_a", "right": "api"}),
    ):
        result = review(env, source, bindings, pattern_id=pattern)
        assert not result["cards"]
    result = review(env, "It is safe.", {"predicate": "safe", "antecedents": ["api", "carol"]},
                    pattern_id="discourse.reference@1")
    for candidate in result["candidates"]:
        parsed = parse_english_with_metadata(env, candidate["wording"] + "\n")
        assert meaning_id(env, parsed.document.formulas[0]) == candidate["meaning_id"]
    assert all("property" not in wording and "antecedent" not in wording
               for card in result["cards"] for wording in card["paraphrases"])
    raw = review(env, "It is safe.", {"predicate": "safe", "antecedents": ["api", "service_a"]},
                 pattern_id="discourse.reference@1")
    assert not raw["cards"] and "plain English vocabulary" in raw["residual"]


def test_pending_cannot_be_erased_and_pattern_disposition_is_attributed():
    env = environment()
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    service.add("u", "It is safe.", {})
    service.start("u")
    assert service.classify("u", parse_outcome="one", discourse="incomplete") == "reading_review"
    service.set_readings("u", [])
    assert service.units["u"].pending and service.units["u"].state == "reading_review"
    service.cancel("u")
    service.start("u")
    assert service.classify("u", parse_outcome="one", discourse="complete") == "reading_review"
    with pytest.raises(ValueError, match="incomplete"):
        service.approve("u", Unary("safe", Const("api")), actor="a",
                        paraphrase="Api is safe.", presentation="Api is safe.", situation={})
    pattern_index = next(i for i, row in enumerate(service.units["u"].pending) if row.get("pattern_id"))
    service.resolve_pending("u", pattern_index, actor="author", reason="No pronoun in rewrite",
                            disposition="not_applicable")
    assert service.units["u"].pending
    service.resolve_pending("u", 0, actor="author", reason="Rewrote the antecedent explicitly",
                            disposition="resolved", wording="Api is safe.",
                            cited_spans=[{"start": 0, "end": 2}])
    assert service.units["u"].state == "ready"
    assert service.events[-2]["actor"] == "author"


def test_translation_requires_separate_narrowing_and_keeps_source_set():
    env = environment()
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    service.add("u", "It is safe.", {}, mode="translation")
    service.start("u")
    assert service.classify("u", parse_outcome="one", catalogue_bindings={
        "discourse.reference@1": {"predicate": "safe", "antecedents": ["api", "carol"]}}) == "ready"
    formula = Unary("safe", Const("api"))
    situation = find_countermodel(env, (), Not(formula)).model.to_dict()
    selected = dict(actor="translator", paraphrase="Api is safe.", presentation="Api is safe.", situation=situation)
    assert len(service.units["u"].readings) == 2
    with pytest.raises(ValueError, match="narrowing"):
        service.approve("u", formula, **selected)
    with pytest.raises(ValueError, match="invalid attributed"):
        service.record_narrowing("u", keeps=["unknown"], actor="translator", reason="source span",
                                 cited_spans=[{"start": 0, "end": 2}])
    record = service.record_narrowing("u", keeps=[meaning_id(env, formula)], actor="translator",
                                      reason="antecedent resolved by cited phrase", cited_spans=[{"start": 0, "end": 2}])
    service.approve("u", formula, narrowing=record["id"], **selected)
    assert len(service.units["u"].readings) == 2
    assert service.events[-2]["action"] == "narrowing"


def test_narrowing_is_bound_to_exact_source_set_and_card_is_rechecked():
    env = environment()
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    service.add("u", "It is safe.", {}, mode="translation")
    service.start("u")
    service.classify("u", parse_outcome="one", catalogue_bindings={
        "discourse.reference@1": {"predicate": "safe", "antecedents": ["api", "carol"]}})
    formula = Unary("safe", Const("api"))
    record = service.record_narrowing("u", keeps=[meaning_id(env, formula)], actor="translator",
                                      reason="cited antecedent", cited_spans=[{"start": 0, "end": 2}])
    extra = Unary("safe", Const("alice"))
    service.set_readings("u", service.units["u"].readings + [{"meaning_id": meaning_id(env, extra),
        "wording": "Alice is safe."}])
    situation = find_countermodel(env, (), Not(formula)).model.to_dict()
    kwargs = dict(actor="translator", paraphrase="Api is safe.", presentation="Api is safe.",
                  situation=situation, narrowing=record["id"])
    with pytest.raises(ValueError, match="narrowing"):
        service.approve("u", formula, **kwargs)
    fresh = service.record_narrowing("u", keeps=[meaning_id(env, formula)], actor="translator",
                                     reason="cited antecedent", cited_spans=[{"start": 0, "end": 2}])
    service.units["u"].catalogue_results["discourse.reference@1"]["cards"][0]["paraphrases"][1] = "Api is safe."
    # An edited cache never reaches a transition, and the approval check itself rereads the card.
    with pytest.raises(ValueError, match="ledger replay"):
        service.approve("u", formula, **{**kwargs, "narrowing": fresh["id"]})
    from ve.assist.ambiguity_patterns import Budget
    with pytest.raises(ValueError, match="card wording changed meaning"):
        service._approval("u", formula, **{**kwargs, "narrowing": fresh["id"]}, rejected=(),
                          budget=Budget())


def test_pagination_retains_cards_counts_and_cursor_until_complete():
    env = environment()
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    service.add("u", "It is safe.", {})
    service.start("u")
    bindings = {"predicate": "safe", "antecedents": ["api", "bob", "carol", "alice"]}
    assert service.classify("u", parse_outcome="one", catalogue_bindings={
        "discourse.reference@1": bindings}) == "reading_review"
    result = service.units["u"].catalogue_results["discourse.reference@1"]
    assert len(result["cards"]) == 3 and result["next_cursor"] == 3
    assert len(service.units["u"].readings) == 4
    result = service.continue_catalogue("u", "discourse.reference@1", bindings)
    assert len(result["cards"]) == 6 and result["comparison_count"] == 6
    assert result["next_cursor"] is None and service.units["u"].state == "ready"


def test_none_of_these_reply_history_proposer_and_task_cap():
    env = environment()
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    service.add("u", "Api is safe.", {})
    service.start("u")
    service.classify("u", parse_outcome="one")
    assert service.reply("u", "None of these; Api is reviewed.", rejected=[
        {"meaning_id": "candidate-1", "reason": "source disagrees"}]) == "analysing"
    assert service.events[-1]["text"].startswith("None of these")
    assert service.units["u"].rejected[0]["meaning_id"] == "candidate-1"
    class Suggest:
        def request(self, source, *, timeout_seconds):
            return "Api is safe."
    service.classify("u", parse_outcome="zero")
    service.request_proposer("u", Suggest())
    assert service.events[-1]["text"] == "Api is safe."
    started = service.units["u"].started
    service.clock = lambda: started + 301
    service.cancel("u")
    assert service.start("u") == "unresolved"
    service.edit("u", source="Api is safe.")
    assert service.start("u") == "unresolved"


def test_ledger_json_restore_and_revision_guard():
    env = environment()
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    service.add("u", "Api is safe.", {})
    service.start("u")
    service.classify("u", parse_outcome="one")
    formula = Unary("safe", Const("api"))
    situation = find_countermodel(env, (), Not(formula)).model.to_dict()
    service.approve("u", formula, actor="author", paraphrase="Api is safe.",
                    presentation="Api is safe.", situation=situation)
    ledger = json.loads(json.dumps(service.to_ledger()))
    restored = RecoveryService.from_ledger(env, ledger)
    assert restored.verify_ledger() and restored.approval_valid("u")
    with pytest.raises(ValueError, match="stale recovery revision"):
        restored.edit("u", source="Api is reviewed.", expected_revision=0)
    ledger["events"][-1]["unit_snapshot"]["paraphrase"] = "Api is not safe."
    with pytest.raises(ValueError, match="invalid recovery ledger"):
        RecoveryService.from_ledger(env, ledger)


def test_versions_exhaustion_and_undo_review_transition():
    env = environment()
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    service.add("u", "Api is safe.", {})
    service.start("u")
    service.classify("u", parse_outcome="one")
    formula = Unary("safe", Const("api"))
    situation = find_countermodel(env, (), Not(formula)).model.to_dict()
    service.approve("u", formula, actor="author", paraphrase="Api is safe.",
                    presentation="Api is safe.", situation=situation)
    approved_revision = service.units["u"].revision
    service.update_versions(glossary="v2")
    assert service.units["u"].state == "stale" and not service.approval_valid("u")
    other = env.to_dict()
    other["vocabulary"]["predicates"].pop("safe")
    service.env = Environment(other)
    assert service.undo("u", approved_revision).state == "stale"
    assert service.events[-1]["action"] == "undo_requires_review"

    capped = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    capped.add("x", "Unknown wording.", {})
    capped.start("x")
    assert capped.classify("x", parse_outcome="exhausted", limit="parser budget") == "exhausted"
    assert capped.units["x"].reason == "parser budget"


def test_catalogue_unknown_background_and_pair_limit_are_visible(monkeypatch):
    import ve.assist.ambiguity_patterns as catalogue

    env = environment()
    bindings = {"predicate": "safe", "antecedents": ["api", "bob", "carol"]}
    pattern = "discourse.reference@1"
    monkeypatch.setattr(catalogue, "find_distinguishing_model", lambda *a, **k:
                        SimpleNamespace(status="Unknown", model=None, detail="search budget"))
    unknown = catalogue.review(env, "It is safe.", bindings, pattern_id=pattern)
    assert not unknown["cards"] and len(unknown["pending"]) == 3
    assert all(row["reason"] == "search budget" for row in unknown["pending"])

    model = find_countermodel(env, (), Not(Unary("safe", Const("api")))).model
    monkeypatch.setattr(catalogue, "find_distinguishing_model", lambda *a, **k:
                        SimpleNamespace(status="Found", model=model, detail=""))
    def invalid_background(*args):
        raise InvalidModel("invalid Background")
    monkeypatch.setattr(catalogue, "validate_background", invalid_background)
    invalid = catalogue.review(env, "It is safe.", bindings, pattern_id=pattern)
    assert not invalid["cards"] and len(invalid["pending"]) == 3
    assert all("invalid Background" in row["reason"] for row in invalid["pending"])

    monkeypatch.setattr(catalogue, "validate_background", lambda *args: None)
    monkeypatch.setattr(catalogue, "MAX_COMPARISONS", 1)
    limited = catalogue.review(env, "It is safe.", bindings, pattern_id=pattern)
    assert limited["next_cursor"] == 1 and limited["comparison_count"] == 1
    assert any(row["reason"].startswith("pair comparison limit") for row in limited["pending"])


def test_edit_preserves_review_for_unchanged_source():
    env = environment()
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    service.add("u", "It is safe.", {}, mode="translation")
    service.start("u")
    service.classify("u", parse_outcome="one", catalogue_bindings={
        "discourse.reference@1": {"predicate": "safe", "antecedents": ["api", "carol"]}})
    original = service.revision
    service.edit("u", source="It is safe.")
    assert service.revision == original
    service.edit("u", presentation="Api is safe.")
    assert len(service.units["u"].readings) == 2
    formula = Unary("safe", Const("api"))
    situation = find_countermodel(env, (), Not(formula)).model.to_dict()
    with pytest.raises(ValueError, match="narrowing"):
        service.approve("u", formula, actor="translator", paraphrase="Api is safe.",
                        presentation="Api is safe.", situation=situation)
    service.units["u"].catalogue_results.clear()
    with pytest.raises(ValueError, match="ledger replay"):
        service.approve("u", formula, actor="translator", paraphrase="Api is safe.",
                        presentation="Api is safe.", situation=situation)
    with pytest.raises(ValueError, match="catalogue review is incomplete"):
        service._catalogue_complete(service.units["u"])


def test_edit_keeps_unresolved_pending_distinction():
    service = RecoveryService(environment(), grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    service.add("u", "It is safe.", {})
    service.start("u")
    service.classify("u", parse_outcome="one", discourse="incomplete")
    pending = service.units["u"].pending.copy()
    service.edit("u", anchor={"start": 0})
    assert service.units["u"].state == "reading_review"
    assert service.units["u"].pending == pending


def test_import_rechecks_display_even_when_ledger_hashes_are_recomputed():
    def forge(ledger):
        approved = next(e["unit_snapshot"] for e in ledger["events"] if e["action"] == "approve")
        approved["paraphrase"] = "Api is not safe."
        approved["approval"]["snapshot"]["paraphrase"] = "Api is not safe."
        approved["approval"]["digest"] = hashlib.sha256(json.dumps(
            approved["approval"]["snapshot"], sort_keys=True, ensure_ascii=False,
            separators=(",", ":")).encode()).hexdigest()
        previous = None
        for event in ledger["events"]:
            event["previous_digest"] = previous
            event["event_digest"] = hashlib.sha256(json.dumps(
                {k: v for k, v in event.items() if k != "event_digest"}, sort_keys=True,
                ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
            previous = event["event_digest"]
        return ledger

    env = environment()
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    service.add("u", "Api is safe.", {})
    service.start("u")
    service.classify("u", parse_outcome="one")
    formula = Unary("safe", Const("api"))
    situation = find_countermodel(env, (), Not(formula)).model.to_dict()
    service.approve("u", formula, actor="author", paraphrase="Api is safe.",
                    presentation="Api is safe.", situation=situation)
    with pytest.raises(ValueError, match="invalid recovery ledger"):
        RecoveryService.from_ledger(env, forge(service.to_ledger()))
    service.edit("u", source="Api is reviewed.")
    with pytest.raises(ValueError, match="invalid recovery ledger"):
        RecoveryService.from_ledger(env, forge(service.to_ledger()))


def test_proposer_result_after_cancel_is_discarded():
    service = RecoveryService(environment(), grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    service.add("u", "Unknown wording.", {})
    service.start("u")
    service.classify("u", parse_outcome="zero")
    class CancelDuringRequest:
        def request(self, source, *, timeout_seconds):
            service.cancel("u")
            return "Api is safe."
    result = service.request_proposer("u", CancelDuringRequest(), expected_revision=service.revision)
    assert result["status"] == "stale"
    assert service.events[-1]["action"] == "cancel"


def test_narrowing_uses_w2_and_records_document_dependency():
    env = environment()
    class RejectingAdapter:
        def add_unit(self, document, **kwargs):
            return document
        def narrow(self, document, **kwargs):
            raise ValueError("W2 rejected narrowing")
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1",
                              reading_set_version="r1", document_adapter=RejectingAdapter())
    service.add("u", "It is safe.", {}, mode="translation")
    service.start("u")
    service.classify("u", parse_outcome="one", catalogue_bindings={
        "discourse.reference@1": {"predicate": "safe", "antecedents": ["api", "carol"]}})
    mid = meaning_id(env, Unary("safe", Const("api")))
    with pytest.raises(ValueError, match="W2"):
        service.record_narrowing("u", keeps=[mid], actor="translator", reason="cited",
                                 cited_spans=[{"start": 0, "end": 2}], document={"units": []})
    assert service.units["u"].narrowings == []

    class AcceptingAdapter:
        def add_unit(self, document, **kwargs):
            self.unit = kwargs
            return document
        def narrow(self, document, **kwargs):
            self.narrowing = kwargs
            return {"valid": True}
    adapter = AcceptingAdapter()
    service.document_adapter = adapter
    record = service.record_narrowing("u", keeps=[mid], actor="translator", reason="cited",
                                      cited_spans=[{"start": 0, "end": 2}], document={"units": []})
    assert adapter.unit["support"] == ["u"]
    assert adapter.narrowing["keeps"] == [mid]
    assert record["document_unit"]["support"] == ["u"]
    formula = Unary("safe", Const("api"))
    situation = find_countermodel(env, (), Not(formula)).model.to_dict()
    approval = service.approve("u", formula, actor="translator", paraphrase="Api is safe.",
                               presentation="Api is safe.", situation=situation, narrowing=record["id"])
    assert approval["snapshot"]["narrowing"] == record["document_unit"]["id"]
    assert RecoveryService.from_ledger(env, json.loads(json.dumps(service.to_ledger()))).approval_valid("u")


def _rehash_ledger(ledger):
    previous = None
    for event in ledger["events"]:
        event["previous_digest"] = previous
        event["event_digest"] = hashlib.sha256(json.dumps(
            {k: v for k, v in event.items() if k != "event_digest"}, sort_keys=True,
            ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
        previous = event["event_digest"]
    return ledger


@pytest.mark.parametrize("obligation", ["catalogue", "pending"])
def test_import_rejects_forged_cancel_erasing_review_obligations(obligation):
    env = environment()
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    service.add("u", "It is safe.", {}, mode="translation")
    service.start("u")
    if obligation == "catalogue":
        service.classify("u", parse_outcome="one", catalogue_bindings={
            "discourse.reference@1": {"predicate": "safe", "antecedents": ["api", "carol"]}})
        assert len(service.units["u"].readings) == 2
    else:
        service.classify("u", parse_outcome="one", discourse="incomplete")
        assert service.units["u"].pending
    service.cancel("u")
    ledger = service.to_ledger()
    snapshot = ledger["events"][-1]["unit_snapshot"]
    if obligation == "catalogue":
        snapshot["readings"] = []
        snapshot["catalogue_reviewed"] = []
        snapshot["catalogue_results"] = {}
    else:
        snapshot["pending"] = []
    forged = _rehash_ledger(ledger)
    assert not service.verify_ledger(forged)
    with pytest.raises(ValueError, match="invalid recovery ledger"):
        RecoveryService.from_ledger(env, forged)


@pytest.mark.parametrize("obligation", ["catalogue_readings", "requested_pending", "catalogue_pending"])
def test_import_rejects_forged_classify_erasing_new_obligations(obligation):
    env = environment()
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    service.add("u", "It is safe.", {}, mode="translation")
    service.start("u")
    bindings = {"discourse.reference@1": {"predicate": "safe", "antecedents": ["api", "carol"]}}
    if obligation == "catalogue_readings":
        service.classify("u", parse_outcome="one", catalogue_bindings=bindings)
        assert len(service.units["u"].readings) == 2
    elif obligation == "requested_pending":
        service.classify("u", parse_outcome="one", pending=[{"reason": "author check"}])
    else:
        service.classify("u", parse_outcome="one")
    ledger = service.to_ledger()
    snapshot = ledger["events"][-1]["unit_snapshot"]
    if obligation == "catalogue_readings":
        snapshot["readings"] = []
    elif obligation == "requested_pending":
        snapshot["pending"] = [row for row in snapshot["pending"] if row.get("pattern_id")]
        snapshot["state"] = ledger["events"][-1]["state"] = "reading_review"
    else:
        snapshot["pending"] = []
        snapshot["state"] = ledger["events"][-1]["state"] = "ready"
    forged = _rehash_ledger(ledger)
    assert not service.verify_ledger(forged)
    with pytest.raises(ValueError, match="invalid recovery ledger"):
        RecoveryService.from_ledger(env, forged)


def test_import_rejects_forged_catalogue_page_erasing_other_pending_review():
    env = environment()
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    service.add("u", "It is safe.", {})
    service.start("u")
    bindings = {"predicate": "safe", "antecedents": ["api", "bob", "carol", "alice"]}
    service.classify("u", parse_outcome="one", discourse="incomplete", catalogue_bindings={
        "discourse.reference@1": bindings})
    service.continue_catalogue("u", "discourse.reference@1", bindings)
    assert any(not row.get("pattern_id") for row in service.units["u"].pending)
    ledger = service.to_ledger()
    ledger["events"][-1]["unit_snapshot"]["pending"] = []
    assert not service.verify_ledger(_rehash_ledger(ledger))


def test_noop_undo_invalidates_approved_dependents_before_parent_revision():
    env = environment()
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    for unit_id, name, dependencies in (("parent", "api", ()), ("child", "carol", ("parent",))):
        service.add(unit_id, f"{name.title()} is safe.", {}, dependencies=dependencies)
        service.start(unit_id)
        service.classify(unit_id, parse_outcome="one")
        formula = Unary("safe", Const(name))
        situation = find_countermodel(env, (), Not(formula)).model.to_dict()
        service.approve(unit_id, formula, actor="author", paraphrase=f"{name.title()} is safe.",
                        presentation=f"{name.title()} is safe.", situation=situation)
        if unit_id == "parent":
            parent_revision = service.units[unit_id].revision
    service.undo("parent", parent_revision)
    assert service.units["parent"].state == "approved"
    assert service.approval_valid("parent")
    assert service.units["child"].state == "stale"
    assert not service.approval_valid("child")
    assert service.verify_ledger()
    restored = RecoveryService.from_ledger(env, json.loads(json.dumps(service.to_ledger())))
    assert restored.verify_ledger() and restored.units["child"].state == "stale"


def test_undo_to_ready_revision_invalidates_approved_dependents():
    env = environment()
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    for unit_id, name, dependencies in (("parent", "api", ()), ("child", "carol", ("parent",))):
        wording = f"{name.title()} is safe."
        service.add(unit_id, wording, {}, dependencies=dependencies)
        service.edit(unit_id, presentation=wording)
        service.start(unit_id)
        service.classify(unit_id, parse_outcome="one")
        if unit_id == "parent":
            ready_revision = service.units[unit_id].revision
        formula = Unary("safe", Const(name))
        situation = find_countermodel(env, (), Not(formula)).model.to_dict()
        service.approve(unit_id, formula, actor="author", paraphrase=wording,
                        presentation=wording, situation=situation)
    service.undo("parent", ready_revision)
    assert service.units["child"].state == "stale"
    assert not service.approval_valid("child")
    assert service.verify_ledger()
    assert RecoveryService.from_ledger(env, json.loads(json.dumps(service.to_ledger()))).verify_ledger()
