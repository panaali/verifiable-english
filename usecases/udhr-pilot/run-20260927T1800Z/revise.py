"""Revise the pinned prior translation after its audit, without editing source."""
import copy
import hashlib
import json
from pathlib import Path

from ve.document import check_document, coverage, load_document, render_document


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "source" / "udhr.md"
DOCUMENT = HERE / "translation.ve.md"
PREVIOUS = Path("/home/seyran/code/manage-agents/pilots/udhr/run-20260927T0646Z")
PIN = "d6495201e9f6229603d2b13427ac68bd8febf5ad80f1cec329bbc3d04d9c7d3a"
raw = SOURCE.read_bytes()
assert hashlib.sha256(raw).hexdigest() == PIN
prior = (PREVIOUS / "translation.ve.md").read_bytes()
front, body = prior[4:].split(b"\n---\n", 1)
assert body == raw
meta = json.loads(front)
old_rows = json.loads((PREVIOUS / "units.json").read_text())["units"]
assert len(meta["units"]) == len(old_rows) == 114
meta["open_terms"].append({
    "name": "spirit_of_brotherhood", "arguments": [],
    "decided_by": "human_rights_interpreter", "necessary": [], "sufficient": [],
    "factors": ["reciprocal conduct", "meaning of brotherhood"],
    "precedents": [], "jurisdiction": "universal", "version": 1,
})
meta["open_terms"].append({
    "name": "justice", "arguments": [],
    "decided_by": "human_rights_interpreter", "necessary": [], "sufficient": [],
    "factors": ["meaning of justice in the Preamble", "scope of the claimed foundation"],
    "precedents": [], "jurisdiction": "universal", "version": 1,
})

# These prior units contain distinct coordinated or purpose clauses. Each cut
# stays inside its old byte span, so aggregation back to that span is exact.
cuts = {
    "u008": [b" and have determined"],
    "u013": [b", to the end that"],
}
new_units = []
new_rows = []
old_to_new = {}
for old_unit, old_row in zip(meta["units"], old_rows):
    uid = old_unit["id"]
    lo, hi = old_unit["span"]
    piece = raw[lo:hi]
    positions = [0] + [piece.index(c) for c in cuts.get(uid, [])] + [len(piece)]
    assert positions == sorted(set(positions))
    old_to_new[uid] = []
    for index, (a, b) in enumerate(zip(positions, positions[1:])):
        unit = copy.deepcopy(old_unit)
        row = copy.deepcopy(old_row)
        new_id = uid if len(positions) == 2 else uid + chr(ord("a") + index)
        unit["id"] = row["id"] = new_id
        unit["span"] = row["span"] = [lo + a, lo + b]
        row["source"] = raw[lo + a:lo + b].decode().strip()
        row["old_unit"] = uid
        old_to_new[uid].append(new_id)
        # The first split clause attributes the proclamation; the later
        # purpose clauses carry obligations whose logic is unavailable.
        if uid == "u013" and index > 0:
            unit["kind"] = ["unformalised", "norms"]
            unit["meaning"] = {"unformalised": "norms"}
            row["missing_feature"] = "norms"
        new_units.append(unit)
        new_rows.append(row)

# The prior audit rejected u017/u031/u074/u114. The same no-formula defect
# also applies to the other substantive OPEN and READINGS units. Their named
# terms and reading inventories remain visible, but they receive no coverage.
reasons = {
    "u010": "other:evaluative_open_claim",
    "u017": "norms",
    "u031": "norms",
    "u052": "norms",
    "u060": "other:evaluative_open_claim",
    "u074": "norms",
    "u112": "norms",
    "u114": "norms",
}
for unit, row in zip(new_units, new_rows):
    if row["old_unit"] == "u003":
        row["open_terms"] = ["inherent_dignity", "inalienable_rights", "justice"]
    reason = reasons.get(row["old_unit"])
    if reason is None:
        continue
    code = reason.replace(":", "_").replace("/", "_")
    unit["kind"] = ["unformalised", code]
    unit["meaning"] = {"unformalised": code}
    row["status"] = "UNFORMALISED"
    row["missing_feature"] = reason
    if row["old_unit"] in {"u017", "u052", "u074", "u112", "u114"}:
        row["reading_elaboration"] = "pending; candidates have no VE content"
    if row["old_unit"] == "u052":
        row["unresolved_features"] = ["norms", "other:exception_scope"]
    if row["old_unit"] in {"u074", "u112", "u114"}:
        row["unresolved_features"] = ["norms"]
    if row["old_unit"] == "u017":
        row["open_terms"] = ["spirit_of_brotherhood"]

