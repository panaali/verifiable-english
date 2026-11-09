"""The `events@0` relay: Lean's answer about an events document, bound to the request (events-time-causation plan
ET-5; spec 1.3, 1.4 and 6.3).

Lean owns the block, the premises it generates, their labels and formulas, and every verdict (`VE.Events`); this
module decides nothing (R8). It relays the fields et-4 and et-4b report on the norm-defaults route's elaboration of
an events document, `events_premises` and the date constants of `base_environment`, after two checks: the row fits
its generated schema, and every date, label and link the answer names exists in the request, once, with no extra row
and none missing. Anything else is `CheckerUnavailable`.

The bindings, a closed list of relations to the request's block (dates with the anchor, event and state sorts, links):

- `base_environment.vocabulary.constants`: the request's constants as written, plus exactly one constant
  `date__YYYY_MM_DD` per named date, of the block's day sort, described by its own ISO date (the anchor's description
  is Lean's wording, spec 1.3, and is not shown).
- `events_premises[].label`: each once, and exactly the labels the block names (spec 1.4, `_labels`): the three
  order axioms; `events:date:A:B` per pair of consecutive named dates and `events:adjacent:A:B` per such pair one day
  apart; `events:one_day:<s>` per event sort; `events:one_begin:<s>`, `events:one_end:<s>` and
  `events:not_before_begin:<s>` per state sort; `events:link_forward:<p>` per link; `events:link_weaker:<n>:<c>` per
  necessary link `n` and contributed link `c` over the same declared sorts.
  Each formula is Lean's, typed by the schema (`generated_formula`); every sort, predicate and constant it names is
  the request's (the constants those of the bound base environment), and every variable index is under a binder.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from types import MappingProxyType

from .backends.service_schema import Invalid, check_row
from .errors import CheckerUnavailable

PROFILE = "events@0"
ORDER_LABELS = ("events:irreflexive", "events:transitive", "events:linear")
STATE_KINDS = ("one_begin", "one_end", "not_before_begin")


@dataclass(frozen=True)
class EventsAnswer:
    """What the relay shows: the pack's premises by label, and the named dates by their constants."""
    premises: MappingProxyType
    dates: MappingProxyType


def _unavailable(why: str):
    raise CheckerUnavailable(f"events@0 answer is not bound to its request: {why}")


def constant(iso: str) -> str:
    """The constant Lean declares for a named date, as spec 1.3 names it (`date__YYYY_MM_DD`)."""
    return "date__" + iso.replace("-", "_")


def _block(case: dict) -> dict:
    environment = case.get("environment") if type(case) is dict else None
    if type(environment) is not dict or PROFILE not in environment.get("profiles", ()) \
            or type(environment.get("events")) is not dict:
        _unavailable("the request has no events block")
    return environment["events"]


def _bind_constants(row: dict, environment: dict, block: dict, dates: list) -> dict:
    written = environment["vocabulary"]["constants"]
    answered = row["base_environment"]["vocabulary"]["constants"]
    named = {constant(iso): iso for iso in dates}
    if set(answered) != set(written) | set(named) or set(written) & set(named):
        _unavailable("the base environment's constants are not the request's and one per named date")
    for name, entry in written.items():
        if answered[name] != entry:
            _unavailable(f"constant {name} is not the request's")
    for name, iso in named.items():
        entry = answered[name]
        if entry["sort"] != block["day"] or (iso != block.get("anchor") and entry["description"] != iso):
            _unavailable(f"date constant {name} is not the day {iso} of the request's day sort")
    return named


