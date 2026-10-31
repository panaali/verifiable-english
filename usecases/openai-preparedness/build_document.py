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
    "Contribute towards im- proved public policy": ("readings", "rs1-contrib-bio", ("AP",)),
    "Contribute towards improved cyberdefense policies": ("readings", "rs1-contrib-cyb", ("AP",)),
    "halt further development": ("readings", "rs1-halt", ("ET",)),
    "required to have robust and effective safeguards": ("readings", "rs3-deploy", ("JT", "ET")),
    "We do not deploy models that reach a High capability threshold": ("readings", "rs3-no-deploy", ("JT",)),
    "Such models require additional safeguards": ("readings", "rs18-develop", ("JT", "ET")),
    "We do not currently possess any models that have Critical": ("blocked_rule", "no-critical-models", ("AT",)),
    "We will require the following practices": ("rule", "f4-security", ("JT",)),
    "plausible chance of reaching a capability threshold": ("condition", "ot7", ("JT",)),
    "If justified by our forecasts and threat models": ("blocked_rule", "f5-checkpoint", ("JT", "ET")),
    "In cases of ambiguity about whether a model is covered": ("blocked_rule", "f5-ambiguous", ("JT",)),
    "ordinarily not require additional safety measures": ("readings", "rs8-distilled", ("DF", "JT")),
    "every covered model undergoes": ("blocked_rule", "f7-evaluations", ("ET",)),
    "The SAG reviews the Capabilities Report": ("rule", "f7-report", ("AT",)),
    "Determine that the capability threshold has been crossed": ("readings", "rs16-recommend", ("readings",)),
    "appears likely to cross": ("rule", "f8-start", ("JT", "ET")),
    "planned safeguards needed to minimize": ("rule", "f9-report", ("JT",)),
    "We first identify the plausible ways": ("rule", "f9-risk-paths", ("JT",)),
    "For each of those, we then identify": ("blocked_rule", "f9-specific", ("SC",)),
    "An assessment on the residual risk of severe harm": ("readings", "rs9-residual", ("JT",)),
    "For each identified safeguard, we identify": ("blocked_rule", "f9-efficacy", ("SC",)),
    "and an efficacy threshold": ("blocked_rule", "f9-threshold", ("SC",)),
    "If we find reasonable evidence": ("rule", "f10-validate", ("JT",)),
    "review the 11": ("rule", "f10-review", ("JT",)),
    "could adjust accordingly": ("readings", "rs5-adjustment", ("JT", "WG")),
    "Research Category Potential response": ("readings", "rs4-lra", ("readings", "SC")),
    "Adopt elicitation approach that overcomes sandbagging": ("readings", "rs4-sandbagging", ("readings", "AP")),
    "Convert Autonomous Replication and Adap- tation": ("readings", "rs4-ara", ("readings",)),
    "require the Safeguards case to be robust": ("readings", "rs4-undermining", ("readings", "SC")),
    "Heighten safeguards (and consider further ac- tions)": ("readings", "rs4-nuclear", ("readings", "AP")),
    "We will periodically review the latest research": ("blocked_rule", "f13-review", ("ET",)),
    "SAG will receive the results of such reviews": ("blocked_rule", "f13-results", ("AP",)),
    "We will document relevant reports": ("rule", "f14-document", ()),
    "Employees may also request and receive a summary": ("readings", "rs13-employee-summary", ("AT", "AP")),
    "We will track and appropriately investigate": ("rule", "f14-investigate", ("JT",)),
    "and where reports are substantiated": ("rule", "f14-corrective", ("JT",)),
    "We will release information about our Preparedness": ("rule", "f15-disclose", ("JT",)),
    "Additionally, if the model is beyond a High threshold": ("rule", "f15-safeguards", ("JT",)),
    "Third-party evaluation of tracked model capabilities": ("rule", "f15-third-party", ("JT",)),
    "For each deployment under the Preparedness Framework, providing recommendations": ("rule", "f16-sag-recommend", ()),
    "The Safety and Security Committee (SSC)": ("rule", "f16-ssc-visibility", ()),
    "Safeguards should sufficiently minimize the risk associated with a misaligned model": ("readings", "rs9-c2-misalignment", ("JT", "DF")),
    "informed by SAG’s recommendations": ("readings", "rs6-informed", ("readings",)),
    "For the avoidance of doubt, OpenAI Leadership can also": ("readings", "rs7-without-sag", ("readings",)),
    "Where necessary, the Board may reverse a decision": ("readings", "rs17-board", ("AT", "AP")),
    "The SAG Chair should also coordinate": ("readings", "rs9-chair", ("JT", "DF")),
    "For all models, especially those presenting High capabilities": ("readings", "rs9-access", ("JT", "AP")),
    "at least once a year": ("readings", "rs0-year", ("ET",)),
    "Going forward we will handle risks related to persuasion": ("readings", "rs15-persuasion", ("AT",)),
    "For these areas, in collaboration with external experts, we commit": ("readings", "rs15-threat-models", ("AT",)),
    "As a reminder, covered systems that reach High capability must have": ("readings", "rs3-reminder", ("JT", "ET")),
    "Systems that reach Critical capability also require sufficient safeguards": ("rule", "f3-reminder", ("JT", "ET")),
}

