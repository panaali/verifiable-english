"""fid-mech-b3: the result record, the K verdict and inputs_sha256 (plan 2e), on a git repo built in tmp_path."""
from __future__ import annotations

import ast
import copy
import json
import re
import subprocess
from pathlib import Path

import pytest

from tools.fidmech import records as R
from tools.fidmech.worker import Mutant

DOC = "toy-doc"
SHA = "0" * 64


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.invalid",
                    "-c", "commit.gpgsign=false", *args], check=True, capture_output=True)


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    write(root / "usecases" / "pinned_sources.json",
          json.dumps({"version": 1, "sources": {DOC: {"text_sha256": "a" * 64, "pdf_sha256": "b" * 64}}}))
    for name in ("boundaries.json", "ruled_out.json", "bindings.json"):
        write(root / "usecases" / DOC / "fidmech" / name, "[]\n")
    write(root / "usecases" / DOC / "run.py", "X = 1\n")
    for name in ("cues.json", "logic_words.json", "segment.py"):
        write(root / "tools" / "fidmech" / name, "{}\n")
    git(root, "init", "-q")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "base")
    return root


def edit(path, text):
    def apply(root):
        write(root / path, text)
    return apply


def json_edit(path, change):
    def apply(root):
        data = json.loads((root / path).read_text())
        change(data)
        write(root / path, json.dumps(data))
    return apply


CHANGES = {
    "commit": (lambda root: git(root, "commit", "-q", "--allow-empty", "-m", "next"), {"commit"}),
    "tracked edit": (edit(f"usecases/{DOC}/run.py", "X = 2\n"), {"uncommitted"}),
    "untracked file": (edit(f"usecases/{DOC}/new.py", "Y = 1\n"), {"uncommitted"}),
    "source sha256": (json_edit("usecases/pinned_sources.json",
                                lambda d: d["sources"][DOC].update(text_sha256="c" * 64)), {"uncommitted", "sources"}),
    "boundaries.json": (edit(f"usecases/{DOC}/fidmech/boundaries.json", "[1]\n"), {"uncommitted", "case_files"}),
    "ruled_out.json": (edit(f"usecases/{DOC}/fidmech/ruled_out.json", "[1]\n"), {"uncommitted", "case_files"}),
    "bindings.json": (edit(f"usecases/{DOC}/fidmech/bindings.json", "[1]\n"), {"uncommitted", "case_files"}),
    "equivalents.json created": (edit(f"usecases/{DOC}/fidmech/equivalents.json", "[]\n"),
                                 {"uncommitted", "case_files"}),
    "actors.json created": (edit(f"usecases/{DOC}/fidmech/actors.json", "[]\n"), {"uncommitted", "case_files"}),
    "cues.json": (edit("tools/fidmech/cues.json", "{\"a\": 1}\n"), {"uncommitted", "tools_fidmech"}),
    "logic_words.json": (edit("tools/fidmech/logic_words.json", "{\"a\": 1}\n"), {"uncommitted", "tools_fidmech"}),
    "a tools/fidmech file": (edit("tools/fidmech/segment.py", "Z = 1\n"), {"uncommitted", "tools_fidmech"}),
}


def test_the_inputs_are_deterministic_and_a_file_later_batches_create_enters_as_absent(repo):
    first, again = R.collect_inputs(repo, DOC), R.collect_inputs(repo, DOC)
    assert first == again and R.inputs_sha256(first) == R.inputs_sha256(again)
    assert first["case_files"]["equivalents.json"] is None
    assert first["generator_version"] is None and first["mutants"] == []
    assert set(first) == set(R.INPUT_KEYS)
    assert first["sources"] == {"text_sha256": "a" * 64, "pdf_sha256": "b" * 64}


@pytest.mark.parametrize("change", sorted(CHANGES))
def test_inputs_sha256_changes_when_any_listed_input_changes(repo, change):
    apply, keys = CHANGES[change]
    before = R.collect_inputs(repo, DOC)
    apply(repo)
    after = R.collect_inputs(repo, DOC)
    assert {k for k in R.INPUT_KEYS if before[k] != after[k]} == keys
    assert R.inputs_sha256(before) != R.inputs_sha256(after)


