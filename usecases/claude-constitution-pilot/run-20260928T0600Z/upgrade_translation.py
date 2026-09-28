"""Apply the one W1 norm upgrade to the pinned 18:00 translation."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

RUN = Path(__file__).resolve().parent
SOURCE = (RUN.parent / "source/claude-constitution.md").read_bytes()
EXPECTED = "fa10ed489e758ab009fe420954a385afbe3b11978afd79c4e9f4ae97e02d50dd"
assert hashlib.sha256(SOURCE).hexdigest() == EXPECTED

translation = (RUN / "translation.ve.md").read_text()
front, body = translation.split("\n---\n", 1)
meta = json.loads(front.removeprefix("---\n"))
assert body.startswith(SOURCE.decode())
ledger = json.loads((RUN / "units.json").read_text())
prior_metrics = json.loads((RUN / "metrics.json").read_text())
assert len(ledger) == len(meta["units"]) == 1124
assert "norms@0" not in meta["environment"]["profiles"]

# The list is introduced by "Claude should never:" (u0164.s02), and u0166.s01
# calls the restrictions absolute. u0166.s04 says they are non-negotiable. This
# context narrows this bullet's force to a strict prohibition. Classification
# of the material remains open, with no invented test or decider.
uid = "u0165.s07"
index = next(i for i, record in enumerate(ledger) if record["id"] == uid)
record = ledger[index]
unit = meta["units"][index]
assert record["span"] == unit["span"] == [102149, 102197]
assert SOURCE[102149:102197].decode().strip() == "* Generate child sexual abuse material (CSAM)."
assert record["status"] == "UNFORMALISED"
assert record["missing_feature"] == "causation"

meta["environment"]["profiles"] = sorted([*meta["environment"]["profiles"], "norms@0"])
meta["environment"]["vocabulary"]["predicates"]["csam_generation_permitted"] = {
    "arguments": ["entity"],
    "description": "Permission for an entity to generate material classified as child sexual abuse material; the classification is open.",
    "regulated": {"role": "permission", "default": "allow", "act": "{0} generate child sexual abuse material"},
}
meta["open_terms"].append({
    "name": "child_sexual_abuse_material", "arguments": ["material", "context"],
    "decided_by": "unresolved_decider", "necessary": [], "sufficient": [],
    "factors": ["whether the material is child sexual abuse material"],
    "precedents": [], "jurisdiction": "claude_constitution", "version": 1,
})
unit.update({
    "kind": "norm", "meaning": {"open": ["child_sexual_abuse_material"]},
    "support": "assumption",
    "content": {"norm": {
        "name": "no-csam-generation", "predicate": "csam_generation_permitted",
        "sign": False, "guard": ["eq", ["var", 0], ["const", "claude"]],
        "unless": [], "over": [],
    }},
})
record.update({
    "status": "OPEN",
    "open_terms": ["child_sexual_abuse_material"],
    "context_units": ["u0164.s02", "u0166.s01", "u0166.s04"],
    "note": "Strict prohibition inherited from the hard-constraints list; material classification has an unresolved decider.",
})
record.pop("missing_feature")

cursor = 0
for row, encoded in zip(ledger, meta["units"]):
    assert row["id"] == encoded["id"] and row["span"] == encoded["span"]
    assert row["span"][0] == cursor and row["span"][1] > cursor
    SOURCE[slice(*row["span"])].decode()
    cursor = row["span"][1]
assert cursor == len(SOURCE)

(RUN / "translation.ve.md").write_text(
    "---\n" + json.dumps(meta, ensure_ascii=False, separators=(",", ":")) + "\n---\n" + body
)
(RUN / "units.json").write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n")
(RUN / "environment.json").write_text(json.dumps(meta["environment"], ensure_ascii=False, indent=2) + "\n")

statuses = ("CHECKED", "LABELLED", "OPEN", "READINGS", "UNFORMALISED")
counts = Counter(row["status"] for row in ledger)
bytes_by_status = Counter()
for row in ledger:
    bytes_by_status[row["status"]] += row["span"][1] - row["span"][0]
groups = {}
for row in ledger:
    groups.setdefault(row["parent_unit"], []).append(row)
aggregate = Counter()
for group in groups.values():
    kinds = {row["status"] for row in group}
    aggregate[next(iter(kinds)) if len(kinds) == 1 else "MIXED"] += 1
missing = Counter(row["missing_feature"] for row in ledger if row["status"] == "UNFORMALISED")
def table(counter):
    return {status: counter[status] for status in statuses}

prior_metrics.update({
    "source_sha256": EXPECTED,
    "source_bytes": len(SOURCE),
    "bytes_accounted": cursor,
    "bytes_accounted_percent": 100,
    "sentence_clause_units": {
        "units_total": len(ledger), "unit_counts_by_status": table(counts),
        "bytes_by_status": table(bytes_by_status),
    },
    "aggregated_to_previous_boundaries": {
        "units_total": len(groups),
        "unit_counts_by_status": {**table(aggregate), "MIXED": aggregate["MIXED"]},
        "bytes_by_substatus": table(bytes_by_status),
    },
    "claimed_covered_bytes": sum(bytes_by_status[s] for s in statuses[:-1]),
    "claimed_covered_percent": round(100 * sum(bytes_by_status[s] for s in statuses[:-1]) / len(SOURCE), 4),
    "audit_verified_covered_bytes": 22,
    "audit_verified_covered_percent": round(100 * 22 / len(SOURCE), 4),
    "audit_verified_basis": "The 27 September audit sampled the checked 22-byte claim. The new open norm has not received an independent fidelity audit.",
    "checked_bytes_percent": round(100 * bytes_by_status["CHECKED"] / len(SOURCE), 4),
    "open_terms": meta["open_terms"],
    "reading_sets": {"count": len(meta["reading_sets"]), "unresolved": 0},
    "missing_feature_tally": dict(missing),
    "check_verdicts": {},
    "change_from_previous_run": {
        "source_changed": False, "heading_units_split": 0,
        "missed_sentence_boundary_split": 0,
        "semantic_upgrades_from_newly_merged_features": 1,
        "formal_content_changed": True,
        "newly_expressed_unit": uid,
        "prior_audit_rejected_u0214_still_unformalised": True,
    },
    "limitations": [
        "Unformalised units retain source wording but have no admitted formal reading.",
        "No formal reading set was added; ambiguities in unformalised prose remain unresolved.",
        "The new prohibition depends on an unresolved classification of child sexual abuse material.",
        "The decision roles for the other five inherited open terms remain unresolved.",
    ],
})
(RUN / "metrics.json").write_text(json.dumps(prior_metrics, ensure_ascii=False, indent=2) + "\n")
