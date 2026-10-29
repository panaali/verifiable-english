"""Partition the pinned PF text and ask VE to classify every unit (PLAN 7, M3).

The generated document includes source prose and stays beside the private copy, never in git.
Only numeric spans, hashes and status evidence are written here. ``--check`` writes nothing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE.parent))
from safetyfw_common import safety_framework  # noqa: E402
sys.path.insert(0, str(HERE))
import pf_translation as T  # noqa: E402

FSF = safety_framework("build_document")["build_document"]
DEFAULT_SOURCE = Path.home() / "code/manage-agents/pilots/openai-preparedness/source/pf-v2.txt"
TEXT_SHA256 = "d2e3dd5b80e5bb86079911230358e0c2bb78f12435757959e14dae50e4d48d0f"
TEXT_BYTES = 67418
meta, label, unformalised, facts, rule, condition, readings = (getattr(FSF, n) for n in
    ("meta", "label", "unformalised", "facts", "rule", "condition", "readings"))

# The phrase locates the source sentence, never a condition or a unit title. The translation is in rules.d1.ve.
# Separate bullets (•) and sentences get separate spans. An unlisted sentence remains explicitly unformalised.
PLACEMENTS = {
    "By “severe harm” in this document": ("unformalised", "quantity", ("QT",)),
    "1/5th the wall-clock time": ("unformalised", "quantity", ("QT", "ET")),
    "We treat a frontier capability as a Tracked Category": ("readings", "rs12-category", ("SC",)),
    "Require safeguards against misuse meet- ing": ("readings", "rs1-misuse-bio", ("JT", "ET")),
    "Require safeguards against misuse meeting": ("readings", "rs1-misuse-cyb", ("JT", "ET")),
    "Require safeguards meeting High standard against misalignment": ("readings", "rs1-alignment-cyb", ("JT", "ET")),
    "Require security con- trols": ("readings", "rs1-security", ("JT",)),
    "halt further development": ("readings", "rs1-halt", ("ET",)),
    "required to have robust and effective safeguards": ("rule", "f2-deploy", ("JT", "ET")),
    "Such models require additional safeguards": ("rule", "f3-develop", ("JT", "ET")),
    "We will require the following practices": ("rule", "f4-security", ("JT",)),
    "plausible chance of reaching a capability threshold": ("condition", "ot7", ("JT",)),
    "ordinarily not require additional safety measures": ("readings", "rs8-distilled", ("DF", "JT")),
    "every covered model undergoes": ("rule", "f7-evaluations", ("ET",)),
    "The SAG reviews the Capabilities Report": ("rule", "f7-report", ("AT",)),
    "appears likely to cross": ("rule", "f8-start", ("JT", "ET")),
    "planned safeguards needed to minimize": ("rule", "f9-report", ("JT",)),
    "We first identify the plausible ways": ("rule", "f9-risk-paths", ("JT",)),
    "For each of those, we then identify": ("rule", "f9-specific", ()),
    "For each identified safeguard, we identify": ("rule", "f9-efficacy", ()),
    "and an efficacy threshold": ("rule", "f9-threshold", ()),
    "If we find reasonable evidence": ("rule", "f10-validate", ("JT",)),
    "review the 11": ("rule", "f10-review", ("JT",)),
    "could adjust accordingly": ("readings", "rs5-adjustment", ("JT", "WG")),
    "Research Category Potential response": ("readings", "rs4-research", ("readings",)),
    "We will periodically review the latest research": ("unformalised", "event_order", ("ET",)),
    "We will document relevant reports": ("rule", "f14-document", ()),
    "We will track and appropriately investigate": ("rule", "f14-investigate", ("JT",)),
    "and where reports are substantiated": ("rule", "f14-corrective", ("JT",)),
    "We will release information about our Preparedness": ("rule", "f15-disclose", ("JT",)),
    "Additionally, if the model is beyond a High threshold": ("rule", "f15-safeguards", ("JT",)),
    "For each deployment under the Preparedness Framework, providing recommendations": ("rule", "f16-sag-recommend", ()),
    "The Safety and Security Committee (SSC)": ("rule", "f16-ssc-visibility", ()),
    "informed by SAG’s recommendations": ("readings", "rs0-informed", ("readings",)),
    "at least once a year": ("readings", "rs0-year", ("ET",)),
}

READINGS = {
    "rs1-misuse-bio": ("RS1", {"strict": ["f1-misuse-bio-strict"], "default": ["f1-misuse-bio-default"]}),
    "rs1-misuse-cyb": ("RS1", {"strict": ["f1-misuse-cyb-strict"], "default": ["f1-misuse-cyb-default"]}),
    "rs1-alignment-cyb": ("RS1", {"strict": ["f1-alignment-cyb-strict"], "default": ["f1-alignment-cyb-default"]}),
    "rs1-security": ("RS1", {"strict": ["f1-security-strict"], "default": ["f1-security-default"]}),
    "rs1-halt": ("RS1", {"strict": ["f1-halt-strict"], "default": ["f1-halt-default"]}),
    "rs0-informed": ("RS0", {"commitment": ["f16-informed"], "prediction": []}),
    "rs0-year": ("RS0", {"commitment": ["f16-year"], "prediction": []}),
    "rs8-distilled": ("RS8", {"rel": [], "pred": []}),
    "rs5-adjustment": ("RS5", {"within": [], "exception": []}),
    "rs4-research": ("RS4", {"N": [], "P": []}),
    "rs12-category": ("RS12", {"suff": [], "iff": []}),
}
SET_FAMILIES = {"RS0": "readings", "RS1": "DF", "RS8": "DF", "RS5": "readings",
                "RS4": "readings", "RS12": "SC"}
OPEN_FOR = {
    "rs1-misuse-bio": ("ot1", "ot4"), "rs1-misuse-cyb": ("ot1", "ot4"),
    "rs1-alignment-cyb": ("ot1", "ot5"), "rs1-security": ("ot1", "ot3"),
    "rs1-halt": ("ot1", "ot6"),
    "f2-deploy": ("ot1", "ot2"), "f3-develop": ("ot1", "ot10"),
    "f4-security": ("ot1", "ot3"), "f8-start": ("ot9",), "f9-report": ("ot2",),
    "f10-validate": ("ot11",), "f10-review": ("ot11",),
    "f14-investigate": ("ot19",), "f15-disclose": ("ot13",),
    "f14-corrective": ("ot19",), "f15-safeguards": ("ot1", "ot13"), "f9-risk-paths": ("ot2",),
    "rs8-distilled": ("ot20",), "rs5-adjustment": ("ot12",), "rs12-category": ("ot16",),
}

# Table 1's six levels: each matched occurrence gets the two source-stated facts for that row.
FACT_ANCHORS = {
    "bio-high": "[High] The model can pro-",
    "bio-critical": "[Critical] The model can en- able",
    "cyb-high": "[High] The model removes existing",
    "cyb-critical": "[Critical] A tool-augmented model",
    "ais-high": "[High] The model’s impact",
    "ais-critical": "[Critical] The model is ca- pable",
}


def check_source(source):
    if len(source) != TEXT_BYTES or hashlib.sha256(source).hexdigest() != TEXT_SHA256:
        raise ValueError("source differs from PLAN section 1's pinned text")


def segments(source):
    """Byte partition at page boundaries, sentence stops and bullets, retaining every separator."""
    starts = [0]
    for match in re.finditer(rb"\n|(?<=[.!?]) (?=[A-Z])| \xe2\x80\xa2 | and review the 11|(?=\[Critical\])|(?=\[High\])|(?<=\[Critical\])|(?<=\[High\])|(?=Prior to deployment, every covered model)|(?=and decides on next steps)|(?=and where reports are substantiated)|(?=and an efficacy threshold)|(?=and can review decisions)|(?=that either exist or should)|(?=as well as rationale)", source):
        at = match.end() if match.group() == b"\n" else (match.start() if not match.group() else match.start() + 1)
        if starts[-1] < at < len(source):
            starts.append(at)
    return list(zip(starts, starts[1:] + [len(source)]))


def _located(source, spans, phrase):
    at = source.find(phrase.encode())
    if at < 0:
        raise ValueError(f"source anchor absent: {phrase}")
    return next(i for i, (a, b) in enumerate(spans) if a <= at < b)


def _open_terms():
    # PLAN 3.2 owns the 21 questions. D1 gives each a named judgment with its stated decider, without deciding it.
    deciders = {1: "sag", 2: "sag", 3: "unstated", 4: "unstated", 5: "unstated", 6: "unstated",
                7: "sag", 8: "unstated", 9: "openai", 10: "openai", 11: "openai", 12: "openai",
                13: "unstated", 14: "openai", 15: "definition", 16: "sag", 17: "unstated",
                18: "unstated", 19: "unstated", 20: "openai", 21: "unstated"}
    return [{"name": f"ot{n}", "arguments": [], "decided_by": deciders[n],
             "necessary": [], "sufficient": [], "factors": [f"PLAN 3.2 OT{n}"], "precedents": [],
             "jurisdiction": "openai_preparedness_v2", "version": 1} for n in range(1, 22)]


def _model():
    from ve.model import FiniteModel
    env = T.environment()
    relations = {p: [] for p in env.predicates}
    return FiniteModel.from_dict(env, {"complete": True,
        "domains": {"situation": ["s"], "level": list(T.vocabulary.LEVELS),
                    "category": sorted({c for c, _ in T.vocabulary.LEVELS.values()}),
                    "proposal": ["p"], "requirement": ["r"]},
        "constants": {c: c for c in env.constants}, "relations": relations})


def _fallback(page, start, text):
    if page in (1, 3, 17, 18, 19, 20) or 43318 <= start < 48336:
        return label("exposition"), None
    if text.strip().startswith((b"Contents", b"Appendix", b"Table ")):
        return meta(), None
    if b"ISO " in text or b"SOC2" in text or b"NIST " in text or b"FedRAMP" in text:
        return unformalised("external_reference"), "external reference"
    if b"could " in text or b"may " in text or b"might " in text:
        return unformalised("hedged_claim"), "AT"
    if b"before " in text or b"during " in text or b"within " in text:
        return unformalised("event_order"), "ET"
    return unformalised("not_translated"), "readings"


def build(source):
    check_source(source)
    spans = segments(source)
    page_starts = [0] + [i + 1 for i, b in enumerate(source) if b == 10]
    placements = {}
    for phrase, value in PLACEMENTS.items():
        index = _located(source, spans, phrase)
        if index in placements:
            raise ValueError(f"two translations in one source unit: {phrase}")
        placements[index] = value
    for block, phrase in FACT_ANCHORS.items():
        index = _located(source, spans, phrase)
        if index in placements:
            raise ValueError(f"fact and rule in one source unit: {block}")
        placements[index] = ("facts", block, ())
    fact_blocks = {b.id: fs for b, fs in T.facts()}
    model = _model()
    from ve import ast as A
    from ve.ast import formula_to_data
    units, records, sets = [], [], []
    for i, (a, b) in enumerate(spans):
        page = sum(p <= a for p in page_starts)
        uid = f"p{page}-u{i+1}"
        kind, ident, waits = placements.get(i, (None, None, ()))
        if kind is None:
            spec, wait = _fallback(page, a, source[a:b])
        elif kind == "facts":
            spec, wait = facts(ident), None
        elif kind == "unformalised":
            spec, wait = unformalised(ident), None
        elif kind == "readings":
            spec, wait = readings(ident, *OPEN_FOR.get(ident, ())), None
        elif kind == "condition":
            spec, wait = condition(ident), None
        else:
            spec, wait = rule(ident, *OPEN_FOR.get(ident, ())), None
        unit = {"id": uid, "span": [a, b], "kind": spec["kind"], "meaning": spec["meaning"],
                "support": spec["support"]}
        rec = {"id": uid, "span": [a, b], "kind": spec["kind"] if isinstance(spec["kind"], str)
               else spec["kind"][0]}
        if kind == "rule":
            unit["content"] = {"norm": json.loads(T.parsed_rule(ident))}
            rec["rule"] = ident
        elif kind == "facts":
            formulas = fact_blocks[ident]
            conjunction = formulas[0]
            for formula in formulas[1:]:
                conjunction = A.And(conjunction, formula)
            unit["content"] = {"ast": formula_to_data(T.environment(), conjunction)}
            rec["premises"] = [ident]
        elif kind == "readings":
            harness, choices = READINGS[ident]
            sets.append({"id": ident, "unit": uid, "version": 1, "status": "open",
                "readings": [{"id": choice, "kind": "norm", "meaning_id": "pending", "content": None,
                              "admission": {"who": "translator", "why": f"{harness}={choice}: " +
                                            (", ".join(blocks) or "no rule"),
                                            "distinguishing_models": {other: model.model_id for other in choices
                                                                      if other != choice}}}
                             for choice, blocks in choices.items()],
                "models": {model.model_id: model.to_dict()}})
            rec["reading_set"] = ident
        if isinstance(spec["meaning"], dict):
            if "unformalised" in spec["meaning"]:
                rec["reason"] = spec["meaning"]["unformalised"]
            if "open" in spec["meaning"]:
                rec["open_terms"] = spec["meaning"]["open"]
        rec["waits"] = list(waits) if waits else ([wait] if wait else [])
        units.append(unit)
        records.append(rec)
    header = {"format": "ve-document@1", "environment": T.vocabulary.environment(), "units": units,
              "open_terms": _open_terms(), "reading_sets": sets}
    document = b"---\n" + json.dumps(header, indent=1, ensure_ascii=False).encode() + b"\n---\n" + source
    return document, records


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    source = args.source.read_bytes()
    document, records = build(source)
    with tempfile.TemporaryDirectory() as scratch:
        path = Path(scratch) / "pf.d1.ve.md"
        report, statuses = FSF.measure(document, path)
    totals = {}
    for rec in records:
        status = statuses[rec["id"]]
        rec["status"] = status
        totals[status] = totals.get(status, 0) + rec["span"][1] - rec["span"][0]
    spans_text = json.dumps({"source_sha256": TEXT_SHA256, "source_bytes": TEXT_BYTES, "units": records},
                            indent=1, ensure_ascii=False) + "\n"
    coverage_text = json.dumps({"document": "pf.d1.ve.md (built locally, not committed)",
        "document_sha256": hashlib.sha256(document).hexdigest(), **report, "master_bytes_by_status": totals},
        indent=1, sort_keys=True) + "\n"
    if args.check:
        if (HERE / "spans.json").read_text() != spans_text or (HERE / "coverage.json").read_text() != coverage_text:
            raise ValueError("spans.json or coverage.json is out of date")
    else:
        (HERE / "spans.json").write_text(spans_text)
        (HERE / "coverage.json").write_text(coverage_text)
        print(totals)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