# Remove readings that the audit found to change normative force into mere
# physical possibility. The remaining candidates are explicitly unelaborated.
by_unit = {item["unit"]: item for item in meta["reading_sets"]}
for uid in ("u074", "u112", "u114"):
    rs = by_unit[uid]
    rs["readings"] = [rs["readings"][0]]
    new_id = {"u074": "compulsion_prohibited", "u112": "exercise_restricted",
              "u114": "interpretive_bar"}[uid]
    rs["readings"][0]["id"] = new_id
    rs["readings"][0]["meaning_id"] = rs["id"] + "." + new_id
    rs["readings"][0]["admission"]["distinguishing_models"] = {}
    rs["models"] = {}
    rs["readings"][0]["admission"]["why"] = (
        "Unelaborated legal prohibition or restriction; actor, action, scope, "
        "and normative force still require VE content. No model is claimed."
    )
for uid in ("u017", "u052"):
    rs = by_unit[uid]
    for reading in rs["readings"]:
        reading["kind"] = "norm"
    if uid == "u017":
        rs["readings"][0]["admission"]["why"] = (
            "Possible strict obligation for all human beings to act reciprocally "
            "in a spirit of brotherhood. The action and open term have no VE formula; "
            "the schema model reference cannot separate null-content candidates."
        )
        rs["readings"][1]["admission"]["why"] = (
            "Possible defeasible recommendation applying generally to human beings. "
            "Defeasibility and the reciprocal open action have no VE formula; "
            "the schema model reference cannot separate null-content candidates."
        )
    else:
        first, second = rs["readings"]
        first["id"] = "invocation_barred"
        first["meaning_id"] = rs["id"] + ".invocation_barred"
        first["admission"]["distinguishing_models"] = {"right_inapplicable":
            next(iter(first["admission"]["distinguishing_models"].values()))}
        first["admission"]["why"] = (
            "Possible prohibition on invoking asylum for the specified prosecutions. "
            "The genuinely and non-political conditions have no VE formula; "
            "the schema model reference cannot separate null-content candidates."
        )
        second["id"] = "right_inapplicable"
        second["meaning_id"] = rs["id"] + ".right_inapplicable"
        second["admission"]["distinguishing_models"] = {"invocation_barred":
            next(iter(second["admission"]["distinguishing_models"].values()))}
        second["admission"]["why"] = (
            "Possible exception to the asylum entitlement itself in those cases. "
            "The triggering conditions have no VE formula; the schema model "
            "reference cannot separate null-content candidates."
        )

meta["units"] = new_units
DOCUMENT.write_bytes(b"---\n" + json.dumps(meta, ensure_ascii=False, sort_keys=True,
                                             indent=2).encode() + b"\n---\n" + raw)
(HERE / "units.json").write_text(json.dumps({
    "source_sha256": PIN,
    "units": new_rows,
    "note": "UNFORMALISED units retain source and open-term/reading metadata; none claims checked substantive content.",
}, ensure_ascii=False, indent=2) + "\n")

doc = load_document(DOCUMENT)
verdict = check_document(DOCUMENT)
cov = coverage(doc)
assert doc["source"] == raw
assert cov["source_bytes"] == cov["accounted_bytes"] == len(raw)
assert sum(u["span"][1] - u["span"][0] for u in new_units) == len(raw)
from collections import Counter
counts = Counter(r["status"] for r in new_rows)
bytes_by_status = Counter()
missing = Counter()
for row in new_rows:
    bytes_by_status[row["status"]] += row["span"][1] - row["span"][0]
    if row["status"] == "UNFORMALISED":
        missing[row["missing_feature"]] += 1

