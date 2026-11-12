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
- `events_premises[].label`: each once, of a closed list of kinds (spec 1.4, `_bind_labels`), each exactly the label
  `label` renders from the request's names (no prefix is stripped; pairs by `_pair`). One per request item,
  none missing: the three order axioms; `events:one_day:<s>` per event sort; `events:one_begin:<s>`,
  `events:one_end:<s>` and `events:not_before_begin:<s>` per state sort; `events:link_forward:<p>` per link.
  Counted: `events:date:A:B` over two named dates, one fewer than the named dates, chaining them all. Named only:
  `events:adjacent:A:B` over a date fact's pair, `events:link_weaker:<n>:<c>` over a necessary link and a contributed
  one. Which dates are consecutive or one day apart and which links are weaker are Lean's decisions, not Python's.
  Each formula is Lean's, typed by the schema (`generated_formula`); every sort, predicate and constant it names is
  the request's (the constants those of the bound base environment), and every variable index is under a binder.
- The `document` mode's `events_view` (et-5b, `Service.Document.eventsView`, `Events.routeView`): the environment
  Lean's chain read, bound by `view` to the document's environment as written: its members but `events`, the profiles
  without `events@0`, the vocabulary's members as written but `constants`, and those the relation above. The document
  is built over it; its identities stay the written environment's (Lean's `Env.profiles` and `Env.envId`).
"""
from __future__ import annotations

import json
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


def _same(answered: object, written: object) -> bool:
    """Equal as JSON values, types included (`True` is not `1`, `1.0` is not `1`)."""
    def canonical(value):
        return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False, default=repr,
                          separators=(",", ":"))
    return type(answered) is type(written) and canonical(answered) == canonical(written)


def named_dates(block: dict) -> list:
    """The block's named dates, the anchor among them (spec 1.3), each once, in the request's order."""
    return list(dict.fromkeys([*block["dates"], *([block["anchor"]] if "anchor" in block else [])]))


def _bind_constants(answered: object, environment: dict, block: dict, dates: list) -> dict:
    """The one relation between a Lean environment's constants and the request's: those written, unchanged, and one
    constant per named date of the block's day sort, described by its ISO date (the anchor's description is Lean's
    wording), nothing else."""
    written = environment["vocabulary"]["constants"]
    named = {constant(iso): iso for iso in dates}
    if type(answered) is not dict or set(answered) != set(written) | set(named) or set(written) & set(named):
        _unavailable("the environment's constants are not the request's and one per named date")
    for name, entry in written.items():
        if not _same(answered[name], entry):
            _unavailable(f"constant {name} is not the request's")
    for name, iso in named.items():
        entry = answered[name]
        if (type(entry) is not dict or set(entry) != {"sort", "description"} or type(entry["description"]) is not str
                or not _same(entry["sort"], block["day"])
                or (iso != block.get("anchor") and entry["description"] != iso)):
            _unavailable(f"date constant {name} is not the day {iso} of the request's day sort")
    return named


def view(answered: object, environment: dict) -> dict:
    """Lean's `events_view` of a `document` row (`Service.Document.eventsView`: `Events.routeView`, the environment its
    chain read), bound to the document's environment as written; `CheckerUnavailable` when it is not exactly: the
    written members but `events`, the profiles without `events@0` in their order, the vocabulary's members as written
    but `constants`, and those `_bind_constants`'s relation. Python builds nothing of it (R8, D1)."""
    block = _block({"environment": environment})
    if type(answered) is not dict or set(answered) != set(environment) - {"events"}:
        _unavailable("the document's events view does not have the written environment's members but events")
    if not _same(answered["profiles"], [p for p in environment["profiles"] if p != PROFILE]):
        _unavailable("the document's events view's profiles are not the written ones without events@0")
    for key, value in environment.items():
        if key not in ("events", "profiles", "vocabulary") and not _same(answered[key], value):
            _unavailable(f"the document's events view's {key} is not the request's")
    vocabulary, written = answered["vocabulary"], environment["vocabulary"]
    if type(vocabulary) is not dict or set(vocabulary) != set(written):
        _unavailable("the document's events view's vocabulary does not have the written members")
    for key, value in written.items():
        if key != "constants" and not _same(vocabulary[key], value):
            _unavailable(f"the document's events view's vocabulary {key} is not the request's")
    _bind_constants(vocabulary["constants"], environment, block, named_dates(block))
    return answered


def label(kind: str, *names: str) -> str:
    """The label Lean gives a premise of `kind` over `names` (`VE.Events.eventsLabelled`: `events:` then the kind and
    the names, joined by `:`). The one renderer: every label the relay accepts is one of these, re-rendered exactly."""
    return ":".join(("events", kind, *names))


