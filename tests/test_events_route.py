"""et-4b: an `events` document through the service's norm-defaults mode, on both layered branches.

Lean owns the route; `lean/VE/Events/RouteExamples.lean` pins the row, the block's faults, the limits and the kinds.
Here the certificate of the accepting replay comes from the untrusted prover (`prove_entailment`): Lean has no producer,
and Python has no model of `events@0` until et-5, so the prover reads the environment Lean's route decodes (no block,
the date constants declared), with the premises Lean's elaboration gives. The answer's schema is fuzzed as the relay
checks it. The relay's binding of the fields is et-5's (`ve/events.py`).
"""
from __future__ import annotations

from copy import deepcopy

import pytest

from conformance import norm_defaults_layered as layered
from tests.test_norm_defaults_three_way import lean_executable  # noqa: F401  (the route fixture)
from ve import norm_defaults_route as route
from ve.ast import Binary, Bottom, Const, Top, formula_from_data, formula_to_data
from ve.backends.service_schema import Invalid, check_row
from ve.entailment import prove_entailment
from ve.wire import digest

DAYS = ("2026-09-21", "2026-09-27")
ANCHOR = "2026-10-12"


def _constant(iso):
    return "date__" + iso.replace("-", "_")


def _fixture(name):
    return next((kind, env, source) for n, kind, env, source, _ in layered.fixtures() if n == name)


def _declared(env):
    """The fixture's environment with the day sort and `before`: what any block's vocabulary declares."""
    env = deepcopy(env)
    vocabulary = env["vocabulary"]
    vocabulary["sorts"]["day"] = {"description": "a day"}
    vocabulary["predicates"]["before"] = {"arguments": ["day", "day"], "description": "before",
                                          "verbalisation": "{0} is before {1}"}
    return env


def _dated(env, dates=DAYS):
    """The environment as a request carries it: the block and the profile."""
    env = _declared(env)
    env["profiles"] = sorted([*env["profiles"], "events@0"])
    env["events"] = {"day": "day", "before": "before", "events": [], "states": [], "dates": list(dates),
                     "anchor": ANCHOR, "links": []}
    return env


def _view(env):
    """What Lean's route decodes: no block, no profile, one constant per named date."""
    view = _declared(env)
    for iso in (*DAYS, ANCHOR):
        wording = "the date of this document" if iso == ANCHOR else iso
        view["vocabulary"]["constants"][_constant(iso)] = {"sort": "day", "description": wording}
    return view


def _elaborate(kind, env, source):
    (row,) = route.run_cases([layered.case(kind, env, source, "norm-defaults-elaborate")])
    assert row["status"] == "ok", row
    return row


def _proved():
    """`before(first, anchor)` on `u2`, from the block's premises, proved over the view and bound as written."""
    kind, env, source = _fixture("u2-unspecified-default")
    dated, row = _dated(env), None
    row = _elaborate(kind, dated, source)
    doc = layered.document(kind, _view(env), source)
    filled = doc.filled.env
    regenerated = [formula_from_data(filled, p["ast"], _generated=True)
                   for p in (*row["soft"], *row["events_premises"])]
    regenerated += [f for _, f in doc.fill_premises] + [f for _, f in doc.filled.premises()]
    conclusion = Binary("before", Const(_constant(DAYS[0])), Const(_constant(ANCHOR)))
    proof = prove_entailment(filled, tuple(regenerated), conclusion)
    assert proof.status == "Found", proof.status
    version = "v0.2:" + ",".join(dated["profiles"])
    meaning = lambda ast: digest(f"ve-meaning-{version}\n", {"environment_id": row["environment_id"], "ast": ast})
    asts = [p["ast"] for key in ("background", "soft", "events_premises", "fill", "premises") for p in row[key]]
    conclusion_ast = formula_to_data(filled, conclusion)
    certificate = {**proof.certificate, "environment_id": row["environment_id"],
                   "premise_meaning_ids": [meaning(a) for a in asts], "conclusion_meaning_id": meaning(conclusion_ast)}
    case = layered.case(kind, dated, source, "norm-defaults-certificate", premises=[], conclusion=conclusion_ast,
                        certificate=certificate)
    return case, meaning, asts


def _swapped(ast):
    """`before(b, a)` for `before(a, b)`: the anchor is not before the first date."""
    tag, predicate, left, right = ast
    return [tag, predicate, right, left]


def test_a_certificate_over_the_block_replays_and_a_changed_block_is_stale(lean_executable):
    """`replayEventsEntailment` accepts the prover's certificate. Every premise of the pack is bound, so a certificate
    without one, for another conclusion or against a changed block, is stale; nothing else about it changes."""
    case, meaning, asts = _proved()
    (row,) = route.run_cases([case])
    assert row["status"] == "ok" and row["valid"] is True, row
    assert row["premises"] == len(asts)

    stale = "certificate is stale or bound to different inputs"
    dated = deepcopy(case)
    dated["environment"]["events"]["dates"].append("2026-09-30")
    missing = deepcopy(case)
    missing["certificate"]["premise_meaning_ids"].pop(0)
    other = deepcopy(case)
    other["conclusion"] = _swapped(case["conclusion"])
    for bad in (dated, missing, other):
        (row,) = route.run_cases([bad])
        assert row == {"id": "norm-defaults-certificate", "status": "error", "error": stale}, row

    moved = deepcopy(case)
    moved["environment"]["events"]["anchor"] = "2026-10-13"
    (row,) = route.run_cases([moved])
    assert row["error"] == "ill-typed or unbound conclusion", row  # the old anchor's constant is gone with the block


