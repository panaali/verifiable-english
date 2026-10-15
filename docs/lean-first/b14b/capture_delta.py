"""Record batch 14b's answer changes on n-ary capture documents (lf-14b review F5).

    uv run python docs/lean-first/b14b/capture_delta.py OUT.json

A capture document has a lower regulated outcome holding an n-ary atom over its
tuple variable, cited under binders of a higher rule
(`tests/test_stage2_norms.py::capture_documents`). Such documents were on the
retained Python route at the base and are on the Lean family route at the head.
The base expansion leaves the atom's variables unsubstituted, so the citing
binders capture them. This records every conflict operation of
`check_conflict` and `check_witness` on each document and model twice at the
head: on the Lean family route, and with the Lean route switched off (the
retained Python, which answers as the base: `evidence/fallback-compare.json`).
Each difference is a change no standing ruling signs. This is batch evidence,
checked at the batch gate and merge; it is not a permanent test.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import ve.norms  # noqa: E402
from ve.errors import VEError  # noqa: E402
from ve.norms import check_conflict, check_witness  # noqa: E402
from tests.test_stage2_norms import capture_documents, capture_models  # noqa: E402


def answer(run):
    try:
        report = run()
    except VEError as error:
        return {"error": type(error).__name__, "text": str(error)}
    if type(report) is bool:
        return {"ok": report}
    return {"ok": {"status": report.status, "target": report.target, "tuple": list(report.tuple),
                   "situation": report.situation, "detail": report.detail}}


def operations(doc):
    third = doc.env.predicates["tri"].arguments[2]
    ops = {"conflict-prove": lambda: check_conflict(doc, prove=True, tableau_steps=2000),
           "conflict-missing": lambda: check_conflict(doc, certificates={})}
    for m, model in enumerate(capture_models(third)):
        ops[f"conflict-model-{m}"] = lambda model=model: check_conflict(doc, model=model)
        for value in model["domains"]["act"]:
            ops[f"witness-model-{m}-{value}"] = (
                lambda model=model, value=value: check_witness(doc, "required->permitted", model, [value]))
    return {name: answer(run) for name, run in ops.items()}


def main():
    _, out = sys.argv
    lean_route = ve.norms._lean_route
    records, differences = [], []
    for name, doc in sorted(capture_documents().items()):
        assert lean_route(doc)
        ve.norms._lean_route = lean_route
        head = operations(doc)
        ve.norms._lean_route = lambda document: False
        base = operations(doc)
        ve.norms._lean_route = lean_route
        for op in head:
            records.append({"document": name, "op": op, "base": base[op], "head": head[op]})
            if base[op] != head[op]:
                differences.append(records[-1])
    result = {"documents": len(capture_documents()), "records": len(records),
              "differences": differences,
              "route": "head Lean family route vs head retained Python (the base's answers)"}
    Path(out).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"{len(records)} records; {len(differences)} differences")


if __name__ == "__main__":
    main()
