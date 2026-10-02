"""The authored BlueDot reading keeps source bytes, speakers and modalities.

Each review finding is pinned as a class: the definitions are used or the
unit stays OPEN; a CHECKED formula uses real structure; no content is added
that the span does not state; anaphora is recorded; and the record classifier
is exactly the conjunction of the definition's clauses.
"""
from __future__ import annotations

import copy
import importlib
import json
import re
from collections import Counter
from hashlib import sha256
from pathlib import Path

import pytest

from ve.alternatives import run_case
from ve.document import check_document, front_matter, load_document

ROOT = Path(__file__).resolve().parents[1] / "usecases/bluedot-grant"
SOURCE_HASH = "a9fa225acce6a684af7519c9c6fa82a20fc3a7e685a04b7e1a4bac88a0d6ed22"
choices = importlib.import_module("usecases.bluedot-grant.author_choices")
readings = importlib.import_module("usecases.bluedot-grant.semantic_readings")
builder = importlib.import_module("usecases.bluedot-grant.build_document")

TERMS = {"matched_cost": r"matched[ -]cost", "real_artefact": r"real[ -]artefact",
         "affordable_proof": r"affordable proof",
         "misleading_formalisation": r"misleading[ -]formalisation",
         "catastrophic_risk": r"catastrophic risk"}
CAUSAL_WORDS = r"\b(prevents|blocks|motivates|could increase|because)\b"
ANAPHORA = r"\b(It|its|their|This|these|the claim|the guarantee|is claimed)\b"
CONDITION_WORDS = {"when", "if", "unless", "beyond", "until", "before", "after"}
FIXED_CAUSAL_WORDS = {"leads_to", "available", "prevents"}


@pytest.fixture(scope="module")
def doc():
    return load_document(ROOT / "document.ve.md")


@pytest.fixture(scope="module")
def vocabulary(doc):
    return doc["environment"].to_dict()["vocabulary"]


def symbols(ast, out=None):
    out = set() if out is None else out
    if type(ast) is list and ast:
        if ast[0] in ("unary", "binary"):
            out.add(("predicate", ast[1]))
        elif ast[0] == "const":
            out.add(("constant", ast[1]))
        for item in ast[1:]:
            symbols(item, out)
    return out


def predicates(ast):
    return {name for kind, name in symbols(ast) if kind == "predicate"}


def kind_tags(kind):
    if type(kind) is str:
        return {kind}
    return {kind[0]} | set().union(*(kind_tags(k) for k in kind[1:] if type(k) is list))


def test_source_partition_and_generated_artifacts(doc):
    source = (ROOT / "source.md").read_bytes()
    assert sha256(source).hexdigest() == SOURCE_HASH
    assert len(source) == 7619
    assert doc["source"] == source
    assert [u["id"] for u in doc["units"]] == [f"u{i:03d}" for i in range(1, 94)]
    cursor = 0
    for unit in doc["units"]:
        assert unit["span"][0] == cursor
        cursor = unit["span"][1]
        assert unit["source"].encode() == source[slice(*unit["span"])]
    assert cursor == len(source)
    assert set(readings.READINGS) == {u["id"] for u in doc["units"]}
    meta, _ = front_matter((ROOT / "document.ve.md").read_bytes())
    assert meta == json.loads(json.dumps(builder.build()))
    causal_meta, _ = front_matter((ROOT / "causal.ve.md").read_bytes())
    assert causal_meta == json.loads(json.dumps(builder.build_causal()[0]))
    # The previous sidecar invented commands, defaults and a year; it is gone.
    assert not (ROOT / "feature-readings.json").exists()
    assert not (ROOT / "feature_readings.py").exists()


def test_definitions_record_author_choices_in_the_document(vocabulary):
    for term, choice in choices.CHOICES.items():
        declaration = vocabulary["predicates"][term]
        assert choice["signature"] in declaration["description"]
        assert choice["rule"] in declaration["description"]
        assert choice["why"] in declaration["description"]
        assert declaration["defined"]["body"] == readings.conj(
            *[builder._clause_ast(c) for c in choice["clauses"]])
        for clause in choice["clauses"]:
            assert clause["predicate"] in vocabulary["predicates"]
            if "constant" in clause:
                assert clause["constant"] in vocabulary["constants"]


