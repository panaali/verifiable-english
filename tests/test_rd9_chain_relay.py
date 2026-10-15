"""The readings route's chain is Lean's, relayed (review F25 of rd-9, DRI condition B1(d); DRI ruling R8).

Lean names the chain a completion took (`filled.chain`, `Readings.Chain.text`); Python reads it and checks only that
the completion fields present are that chain's, typed, and that the request declares the profiles the chain names. No
Python copy of Lean's chain derivation (`Compose.dispatch`, `chainOf`) decides which fields a row carries. The
acceptance test compares field presence and route with Lean's on all three chains (norms, soft, rights); a forged
chain is refused.
"""
from __future__ import annotations

import ast
import copy
import inspect

import pytest

from tests import lean_routes
from tests.test_readings_nd_lean import doc1, env1
from tests.test_readings_s1_lean import env_rights, r9_line, r9_right, rs9, run
from tests.test_readings_sd_lean import LEAN, doc4, env4, fsd1
from ve import readings_route
from ve.errors import CheckerUnavailable


@pytest.fixture(scope="module")
def lean():
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service has not been built")
    return LEAN


def _rights():
    raw = env_rights()
    return raw, {"units": [{"id": "u9"}], "reading_sets": [rs9(raw, r9_right([r9_line("strict")]))]}


def _norms():
    raw = env1()
    return raw, doc1(raw)[0]


def _soft():
    raw = env4()
    return raw, doc4(raw)


# chain -> (the requests (validate, elaborate), the chain Lean names, the routes Lean may take)
CHAINS = {"norms": ((_norms, _norms), "norms", ("superposed", "enumerated")),
          "soft": ((lambda: fsd1()[:2], _soft), "soft", ("enumerated",)),
          "rights": ((_rights, _rights), None, ("enumerated",))}


def _case(kind, raw, document):
    return {"id": kind, "kind": kind, "environment": raw, "document": document}


@pytest.fixture(scope="module")
def answers(lean):
    out = {}
    for name, (builds, _, _) in CHAINS.items():
        cases = [_case(kind, *build()) for kind, build in zip(("readings-validate", "readings-elaborate"), builds)]
        rows = run(lean, cases)
        assert [row["status"] for row in rows] == ["ok", "ok"], rows
        out[name] = list(zip(rows, cases))
    return out


def test_probe_f25_python_holds_no_copy_of_the_chain_derivation():
    """PROBE F25: `soft_chain` is gone, and no binder of the completion reads a chain's profile from the request to
    decide which fields a row carries."""
    assert not hasattr(readings_route, "soft_chain")
    source = inspect.getsource(readings_route)
    assert "def soft_chain" not in source
    tree = ast.parse(inspect.getsource(readings_route._bind_completion))
    literals = {node.value for node in ast.walk(tree) if isinstance(node, ast.Constant)}
    assert not literals & {"soft-norms@0", "rights@0"}


@pytest.mark.parametrize("chain", sorted(CHAINS))
def test_field_presence_and_route_are_leans_on_every_chain(answers, chain):
    """Acceptance: on each chain the relay accepts Lean's genuine rows, and the completion fields present are exactly
    those of the chain Lean names (none off the completion); the route is Lean's."""
    _, named, routes = CHAINS[chain]
    (validated, vcase), (elaborated, ecase) = answers[chain]
    for row in (validated, elaborated):
        assert (row["filled"]["chain"] if "filled" in row else None) == named
        assert set(readings_route._COMPLETION) & set(row) == readings_route.COMPLETION_FIELDS.get(named, set())
    assert elaborated["route"] in routes
    readings_route._check(copy.deepcopy(validated), vcase)
    if named is not None:
        assert readings_route._completion_elaborate(copy.deepcopy(elaborated), ecase)["route"] == elaborated["route"]


def test_the_rights_chain_beside_norm_defaults_is_leans_refusal(lean):
    """The rights chain keeps the abstention (rd-9-soft-chain.md 1.1): Lean refuses its content beside
    `norm-defaults@0`, so no rights chain is ever relayed under a completion."""
    raw, document = _rights()
    raw["profiles"] = sorted({*raw["profiles"], "norm-defaults@0"})
    [row] = run(lean, [_case("readings-validate", raw, document)])
    assert row["error"] == "UnsupportedProfile: readings@1 content with norm-defaults@0 is not implemented"


def _set_chain(value):
    return lambda row: row["filled"].__setitem__("chain", value)


FORGED = {
    "norms": {"named soft": _set_chain("soft"), "named rights": _set_chain("rights"), "retyped": _set_chain(7),
              "null": _set_chain(None), "dropped": lambda row: row["filled"].pop("chain"),
              "capitalised": _set_chain("Norms"), "soft fields added": lambda row: row.__setitem__(
                  "soft_premises", copy.deepcopy(row["fill_premises"])),
              "filled dropped": lambda row: row.pop("filled")},
    "soft": {"named norms": _set_chain("norms"), "named rights": _set_chain("rights"), "retyped": _set_chain(True),
             "dropped": lambda row: row["filled"].pop("chain"), "soft fields dropped": lambda row: row.pop(
                 "soft_premises"), "padded": _set_chain("soft ")},
}


