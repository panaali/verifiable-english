"""keyed-wording F1: docs say who computes the keyed answers of a soft-rule norm document, and that is true.

The class: a document claims Lean decides (evaluates, checks) an answer that Python's retained path computes.
`docs/usecases/keyed-answers.md` owns that wording; its table is checked here against the paths the code takes
(recorded by `usecases/keyed_paths.py`) on a small soft document and in the three harnesses' saved counts.
"""
from __future__ import annotations

import importlib
import importlib.util
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "docs" / "usecases" / "keyed-answers.md"
_SPEC = importlib.util.spec_from_file_location("keyed_paths", ROOT / "usecases" / "keyed_paths.py")
keyed_paths = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(keyed_paths)

# The keyed-wording review's overclaims (F1): each said Lean evaluates the models Python evaluates.
OVERCLAIMS = ("evaluates models over those formulas", "evaluate a model over them", "the evaluation are Lean",
              "checking under those answers is Lean")
# The documents that describe the keyed answers: the README, the architecture map, every use-case README
# and every use-case document.
DESCRIBING = ("README.md", "docs/ARCHITECTURE.md", "usecases/*/README.md", "docs/usecases/**/*.md")
LINKING = ("README.md", "docs/ARCHITECTURE.md", "usecases/anthropic-rsp/README.md",
           "usecases/openai-preparedness/README.md", "usecases/safety-framework/README.md")


def _table():
    """{recorded path: owner} from the page's table; every recorded path is in one row."""
    owners = {}
    for line in PAGE.read_text().splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 3 or cells[1] not in ("Lean", "Python"):
            continue
        if cells[2].startswith("not recorded"):
            continue
        for path in re.findall(r"`([^`]+)`", cells[2]):
            assert path not in owners, f"{path} is in two rows"
            owners[path] = cells[1].lower()
    assert owners, "the page has no answer table"
    return owners


def _check_against_table(counts):
    owners = _table()
    for key in counts:
        owner, path = key.split(" ", 1)
        assert path in owners, f"{key}: a path the page's table does not list"
        assert owners[path] == owner, f"{key}: the page says {owners[path]}"


def test_no_describing_document_says_lean_evaluates_pythons_models():
    """PROBE F1, over every document that describes the keyed answers."""
    norms = importlib.import_module("ve.norms")
    import inspect
    python = "_Evaluator" in inspect.getsource(norms.NormDocument.selected_rules) + inspect.getsource(
        norms._find_conflict)
    assert python, "selected_rules and _find_conflict no longer evaluate in Python: update keyed-answers.md"
    found = [(str(path.relative_to(ROOT)), phrase)
             for pattern in DESCRIBING for path in sorted(ROOT.glob(pattern))
             for phrase in OVERCLAIMS if phrase in path.read_text()]
    assert found == []


def test_the_wording_has_one_owner():
    """Each describing document links the page instead of keeping its own copy of the table."""
    for name in LINKING:
        text = (ROOT / name).read_text()
        assert "keyed-answers.md" in text, name
        assert "| Answer | Owner |" not in text, name


def test_saved_harness_paths_match_the_table():
    """Every path the three keyed harnesses took (saved 2026-11-14) is in the table with its true owner."""
    evidence = json.loads(keyed_paths.EVIDENCE.read_text())
    assert sorted(evidence) == sorted(keyed_paths.HARNESSES)
    for harness, counts in evidence.items():
        assert counts, harness
        _check_against_table(counts)
        # Selection and outcomes are Lean's in every harness (kb-10b); conflicts are still Python's (kb-10c).
        assert counts["lean soft-selected"] > 0 and counts["python _find_conflict"] > 0, harness
        assert "python selected_rules" not in counts and "python completed" not in counts, harness
        assert "lean _check_conflict_lean" not in counts, harness


def _soft_env():
    """A norms environment with the soft-norms profile: an obligation `required` and its permission."""
    from ve.profiles import LANGUAGE, SPEC_REVISION
    from ve.softnorms import SoftEnvironment
    regulated = {"role": "obligation", "default": "deny", "act": "{0} be done", "permission": "permitted"}
    return SoftEnvironment({
        "language": LANGUAGE, "profiles": ["norms@0", "relational-fol@0", "soft-norms@0"],
        "spec_revision": SPEC_REVISION,
        "vocabulary": {
            "sorts": {"act": {"description": "act"}}, "constants": {},
            "predicates": {
                "required": {"arguments": ["act"], "description": "obligation", "regulated": regulated},
                "permitted": {"arguments": ["act"], "description": "permission",
                              "regulated": {"role": "permission", "default": "deny", "act": "{0} be done"}}},
            "soft": {"parties": ["operator", "user"], "ranks": ["helpfulness"], "outranks": [], "ties": [],
                     "outranking": {"mode": "strict"}}}})


