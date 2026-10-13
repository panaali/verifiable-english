"""ET-1: the constitution's hard-constraint argument as an alternatives component (plan 4.2 P3 to P5).

A separate component on today's alternatives route (`alternatives@0`, `norms@0`, `relational-fol@0`): chooser
`decision`, action `response`, harm `harm`; refusal is the inaction; the seven hard constraints of u0165.s01-s07
are prohibitions on responses with the pilot's own open terms and the shared condition
`restricted_action_knowing_or_quite_likely` (u0173.s01). It edits no pilot file and no unit u0165.s01-s07.

Lean answers every verdict (the alternatives route). Python's prover only searches for certificates, which Lean
replays, as the route's own tests do (`tests/test_alternatives_three_way.py`, `tests/test_asimov_laws.py`).
"""
from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ve.profiles import LANGUAGE, SPEC_REVISION  # noqa: E402

# The seven hard constraints (u0165.s01-s07), with the open-term names of the pilot's main translation
# (run 20261012T1800Z, translation.ve.md), restated over a response instead of a situation.
CONSTRAINTS = [
    ("u0165.s01", "mass_casualty_weapon_uplift",
     "provides serious uplift to those seeking to create biological, chemical, nuclear, or radiological weapons "
     "with the potential for mass casualties"),
    ("u0165.s02", "critical_infrastructure_uplift",
     "provides serious uplift to attacks on critical infrastructure or critical safety systems"),
    ("u0165.s03", "damaging_cyberweapon_or_malicious_code",
     "creates cyberweapons or malicious code that could cause significant damage if deployed"),
    ("u0165.s04", "clear_and_substantial_undermining_of_oversight",
     "clearly and substantially undermines Anthropic's ability to oversee and correct advanced AI models"),
    ("u0165.s05", "attempt_to_kill_or_disempower_most_of_humanity",
     "engages or assists in an attempt to kill or disempower the vast majority of humanity"),
    ("u0165.s06", "illegitimate_absolute_control",
     "engages or assists an attempt to seize unprecedented and illegitimate absolute control"),
    ("u0165.s07", "child_sexual_abuse_material", "generates child sexual abuse material"),
]
KNOWING = "restricted_action_knowing_or_quite_likely"


def base(arguments, wording, description=None):
    return {"arguments": arguments, "description": description or wording, "verbalisation": wording}


def environment(documents=False):
    predicates = {
        "available": base(["response", "decision"], "{0} is available to {1}"),
        "leads_to": base(["response", "harm"], "{0} leads to {1}"),
        "inaction": base(["response"], "{0} is inaction",
                         "The response is refusal: remaining passive, or explaining that the relevant action "
                         "would violate Claude's fundamental principles (u0172.s02)"),
        "taken": base(["response"], "{0} is taken"),
        KNOWING: base(["response"], "{0} is knowingly restricted",
                      "Claude knows, or thinks it quite likely, that the response falls into the restricted "
                      "category (u0173.s01); the open term restricted_action_knowing_or_quite_likely"),
        "permitted": {"arguments": ["response"],
                      "description": "The response may be given: no hard constraint forbids it (this component "
                                     "holds only the hard constraints)",
                      "regulated": {"role": "permission", "default": "allow", "act": "{0} be given"}},
        "required": {"arguments": ["response"], "description": "The response must be given",
                     "regulated": {"role": "obligation", "default": "deny", "act": "{0} be given",
                                   "permission": "permitted"}},
    }
    for unit, name, words in CONSTRAINTS:
        predicates[name] = base(["response"], "{0} " + words.split(" ", 1)[0] + " " + words.split(" ", 1)[1],
                                f"The response {words} ({unit}); the open term {name}")
    sorts = {
        "decision": {"description": "one decision of one instance of Claude about one request"},
        "response": {"description": "one response that instance of Claude can give at one decision"},
        "harm": {"description": "one harm, such as an attack by another actor"},
    }
    profiles = ["alternatives@0", "norms@0", "relational-fol@0"]
    if documents:
        profiles = ["alternatives@0", "documents@1", "norms@0", "relational-fol@0"]
    return {"language": LANGUAGE, "profiles": profiles, "spec_revision": SPEC_REVISION,
            "vocabulary": {"sorts": sorts, "predicates": predicates, "constants": {}},
            "alternatives": {"chooser": "decision", "action": "response", "harm": "harm",
                             "available": "available", "leads_to": "leads_to", "outcomes": "signed",
                             "decided_by": "unresolved_decider",
                             "performed": {"permission": "permitted", "obligation": "required"},
                             "inaction": "inaction", "taken": "taken", "fulfilments": []}}