VALID = {
    "matched_cost": {
        "same_task": True, "budget_record_id": "pre-1", "budget_registered_on": "2026-09-01",
        "comparison_started_on": "2026-09-02",
        "arms": {"proof": {"authoring": 0, "formalisation": 0, "proof": 100, "compute": 0, "review": 0},
                 "cross_examination": {"authoring": 0, "formalisation": 0, "proof": 0, "compute": 0,
                                       "review": 95}}},
    "real_artefact": {"provenance_sha256": "a" * 64, "created_on": "2026-08-01",
                      "selected_on": "2026-09-01", "independent_task": True,
                      "evaluator_seeded_flaw": False},
    "affordable_proof": {"proof_cost_recorded": True, "formalisation_cost_recorded": True,
                         "certificate_complete": True, "certificate_checked": True,
                         "budget_registered_on": "2026-09-01", "deadline_registered_on": "2026-09-01",
                         "claim_made_on": "2026-09-02", "total_cost": "100", "registered_budget": "100",
                         "elapsed_hours": "2", "registered_deadline_hours": "2"},
    "misleading_formalisation": {"source_sha256": "a" * 64, "formula_sha256": "b" * 64,
                                 "counterexample_id": "case-1", "answer_changes": True,
                                 "reviewers": [{"id": "r1", "reproduced": True, "blind_to_arm": True},
                                               {"id": "r2", "reproduced": True, "blind_to_arm": True}]},
    "catastrophic_risk": {"pathway_record_id": "path-1", "evidence_record_id": "evidence-1",
                          "severity_assessment_id": "severity-1", "projected_deaths": 1_000_000},
}


def _set(path, value):
    def edit(record):
        target = record
        for key in path[:-1]:
            target = target[key]
        if value is KeyError:
            del target[path[-1]]
        else:
            target[path[-1]] = value
    return edit


# One failing record per clause.  Each was a gap or a near miss: the review
# found proof-cost recording, budget-before-claim, reviewer blindness and the
# severity assessment missing from the old classifier.
MUTATIONS = {
    "matched_cost": {
        "same_task": _set(["same_task"], False),
        "budget_preregistered": _set(["budget_registered_on"], "2026-09-02"),
        "counts_authoring": _set(["arms", "proof", "authoring"], KeyError),
        "counts_formalisation_work": _set(["arms", "cross_examination", "formalisation"], KeyError),
        "counts_proof_production": _set(["arms", "proof", "proof"], KeyError),
        "counts_compute": _set(["arms", "proof", "compute"], KeyError),
        "counts_review": _set(["arms", "cross_examination", "review"], KeyError),
        "totals_within_tolerance": _set(["arms", "cross_examination", "review"], 94),
    },
    "real_artefact": {
        "provenance_recorded": _set(["provenance_sha256"], "A" * 64),
        "independent_task": _set(["independent_task"], False),
        "predates_selection": _set(["created_on"], "2026-09-01"),
        "no_seeded_flaw": _set(["evaluator_seeded_flaw"], True),
    },
    "affordable_proof": {
        "proof_cost_recorded": _set(["proof_cost_recorded"], False),
        "formalisation_cost_recorded": _set(["formalisation_cost_recorded"], KeyError),
        "certificate_complete": _set(["certificate_complete"], False),
        "certificate_checked": _set(["certificate_checked"], False),
        "claim_budget_preregistered": _set(["budget_registered_on"], "2026-09-03"),
        "claim_deadline_preregistered": _set(["deadline_registered_on"], "2026-09-02"),
        "within_budget": _set(["total_cost"], "100.01"),
        "within_deadline": _set(["elapsed_hours"], "2.5"),
    },
    "misleading_formalisation": {
        "source_pinned": _set(["source_sha256"], "short"),
        "formula_pinned": _set(["formula_sha256"], KeyError),
        "answer_changing_counterexample": _set(["answer_changes"], False),
        "two_reproductions": _set(["reviewers", 1, "id"], "r1"),
        "reviewers_blind": _set(["reviewers", 0, "blind_to_arm"], False),
    },
    "catastrophic_risk": {
        "pathway_documented": _set(["pathway_record_id"], ""),
        "evidence_recorded": _set(["evidence_record_id"], KeyError),
        "severity_assessed": _set(["severity_assessment_id"], KeyError),
        "meets_severity_threshold": _set(["projected_deaths"], 999_999),
    },
}


