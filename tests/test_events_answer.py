"""et-5: the `events@0` relay (`ve/events.py`) on genuine Lean answers, and fuzz tests of its binding.

Lean answers each source once (`genuine`); every mutant of the answer's events fields, one and two faults at a time
(each member dropped, emptied, retyped, duplicated, reordered; an index out of range; a bound label, name or date
rebound to another of the request; a label mangled outside Lean's grammar, in place or as an extra row beside its
genuine twin; the formulas are Lean's, so inside them only names and indices are mutated), is either
`CheckerUnavailable` or changes nothing the relay shows (plan ET-5)."""
from __future__ import annotations

import itertools
import random
import re
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
        assert list(shown.premises) == sorted(p["label"] for p in row["events_premises"])
        lean = {k: v for k, v in row["base_environment"]["vocabulary"]["constants"].items() if k.startswith("date__")}
        anchor = case["environment"]["events"]["anchor"]
        assert dict(shown.dates) == {k: (anchor if v["description"] == "the date of this document" else v["description"])
                                     for k, v in lean.items()}
    kinds = {label.split(":")[1] for label in events.answer(*reversed(genuine["rich"])).premises}
    assert kinds == {"irreflexive", "transitive", "linear", "date", "adjacent", "one_day", "one_begin", "one_end",
                     "not_before_begin", "link_forward", "link_weaker"}


def test_a_block_with_no_named_date_has_no_date_fact(lean_executable):
    """et-5b review F1: a block with no named date (no dates and no ISO anchor: the open anchor, spec 1.3) has no
    date fact. The relay required one fewer than none (-1) and refused every such genuine answer, so no open-anchor
    document reached the check's premise set."""
    kind, env, source = _fixture("u2-unspecified-default")
    env = _dated(env, ())
    del env["events"]["anchor"]
    shown = events.elaborate(layered.case(kind, env, source, "norm-defaults-elaborate"))
    assert set(shown.premises) == {"events:irreflexive", "events:transitive", "events:linear"} and not shown.dates


def test_the_relay_entry_asks_lean_and_binds(genuine):
    case, row = genuine["rich"]
    assert events.elaborate(case) == events.answer(row, case)


def test_a_deep_formula_is_walked_to_its_end(genuine):
    """A schema-valid formula 5,000 connectives deep is walked without recursion: an index out of range at its bottom
    is `CheckerUnavailable`, and the same chain with its index in range is bound."""
    case, row = genuine["plain"]
    for index, refused in ((1, True), (0, False)):
        mutant = deepcopy(row)
        chain = ["binary", "before", ["var", index], ["var", 0]]
        for _ in range(5_000):
            chain = ["not", chain]
        mutant["events_premises"][0]["ast"] = ["forall", "day", chain]
        if refused:
            with pytest.raises(CheckerUnavailable, match="not bound"):
                events.answer(mutant, case)
        else:
            assert events.answer(mutant, case).premises["events:irreflexive"] == ["forall", "day", chain]


def test_a_request_at_the_date_limit_with_many_links_is_bound(lean_executable):
    """64 consecutive named dates (Lean's limit) and twenty links over one sort pair: 63 date and 63 adjacency rows,
    100 weaker pairs; Lean answers within its limits and the binder binds every row."""
    kind, env, source = _fixture("u2-unspecified-default")
    days = [f"2026-{m:02d}-{d:02d}" for m, n in ((1, 31), (2, 28), (3, 31)) for d in range(1, n + 1)][:64]
    links = {f"link_{form}_{i}": (["act", "act"], form, "{0} contributed to {1}" if form == "contributed"
                                  else "{0} was necessary for {1}") for form in ("contributed", "necessary") for i in range(10)}
    env = rich_environment(env, days[:-1], links=links)
    env["events"]["anchor"] = days[-1]
    case = layered.case(kind, env, source, "norm-defaults-elaborate", open_terms=open_terms(env))
    shown = events.elaborate(case)
    assert len(shown.dates) == 64 and len(shown.premises) == 3 + 63 + 63 + 1 + 3 + 20 + 100


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

DEEP = [[]]
for _ in range(10_000):
    DEEP = [DEEP]


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


def _mangled(label):
    """`label` moved outside Lean's grammar (`events:` then the kind and names, joined by `:`): its prefix dropped or
    respelled, a segment added, emptied or padded. Each is a label no request names, so each is refused."""
    rest = label.removeprefix("events:")
    variants = (rest, "Events:" + rest, "events::" + rest, "events " + rest, " " + label, label + " ", label + ":",
                label + ":x", "x:" + label, label.replace(":", "::", 1), "events:" + rest.replace(":", "", 1))
    yield from dict.fromkeys(v for v in variants if v != label)


