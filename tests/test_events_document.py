"""et-5b: an `events@0` document through Lean's `document` mode (docs/spec/events-time-causation.md 1.3, 2.9, 4; DRI
2026-11-10 item 1). Lean decides every answer here; these tests read it through the one relay entry. Each 2.9 item's
document is a `#guard` of lean/VE/Service/EventsDocumentExamples.lean; this file checks that the relayed answer is
Lean's, end to end, that a malformed block raises only a `VEError`, and the date limit's boundary."""
from __future__ import annotations

import copy
import json

import pytest

from ve.backends.relay import answer
from ve.errors import CheckerUnavailable, ResourceLimit, VEError

LISTED = ["events@0", "norm-defaults@0", "norms@0", "relational-fol@0", "soft-norms@0"]
REGULATED = {"default": "unspecified", "act": "{0} x"}
ENVIRONMENT = {
    "language": "ve.core@0.2", "profiles": LISTED, "spec_revision": "ve-v0.2-expand2-2026-09-25",
    "vocabulary": {
        "sorts": {"claude_instance": {"description": "Claude"}, "day": {"description": "a day"}},
        "constants": {"date_of_this_document": {"sort": "day", "description": "the date of this document"}},
        "predicates": {
            "before": {"arguments": ["day", "day"], "description": "before", "verbalisation": "{0} is before {1}"},
            "x_required": {"arguments": ["claude_instance"], "description": "x",
                           "regulated": {**REGULATED, "role": "obligation", "permission": "x_permitted"}},
            "x_permitted": {"arguments": ["claude_instance"], "description": "may x",
                            "regulated": {**REGULATED, "default": "allow", "role": "permission"}}}},
    "events": {"day": "day", "before": "before", "events": [], "states": [], "dates": [], "links": []}}
RULE = {"norm": {"name": "r", "predicate": "x_required", "sign": True, "mode": "default", "guard": ["top"],
                 "unless": [], "over": [], "exception": {"decided_by": "unstated", "necessary": [], "sufficient": [],
                                                         "factors": []}}}


def reading_set(rid):
    admission = {"who": "translator", "why": "the source word", "distinguishing_models": {}}
    return {"id": "rs", "unit": "u1", "version": 1, "status": "authored", "signature": "author",
            "readings": [{"id": rid, "kind": "asserted", "meaning_id": "pending", "content": None,
                          "admission": admission}]}


def front(environment=None, **members):
    unit = {"id": "u1", "span": [0, 1], "kind": "norm", "meaning": "specified", "support": "assumption",
            "content": RULE}
    return {"format": "ve-document@1", "environment": copy.deepcopy(environment or ENVIRONMENT), "units": [unit],
            **members}


def checked(document):
    """Lean's `document` row and error for one document: the relay's answer, as `ve document check` reads it."""
    return answer("document", {"id": "d", "document": "---\n" + json.dumps(document) + "\n---\nx", "admit": True})


def edited(change):
    document = front()
    change(document["environment"])
    return document


def test_an_events_document_is_checked_where_it_was_unavailable():
    """DELTA row 1: the open-anchor document is CHECKED, as is a dated one; before et-5b both were refused before
    decoding (`undecided`: here the environment's own fault, `fields do not match: ... got [events, ...]`)."""
    row, error = checked(front())
    assert error is None and [(u["id"], u["status"]) for u in row["units"]] == [("u1", "CHECKED")]

    def dated(e):
        del e["vocabulary"]["constants"]["date_of_this_document"]
        e["events"].update(dates=["2026-10-12"], anchor="2026-10-13")
    row, error = checked(edited(dated))
    assert error is None and [u["status"] for u in row["units"]] == ["CHECKED"]


def test_a_list_off_the_soft_chain_stays_unavailable():
    """The other direction: off the soft chain the base's refusal stands, by the base's own expression (`undecided`:
    the environment's own fault, Python's `Environment`'s, before `document checks under events@0 need ...`)."""
    def plain(e):
        e["profiles"] = ["events@0", "norm-defaults@0", "norms@0", "relational-fol@0"]
    _, error = checked(edited(plain))
    assert str(error) == ("fields do not match: expected [language, profiles, spec_revision, vocabulary], got [events, "
                          "language, profiles, spec_revision, vocabulary]")

    def bare(e):
        plain(e)
        del e["events"]
    _, error = checked(edited(bare))
    assert str(error) == "UnsupportedProfile: Unsupported profile events@0"

    # With rights@0 (DRI 2026-11-10 et-5b item 1), with its block and without.
    def rights(e):
        e["profiles"] = ["events@0", "norm-defaults@0", "norms@0", "relational-fol@0", "rights@0", "soft-norms@0"]
    for change in (rights, lambda e: (rights(e), e.pop("events"))):
        _, error = checked(edited(change))
        assert isinstance(error, CheckerUnavailable)
        assert str(error) == "CheckerUnavailable: document checks under events@0 need its Lean profile route"


