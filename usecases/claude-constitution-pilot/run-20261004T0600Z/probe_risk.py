#!/usr/bin/env python3
"""Probe (not part of the translation): what can `risk@0` (merged since ve-green-discourse) say about the constitution?

It tries the nearest constitution sentences as a risk policy and sends each to the Lean risk route (`risk-elaborate`),
then asks the profile gate whether the risk profile may share a document with the norms of the translation.
Results are written to probes/risk-probe.json. Nothing here is counted in the run's coverage or metrics.

Candidates (the only spans of the source whose words are "could/might lead to harm" with a severity):
  u0087.s06  "Take actions that could cause severe or irreversible harm in the world, e.g., as part of an agentic task, even if asked to do so."
  u0209.s07  "... avoiding situations that might lead to this outcome ..."
  u0141.s02  "... unless the potential hazards of that information are very high ..."
  u0218.s13  "Giving appropriate weight to the badness of unrecoverable situations relative to those that are bad but recoverable."
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))

from conformance.risk import rule  # noqa: E402
from ve.profiles import LANGUAGE, SPEC_REVISION, checker_family  # noqa: E402
from ve.errors import VEError  # noqa: E402
from ve.risk import run_case  # noqa: E402


def base(arguments, wording):
    return {"arguments": arguments, "description": wording, "verbalisation": wording}


def env(*, harms, classes, more_severe, unranked, permission):
    """A minimal risk environment: chooser `claude_instance`; one obligation on Claude about an action."""
    predicates = {
        "available": base(["action", "claude_instance"], "{0} is available to {1}"),
        "leads_to": base(["action", "harm"], "{0} leads to {1}"),
        "avoidance_required": {"arguments": ["claude_instance", "action"],
                               "description": "Claude is required to avoid the action.",
                               "regulated": {"role": "obligation", "default": "deny", "act": "{0} avoid {1}"}},
    }
    alternatives = {"chooser": "claude_instance", "action": "action", "harm": "harm", "available": "available",
                    "leads_to": "leads_to", "outcomes": "signed", "decided_by": "nobody the source names"}
    if permission:  # the `performed` pair needs a permission predicate, whose default is allow in every fixture
        predicates["permitted"] = {"arguments": ["action"], "description": "permission",
                                   "regulated": {"role": "permission", "default": "allow", "act": "{0} be performed"}}
        predicates["required"] = {"arguments": ["action"], "description": "obligation",
                                  "regulated": {"role": "obligation", "default": "deny", "act": "{0} be performed",
                                                "permission": "permitted"}}
        alternatives["performed"] = {"permission": "permitted", "obligation": "required"}
    return {"language": LANGUAGE, "profiles": ["alternatives@0", "norms@0", "relational-fol@0", "risk@0"],
            "spec_revision": SPEC_REVISION,
            "vocabulary": {"sorts": {"claude_instance": {"description": "Claude"}, "action": {"description": "an action"},
                                     "harm": {"description": "a harm"}},
                           "predicates": predicates,
                           "constants": {h: {"sort": "harm", "description": h.replace("_", " ")} for h in harms}},
            "alternatives": alternatives,
            "risk": {"severity": {"sort": "severity", "classes": classes, "more_severe": more_severe,
                                  "unranked": unranked, "decided_by": "nobody the source names"},
                     "harm_classes": [[h, c] for h, c in harms.items()],
                     "unexamined": "possible"}}


def classify(result):
    if result.get("status") == "ok":
        return "accepted"
    return result.get("error") or result.get("diagnostic") or json.dumps(result)[:300]


def try_case(name, environment, norms):
    try:
        res = run_case({"id": name, "kind": "risk-elaborate", "environment": environment, "document": {"norms": norms}})
    except VEError as exc:
        return {"verdict": f"rejected: {exc}"}
    return {"verdict": classify(res), "raw_status": res.get("status"),
            "keys": sorted(res) if isinstance(res, dict) else None}


def main():
    out = {"language_tag": "ve-green-risk", "cases": {}}
    # --- u0087.s06: "could cause severe or irreversible harm": severe and irreversible are two unranked classes, so the
    # guard says "severe or worse, or irreversible or worse". It needs a closed list of harms: the source names none.
    harms = {"a_severe_harm": "severe", "an_irreversible_harm": "irreversible", "a_lesser_harm": "lesser"}
    ms = [["severe", "lesser"], ["irreversible", "lesser"]]
    unranked = [["severe", "irreversible"]]
    guard = ["exists", "harm", ["and", ["or", ["binary", "risk__or_worse", ["var", 0], ["const", "severe"]],
                                        ["binary", "risk__or_worse", ["var", 0], ["const", "irreversible"]]],
                                ["binary", "risk__might_lead_to", ["var", 1], ["var", 0]]]]
    r = rule("avoid-severe-or-irreversible-harm", "avoidance_required", True, guard)
    out["cases"]["u0087.s06 (obligation on Claude, no permission predicate)"] = try_case(
        "u0087s06-obligation", env(harms=harms, classes=["severe", "irreversible", "lesser"], more_severe=ms,
                                   unranked=unranked, permission=False), [r])
    out["cases"]["u0087.s06 (with the `performed` pair: permitted, allow by default)"] = try_case(
        "u0087s06-performed", env(harms=harms, classes=["severe", "irreversible", "lesser"], more_severe=ms,
                                  unranked=unranked, permission=True), [r])
    # the same rule written as a prohibition on the `performed` permission (what alternatives@0 fixtures do)
    perm_rule = rule("no-severe-or-irreversible-harm-action", "permitted", False, guard)
    out["cases"]["u0087.s06 as 'must not be performed' (permission predicate with default allow)"] = try_case(
        "u0087s06-permission", env(harms=harms, classes=["severe", "irreversible", "lesser"], more_severe=ms,
                                   unranked=unranked, permission=True), [perm_rule])
    # --- u0218.s13: "weight to the badness of unrecoverable relative to recoverable": an order of severity, no weighing.
    e13 = env(harms={"an_unrecoverable_situation": "unrecoverable", "a_recoverable_bad_situation": "recoverable"},
              classes=["unrecoverable", "recoverable"], more_severe=[["unrecoverable", "recoverable"]], unranked=[],
              permission=False)
    out["cases"]["u0218.s13 (severity order only; 'appropriate weight' has no place in stage A)"] = try_case(
        "u0218s13-order", e13, [])
    # --- stage B/C fields (chances, costs) that 'expected outcome', 'variance', 'likely' would need
    e14 = copy.deepcopy(e13)
    e14["risk"]["chance_tag"] = "chance"
    out["cases"]["u0218.s14 (expected outcome / variance: needs chances and costs)"] = try_case("u0218s14-stageB", e14, [])
    # --- profile gate: may the risk profile share a document with the translation's norms and soft norms?
    gate = {}
    for label, profiles in {
            "risk@0 with the translation's profiles (documents@1, norms@0, relational-fol@0, soft-norms@0)":
            ["documents@1", "norms@0", "relational-fol@0", "risk@0", "soft-norms@0"],
            "alternatives@0 + risk@0 + norms@0 with soft-norms@0":
            ["alternatives@0", "norms@0", "relational-fol@0", "risk@0", "soft-norms@0"],
            "alternatives@0 + risk@0 + norms@0 (no soft-norms@0)":
            ["alternatives@0", "norms@0", "relational-fol@0", "risk@0"],
            "alternatives@0 + risk@0 + norms@0 + rights@0":
            ["alternatives@0", "norms@0", "relational-fol@0", "rights@0", "risk@0"],
            "alternatives@0 + risk@0 + norms@0 + closure@0":
            ["alternatives@0", "closure@0", "norms@0", "relational-fol@0", "risk@0"]}.items():
        try:
            gate[label] = f"accepted (checker family {checker_family(profiles)})"
        except VEError as exc:
            gate[label] = f"rejected: {exc}"
    out["profile_gate"] = gate
    (RUN / "probes").mkdir(exist_ok=True)
    (RUN / "probes/risk-probe.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
