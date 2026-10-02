"""Status witnesses for the norm-defaults companions: a case inside the guard is SETTLED, a case outside it is UNDECIDED."""
from __future__ import annotations

import json
from pathlib import Path

import companions_nd as N
from ve.document import load_document


def run(path: Path, spec: dict) -> list[dict]:
    ud = load_document(path)["norm_defaults"]
    declared = json.loads(path.read_bytes()[4:].split(b"\n---\n", 1)[0])["environment"]["vocabulary"]["predicates"]
    out = []
    for domains, rels, checks in spec["witnesses"]:
        relations = {n: [] for n, p in declared.items() if "regulated" not in p}
        relations.update({k: v for k, v in rels.items() if k in relations})
        sit = ud.situation({"complete": True, "constants": {}, "domains": domains, "relations": relations})
        for pred, row, (expected, value) in checks:
            s = ud.status(sit, pred, row)
            got = (s.status, s.value if s.status == "SETTLED" else None)
            out.append({"predicate": pred, "row": list(row), "status": s.status,
                        "value": s.value if s.status == "SETTLED" else None, "evidence": s.evidence,
                        "expected": [expected, value], "as_expected": got == (expected, value)})
    return out