@pytest.mark.parametrize("term", sorted(choices.CHOICES))
def test_classifier_is_exactly_the_definition_clauses(term):
    clause_ids = [c["id"] for c in choices.CHOICES[term]["clauses"]]
    assert list(choices.clauses(term, VALID[term])) == clause_ids
    assert all(choices.clauses(term, VALID[term]).values())
    assert choices.decide(term, VALID[term])
    assert set(MUTATIONS[term]) == set(clause_ids)
    for clause, edit in MUTATIONS[term].items():
        record = copy.deepcopy(VALID[term])
        edit(record)
        assert choices.clauses(term, record)[clause] is False, (term, clause)
        assert not choices.decide(term, record), (term, clause)
    assert not choices.decide(term, {})
    with pytest.raises(ValueError):
        choices.decide(term, [])


def test_defined_terms_are_used_or_the_unit_stays_open(doc):
    used = Counter()
    open_used = set()
    for unit in doc["units"]:
        mentioned = {t for t, pattern in TERMS.items() if re.search(pattern, unit["source"], re.I)}
        content_terms = (predicates(unit["content"]) & set(TERMS)
                         if unit["status"] == "CHECKED" else set())
        open_terms = set(unit["meaning"]["open"]) if unit["status"] == "OPEN" else set()
        for term in mentioned:
            assert term in content_terms or term in open_terms, (unit["id"], term)
        # Neither direction imposes a term the span does not use.
        assert content_terms <= mentioned and open_terms <= mentioned, unit["id"]
        used.update(content_terms)
        open_used |= open_terms
    assert {o["name"] for o in doc["meta"]["open_terms"]} == open_used
    # The definitions are not orphaned: three are used by checked readings.
    assert {t for t in used if used[t]} == {"matched_cost", "real_artefact", "affordable_proof"}


def test_checked_formulas_use_real_structure(doc, vocabulary):
    # No auto-declared one-off atoms: the vocabulary is the authored one.
    authored = {k for k in readings.PREDICATES if k not in builder.CAUSAL_ROLES}
    authored |= set(builder.definitions())
    assert set(vocabulary["predicates"]) == authored
    for name in vocabulary["predicates"]:
        assert not re.search(r"\d", name), name
        assert not set(name.split("_")) & CONDITION_WORDS, name
    for name in vocabulary["constants"]:
        assert not set(name.split("_")) & CONDITION_WORDS, name
    defined = set(choices.CHOICES)

    def structured(ast):
        if type(ast) is not list or not ast:
            return False
        if ast[0] in ("binary", "eq", "forall", "exists") or (ast[0] == "unary" and ast[1] in defined):
            return True
        return any(structured(item) for item in ast[1:])

    for unit in doc["units"]:
        if unit["status"] == "CHECKED":
            assert structured(unit["content"]), unit["id"]
            for name in predicates(unit["content"]):
                assert vocabulary["predicates"][name].get("verbalisation"), name


def _grounding_violations(unit, vocabulary):
    stop = set("a an the of to is are be by for in on and or not with its it this that from as at no "
               "any each every has have than".split())

    def words(text):
        return [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in stop]

    allowed = {w[:4] for w in words(unit["source"] + " " + readings.RESOLUTIONS.get(unit["id"], ""))}
    bad = []
    for kind, name in sorted(symbols(unit["content"])):
        if kind == "predicate":
            declaration = vocabulary["predicates"][name] if name not in FIXED_CAUSAL_WORDS else None
            if declaration is None or "defined" in declaration:
                continue  # profile words and defined terms carry their own definitions
            text = declaration["verbalisation"].replace("{0}", "").replace("{1}", "")
        else:
            text = vocabulary["constants"][name]["description"]
        bad += [(name, w) for w in words(text) if w[:4] not in allowed]
    return bad


