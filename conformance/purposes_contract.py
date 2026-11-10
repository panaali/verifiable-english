"""Python classifiers, adapter and legacy validation of the `purposes@0` wire table, in shadow (sa-wire-purposes0;
docs/spec/purpose-explanation.md 5.4 and 7): it reports and refuses nothing.

`VE.Purposes.Wire`'s decoder decides, and Python holds no copy of it: each classifier relays the block to Lean's
`diagnose` mode (`Hooks/Purposes.lean`) and reads back the member Lean named, bound to this table: a member of the
check's own phase, at `/purposes`, with exactly its template's arguments, each a string. Anything else is
`CheckerUnavailable`. Diagnostic only: no route imports this module.
"""

from functools import cache

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


def bound(row):
    """The record of a `diagnose` row for this unit, `None` when clean, refused unless bound to the table: every
    field the member fixes, exactly its template's arguments (each a string), and the text they render."""
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
    return record


def lean_record(block):
    """Lean's record for the block (`None`, which the wire does not carry, is an absent member), `None` when the
    contract finds it clean."""
    case = {"id": "purposes", "unit": UNIT, **({} if block is None else {"purposes": block})}
    return bound(decide("diagnose", [case])[0])


def legacy_validation(block):
    """The decoder's own refusal (phase `decode`, whose clean outcome is `decodeBlock` accepting, `classifier_ok_iff`
    in `Hooks/Purposes.lean`), raised with Lean's text; main has no route that decodes the block until PE-2."""
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