def test_a_certificate_rebound_to_a_false_conclusion_does_not_close(lean_executable):
    """The opposite side of the replay: bound to the swapped conclusion the proof does not close, so `valid` is false."""
    case, meaning, _ = _proved()
    flipped = deepcopy(case)
    flipped["conclusion"] = _swapped(case["conclusion"])
    flipped["certificate"]["conclusion_meaning_id"] = meaning(flipped["conclusion"])
    (row,) = route.run_cases([flipped])
    assert row["status"] == "ok" and row["valid"] is False, row


def _listed(env):
    """The profile without the block: the route decodes the list without `events@0`, with no pack (spec 1.1, 1.11)."""
    env = _declared(env)
    env["profiles"] = sorted([*env["profiles"], "events@0"])
    return env


def _unblocked(env, conclusion=Top()):
    """A prover certificate for `conclusion` from the regenerated premises of `u2` under `env`, bound as written."""
    kind, base, source = _fixture("u2-unspecified-default")
    row = _elaborate(kind, env, source)
    doc = layered.document(kind, _declared(base), source)
    filled = doc.filled.env
    regenerated = [formula_from_data(filled, p["ast"], _generated=True) for p in row["soft"]]
    regenerated += [f for _, f in doc.fill_premises] + [f for _, f in doc.filled.premises()]
    proof = prove_entailment(filled, tuple(regenerated), conclusion)
    assert proof.status == "Found", proof.status
    version = "v0.2:" + ",".join(env["profiles"])
    meaning = lambda ast: digest(f"ve-meaning-{version}\n", {"environment_id": row["environment_id"], "ast": ast})
    asts = [p["ast"] for key in ("background", "soft", "fill", "premises") for p in row[key]]
    conclusion_ast = formula_to_data(filled, conclusion)
    certificate = {**proof.certificate, "environment_id": row["environment_id"],
                   "premise_meaning_ids": [meaning(a) for a in asts], "conclusion_meaning_id": meaning(conclusion_ast)}
    case = layered.case(kind, env, source, "norm-defaults-certificate", premises=[], conclusion=conclusion_ast,
                        certificate=certificate)
    return case, meaning, asts


def test_a_certificate_listing_the_profile_without_the_block_replays_as_the_list_without_it(lean_executable):
    """F1 (et-4b review): `replayUnblockedEntailment`. Without a block the profile adds no pack, so a certificate over
    soft's premises replays as on the list without `events@0`, bound to the list as written; it is never refused."""
    _, base, _ = _fixture("u2-unspecified-default")
    listed, bare = _listed(base), _declared(base)
    assert "events" not in listed and "events@0" in listed["profiles"]
    case, meaning, asts = _unblocked(listed)
    (row,) = route.run_cases([case])
    check_row("norm-defaults", row, case, 0)
    assert row["status"] == "ok" and row["valid"] is True, row
    assert row["premises"] == len(asts)

    plain, _, _ = _unblocked(bare)
    (plain_row,) = route.run_cases([plain])
    assert plain_row == row, plain_row

    stale = {"id": "norm-defaults-certificate", "status": "error", "error": "certificate is stale or bound to different inputs"}
    for other in ({**case, "certificate": plain["certificate"]}, {**plain, "certificate": case["certificate"]}):
        (other_row,) = route.run_cases([other])
        assert other_row == stale, other_row

    false = deepcopy(case)
    false["conclusion"] = formula_to_data(layered.document("soft", bare, case["norms"]).filled.env, Bottom())
    false["certificate"]["conclusion_meaning_id"] = meaning(false["conclusion"])
    (false_row,) = route.run_cases([false])
    assert false_row["status"] == "ok" and false_row["valid"] is False, false_row


@pytest.mark.parametrize("name", ["u2-unspecified-default", "u9-unspecified"])
def test_the_pack_is_last_and_the_rest_of_the_answer_is_the_list_without_it(lean_executable, name):
    """`events_row_composition` on both branches: the pack's rows are new, the base environment gains the dates and
    nothing else, the other packs' rows are the block-less answer's, and the identity is the bytes as written."""
    kind, env, source = _fixture(name)
    bare = _elaborate(kind, _declared(env), source)
    row = _elaborate(kind, _dated(env), source)
    labels = [p["label"] for p in row["events_premises"]]
    assert labels[:3] == ["events:irreflexive", "events:transitive", "events:linear"]
    assert labels[3:] == [f"events:date:{a}:{b}" for a, b in zip((*DAYS, ), (*DAYS[1:], ANCHOR))]
    for key in ("soft", "rights", "premises", "fill"):
        assert row[key] == bare[key], key
    assert "events_premises" not in bare
    assert row["environment_id"] != bare["environment_id"] and row["document_hash"] != bare["document_hash"]
    constants = row["base_environment"]["vocabulary"]["constants"]
    assert {_constant(d) for d in (*DAYS, ANCHOR)} <= set(constants)
    assert "events" not in row["base_environment"] and "events@0" not in row["base_environment"]["profiles"]
    other = _elaborate(kind, _dated(env, DAYS[:1]), source)
    assert other["environment_id"] != row["environment_id"]


@pytest.mark.parametrize("value", [7, True, None, "x", {}, [7], [{}], [{"label": "l"}], [{"label": 7, "ast": ["top"]}],
                                   [{"label": "l", "ast": ["top"], "extra": 1}]])
def test_a_retyped_events_premises_row_is_refused(lean_executable, value):
    """The new field is fully typed: every retyping fails the answer's schema; the genuine row and an empty list pass."""
    kind, env, source = _fixture("u2-unspecified-default")
    case = layered.case(kind, _dated(env), source, "norm-defaults-elaborate")
    (row,) = route.run_cases([case])
    check_row("norm-defaults", row, case, 0)
    with pytest.raises(Invalid):
        check_row("norm-defaults", {**row, "events_premises": value}, case, 0)