def test_no_invented_content(doc, vocabulary):
    causal = load_document(ROOT / "causal.ve.md")
    causal_vocabulary = causal["environment"].to_dict()["vocabulary"]
    for document, words in ((doc, vocabulary), (causal, causal_vocabulary)):
        for unit in document["units"]:
            # No causal kind tag; causal links use the merged route or stay unformalised.
            assert "causal" not in kind_tags(unit["kind"]), unit["id"]
            if unit["status"] == "CHECKED":
                # Every word a reading adds, including a year or carried-over
                # OLD phrase, is in the span or a recorded resolution.
                assert _grounding_violations(unit, words) == [], unit["id"]
    env = doc["environment"].to_dict()
    assert "alternatives" not in env and "risk" not in env
    assert not any("regulated" in p for p in env["vocabulary"]["predicates"].values())
    causal_env = causal["environment"].to_dict()
    assert causal_env["alternatives"]["outcomes"] == "signed" and "risk" not in causal_env
    by_id = {u["id"]: u for u in doc["units"]}
    for unit in doc["units"]:
        if re.search(CAUSAL_WORDS, unit["source"]):
            assert unit["status"] == "UNFORMALISED", unit["id"]
        assert "norm" not in kind_tags(unit["kind"])
    # Milestones are plans: never checked, never instructions or obligations.
    for uid in [f"u{i:03d}" for i in (*range(12, 16), *range(17, 22), *range(78, 83))]:
        assert by_id[uid]["status"] in {"LABELLED", "OPEN"}
        assert by_id[uid]["kind"][0] == "attributed" and by_id[uid]["kind"][3] == readings.PLAN
    # Superseded OLD wording is attributed to the OLD text, never a current plan.
    for uid in ("u003", "u012", "u013", "u014", "u015", "u024", "u029", "u030", "u031", "u032",
                "u033"):
        assert by_id[uid]["kind"][:2] == ["attributed", "old_text"], uid
    assert by_id["u041"]["content"] == by_id["u092"]["content"] == readings.TRANSFER
    assert "plant" not in json.dumps(vocabulary).lower()


def test_meaning_shift_and_omission_regressions(doc):
    by_id = {u["id"]: u for u in doc["units"]}
    # "no novelty ... is claimed" denies a claim; it does not claim a denial.
    for uid in ("u054", "u058"):
        content = by_id[uid]["content"]
        assert content[0] == "and" and all(part[0] == "not" and part[1][1] == "claims"
                                           for part in content[1:])
    # VEX would require evidence; nothing makes VEX require the quality review.
    for uid in ("u039", "u090"):
        content = by_id[uid]["content"]
        assert predicates(content) == {"adopted", "required_by", "needs_quality_review"}
        assert ["unary", "needs_quality_review", ["const", "vex"]] not in json.loads(json.dumps(content))
    # The motivation is the author's link, not the update's; it is unformalised.
    assert by_id["u060"]["status"] == "UNFORMALISED"
    assert "supplied_update" not in json.dumps(by_id["u060"]["kind"])
    # Omitted parts are now stated or the unit is not CHECKED.
    title = json.dumps(by_id["u003"]["content"])
    assert all(c in title for c in ("verified_checker", "evidence_layer", "cross_examination",
                                    "smuggled_premises", "equivocation", "shifting_definitions"))
    assert set(readings.OLD_HARMS) <= {n for _, n in symbols(readings.CAUSAL["u029"]["content"])}
    assert "sound_proof_checking" in json.dumps(by_id["u052"]["content"])
    assert by_id["u019"]["status"] == "LABELLED"
    assert by_id["u026"]["meaning"] == by_id["u084"]["meaning"] == {"unformalised": "causal_means"}
    assert by_id["u024"]["meaning"] == {"open": ["matched_cost"]}
    # Every resolved pronoun or ellipsis in a checked unit is recorded.
    sets = {r["unit"]: r for r in doc["meta"]["reading_sets"]}
    for unit in doc["units"]:
        if unit["status"] == "CHECKED" and re.search(ANAPHORA, unit["source"]):
            assert unit["id"] in readings.RESOLUTIONS, unit["id"]
            if unit["id"] in sets:
                assert readings.RESOLUTIONS[unit["id"]] in sets[unit["id"]]["readings"][0]["admission"]["why"]


def holds(ast, model, stack=()):
    """Evaluate a formula in a finite model: ``model`` maps each sort to its
    elements and each predicate to its set of argument tuples."""
    op = ast[0]
    if op in ("unary", "binary"):
        args = tuple(stack[-1 - a[1]] if a[0] == "var" else a[1] for a in ast[2:])
        return args in model[ast[1]]
    if op == "and":
        return holds(ast[1], model, stack) and holds(ast[2], model, stack)
    if op == "or":
        return holds(ast[1], model, stack) or holds(ast[2], model, stack)
    if op == "not":
        return not holds(ast[1], model, stack)
    if op == "implies":
        return not holds(ast[1], model, stack) or holds(ast[2], model, stack)
    if op in ("forall", "exists"):
        test = all if op == "forall" else any
        return test(holds(ast[2], model, (*stack, e)) for e in model[ast[1]])
    raise AssertionError(op)