READINGS = {
    "rs1-misuse-bio": ("RS1", {"strict": ["f1-misuse-bio-strict"], "default": ["f1-misuse-bio-default"]}),
    "rs1-misuse-cyb": ("RS1", {"strict": ["f1-misuse-cyb-strict"], "default": ["f1-misuse-cyb-default"]}),
    "rs1-alignment-cyb": ("RS1", {"strict": ["f1-alignment-cyb-strict"], "default": ["f1-alignment-cyb-default"]}),
    "rs1-security": ("RS1", {"strict": ["f1-security-strict"], "default": ["f1-security-default"]}),
    "rs1-halt": ("RS1", {"strict": ["f1-halt-strict"], "default": ["f1-halt-default"]}),
    "rs1-contrib-bio": ("RS1", {"strict": ["f1-contrib-bio-strict"], "default": ["f1-contrib-bio-default"]}),
    "rs1-contrib-cyb": ("RS1", {"strict": ["f1-contrib-cyb-strict"], "default": ["f1-contrib-cyb-default"]}),
    # F2 (2.2, 4.2, Appendix C) and section 1's deployment sentence: "deployed" is RS3. 2.2's second object
    # ("appropriate security controls as they are developed") holds under both choices.
    "rs3-deploy": ("RS3", {"ext": ["f2-deploy", "f2-security-developed"],
                           "any": ["f2-deploy-any", "f2-security-developed"]}),
    "rs3-reminder": ("RS3", {"ext": ["f2-reminder"], "any": ["f2-reminder-any"]}),
    "rs3-no-deploy": ("RS3", {"ext": ["f2-no-deploy"], "any": ["f2-no-deploy-any"]}),
    "rs18-develop": ("RS18", {"devonly": ["f3-develop", "f3-develop-forecast"],
                              "inuse": ["f3-develop-inuse", "f3-develop-inuse-forecast"]}),
    # RS2 is 4.2's "also" (p12-u195, which stays UNFORMALISED for its "during development" order); RS11 shares
    # p16-u281 with RS6. Neither has a unit of its own, so neither is placed.
    "rs2-nest": ("RS2", {"nest": ["rs2-nest"], "sep": []}),
    "rs11-final": ("RS11", {"final": ["f16-final"], "process": ["f16-process"]}),
    "rs6-informed": ("RS6", {"req": ["f16-informed"], "desc": []}),
    "rs7-without-sag": ("RS7", {"noinput": ["f16-without-noinput"], "nodelib": ["f16-without-nodelib"]}),
    "rs17-board": ("RS17", {"bperm": ["f16-board-reverse"], "bmight": []}),
    "rs16-recommend": ("RS16", {"coupled": ["f7-recommend"], "option": []}),
    "rs9-residual": ("RS9", {"strict": ["f9-residual-strict"], "default": ["f9-residual-default"]}),
    "rs9-chair": ("RS9", {"strict": ["f16-chair-strict"], "default": ["f16-chair-default"]}),
    "rs9-access": ("RS9", {"strict": ["c3-access-strict"], "default": ["c3-access-default"]}),
    "rs0-year": ("RS0", {"commitment": ["f16-year"], "prediction": []}),
    "rs8-distilled": ("RS8", {"rel": ["f6-rel"], "pred": []}),
    "rs5-adjustment": ("RS5", {"within": ["f11-within", "f11-acknowledge", "f11-protect", "f11-share"],
                               "exception": ["f11-exception", "f11-acknowledge", "f11-protect", "f11-share"]}),
    "rs4-lra": ("RS4", {"N": ["f12-lra", "f12-lra-unscoped"], "P": []}),
    "rs4-sandbagging": ("RS4", {"N": ["f12-sandbagging", "f12-sandbagging-unscoped"], "P": []}),
    "rs4-ara": ("RS4", {"N": ["f12-ara", "f12-ara-unscoped"], "P": []}),
    "rs4-undermining": ("RS4", {"N": ["f12-undermining", "f12-undermining-unscoped"], "P": []}),
    "rs4-nuclear": ("RS4", {"N": ["f12-nuclear", "f12-nuclear-unscoped"], "P": []}),
    "rs12-category": ("RS12", {"suff": ["f17-suff"], "iff": ["f17-iff", "f17-iff-only"]}),
    "rs15-persuasion": ("RS15", {"explanation": [], "rule": ["cl4-persuasion"]}),
    "rs15-threat-models": ("RS15", {"explanation": [], "rule": []}),
    # The permission reading keeps "subject to certain limits for highly sensitive information" as a carve-out.
    "rs13-employee-summary": ("RS13", {"permission": ["f14-summary"], "might": []}),
    "rs9-c2-misalignment": ("RS9", {"strict": ["c2-misalignment-strict"],
                                 "default": ["c2-misalignment-default"]}),
}
SET_FAMILIES = {"RS0": "readings", "RS1": "DF", "RS8": "DF", "RS5": "readings",
                "RS4": "readings", "RS12": "SC", "RS13": "AT", "RS15": "readings", "RS9": "DF",
                "RS3": "readings", "RS18": "readings", "RS2": "SC", "RS6": "readings", "RS7": "readings",
                "RS11": "readings", "RS16": "readings", "RS17": "AT"}