def test_the_generator_version_and_each_mutant_id_and_edit_enter_the_hash(repo):
    base = R.collect_inputs(repo, DOC, mutants=[Mutant("m1", {"a/run.py": "x"})])
    variants = [R.collect_inputs(repo, DOC, generator_version="wording/1", mutants=[Mutant("m1", {"a/run.py": "x"})]),
                R.collect_inputs(repo, DOC, mutants=[Mutant("m2", {"a/run.py": "x"})]),
                R.collect_inputs(repo, DOC, mutants=[Mutant("m1", {"a/run.py": "y"})]),
                R.collect_inputs(repo, DOC, mutants=[Mutant("m1", {"a/run.py": "x"}), Mutant("m0")])]
    hashes = {R.inputs_sha256(v) for v in variants}
    assert len(hashes) == len(variants) and R.inputs_sha256(base) not in hashes
    order = [Mutant("b"), Mutant("a")]
    assert R.collect_inputs(repo, DOC, mutants=order) == R.collect_inputs(repo, DOC, mutants=order[::-1])


def test_every_key_of_the_inputs_enters_the_hash_and_a_missing_or_extra_key_is_refused(repo):
    inputs = R.collect_inputs(repo, DOC)
    for key in R.INPUT_KEYS:
        changed = copy.deepcopy(inputs)
        changed[key] = ["changed"]
        assert R.inputs_sha256(changed) != R.inputs_sha256(inputs), key
    with pytest.raises(ValueError, match="inputs keys"):
        R.inputs_sha256({k: v for k, v in inputs.items() if k != "mutants"})
    with pytest.raises(ValueError, match="inputs keys"):
        R.inputs_sha256({**inputs, "seconds": 1})


BASE = {"Q1": (("ve", "ALL"),), "Q2": (("ve", "NONE"),), "Q3": (("ve", "UNDECIDED"),)}


@pytest.mark.parametrize("mutant, expected", [
    (BASE, ("survived", [], [])),
    ({**BASE, "Q1": (("ve", "NONE"),)}, ("killed", ["Q1"], [])),
    ({**BASE, "Q2": (("ve", "UNDECIDED"),)}, ("inconclusive", [], ["Q2"])),
    ({**BASE, "Q3": (("ve", "ALL"),)}, ("inconclusive", [], ["Q3"])),
    ({**BASE, "Q1": (("ve", "NONE"),), "Q3": (("ve", "ALL"),)}, ("killed", ["Q1"], ["Q3"])),
    ({**BASE, "Q1": (("ve", "ALL"), ("soft.ve", ("RS1=default",)))}, ("killed", ["Q1"], [])),
])
def test_k_kills_on_a_decided_answer_that_differs_and_a_move_to_or_from_undecided_is_inconclusive(mutant, expected):
    verdict, kernel = R.kernel_verdict(BASE, mutant)
    assert (verdict, kernel["changed"], kernel["inconclusive"]) == expected


@pytest.mark.parametrize("undecided", ["UNKNOWN", "UNDECIDED", "UNDECIDED-faithful", "NOT RUN", "resource-limit",
                                       "resource limit: no quantity certificate", "UNKNOWN (budget)"])
@pytest.mark.parametrize("shape", ["flat", "premises", "parts"])
def test_a_move_to_or_from_every_third_value_spelling_is_inconclusive_never_a_kill(undecided, shape):
    """fid-mech-b3 review F1: FSF writes UNKNOWN (N1, premises, S1, S4, D1, D3); it was scored a kill."""
    def answer(value):
        if shape == "premises":
            return (("ve", "SOME(RS2=U)"), ("premises", (value, ("p(x)",)) if value != "model" else value))
        if shape == "parts":
            return (("ve", (("GOV", value), ("SILENT:CCA", "ALL"))),)
        return (("ve", value),)
    decided = "model" if shape == "premises" else "ALL"
    for before, after in ((decided, undecided), (undecided, decided)):
        verdict, kernel = R.kernel_verdict({"N1": answer(before)}, {"N1": answer(after)})
        assert (verdict, kernel["changed"], kernel["inconclusive"]) == ("inconclusive", [], ["N1"]), (before, after)


