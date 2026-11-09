"""et-5: the `events@0` relay (`ve/events.py`) on genuine Lean answers, and fuzz tests of its binding.

Lean answers each source once (`genuine`); every mutant of the answer's events fields, one and two faults at a time
(each member dropped, emptied, retyped, duplicated, reordered; an index out of range; a bound label, name or date
rebound to another of the request; the formulas are Lean's, so inside them only names and indices are mutated), is either `CheckerUnavailable` or changes nothing the relay shows (plan ET-5)."""
from __future__ import annotations

import itertools
import random
from copy import deepcopy

import pytest

from conformance import norm_defaults_layered as layered
from tests.test_events_route import _dated, _fixture
from tests.test_norm_defaults_three_way import lean_executable  # noqa: F401  (the route fixture)
from ve import events
from ve import norm_defaults_route as route
from ve.errors import CheckerUnavailable

ROLES = {"happens_on": (["act", "day"], "{0} happens on {1}"), "stay_begins": (["stay", "day"], "{0} begins on {1}"),
         "stay_ends": (["stay", "day"], "{0} ends on {1}")}
LINKS = {"contributed_to": (["act", "act"], "contributed", "{0} contributed to {1}"),
         "necessary_for": (["act", "act"], "necessary", "{0} was necessary for {1}"),
         "contributed_to_stay": (["act", "stay"], "contributed", "{0} contributed to {1}")}


def rich_environment(env, dates=("2026-10-12", "2026-10-13"), roles=ROLES, links=LINKS):
    """`env` with an event sort, a state sort and links over them, and adjacent named dates."""
    env = _dated(env, dates)
    vocabulary = env["vocabulary"]
    vocabulary["sorts"].update(act={"description": "an act"}, stay={"description": "a stay"})
    for name, (arguments, wording) in roles.items():
        vocabulary["predicates"][name] = {"arguments": arguments, "description": name, "verbalisation": wording}
    for name, (arguments, _, wording) in links.items():
        vocabulary["predicates"][name] = {"arguments": arguments, "description": name, "verbalisation": wording}
    env["events"].update(
        anchor="2026-10-14", events=[{"sort": "act", "on": "happens_on"}],
        states=[{"sort": "stay", "begins": "stay_begins", "ends": "stay_ends"}],
        links=[{"predicate": name, "form": form, "decided_by": "unstated"} for name, (_, form, _) in links.items()])
    return env


def open_terms(env):
    return [{"name": link["predicate"], "decided_by": link["decided_by"]} for link in env["events"]["links"]]


def plain_case(name="u2-unspecified-default"):
    kind, env, source = _fixture(name)
    return layered.case(kind, _dated(env), source, "norm-defaults-elaborate")


def rich_case(name="u2-unspecified-default"):
    kind, env, source = _fixture(name)
    env = rich_environment(env)
    return layered.case(kind, env, source, "norm-defaults-elaborate", open_terms=open_terms(env))


SOURCES = {"plain": plain_case, "rich": rich_case, "rich-u9": lambda: rich_case("u9-unspecified")}


@pytest.fixture(scope="module")
def genuine(lean_executable):
    """Each source's case and Lean's answer to it, asked once."""
    cases = {name: build() for name, build in SOURCES.items()}
    answers = route.run_cases(list(cases.values()))
    return {name: (case, row) for (name, case), row in zip(cases.items(), answers)}


def test_genuine_answers_are_relayed_with_every_kind_of_label(genuine):
    """The relay shows Lean's premises by label and one date constant per named date; the rich source has every
    label kind (adjacent dates, a state, a weaker link pair)."""
    for name, (case, row) in genuine.items():
        assert row["status"] == "ok", (name, row)
        shown = events.answer(row, case)
        assert list(shown.premises) == [p["label"] for p in row["events_premises"]]
        block = case["environment"]["events"]
        assert dict(shown.dates) == {events.constant(d): d for d in (*block["dates"], block["anchor"])}
    kinds = {label.split(":")[1] for label in events.answer(*reversed(genuine["rich"])).premises}
    assert kinds == {"irreflexive", "transitive", "linear", "date", "adjacent", "one_day", "one_begin", "one_end",
                     "not_before_begin", "link_forward", "link_weaker"}