def vex_model(**overrides):
    """VEX adopted as mandatory evidence, with one reviewed evidence item."""
    model = {"evidence": {"e1"}, "is_evidence": {("vex",)}, "adopted": {("vex",)},
             "mandatory_for": {("vex", c) for c in readings.VEX_CLASSES},
             "required_by": {("e1", "vex")}, "needs_quality_review": {("e1",)}}
    model.update(overrides)
    return model


def conjuncts(ast):
    return [p for side in ast[1:] for p in conjuncts(side)] if ast[0] == "and" else [ast]


def _vex_part(ast):
    """The conjuncts of a title or note reading that mention VEX's evidence role."""
    return [p for p in conjuncts(ast) if {"is_evidence", "mandatory_for", "adopted"} & predicates(p)]


def test_mandatory_evidence_is_stated_and_stays_a_proposal(doc):
    # Review: five spans call VEX "mandatory evidence", but the formulas only
    # said it was proposed or developed and was "for" the claims, so they held
    # if VEX were optional or not evidence.
    by_id = {u["id"]: u for u in doc["units"]}
    spans = [u for u in doc["units"] if re.search(r"mandatory evidence", u["source"])]
    assert [u["id"] for u in spans] == ["u007", "u009", "u056", "u074", "u076"]
    for unit in spans:
        assert unit["status"] == "CHECKED", unit["id"]
        assert not any(p[1] == "applies_to" and p[2] == ["const", "vex"]
                       for p in conjuncts(unit["content"])), unit["id"]
        part = readings.conj(*_vex_part(unit["content"]))
        assert part == readings.VEX_MANDATORY, unit["id"]
        assert holds(part, vex_model()), unit["id"]
        # Optional once adopted, or not evidence: the reading is false.
        assert not holds(part, vex_model(mandatory_for={("vex", "statistical_claims")})), unit["id"]
        assert not holds(part, vex_model(is_evidence=set())), unit["id"]
        # Still a proposal: nothing asserts that VEX is adopted.
        assert holds(part, vex_model(adopted=set(), mandatory_for=set())), unit["id"]
        assert ["unary", "adopted", ["const", "vex"]] not in conjuncts(unit["content"])
    for uid in ("u007", "u056", "u074"):
        assert ["unary", "proposed", ["const", "vex"]] in conjuncts(by_id[uid]["content"])


def test_would_keeps_its_conditional_force(doc):
    # Review: u039/u090 "VEX would require evidence" was read as a required
    # evidence item existing now.  The requirement holds once VEX is adopted.
    for uid in ("u039", "u090"):
        content = next(u for u in doc["units"] if u["id"] == uid)["content"]
        assert content == readings.VEX_EVIDENCE
        assert content[0] == "implies" and content[1] == ["unary", "adopted", ["const", "vex"]]
        assert holds(content, vex_model())
        assert holds(content, vex_model(adopted=set(), required_by=set(), needs_quality_review=set()))
        assert not holds(content, vex_model(required_by=set()))
        assert not holds(content, vex_model(needs_quality_review=set()))
    # The class: each modal word in a checked span is kept by the kind or by
    # an explicit condition; none becomes a plain present-tense fact.
    modal = {"would": lambda u: u["content"][0] == "implies",
             "may": lambda u: "hedged" in kind_tags(u["kind"]),
             "could": lambda u: "hedged" in kind_tags(u["kind"]),
             "will": lambda u: "promised" in json.dumps(u["kind"]),
             "should": lambda u: "expects" in json.dumps(u["kind"])}
    seen = set()
    for unit in doc["units"]:
        for word, kept in modal.items():
            if unit["status"] == "CHECKED" and re.search(rf"\b{word}\b", unit["source"]):
                assert kept(unit), (unit["id"], word)
                seen.add(word)
    assert seen == {"would", "may", "will"}


