"""Python classifiers, adapter and legacy validation of the `purposes@0` wire table, in shadow (sa-wire-purposes0;
docs/spec/purpose-explanation.md 5.4 and 7): it reports and refuses nothing.

`VE.Purposes.Wire`'s decoder decides, and Python holds no copy of it: each classifier relays the block to Lean's
`diagnose` mode (`Hooks/Purposes.lean`) and reads back the member Lean named, bound to this table: a member of the
check's own phase, at `/purposes`, with exactly its template's arguments, each a string, and each argument naming
what the request block carries (`BINDS`). Anything else is `CheckerUnavailable`. Diagnostic only: no route imports
this module.
"""

from functools import cache
import json
import re

from conformance.wire_contract_engine import load, pieces
from ve.backends.relay import decide
from ve.errors import CheckerUnavailable, ResourceLimit, VEError
from ve.wire_contract.registry import Registry

UNIT = "purposes@0"


@cache
def members():
    """Each member of the table: the record fields it fixes, and its text's pieces."""
    contract = load(UNIT)
    return {member["id"]: ({"contract": UNIT, "revision": contract["revision"], "check": member["id"],
                            "phase": phase["name"], "code": member["code"],
                            "class": contract["codes"][member["code"]]["class"], "path": "/purposes"},
                           pieces(member["text"]))
            for phase in contract["phases"] for check in phase["checks"] for member in check["emits"]}


def text(template, args):
    """The member's text with `args` in its placeholders (each a string, written as it is)."""
    return "".join(p[1] if p[0] == "lit" else args[p[1]] for p in template)


def _links(block):
    """The links the request carries: its block's `links` array, `[]` when it carries none."""
    links = block.get("links") if type(block) is dict else None
    return links if type(links) is list else []


def _same(a, b):
    """`a` and `b` are one JSON value, type for type (`true` is not `1`); the wire carries no fraction."""
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return a.keys() == b.keys() and all(_same(a[k], b[k]) for k in a)
    if type(a) is list:
        return len(a) == len(b) and all(map(_same, a, b))
    return a == b


def _quotes(value, arg):
    """`arg` quotes the request's `value` as Lean's texts do (`idOf`, `wordOf`): a string as it is, any other value as
    JSON, compared as the value it parses to, never by Lean's spelling of it."""
    if type(value) is str:
        return arg == value
    try:
        return _same(json.loads(arg, parse_constant=_no_constant), value)
    except (ValueError, RecursionError):
        return False


def _no_constant(name):
    raise ValueError(f"{name} is not JSON")


def _count(arg):
    """`arg` as a count: ASCII digits without a leading zero, else `None`."""
    return int(arg) if re.fullmatch(r"0|[1-9][0-9]*", arg) else None


def _ids(block):
    """Every value the request offers `idOf`: each link's `id` and `marker`, and each side's part and mention ids."""
    for link in _links(block):
        if type(link) is dict:
            yield from (link[k] for k in ("id", "marker") if k in link)
            for side in (link.get("reason"), link.get("target")):
                for ref in side if type(side) is list else ():
                    if type(ref) is dict and len(ref) == 1 and set(ref) <= {"part", "mention"}:
                        yield next(iter(ref.values()))


def _field(name):
    """`link` is a link's id in the request, and (unless `name` is `None`) the argument `name` quotes that link's
    `name` member."""
    return lambda block, args: any(
        type(link) is dict and type(link.get("id")) is str and link["id"] == args["link"]
        and (name is None or (name in link and _quotes(link[name], args[name]))) for link in _links(block))


# R8 (b): each member's arguments tied to the request block, the one binding table (a member missing here is refused,
# and `tests/test_purposes_contract.py` checks that its keys are the table's members). A member with no argument names
# nothing of the request.
BINDS = {
    "1.1b": lambda block, args: True,
    "1.1c": lambda block, args: (n := _count(args["limit"])) is not None and len(_links(block)) > n,
    "1.1d": lambda block, args: (n := _count(args["link"])) is not None and 1 <= n <= len(_links(block)),
    "1.1e": lambda block, args: any(_quotes(value, args["id"]) for value in _ids(block)),
    "1.1f": _field("relation"),
    "1.1g": _field("polarity"),
    "1.1h": _field("share"),
    "1.1i": _field(None),
    "2.1b": lambda block, args: True,
}


def bound(row, block):
    """The record of a `diagnose` row for this unit on the request's `block`, `None` when clean, refused unless bound
    to the table (every field the member fixes, exactly its template's arguments, each a string, and the text they
    render) and to the request (each argument names what `BINDS` ties it to in `block`)."""
    outcome, record = row.get("outcome"), row.get("diagnostic")
    if row.get("status") != "ok" or (outcome, "diagnostic" in row) not in (("clean", False), ("fault", True)):
        raise CheckerUnavailable("diagnose: a purposes@0 row is neither clean nor a fault", operation="diagnose")
    if outcome == "clean":
        return None
    if type(record) is not dict:
        raise CheckerUnavailable("diagnose: a purposes@0 fault has no record", operation="diagnose")
    check = record.get("check")
    fixed, template = members().get(check, (None, None)) if type(check) is str else (None, None)
    args = record.get("args")
    if (fixed is None or set(record) != {*fixed, "text", "args"} or any(type(record[k]) is not type(v) or record[k] != v for k, v in fixed.items())
            or type(args) is not dict or set(args) != {p[1] for p in template if p[0] == "arg"}
            or any(type(v) is not str for v in args.values()) or record["text"] != text(template, args)):
        raise CheckerUnavailable("diagnose: a purposes@0 record is not bound to the table", operation="diagnose")
    binds = BINDS.get(check)
    if binds is None or not binds(block, args):
        raise CheckerUnavailable("diagnose: a purposes@0 record names what the request does not carry",
                                 operation="diagnose")
    return record


def lean_record(block):
    """Lean's record for the block (`None`, which the wire does not carry, is an absent member), `None` when the
    contract finds it clean."""
    case = {"id": "purposes", "unit": UNIT, **({} if block is None else {"purposes": block})}
    return bound(decide("diagnose", [case])[0], block)


def legacy_validation(block):
    """The decoder's own refusal (phase `decode`, whose clean outcome is `decodeBlock` accepting: the round-trip
    guards of `Hooks/Purposes.lean`), raised with Lean's text; main has no route that decodes the block until PE-2."""
    record = lean_record(block)
    if record is not None and record["phase"] == "decode":
        raise (ResourceLimit if record["class"] == "ResourceLimit" else VEError)(record["text"])


def classifier(phase):
    def classify(root, items):
        record = lean_record(root.get("purposes"))
        return None if record is None or record["phase"] != phase else (record["check"], dict(record["args"]))
    return classify


def purposes_block(case):
    """The adapter: the case's `purposes` member, `null` when absent, as `Diagnose.caseRoot ["purposes"]`."""
    return {"purposes": case.get("purposes")}


REGISTRY = Registry().register(classifiers={"purposes_block": classifier("decode"), "purposes_ids": classifier("check")},
                               adapters={"purposes_block": purposes_block})
