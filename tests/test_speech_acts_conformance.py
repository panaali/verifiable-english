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
    return SpeechDocument(Environment(env), document["units"], document.get("queries", []),
                          reading_sets=document.get("reading_sets", []))


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


def reading_set(uid, version, status, kind="asserted", content=None):
    reading = {"id": "r", "kind": kind, "meaning_id": "candidate", "content": content,
               "admission": {"who": "author", "why": "reproducer", "distinguishing_models": {}}}
    return {"id": "rs", "unit": uid, "version": version, "status": status, "readings": [reading],
            **({"signature": "author"} if status == "authored" else {})}


def agree(env, document):
    """Python and Lean regenerate the same premises, active commands and dormant units."""
    py, le = core(env, document), elaborate(env, document)
    assert [_to_data(f) for f in py.premises()] == le["premises"]
    assert [c.unit for c in py.commands if c.active] == [c["unit"] for c in le["commands"]]
    assert [c.unit for c in py.commands if not c.active] == le["dormant"]
    return py, le


def test_pending_assertions_and_norms_supply_no_premise(lean):
    # Regression: Python kept an asserted or norm unit active while its reading set was open,
    # so a pending reading's rejected alternative still answered questions.
    env = F0()
    fact = unit("a", 0, "asserted", {"ast": U("reviewed", "atlas")})
    asked = unit("q", 1, "question", polar(U("reviewed", "atlas")))
    negative = ["not", U("reviewed", "atlas")]
    pending = {"units": [fact, asked], "reading_sets": [reading_set("a", 1, "open", content=negative)]}
    py, le = agree(env, pending)
    assert py.asserted == [] and le["premises"] == elaborate(env, {"units": [asked]})["premises"]
    from ve.ast import And
    from ve.entailment import prove_entailment
    q = py.questions[0]
    assert prove_entailment(py.env, py._caller_premises(), And(py.presupposition(q), py.correct(q, "yes")),
                            max_steps=2000).status != "Found"
    norm = {"norm": {"name": "n1", "predicate": "click_required", "sign": True, "guard": ["top"],
                     "unless": [], "over": []}}
    norm_doc = {"units": [unit("n", 0, "norm", norm)],
                "reading_sets": [reading_set("n", 1, "open", "norm", norm)]}
    py, le = agree(env, norm_doc)
    assert py.policy.rules == () or list(py.policy.rules) == []
    assert agree(env, {"units": [unit("n", 0, "norm", norm)]})[0].policy.rules


@pytest.mark.parametrize("versions,active", [
    ([("authored", 1)], True), ([("open", 1)], False),
    ([("open", 1), ("authored", 2)], True), ([("authored", 1), ("open", 2)], False),
    ([("authored", 2), ("open", 1)], True)])
def test_latest_reading_version_decides_command_activeness(lean, versions, active):
    # Regression: Python kept a command with an authored latest version dormant, and Lean let a
    # historical open version suppress a resolved command.
    env = F0()
    click = command("require", "click_required", ["check"])
    document = {"units": [unit("u", 0, "instruction", click)],
                "reading_sets": [reading_set("u", v, s, "instruction", click) for s, v in versions]}
    py, le = agree(env, document)
    assert py.commands[0].active is active and len(le["commands"]) == int(active)


def test_authored_singleton_choice_is_the_units_meaning(lean):
    # Regression: an authored singleton assertion (1.5) was rejected by Python and dropped by Lean.
    env = F0()
    for content in (U("reviewed", "atlas"), {"ast": U("reviewed", "atlas")}):
        document = {"units": [unit("a", 0, "asserted")],
                    "reading_sets": [reading_set("a", 1, "authored", content=content)]}
        py, le = agree(env, document)
        assert le["premises"][-1] == U("reviewed", "atlas") and py.asserted[0][0] == "a"
    # The choice replaces the unit's own content: an authored forbid on a require unit.
    forbid = command("forbid", "click_permitted", ["check"])
    document = {"units": [unit("u", 0, "instruction", command("require", "click_required", ["check"]))],
                "reading_sets": [reading_set("u", 1, "authored", "instruction", forbid)]}
    py, le = agree(env, document)
    assert py.commands[0].force == "forbid" and le["commands"][0]["force"] == "forbid"
    # A content-less asserted unit needs a reading set, and unformalised content is rejected, in both.
    for bad, error in [({"units": [unit("a", 0, "asserted")]}, "asserted unit needs content or a reading set"),
                       ({"units": [unit("a", 0, "asserted", {"ast": U("reviewed", "atlas")},
                                        meaning={"unformalised": "vague"})]},
                        "unformalised unit cannot assert content")]:
        with pytest.raises(VEError, match=error):
            core(env, bad)
        assert run1({"id": "b", "kind": "speech-elaborate", "environment": env, "document": bad})["error"] == error