@pytest.fixture(scope="module")
def soft_document():
    from ve.norm_english import parse_english
    with keyed_paths.recording() as counts:
        parsed = parse_english(_soft_env(), "Rule 1. Every act should be done.\n"
                                            "Rule 2. Every act must be done.\nRule 3. No act may be done.")
    assert counts == {"lean soft-elaborate": counts["lean soft-elaborate"]} and counts["lean soft-elaborate"]
    return parsed.elaborated


def _case(document):
    from ve.model import FiniteModel
    env = document.base_environment()
    return FiniteModel.from_dict(env, {"complete": True, "domains": {"act": ["a"]}, "constants": {},
                                       "relations": {p: [] for p in env.predicates}})


def test_a_soft_document_takes_no_lean_norms_route(soft_document):
    norms = importlib.import_module("ve.norms")
    assert type(soft_document).__name__ == "SoftenedNormDocument"
    assert not norms._lean_route(soft_document)


def test_selection_and_outcome_are_leans_soft_selected(soft_document):
    """kb-10b: a document built from its soft source asks Lean's `soft-selected`, once per document and model."""
    model = _case(soft_document)
    with keyed_paths.recording() as counts:
        selected = soft_document.selected_rules("required", model, ("a",))
        outcome = soft_document.outcome_at("required", model, ("a",))
    assert [rule.name for rule in selected] == ["rule-2"] and outcome is True
    assert dict(counts) == {"lean soft-selected": 1}
    _check_against_table(counts)


def test_a_hand_built_document_keeps_pythons_selection(soft_document):
    """A SoftenedNormDocument without its soft source is Python's evaluation, and the page says so."""
    from ve.softnorms import SoftenedNormDocument
    bare = SoftenedNormDocument(soft_document.env, list(soft_document.rules))
    model = _case(soft_document)
    with keyed_paths.recording() as counts:
        selected = bare.selected_rules("required", model, ("a",))
        outcome = bare.outcome_at("required", model, ("a",))
    assert [rule.name for rule in selected] == ["rule-2"] and outcome is True
    assert dict(counts) == {"python selected_rules": 1, "python outcome_at": 1}
    _check_against_table(counts)


def test_a_conflict_on_a_model_is_pythons_evaluation(soft_document):
    norms = importlib.import_module("ve.norms")
    model = _case(soft_document)
    with keyed_paths.recording() as counts:
        report = norms.check_conflict(soft_document, model=model)
    assert (report.status, report.target) == ("CONFLICT", "required->permitted")
    assert counts["python _check_conflict_python"] == 1 and counts["python _find_conflict"] == 1
    assert not [key for key in counts if key.startswith("lean ")]
    _check_against_table(counts)


def test_conflict_freedom_is_a_certificate_lean_replays():
    from ve.norm_english import parse_english
    norms = importlib.import_module("ve.norms")
    document = parse_english(_soft_env(), "Rule 1. Every act should be done.\nRule 2. No act may be done.").elaborated
    with keyed_paths.recording() as counts:
        report = norms.check_conflict(document, prove=True)
    assert report.status == "CONFLICT-FREE"
    targets = len(document.conflict_targets())
    assert counts["lean _check_certificate_lean"] == targets and counts["python _check_conflict_python"] == 1
    assert "python _check_certificate_python" not in counts
    _check_against_table(counts)


def test_the_public_evaluate_is_leans(soft_document):
    from ve.ast import Forall, Unary, Var
    evaluate = importlib.import_module("ve.evaluate").evaluate
    env = soft_document.base_environment()
    (predicate,) = env.predicates
    with keyed_paths.recording() as counts:
        result = evaluate(env, Forall("act", Unary(predicate, Var(0))), _case(soft_document), trace=False)
    assert result.value is False
    assert counts["lean _evaluate_lean"] == 1 and not [key for key in counts if key.startswith("python ")]
    _check_against_table(counts)


def test_the_recorder_restores_what_it_patches():
    evaluate = importlib.import_module("ve.evaluate")
    entailment = importlib.import_module("ve.entailment")
    before = (evaluate._Evaluator.__init__, entailment._check_certificate_lean, evaluate._evaluate_lean)
    with pytest.raises(RuntimeError):
        with keyed_paths.recording():
            raise RuntimeError
    assert (evaluate._Evaluator.__init__, entailment._check_certificate_lean, evaluate._evaluate_lean) == before
