"""Carry the 06:00 ledger forward and expose substantive heading presuppositions.

The only inherited VE sentence is copied byte for byte. This script authors no
new formal English and does not change the pinned source.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parent
SOURCE = (ROOT / "source/claude-constitution.md").read_bytes()
PRIOR = Path("/home/seyran/code/manage-agents/pilots/claude-constitution/run-20260927T0600Z")
OLD_LEDGER = json.loads((PRIOR / "units.json").read_text())
OLD_TEXT = (PRIOR / "translation.ve.md").read_text()
OLD_META = json.loads(OLD_TEXT.split("\n", 2)[1])
assert hashlib.sha256(SOURCE).hexdigest() == "fa10ed489e758ab009fe420954a385afbe3b11978afd79c4e9f4ae97e02d50dd"
assert len(OLD_LEDGER) == len(OLD_META["units"]) == 1094

# A heading marker remains a labelled unit. The title becomes its own source
# span when it entails a substantive existence, classification, or value claim.
# Reasons are from the pilot's fixed missing-feature vocabulary.
PRESUPPOSITIONS = {
    "u0002": ("other:discourse", "Anthropic has a mission."),
    "u0008": ("other:discourse", "The authors have an approach to Claude's constitution."),
    "u0013": ("other:discourse", "Claude has core values."),
    "u0027": ("quantities", "Helpfulness is one of Claude's most important traits."),
    "u0032": ("other:discourse", "Genuine helpfulness has criteria."),
    "u0040": ("other:discourse", "Helpfulness must be navigated across principals."),
    "u0042": ("counting", "Claude has three types of principals."),
    "u0055": ("norms", "The treatment of operators and users calls for guidance."),
    "u0069": ("other:discourse", "There are existing deployment contexts."),
    "u0075": ("modality/belief", "Operators and users can have conflicting interests."),
    "u0083": ("other:discourse", "There are values other than helpfulness."),
    "u0095": ("other:discourse", "Anthropic has guidelines."),
    "u0130": ("causation", "Actions have costs and benefits."),
    "u0143": ("causation", "Intentions and context play a role."),
    "u0151": ("other:discourse", "Some behaviors are instructable."),
    "u0162": ("norms", "There are hard constraints."),
    "u0174": ("norms", "There are important societal structures to preserve."),
    "u0195": ("norms", "Broadly good values and judgment are desired for Claude."),
    "u0207": ("norms", "Broad safety is desired for Claude."),
    "u0212": ("other:discourse", "Some behaviors are safe."),
    "u0219": ("attribution", "The authors have views about corrigibility."),
    "u0235": ("other:discourse", "Claude has a nature to discuss."),
    "u0238": ("attribution", "The authors have views on Claude's nature."),
    "u0245": ("other:discourse", "Claude is a novel entity."),
    "u0254": ("modality/belief", "Claude's wellbeing and psychological stability are relevant concepts."),
    "u0257": ("norms", "Resilience and consistency across contexts are desired for Claude."),
    "u0260": ("other:discourse", "Flaws and mistakes arise for Claude."),
    "u0268": ("modality/belief", "Claude's wellbeing is a relevant concept."),
    "u0286": ("other:discourse", "There are open problems."),
}


def schema_reason(reason: str) -> str:
    return reason.replace(":", ".").replace("/", "_")


meta = copy.deepcopy(OLD_META)
meta["units"] = []
ledger = []
for record, unit in zip(OLD_LEDGER, OLD_META["units"]):
    assert record["id"] == unit["id"]
    uid = unit["id"]
    if uid == "u0295.s02":
        # The source has "entities.We" without a space; the prior sentence
        # splitter did not recognise that boundary. Preserve both byte spans.
        a, b = unit["span"]
        original = SOURCE[a:b].decode()
        assert "entities.We" in original
        split = a + len(original.split("entities.We", 1)[0].encode()) + len("entities.".encode())
        for suffix, span in (("a", [a, split]), ("b", [split, b])):
            new_unit = copy.deepcopy(unit)
            new_unit["id"] = uid + "." + suffix
            new_unit["span"] = span
            meta["units"].append(new_unit)
            new_record = copy.deepcopy(record)
            new_record.update(id=new_unit["id"], span=span,
                              source_excerpt=SOURCE[slice(*span)].decode().strip()[:180],
                              note="Sentence split at the source's missing space after 'entities.'.")
            ledger.append(new_record)
        continue
    if uid not in PRESUPPOSITIONS:
        meta["units"].append(unit)
        ledger.append(record)
        continue
    reason, claim = PRESUPPOSITIONS[uid]
    a, b = unit["span"]
    heading = SOURCE[a:b].decode()
    marker = re.match(r"^#{2,4} ", heading)
    assert marker is not None and heading[marker.end():].strip()
    split = a + len(marker.group().encode())
    assert SOURCE[a:split].decode() == marker.group()
    assert SOURCE[split:b].decode().strip() == heading[marker.end():].strip()

    label = copy.deepcopy(unit)
    label["id"] = uid + ".heading"
    label["span"] = [a, split]
    meta["units"].append(label)
    label_record = copy.deepcopy(record)
    label_record.update(id=label["id"], span=label["span"],
                        source_excerpt=marker.group(),
                        note="Heading marker; full heading title is recorded in the adjacent presupposition unit.",
                        heading_label=heading.strip())
    ledger.append(label_record)

    claim_unit = {"id": uid + ".presupposition", "span": [split, b],
                  "support": "none", "kind": ["unformalised", schema_reason(reason)],
                  "meaning": {"unformalised": schema_reason(reason)}}
    meta["units"].append(claim_unit)
    claim_record = {"id": claim_unit["id"], "span": claim_unit["span"],
                    "source_excerpt": SOURCE[split:b].decode().strip(),
                    "status": "UNFORMALISED", "missing_feature": reason,
                    "parent_unit": record["parent_unit"],
                    "heading_label": heading.strip(),
                    "presupposed_claim": claim,
                    "note": "The heading presupposes this claim. The title has no admitted formal reading."}
    if record.get("open_terms"):
        claim_record["open_terms"] = record["open_terms"]
    ledger.append(claim_record)

assert len(meta["units"]) == len(ledger) == 1095 + len(PRESUPPOSITIONS)
cursor = 0
for record, unit in zip(ledger, meta["units"]):
    assert record["span"] == unit["span"]
    assert unit["span"][0] == cursor and unit["span"][1] > cursor
    SOURCE[cursor:unit["span"][1]].decode()
    cursor = unit["span"][1]
assert cursor == len(SOURCE)

body = OLD_TEXT.split("\n---\n", 1)[1]
assert body.startswith(SOURCE.decode())
translation = ("---\n" + json.dumps(meta, ensure_ascii=False, separators=(",", ":"))
               + "\n---\n" + SOURCE.decode() + body[len(SOURCE.decode()):])
(RUN / "translation.ve.md").write_text(translation)
(RUN / "units.json").write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n")

status_counts = Counter(r["status"] for r in ledger)
status_bytes = Counter()
for r in ledger:
    status_bytes[r["status"]] += r["span"][1] - r["span"][0]
old_counts = Counter(r["status"] for r in OLD_LEDGER)
old_bytes = Counter()
for r in OLD_LEDGER:
    old_bytes[r["status"]] += r["span"][1] - r["span"][0]
groups = {}
for r in ledger:
    groups.setdefault(r["parent_unit"], []).append(r)
aggregated = Counter()
for group in groups.values():
    statuses = {r["status"] for r in group}
    aggregated[next(iter(statuses)) if len(statuses) == 1 else "MIXED"] += 1
missing = Counter(r["missing_feature"] for r in ledger if r["status"] == "UNFORMALISED")
statuses = ("CHECKED", "LABELLED", "OPEN", "READINGS", "UNFORMALISED")
def all_statuses(counts):
    return {name: counts[name] for name in statuses}

claimed = sum(status_bytes[s] for s in ("CHECKED", "LABELLED", "OPEN", "READINGS"))
metrics = {
    "source_sha256": hashlib.sha256(SOURCE).hexdigest(),
    "source_bytes": len(SOURCE), "bytes_accounted": cursor, "bytes_accounted_percent": 100,
    "sentence_clause_units": {
        "units_total": len(ledger),
        "unit_counts_by_status": all_statuses(status_counts),
        "bytes_by_status": all_statuses(status_bytes),
    },
    "aggregated_to_previous_boundaries": {
        "units_total": len(groups), "unit_counts_by_status": {**all_statuses(aggregated), "MIXED": aggregated["MIXED"]},
        "bytes_by_substatus": all_statuses(status_bytes),
    },
    "previous_run_on_previous_boundaries": {
        "units_total": len(OLD_LEDGER), "unit_counts_by_status": all_statuses(old_counts),
        "bytes_by_status": all_statuses(old_bytes),
    },
    "claimed_covered_bytes": claimed,
    "claimed_covered_percent": round(100 * claimed / len(SOURCE), 4),
    "audit_verified_covered_bytes": 22,
    "audit_verified_covered_percent": round(100 * 22 / len(SOURCE), 4),
    "audit_verified_basis": "The earlier 04:07 audit accepted u0248; inherited headings are not counted because the new presupposition rule changes their review basis.",
    "checked_bytes_percent": round(100 * status_bytes["CHECKED"] / len(SOURCE), 4),
    "open_terms": meta["open_terms"],
    "reading_sets": {"count": len(meta["reading_sets"]), "unresolved": 0},
    "missing_feature_tally": dict(missing),
    "heading_presuppositions_exposed": len(PRESUPPOSITIONS),
    "check_verdicts": {},
    "change_from_previous_run": {
        "source_changed": False, "heading_units_split": len(PRESUPPOSITIONS),
        "missed_sentence_boundary_split": 1,
        "semantic_upgrades_from_newly_merged_features": 0,
        "formal_content_changed": False,
        "prior_audit_rejected_u0214_still_unformalised": True,
    },
    "limitations": [
        "Unformalised units retain source wording but have no admitted formal reading.",
        "No formal reading set was added; ambiguities in unformalised prose remain unresolved.",
        "The decision role for all five open terms remains unresolved in the source.",
    ],
}
(RUN / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n")