def test_only_a_signed_version_is_a_choice(lean):
    # Regression: an authored assertion without its `signature` became a premise in both cores,
    # though W2's loader rejects it; open versions carrying a signature, version 0 and sets for
    # no unit of the document were likewise accepted by the cores alone.
    env = F0()
    signed = reading_set("a", 1, "authored", content=U("reviewed", "atlas"))
    assert agree(env, {"units": [unit("a", 0, "asserted")], "reading_sets": [signed]})[0].asserted
    unsigned = {k: v for k, v in signed.items() if k != "signature"}
    click = command("require", "click_required", ["check"])
    for units, sets, error in [
            ([unit("a", 0, "asserted")], [unsigned], "authored reading needs one signed choice"),
            ([unit("a", 0, "asserted")], [{**signed, "signature": ""}], "authored reading needs one signed choice"),
            ([unit("a", 0, "asserted")], [{**signed, "signature": 7}], "authored reading needs one signed choice"),
            ([unit("u", 0, "instruction", click)], [{**reading_set("u", 1, "authored", "instruction", click),
                                                    "signature": ["author"]}], "authored reading needs one signed choice"),
            ([unit("u", 0, "instruction", click)], [{**reading_set("u", 1, "open", "instruction", click),
                                                    "signature": "author"}],
             "open reading set cannot have an author signature"),
            ([unit("a", 0, "asserted")], [{**signed, "version": 0}], "invalid or duplicate reading set version"),
            ([unit("a", 0, "asserted", {"ast": U("reviewed", "atlas")})],
             [reading_set("ghost", 1, "open", content=U("reviewed", "atlas"))], "invalid reading set unit or status")]:
        document = {"units": units, "reading_sets": sets}
        with pytest.raises(VEError, match=error):
            core(env, document)
        assert run1({"id": "s", "kind": "speech-elaborate", "environment": env, "document": document})["error"] == error


def test_combine_keeps_pending_commands_dormant(lean):
    # Regression: combine() rebuilt the document without its reading sets or queries and
    # reactivated a pending command.
    from ve.speech_acts import combine
    env = F0()
    click = command("require", "click_required", ["check"])
    first = core(env, {"units": [unit("u", 0, "instruction", click)],
                       "reading_sets": [reading_set("u", 1, "open", "instruction", click)]})
    second = core(env, {"units": [unit("p", 1, "asserted", {"ast": U("cat", "tom")}),
                                  unit("f", 2, "question", {"question": {"mode": "follows", "query": "q1"}})],
                        "queries": [{"id": "q1", "premises": ["p"], "target": {"ast": U("cat", "tom")}}]})
    both = combine(first, second)
    assert not both.commands[0].active and both.policy.rules == first.policy.rules
    assert both.queries["q1"].premises == ("p",)


def test_authored_bindings_are_bound_into_every_identity(lean):
    # Regression: binding "you" to alice or to bob changed the demand but kept the environment
    # id and the command meaning id in both checkers, so certificates and ids crossed scopes.
    env = F0(addressee=None)
    env["vocabulary"]["constants"]["bob"] = {"sort": "user", "description": "bob"}
    click = unit("u1", 1, "instruction", command("require", "click_required", ["check"]))
    results = {}
    for who in ("alice", "bob"):
        document = {"units": [unit("b", 0, "binding", {"binding": {"you": who}}), click]}
        py, le = core(env, document), elaborate(env, document)
        assert py.env.environment_id == le["environment_id"]
        assert py.meaning_ids["u1"] == le["commands"][0]["meaning_id"]
        assert py.meaning_ids["b"]
        results[who] = (le["environment_id"], le["commands"][0]["meaning_id"])
    assert results["alice"][0] != results["bob"][0] and results["alice"][1] != results["bob"][1]
    # A binding that supplies an entry means what the block declaring it means.
    declared = F0()
    declared["vocabulary"]["constants"]["bob"] = {"sort": "user", "description": "bob"}
    same = elaborate(declared, {"units": [click]})
    assert (same["environment_id"], same["commands"][0]["meaning_id"]) == results["alice"]
    assert core(declared, {"units": [click]}).meaning_ids["u1"] == results["alice"][1]
    # A certificate proved under bob's scope is stale under alice's.
    fact = unit("a", 2, "asserted", {"ast": U("reviewed", "atlas")})
    asked = unit("q", 3, "question", polar(U("reviewed", "atlas")))
    from ve.ast import And
    from ve.entailment import prove_entailment
    bob = core(env, {"units": [unit("b", 0, "binding", {"binding": {"you": "bob"}}), click, fact, asked]})
    q = bob.questions[0]
    proof = prove_entailment(bob.env, bob._caller_premises(), And(bob.presupposition(q), bob.correct(q, "yes")))
    alice_doc = {"units": [unit("b", 0, "binding", {"binding": {"you": "alice"}}), click, fact, asked]}
    with pytest.raises(VEError, match="AnswerMismatch: q"):
        core(env, alice_doc).check_answer_certificate(core(env, alice_doc).questions[0], "yes", proof.certificate)
    assert run1({"id": "s", "kind": "speech-answer", "environment": env, "document": alice_doc, "question": "q",
                 "answer": "yes", "evidence": {"certificate": proof.certificate}})["error"] == \
        "certificate is stale or bound to different inputs"
    # A phrase binding is bound likewise, and an empty definite map is the absent one in both checkers.
    phrase = {"units": [unit("b", 0, "binding", {"binding": {"phrase": "the check", "constant": "check"}})]}
    assert core(F0(), phrase).env.environment_id == elaborate(F0(), phrase)["environment_id"] != \
        elaborate(F0(), {"units": []})["environment_id"]
    empty = F0(definites={})
    empty["speech_acts"]["definites"] = {}
    assert Environment(empty).environment_id == elaborate(empty, {"units": []})["environment_id"] == \
        elaborate(F0(definites={}), {"units": []})["environment_id"]