def test_the_relay_entry_asks_lean_and_binds(genuine):
    case, row = genuine["rich"]
    assert events.elaborate(case) == events.answer(row, case)


def test_an_answer_bound_to_another_request_is_unavailable(genuine):
    """Another request's genuine answer names dates, sorts and links this request does not have."""
    (plain, plain_row), (rich, rich_row) = genuine["plain"], genuine["rich"]
    for row, case in ((plain_row, rich), (rich_row, plain)):
        with pytest.raises(CheckerUnavailable):
            events.answer(row, case)


def test_a_request_without_the_block_is_not_an_events_request(genuine):
    case, row = genuine["plain"]
    bare = deepcopy(case)
    del bare["environment"]["events"]
    with pytest.raises(CheckerUnavailable, match="no events block"):
        events.answer(row, bare)


# The fuzzer: every node under the relayed fields, and its mutants.

def _nodes(value, path=()):
    yield path, value
    if isinstance(value, dict):
        for key, item in value.items():
            yield from _nodes(item, (*path, key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _nodes(item, (*path, index))


def _set(row, path, value):
    target = row
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value


def _get(row, path):
    for key in path:
        row = row[key]
    return row


def _rebound(value, case):
    """`value` renamed to another name of the request of its own kind (a date, a sort, a link, a constant)."""
    block = case["environment"]["events"]
    names = [*block["dates"], block["anchor"], "act", "stay", *(link["predicate"] for link in block["links"]),
             *(events.constant(d) for d in (*block["dates"], block["anchor"])), "day"]
    for name in names:
        if name in value:
            for other in names:
                if other != name and other not in value:
                    yield value.replace(name, other, 1)


def _mutants(row, case):
    """(description, mutate) pairs over `events_premises` and the base environment's constants."""
    fields = (("events_premises",), ("base_environment", "vocabulary", "constants"))
    out = []
    for root in fields:
        for path, value in _nodes(_get(row, root), root):
            out.append((f"drop {path}", lambda r, p=path: _get(r, p[:-1]).pop(p[-1])))
            for other in (7, True, None, "x", [], {}):
                if type(other) is not type(value):
                    out.append((f"retype {path} {other!r}", lambda r, p=path, o=other: _set(r, p, deepcopy(o))))
            if isinstance(value, (str, list, dict)) and value and path != root:
                out.append((f"empty {path}", lambda r, p=path, v=value: _set(r, p, type(v)())))
            if isinstance(value, list) and value:
                out.append((f"duplicate in {path}", lambda r, p=path: _get(r, p).append(deepcopy(_get(r, p)[0]))))
                out.append((f"reorder {path}", lambda r, p=path: _get(r, p).reverse()))
            if isinstance(value, dict) and value:
                out.append((f"reorder {path}", lambda r, p=path: _reorder(_get(r, p))))
                out.append((f"duplicate in {path}", lambda r, p=path: _duplicate(_get(r, p))))
            if type(value) is int and path != root:
                out.append((f"index out of range {path}", lambda r, p=path, v=value: _set(r, p, v + 64)))
            if type(value) is str and "ast" not in path:  # the formulas are Lean's; only their names are bound
                for other in _rebound(value, case):
                    out.append((f"rebind {path} {other}", lambda r, p=path, o=other: _set(r, p, o)))
            if path and isinstance(path[-1], str) and path[:-1] == fields[1]:
                for other in _rebound(path[-1], case):
                    out.append((f"rename {path} {other}", lambda r, p=path, o=other: _rename(_get(r, p[:-1]), p[-1], o)))
    return out


def _reorder(mapping):
    items = list(mapping.items())[::-1]
    mapping.clear()
    mapping.update(items)


def _duplicate(mapping):
    key = next(iter(mapping))
    mapping[key + "_copy"] = deepcopy(mapping[key])


def _rename(mapping, key, other):
    mapping[other] = mapping.pop(key)


def _outcome(row, case, mutations):
    mutant = deepcopy(row)
    for _, mutate in mutations:
        try:
            mutate(mutant)
        except (KeyError, IndexError, TypeError, AttributeError):
            return None  # a second fault on a member the first removed: not a mutant
    try:
        return events.answer(mutant, case)
    except CheckerUnavailable:
        return "unavailable"


@pytest.mark.parametrize("name", SOURCES)
def test_every_single_fault_mutant_is_unavailable_or_changes_nothing_shown(genuine, name):
    case, row = genuine[name]
    shown = events.answer(row, case)
    mutants = _mutants(row, case)
    assert len(mutants) > 200
    bad = [d for d, m in mutants if _outcome(row, case, [(d, m)]) not in ("unavailable", shown)]
    assert not bad, bad[:10]


@pytest.mark.parametrize("name", SOURCES)
def test_every_two_fault_mutant_is_unavailable_or_changes_nothing_shown(genuine, name):
    """A deterministic sample of pairs: two faults may not cancel into an answer that shows something else."""
    case, row = genuine[name]
    shown = events.answer(row, case)
    pairs = list(itertools.combinations(_mutants(row, case), 2))
    sample = random.Random(20261109).sample(pairs, min(len(pairs), 4000))
    bad = [(a[0], b[0]) for a, b in sample if _outcome(row, case, [a, b]) not in (None, "unavailable", shown)]
    assert not bad, bad[:10]


def test_named_binding_faults_are_unavailable(genuine):
    """One fixture per binding relation of `ve/events.py`, each refused with its reason."""
    case, row = genuine["rich"]
    labels = [p["label"] for p in row["events_premises"]]

    def refused(mutate, reason):
        mutant = deepcopy(row)
        mutate(mutant)
        with pytest.raises(CheckerUnavailable, match=reason):
            events.answer(mutant, case)

    constants = ("base_environment", "vocabulary", "constants")
    refused(lambda r: _get(r, constants).pop("date__2026_10_13"), "one per named date")
    refused(lambda r: _get(r, constants).update(date__2026_10_15={"sort": "day", "description": "2026-10-15"}),
            "one per named date")
    refused(lambda r: _get(r, constants)["date__2026_10_13"].update(sort="act"), "day sort")
    refused(lambda r: _get(r, constants)["date__2026_10_13"].update(description="2026-10-12"), "day sort")
    i = labels.index("events:date:2026-10-12:2026-10-13")
    refused(lambda r: r["events_premises"][i].update(label="events:date:2026-10-13:2026-10-12"), "names nothing")
    refused(lambda r: r["events_premises"][i].update(label="events:date:2026-10-12:2026-10-14"), "names nothing")
    refused(lambda r: r["events_premises"].pop(i), "is missing")
    # The fuzzer's two survivors before `_labels` bound them: which dates are adjacent, which links are weaker.
    k = labels.index("events:adjacent:2026-10-12:2026-10-13")
    refused(lambda r: r["events_premises"].pop(k), "is missing")
    refused(lambda r: r["events_premises"][k].update(label="events:adjacent:2026-10-12:2026-10-14"), "names nothing")
    w = labels.index("events:link_weaker:necessary_for:contributed_to")
    refused(lambda r: r["events_premises"].pop(w), "is missing")
    refused(lambda r: r["events_premises"][w].update(label="events:link_weaker:necessary_for:contributed_to_stay"),
            "names nothing")
    refused(lambda r: r["events_premises"].append(deepcopy(r["events_premises"][i])), "repeated")
    j = labels.index("events:one_day:act")
    refused(lambda r: r["events_premises"][j].update(label="events:one_day:stay"), "names nothing")
    refused(lambda r: r["events_premises"][j].update(label="events:one_end:stay"), "repeated")
    refused(lambda r: _set(r, ("events_premises", j, "ast", 1), "nosuchsort"), "does not declare")
    refused(lambda r: _set(r, ("events_premises", 0, "ast", 2, 1, 2), ["var", 1]), "not bound")
    refused(lambda r: _set(r, ("events_premises", i, "ast", 2), ["const", "date__2026_10_15"]), "not bound")
    refused(lambda r: _set(r, ("events_premises", i, "ast", 1), "after"), "does not declare")