def _set(path, value):
    def change(e):
        target = e
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
    return change


@pytest.mark.parametrize(("change", "text"), [
    (_set(("profiles",), ["events@0", "norms@0", "relational-fol@0", "soft-norms@0"]),
     "UnsupportedProfile: events@0 requires norm-defaults@0"),
    (_set(("events", "extra"), 1), "InvalidInput: events.extra"),
    (_set(("events", "day"), "days"), "EventsSort: days"),
    (_set(("events", "dates"), ["nonsense"]), "InvalidDate(nonsense)"),
    (_set(("events", "anchor"), "2026-10-13"), "AnchorNotOpen: date_of_this_document"),
    (_set(("vocabulary", "constants", "date_of_this_document", "sort"), "claude_instance"),
     "AnchorNotOpen: date_of_this_document"),
], ids=["item-1", "item-2", "item-3", "item-6", "item-8-anchor", "item-8-sort"])
def test_a_broken_2_9_check_gets_its_diagnostic_on_the_document_route(change, text):
    _, error = checked(edited(change))
    assert isinstance(error, VEError) and not isinstance(error, CheckerUnavailable)
    assert str(error) == text


@pytest.mark.parametrize(("rid", "text"), [("A2", "AnchorOpen: A2"), ("E2", "AnchorOpen: E2"), ("A1", None)])
def test_an_anchor_dependent_reading_is_refused_while_the_anchor_is_open(rid, text):
    _, error = checked(front(reading_sets=[reading_set(rid)]))
    assert (str(error) if error else None) == text


def test_an_unopened_link_is_refused_and_an_opened_one_is_checked():
    def linked(e):
        e["vocabulary"]["sorts"]["act"] = {"description": "an act"}
        e["vocabulary"]["predicates"].update(
            on={"arguments": ["act", "day"], "description": "on", "verbalisation": "{0} happens on {1}"},
            led_to={"arguments": ["act", "act"], "description": "led", "verbalisation": "{0} contributed to {1}"})
        e["events"]["events"] = [{"sort": "act", "on": "on"}]
        e["events"]["links"] = [{"predicate": "led_to", "form": "contributed", "decided_by": "drafters"}]
    document = edited(linked)
    assert str(checked(document)[1]) == "LinkNotOpen: led_to"
    term = {"name": "led_to", "arguments": ["x", "y"], "decided_by": "drafters", "necessary": [], "sufficient": [],
            "factors": [], "precedents": [], "jurisdiction": "drafting", "version": 1}
    assert checked({**document, "open_terms": [term]})[1] is None


def test_the_dates_are_charged_at_their_limit():
    """A large well-formed block, 64 dates, is checked; 65 is Lean's `ResourceLimit`, never a partial answer."""
    days = [f"2026-{m:02d}-{d:02d}" for m in range(1, 4) for d in range(1, 29)]

    def dates(n):
        return _set(("events", "dates"), days[:n])
    assert checked(edited(dates(64)))[1] is None
    _, error = checked(edited(dates(65)))
    assert isinstance(error, ResourceLimit) and str(error) == "ResourceLimit: events dates"


@pytest.mark.parametrize("key", ["day", "before", "events", "states", "dates", "links", "anchor"])
@pytest.mark.parametrize("value", [7, True, None, [], {}, 1.5, "\ud800"],
                         ids=["int", "bool", "null", "list", "object", "float", "surrogate"])
def test_only_a_ve_error_escapes_a_malformed_block_member(key, value):
    """A null or a non-natural number is outside the document mode's JSON reader in any front matter (unavailable, as
    before et-5b); every other value is Lean's diagnostic, or an answer."""
    _, error = checked(edited(_set(("events", key), value)))
    if value == "\ud800":
        assert isinstance(error, VEError) and str(error) == "JSON strings must not contain lone UTF-16 surrogates"
    elif value is None or type(value) is float:
        assert isinstance(error, CheckerUnavailable)
        assert str(error).startswith("CheckerUnavailable: front matter outside the document mode's JSON reader")
    elif value == [] and key in ("events", "states", "dates", "links"):
        assert error is None  # an empty list is the block's own, legitimately empty value
    else:
        assert isinstance(error, VEError) and not isinstance(error, CheckerUnavailable), error
        assert str(error).startswith(("InvalidInput: events", "EventsSort: ", "DateRange(", "InvalidDate(")), error