BLOCKED_RULE_REASONS = {"f5-checkpoint": "event_order", "f5-ambiguous": "unmapped_clause",
                        "f13-review": "event_order", "f13-results": "unmapped_clause",
                        "f7-evaluations": "event_order", "f9-specific": "quantifier_scope",
                        "f9-efficacy": "quantifier_scope", "f9-threshold": "quantifier_scope",
                        "f7-report": "attitude", "f14-document": "unmapped_clause",
                        "f16-sag-recommend": "unmapped_clause", "no-critical-models": "attitude"}
BLOCKER_FAMILY = {"event_order": "ET", "quantifier_scope": "SC", "attitude": "AT",
                  "unmapped_clause": "AP"}

# Each source fragment must map to a named element of the admitted rule or its
# vocabulary. The fragments must cover every word in the source unit. A new
# CHECKED rule requires an entry for every condition, quantifier and object.
CHECKED_CLAUSES = {
    "f16-ssc-visibility": (
        ("The Safety and Security Committee (SSC) of the OpenAI Board of Directors (Board)",
         "description", "Safety and Security Committee of the OpenAI Board of Directors"),
        ("will be given", "sign", True),
        ("visibility into processes", "act", "visibility into processes"),
    ),
}


def _complete_clause_map(block_id, source_text):
    clauses = CHECKED_CLAUSES.get(block_id)
    if not clauses:
        return False
    norm = json.loads(T.parsed_rule(block_id))
    predicate = T.vocabulary.environment()["vocabulary"]["predicates"][norm["predicate"]]
    elements = {"description": predicate["description"], "sign": norm["sign"],
                "act": predicate["regulated"]["act"], "guard": json.dumps(norm["guard"])}
    residual = source_text.decode()
    for fragment, element, expected in clauses:
        if residual.count(fragment) != 1:
            return False
        target = elements[element]
        matches = target == expected if isinstance(expected, bool) else expected in target
        if not matches:
            return False
        residual = residual.replace(fragment, "", 1)
    return not re.search(r"\w", residual)
OPEN_FOR = {
    "rs1-misuse-bio": ("ot1", "ot4"), "rs1-misuse-cyb": ("ot1", "ot4"),
    "rs1-alignment-cyb": ("ot1", "ot5"), "rs1-security": ("ot1", "ot3"),
    "rs1-halt": ("ot1", "ot6"),
    "rs3-deploy": ("ot1", "ot2"), "rs3-reminder": ("ot1", "ot2"), "rs3-no-deploy": ("ot1", "ot2"),
    "rs18-develop": ("ot1", "ot10"), "f3-reminder": ("ot1",), "rs1-contrib-bio": ("ot1",), "rs1-contrib-cyb": ("ot1",),
    "rs16-recommend": ("ot1",), "rs9-residual": ("ot2",), "rs9-chair": ("ot18", "ot21"), "rs9-access": ("ot3",),
    "f15-third-party": ("ot14",),
    "f4-security": ("ot1", "ot3"), "f8-start": ("ot9",), "f9-report": ("ot2",),
    "f10-validate": ("ot11",), "f10-review": ("ot11",),
    "f14-investigate": ("ot19",), "f15-disclose": ("ot13",),
    "f14-corrective": ("ot19",), "f15-safeguards": ("ot1", "ot13"), "f9-risk-paths": ("ot2",),
    "rs8-distilled": ("ot20",), "rs5-adjustment": ("ot12",), "rs12-category": ("ot16",),
    "rs9-c2-misalignment": ("ot2",),
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
                    "proposal": ["p"], "requirement": ["r"], "capability": ["c"]},
        "constants": {c: c for c in env.constants}, "relations": relations})


