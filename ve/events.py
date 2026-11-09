"""The `events@0` relay: Lean's answer about an events document, bound to the request (events-time-causation plan
ET-5; spec 1.3, 1.4 and 6.3).

Lean owns the block, the premises it generates, their labels and formulas, and every verdict (`VE.Events`); this
module decides nothing (R8). It relays the fields et-4 and et-4b report on the norm-defaults route's elaboration of
an events document, `events_premises` and the date constants of `base_environment`, after two checks: the row fits
its generated schema, and every date, label and link the answer names exists in the request, once, with no extra row.
Anything else is `CheckerUnavailable`.

The bindings, a closed list of relations to the request's block (dates with the anchor, event and state sorts, links):

- `base_environment.vocabulary.constants`: the request's constants as written, plus exactly one constant
  `date__YYYY_MM_DD` per named date, of the block's day sort, described by its own ISO date (the anchor's description
  is Lean's wording, spec 1.3, and is not shown).
- `events_premises[].label`: each once, of a closed list of kinds (spec 1.4, `_bind_labels`). One per request item,
  none missing: the three order axioms; `events:one_day:<s>` per event sort; `events:one_begin:<s>`,
  `events:one_end:<s>` and `events:not_before_begin:<s>` per state sort; `events:link_forward:<p>` per link.
  Counted: `events:date:A:B` over two named dates, one fewer than the named dates, chaining them all. Named only:
  `events:adjacent:A:B` over a date fact's pair, `events:link_weaker:<n>:<c>` over a necessary link and a contributed
  one. Which dates are consecutive or one day apart and which links are weaker are Lean's decisions, not Python's.
  Each formula is Lean's, typed by the schema (`generated_formula`); every sort, predicate and constant it names is
  the request's (the constants those of the bound base environment), and every variable index is under a binder.
"""
from __future__ import annotations

from dataclasses import dataclass
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


def _strings(value: object) -> bool:
    return type(value) is list and all(type(item) is str for item in value)


def _rows(value: object, *keys: str) -> bool:
    return type(value) is list and all(type(item) is dict and all(type(item.get(k)) is str for k in keys)
                                       for item in value)


def _block(case: dict) -> dict:
    """The request's events block, of the shape the bindings read; anything else is no events request."""
    environment = case.get("environment") if type(case) is dict else None
    vocabulary = environment.get("vocabulary") if type(environment) is dict else None
    block = environment.get("events") if type(environment) is dict else None
    if type(vocabulary) is not dict or not all(type(vocabulary.get(k)) is dict
                                               for k in ("sorts", "predicates", "constants")) \
            or PROFILE not in environment.get("profiles", ()) or type(block) is not dict:
        _unavailable("the request has no events block")
    if not (_strings(block.get("dates")) and type(block.get("day")) is str
            and type(block.get("anchor", "")) is str and _rows(block.get("events"), "sort")
            and _rows(block.get("states"), "sort") and _rows(block.get("links"), "predicate", "form")):
        _unavailable("the request's events block is not of the shape the bindings read")
    return block


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


def _bind_labels(rows: list, block: dict, dates: list) -> None:
    """Each label once, of a closed list of kinds, naming the request's dates, sorts and links (spec 1.4). The rows
    one per request item are all there: the order axioms, each event and state sort's conventions, each link's
    forward premise. The date facts are counted: one fewer than the named dates, chaining them all. Which named
    dates are consecutive, which are one day apart and which links are weaker are Lean's (`calendarLabelled`,
    `weakerPairs`); Python names, counts and checks membership only (R8)."""
    labels = [p["label"] for p in rows]
    if len(set(labels)) != len(labels):
        _unavailable("a premise label is repeated")
    forms = {link["predicate"]: link["form"] for link in block["links"]}
    each = {*ORDER_LABELS, *(f"events:one_day:{e['sort']}" for e in block["events"]),
            *(f"events:{kind}:{s['sort']}" for s in block["states"] for kind in STATE_KINDS),
            *(f"events:link_forward:{name}" for name in forms)}
    facts, adjacent = set(), set()
    for label in set(labels) - each:
        kind, _, pair = label.removeprefix("events:").partition(":")
        a, _, b = pair.partition(":")
        if kind in ("date", "adjacent") and a in dates and b in dates and a != b:
            (facts if kind == "date" else adjacent).add((a, b))
        elif not (kind == "link_weaker" and forms.get(a) == "necessary" and forms.get(b) == "contributed"):
            _unavailable(f"premise {label!r} names nothing of the request")
    if missing := each - set(labels):
        _unavailable(f"the premise for {sorted(missing)[0]!r} of the request is missing")
    # The chain from the one date no fact ends at, each date followed once: it must reach every named date.
    following, starts = dict(facts), set(dates) - {b for _, b in facts}
    chain = [*starts]
    if len(starts) == 1 and len(following) == len(facts):
        while chain[-1] in following and len(chain) <= len(dates):
            chain.append(following[chain[-1]])
    if len(facts) != len(dates) - 1 or sorted(chain) != sorted(dates):
        _unavailable("the date facts do not chain the request's named dates, one fewer than they")
    if adjacent - facts:
        _unavailable(f"premise 'events:adjacent:{':'.join(sorted(adjacent - facts)[0])}' names nothing of the request")


def _bind_formula(ast: list, names: dict) -> None:
    """Every sort, predicate and constant the formula names is the request's (constants: the bound base
    environment's), and every variable index is under one of its binders. An explicit stack: any depth the schema
    admits is walked without recursion."""
    stack = [(ast, 0)]
    while stack:
        node, depth = stack.pop()
        tag = node[0]
        if tag in ("forall", "exists") and node[1] in names["sorts"]:
            stack.append((node[2], depth + 1))
        elif tag in ("not", "and", "or", "implies"):
            stack.extend((part, depth) for part in node[1:])
        elif tag == "eq" or tag in ("unary", "binary") and node[1] in names["predicates"]:
            terms = node[1 if tag == "eq" else 2:]
            if tag != "eq" and len(terms) != len(names["predicates"][node[1]]["arguments"]):
                _unavailable(f"a premise applies {node[1]} to {len(terms)} terms, not its declared arity")
            for term in terms:
                if not ((term[0] == "var" and term[1] < depth) or (term[0] == "const" and term[1] in names["constants"])):
                    _unavailable(f"a premise's term {term} is not bound in the request")
        elif tag not in ("top", "bottom"):
            _unavailable(f"a premise names {tag} {node[1] if len(node) > 1 else ''}, which the request does not declare")


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
    _bind_labels(row["events_premises"], block, dates)
    vocabulary = case["environment"]["vocabulary"]
    names = {"sorts": vocabulary["sorts"], "predicates": vocabulary["predicates"],
             "constants": row["base_environment"]["vocabulary"]["constants"]}
    for premise in row["events_premises"]:
        _bind_formula(premise["ast"], names)
    # Shown by label: the order of the answer's rows changes nothing shown.
    return EventsAnswer(MappingProxyType({p["label"]: p["ast"] for p in sorted(row["events_premises"],
                                                                                 key=lambda p: p["label"])}),
                        MappingProxyType(dict(sorted(named.items()))))


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
