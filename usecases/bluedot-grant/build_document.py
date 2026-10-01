"""Deterministically wrap the unchanged grant draft as a VE use case.

This script makes only local artifacts. It never edits source.md or calls a model.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from ve.environment import Environment
from ve.identity import meaning_id
from ve.ast import Top, formula_from_data
from ve.entailment import prove_entailment
from ve.profiles import LANGUAGE, SPEC_REVISION
from .author_choices import CHOICES
from .semantic_readings import READINGS

HERE = Path(__file__).resolve().parent
SOURCE = (HERE / "source.md").read_bytes()


def predicate(words: str, sort: str = "artifact") -> dict:
    return {"arguments": [sort], "description": words,
            "verbalisation": "{0} " + words}


ENV = {"language": LANGUAGE, "profiles": ["definitions@0", "relational-fol@0"],
       "spec_revision": SPEC_REVISION,
       "vocabulary": {
           "sorts": {
               "artifact": {"description": "an artifact", "verbalisation": {"singular": "artifact", "plural": "artifacts"}},
               "foundation_leaf": {"description": "a declared foundation leaf", "verbalisation": {"singular": "foundation leaf", "plural": "foundation leaves"}},
               "field": {"description": "a form field", "verbalisation": {"singular": "field", "plural": "fields"}},
           },
           "predicates": {
               "accepted_without_proof": predicate("is accepted without proof", "foundation_leaf"),
               "claims_vex_result": predicate("claims a VEX result"),
               "claims_completed_extension": predicate("claims a completed extension"),
               "reports_new_result": predicate("reports a new experimental result"),
               "asserts_cost_advantage": predicate("asserts a cost advantage"),
               "revised": predicate("is revised", "field"),
               "includes_formalisation": predicate("includes formalisation"),
               "includes_proof_production": predicate("includes proof production"),
               "includes_spaces": predicate("includes spaces"),
               "includes_punctuation": predicate("includes punctuation"),
               "includes_labels": predicate("includes labels"),
               "includes_trailing_newlines": predicate("includes trailing newlines"),
               "establishes_foundation_truth": predicate("establishes foundation truth"),
               "establishes_faithful_formalisation": predicate("establishes faithful formalisation"),
               "guarantees_evidence_quality": predicate("guarantees evidence quality"),
               "schedules_development": predicate("schedules evidence layer development"),
               "conditional_on_foundations": predicate("is conditional on declared foundations"),
               "concerns_estimated_leaves": predicate("concerns estimated leaves"),
               "concerns_proved_subclaims": predicate("concerns proved subclaims"),
               "establishes_truth": {"arguments": ["artifact", "artifact"],
                                     "description": "establishes the truth of",
                                     "verbalisation": "{0} establishes the truth of {1}"},
           },
           "constants": {
               "draft": {"sort": "artifact", "description": "this grant draft"},
               "comparison": {"sort": "artifact", "description": "the matched-cost comparison"},
               "counts": {"sort": "artifact", "description": "the stated character counts"},
               "proof_rule": {"sort": "artifact", "description": "the mandatory proof rule"},
               "requirements": {"sort": "artifact", "description": "the proposed evidence requirements"},
               "milestones": {"sort": "artifact", "description": "the existing evidence layer milestones"},
               "guarantee": {"sort": "artifact", "description": "the proof guarantee"},
               "caveat": {"sort": "artifact", "description": "the existing stability caveat"},
               "foundations": {"sort": "artifact", "description": "the declared foundations"},
           }}}

# These are source propositions, never observations supplied by the checker.
# Definitions bind the five author decisions to explicit conjunctions of
# auditable inputs.  author_choices.py specifies how numerical flags are made.
for _, subject, propositions in READINGS.values():
    ENV["vocabulary"]["constants"].setdefault(
        subject, {"sort": "artifact", "description": subject.replace("_", " ")})
    for name in propositions:
        ENV["vocabulary"]["predicates"].setdefault(
            name, predicate(name.replace("_", " ")))

def conjunction(items):
    result = items[0]
    for item in items[1:]:
        result = ["and", result, item]
    return result


for term, choice in CHOICES.items():
    for flag in choice["flags"]:
        ENV["vocabulary"]["predicates"].setdefault(flag, predicate(flag.replace("_", " ")))
    ENV["vocabulary"]["predicates"][term] = {
        "arguments": ["artifact"], "description": choice["rule"],
        "defined": {"arguments": ["artifact"],
                    "body": conjunction([["unary", flag, ["var", 0]] for flag in choice["flags"]])},
    }


def atom(name: str, subject: str = "draft") -> list:
    return ["unary", name, ["const", subject]]


FOUNDATIONS = ["forall", "foundation_leaf", ["unary", "accepted_without_proof", ["var", 0]]]
CHECKED = {
    "foundation leaves remain accepted without proof": FOUNDATIONS,
    "no VEX result or completed extension is claimed":
        ["and", ["not", atom("claims_vex_result")], ["not", atom("claims_completed_extension")]],
    "The revised form text does not report new experimental results or assert a cost advantage":
        ["and", ["not", atom("reports_new_result")], ["not", atom("asserts_cost_advantage")]],
    "Formalisation and proof production are included in the matched-cost comparison":
        ["and", atom("includes_formalisation", "comparison"), atom("includes_proof_production", "comparison")],
    "No budget or other field is revised":
        ["not", ["exists", "field", ["unary", "revised", ["var", 0]]]],
    "Character counts include spaces and punctuation but exclude labels and trailing newlines":
        ["and", ["and", atom("includes_spaces", "counts"), atom("includes_punctuation", "counts")],
         ["and", ["not", atom("includes_labels", "counts")],
          ["not", atom("includes_trailing_newlines", "counts")]]],
    "It does not establish their truth or faithful formalisation":
        ["and", ["not", atom("establishes_foundation_truth", "proof_rule")],
         ["not", atom("establishes_faithful_formalisation", "proof_rule")]],
    "Evidence requirements do not guarantee evidence quality":
        ["not", atom("guarantees_evidence_quality", "requirements")],
    "The existing evidence-layer milestones remain its development schedule":
        atom("schedules_development", "milestones"),
    "the guarantee is conditional on the declared foundations":
        atom("conditional_on_foundations", "guarantee"),
    "The existing stability caveat concerns estimated leaves, not proved sub-claims":
        ["and", atom("concerns_estimated_leaves", "caveat"),
         ["not", atom("concerns_proved_subclaims", "caveat")]],
}

OPEN = {
    "matched_cost": "What computational, authoring, and review costs enter the comparison, and how are they measured?",
    "real_artefact": "What qualifies as a real artifact rather than a planted flaw?",
    "affordable_proof": "Which proof budgets and hardware make a proof affordable?",
    "misleading_formalisation": "Who judges fidelity between the source task and its formalisation?",
    "catastrophic_risk": "Which outcomes count as catastrophic risk, and how is reduction assessed?",
}


def chunks(line: str, line_no: int) -> list[str]:
    """Cut prose at sentences and semicolon clauses, never inside .md names."""
    if line_no in {35, 62}:
        line = line.replace(": foundation leaves", ": \x00foundation leaves")
        line = line.replace(", and formalisation", ", \x00and formalisation")
    if line_no == 42:
        line = line.replace(", and no VEX", ", \x00and no VEX")
    pieces = []
    start = 0
    for match in re.finditer(r"(?<=;)[ ]|(?<=[.!?])[ ](?=[A-Z])|\x00", line):
        boundary = match.end()
        prefix = line[start:match.start()].strip()
        if re.fullmatch(r"[1-7]\.", prefix):
            continue
        pieces.append(line[start:boundary].replace("\x00", ""))
        start = boundary
    pieces.append(line[start:].replace("\x00", ""))
    return [piece for piece in pieces if piece]


def classify(text: str, line_no: int) -> tuple[str, object, object, str, object | None]:
    stripped = text.strip().rstrip(".,;:")
    for cue, ast in CHECKED.items():
        if cue in stripped and (len(stripped) - len(cue) < 8 or stripped.startswith("A proof label could increase false confidence")):
            return "CHECKED", "meta" if line_no >= 37 else "exposition", "specified", "assumption", ast
    if "affordable proof" in text or "proofs beyond budget" in text:
        return "OPEN", ["hedged", "could", "asserted"], {"open": ["affordable_proof"]}, "none", None
    if "real artefact" in text or "real-artefact" in text:
        return "OPEN", "exposition", {"open": ["real_artefact"]}, "none", None
    if "matched cost" in text or "matched-cost" in text:
        return "OPEN", "exposition", {"open": ["matched_cost"]}, "none", None
    if "misleading formalisation" in text:
        return "OPEN", "exposition", {"open": ["misleading_formalisation"]}, "none", None
    if "catastrophic risk" in text:
        return "OPEN", "question", {"open": ["catastrophic_risk"]}, "none", None
    if "should help other oversight" in text:
        return "UNFORMALISED", ["attributed", "applicant", "expects", ["unformalised", "causal_evidence"]], {"unformalised": "causal_evidence"}, "none", None
    if any(cue in text for cue in ("blocks the Barnes-Christiano", "prevents arbitrary false sub-claims", "test these harms", "tests transfer", "should help other oversight", "motivat")):
        return "UNFORMALISED", ["unformalised", "causal_evidence"], {"unformalised": "causal_evidence"}, "none", None
    if "current length" in text:
        return "UNFORMALISED", ["attributed", "author", "believes", ["unformalised", "vague_comparison"]], {"unformalised": "vague_comparison"}, "none", None
    if any(cue in text for cue in ("50 to 5,000", "50-to-5,000")) and line_no not in {7, 10, 49, 52}:
        return "UNFORMALISED", ["unformalised", "numeric_range"], {"unformalised": "numeric_range"}, "none", None
    if line_no in {4, 8, 11, 16, 19, 24, 27, 32, 35, 50, 53, 56, 59, 62}:
        if any(cue in text for cue in ("will be", "release benchmarks", "Include real", "replicate", "Compare with", "Focus on", "test authentic", "Testing mandatory", "testing mandatory", "developing mandatory")):
            return "LABELLED", ["attributed", "applicant", "intends", "asserted"], "specified", "none", None
        if any(cue in text for cue in ("could increase", "would require", "may misstate", "should help")):
            return "LABELLED", ["hedged", "could", "asserted"], "specified", "none", None
        return "LABELLED", "exposition", "specified", "none", None
    if line_no in {2, 5, 9, 12, 14, 17, 20, 22, 25, 28, 30, 33, 36, 38, 46, 48, 51, 54, 57, 60}:
        return "LABELLED", "meta", "specified", "none", None
    if line_no == 45 and "Paste only" in text:
        return "LABELLED", "instruction", "specified", "none", None
    if "remains appropriate" in text or "This is a benefit" in text:
        return "LABELLED", ["attributed", "author", "believes", "asserted"], "specified", "none", None
    if "the extra space states the proof rule" in text:
        return "LABELLED", "explanation", "specified", "none", None
    return "LABELLED", "meta", "specified", "none", None


def build() -> dict:
    env = Environment(ENV)
    units = []
    reading_sets = []
    pos = 0
    for line_no, raw in enumerate(SOURCE.decode().splitlines(keepends=True), 1):
        if not raw.strip():
            # A blank separator stays with the preceding sentence.
            units[-1]["span"][1] += len(raw.encode())
            pos += len(raw.encode())
            continue
        parts = chunks(raw, line_no)
        assert "".join(parts) == raw, (line_no, parts)
        for part in parts:
            end = pos + len(part.encode())
            status, kind, meaning, support, ast = classify(part, line_no)
            uid = f"u{len(units)+1:03d}"
            if uid in READINGS:
                kind, subject, propositions = READINGS[uid]
                ast = conjunction([atom(name, subject) for name in propositions])
                status, meaning = "CHECKED", "specified"
                support = "assumption" if kind == "asserted" else "none"
            elif uid == "u049":
                ast = ["and", ["not", ["binary", "establishes_truth",
                                         ["const", "proof_rule"], ["const", "foundations"]]],
                       ["not", atom("establishes_faithful_formalisation", "proof_rule")]]
            elif uid in {"u022", "u027", "u083", "u085"}:
                status, kind, meaning, support, ast = "LABELLED", "meta", "specified", "none", None
            elif uid == "u033":
                # "Should help" is a prediction/hope here, not a demand on an
                # addressee.  A soft obligation would change the author's claim.
                status, kind, meaning, support, ast = "LABELLED", ["attributed", "applicant", "expects", "asserted"], "specified", "none", None
            unit = {"id": uid, "span": [pos, end], "status": status,
                    "kind": kind, "meaning": meaning, "support": support}
            if ast is not None:
                unit["content"] = {"ast": ast}
                mid = meaning_id(env, formula_from_data(env, ast))
                if kind == "asserted" or uid not in READINGS:
                    reading_sets.append({"id": f"reading-{uid}", "unit": uid, "version": 1,
                                         "status": "authored", "signature": "grant-author",
                                         "readings": [{"id": "chosen", "kind": "asserted", "meaning_id": mid,
                                                       "content": ast,
                                                       "admission": {"who": "grant-author",
                                                                     "why": "Chosen reading of this source clause; scope is this draft, not an empirical verification.",
                                                                     "distinguishing_models": {}}}]})
            units.append(unit)
            pos = end
    assert pos == len(SOURCE)
    return {"format": "ve-document@1", "environment": ENV, "units": units,
            "open_terms": [], "reading_sets": reading_sets}


def main() -> None:
    front = json.dumps(build(), ensure_ascii=False, indent=2)
    path = HERE / "document.ve.md"
    path.write_bytes(b"---\n" + front.encode() + b"\n---\n" + SOURCE)
    from ve.document import load_document
    from ve.natural import render_natural_sentence
    from ve.english import parse_english
    from ve.ast import Document

    doc = load_document(path)
    lines = ["# Audited natural view of the draft", "",
             "Each quoted passage is an exact byte span from `source.md`. Checked readings are",
             "rendered by `ve_natural` and parsed back to one identical formula. The display",
             "uses an explicit-form fallback where the current natural grammar cannot express",
             "the chosen reading without quoted identifiers.", ""]
    for unit in doc["units"]:
        status = unit["status"]
        source = unit["source"].strip().replace("\n", " ")
        lines += [f"### {unit['id']} · {status}", "", f"> {source}", ""]
        if status == "CHECKED":
            formula = formula_from_data(doc["environment"], unit["content"])
            natural = render_natural_sentence(formula, doc["environment"],
                                              accept_suggested_vocabulary=True)
            assert parse_english(doc["environment"], natural.text + ".",
                                 accept_suggested_vocabulary=True) == Document((formula,))
            qualifier = "natural" if natural.natural else "explicit-form fallback"
            lines += [f"**{qualifier}:** {natural.text}.", ""]
        elif status == "OPEN":
            lines += [f"**Open term:** {', '.join(unit['meaning']['open'])}.", ""]
        elif status == "UNFORMALISED":
            lines += [f"**Missing feature:** {unit['meaning']['unformalised']}.", ""]
        else:
            lines += [f"**Kind:** {unit['kind']}.", ""]
    (HERE / "natural-view.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
