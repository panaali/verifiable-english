"""Rebuild the UDHR W6a measurement from the pinned prior run, without model calls."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from ve.document import check_document, coverage, load_document, render_document


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "source" / "udhr.md"
PREVIOUS = Path("/home/seyran/code/manage-agents/pilots/udhr/run-20260928T1800Z")
PIN = "d6495201e9f6229603d2b13427ac68bd8febf5ad80f1cec329bbc3d04d9c7d3a"
raw = SOURCE.read_bytes()
assert hashlib.sha256(raw).hexdigest() == PIN

prior_document = (PREVIOUS / "translation.ve.md").read_bytes()
front, body = prior_document[4:].split(b"\n---\n", 1)
assert body == raw
meta = json.loads(front)
rows = json.loads((PREVIOUS / "units.json").read_text())["units"]
old_metrics = json.loads((PREVIOUS / "metrics.json").read_text())
assert len(meta["units"]) == len(rows) == 129

# The audit found that these inventories are not semantic evidence. Retain
# the choices and the schema-required model references, explicitly recording
# that null-content candidates cannot be distinguished by those models.
audit_gaps = {
    "u017": "Both candidate forces remain unformalised. Reciprocal actors, the act, and the open 'spirit of brotherhood' standard have no checked content; force separation is unverified.",
    "u052": "The invocation-bar and entitlement-exception choices remain unformalised. Genuine prosecution, the two alternative grounds, and the scope of the exception have no checked content.",
    "u112": "The candidate remains unformalised. The absolute restriction, exercise of the referenced rights, and the UN-purpose condition have no checked content.",
    "u114": "The candidate remains unformalised. The interpretive ban, State/group/person scope, and destructive-purpose condition have no checked content.",
}
for reading_set in meta["reading_sets"]:
    uid = reading_set["unit"]
    if uid in audit_gaps:
        for reading in reading_set["readings"]:
            reading["admission"]["why"] += " Schema model references do not distinguish null-content candidates. " + audit_gaps[uid]

for row in rows:
    if row["id"] == "u074":
        assert row.pop("reading_set") == "rs_u074"  # stale after the prior repair
    if row["id"] in audit_gaps:
        assert row["status"] == "UNFORMALISED"
        row["audit_gap"] = audit_gaps[row["id"]]
        row["audit_disposition"] = "unrepaired semantic gap; excluded from claimed and audit-verified coverage"

document = HERE / "translation.ve.md"
document.write_bytes(b"---\n" + json.dumps(meta, ensure_ascii=False, sort_keys=True,
                                           indent=2).encode() + b"\n---\n" + raw)
(HERE / "units.json").write_text(json.dumps({
    "source_sha256": PIN,
    "units": rows,
    "note": "Every null-content reading set remains UNFORMALISED in the manifest; its candidates are not counted as semantic coverage.",
}, ensure_ascii=False, indent=2) + "\n")

doc = load_document(document)
verdict = check_document(document)
cov = coverage(doc)
rendered = render_document(document)
assert doc["source"] == raw
assert cov["source_bytes"] == cov["accounted_bytes"] == len(raw)
assert sum(u["span"][1] - u["span"][0] for u in meta["units"]) == len(raw)
assert [u["span"] for u in meta["units"]] == [r["span"] for r in rows]
assert [r["span"] for r in rows] == [r["span"] for r in json.loads((PREVIOUS / "units.json").read_text())["units"]]
assert all(r["status"] == "UNFORMALISED" for r in rows if r["id"] in audit_gaps)
assert "must not compel each person to belong to an association" in rendered
(HERE / "rendered.md").write_text(rendered)

counts = Counter(r["status"] for r in rows)
bytes_by_status = Counter()
missing = Counter()
for row in rows:
    bytes_by_status[row["status"]] += row["span"][1] - row["span"][0]
    if row["status"] == "UNFORMALISED":
        missing[row["missing_feature"]] += 1
old_aggregation = Counter()
for children in old_metrics["old_to_new_units"].values():
    statuses = {next(r["status"] for r in rows if r["id"] == uid) for uid in children}
    old_aggregation[next(iter(statuses)) if len(statuses) == 1 else "MIXED"] += 1

# The 2026-09-28 audit passed these exact, unchanged units. Its 15 metadata
# labels and u074 total 303 bytes. The four failures above count zero.
audit_passes = set("u001 u002 u021 u030 u034 u053 u056 u062 u065 u069 u072 u095 u104 u109 u113 u074".split())
audit_bytes = sum(r["span"][1] - r["span"][0] for r in rows if r["id"] in audit_passes)
assert audit_bytes == 303
claimed_bytes = sum(bytes_by_status[s] for s in ("CHECKED", "LABELLED", "OPEN", "READINGS"))
assert claimed_bytes == 592
assert cov["bytes_by_status"]["OPEN"] == 593
metrics = {
    "source": {"path": "source/udhr.md", "sha256": PIN, "bytes": len(raw), "fetch_date_utc": "2026-09-27"},
    "baseline": "ve-green-w6a",
    "previous_run": str(PREVIOUS),
    "previous_baseline": "ve-green-layers",
    "old_unit_count": old_metrics["old_unit_count"],
    "old_boundary_aggregation": dict(sorted(old_aggregation.items())),
    "old_to_new_units": old_metrics["old_to_new_units"],
    "unit_scale": "sentence or clause; coordinated regulated acts split; headings separate",
    "bytes_accounted": cov["accounted_bytes"],
    "bytes_accounted_percent": cov["coverage_percent"],
    "unit_count": len(rows),
    "unit_counts_by_status": dict(sorted(counts.items())),
    "bytes_by_status": dict(sorted(bytes_by_status.items())),
    "claimed_covered_bytes": claimed_bytes,
    "claimed_covered_percent": round(100 * claimed_bytes / len(raw), 2),
    "tool_open_bytes_not_claimed": cov["bytes_by_status"]["OPEN"],
    "status_note": "The document tool calls null-content reading inventories OPEN; the manifest keeps them UNFORMALISED because no candidate has checked content.",
    "audit_verified_covered_bytes": audit_bytes,
    "audit_verified_covered_percent": round(100 * audit_bytes / len(raw), 2),
    "audit_verified_substantive_bytes": 57,
    "audit_rejected_units": sorted(audit_gaps),
    "newly_covered_units": [],
    "open_terms": [{k: item[k] for k in ("name", "decided_by", "necessary", "sufficient", "factors")}
                   for item in meta["open_terms"]],
    "reading_sets": [{"id": rs["id"], "unit": rs["unit"], "status": "unelaborated",
                      "candidates": [r["id"] for r in rs["readings"]],
                      "formula_elaborated": False, "semantic_separation_verified": False}
                     for rs in meta["reading_sets"]],
    "missing_feature_tally": dict(sorted(missing.items())),
    "unresolved_reading_feature_tally": dict(sorted(Counter(
        feature for row in rows for feature in row.get("unresolved_features", [])
    ).items())),
    "check_verdicts": {
        "document_load": "PASS", "byte_partition": "PASS", "document_check": "PASS",
        "premises": verdict["premises"], "reading_plan_route": verdict["reading_plan"]["route"],
        "formal_norm_units": sum(type(u["content"]) is dict and "norm" in u["content"] for u in doc["units"]),
        "render": "PASS", "ve_natural": "document norm renderer used; full natural view does not round-trip W1 norm blocks",
        "reading_models": "No semantic separation claimed for null-content candidates.",
    },
    "document_id": verdict["document_id"], "source_id": verdict["source_id"],
    "coverage_tool": cov,
}
(HERE / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"units": len(rows), "statuses": dict(counts), "old_aggregation": dict(old_aggregation),
                  "audit_bytes": audit_bytes, "premises": verdict["premises"]}, ensure_ascii=False))
