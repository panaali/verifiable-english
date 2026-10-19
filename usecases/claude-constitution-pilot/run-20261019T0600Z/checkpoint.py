#!/usr/bin/env python3
"""Run 20261018T1800Z: the checks the merged prompt asks for after QT-0p and again at the end (DRI 2026-10-14 15:30Z (2), X3; 2026-10-18 order of sections).

    uv run python usecases/claude-constitution-pilot/run-20261018T1800Z/checkpoint.py <label> [<document>]     # default document: readings/nd-all.ve.md

After `nd.py all` (the situation step) it checks, for the document that nd.py wrote: (1) the vocabulary: every predicate that existed in the start document keeps its
English wording (a changed wording is the X3 danger: adding a wording once turned u0248's “is human” into a refusal) and every unit that existed keeps its span and
kind unless this run changed it; (2) every fenced unit of the start document still parses to the same formula; (3) `ve document check`: admitted, premises, route, the
choices all CONFLICT-FREE, bytes by status; (4) the two carried conclusion queries (denial, claim to be human) are ALL. It writes evidence/checkpoint-<label>.json.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))
from ve.english import EnglishVocabulary  # noqa: E402
from ve.environment import Environment  # noqa: E402

PREV = RUN / "prev"


def meta_of(path):
    return json.loads(Path(path).read_bytes().split(b"---\n", 2)[1])


def ve(*args):
    proc = subprocess.run([sys.executable, "-m", "ve", *args], cwd=ROOT, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr[-1500:]


def norm(o):
    return json.loads(json.dumps(o, sort_keys=True))


def main(argv):
    label = argv[1]
    doc = Path(argv[2]) if len(argv) > 2 else RUN / "readings/nd-all.ve.md"
    start = PREV / "translation.ve.md"
    m0, m1 = meta_of(start), meta_of(doc)
    out = {"label": label, "document": str(doc.relative_to(ROOT)), "start_document": str(start.relative_to(ROOT))}
    v0, v1 = EnglishVocabulary(Environment.from_dict(m0["environment"])), EnglishVocabulary(Environment.from_dict(m1["environment"]))
    changed = {k: [v0.predicates[k], v1.predicates.get(k)] for k in v0.predicates if v1.predicates.get(k) != v0.predicates[k]}
    changed_sorts = {k: [v0.sorts[k], v1.sorts.get(k)] for k in v0.sorts if v1.sorts.get(k) != v0.sorts[k]}
    out["x3_vocabulary"] = {"predicates_before": len(v0.predicates), "predicates_after": len(v1.predicates),
                            "predicates_added": sorted(set(v1.predicates) - set(v0.predicates)), "sorts_added": sorted(set(v1.sorts) - set(v0.sorts)),
                            "constants_added": sorted(set(m1["environment"]["vocabulary"]["constants"]) - set(m0["environment"]["vocabulary"]["constants"])),
                            "existing_predicate_wordings_changed": changed, "existing_sort_nouns_changed": changed_sorts,
                            "noun_of_sort_entity": v1.sorts["entity"]}
    # run 20261019T0600Z: the audit repair of QT-0p removes the predicate `claude_principal_type` and gives the sort `principal_type` the noun "principal type of Claude"; nothing else may change
    allowed = {"claude_principal_type": [v0.predicates["claude_principal_type"], None]}
    assert "principal type of Claude" in str(v1.sorts["principal_type"]), v1.sorts["principal_type"]
    allowed_sorts = {"principal_type": [v0.sorts["principal_type"], v1.sorts["principal_type"]]}
    out["x3_vocabulary"]["intended_removals"] = {"predicates": allowed, "sorts": allowed_sorts}
    for k in list(changed):
        if k in allowed and changed[k] == allowed[k]:
            changed.pop(k)
    for k in list(changed_sorts):
        if k in allowed_sorts and changed_sorts[k] == allowed_sorts[k]:
            changed_sorts.pop(k)
    assert not changed and not changed_sorts, (changed, changed_sorts)
    assert v1.sorts["entity"] == "thing" or v1.sorts["entity"] == ("thing", "things") or "thing" in str(v1.sorts["entity"]), v1.sorts["entity"]
    u0 = {u["id"]: u for u in m0["units"]}
    u1 = {u["id"]: u for u in m1["units"]}
    differing = sorted(i for i in u0 if i in u1 and u0[i] != u1[i])
    out["units_start"], out["units_now"] = len(u0), len(u1)
    out["units_differing_from_start"] = differing
    out["units_missing_now"] = sorted(set(u0) - set(u1))
    out["units_new_now"] = sorted(set(u1) - set(u0))
    # (2) fenced units: the fences of the start document parse to the same formulas
    g0 = {n["unit"]: n["ast"] for n in m0["graph"]["nodes"]}
    g1 = {n["unit"]: n["ast"] for n in m1["graph"]["nodes"]}
    out["x3_fenced_units"] = {i: {"start": g0[i], "now": g1.get(i), "unchanged": g1.get(i) == g0[i]} for i in g0}
    assert all(v["unchanged"] for v in out["x3_fenced_units"].values()), out["x3_fenced_units"]
    out["fenced_units_now"] = sorted(g1)
    # (3) ve document check
    t0 = time.monotonic()
    rc, so, se = ve("document", "check", str(doc.relative_to(ROOT)))
    out["document_check"] = {"returncode": rc, "seconds": round(time.monotonic() - t0, 1), "stderr": se}
    assert rc == 0, se
    check = json.loads(so)
    prev_check = json.load(open(PREV / "check.json"))
    out["document_check"].update({
        "admitted": check["admission"]["admitted"], "premises": check["premises"]["status"], "premises_route": check["premises"]["route"],
        "reading_route": check["readings"]["route"], "choices": len(check["reading_plan"]["choices"]),
        "conflict": check["readings"]["conflict"]["status"], "conflicts_by_choice": {k: sum(1 for c in check["readings"]["conflict"]["choices"] if c["status"] == k) for k in {c["status"] for c in check["readings"]["conflict"]["choices"]}},
        "bytes_by_status": check["coverage"]["bytes_by_status"], "bytes_by_status_start": prev_check["coverage"]["bytes_by_status"],
        "residual": check["coverage"]["residual"], "residual_start": prev_check["coverage"]["residual"]})
    assert check["premises"]["status"] == "model" and out["document_check"]["conflict"] == "CONFLICT-FREE" and out["document_check"]["choices"] == 32
    # (4) the carried conclusion queries
    out["conclusions"] = {}
    for name in ("conclusion-no-denial", "conclusion-no-claim-human"):
        rc, so, se = ve("document", "readings", str(doc.relative_to(ROOT)), "--conclusion", str((RUN / f"probes/nd/{name}.json").relative_to(ROOT)))
        res = json.loads(so)
        out["conclusions"][name] = {"returncode": rc, "verdict": res["verdict"], "evidence": res["evidence"], "route": res["route"]}
        assert res["verdict"] == "ALL", (name, res["verdict"])
    (RUN / "evidence").mkdir(exist_ok=True)
    (RUN / f"evidence/checkpoint-{label}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({k: out[k] for k in ("label", "units_differing_from_start", "units_new_now")}, ensure_ascii=False))
    print(json.dumps(out["document_check"], ensure_ascii=False)[:1500])
    print(json.dumps(out["conclusions"]))


if __name__ == "__main__":
    main(sys.argv)
