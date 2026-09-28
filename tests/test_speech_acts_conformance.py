"""Shared section-9 speech-act fixtures across Python, Lean, and Rust FOL evaluation.

Rust evaluates the regenerated formulas in a complete model. It has no speech
admission route, so these checks do not enable trusted document admission.
"""
from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys

import pytest

from ve.ast import _to_data
from ve.environment import Environment
from ve.errors import VEError
from ve.speech_acts import SpeechDocument
from ve.speech_document import load_speech_document
from ve.speech_english import parse_speech

from test_speech_acts_lean import F0, MODEL, ROOT, U, command, elaborate, lean, model, polar, run1, unit, which


@pytest.fixture(scope="module")
def rust():
    executable = ROOT / "rust/target/debug/ve"
    if not executable.exists():
        cargo = shutil.which("cargo")
        if cargo is None:
            pytest.skip("cargo is required for speech-act FOL conformance")
        built = subprocess.run([cargo, "build", "-p", "ve"], cwd=ROOT / "rust",
                               capture_output=True, text=True, timeout=600)
        assert built.returncode == 0, built.stdout + built.stderr
    return executable


def core(env, document):
    return SpeechDocument(Environment(env), document["units"], document.get("queries", []))


def fol_environment(env):
    """The common FOL vocabulary after speech and norm metadata are erased."""
    base = copy.deepcopy(env)
    base.pop("speech_acts")
    base["profiles"] = ["relational-fol@0"]
    for predicate in base["vocabulary"]["predicates"].values():
        predicate.pop("regulated", None)
    return base


def rust_values(rust, env, formulas, complete_model):
    case = {"id": "speech-section-9", "environment": fol_environment(env),
            "ast": formulas, "model": complete_model}
    completed = subprocess.run([str(rust), "conformance", "-"], input=json.dumps([case]),
                               capture_output=True, text=True, timeout=60)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    [result] = json.loads(completed.stdout)
    assert result["status"] == "ok", result
    return result["values"]


def test_alpha_command_regeneration_and_no_done_fact(rust, lean):
    env = F0()
    document = {"units": [unit("u1", 0, "instruction", command("require", "click_required", ["check"]))]}
    py, lean = core(env, document), elaborate(env, document)
    [cmd] = py.commands
    assert cmd.active
    assert py.policy.rules[0].to_dict()["norm"] == lean["commands"][0]["demand"]
    assert py.meaning_ids["u1"] == lean["commands"][0]["meaning_id"]
    assert [_to_data(f) for f in py.premises()] == lean["premises"]
    complete = py.complete_model(MODEL).to_dict()
    assert rust_values(rust, env,
                       [["binary", "click_required", ["const", "alice"], ["const", "check"]],
                        ["binary", "done_click", ["const", "alice"], ["const", "check"]]],
                       complete) == [True, False]


@pytest.mark.parametrize("reviewed,expected", [([], "no"), ([["atlas"]], "yes")])
def test_eta_polar_answer_in_same_model(rust, lean, reviewed, expected):
    env = F0()
    document = {"units": [unit("u5", 0, "question", polar(U("reviewed", "atlas")))]}
    py, lean = core(env, document), elaborate(env, document)
    q = py.questions[0]
    assert py.meaning_ids[q.unit] == lean["questions"][0]["meaning_id"]
    assert _to_data(py.presupposition(q)) == lean["questions"][0]["presupposition"]
    base_model = model(reviewed=reviewed)
    py_answer = py.evaluate_answer_model(q, expected, base_model)
    lean_answer = run1({"id": "eta", "kind": "speech-answer", "environment": env,
                        "document": document, "question": "u5", "evidence": {"model": base_model},
                        "model_id": "same-model"})
    assert py_answer["status"] == "evaluated"
    assert lean_answer["answer"] == f"evaluated {expected} in model same-model (this situation only)"
    assert rust_values(rust, env, [U("reviewed", "atlas"), ["not", U("reviewed", "atlas")]],
                       py.complete_model(base_model).to_dict()) == ([True, False] if expected == "yes" else [False, True])


def test_iota_false_presupposition_is_neither_yes_nor_no(rust, lean):
    env = F0()
    document = {"units": [unit("u5", 0, "question", which("which_one"))]}
    py, lean = core(env, document), elaborate(env, document)
    q = py.questions[0]
    h = _to_data(py.presupposition(q))
    assert h == lean["questions"][0]["presupposition"]
    base_model = model(reviewed=[["atlas"], ["beacon"]])
    assert py.evaluate_answer_model(q, "atlas", base_model)["status"] == "PRESUPPOSITION-FAILED"
    answer = run1({"id": "iota", "kind": "speech-answer", "environment": env,
                   "document": document, "question": "u5", "evidence": {"model": base_model},
                   "model_id": "same-model"})
    assert answer["answer"] == "PRESUPPOSITION-FAILED (model same-model)"
    assert rust_values(rust, env, [h], py.complete_model(base_model).to_dict()) == [False]


