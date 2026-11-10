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
    """Each member of the table: its phase and the names its template reads."""
    return {member["id"]: (phase["name"], frozenset(p[1] for p in pieces(member["text"]) if p[0] == "arg"))
            for phase in load(UNIT)["phases"] for check in phase["checks"] for member in check["emits"]}


def bound(row):
    """The record of a `diagnose` row for this unit, `None` when clean, refused unless bound to the table."""
    record = row.get("diagnostic") if row.get("outcome") == "fault" else None
    if row.get("status") != "ok" or row.get("outcome") not in ("clean", "fault"):
        raise CheckerUnavailable("diagnose: a purposes@0 row is neither clean nor a fault", operation="diagnose")
    if record is None:
        return None
    phase, names = members().get(record.get("check"), (None, None))
    args = record.get("args")
    if (phase is None or record.get("phase") != phase or record.get("path") != "/purposes"
            or type(args) is not dict or set(args) != names or any(type(v) is not str for v in args.values())):
        raise CheckerUnavailable("diagnose: a purposes@0 record is not bound to the table", operation="diagnose")
    return record


def lean_record(block):
    """Lean's record for the block, `None` when the contract finds it clean."""
    return bound(decide("diagnose", [{"id": "purposes", "unit": UNIT, "purposes": block}])[0])


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