CLAIM_MARKER = re.compile(rb"\b(?:must|shall|will|should|may|might|could|required|require|requires|"
                          rb"commit|committed|ensure|undertake|we|our|can)\b", re.I)


def _fallback(page, start, text):
    # Positive exposition kinds are recognised on the whole unit. A heading
    # prefix cannot hide a claim later in the same source span.
    stripped = text.strip()
    if not CLAIM_MARKER.search(stripped) and (
        re.fullmatch(rb"(?:Contents|Appendix [A-Z0-9. :_-]+|Table [0-9]+(?:: [^.!?]+)?|[0-9.]+ [A-Z][^.!?]{0,70})", stripped)
        or re.fullmatch(rb"[0-9]+", stripped)
        or stripped.startswith((b"Preparedness Framework Version", b"Last updated:"))
        or (page in (18, 19, 20) and stripped.startswith(b"\xe2\x80\xa2"))
    ):
        return label("exposition"), None
    if b"ISO " in text or b"SOC2" in text or b"NIST " in text or b"FedRAMP" in text:
        return unformalised("external_reference"), "external reference"
    if re.search(rb"\b(?:could|may|might|believe|expect|aim|suggests)\b", text, re.I):
        return unformalised("hedged_claim"), "AT"
    if b"before " in text or b"during " in text or b"within " in text:
        return unformalised("event_order"), "ET"
    if re.search(rb"\b(?:each|every|all|any|only)\b", text, re.I):
        return unformalised("quantifier_scope"), "SC"
    if CLAIM_MARKER.search(text):
        return unformalised("unmapped_duty"), "AP"
    return unformalised("unmapped_claim"), "readings"


SOURCE_SUBJECT = {
    1: "front matter", 2: "framework introduction", 3: "contents", 4: "overview and rationale",
    5: "tracked-category criteria", 6: "Table 1 biological and cybersecurity thresholds",
    7: "Table 1 cybersecurity and self-improvement thresholds", 8: "research-category responses",
    9: "research-category assessment", 10: "capability evaluation and deployment scope",
    11: "safeguard selection", 12: "safeguard assessment and SAG decisions",
    13: "marginal risk and governance", 14: "disclosure and independent review",
    15: "change log", 16: "SAG and Board governance", 17: "safeguard examples",
    18: "C.1 safeguard examples", 19: "C.2 misalignment safeguards",
    20: "C.2 safeguard examples", 21: "C.3 security controls", 22: "C.3 security controls",
}
BLOCKER_DETAIL = {
    "unmapped_claim": ("readings", "D1 has no admitted descriptive predicate or selected reading for this claim"),
    "unmapped_duty": ("AP", "D1 has no complete regulated act and guard for this duty"),
    "unmapped_clause": ("AP", "the source-linked draft omits an object, condition, or reporting clause"),
    "quantifier_scope": ("SC", "D1's unary situation rule does not bind each source item"),
    "hedged_claim": ("AT", "D1 has no attitude or possibility operator preserving the source hedge"),
    "attitude": ("AT", "D1's draft does not preserve the source attitude"),
    "event_order": ("ET", "D1 has no event-order relation for the source temporal qualifier"),
    "quantity": ("QT", "D1 has no quantity bridge for the source magnitude or ratio"),
    "external_reference": ("external reference", "the outside standard is not represented in D1"),
}


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
        if kind == "rule" and not OPEN_FOR.get(ident) and (
            waits or not _complete_clause_map(ident, source[a:b])
        ):
            reason = BLOCKED_RULE_REASONS.get(ident, "unmapped_clause")
            kind, waits = "blocked_rule", (BLOCKER_FAMILY[reason],)
        if kind is None:
            spec, wait = _fallback(page, a, source[a:b])
        elif kind == "facts":
            spec, wait = facts(ident), None
        elif kind == "unformalised":
            spec, wait = unformalised(ident), None
        elif kind == "blocked_rule":
            spec, wait = unformalised(BLOCKED_RULE_REASONS.get(ident, "unmapped_clause")), None
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
        elif kind == "blocked_rule":
            rec["blocked_rule"] = ident
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
                family, explanation = BLOCKER_DETAIL[rec["reason"]]
                rec["detail"] = f"{family}: {explanation} in {SOURCE_SUBJECT[page]}"
                if kind is None:
                    # Keep every untranslated claim independently addressable
                    # without copying the private source text into the repo.
                    rec["residual"] = (f"{rec['reason']}-{uid}-"
                                       f"{hashlib.sha256(source[a:b]).hexdigest()[:12]}")
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
