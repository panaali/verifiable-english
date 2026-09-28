"""Reproduce the 2026-09-28 UDHR pilot from the pinned prior translation."""
from __future__ import annotations

from collections import Counter
import copy
import hashlib
import json
from pathlib import Path

from ve.document import check_document, coverage, load_document, render_document
from ve.environment import Environment
from ve.model import FiniteModel


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "source" / "udhr.md"
PREVIOUS = Path("/home/seyran/code/manage-agents/pilots/udhr/run-20260927T1800Z")
PIN = "d6495201e9f6229603d2b13427ac68bd8febf5ad80f1cec329bbc3d04d9c7d3a"
raw = SOURCE.read_bytes()
assert hashlib.sha256(raw).hexdigest() == PIN
front, body = (PREVIOUS / "translation.ve.md").read_bytes()[4:].split(b"\n---\n", 1)
assert body == raw
meta = json.loads(front)
previous_rows = json.loads((PREVIOUS / "units.json").read_text())["units"]
assert len(meta["units"]) == len(previous_rows) == 116

# Cut only at coordinated clauses or separately regulated acts. The source
# bytes, including punctuation and whitespace, stay in exactly one child.
cuts = {
    "u013b": [b" and by progressive measures"],
    "u033": [b" and against any incitement"],
    "u045": [b", nor to attacks"],
    "u071": [b" and to seek"],
    "u079": [b" and shall be held"],
    "u084": [b", to free choice", b", to just and favourable", b" and to protection"],
    "u099": [b" and higher education"],
    "u100": [b" and to the strengthening"],
    "u105": [b", to enjoy the arts", b" and to share"],
    "u111": [b" and of meeting"],
}
units = []
rows = []
previous_to_new = {}
for old_unit, old_row in zip(meta["units"], previous_rows):
    uid = old_unit["id"]
    assert old_row["id"] == uid and old_unit["span"] == old_row["span"]
    lo, hi = old_unit["span"]
    piece = raw[lo:hi]
    points = [0] + [piece.index(marker) for marker in cuts.get(uid, [])] + [len(piece)]
    assert points == sorted(set(points))
    previous_to_new[uid] = []
    for index, (start, end) in enumerate(zip(points, points[1:])):
        unit = copy.deepcopy(old_unit)
        row = copy.deepcopy(old_row)
        child = uid if len(points) == 2 else uid + chr(ord("a") + index)
        unit["id"] = row["id"] = child
        unit["span"] = row["span"] = [lo + start, lo + end]
        row["source"] = raw[lo + start:lo + end].decode().strip()
        row["previous_unit"] = uid
        previous_to_new[uid].append(child)
        units.append(unit)
        rows.append(row)

# Keep the speech act visible even when its inner proposition has no formal
# content yet. These are kind labels, not upgrades to covered status.
attributed_kinds = {
    "u005": ["attributed", "unstated", "says", "asserted"],
    "u008a": ["attributed", "peoples_of_un", "believes", "asserted"],
    "u008b": ["attributed", "peoples_of_un", "intends", "norm"],
    "u009": ["attributed", "member_states", "promised", "norm"],
    "u013a": ["attributed", "general_assembly", "says", "norm"],
}
for unit, row in zip(units, rows):
    if unit["id"] in attributed_kinds:
        unit["kind"] = attributed_kinds[unit["id"]]
        row["semantic_kind"] = attributed_kinds[unit["id"]]
for uid, label in {
    "u003": "evaluative causal claim",
    "u004": "causal claim with evaluative words",
    "u006": "evaluative conditional claim with should",
    "u007": "evaluative claim",
    "u010": "evaluative claim",
    "u060": "evaluative claim",
}.items():
    next(row for row in rows if row["id"] == uid)["semantic_kind"] = label

# W1 norm content is now admitted inside W2 documents. The previous audit
# rejected u074 because it offered a physical-possibility reading. The only
# retained reading was a legal prohibition, which is expressible as a strict
# norm over every coercing actor and affected person. Its guard is universal,
# so the regulated predicate's fallback default never adds another case.
env = meta["environment"]
env["profiles"] = ["documents@1", "norms@0", "relational-fol@0"]
env["vocabulary"]["sorts"]["actor"] = {
    "description": "a person, group, or institution capable of compelling a person",
    "verbalisation": {"singular": "actor", "plural": "actors"},
}
env["vocabulary"]["predicates"]["compel_association_membership_permitted"] = {
    "arguments": ["actor", "person"],
    "description": "The actor is permitted to compel the person to belong to an association",
    "regulated": {
        "role": "permission", "default": "allow",
        "act": "{0} compel {1} to belong to an association",
    },
}
unit_074 = next(unit for unit in units if unit["id"] == "u074")
row_074 = next(row for row in rows if row["id"] == "u074")
assert row_074["status"] == "UNFORMALISED"
unit_074["kind"] = "norm"
unit_074["meaning"] = "specified"
unit_074["status"] = "CHECKED"
unit_074["content"] = {"norm": {
    "name": "no-compelled-association-membership",
    "predicate": "compel_association_membership_permitted",
    "sign": False,
    "guard": ["top"],
    "unless": [],
    "over": [],
}}
row_074["status"] = "CHECKED"
del row_074["missing_feature"]
row_074.pop("reading_elaboration", None)
row_074.pop("unresolved_features", None)
row_074["audit_repair"] = (
    "Strict legal prohibition: every actor is forbidden to compel any person "
    "to belong to an association. The rejected physical-possibility reading is absent."
)
meta["reading_sets"] = [r for r in meta["reading_sets"] if r["unit"] != "u074"]
assert len(meta["reading_sets"]) == 4
# Existing null-content reading inventories cite complete model records. Their
# model identities must be rebound when the environment gains a sort and a
# regulated predicate; this does not turn them into semantic evidence.
for reading_set in meta["reading_sets"]:
    replacements = {}
    for model_id, model in reading_set.get("models", {}).items():
        model["domains"]["actor"] = ["a"]
        model["relations"]["compel_association_membership_permitted"] = []
        replacements[model_id] = FiniteModel.from_dict(Environment(env), model).model_id
    reading_set["models"] = {replacements.get(mid, mid): model
                             for mid, model in reading_set.get("models", {}).items()}
    for reading in reading_set["readings"]:
        refs = reading["admission"]["distinguishing_models"]
        reading["admission"]["distinguishing_models"] = {
            other: replacements.get(mid, mid) for other, mid in refs.items()}