def _mutants(row, case):
    """(description, mutate) pairs over `events_premises` and the base environment's constants."""
    fields = (("events_premises",), ("base_environment", "vocabulary", "constants"))
    out = []
    for root in fields:
        for path, value in _nodes(_get(row, root), root):
            out.append((f"drop {path}", lambda r, p=path: _get(r, p[:-1]).pop(p[-1])))
            for other in (7, True, None, 1.5, "x", "\ud800", [], {}, DEEP):
                if type(other) is not type(value):
                    out.append((f"retype {path} {other!r}", lambda r, p=path, o=other: _set(r, p, o if o is DEEP else deepcopy(o))))
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
            if path[1:] and path[-1] == "label":
                for other in _mangled(value):
                    out.append((f"mangle {path} {other!r}", lambda r, p=path, o=other: _set(r, p, o)))
                    out.append((f"twin {path} {other!r}", lambda r, p=path, o=other: r["events_premises"].append(
                        {**r["events_premises"][p[1]], "label": o})))  # shallow: the mutant is a copy already
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
        except (KeyError, IndexError, TypeError, AttributeError, StopIteration):
            return None  # a second fault on a member the first removed or emptied: not a mutant
    try:
        return events.answer(mutant, case)
    except CheckerUnavailable:
        return "unavailable"


LEAN_CHOSEN = ("events:adjacent:", "events:link_weaker:")


def _lean_chosen(row, description):
    """A mutant that only drops or rebinds a row Lean chooses: which named dates are one day apart and which links
    are weaker are Lean's decisions (`calendarLabelled`, `weakerPairs`), so the relay names them and does not
    recompute them (R8, D1). Every other fault on those rows (retyped, emptied, duplicated, unnamed) is refused."""
    match = re.fullmatch(r"(?:drop \('events_premises', (\d+)\)|rebind \('events_premises', (\d+), 'label'\) .*)",
                         description)
    index = match and int(match[1] or match[2])
    return bool(match) and row["events_premises"][index]["label"].startswith(LEAN_CHOSEN)


@pytest.mark.parametrize("name", SOURCES)
def test_every_single_fault_mutant_is_unavailable_or_changes_nothing_shown(genuine, name):
    case, row = genuine[name]
    shown = events.answer(row, case)
    mutants = _mutants(row, case)
    assert len(mutants) > 200
    bad = [d for d, m in mutants if not _lean_chosen(row, d) and _outcome(row, case, [(d, m)]) not in
           ("unavailable", shown)]
    assert not bad, bad[:10]


@pytest.mark.parametrize("name", SOURCES)
def test_every_two_fault_mutant_is_unavailable_or_changes_nothing_shown(genuine, name):
    """A deterministic sample of 2,000 pairs: two faults may not cancel into an answer that shows something else
    than one of Lean's choices alone shows."""
    case, row = genuine[name]
    shown = events.answer(row, case)
    pairs = list(itertools.combinations(_mutants(row, case), 2))
    sample = random.Random(20261109).sample(pairs, min(len(pairs), 2000))
    bad = []
    for a, b in sample:
        chosen = [m for m in (a, b) if _lean_chosen(row, m[0])]
        if len(chosen) == 2:
            continue
        allowed = (None, "unavailable", shown, *(_outcome(row, case, [m]) for m in chosen))
        if _outcome(row, case, [a, b]) not in allowed:
            bad.append((a[0], b[0]))
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
    j = labels.index("events:one_day:act")
    refused(lambda r: r["events_premises"][i].update(label="events:date:2026-10-13:2026-10-12"), "do not chain")
    refused(lambda r: r["events_premises"][i].update(label="events:date:2026-10-12:2026-10-14"), "do not chain")
    refused(lambda r: r["events_premises"][i].update(label="events:date:2026-10-12:2026-10-15"), "names nothing")
    refused(lambda r: r["events_premises"].pop(i), "do not chain")
    # Which dates are one day apart and which links are weaker are Lean's (R8): only their names are bound.
    k = labels.index("events:adjacent:2026-10-12:2026-10-13")
    refused(lambda r: r["events_premises"][k].update(label="events:adjacent:2026-10-12:2026-10-14"), "names nothing")
    w = labels.index("events:link_weaker:necessary_for:contributed_to")
    refused(lambda r: r["events_premises"][w].update(label="events:link_weaker:contributed_to:necessary_for"),
            "names nothing")
    refused(lambda r: r["events_premises"][w].update(label="events:link_weaker:necessary_for:happens_on"),
            "names nothing")
    refused(lambda r: r["events_premises"][j].update(label="events:one_day:act:x"), "names nothing")
    # F1 (et-5 review): a label without Lean's `events:` prefix, as an extra row beside its genuine twin, of each kind
    # matched by pair (the date facts, the adjacent days, the weaker links) and of the kinds matched exactly.
    for genuine_label in ("events:date:2026-10-12:2026-10-13", "events:adjacent:2026-10-12:2026-10-13",
                          "events:link_weaker:necessary_for:contributed_to", "events:one_day:act", "events:linear"):
        for twin in _mangled(genuine_label):
            refused(lambda r, t=twin, g=genuine_label: r["events_premises"].append(
                {**deepcopy(r["events_premises"][labels.index(g)]), "label": t}), "names nothing")
    refused(lambda r: r["events_premises"].append(deepcopy(r["events_premises"][i])), "repeated")
    refused(lambda r: r["events_premises"].pop(j), "is missing")
    refused(lambda r: r["events_premises"][j].update(label="events:one_day:stay"), "names nothing")
    refused(lambda r: r["events_premises"][j].update(label="events:one_end:stay"), "repeated")
    refused(lambda r: _set(r, ("events_premises", j, "ast", 1), "nosuchsort"), "does not declare")
    refused(lambda r: _set(r, ("events_premises", 0, "ast", 2, 1, 2), ["var", 1]), "not bound")
    refused(lambda r: _set(r, ("events_premises", i, "ast", 2), ["const", "date__2026_10_15"]), "not bound")
    refused(lambda r: _set(r, ("events_premises", i, "ast", 1), "after"), "does not declare")


