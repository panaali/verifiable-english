"""RD-5 step 2: separating situations for the migrated UDHR sets, proposed by the search and checked by Lean.

`separate` offers each candidate set to Lean as a document of its own (the main document's units, that one set):

1. `readings-elaborate` on the set with every distinguishing model pending. Lean's split answers the set's case:
   its merged environment, its document and, under the completion, its filled document and `Fill_T`. A refusal
   (Lean's text) leaves the set on W2 (E1).
2. For each ordered pair of readings, the retained S1 search (`ve.readings_s1.search`, untrusted, RD-2b) proposes a
   situation over Lean's filled document, trying first the 3.3 pattern for each reading as witness (`guard_base`:
   one element per sort, the witness's guard atoms true) and then the exchanged witness, as the search does.
3. `readings-validate` on the set with the situations recorded. Lean checks every separation; the set migrates only
   when Lean admits it with every pair separated. Otherwise it stays on W2, and its unseparated pairs (the pairs the
   search found no situation for) or Lean's text are listed.

The search proposes and Lean decides: nothing here reads a verdict from Python.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

BATCH = 8


def pending(item):
    """The set with every distinguishing model pending and no situation."""
    item = copy.deepcopy(item)
    item["situations"] = {}
    for r in item["readings"]:
        r["admission"]["distinguishing_models"] = {o["id"]: "pending" for o in item["readings"] if o["id"] != r["id"]}
    return item


def _case(kind, env, units, item):
    from ve.readings_route import document_wire
    from ve.readings_s1 import wire
    return {"id": f"{kind}:{item['id']}", "kind": kind, "environment": wire(env),
            "document": wire(document_wire(units, [item]))}


def _rows(cases, executable):
    from ve.readings_route import run_lean
    rows = []
    for k in range(0, len(cases), BATCH):
        rows += run_lean(cases[k:k + BATCH], executable=executable)
    return rows


def _component(row, set_id):
    """The set's own case in Lean's split answer."""
    [part] = [c for c in row["components"] if c["component"] == set_id]
    return part


def propose(part, set_id):
    """The search's situations for the set's pairs over Lean's filled document, the 3.3 pattern first."""
    from ve.readings_s1 import Decoded, guard_base, search
    answer = part["answer"]
    decoded = Decoded(part["environment"], part["document"], answer["filled"], answer["fill_premises"])
    R = decoded.doc.set_by_id(set_id)
    hints = [guard_base(decoded, set_id, i) for i, a in enumerate(R.candidates) if a.content is not None]
    return search(part["environment"], part["document"], set_id, max_size=1, hints=hints, decoded=decoded)


def separate(env, units, candidates, *, executable=None):
    """{migrated: {set: set with situations}, refused: {set: Lean's text}, unseparated: {set: [[a, b], ...]}}."""
    from ve.errors import VEError
    from ve.readings_s1 import record_situations
    refused, unseparated, recorded = {}, {}, {}
    waiting = [pending(item) for item in candidates]
    for item, row in zip(waiting, _rows([_case("readings-elaborate", env, units, i) for i in waiting], executable)):
        if row.get("status") != "ok":
            refused[item["id"]] = row.get("error", json.dumps(row))
            continue
        try:
            found = propose(_component(row, item["id"]), item["id"])
        except VEError as exc:
            refused[item["id"]] = f"search: {exc}"
            continue
        missing = sorted([a, b] for (a, b), hit in found.items() if hit is None)
        if missing:
            unseparated[item["id"]] = missing
            continue
        recorded[item["id"]] = record_situations(item, found)
    checked = list(recorded.values())
    migrated = {}
    for item, row in zip(checked, _rows([_case("readings-validate", env, units, i) for i in checked], executable)):
        if row.get("status") != "ok":
            refused[item["id"]] = row.get("error", json.dumps(row))
            continue
        answer = _component(row, item["id"])["answer"]
        pairs = [p for s in answer["sets"] for p in s["pairs"]]
        apart = [[p["pair"]["first"], p["pair"]["second"]] for p in pairs if not p["pair"]["separated"]] \
            if pairs and "first" in pairs[0]["pair"] else [p for p in pairs if not p["pair"]["separated"]]
        if apart:
            unseparated[item["id"]] = apart
            continue
        migrated[item["id"]] = item
    return {"migrated": migrated, "refused": refused, "unseparated": unseparated}