def test_beta_prohibition_regenerates_permission_negation(rust, lean):
    env = F0()
    document = {"units": [unit("u1", 0, "instruction", command("forbid", "share_permitted", ["token1"]))]}
    py, lean = core(env, document), elaborate(env, document)
    rule = py.policy.rules[0].to_dict()["norm"]
    assert rule == lean["commands"][0]["demand"]
    assert rule["sign"] is False and rule["predicate"] == "share_permitted"
    complete = py.complete_model(MODEL).to_dict()
    assert rust_values(rust, env, [["binary", "share_permitted", ["const", "alice"], ["const", "token1"]]],
                       complete) == [False]


def test_xi_eta_source_to_answer_end_to_end(rust, lean, tmp_path):
    env = F0()
    env["vocabulary"]["predicates"]["reviewed"]["verbalisation"] = "{0} is reviewed"
    lines = ["In this task, you are alice.\n", "Click check.\n", "Is atlas reviewed?\n"]
    positions = [0]
    for line in lines:
        positions.append(positions[-1] + len(line.encode()))
    units = [
        {**unit("u0", positions[0], "binding", {"binding": {"you": "alice"}}),
         "span": positions[:2]},
        {**unit("u1", positions[1], "instruction", command("require", "click_required", ["check"])),
         "span": positions[1:3]},
        {**unit("u2", positions[2], "question", polar(U("reviewed", "atlas"))),
         "span": positions[2:4]},
    ]
    base_model = model(reviewed=[["atlas"]])
    metadata = {"format": "ve-document@2", "environment": env, "units": units,
                "answers": [{"question": "u2", "by": "checker", "support": "model", "answer": "yes",
                             "evidence": {"model": base_model}}]}
    path = tmp_path / "speech.ve.md"
    path.write_text("---\n" + json.dumps(metadata) + "\n---\n" + "".join(lines))
    source = load_speech_document(path)
    assert source.answer_lines[0]["status"] == "evaluated"
    assert source.coverage()["bytes_by_class"] == {"C": positions[-1]}
    inspected = subprocess.run([sys.executable, "-m", "ve", "speech-acts", str(path)],
                               capture_output=True, text=True, timeout=60)
    assert inspected.returncode == 0, inspected.stderr
    report = json.loads(inspected.stdout)
    assert report["status"] == "experimental" and report["answers"][0]["status"] == "evaluated"
    lean_result = elaborate(env, {"units": units})
    assert source.document.meaning_ids["u1"] == lean_result["commands"][0]["meaning_id"]
    assert source.document.meaning_ids["u2"] == lean_result["questions"][0]["meaning_id"]
    assert run1({"id": "source-answer", "kind": "speech-answer", "environment": env,
                 "document": {"units": units}, "question": "u2", "evidence": {"model": base_model},
                 "model_id": "same-model"})["answer"] == "evaluated yes in model same-model (this situation only)"
    assert rust_values(rust, env, [U("reviewed", "atlas")],
                       source.document.complete_model(base_model).to_dict()) == [True]


def test_proof_task_wording_uses_an_act_both_linters_accept(lean):
    # Regression: Python once exempted `{0} submit a certificate for {1}` from W1's act linter,
    # so every Python proof task named an environment the Lean route rejected.
    env = F0()
    env["vocabulary"]["predicates"]["cat"]["verbalisation"] = "{0} is a cat"
    for name in ("submit_required", "submit_permitted"):
        rejected = copy.deepcopy(env)
        rejected["vocabulary"]["predicates"][name]["regulated"]["act"] = "{0} submit a certificate for {1}"
        with pytest.raises(VEError, match=f"invalid act phrase for {name}"):
            Environment(rejected)
        lean_error = run1({"id": "act", "kind": "speech-elaborate", "environment": rejected,
                           "document": {"units": []}})["error"]
        assert "invalid act phrase" in lean_error
    e = Environment(env)
    content, kind = parse_speech(e, "Prove that tom is a cat using these premises.", e.speech_acts, query="q1")
    assert (kind, content["act"], content["args"]) == ("instruction", "submit_required", ["q1"])
    document = {"units": [unit("u1", 0, "asserted", {"ast": U("cat", "tom")}), unit("u2", 1, kind, {"command": content})],
                "queries": [{"id": "q1", "premises": ["u1"], "target": {"ast": U("cat", "tom")}}]}
    assert len(elaborate(env, document)["commands"]) == 1
    assert len(core(env, document).commands) == 1