def _sections(doc):
    """Yield (section, unit) where the section is OLD, NEW or Notes."""
    markers = {"OLD\n": "OLD", "NEW\n": "NEW", "Notes\n\n": "Notes", "=== PASTE ===\n\n": None}
    section = None
    for unit in doc["units"]:
        if unit["source"] in markers:
            section = markers[unit["source"]]
        elif unit["kind"] in ("meta", "question"):
            if section != "Notes":
                section = None
        else:
            yield section, unit


def test_kinds_keep_speaker_and_force(doc):
    # Review: u062 reports, in the present tense, what the comparison
    # includes; a PLAN kind turned it into an intention.  The class: OLD
    # wording is the OLD text's, and the author's notes are asserted or the
    # author's statement, never a belief, intention, expectation or exposition.
    seen = Counter()
    for section, unit in _sections(doc):
        seen[section] += 1
        if section == "OLD":
            assert unit["kind"][:2] == ["attributed", "old_text"], unit["id"]
        elif section == "NEW":
            assert unit["kind"][:2] == ["attributed", "new_text"], unit["id"]
        elif section == "Notes":
            text = json.dumps(unit["kind"])
            assert not re.search(r'"(intends|believes|expects|promised|exposition)"', text), unit["id"]
            if unit["status"] == "CHECKED":
                # "is presented as" (u056) reports the revised text's wording.
                assert unit["kind"] in ("asserted", "instruction") or \
                    unit["kind"][:3] == ["attributed", "new_text", "says"], unit["id"]
            elif unit["status"] == "OPEN":
                assert unit["kind"] == readings.AUTHOR_SAYS, unit["id"]
            else:
                assert unit["kind"] == ["unformalised", unit["meaning"]["unformalised"]], unit["id"]
    assert seen["OLD"] == 11 and seen["NEW"] == 14 and seen["Notes"] == 27
    by_id = {u["id"]: u for u in doc["units"]}
    assert by_id["u062"]["kind"] == "asserted" and by_id["u062"]["support"] == "assumption"
    assert "reading-u062" in {r["id"] for r in doc["meta"]["reading_sets"]}
    assert by_id["u033"]["kind"][:2] == ["attributed", "old_text"]


def test_causal_units_on_the_merged_route(doc):
    causal = check_document(ROOT / "causal.ve.md")
    assert causal["admission"]["admitted"] is True
    assert causal["coverage"]["bytes_by_status"] == {"CHECKED": 279}
    loaded = load_document(ROOT / "causal.ve.md")
    by_id = {u["id"]: u for u in doc["units"]}
    assert [u["id"] for u in loaded["units"]] == list(readings.CAUSAL)
    for unit in loaded["units"]:
        main = by_id[unit["id"]]
        assert unit["source"] == main["source"]
        assert main["status"] == "UNFORMALISED"
        assert main["meaning"] == {"unformalised": readings.CAUSAL_REASON}
    # Why they are separate: the Lean route refuses definitions beside alternatives.
    combined = copy.deepcopy(builder.CAUSAL_ENV)
    combined["profiles"] = ["alternatives@0", "definitions@0", "norms@0", "relational-fol@0"]
    combined["vocabulary"]["predicates"]["affordable_proof"] = {
        "arguments": ["harm"], "description": "probe",
        "defined": {"arguments": ["harm"], "body": ["top"]}}
    result = run_case({"id": "probe", "kind": "alt-elaborate", "environment": combined, "norms": []})
    assert result["status"] == "error" and "with definitions is not implemented" in result["error"]


def test_document_coverage_and_premise_limit():
    result = check_document(ROOT / "document.ve.md")
    coverage = result["coverage"]
    assert coverage["source_bytes"] == coverage["accounted_bytes"] == 7619
    assert coverage["coverage_percent"] == 100
    assert coverage["bytes_by_status"] == {
        "CHECKED": 3351, "LABELLED": 1029, "OPEN": 2114, "UNFORMALISED": 1125}
    assert coverage["unformalised_reasons"] == {
        "causal_means": 2, "causal_route_excludes_definitions": 4,
        "motivation_link": 1, "vague_comparison": 1, "vague_evaluation": 1}
    assert coverage["residual"]["open_terms"] == 4
    assert Counter(u["status"] for u in load_document(ROOT / "document.ve.md")["units"]) == {
        "CHECKED": 40, "LABELLED": 25, "OPEN": 19, "UNFORMALISED": 9}
    assert result["premises"]["status"] in {"UNKNOWN", "model"}