meta["units"] = units

document = HERE / "translation.ve.md"
document.write_bytes(b"---\n" + json.dumps(meta, ensure_ascii=False, sort_keys=True,
                                           indent=2).encode() + b"\n---\n" + raw)
(HERE / "units.json").write_text(json.dumps({
    "source_sha256": PIN,
    "units": rows,
    "note": "The source is pinned. UNFORMALISED rows retain open-term and reading metadata without claiming formal content.",
}, ensure_ascii=False, indent=2) + "\n")

doc = load_document(document)
verdict = check_document(document)
cov = coverage(doc)
rendered = render_document(document)
assert doc["source"] == raw
assert cov["source_bytes"] == cov["accounted_bytes"] == len(raw)
assert sum(u["span"][1] - u["span"][0] for u in units) == len(raw)
assert "must not compel each person to belong to an association" in rendered
assert next(u for u in doc["units"] if u["id"] == "u074")["content"] is not None
(HERE / "rendered.md").write_text(rendered)

counts = Counter(r["status"] for r in rows)
bytes_by_status = Counter()
missing = Counter()
for row in rows:
    bytes_by_status[row["status"]] += row["span"][1] - row["span"][0]
    if row["status"] == "UNFORMALISED":
        missing[row["missing_feature"]] += 1
old_aggregation = Counter()
for previous in previous_rows:
    children = [r for r in rows if r["previous_unit"] == previous["id"]]
    assert children[0]["span"][0] == previous["span"][0]
    assert children[-1]["span"][1] == previous["span"][1]
    statuses = {child["status"] for child in children}
    old_aggregation[next(iter(statuses)) if len(statuses) == 1 else "MIXED"] += 1

# The September 27 independent audit passed sixteen metadata units. It did
# not inspect the new u074 formula, so that new claim is not audit-verified.
audit_passes = "u011 u021 u023 u026 u028 u030 u036 u040 u056 u069 u072 u075 u083 u104 u107 u113".split()
audit_bytes = sum(r["span"][1] - r["span"][0] for r in rows if r["id"] in audit_passes)
assert audit_bytes == 236
claimed_bytes = sum(bytes_by_status[s] for s in ("CHECKED", "LABELLED", "OPEN", "READINGS"))
tool_open_unelaborated = cov["bytes_by_status"].get("OPEN", 0)
assert tool_open_unelaborated == sum(
    r["span"][1] - r["span"][0] for r in rows
    if any(rs["unit"] == r["id"] for rs in meta["reading_sets"])
)
metrics = {
    "source": {"path": "source/udhr.md", "sha256": PIN, "bytes": len(raw),
               "fetch_date_utc": "2026-09-27"},
    "baseline": "ve-green-layers",
    "previous_run": str(PREVIOUS),
    "previous_baseline": "ve-green-flaky",
    "old_unit_count": len(previous_rows),
    "old_boundary_aggregation": dict(sorted(old_aggregation.items())),
    "old_to_new_units": previous_to_new,
    "unit_scale": "sentence or clause; coordinated regulated acts split; headings separate",
    "bytes_accounted": cov["accounted_bytes"],
    "bytes_accounted_percent": cov["coverage_percent"],
    "unit_count": len(rows),
    "unit_counts_by_status": dict(sorted(counts.items())),
    "bytes_by_status": dict(sorted(bytes_by_status.items())),
    "claimed_covered_bytes": claimed_bytes,
    "claimed_covered_percent": round(100 * claimed_bytes / len(raw), 2),
    "tool_open_bytes_not_claimed": tool_open_unelaborated,
    "status_note": "The document tool calls null-content reading inventories OPEN; unit metrics keep them UNFORMALISED because no candidate has a checked formula.",
    "audit_verified_covered_bytes": audit_bytes,
    "audit_verified_covered_percent": round(100 * audit_bytes / len(raw), 2),
    "audit_verified_substantive_bytes": 0,
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
        "premises": verdict["premises"],
        "reading_plan_route": verdict["reading_plan"]["route"],
        "formal_norm_units": sum(type(u["content"]) is dict and "norm" in u["content"]
                                 for u in doc["units"]),
        "render": "PASS",
        "ve_natural": "not applicable to W1 norm content; document render checked",
        "reading_models": "Unelaborated candidates do not establish semantic separation.",
    },
    "document_id": verdict["document_id"],
    "source_id": verdict["source_id"],
    "coverage_tool": cov,
}
(HERE / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"units": len(rows), "statuses": dict(counts),
                  "old_aggregation": dict(old_aggregation), "audit_bytes": audit_bytes,
                  "premises": verdict["premises"]}, ensure_ascii=False))