def test_the_review_probe_f1_an_fsf_answer_moving_to_unknown_is_inconclusive():
    verdict, _ = R.kernel_verdict({"N1": (("ve", "ALL"),)}, {"N1": (("ve", "UNKNOWN"),)})
    assert verdict == "inconclusive"


@pytest.mark.parametrize("decided", ["UNKNOWN_ACTOR", "SOME(UNKNOWN=x)", "UNKNOWNS", "NOT RUNNING", "unknown"])
def test_a_decided_string_that_only_contains_a_third_value_word_still_kills(decided):
    verdict, kernel = R.kernel_verdict({"Q1": (("ve", "ALL"),)}, {"Q1": (("ve", decided),)})
    assert (verdict, kernel["changed"]) == ("killed", ["Q1"])


def test_fsfs_own_undecided_answers_on_its_committed_results_are_inconclusive():
    """End to end on usecases/safety-framework/results.json through the adapter's projection: each FSF site that
    writes UNKNOWN (and a missing item, NOT RUN) moves an answer to the third value; a decided change still kills."""
    from tools.fidmech import adapters
    root = Path(__file__).resolve().parents[1]
    results = json.loads((root / "usecases" / "safety-framework" / "results.json").read_text(encoding="utf-8"))
    base = adapters.project("safety-framework", results).answers
    rows = {row["id"]: row for row in results["comparison"]}
    edits = {"N1": ("ve", "UNKNOWN"), "S1-L1": ("ve", "UNKNOWN"), "S4": ("ve", "UNKNOWN"), "D1": ("ve", "UNKNOWN"),
             "D3": ("ve", "UNKNOWN"), "G6": ("premises", ["UNKNOWN", ["p(x)"]]), "G9": ("ve", "NOT RUN")}
    assert set(edits) <= set(rows)
    for item, (field, value) in edits.items():
        mutated = copy.deepcopy(results)
        next(r for r in mutated["comparison"] if r["id"] == item)[field] = value
        answers = adapters.project("safety-framework", mutated).answers
        assert R.kernel_verdict(base, answers)[0] == "inconclusive", item
        assert R.kernel_verdict(answers, base)[0] == "inconclusive", item
    mutated = copy.deepcopy(results)
    next(r for r in mutated["comparison"] if r["id"] == "S1-L1")["ve"] = "severe"
    assert rows["S1-L1"]["ve"] != "severe"
    assert R.kernel_verdict(base, adapters.project("safety-framework", mutated).answers)[0] == "killed"


# Strings of the documents' sources that name the third value but are never an answer value: result-dict keys,
# summary keys, reason texts kept beside an UNDECIDED answer and error-message fragments. Any other spelling must be
# one `records.UNDECIDED` recognises.
THIRD_VALUE_WORDS = re.compile(r"unknown|undecided|not.run|resource.limit|time.?out|timed.out|exhaust|budget|"
                               r"inconclusive|undetermined|unresolved", re.I)
NOT_ANSWERS = {
    "undecided": "the key of a result's undecided reason; its answer is verdict()'s UNDECIDED",
    "faithful_undecided": "a summary count key",
    "unknown_items": "a summary list key",
    "resource_limit": "a summary count key",
    "unresolved_reading_sets": "a coverage-residual key of readings_r1's report",
    ": unknown reading ": "a translation error-message fragment",
    "conflict check UNKNOWN for ": "a SystemExit message: the run stops, the worker records an error",
    "unknown": "measure_r1's measurement label, not run.py's answer",
    "VE limit (SC): no exhaustive dead-rule or changelog-rule certificate": "an undecided reason; the answer is UNDECIDED",
    "comparison[].agree; comparison[].status == 'UNDECIDED-faithful' marks the rest": "a summary field description",
}


