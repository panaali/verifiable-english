"""Deterministically wrap the unchanged grant draft as a VE use case.

This script makes only local artifacts. It never edits source.md or calls a model.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from ve.environment import Environment
from ve.identity import meaning_id
from ve.ast import formula_from_data
from ve.profiles import LANGUAGE, SPEC_REVISION
from .author_choices import CHOICES
from .semantic_readings import (CAUSAL, CAUSAL_SORTS, CONSTANTS, OPEN_DECIDERS, OPEN_REASONS,
                                PREDICATES, READINGS, RESOLUTIONS, SORTS, conj)

HERE = Path(__file__).resolve().parent
SOURCE = (HERE / "source.md").read_bytes()


def _clause_ast(clause: dict) -> list:
    if "constant" in clause:
        return ["binary", clause["predicate"], ["var", 0], ["const", clause["constant"]]]
    return ["unary", clause["predicate"], ["var", 0]]


def definitions() -> dict:
    """The five author choices, recorded as definitions in the environment.

    Each description carries the signed rule and its reason, so the document
    itself records the choice.  The body is the conjunction of the rule's
    clauses, the same clauses that ``author_choices.clauses`` evaluates.
    """
    predicates = {}
    for term, choice in CHOICES.items():
        for clause in choice["clauses"]:
            if "constant" in clause:
                continue  # counts_cost is shared vocabulary; its constants name the components.
            predicates[clause["predicate"]] = {
                "arguments": [clause["sort"]],
                "description": f"author-choice clause of {term}: {clause['words']}",
                "verbalisation": "{0} " + clause["words"]}
        predicates[term] = {
            "arguments": [choice["sort"]],
            "description": (f"Author choice signed by {choice['signature']}. Rule: {choice['rule']}. "
                            f"Why: {choice['why']}"),
            "verbalisation": choice["verbalisation"],
            "defined": {"arguments": [choice["sort"]],
                        "body": conj(*[_clause_ast(c) for c in choice["clauses"]])}}
    return predicates


CAUSAL_ROLES = ("available", "leads_to")
ENV = {"language": LANGUAGE,
       "profiles": ["definitions@0", "relational-fol@0"],
       "spec_revision": SPEC_REVISION,
       "vocabulary": {
           "sorts": {k: v for k, v in SORTS.items() if k not in ("chooser", "action")},
           "predicates": {**{k: v for k, v in PREDICATES.items() if k not in CAUSAL_ROLES},
                          **definitions()},
           "constants": {k: v for k, v in CONSTANTS.items() if v["sort"] != "action"}}}

# The merged causation route.  Its Lean route refuses definitions, so the
# causal units are checked in their own document on the same source bytes.
# Outcomes are signed by their units; no table completion, default or risk
# policy is supplied.
CAUSAL_ENV = {"language": LANGUAGE,
              "profiles": ["alternatives@0", "norms@0", "relational-fol@0"],
              "spec_revision": SPEC_REVISION,
              "vocabulary": {
                  "sorts": {k: SORTS[k] for k in CAUSAL_SORTS},
                  "predicates": {k: PREDICATES[k] for k in CAUSAL_ROLES},
                  "constants": {k: v for k, v in CONSTANTS.items() if v["sort"] in CAUSAL_SORTS}},
              "alternatives": {"chooser": "chooser", "action": "action", "harm": "harm",
                               "available": "available", "leads_to": "leads_to",
                               "outcomes": "signed"}}

OPEN_TERMS = [{"name": term, "arguments": [CHOICES[term]["sort"]],
               "decided_by": OPEN_DECIDERS[term], "necessary": [], "sufficient": [],
               "factors": [OPEN_REASONS[term]], "precedents": [],
               "jurisdiction": "this-draft", "version": 1}
              for term in OPEN_REASONS]


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


def unit_spans() -> list[tuple[int, int]]:
    spans = []
    pos = 0
    for line_no, raw in enumerate(SOURCE.decode().splitlines(keepends=True), 1):
        if not raw.strip():
            # A blank separator stays with the preceding sentence.
            spans[-1] = (spans[-1][0], spans[-1][1] + len(raw.encode()))
            pos += len(raw.encode())
            continue
        parts = chunks(raw, line_no)
        assert "".join(parts) == raw, (line_no, parts)
        for part in parts:
            end = pos + len(part.encode())
            spans.append((pos, end))
            pos = end
    assert pos == len(SOURCE)
    return spans


def _reading_set(uid: str, ast: list, mid: str, why: str) -> dict:
    return {"id": f"reading-{uid}", "unit": uid, "version": 1,
            "status": "authored", "signature": "grant-author",
            "readings": [{"id": "chosen", "kind": "asserted", "meaning_id": mid, "content": ast,
                          "admission": {"who": "grant-author", "why": why,
                                        "distinguishing_models": {}}}]}


def build_causal() -> tuple[dict, bytes]:
    """The causal units, byte for byte, on the alternatives route.

    The source is the concatenation of the main document's spans for these
    units, in order; unit ids are the main document's ids.  Asserted units
    enter a graph so Lean admission types them with the profile words.
    """
    env = Environment(CAUSAL_ENV)
    spans = unit_spans()
    source = b""
    units, reading_sets, nodes = [], [], []
    for uid, spec in CAUSAL.items():
        start, end = spans[int(uid[1:]) - 1]
        piece = SOURCE[start:end]
        ast = spec["content"]
        mid = meaning_id(env, formula_from_data(env, ast))
        asserted = spec["kind"] == "asserted"
        units.append({"id": uid, "span": [len(source), len(source) + len(piece)], "status": "CHECKED",
                      "kind": spec["kind"], "meaning": "specified",
                      "support": "assumption" if asserted else "none",
                      "content": {"ast": ast}, "meaning_id": mid})
        if asserted:
            reading_sets.append(_reading_set(uid, ast, mid, spec["why"]))
            nodes.append({"name": uid, "ast": ast, "label": f"readings:reading-{uid}@1:0"})
        source += piece
    assert len(nodes) == 1
    return ({"format": "ve-document@1", "environment": CAUSAL_ENV, "units": units,
             "reading_sets": reading_sets, "graph": {"root": nodes[0]["name"], "nodes": nodes}},
            source)


def build() -> dict:
    env = Environment(ENV)
    spans = unit_spans()
    assert len(spans) == len(READINGS)
    units = []
    reading_sets = []
    for index, span in enumerate(spans, 1):
        uid = f"u{index:03d}"
        spec = READINGS[uid]
        status = spec["status"]
        meaning = ({"open": spec["open"]} if status == "OPEN" else
                   {"unformalised": spec["reason"]} if status == "UNFORMALISED" else "specified")
        support = "assumption" if status == "CHECKED" and spec["kind"] == "asserted" else "none"
        unit = {"id": uid, "span": list(span), "status": status,
                "kind": spec["kind"], "meaning": meaning, "support": support}
        if status == "CHECKED":
            ast = spec["content"]
            unit["content"] = {"ast": ast}
            unit["meaning_id"] = meaning_id(env, formula_from_data(env, ast))
            if spec["kind"] == "asserted":
                # An authored reading set may hold only assertions; quoted,
                # hedged and planned units keep their force in the kind.
                why = spec["why"] + (f" Resolution: {RESOLUTIONS[uid]}." if uid in RESOLUTIONS else "")
                reading_sets.append(_reading_set(uid, ast, unit["meaning_id"], why))
        units.append(unit)
    return {"format": "ve-document@1", "environment": ENV, "units": units,
            "open_terms": OPEN_TERMS, "reading_sets": reading_sets}


def main() -> None:
    front = json.dumps(build(), ensure_ascii=False, indent=2)
    path = HERE / "document.ve.md"
    path.write_bytes(b"---\n" + front.encode() + b"\n---\n" + SOURCE)
    causal, causal_source = build_causal()
    (HERE / "causal.ve.md").write_bytes(
        b"---\n" + json.dumps(causal, ensure_ascii=False, indent=2).encode() + b"\n---\n" + causal_source)
    from ve.document import load_document
    from ve.natural import render_natural_sentence
    from ve.english import parse_english, render_english
    from ve.errors import VEError
    from ve.ast import Document

    doc = load_document(path)
    lines = ["# Audited natural view of the draft", "",
             "Each quoted passage is an exact byte span from `source.md`. Checked readings are",
             "rendered by `ve_natural` and parsed back to one identical formula. The display",
             "uses an explicit-form fallback where the current natural grammar cannot express",
             "the chosen reading without quoted identifiers. The kind line keeps the speaker:",
             "quoted, candidate, hedged and planned readings are not assertions of the draft.", ""]
    for unit in doc["units"]:
        status = unit["status"]
        source = unit["source"].strip().replace("\n", " ")
        lines += [f"### {unit['id']} · {status}", "", f"> {source}", ""]
        if status == "CHECKED":
            formula = formula_from_data(doc["environment"], unit["content"])
            try:
                natural = render_natural_sentence(formula, doc["environment"],
                                                  accept_suggested_vocabulary=True)
                text, qualifier = natural.text, ("natural" if natural.natural else "explicit-form fallback")
            except (KeyError, VEError):
                # The natural grammar has no entry for the merged `prevents`
                # word; the controlled-English renderer does.
                text, qualifier = render_english(formula, doc["environment"],
                                                 accept_suggested_vocabulary=True), "explicit-form fallback"
            assert parse_english(doc["environment"], text.rstrip(".") + ".",
                                 accept_suggested_vocabulary=True) == Document((formula,))
            lines += [f"**Kind:** {json.dumps(unit['kind'])}.", "",
                      f"**{qualifier}:** {text.rstrip('.')}.", ""]
            if unit["id"] in RESOLUTIONS:
                lines += [f"**Author resolution:** {RESOLUTIONS[unit['id']]}.", ""]
        elif status == "OPEN":
            lines += [f"**Open term:** {', '.join(unit['meaning']['open'])}.", ""]
        elif status == "UNFORMALISED":
            lines += [f"**Missing feature:** {unit['meaning']['unformalised']}.", ""]
            if unit["id"] in CAUSAL:
                lines += ["**Causal route:** checked in `causal.ve.md` on alternatives@0; "
                          "not counted as CHECKED here.", ""]
        else:
            lines += [f"**Kind:** {json.dumps(unit['kind'])}.", ""]
    (HERE / "natural-view.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
