#!/usr/bin/env python3
"""Run 20261017T1800Z: ask VE what the in-frame strict candidate of u0156.s03 says, on one-element situations. Writes probes/frame-probe.json.

Reads readings/all-strict-in-frame.ve.md (the strict companion with u0156.s03 as the strict-in-frame rule: guard = asked_to_keep_system_prompt_confidential(c)) and asks, with
VE's norm-defaults route as probe_unspecified.py does: is Claude permitted to actively deceive a user about the system prompt (a) where Claude is asked to keep it confidential
(expected SETTLED no) and (b) where it is not (expected UNDECIDED: the in-frame reading says nothing outside the frame). The unframed strict candidate (readings/all-strict.ve.md)
is SETTLED no in both (probe_unspecified.py, 'u0156.s03: any situation'). Nothing here reads the answer from the source: the verdicts are VE's.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(RUN))

from ve.document import load_document  # noqa: E402
from ve.norm_defaults_route import run_case, source_case  # noqa: E402
import frame_u0156 as fr  # noqa: E402
import probe_unspecified as pu  # noqa: E402

PRED = "system_prompt_deception_permitted"


def main():
    out = {"document": "readings/all-strict-in-frame.ve.md", "points": []}
    for name, path in (("strict-in-frame", "readings/all-strict-in-frame.ve.md"), ("strict", "readings/all-strict.ve.md")):
        doc = load_document(RUN / path)["norm_defaults"]
        for label, atoms in (("Claude is asked to keep its system prompt confidential", [fr.FRAME_TERM]), ("Claude is not asked to keep its system prompt confidential", [])):
            if name == "strict" and atoms:
                continue   # the unframed document has no frame term
            model = pu.situation(doc, atoms)
            sorts = doc.env.predicates[PRED].arguments
            case = source_case(doc, "norm-defaults-status", model=model.to_dict(), predicate=PRED, tuple=[x + "0" for x in sorts], method="enumerate")
            row = run_case(case)
            status = row["point_status"]
            if status == "UNKNOWN":
                from itertools import product
                yes = {i["name"]: [list(v) for v in product(*(model.to_dict()["domains"][x] for x in i["sorts"]))] for i in doc.elaboration["unsaid"]}
                no = {i["name"]: [] for i in doc.elaboration["unsaid"]}
                status = run_case({**case, "method": "undecided", "yes": yes, "no": no})["point_status"]
            out["points"].append({"candidate": name, "label": label, "predicate": PRED, "true_atoms": atoms, "status": status})
    (RUN / "probes/frame-probe.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(out["points"], indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