def _source_strings(path):
    """Every string constant of a Python file except docstrings, read by the Python parser."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    docstrings = {id(node.body[0].value) for node in ast.walk(tree)
                  if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                  and node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant)}
    return [(node.lineno, node.value) for node in ast.walk(tree) if isinstance(node, ast.Constant)
            and isinstance(node.value, str) and id(node) not in docstrings]


def test_every_third_value_spelling_in_an_adapted_documents_sources_is_recognised_by_the_kill_rule():
    """The class of review F1: a document's spelling of the third value the K rule does not know scores a kill. Every
    adapted document's sources are read (ast); a third-value string is either recognised or listed as no answer."""
    from tools.fidmech import adapters
    root = Path(__file__).resolve().parents[1]
    unknown, seen = [], set()
    for document in adapters.DOCUMENTS:
        files = sorted((root / "usecases" / document).glob("*.py"))
        assert files, document
        for path in files:
            for line, value in _source_strings(path):
                if THIRD_VALUE_WORDS.search(value):
                    seen.add(value)
                    if not R._undecided(value) and value not in NOT_ANSWERS:
                        unknown.append(f"{path.relative_to(root)}:{line}: {value!r}")
    assert not unknown, unknown
    assert {"UNKNOWN", "UNDECIDED", "NOT RUN", "resource-limit"} <= seen
    assert set(NOT_ANSWERS) <= seen, sorted(set(NOT_ANSWERS) - seen)


def test_the_movement_toward_and_away_from_the_key_reads_the_documents_agreement():
    mutant = {**BASE, "Q1": (("ve", "NONE"),), "Q2": (("ve", "ALL"),)}
    _, kernel = R.kernel_verdict(BASE, mutant, {"Q1": True, "Q2": False, "Q3": False},
                                 {"Q1": False, "Q2": True, "Q3": False})
    assert (kernel["toward_key"], kernel["away_from_key"]) == (1, 1)


def test_a_mutant_whose_items_differ_from_the_baseline_is_an_error():
    verdict, kernel = R.kernel_verdict(BASE, {"Q1": BASE["Q1"]})
    assert verdict == "error" and kernel["items_differ"] == ["Q2", "Q3"]


VERDICT = {"K": "killed", "L1": "survived", "L2": "survived", "L3": "killed", "L4": "survived", "D": "survived",
           "CR": "not-read"}
KERNEL = {"changed": ["Q1"], "inconclusive": [], "toward_key": 0, "away_from_key": 1}


def test_a_result_record_has_the_plans_fields_in_their_vocabulary():
    record = R.result_record("m1", VERDICT, KERNEL, 12.5, 3.1, "w0", True, SHA)
    assert list(record) == ["id", "verdict", "kernel", "seconds", "cpu_seconds", "worker", "sentinel_ok",
                            "inputs_sha256"]
    assert R.VOCABULARY["K"] == ("killed", "survived", "inconclusive", "error", "not-run")
    assert R.VOCABULARY["CR"] == ("found", "missed", "not-read")
    assert all(R.VOCABULARY[c] == ("killed", "survived") for c in ("L1", "L2", "L3", "L4", "D"))


@pytest.mark.parametrize("bad", [
    {**VERDICT, "K": "INVALID"}, {**VERDICT, "L1": "not-run"}, {**VERDICT, "CR": "killed"},
    {k: v for k, v in VERDICT.items() if k != "D"}, {**VERDICT, "L5": "survived"},
])
def test_a_verdict_outside_its_vocabulary_or_a_missing_one_is_refused(bad):
    with pytest.raises(ValueError, match="verdict"):
        R.result_record("m1", bad, KERNEL, 1.0, 1.0, "w0", True, SHA)


def test_a_record_without_a_bool_sentinel_or_a_sha256_or_a_full_kernel_is_refused():
    with pytest.raises(ValueError, match="sentinel_ok"):
        R.result_record("m1", VERDICT, KERNEL, 1.0, 1.0, "w0", None, SHA)
    with pytest.raises(ValueError, match="sha256"):
        R.result_record("m1", VERDICT, KERNEL, 1.0, 1.0, "w0", True, "abc")
    with pytest.raises(ValueError, match="kernel lacks"):
        R.result_record("m1", VERDICT, {"changed": []}, 1.0, 1.0, "w0", True, SHA)