@pytest.mark.parametrize("chain,name", [(c, n) for c, forged in FORGED.items() for n in sorted(forged)])
def test_a_forged_chain_is_refused(answers, chain, name):
    for row, case in answers[chain]:
        mutant = copy.deepcopy(row)
        FORGED[chain][name](mutant)
        relay = readings_route._check if case["kind"] == "readings-validate" else readings_route._completion_elaborate
        with pytest.raises(CheckerUnavailable):
            relay(mutant, case)


def test_a_chain_the_request_does_not_declare_is_refused(answers):
    """Binding (R8), two faults at once: a norms row renamed to the soft chain with soft fields to match names a
    profile (`soft-norms@0`) the request does not declare."""
    for row, case in answers["norms"]:
        mutant = copy.deepcopy(row)
        FORGED["norms"]["named soft"](mutant)
        FORGED["norms"]["soft fields added"](mutant)
        relay = readings_route._check if case["kind"] == "readings-validate" else readings_route._completion_elaborate
        with pytest.raises(CheckerUnavailable):
            relay(mutant, case)


# The completion's members as a group: its top-level fields and every pair's `gaps`.
def _drop(row, members):
    for key in members - {"gaps"}:
        row.pop(key, None)
    if "gaps" in members:
        for entry in row.get("sets", ()):
            for pair in entry["pairs"]:
                pair["pair"].pop("gaps", None)


def _members(row):
    present = set(readings_route._COMPLETION) & set(row)
    gaps = any("gaps" in p["pair"] for e in row.get("sets", ()) for p in e["pairs"])
    return sorted(present | ({"gaps"} if gaps else set()))


def _relay(case):
    return readings_route._check if case["kind"] == "readings-validate" else readings_route._completion_elaborate


@pytest.mark.parametrize("chain", ["norms", "soft"])
def test_probe_f29_a_row_without_the_requested_completion_is_refused(answers, chain):
    """PROBE F29: the request declares `norm-defaults@0` beside a content-bearing set, so a genuine row with its whole
    completion dropped (`filled`, `fill_premises`, `soft_premises` and every pair's `gaps`) is refused."""
    for row, case in answers[chain]:
        assert "norm-defaults@0" in case["environment"]["profiles"] and "filled" in row
        mutant = copy.deepcopy(row)
        _drop(mutant, {"filled", "fill_premises", "soft_premises", "gaps"})
        with pytest.raises(CheckerUnavailable):
            _relay(case)(mutant, case)


@pytest.mark.parametrize("chain", ["norms", "soft"])
def test_every_part_of_the_completion_dropped_is_refused(answers, chain):
    """The class of F29: the completion is present exactly when the request asks for it, so dropping any non-empty
    subset of its members (not only the whole) from a genuine row is refused."""
    from itertools import combinations
    assert any("gaps" in _members(row) for row, _ in answers[chain])
    for row, case in answers[chain]:
        members = _members(row)
        assert {"filled", "fill_premises"} <= set(members)
        for n in range(1, len(members) + 1):
            for subset in combinations(members, n):
                mutant = copy.deepcopy(row)
                _drop(mutant, set(subset))
                with pytest.raises(CheckerUnavailable):
                    _relay(case)(mutant, case)


@pytest.mark.parametrize("field", sorted(readings_route._COMPLETION))
def test_a_completion_the_request_does_not_ask_for_is_refused(answers, field):
    """The converse: the rights chain's request has no `norm-defaults@0`, so any completion member (one taken from a
    genuine soft row) added to its genuine row is refused."""
    donor = answers["soft"][0][0]
    for row, case in answers["rights"]:
        assert "norm-defaults@0" not in case["environment"]["profiles"]
        mutant = copy.deepcopy(row)
        mutant[field] = copy.deepcopy(donor[field])
        with pytest.raises(CheckerUnavailable):
            readings_route._check(mutant, case)


def test_a_completion_beside_no_content_bearing_set_is_refused(lean, answers):
    """The converse under `norm-defaults@0`: a document without content keeps W2's route and no completion (on
    validate and on elaborate's W2 branch alike), so a completion member added to its genuine row is refused."""
    raw, document = _norms()
    for r in document["reading_sets"][0]["readings"]:
        r["content"], r["kind"] = None, "norm"
    cases = [_case(kind, raw, document) for kind in ("readings-validate", "readings-elaborate")]
    rows = run(lean, cases)
    assert rows[1]["route"] == "w2" and not set(readings_route._COMPLETION) & (set(rows[0]) | set(rows[1]))
    donor = answers["soft"][0][0]
    for row, case in zip(rows, cases):
        _relay(case)(copy.deepcopy(row), case)
        for field in sorted(readings_route._COMPLETION):
            mutant = copy.deepcopy(row)
            mutant[field] = copy.deepcopy(donor[field])
            with pytest.raises(CheckerUnavailable):
                _relay(case)(mutant, case)
