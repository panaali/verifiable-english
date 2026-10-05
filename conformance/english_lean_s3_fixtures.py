"""The fixture environments of docs/spec/english-lean-s3.md section 8, as environment JSON.

`F` is base spec 8.5's (`examples/fluent/environment.json`). `FO` (8.1), `FD` (8.2), `FA` (8.3), `FR` (8.4)
and `FM` (8.5) extend it as the spec states; each builder returns a fresh dict, so a test may mutate it.
The spec computed its fixtures over Lean data written by hand (spec 12); these are the same vocabularies as
environment JSON that Python's `Environment` admits, which is what S3.5 runs Python on (ev5) and what the
boundary of spec 2.3 must admit (ev8 to ev11).
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

from ve.profiles import LANGUAGE, SPEC_REVISION

ROOT = Path(__file__).resolve().parents[1]


def _pred(arguments, wording, **extra):
    return {"arguments": list(arguments), "description": wording, "verbalisation": wording, **extra}


def _const(sort):
    return {"sort": sort, "description": sort}


def F() -> dict:
    """Base spec 8.5's `F`, in the modern form (`profiles` instead of `profile`)."""
    raw = json.loads((ROOT / "examples/fluent/environment.json").read_text())
    raw.pop("profile")
    raw["language"], raw["spec_revision"] = LANGUAGE, SPEC_REVISION
    raw["profiles"] = ["relational-fol@0"]
    return raw


def FO() -> dict:
    """8.1: `F` with `order@0`, `costs` (service, integer), `exceeds` (two integers), and the integer
    constants `budget` and `limit`."""
    raw = F()
    raw["profiles"] = ["order@0", "relational-fol@0"]
    vocabulary = raw["vocabulary"]
    vocabulary["predicates"]["costs"] = _pred(["service", "$int"], "{0} costs {1}")
    vocabulary["predicates"]["exceeds"] = _pred(["$int", "$int"], "{0} exceeds {1}")
    vocabulary["constants"]["budget"] = _const("$int")
    vocabulary["constants"]["limit"] = _const("$int")
    return raw


def FD() -> dict:
    """8.2: `F` with `data@0`, `senior` on persons, and the attributes `owner_of` (service to person) and
    `backup_of` (service to service), functional and total, without a declared wording (so on their quoted
    fallback)."""
    raw = F()
    raw["profiles"] = ["data@0", "relational-fol@0"]
    predicates = raw["vocabulary"]["predicates"]
    predicates["senior"] = _pred(["person"], "{0} is senior")
    for name, arguments in (("owner_of", ["service", "person"]), ("backup_of", ["service", "service"])):
        predicates[name] = {"arguments": arguments, "description": name, "functional": True, "total": True}
    return raw


def FA() -> dict:
    """8.3: sorts `action`, `agent`, `harm`; `available`, `leads_to` and `safe`; constants `wait`, `robot`,
    `injury`; the `alternatives` block (with `norms@0`, which `alternatives@0` requires)."""
    return {
        "language": LANGUAGE, "profiles": ["alternatives@0", "norms@0", "relational-fol@0"],
        "spec_revision": SPEC_REVISION,
        "vocabulary": {
            "sorts": {s: {"description": s} for s in ("action", "agent", "harm")},
            "predicates": {"available": _pred(["action", "agent"], "{0} is available to {1}"),
                           "leads_to": _pred(["action", "harm"], "{0} leads to {1}"),
                           "safe": _pred(["action"], "{0} is safe")},
            "constants": {"wait": _const("action"), "robot": _const("agent"), "injury": _const("harm")}},
        "alternatives": {"chooser": "agent", "action": "action", "harm": "harm", "available": "available",
                         "leads_to": "leads_to", "outcomes": "signed"},
    }


def FR() -> dict:
    """8.4: `FA` with the risk block: the severity sort with the classes `minor` and `catastrophic`."""
    raw = FA()
    raw["profiles"] = ["alternatives@0", "norms@0", "relational-fol@0", "risk@0"]
    raw["risk"] = {
        "severity": {"sort": "severity", "classes": ["catastrophic", "minor"],
                     "more_severe": [["catastrophic", "minor"]], "unranked": [], "decided_by": "the team"},
        "harm_classes": [["injury", "catastrophic"]],
        "unexamined": "possible",
    }
    return raw


def FM() -> dict:
    """8.5: `F` with `norms@0` and the regulated predicates `access` (permission) and `review` (obligation)
    over person and service, with the acts `{0} access {1}` and `{0} review {1}`."""
    raw = F()
    raw["profiles"] = ["norms@0", "relational-fol@0"]
    predicates = raw["vocabulary"]["predicates"]
    predicates["access"] = {"arguments": ["person", "service"], "description": "access",
                            "regulated": {"role": "permission", "default": "deny", "act": "{0} access {1}"}}
    predicates["review"] = {"arguments": ["person", "service"], "description": "review",
                            "regulated": {"role": "obligation", "default": "deny", "act": "{0} review {1}"}}
    return raw


def FR_UNITS() -> dict:
    """ev11: `FR` with the W6 unit extension as the risk route admits it: the unit profile tuple, `unit_schema`,
    one declared tag `usd`, an empty `argument_units` on `leads_to` and the constant `wait` with the display
    `verbalisation` `wait`. `FR` has no integer slot or constant, so no slot or constant carries a unit."""
    raw = FR()
    raw["unit_schema"] = "ve-units@1"
    raw["units"] = {"usd": {"scale": "100", "display": {"kind": "money", "currency": "USD"}}}
    raw["vocabulary"]["predicates"]["leads_to"]["argument_units"] = {}
    raw["vocabulary"]["constants"]["wait"]["verbalisation"] = "wait"
    return raw


BUILDERS = {"F": F, "FO": FO, "FD": FD, "FA": FA, "FR": FR, "FM": FM, "FR_UNITS": FR_UNITS}


def environment(name: str):
    from ve import Environment
    return Environment(copy.deepcopy(BUILDERS[name]()))