def test_every_certificate_line_carries_premise_status_and_vacuity(lean):
    # Regression: contradictory premises certified both polar answers in Python with no premise
    # status, and Lean's `follows` line omitted the status of Π_q.
    from ve.ast import And
    from ve.entailment import prove_entailment
    env = F0()
    facts = [unit("p", 0, "asserted", {"ast": U("reviewed", "atlas")}),
             unit("n", 1, "asserted", {"ast": ["not", U("reviewed", "atlas")]})]
    document = {"units": facts + [unit("q", 2, "question", polar(U("reviewed", "atlas")))]}
    py = core(env, document)
    q = py.questions[0]
    for token in ("yes", "no"):
        proof = prove_entailment(py.env, py._caller_premises(), And(py.presupposition(q), py.correct(q, token)))
        line = py.check_answer_certificate(q, token, proof.certificate)
        assert (line["premises"]["status"], line["vacuous"]) == ("INCONSISTENT", "yes")
        lean_line = run1({"id": "v", "kind": "speech-answer", "environment": env, "document": document,
                          "question": "q", "answer": token, "evidence": {"certificate": proof.certificate},
                          "premise_status": {"inconsistent": line["premises"]["certificate"]}})["answer"]
        assert lean_line == f"supported {token} (certificate; premises: INCONSISTENT (certificate); vacuous: yes)"
    follows = {"units": facts + [unit("f", 2, "question", {"question": {"mode": "follows", "query": "q1"}})],
               "queries": [{"id": "q1", "premises": ["p", "n"], "target": {"ast": U("reviewed", "beacon")}}]}
    py = core(env, follows)
    proof = prove_entailment(py.env, py._caller_premises("q1"), py.queries["q1"].target)
    line = py.check_consequence_certificate("q1", proof.certificate)
    assert (line["status"], line["premises"]["status"], line["vacuous"]) == ("follows", "INCONSISTENT", "yes")
    judgment = run1({"id": "f", "kind": "speech-consequence", "environment": env, "document": follows, "query": "q1",
                     "certificate": proof.certificate,
                     "premise_status": {"inconsistent": line["premises"]["certificate"]}})["judgment"]
    assert judgment == "follows (certificate; premises: INCONSISTENT (certificate); vacuous: yes)"
    # Consistent premises: a checked model, not vacuous.
    consistent = {"units": facts[:1] + [unit("q", 2, "question", polar(U("reviewed", "atlas")))]}
    py = core(env, consistent)
    q = py.questions[0]
    proof = prove_entailment(py.env, py._caller_premises(), And(py.presupposition(q), py.correct(q, "yes")))
    line = py.check_answer_certificate(q, "yes", proof.certificate)
    assert (line["premises"]["status"], line["vacuous"]) == ("model", "no")


def test_document_admission_stays_closed_until_source_wrapper_is_proved(lean):
    case = {"id": "closed", "kind": "admission", "environment": F0(),
            "document": {"units": [unit("u1", 0, "instruction",
                                        command("require", "click_required", ["check"]))]}}
    assert run1(case)["error"] == (
        "UnsupportedProfile: case kind admission is not available on the speech-acts route")