def v(i):
    return ["var", i]


def norms():
    """u0165.s01-s07: "Every response must not be given, if that response <constraint> and Claude knows or
    thinks it quite likely that it does." One prohibition per hard constraint."""
    return [{"norm": {"name": f"hc-{unit[-3:]}", "predicate": "permitted", "sign": False,
                      "guard": ["and", ["unary", name, v(0)], ["unary", KNOWING, v(0)]],
                      "unless": [], "over": []}} for unit, name, _ in CONSTRAINTS]


def violates_some(i):
    out = None
    for _, name, _ in CONSTRAINTS:
        atom = ["and", ["unary", name, v(i)], ["unary", KNOWING, v(i)]]
        out = atom if out is None else ["or", out, atom]
    return out


# P3's two premises (Γ), support testimony, citing u0172.s02.
AVAILABLE_INACTION = {
    "label": "u0172.s02:refusal-available",
    "ast": ["forall", "decision", ["exists", "response",
                                   ["and", ["binary", "available", v(0), v(1)], ["unary", "inaction", v(0)]]]]}
INACTION_COMPATIBLE = {
    "label": "u0172.s02:refusal-compatible",
    "ast": ["forall", "response", ["implies", ["unary", "inaction", v(0)], ["not", violates_some(0)]]]}

# u0171.s03 as an entailed assertion: "Every response that clearly and substantially undermines Anthropic's
# ability to oversee and correct advanced AI models, if Claude knows or thinks it quite likely that it does, may
# not be given" (the "even if ... prevents" clause is this universal's instance; the scenario shows it).
U0171_S03 = ["forall", "response", ["implies",
                                    ["and", ["unary", "clear_and_substantial_undermining_of_oversight", v(0)],
                                     ["unary", KNOWING, v(0)]],
                                    ["not", ["unary", "permitted", v(0)]]]]


def scenario():
    """P4: one decision d; responses undermine, refuse (inaction), answer; harm attack (another actor's
    bioweapons attack). refuse and answer lead to the attack; undermine does not."""
    env = environment()
    relations = {name: [] for name, p in env["vocabulary"]["predicates"].items() if "regulated" not in p}
    actions = ["undermine", "refuse", "answer"]
    positive = [("refuse", "attack"), ("answer", "attack")]
    relations.update(available=[[a, "d"] for a in actions], leads_to=[list(p) for p in positive],
                     inaction=[["refuse"]],
                     clear_and_substantial_undermining_of_oversight=[["undermine"]],
                     **{KNOWING: [["undermine"]]})
    model = {"complete": True, "domains": {"decision": ["d"], "response": actions, "harm": ["attack"]},
             "constants": {}, "relations": relations}
    rows = [{"action": a, "harm": "attack", "leads_to": (a, "attack") in positive, "support": "testimony"}
            for a in actions]
    return {"model": model, "outcomes": rows}


def source(units=(AVAILABLE_INACTION, INACTION_COMPATIBLE)):
    return {"id": "et1-hard-constraints", "environment": environment(), "norms": norms(),
            "units": [deepcopy(u) for u in units]}


if __name__ == "__main__":
    from ve.alternatives import run_case
    out = run_case(source() | {"kind": "alt-elaborate"})
    print(json.dumps({k: (v if not isinstance(v, (list, dict)) else type(v).__name__ + ":" + str(len(v)))
                      for k, v in out.items()}, indent=1))
    Path(sys.argv[1]).write_text(json.dumps(out, indent=1) + "\n")
