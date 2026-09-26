"""Rebuild the W3 pilot document from the pinned, immutable source copy.

This is a deliberately conservative translation. A byte partition is not a
claim that the surrounding English has acquired a formal meaning.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent
SOURCE = ROOT / "source/claude-constitution.md"
RUN = ROOT / "run-20260926T2321Z"
EXPECTED_SHA256 = "fa10ed489e758ab009fe420954a385afbe3b11978afd79c4e9f4ae97e02d50dd"
CHECKED_CLAUSE = "Claude is not a human."
OPEN_PARAGRAPH_START = "As discussed above, Claude’s three main principals"

ENVIRONMENT = {
    "language": "ve.core@0.2",
    "profiles": ["documents@1", "relational-fol@0"],
    "spec_revision": "ve-v0.2-expand2-2026-09-25",
    "vocabulary": {
        "sorts": {"entity": {"description": "An entity discussed in the source.",
                             "verbalisation": {"singular": "entity", "plural": "entities"}}},
        "predicates": {"human": {"arguments": ["entity"],
                                  "description": "The entity is human.",
                                  "verbalisation": "{0} is human",
                                  "negative_verbalisation": "{0} is not human"}},
        "constants": {"claude": {"sort": "entity", "description": "Claude in the source."}},
    },
}
CHECKED_AST = ["not", ["unary", "human", ["const", "claude"]]]

# A named term is a question left for the named role. Empty necessary and
# sufficient arrays mean no criterion has been smuggled in as a definition.
OPEN_TERMS = [
    {"name": "broad_safety", "arguments": ["claude", "context"],
     "decided_by": "anthropic_reviewer", "necessary": [], "sufficient": [],
     "factors": ["human oversight", "principal hierarchy", "current phase of AI development"],
     "precedents": [], "jurisdiction": "claude_constitution", "version": 1},
    {"name": "appropriate_oversight", "arguments": ["mechanism", "context"],
     "decided_by": "anthropic_reviewer", "necessary": [], "sufficient": [],
     "factors": ["human authorization", "ability to correct AI", "misuse of power"],
     "precedents": [], "jurisdiction": "claude_constitution", "version": 1},
    {"name": "genuine_helpfulness", "arguments": ["action", "principal", "context"],
     "decided_by": "anthropic_reviewer", "necessary": [], "sufficient": [],
     "factors": ["benefit to operators and users", "longer term interests", "other people affected"],
     "precedents": [], "jurisdiction": "claude_constitution", "version": 1},
    {"name": "ethical_harm", "arguments": ["action", "context"],
     "decided_by": "anthropic_reviewer", "necessary": [], "sufficient": [],
     "factors": ["severity", "likelihood", "who bears harm", "possible benefits"],
     "precedents": [], "jurisdiction": "claude_constitution", "version": 1},
    {"name": "good_judgment", "arguments": ["action", "context"],
     "decided_by": "anthropic_reviewer", "necessary": [], "sufficient": [],
     "factors": ["competing values", "uncertainty", "context"],
     "precedents": [], "jurisdiction": "claude_constitution", "version": 1},
]

FEATURE_PATTERNS = [
    ("norms", r"\b(?:should|ought|must|we want|we ask|we would like|we hope|never do|need to)\b"),
    ("defaults", r"\b(?:by default|generally|typically|usually|normally|unless|in most cases|absent)\b"),
    ("causation", r"\b(?:because|therefore|causes?|lead(?:s)? to|in order to|as a result|so that)\b"),
    ("quantities", r"\b(?:more|less|most|many|significant|substantial|enormous|large|small|rarely)\b"),
    ("counting", r"\b(?:one|two|three|four|five|first|second|third|number of)\b"),
    ("time", r"\b(?:currently|at the moment|in the future|now|before|after|during|eventually)\b"),
    ("attribution", r"\b(?:we believe|we think|Anthropic believes|our view|we expect)\b"),
    ("modality/belief", r"\b(?:could|might|may|perhaps|likely|uncertain|possible|seems?)\b"),
]


def paragraphs(source: str):
    """Keep delimiters with paragraphs, so concatenation is byte identical."""
    return re.findall(r".*?(?:\n\n|\Z)", source, re.S)[:-1]


def chunks(source: str):
    for paragraph in paragraphs(source):
        if CHECKED_CLAUSE in paragraph:
            before, after = paragraph.split(CHECKED_CLAUSE, 1)
            assert before and after and paragraph.count(CHECKED_CLAUSE) == 1
            yield before, "ordinary"
            yield CHECKED_CLAUSE, "checked"
            yield after, "ordinary"
        else:
            yield paragraph, "ordinary"


def features(text: str):
    found = [name for name, pattern in FEATURE_PATTERNS
             if re.search(pattern, text, re.I)]
    return found or ["other:discourse"]


def unformalised_kind(text: str, reason: str):
    wire_reason = reason.replace("/", "_").replace(":", ".")
    kind = ["unformalised", wire_reason]
    if re.match(r"\s*(?:We|Anthropic) (?:believe|think|expect)\b", text, re.I):
        kind = ["attributed", "anthropic", "believes", kind]
    if re.match(r"\s*Perhaps\b", text, re.I):
        kind = ["hedged", "could", kind]
    return kind, wire_reason


def mentioned_open_terms(text: str):
    patterns = {
        "broad_safety": r"\b(?:broad(?:ly)? safe(?:ty)?|safety)\b",
        "appropriate_oversight": r"\b(?:appropriate oversight|oversight mechanism|human oversight)\b",
        "genuine_helpfulness": r"\b(?:genuine(?:ly)? helpful(?:ness)?|helpfulness)\b",
        "ethical_harm": r"\b(?:harm|harmful|dangerous)\b",
        "good_judgment": r"\b(?:good judgment|wise judgment|sound judgment)\b",
    }
    return [name for name, pattern in patterns.items() if re.search(pattern, text, re.I)]


def main():
    data = SOURCE.read_bytes()
    assert hashlib.sha256(data).hexdigest() == EXPECTED_SHA256, "pinned source changed"
    source = data.decode("utf-8")
    parts = list(chunks(source))
    assert "".join(text for text, _ in parts) == source
    units, ledger = [], []
    cursor = 0
    checked_id = None
    for index, (text, role) in enumerate(parts, 1):
        uid = f"u{index:04d}"
        start = cursor
        cursor += len(text.encode("utf-8"))
        unit = {"id": uid, "span": [start, cursor], "support": "none"}
        entry = {"id": uid, "span": [start, cursor], "source_excerpt": text.strip()[:180]}
        terms = mentioned_open_terms(text)
        if terms:
            entry["open_terms"] = terms
        if role == "checked":
            checked_id = uid
            unit.update(kind="asserted", meaning="specified", support="assumption",
                        content={"fence": uid}, surface="english")
            entry.update(status="CHECKED", note="The isolated clause asserts that Claude is not human.")
        elif text.lstrip().startswith("#") and "\n" not in text.strip():
            unit.update(kind="meta", meaning="specified")
            entry.update(status="LABELLED", note="Section heading; no propositional content asserted.")
        elif text.startswith(OPEN_PARAGRAPH_START):
            unit.update(kind="definition", meaning={"open": ["broad_safety"]})
            entry.update(status="OPEN", open_terms=["broad_safety"],
                         note="The passage names a broad pattern but leaves its test open; other clauses remain unchecked.",
                         other_blockers=features(text))
        else:
            blockers = features(text)
            kind, wire_reason = unformalised_kind(text, blockers[0])
            unit.update(kind=kind, meaning={"unformalised": wire_reason})
            entry.update(status="UNFORMALISED", missing_feature=blockers[0],
                         other_blockers=blockers[1:])
        units.append(unit)
        ledger.append(entry)
    assert cursor == len(data) and checked_id
    meta = {"format": "ve-document@1", "environment": ENVIRONMENT,
            "units": units, "open_terms": OPEN_TERMS, "reading_sets": [],
            "graph": {"root": "claim", "nodes": [{"name": "claim", "ast": CHECKED_AST,
                                                     "unit": checked_id}]}}
    RUN.mkdir(exist_ok=True)
    fence = f"```ve {checked_id}\nClaude is not human.\n```\n"
    document = "---\n" + json.dumps(meta, ensure_ascii=False, separators=(",", ":")) + "\n---\n" + source + fence
    (RUN / "translation.ve.md").write_text(document)
    (RUN / "units.json").write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n")
    from ve.document import check_document, render_document
    result = check_document(RUN / "translation.ve.md")
    coverage = result["coverage"]
    counts = Counter(entry["status"] for entry in ledger)
    bytes_by_status = Counter()
    missing = Counter()
    for entry in ledger:
        bytes_by_status[entry["status"]] += entry["span"][1] - entry["span"][0]
        if entry["status"] == "UNFORMALISED":
            missing[entry["missing_feature"]] += 1
    metrics = {
        "source_sha256": EXPECTED_SHA256,
        "source_bytes": len(data),
        "bytes_accounted": coverage["accounted_bytes"],
        "bytes_accounted_percent": coverage["coverage_percent"],
        "checked_bytes_percent": round(100 * bytes_by_status["CHECKED"] / len(data), 4),
        "units_total": len(ledger),
        "unit_counts_by_status": dict(sorted(counts.items())),
        "bytes_by_status": dict(sorted(bytes_by_status.items())),
        "open_terms": [{"name": term["name"], "decided_by": term["decided_by"],
                        "necessary": term["necessary"], "sufficient": term["sufficient"],
                        "unit_count": sum(term["name"] in entry.get("open_terms", [])
                                          for entry in ledger)} for term in OPEN_TERMS],
        "reading_sets": {"count": 0, "unresolved": 0},
        "missing_feature_tally": dict(sorted(missing.items())),
        "check_verdicts": {
            "document_loaded_and_english_fence_parsed": True,
            "graph_admitted": result["admission"]["admitted"],
            "premises_status": result["premises"]["status"],
            "premises_vacuous": result["admission"]["vacuous"],
            "reading_plan": result["reading_plan"]["route"],
            "source_id": result["source_id"],
            "document_id": result["document_id"],
        },
    }
    (RUN / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n")
    (RUN / "rendered.md").write_text(render_document(RUN / "translation.ve.md"))


if __name__ == "__main__":
    main()
