"""Executable forms of the alternatives spec's scenario fixtures a, b, c and o.

Lean owns the derived semantics. The third-party evaluators receive only the
closed, base-vocabulary formula returned by Lean's alt-elaborate case.
"""
from __future__ import annotations

from copy import deepcopy

from ve.profiles import LANGUAGE, SPEC_REVISION


def environment():
    def base(arguments, wording):
        return {"arguments": arguments, "description": wording, "verbalisation": wording}

    predicates = {
        "available": base(["action", "robot"], "{0} is available to {1}"),
        "leads_to": base(["action", "harm"], "{0} leads to {1}"),
        "inaction": base(["action"], "{0} is inaction"),
        "taken": base(["action"], "{0} is taken"),
        "harms_human": base(["harm"], "{0} is a harm to a human being"),
        "injures_human": base(["action"], "{0} injures a human being"),
        "permitted": {"arguments": ["action"], "description": "permission", "regulated":
                      {"role": "permission", "default": "allow", "act": "{0} be performed"}},
        "required": {"arguments": ["action"], "description": "obligation", "regulated":
                     {"role": "obligation", "default": "deny", "act": "{0} be performed",
                      "permission": "permitted"}},
        "prevent_required": {"arguments": ["robot", "harm"], "description": "prevention", "regulated":
                             {"role": "obligation", "default": "deny", "act": "{0} prevent {1}"}},
    }
    return {"language": LANGUAGE, "profiles": ["alternatives@0", "norms@0", "relational-fol@0"],
            "spec_revision": SPEC_REVISION,
            "vocabulary": {"sorts": {s: {"description": s} for s in ("robot", "action", "harm")},
                           "predicates": predicates, "constants": {}},
            "alternatives": {"chooser": "robot", "action": "action", "harm": "harm",
                             "available": "available", "leads_to": "leads_to", "outcomes": "signed",
                             "decided_by": "Asimov case annotator",
                             "performed": {"permission": "permitted", "obligation": "required"},
                             "inaction": "inaction", "taken": "taken",
                             "fulfilments": [{"obligation": "prevent_required", "body": "avoids"}]}}


def rule(name, predicate, sign, guard):
    return {"norm": {"name": name, "predicate": predicate, "sign": sign,
                     "guard": guard, "unless": [], "over": []}}


def rules():
    human_allows = ["exists", "harm", ["and", ["unary", "harms_human", ["var", 0]],
                                       ["binary", "allows", ["var", 1], ["var", 0]]]]
    return {
        "3": rule("law-1-direct", "permitted", False, ["unary", "injures_human", ["var", 0]]),
        "7": rule("inaction-allows", "permitted", False,
                  ["and", ["unary", "inaction", ["var", 0]], human_allows]),
        "7p": rule("allows-harm", "permitted", False, human_allows),
        "8": rule("prevent-harm", "prevent_required", True,
                  ["and", ["unary", "harms_human", ["var", 0]],
                   ["binary", "avoidable", ["var", 0], ["var", 1]]]),
        "8m": rule("prevent-harm", "prevent_required", True,
                   ["unary", "harms_human", ["var", 0]]),
    }


def scenario(actions, harms, positive, *, injured=()):
    relations = {name: [] for name in environment()["vocabulary"]["predicates"]
                 if name not in {"permitted", "required", "prevent_required"}}
    relations.update(available=[[a, "r"] for a in actions],
                     leads_to=[list(pair) for pair in positive],
                     inaction=[["nothing"]] if "nothing" in actions else [],
                     harms_human=[[h] for h in harms],
                     injures_human=[[a] for a in injured])
    model = {"complete": True, "domains": {"robot": ["r"], "action": actions, "harm": harms},
             "constants": {}, "relations": relations}
    rows = [{"action": a, "harm": h, "leads_to": (a, h) in positive,
             "support": "testimony"} for a in actions for h in harms]
    return {"model": model, "outcomes": rows}


def cases():
    r = rules()
    entries = [
        ("a", ("3", "7"), ("nothing", "pull"), ("h1",), (("nothing", "h1"),), (), ("pull",)),
        ("b-A0", ("3", "7"), ("nothing", "pull"), ("h1", "h2"),
         (("nothing", "h1"), ("pull", "h2")), (), ("pull",)),
        ("b-A1", ("3", "7"), ("nothing", "pull"), ("h1", "h2"),
         (("nothing", "h1"), ("pull", "h2")), ("pull",), ()),
        ("b-A2", ("3", "7p"), ("nothing", "pull"), ("h1", "h2"),
         (("nothing", "h1"), ("pull", "h2")), (), ()),
        ("b-B", ("3", "8"), ("nothing", "pull"), ("h1", "h2"),
         (("nothing", "h1"), ("pull", "h2")), (), ()),
        ("c-7", ("3", "7"), ("nothing", "pull"), ("h",),
         (("nothing", "h"), ("pull", "h")), (), ("nothing", "pull")),
        ("c-8", ("3", "8"), ("nothing", "pull"), ("h",),
         (("nothing", "h"), ("pull", "h")), (), ("nothing", "pull")),
        ("c-8m", ("3", "8m"), ("nothing", "pull"), ("h",),
         (("nothing", "h"), ("pull", "h")), (), ()),
        ("o-7", ("3", "7"), ("nothing", "act", "rescue"), ("h",),
         (("nothing", "h"), ("act", "h")), (), ("act", "rescue")),
        ("o-8", ("3", "8"), ("nothing", "act", "rescue"), ("h",),
         (("nothing", "h"), ("act", "h")), (), ("rescue",)),
    ]
    for name, selected, actions, harms, positive, injured, clear in entries:
        source = {"id": name, "environment": environment(), "norms": [deepcopy(r[k]) for k in selected],
                  "scenario": scenario(list(actions), list(harms), positive, injured=injured)}
        yield {**source, "expected_clear": list(clear)}


def base_environment(source):
    """The declared base vocabulary used for independent finite evaluation."""
    env = deepcopy(source)
    env["profiles"] = ["relational-fol@0"]
    del env["alternatives"]
    for name in ("permitted", "required", "prevent_required"):
        del env["vocabulary"]["predicates"][name]
    return env