def test_a_request_not_of_the_block_s_shape_is_unavailable(genuine):
    """The request side is bound too: a block without links, dates or its day sort, links not a list, or a link
    row without its predicate is `CheckerUnavailable`, never a Python error."""
    case, row = genuine["rich"]
    block = ("environment", "events")
    for mutate in (lambda c: _get(c, block).pop("links"), lambda c: _get(c, block).pop("dates"),
                   lambda c: _get(c, block).pop("day"), lambda c: _set(c, (*block, "links"), 7),
                   lambda c: _get(c, block)["links"][0].pop("predicate"), lambda c: _set(c, (*block, "anchor"), 7),
                   lambda c: _get(c, ("environment", "vocabulary")).pop("constants")):
        mutant = deepcopy(case)
        mutate(mutant)
        with pytest.raises(CheckerUnavailable):
            events.answer(row, mutant)


def test_a_label_is_bound_only_as_lean_renders_it():
    """F1 (et-5 review), on the binder alone, with no Lean answer: the reviewer's probe, a twin without the `events:`
    prefix of each pair kind beside the genuine labels, is refused; the genuine labels are bound; a pair whose names
    hold a `:` is read only when exactly one split of it names the request (`_pair`)."""
    block = {"dates": ["2026-10-12", "2026-10-13"], "day": "day", "events": [], "states": [],
             "links": [{"predicate": "n", "form": "necessary"}, {"predicate": "c", "form": "contributed"}]}
    genuine = [*events.ORDER_LABELS, "events:link_forward:n", "events:link_forward:c", "events:link_weaker:n:c",
               "events:date:2026-10-12:2026-10-13", "events:adjacent:2026-10-12:2026-10-13"]
    assert events.ORDER_LABELS == tuple(events.label(k) for k in ("irreflexive", "transitive", "linear"))
    rows = lambda labels: [{"label": text, "ast": ["top"]} for text in labels]  # noqa: E731
    events._bind_labels(rows(genuine), block, block["dates"])
    for twin in ("date:2026-10-12:2026-10-13", "adjacent:2026-10-12:2026-10-13", "link_weaker:n:c"):
        with pytest.raises(CheckerUnavailable, match="names nothing"):
            events._bind_labels(rows([*genuine, twin]), block, block["dates"])
    assert events._pair("events:link_weaker:a:b", "link_weaker", {"a"}, {"b"}) == ("a", "b")
    assert events._pair("events:link_weaker:a:b:c", "link_weaker", {"a:b"}, {"c"}) == ("a:b", "c")
    assert events._pair("events:link_weaker:a:b:c", "link_weaker", {"a", "a:b"}, {"b:c", "c"}) is None
    assert events._pair("link_weaker:a:b", "link_weaker", {"a"}, {"b"}) is None
    assert events._pair("events:link_weaker:a:a", "link_weaker", {"a"}, {"a"}) is None
    assert events._pair("events:date:a:b", "link_weaker", {"a"}, {"b"}) is None