def _pair(text: str, kind: str, left, right):
    """The one pair (a, b) of `left` × `right`, a ≠ b, whose label of `kind` is exactly `text`; else None. The label is
    never parsed loosely: its prefix and kind are required, and every split of the rest at a `:` is tried, so a name
    holding a `:` neither breaks a genuine label nor lets two readings of one label pass."""
    head = label(kind, "")
    if not text.startswith(head):
        return None
    rest = text[len(head):]
    found = [(rest[:i], rest[i + 1:]) for i, ch in enumerate(rest)
             if ch == ":" and rest[:i] in left and rest[i + 1:] in right and rest[:i] != rest[i + 1:]]
    return found[0] if len(found) == 1 and label(kind, *found[0]) == text else None


def _bind_labels(rows: list, block: dict, dates: list) -> None:
    """Each label once, of a closed list of kinds, naming the request's dates, sorts and links (spec 1.4). Every
    label is one `label` renders from the request's names, exactly (`_pair` for the pairs): no prefix is stripped,
    so no row outside the closed list passes beside its genuine twin. The rows one per request item are all there:
    the order axioms, each event and state sort's conventions, each link's forward premise. The date facts are
    counted: one fewer than the named dates, chaining them all. Which named dates are consecutive, which are one day
    apart and which links are weaker are Lean's (`calendarLabelled`, `weakerPairs`); Python names, counts and checks
    membership only (R8)."""
    labels = [p["label"] for p in rows]
    if len(set(labels)) != len(labels):
        _unavailable("a premise label is repeated")
    forms = {link["predicate"]: link["form"] for link in block["links"]}
    necessary = {name for name, form in forms.items() if form == "necessary"}
    contributed = {name for name, form in forms.items() if form == "contributed"}
    each = {*ORDER_LABELS, *(label("one_day", e["sort"]) for e in block["events"]),
            *(label(kind, s["sort"]) for s in block["states"] for kind in STATE_KINDS),
            *(label("link_forward", name) for name in forms)}
    named = set(dates)
    facts, adjacent = set(), set()
    for text in set(labels) - each:
        if pair := _pair(text, "date", named, named):
            facts.add(pair)
        elif pair := _pair(text, "adjacent", named, named):
            adjacent.add(pair)
        elif not _pair(text, "link_weaker", necessary, contributed):
            _unavailable(f"premise {text!r} names nothing of the request")
    if missing := each - set(labels):
        _unavailable(f"the premise for {sorted(missing)[0]!r} of the request is missing")
    # The chain from the one date no fact ends at, each date followed once: it must reach every named date.
    following, starts = dict(facts), set(dates) - {b for _, b in facts}
    chain = [*starts]
    if len(starts) == 1 and len(following) == len(facts):
        while chain[-1] in following and len(chain) <= len(dates):
            chain.append(following[chain[-1]])
    # No named date (an open anchor, spec 1.3) has no date fact: zero, not minus one.
    if len(facts) != max(len(dates) - 1, 0) or sorted(chain) != sorted(dates):
        _unavailable("the date facts do not chain the request's named dates, one fewer than they")
    if adjacent - facts:
        _unavailable(f"premise {label('adjacent', *sorted(adjacent - facts)[0])!r} names nothing of the request")


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
    dates = named_dates(block)
    named = _bind_constants(row["base_environment"]["vocabulary"]["constants"], case["environment"], block, dates)
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


def elaborated(case: dict) -> tuple[dict, EventsAnswer]:
    """Lean's `norm-defaults-elaborate` row for an events document `case` and its pack, relayed and bound (`answer`)."""
    from .norm_defaults_route import run_case
    row = run_case({**case, "kind": "norm-defaults-elaborate"})
    return row, answer(row, case)


def elaborate(case: dict) -> EventsAnswer:
    """Lean's elaboration of an events document (a `norm-defaults-elaborate` case), relayed and bound."""
    return elaborated(case)[1]


class Written:
    """An `events@0` document's environment as written (`source`), whose identity version its `source_id` binds:
    Lean's `Env.profiles`, `events@0` among them (`Service.Document.environmentOf`). Read through the environment's
    own projection (`Environment.identity_version`, its one owner); it decides nothing."""

    def __init__(self, source: dict):
        from .environment import Environment
        self.source = source
        self.identity_version = Environment(source, _validated_projection=True).identity_version


def english(case: dict):
    """The English vocabulary of the events document `case` once Lean's route has accepted it (`elaborate`): the
    profile wordings are not judged by the author lint and role wordings are (plan 2.7)."""
    from .english import EnglishVocabulary
    from .environment import Environment
    elaborate(case)
    return EnglishVocabulary(Environment(case["environment"], _validated_projection=True))