# Only the 16 metadata units named as passes by the prior independent audit
# count as audit-verified coverage. The audit passed no substantive clause.
audit_passes = "u011 u021 u023 u026 u028 u030 u036 u040 u056 u069 u072 u075 u083 u104 u107 u113".split()
audit_verified_bytes = sum(
    r["span"][1] - r["span"][0] for r in new_rows if r["id"] in audit_passes
)
assert len(audit_passes) == 16
old_aggregated = Counter()
for row in old_rows:
    children = [r for r in new_rows if r["old_unit"] == row["id"]]
    assert children[0]["span"][0] == row["span"][0]
    assert children[-1]["span"][1] == row["span"][1]
    statuses = {r["status"] for r in children}
    old_aggregated[next(iter(statuses)) if len(statuses) == 1 else "MIXED"] += 1

metrics = {
    "source": {"path": "source/udhr.md", "sha256": PIN, "bytes": len(raw),
               "fetch_date_utc": "2026-09-27"},
    "baseline": "ve-green-flaky",
    "previous_run": "/home/seyran/code/manage-agents/pilots/udhr/run-20260927T0646Z",
    "old_unit_count": len(old_rows),
    "old_boundary_aggregation": dict(sorted(old_aggregated.items())),
    "old_to_new_units": old_to_new,
    "unit_scale": "sentence or clause; headings and standalone speaker/transition fragments separate",
    "bytes_accounted": cov["accounted_bytes"],
    "bytes_accounted_percent": cov["coverage_percent"],
    "unit_count": len(new_rows),
    "unit_counts_by_status": dict(sorted(counts.items())),
    "bytes_by_status": dict(sorted(bytes_by_status.items())),
    "claimed_covered_bytes": sum(bytes_by_status[s] for s in ("CHECKED", "LABELLED", "OPEN", "READINGS")),
    "claimed_covered_percent": round(100 * sum(bytes_by_status[s] for s in
        ("CHECKED", "LABELLED", "OPEN", "READINGS")) / len(raw), 2),
    "audit_verified_covered_bytes": audit_verified_bytes,
    "audit_verified_covered_percent": round(100 * audit_verified_bytes / len(raw), 2),
    "audit_verified_substantive_bytes": 0,
    "open_terms": [{k: item[k] for k in ("name", "decided_by", "necessary", "sufficient", "factors")}
                   for item in meta["open_terms"]],
    "reading_sets": [{"id": rs["id"], "unit": rs["unit"], "status": "unelaborated",
                      "candidates": [r["id"] for r in rs["readings"]],
                      "formula_elaborated": False,
                      "semantic_separation_verified": False}
                     for rs in meta["reading_sets"]],
    "missing_feature_tally": dict(sorted(missing.items())),
    "unresolved_reading_feature_tally": dict(sorted(Counter(
        feature for row in new_rows for feature in row.get("unresolved_features", [])
    ).items())),
    "check_verdicts": {
        "document_load": "PASS", "byte_partition": "PASS", "document_check": "PASS",
        "premises": verdict["premises"],
        "reading_plan_route": verdict["reading_plan"]["route"],
        "formal_formula_units": sum(u["content"] is not None for u in doc["units"]),
        "render": "PASS",
        "ve_natural": "not applicable: no formal formulas to render",
        "reading_models": "Unelaborated candidates; schema references for the two multi-reading sets do not prove separation.",
    },
    "document_id": verdict["document_id"],
    "source_id": verdict["source_id"],
    "coverage_tool": cov,
}
(HERE / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n")
(HERE / "rendered.md").write_text(render_document(DOCUMENT))
print(json.dumps({"units": len(new_rows), "statuses": dict(counts),
                  "old_aggregate": dict(old_aggregated), "audit_bytes": audit_verified_bytes,
                  "check": verdict["premises"]}, ensure_ascii=False))
