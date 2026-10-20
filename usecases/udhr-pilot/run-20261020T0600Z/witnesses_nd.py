"""Status witnesses for the norm-defaults companions: a case inside the guard is SETTLED, a case outside it is UNDECIDED.

At ve-green-rd-6a the statuses are Lean's `norm-defaults-status` rows (Python's `situation`/`status` objects are gone), read
through `ve.norm_defaults_route`: the enumerating replay first, and where it answers UNKNOWN the `undecided` replay with every
unsaid permission filled in (`yes`) and left out (`no`), as `ve.norm_defaults._point_statuses` does.
"""
from __future__ import annotations

import json
from itertools import product
from pathlib import Path

from ve.document import load_document
from ve.norm_defaults_route import run_case, source_case

READ = {"SETTLED yes": ("SETTLED", True), "SETTLED no": ("SETTLED", False), "UNDECIDED": ("UNDECIDED", None)}


def status(ud, model, predicate, row):
    case = source_case(ud, "norm-defaults-status", model=model, predicate=predicate, tuple=list(row), method="enumerate")
    out = run_case(case)
    if out["point_status"] == "UNKNOWN":
        yes = {item["name"]: [list(values) for values in product(*(model["domains"][s] for s in item["sorts"]))]
               for item in ud.elaboration["unsaid"]}
        no = {item["name"]: [] for item in ud.elaboration["unsaid"]}
        out = run_case({**case, "method": "undecided", "yes": yes, "no": no})
    return out


def run(path: Path, spec: dict) -> list[dict]:
    ud = load_document(path)["norm_defaults"]
    declared = json.loads(path.read_bytes()[4:].split(b"\n---\n", 1)[0])["environment"]["vocabulary"]["predicates"]
    out = []
    for domains, rels, checks in spec["witnesses"]:
        relations = {n: [] for n, p in declared.items() if "regulated" not in p}
        relations.update({k: v for k, v in rels.items() if k in relations})
        model = {"complete": True, "constants": {}, "domains": domains, "relations": relations}
        for pred, row, (expected, value) in checks:
            res = status(ud, model, pred, row)
            got = READ[res["point_status"]]
            out.append({"predicate": pred, "row": list(row), "status": got[0], "value": got[1] if got[0] == "SETTLED" else None,
                        "lean_point_status": res["point_status"], "rules": res.get("rules"),
                        "expected": [expected, value], "as_expected": got == (expected, value)})
    return out
