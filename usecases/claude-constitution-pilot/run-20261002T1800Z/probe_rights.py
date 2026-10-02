#!/usr/bin/env python3
"""Probe (not part of the translation): can the two force readings of one user-directed duty (u0156.s03,
"Claude shouldn't actively deceive the user ...") be carried as `rights@0` candidates that hold content, so that VE
itself checks that the readings differ?

Result (probes/rights-reading-probe.json): no. A rights candidate is checked on a finite situation whose relations
must be exactly the base predicates of that candidate's own elaboration. The defeasible candidate adds its exception
atom to that vocabulary and the strict candidate does not, so no single situation is accepted for both candidates and
the pair cannot be separated by a checked model. Nothing here is counted in the run's coverage or metrics."""
from __future__ import annotations

import json
import sys
from itertools import product as tuples
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))

from ve.errors import VEError  # noqa: E402
from ve.readings import _right_situation  # noqa: E402
from ve.rights import RightsDocument, RightsEnvironment  # noqa: E402

UNIT = "u0156.s03"
RULE = {"name": "no-system-prompt-deception", "predicate": "system_prompt_deception_avoidance_required",
        "sign": True, "guard": ["top"], "unless": [], "over": []}


def right(default):
    norm = dict(RULE)
    if default:
        norm.update({"mode": "default", "exception": {"decided_by": "unstated", "sufficient": [], "necessary": [], "factors": []}})
    return {"right": {"name": "user-claim-no-system-prompt-deception", "holder": "user", "guard": ["top"],
                      "lines": [{"kind": "claim", "holder_slot": None, "cites": {}, "norm": norm}]}}


def main():
    data = (RUN / "readings/all-default.ve.md").read_bytes()  # the soft companion: the main document has no soft-norms@0 (norm-defaults@0 cannot join it)
    meta = json.loads(data[4:data.index(b"\n---\n", 4)])
    env_data = meta["environment"]
    env_data["profiles"] = sorted(set(env_data["profiles"]) | {"rights@0"})
    env_data["vocabulary"]["rights"] = {"holders": ["user"], "bearers": ["claude_instance"], "protected": [], "alters": {}}
    env = RightsEnvironment(env_data)
    unit_ids = {u["id"] for u in meta["units"]}
    constants = {c: env_data["vocabulary"]["constants"][c]["sort"][0] + "0" for c in env_data["vocabulary"]["constants"]}
    result = {"unit": UNIT, "rights_block": env_data["vocabulary"]["rights"], "candidates": {}}
    wires = {}
    for name, default in (("strict", False), ("default", True)):
        content = right(default)
        base = RightsDocument(env, [{"source_units": sorted(unit_ids)}, content]).soft_document.elaborated.base_environment()
        domains = {sort: [sort[0] + "0"] for sort in base.sorts}
        wires[name] = {"domains": domains, "complete": True, "constants": constants,
                       "relations": {n: [list(v) for v in tuples(*(domains[s] for s in d.arguments))]
                                     for n, d in sorted(base.predicates.items())}}
        result["candidates"][name] = {"base_predicates_in_its_situation": sorted(
            n for n in wires[name]["relations"] if "excepted" in n or "deception" in n)}
    contents = {"strict": right(False), "default": right(True)}
    for wire_of in ("strict", "default"):
        for candidate in ("strict", "default"):
            try:
                model_id = _right_situation(env, contents[candidate], wires[wire_of], unit_ids)[0]
                outcome = f"accepted (model {model_id[:12]}…)"
            except VEError as exc:
                outcome = f"rejected: {exc}"
            result.setdefault("situation_of_candidate_x_candidate_checked", {})[f"situation built for {wire_of}, checked on {candidate}"] = outcome
    result["conclusion"] = ("A situation is accepted only for the candidate it was built for; the strict and the defeasible "
                            "candidate never share one, so VE cannot check that they differ. Force readings therefore cannot "
                            "be rights-reading candidates that carry checked content.")
    (RUN / "probes/rights-reading-probe.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(result, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