@pytest.mark.parametrize("target", [["top"], U("cat", "tom"), U("animal", "tom")])
def test_query_bound_meaning_ids_agree_with_lean(lean, target):
    # Regression: Python appended a flat `query_meaning_ids` list while Lean nests
    # `query: {id, premises, target}`, so proof tasks and follows questions disagreed.
    env = F0()
    premises = [unit("u1", 0, "asserted", {"ast": U("cat", "tom")})]
    for kind, content, key in [("question", {"question": {"mode": "follows", "query": "q1"}}, "questions"),
                               ("instruction", command("require", "submit_required", ["q1"]), "commands")]:
        document = {"units": premises + [unit("u2", 1, kind, content)],
                    "queries": [{"id": "q1", "premises": ["u1"], "target": {"ast": target}}]}
        assert core(env, document).meaning_ids["u2"] == elaborate(env, document)[key][0]["meaning_id"]


@pytest.mark.parametrize("facts,mode,token,wire", [
    ([U("reviewed", "atlas"), ["not", U("reviewed", "beacon")]], "which_all", ("atlas",), {"all": ["atlas"]}),
    ([["not", U("reviewed", "atlas")], ["not", U("reviewed", "beacon")]], "which_all", (), {"all": []}),
    ([U("reviewed", "atlas"), U("reviewed", "beacon")], "which_all", ("atlas", "beacon"),
     {"all": ["atlas", "beacon"]}),
    ([U("reviewed", "atlas"), ["not", U("reviewed", "beacon")]], "which_one", "atlas", {"one": "atlas"}),
    ([U("reviewed", "atlas")], "polar", "yes", "yes"),
    ([["not", U("reviewed", "atlas")]], "polar", "no", "no")])
def test_python_answer_certificates_replay_in_lean(lean, facts, mode, token, wire):
    # Regression: Python folded F(S) of a complete-list answer as one mixed conjunction, so its
    # certificate's conclusion identity differed from Lean's two conjunctions and replayed only locally.
    from ve.ast import And
    from ve.entailment import prove_entailment
    env = F0()
    asked = polar(U("reviewed", "atlas")) if mode == "polar" else which(mode)
    document = {"units": [*(unit(f"a{i}", i, "asserted", {"ast": f}) for i, f in enumerate(facts)),
                          unit("q", len(facts), "question", asked)]}
    py = core(env, document)
    q = py.questions[0]
    proof = prove_entailment(py.env, py._caller_premises(), And(py.presupposition(q), py.correct(q, token)))
    assert proof.status == "Found"
    assert py.check_answer_certificate(q, token, proof.certificate)["status"] == "supported"
    line = run1({"id": "portable", "kind": "speech-answer", "environment": env, "document": document,
                 "question": "q", "answer": wire, "evidence": {"certificate": proof.certificate}})
    assert line.get("answer", line).startswith("supported "), line


def test_reused_query_is_regenerated_at_every_consumer(lean):
    # Regression: Python compared a reused query only at its earliest consumer and accepted a
    # later consumer whose earlier assertions differ; Lean rejects it. Orphan records also agree.
    env = F0()
    ask = {"question": {"mode": "follows", "query": "q1"}}
    task = command("require", "submit_required", ["q1"])
    fact = unit("p", 1, "asserted", {"ast": U("reviewed", "atlas")})
    query = [{"id": "q1", "premises": [], "target": {"ast": ["top"]}}]
    for first, later in [(ask, ask), (ask, task), (task, ask)]:
        kinds = ["question" if "question" in c else "instruction" for c in (first, later)]
        document = {"units": [unit("u0", 0, kinds[0], first), fact, unit("u2", 2, kinds[1], later)],
                    "queries": query}
        with pytest.raises(VEError, match="QueryMismatch: u2"):
            core(env, document)
        assert run1({"id": "r", "kind": "speech-elaborate", "environment": env,
                     "document": document})["error"] == "QueryMismatch: u2"
    # Consumers with the same earlier assertions share the record in both checkers.
    same = {"units": [unit("u0", 0, "question", ask), unit("u2", 2, "question", ask),
                      unit("p", 3, "asserted", {"ast": U("reviewed", "atlas")})], "queries": query}
    assert len(core(env, same).questions) == len(elaborate(env, same)["questions"]) == 2
    orphan = {"units": [fact], "queries": query}
    with pytest.raises(VEError, match="QueryMismatch: q1"):
        core(env, orphan)
    assert run1({"id": "o", "kind": "speech-elaborate", "environment": env,
                 "document": orphan})["error"] == "QueryMismatch: q1"


def test_document_admission_stays_closed_until_source_wrapper_is_proved(lean):
    case = {"id": "closed", "kind": "admission", "environment": F0(),
            "document": {"units": [unit("u1", 0, "instruction",
                                        command("require", "click_required", ["check"]))]}}
    assert run1(case)["error"] == (
        "UnsupportedProfile: case kind admission is not available on the speech-acts route")