def _labels(block: dict, predicates: dict, dates: list) -> set:
    """The labels the request's block names (spec 1.4): the three order axioms; each pair of consecutive named dates,
    and those one day apart; each event and state sort's conventions; each link, and each pair of a necessary and a
    contributed link over the same declared sorts."""
    ordered = sorted(dates)
    consecutive = list(zip(ordered, ordered[1:]))
    adjacent = [(a, b) for a, b in consecutive if date.fromisoformat(b) - date.fromisoformat(a) == timedelta(days=1)]
    links = block["links"]
    weaker = [(n["predicate"], c["predicate"]) for n in links if n["form"] == "necessary" for c in links
              if c["form"] == "contributed" and predicates[c["predicate"]]["arguments"] ==
              predicates[n["predicate"]]["arguments"]]
    return {*ORDER_LABELS, *(f"events:date:{a}:{b}" for a, b in consecutive),
            *(f"events:adjacent:{a}:{b}" for a, b in adjacent),
            *(f"events:one_day:{e['sort']}" for e in block["events"]),
            *(f"events:{kind}:{s['sort']}" for s in block["states"] for kind in STATE_KINDS),
            *(f"events:link_forward:{link['predicate']}" for link in links),
            *(f"events:link_weaker:{n}:{c}" for n, c in weaker)}


def _bind_labels(rows: list, block: dict, predicates: dict, dates: list) -> None:
    labels = [p["label"] for p in rows]
    if len(set(labels)) != len(labels):
        _unavailable("a premise label is repeated")
    expected = _labels(block, predicates, dates)
    if extra := set(labels) - expected:
        _unavailable(f"premise {sorted(extra)[0]!r} names nothing of the request")
    if missing := expected - set(labels):
        _unavailable(f"the premise for {sorted(missing)[0]!r} of the request is missing")


def _bind_formula(ast: list, depth: int, names: dict) -> None:
    """Every sort, predicate and constant the formula names is the request's (constants: the bound base
    environment's), and every variable index is under one of its binders."""
    tag = ast[0]
    if tag in ("top", "bottom"):
        return
    if tag in ("forall", "exists") and ast[1] in names["sorts"]:
        return _bind_formula(ast[2], depth + 1, names)
    if tag in ("not", "and", "or", "implies"):
        for part in ast[1:]:
            _bind_formula(part, depth, names)
        return
    terms = ast[2:] if tag in ("unary", "binary") and ast[1] in names["predicates"] else ast[1:] if tag == "eq" else None
    if terms is None:
        _unavailable(f"a premise names {tag} {ast[1] if len(ast) > 1 else ''}, which the request does not declare")
    for term in terms:
        if not ((term[0] == "var" and term[1] < depth) or (term[0] == "const" and term[1] in names["constants"])):
            _unavailable(f"a premise's term {term} is not bound in the request")


def answer(row: object, case: dict) -> EventsAnswer:
    """Lean's `norm-defaults-elaborate` row for the events document `case`, checked and bound, as the relay shows
    it; `CheckerUnavailable` when the row does not fit its schema or names anything the request does not have."""
    block = _block(case)
    try:
        check_row("norm-defaults", row, case, 0)
    except Invalid as exc:
        raise CheckerUnavailable(f"events@0 answer does not fit its schema: {exc}") from exc
    if row.get("status") != "ok" or "events_premises" not in row:
        _unavailable("the answer has no events premises")
    dates = list(dict.fromkeys([*block["dates"], *([block["anchor"]] if "anchor" in block else [])]))
    named = _bind_constants(row, case["environment"], block, dates)
    _bind_labels(row["events_premises"], block, case["environment"]["vocabulary"]["predicates"], dates)
    vocabulary = case["environment"]["vocabulary"]
    names = {"sorts": vocabulary["sorts"], "predicates": vocabulary["predicates"],
             "constants": row["base_environment"]["vocabulary"]["constants"]}
    for premise in row["events_premises"]:
        _bind_formula(premise["ast"], 0, names)
    return EventsAnswer(MappingProxyType({p["label"]: p["ast"] for p in row["events_premises"]}),
                        MappingProxyType(named))


def elaborate(case: dict) -> EventsAnswer:
    """Lean's elaboration of an events document (a `norm-defaults-elaborate` case), relayed and bound."""
    from .norm_defaults_route import run_case
    return answer(run_case({**case, "kind": "norm-defaults-elaborate"}), case)


def english(case: dict):
    """The English vocabulary of the events document `case` once Lean's route has accepted it (`elaborate`): the
    profile wordings are not judged by the author lint and role wordings are (plan 2.7)."""
    from .english import EnglishVocabulary
    from .environment import Environment
    elaborate(case)
    return EnglishVocabulary(Environment(case["environment"], _validated_projection=True))
