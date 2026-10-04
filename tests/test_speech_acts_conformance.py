"""Shared section-9 speech-act fixtures across Python, Lean, and Rust FOL evaluation.

Rust evaluates the regenerated formulas in a complete model. It has no speech
admission route, so these checks do not enable trusted document admission.
"""
from __future__ import annotations

import copy
import json
import re
import shutil
import subprocess
import sys

import pytest

from tools import rust_build
from ve.ast import _to_data
from ve.environment import Environment
from ve.errors import VEError
from ve.speech_acts import SpeechDocument
from ve.speech_document import SpeechSource, load_speech_document
from ve.speech_english import parse_speech

from test_speech_acts_lean import F0, MODEL, ROOT, U, command, elaborate, lean, model, polar, run, run1, unit, which


@pytest.fixture(scope="module")
def rust():
    executable = ROOT / "rust/target/debug/ve"
    if not executable.exists():
        cargo = shutil.which("cargo")
        if cargo is None:
            pytest.skip("cargo is required for speech-act FOL conformance")
        built = subprocess.run([cargo, "build", "-p", "ve"], cwd=ROOT / "rust", env=rust_build.cargo_env(),
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


def test_pending_bindings_supply_no_scope_entry(lean):
    # Regression: an open binding of "you" to bob still bound the active command's addressee in both
    # cores, although its sole candidate binds alice; a pending binding is dormant like a pending command.
    env = F0(addressee=None)
    env["vocabulary"]["constants"]["bob"] = {"sort": "user", "description": "bob"}
    click = unit("u1", 1, "instruction", command("require", "click_required", ["check"]))
    bob = unit("b", 0, "binding", {"binding": {"you": "bob"}})
    to_alice = reading_set("b", 1, "open", "binding", {"binding": {"you": "alice"}})
    leaked = {"units": [bob, click], "reading_sets": [to_alice]}
    with pytest.raises(VEError, match="UnboundSlot: you"):
        core(env, leaked)
    assert run1({"id": "p", "kind": "speech-elaborate", "environment": env, "document": leaked})["error"] == \
        "UnboundSlot: you"
    # Without the active command the pending binding leaves the scope, and so every identity, unchanged.
    alone = {"units": [bob], "reading_sets": [to_alice]}
    py, le = core(env, alone), elaborate(env, alone)
    assert "addressee" not in py.scope and "addressee" not in le["scope"]
    assert py.env.environment_id == le["environment_id"] == elaborate(env, {"units": []})["environment_id"]
    # A pending binding neither conflicts with nor duplicates the block or an authored binding.
    for environment, units in [(F0(), [bob, click]),
                               (env, [bob, click, unit("a", 2, "binding", {"binding": {"you": "alice"}})])]:
        environment["vocabulary"]["constants"]["bob"] = {"sort": "user", "description": "bob"}
        document = {"units": units, "reading_sets": [to_alice]}
        py, le = core(environment, document), elaborate(environment, document)
        assert py.scope["addressee"]["constant"] == le["scope"]["addressee"]["constant"] == "alice"
        assert py.policy.rules[0].to_dict()["norm"] == le["commands"][0]["demand"]
        assert py.env.environment_id == le["environment_id"]
    # It keeps the single-binding checks of the unit it would supply.
    for binding, error in [({"you": "carol"}, "UnknownSymbol: carol"),
                           ({"phrase": "bad phrase", "constant": "check"}, "InvalidInput: invalid binding fields for b"),
                           ({"phrase": "the check", "constant": "carol"}, "UnknownSymbol: carol")]:
        document = {"units": [unit("b", 0, "binding", {"binding": binding})], "reading_sets": [to_alice]}
        with pytest.raises(VEError, match=error):
            core(env, document)
        assert run1({"id": "p", "kind": "speech-elaborate", "environment": env, "document": document})["error"] == error


def test_every_candidate_is_checked_as_its_unit_would_be(lean):
    # Regression: a follows-question candidate naming no query record and a binding candidate with a
    # malformed phrase were counted as elaborated (class R) by Python; Lean checked no open candidate
    # at all and accepted `{"command": {}}`.
    env = F0()
    asked = unit("u", 0, "question", polar(U("reviewed", "atlas")))
    follows = {"question": {"mode": "follows", "query": "q1"}}
    fact = unit("p", 0, "asserted", {"ast": U("reviewed", "atlas")})
    query = [{"id": "q1", "premises": [], "target": {"ast": U("reviewed", "atlas")}}]
    cases = [
        ({"units": [asked], "reading_sets": [reading_set("u", 1, "open", "question", follows)]}, "QueryMismatch: u"),
        ({"units": [fact, {**asked, "span": [1, 2]}], "queries": query,
          "reading_sets": [reading_set("u", 1, "open", "question", follows)]}, "QueryMismatch: u"),
        ({"units": [asked], "reading_sets": [reading_set("u", 1, "open", "instruction",
                                                         command("require", "submit_required", ["q1"]))]},
         "QueryMismatch: u"),
        ({"units": [asked], "reading_sets": [reading_set("u", 1, "open", "question",
                                                         {"question": {"mode": "follows", "query": 1}})]},
         "InvalidInput: invalid question fields for u"),
        ({"units": [asked], "reading_sets": [reading_set("u", 1, "open", "question", {"question": {"mode": "follows"}})]},
         "InvalidInput: invalid question fields for u"),
        ({"units": [asked], "reading_sets": [reading_set("u", 1, "open", "binding",
                                                         {"binding": {"phrase": "bad phrase", "constant": "check"}})]},
         "InvalidInput: invalid binding fields for u"),
        ({"units": [asked], "reading_sets": [reading_set("u", 1, "open", "binding", {"binding": {"you": "carol"}})]},
         "UnknownSymbol: carol"),
        ({"units": [asked], "reading_sets": [reading_set("u", 1, "open", "instruction", {"command": {}})]},
         "InvalidInput: invalid command fields for u"),
        ({"units": [asked], "reading_sets": [reading_set("u", 1, "open", "instruction",
                                                         command("require", "click_required", ["atlas"]))]},
         "TypeMismatch: command args for u"),
        ({"units": [asked], "reading_sets": [reading_set("u", 1, "open", "instruction",
                                                         command("require", "click_permitted", ["check"]))]},
         "MissingObligationRole: {0} click {1}"),
        ({"units": [asked], "reading_sets": [reading_set("u", 1, "open", "question", U("reviewed", "atlas"))]},
         "invalid speech reading content"),
        ({"units": [asked], "reading_sets": [reading_set("u", 1, "open", "asserted", polar(U("reviewed", "atlas")))]},
         "invalid speech reading content"),
        ({"units": [asked], "reading_sets": [{**reading_set("u", 1, "open", "question", polar(U("reviewed", "atlas"))),
                                              "readings": []}]}, "reading sets hold 1 to 64 readings"),
        ({"units": [asked], "reading_sets": [{**reading_set("u", 1, "open"), "readings": [{"id": "r", "kind": "asserted"}]}]},
         "invalid reading")]
    for document, error in cases:
        with pytest.raises(VEError, match=re.escape(error)):
            core(env, document)
        assert run1({"id": "c", "kind": "speech-elaborate", "environment": env, "document": document})["error"] == error
    # A candidate that asks about a regenerated record is its consumer; well-formed candidates are accepted.
    for candidate, kind, records in [(follows, "question", query),
                                     (command("require", "submit_required", ["q1"]), "instruction", query),
                                     ({"binding": {"phrase": "the check", "constant": "check"}}, "binding", []),
                                     (["not", U("reviewed", "atlas")], "asserted", [])]:
        document = {"units": [asked], "queries": records,
                    "reading_sets": [reading_set("u", 1, "open", kind, candidate)]}
        assert core(env, document) and elaborate(env, document)


def test_cli_and_fences_read_the_effective_scope(lean, tmp_path):
    # Regression: `python -m ve speech-acts` reported the embedded environment's id and legend, so
    # alice- and bob-bound documents shared one reported id and neither legend named the addressee;
    # fences were likewise parsed under the block alone, so a bound phrase could not be written.
    env = F0(addressee=None)
    env["vocabulary"]["constants"]["bob"] = {"sort": "user", "description": "bob"}
    reported = {}
    for who in ("alice", "bob"):
        lines = [f"In this task, you are {who}.\n", "In this task, the button is check.\n", "Click the button.\n"]
        positions = [0]
        for line in lines:
            positions.append(positions[-1] + len(line.encode()))
        units = [{**unit("y", 0, "binding", {"binding": {"you": who}}), "span": positions[0:2]},
                 {**unit("p", 0, "binding", {"binding": {"phrase": "the button", "constant": "check"}}),
                  "span": positions[1:3]},
                 {**unit("u1", 0, "instruction", {"fence": "u1"}), "span": positions[2:4], "surface": "english"}]
        path = tmp_path / f"{who}.ve.md"
        path.write_text("---\n" + json.dumps({"format": "ve-document@2", "environment": env, "units": units}) +
                        "\n---\n" + "".join(lines) + "```ve u1\nClick the button.\n```\n")
        source = load_speech_document(path)
        inspected = subprocess.run([sys.executable, "-m", "ve", "speech-acts", str(path)],
                                   capture_output=True, text=True, timeout=60)
        assert inspected.returncode == 0, inspected.stdout + inspected.stderr
        report = json.loads(inspected.stdout)
        le = elaborate(env, {"units": [*units[:2], unit("u1", 0, "instruction", command("require", "click_required", ["check"])) | {"span": positions[2:4]}]})
        assert report["environment_id"] == source.document.env.environment_id == le["environment_id"]
        assert report["legend"].splitlines()[:len(le["legend"])] == le["legend"]
        assert le["legend"][:3] == ["This document is task t1.", f"In this task, you are {who}.",
                                    "In this task, the button is check."]
        assert report["rules"][0]["norm"] == le["commands"][0]["demand"]
        reported[who] = report["environment_id"]
    assert reported["alice"] != reported["bob"]


def test_fenced_and_unfenced_sources_agree_on_the_effective_scope(lean, tmp_path):
    # Regression: effective_scope() built a binding-only document without the query records, so an open
    # binding whose candidate asks about the valid query q1 made the fenced form of a later "Click check."
    # raise `QueryMismatch: b`, while the unfenced source and Lean accepted the document.  The scope is now
    # the document's own merge, so a record whose premises are asserted units outside the bindings (p here)
    # is checked only in its context, by the document.
    env = F0()
    env["vocabulary"]["predicates"]["reviewed"]["verbalisation"] = "{0} is reviewed"
    follows = {"question": {"mode": "follows", "query": "q1"}}
    lines = ["Atlas is reviewed.\n", "In this task, you are alice.\n", "Click check.\n"]
    positions = [0]
    for line in lines:
        positions.append(positions[-1] + len(line.encode()))
    click = command("require", "click_required", ["check"])
    for premises in ([], ["p"]):
        fact = [{**unit("p", 0, "asserted", {"ast": U("reviewed", "atlas")}), "span": positions[0:2]}] if premises else []
        head = lines[:1] if premises else []
        offset = 0 if premises else positions[1]
        shift = lambda span: [span[0] - offset, span[1] - offset]  # noqa: E731
        units = [*fact, {**unit("b", 0, "binding", {"binding": {"you": "alice"}}), "span": shift(positions[1:3])},
                 {**unit("u1", 0, "instruction", click), "span": shift(positions[2:4])}]
        meta = {"format": "ve-document@2", "environment": env, "units": units,
                "queries": [{"id": "q1", "premises": premises, "target": {"ast": U("reviewed", "atlas")}}],
                "reading_sets": [reading_set("b", 1, "open", "question", follows)]}
        body = "".join(head + lines[1:])
        plain = tmp_path / f"plain{len(premises)}.ve.md"
        plain.write_text("---\n" + json.dumps(meta) + "\n---\n" + body)
        fenced_units = copy.deepcopy(units)
        fenced_units[-1] = {**fenced_units[-1], "content": {"fence": "u1"}, "surface": "english"}
        fenced = tmp_path / f"fenced{len(premises)}.ve.md"
        fenced.write_text("---\n" + json.dumps({**meta, "units": fenced_units}) + "\n---\n" + body +
                          "```ve u1\nClick check.\n```\n")
        a, b = load_speech_document(plain).document, load_speech_document(fenced).document
        le = elaborate(env, {k: meta[k] for k in ("units", "queries", "reading_sets")})
        assert a.scope == b.scope and a.env.environment_id == b.env.environment_id == le["environment_id"]
        assert [r.to_dict() for r in a.policy.rules] == [r.to_dict() for r in b.policy.rules]
        assert a.policy.rules[0].to_dict()["norm"] == le["commands"][0]["demand"]
    # A binding conflict is the document's, in either form.
    conflict = {**meta, "units": [*units[:-2], {**units[-2], "content": {"binding": {"you": "bob"}}}, units[-1]],
                "reading_sets": []}
    conflict["environment"] = copy.deepcopy(env)
    conflict["environment"]["vocabulary"]["constants"]["bob"] = {"sort": "user", "description": "bob"}
    conflict["queries"] = []
    for fence in (False, True):
        path = tmp_path / f"conflict{fence}.ve.md"
        chosen = copy.deepcopy(conflict)
        if fence:
            chosen["units"][-1] = {**chosen["units"][-1], "content": {"fence": "u1"}, "surface": "english"}
        path.write_text("---\n" + json.dumps(chosen) + "\n---\n" + body + ("```ve u1\nClick check.\n```\n" if fence else ""))
        with pytest.raises(VEError, match="BindingConflict: you"):
            load_speech_document(path)


def _diagnostic(error):
    """A Python diagnostic as Lean renders it (norms.md 11.1): `<code>: <message>` unless the message carries it."""
    return str(error) if type(error) is VEError or str(error).startswith(f"{error.code}: ") else f"{error.code}: {error}"


def _reference_cases():
    """Every reference-bearing field of a speech document, dangling (a name nothing declares) and mistyped (not a
    name), under a unit, a quoted unit or a reading candidate, with the one diagnostic both checkers give."""
    asked = unit("u", 0, "question", polar(U("reviewed", "atlas")))
    fact = unit("p", 0, "asserted", {"ast": U("reviewed", "atlas")})
    follows = unit("f", 1, "question", {"question": {"mode": "follows", "query": "q1"}})
    ambiguous = unit("x", 1, "asserted")
    rs_x = reading_set("x", 1, "open", "asserted", U("reviewed", "atlas"))
    quoted = lambda k: ["attributed", "bob", "says", k]  # noqa: E731
    reading = lambda s, v=1: {"question": {"mode": "reading", "set": s, "version": v}}  # noqa: E731
    which_q = lambda sort="service", domain=("atlas", "beacon"): {"question": {  # noqa: E731
        "mode": "which_all", "sort": sort, "domain": list(domain), "body": ["unary", "reviewed", ["var", 0]]}}
    click = lambda args=("check",), act="click_required", **extra: {  # noqa: E731
        "command": {"force": "require", "act": act, "args": list(args), **extra}}
    query = lambda **fields: {"id": "q1", "premises": ["p"], "target": {"ast": U("reviewed", "atlas")}, **fields}  # noqa: E731
    fields = lambda u: f"InvalidInput: invalid question fields for {u}"  # noqa: E731
    command_fields = "InvalidInput: invalid command fields for u"
    unknown = "UnknownSymbol: Unknown constant 'nope'"
    term, formula = "invalid indexed term", "invalid indexed formula"
    deep = ["top"]
    for _ in range(64):
        deep = ["not", deep]
    norm_with = lambda **fields: {"norm": {"name": "n1", "predicate": "click_required", "sign": True,  # noqa: E731
                                           "guard": ["top"], "unless": [], "over": [], **fields}}
    # (name, units or content placement, error)
    placed = [  # contents placed under a unit, a quoted unit and a reading candidate
        ("act dangling", "instruction", click(act="nope"), "UnknownSymbol: regulated predicate nope"),
        ("act mistyped", "instruction", click(act=7), command_fields),
        ("arg dangling", "instruction", click(["nope"]), "UnknownSymbol: nope"),
        ("arg mistyped", "instruction", click([7]), command_fields),
        ("arg of another sort", "instruction", click(["atlas"]), "TypeMismatch: command args for u"),
        ("guard dangling", "instruction", click(guard=U("reviewed", "nope")), unknown),
        ("body dangling", "question", polar(U("reviewed", "nope")), unknown),
        ("sort dangling", "question", which_q(sort="nope"), "UnknownSymbol: sort nope"),
        ("sort mistyped", "question", which_q(sort=7), fields("u")),
        ("alternative dangling", "question", which_q(domain=("atlas", "nope")), "UnknownAlternative: u, nope"),
        ("alternative mistyped", "question", which_q(domain=("atlas", 7)), fields("u")),
        ("query dangling", "question", {"question": {"mode": "follows", "query": "nope"}}, "QueryMismatch: u"),
        ("query mistyped", "question", {"question": {"mode": "follows", "query": 7}}, fields("u")),
        ("reading set dangling", "question", reading("missing"), fields("u")),
        ("reading version dangling", "question", reading("rs", 2), fields("u")),
        ("reading set mistyped", "question", reading(7), fields("u")),
        ("reading set missing", "question", {"question": {"mode": "reading", "version": 1}}, fields("u")),
        ("formula dangling", "asserted", {"ast": U("reviewed", "nope")}, unknown),
        # A formula's own references (predicate, constant, binder sort) that are not names, and every other
        # structure outside the route's P0 form, are the Lean route's P0 decoder error in both checkers.
        ("guard constant mistyped", "instruction", click(guard=["unary", "disabled", ["const", 7]]), term),
        ("guard predicate mistyped", "instruction", click(guard=["unary", [], ["const", "check"]]), formula),
        ("body constant mistyped", "question", polar(["unary", "reviewed", ["const", 7]]), term),
        ("body constant a list", "question", polar(["unary", "reviewed", ["const", []]]), term),
        ("body predicate mistyped", "question", polar(["unary", 7, ["const", "atlas"]]), formula),
        ("body binder sort mistyped", "question", polar(["exists", 7, ["top"]]), formula),
        ("which body variable mistyped", "question",
         {"question": {**which_q()["question"], "body": ["unary", "reviewed", ["var", "0"]]}}, "Natural number expected"),
        ("which body before its sort", "question",
         {"question": {**which_q(sort=7)["question"], "body": ["unary", "reviewed", ["const", 7]]}}, term),
        ("formula constant mistyped", "asserted", {"ast": ["unary", "reviewed", ["const", 7]]}, term),
        ("formula term not an array", "asserted", {"ast": ["unary", "reviewed", "atlas"]}, "array expected"),
        ("formula of another profile", "asserted", {"ast": ["lt", ["num", "1"], ["num", "2"]]}, formula),
        ("formula too deep", "asserted", {"ast": deep}, "ResourceLimit: formula depth exceeds 64"),
        ("norm guard mistyped", "norm", norm_with(guard=["unary", "disabled", ["const", 7]]), term),
        ("norm carve-out mistyped", "norm", norm_with(unless=[["unary", 7, ["const", "check"]]]), formula)]
    cases = []
    for name, kind, content, error in placed:
        extra = {"units": [ambiguous], "reading_sets": [{**rs_x, "id": "rs"}]}
        meaning = {"open": ["intended-reading.u"]} if content.get("question", {}).get("mode") == "reading" else "specified"
        cases.append((f"unit {name}", {"units": [unit("u", 0, kind, content, meaning), *extra["units"]],
                                       "reading_sets": extra["reading_sets"]}, error))
        cases.append((f"quoted {name}", {"units": [unit("u", 0, quoted(kind), content), *extra["units"]],
                                         "reading_sets": extra["reading_sets"]}, error))
        candidate = content["ast"] if kind == "asserted" else content
        cases.append((f"candidate {name}", {"units": [asked, *extra["units"]],
                                            "reading_sets": [{**rs_x, "id": "rs"},
                                                             {**reading_set("u", 1, "open", kind, candidate), "id": "ru"}]},
                      error))
    for name, binding, error in [("you dangling", {"you": "nope"}, "UnknownSymbol: nope"),
                                 ("you mistyped", {"you": 7}, "InvalidInput: invalid binding fields for b"),
                                 ("phrase constant dangling", {"phrase": "the knob", "constant": "nope"},
                                  "UnknownSymbol: nope"),
                                 ("phrase constant mistyped", {"phrase": "the knob", "constant": 7},
                                  "InvalidInput: invalid binding fields for b"),
                                 ("task mistyped", {"task": 7}, "InvalidInput: invalid binding fields for b"),
                                 ("task not a token", {"task": "a b"}, "InvalidInput: speech_acts block")]:
        cases.append((f"binding {name}", {"units": [unit("b", 0, "binding", {"binding": binding})]}, error))
        cases.append((f"pending binding {name}", {"units": [unit("b", 0, "binding", {"binding": binding})],
                                                  "reading_sets": [reading_set("b", 1, "open", "binding",
                                                                               {"binding": {"you": "alice"}})]}, error))
    for name, record, error in [("premise dangling", query(premises=["nope"]), "QueryMismatch: f"),
                                ("premise mistyped", query(premises=[7]), "InvalidInput: query"),
                                ("premises mistyped", query(premises="p"), "InvalidInput: query"),
                                ("id mistyped", query(id=7), "InvalidInput: query"),
                                ("target dangling", query(target={"ast": U("reviewed", "nope")}), unknown),
                                ("target mistyped", query(target=U("reviewed", "atlas")), "InvalidInput: query"),
                                ("target constant mistyped", query(target={"ast": ["unary", "reviewed", ["const", 7]]}),
                                 term)]:
        cases.append((f"query {name}", {"units": [fact, follows], "queries": [record]}, error))
    cases.append(("query id twice", {"units": [fact, follows], "queries": [query(), query()]},
                  "InvalidInput: duplicate query"))
    # (Lean's frozen JSON parser cannot carry a null candidate, so these sets hold an elaborated one.)
    for name, owner, error in [
            ("dangling", "nope", "invalid reading set unit or status"),
            ("mistyped", 7, "InvalidInput: reading sets on the speech-acts route need their unit, version and status")]:
        cases.append((f"reading set unit {name}",
                      {"units": [fact], "reading_sets": [reading_set(owner, 1, "open", content=U("reviewed", "atlas"))]},
                      error))
    norm = {"norm": {"name": "n1", "predicate": "nope", "sign": True, "guard": ["top"], "unless": [], "over": []}}
    cases.append(("norm predicate dangling", {"units": [unit("n", 0, "norm", norm)]},
                  "UnknownSymbol: regulated predicate nope"))
    over = {"norm": {**norm["norm"], "predicate": "click_required", "over": ["nope"]}}
    cases.append(("norm over dangling", {"units": [unit("n", 0, "norm", over)]}, "UnknownRule: rule nope"))
    return cases


def test_every_reference_is_resolved_and_typed_identically(lean):
    # Directive: every reference is resolved and typed at decode time.  Regression: an open reading-question
    # candidate naming a missing set (or, in Python, a numeric one) was accepted, and further probing found the
    # two checkers disagreeing on dangling or mistyped references elsewhere: Python crashed or said
    # `TypeMismatch` on a mistyped or undeclared command argument, `AlternativeSort` on an undeclared sort and
    # `QueryMismatch` on a malformed query record; Lean checked no quoted question and no open-meaning command,
    # demanded an addressee of a dormant command, gave `BindingConflict` before an undeclared constant and an
    # untyped "ill-typed or unbound conclusion" for an undeclared constant in a guard, an assertion or a target.
    env = F0()
    cases = _reference_cases()
    results = run([{"id": name, "kind": "speech-elaborate", "environment": env, "document": document}
                   for name, document, _ in cases])
    for (name, document, error), result in zip(cases, results, strict=True):
        with pytest.raises(VEError) as raised:
            core(env, copy.deepcopy(document))
        assert (name, _diagnostic(raised.value)) == (name, error)
        assert (name, result.get("error")) == (name, error)
    # The well-formed forms of the same fields are accepted by both, and dormant commands need no addressee.
    click = command("require", "click_required", ["check"])
    x, rs_x = unit("x", 1, "asserted"), {**reading_set("x", 1, "open", "asserted", U("reviewed", "atlas")), "id": "rs"}
    reading = {"question": {"mode": "reading", "set": "rs", "version": 1}}
    for environment, document in [
            (F0(addressee=None), {"units": [unit("u", 0, ["attributed", "bob", "says", "instruction"], click)]}),
            (F0(addressee=None), {"units": [unit("u", 0, "instruction", click)],
                                  "reading_sets": [reading_set("u", 1, "open", "instruction", click)]}),
            (env, {"units": [unit("u", 0, "question", reading, {"open": ["intended-reading.u"]}), x],
                   "reading_sets": [rs_x]}),
            (env, {"units": [unit("u", 0, ["attributed", "bob", "says", "question"], reading), x], "reading_sets": [rs_x]}),
            (env, {"units": [unit("u", 0, "question", polar(U("reviewed", "atlas"))), x],
                   "reading_sets": [rs_x, {**reading_set("u", 1, "authored", "question", reading), "id": "ru"}]}),
            (env, {"units": [unit("p", 0, "asserted", {"ast": U("reviewed", "atlas")}),
                             unit("f", 1, ["attributed", "bob", "says", "question"],
                                  {"question": {"mode": "follows", "query": "q1"}})],
                   "queries": [{"id": "q1", "premises": ["p"], "target": {"ast": U("reviewed", "atlas")}}]})]:
        py, le = core(environment, document), elaborate(environment, document)
        assert [q.unit for q in py.questions] == [q["unit"] for q in le["questions"]]
    # A chosen reading question is asked, meaning its open term (4.6), in both.
    chosen = {"units": [unit("u", 0, "question", polar(U("reviewed", "atlas"))), x],
              "reading_sets": [rs_x, {**reading_set("u", 1, "authored", "question", reading), "id": "ru"}]}
    assert [q.mode for q in core(env, chosen).questions] == [q["mode"] for q in elaborate(env, chosen)["questions"]] \
        == ["reading"]


def test_scope_references_are_names_before_they_are_resolved(lean):
    # Regression: an addressee `sort` or `constant` of `[]` raised an uncaught TypeError in Python while Lean
    # said `InvalidInput: speech_acts block`, and a numeric one gave `UnknownSymbol` in Python.  Every scope
    # reference is a name, with the block's structure and phrase checks, before anything is resolved, in
    # Lean's order (`parseScope`, `checkPhrases`, then `checkSpeech`).
    block = "InvalidInput: speech_acts block"
    many = {f"the knob k{a}{b}": "check" for a in "abc" for b in "abcdefghijklmnopqrstuvwxyz"}
    cases = []
    for field in ("sort", "constant"):
        for bad in ([], {}, 7, True):  # (the frozen JSON parser of the Lean route cannot carry null)
            cases.append((f"addressee {field} {bad!r}", {"addressee": {**F0()["speech_acts"]["addressee"], field: bad}},
                          block))
    for bad in ([], 7, True):
        cases.append((f"definite constant {bad!r}", {"definites": {"the knob": bad}}, block))
    cases += [
        ("addressee without its constant", {"addressee": {"sort": "user"}}, block),
        ("dangling addressee, then a malformed phrase", {"addressee": {"sort": "user", "constant": "nope"},
                                                         "definites": {"knob": "check"}}, block),
        ("dangling addressee, then a mistyped definite", {"addressee": {"sort": "user", "constant": "nope"},
                                                          "definites": {"the knob": 7}}, block),
        ("too many definites, then a malformed phrase", {"definites": {**many, "knob": "check"}}, block),
        ("addressee sort dangling", {"addressee": {"sort": "nope", "constant": "alice"}}, "UnknownSymbol: sort nope"),
        ("addressee constant dangling", {"addressee": {"sort": "user", "constant": "nope"}}, "UnknownSymbol: nope"),
        ("addressee of another sort", {"addressee": {"sort": "service", "constant": "alice"}}, "UnknownSymbol: alice"),
        ("dangling addressee before too many definites", {"addressee": {"sort": "user", "constant": "nope"},
                                                          "definites": many}, "UnknownSymbol: nope"),
        ("too many definites", {"definites": many}, "ResourceLimit: definites"),
        ("definite constant dangling", {"definites": {"the knob": "nope"}}, "UnknownSymbol: nope")]
    envs = []
    for _, fields, _ in cases:
        env = F0()
        env["speech_acts"] = {**env["speech_acts"], **fields}
        envs.append(env)
    results = run([{"id": name, "kind": "speech-elaborate", "environment": env, "document": {"units": []}}
                   for (name, _, _), env in zip(cases, envs)])
    for (name, _, error), env, result in zip(cases, envs, results, strict=True):
        with pytest.raises(VEError) as raised:
            Environment(env)
        assert (name, _diagnostic(raised.value)) == (name, error)
        assert (name, result.get("error")) == (name, error)


def _fenced_pair(tmp_path, name, env, lines, units, fenced, **meta):
    """The source with the given units, and the same source with unit `fenced`'s content an English fence."""
    positions = [0]
    for line in lines:
        positions.append(positions[-1] + len(line.encode()))
    units = [{**u, "span": positions[i:i + 2]} for i, u in enumerate(units)]
    fence_units = [{**u, "content": {"fence": u["id"]}, "surface": "english"} if u["id"] == fenced else u
                   for u in units]
    wording = lines[[u["id"] for u in units].index(fenced)].strip()
    paths = []
    for suffix, us, tail in (("plain", units, ""), ("fenced", fence_units, f"```ve {fenced}\n{wording}\n```\n")):
        path = tmp_path / f"{name}-{suffix}.ve.md"
        path.write_text("---\n" + json.dumps({"format": "ve-document@2", "environment": env, "units": us, **meta}) +
                        "\n---\n" + "".join(lines) + tail)
        paths.append(path)
    return units, paths


def test_fenced_query_and_reading_consumers_regenerate_their_reference(lean, tmp_path):
    # Regression: "Does it follow from these premises that atlas is reviewed?" with a valid q1 passed unfenced and
    # in Lean, but its English fence raised `InvalidInput: query required`, as did "Prove that ... using these
    # premises." and "Which reading did you mean?": fence parsing received no document context.  A fenced wording
    # that names neither its query nor its reading set is about the one query record regenerated at its unit (1.4)
    # and the set version its derived open term names (4.6), so both forms and Lean agree.
    env = F0()
    env["vocabulary"]["predicates"]["reviewed"]["verbalisation"] = "{0} is reviewed"
    fact = unit("p", 0, "asserted", {"ast": U("reviewed", "atlas")})
    record = {"id": "q1", "premises": ["p"], "target": {"ast": U("reviewed", "atlas")}}
    asks = [("follows", "Does it follow from these premises that atlas is reviewed?\n", "question",
             {"question": {"mode": "follows", "query": "q1"}}, "questions"),
            ("proof", "Prove that atlas is reviewed using these premises.\n", "instruction",
             command("require", "submit_required", ["q1"]), "commands")]
    for name, wording, kind, content, key in asks:
        units, (plain, fenced) = _fenced_pair(tmp_path, name, env, ["Atlas is reviewed.\n", wording],
                                              [fact, unit("f", 0, kind, content)], "f", queries=[record])
        a, b = load_speech_document(plain).document, load_speech_document(fenced).document
        le = elaborate(env, {"units": units, "queries": [record]})
        assert a.meaning_ids["f"] == b.meaning_ids["f"] == le[key][0]["meaning_id"]
        # No record, a stale one, or two regenerated at the unit: the unit's query is not determined.
        for records in ([], [{**record, "premises": []}], [{**record, "target": {"ast": U("reviewed", "beacon")}}],
                        [record, {**record, "id": "q2"}]):
            _, (plain, fenced) = _fenced_pair(tmp_path, name, env, ["Atlas is reviewed.\n", wording],
                                              [fact, unit("f", 0, kind, content)], "f", queries=records)
            with pytest.raises(VEError, match="^QueryMismatch: (f|q2)$"):
                load_speech_document(plain)
            with pytest.raises(VEError, match="^QueryMismatch: f$"):
                load_speech_document(fenced)
    # A premise pending in an open reading set is not among "these premises", in either form.
    pending = reading_set("p", 1, "open", "asserted", U("reviewed", "atlas"))
    pending["readings"][0]["meaning_id"] = _meaning_id(env, U("reviewed", "atlas"))
    for records, ok in (([{**record, "premises": []}], True), ([record], False)):
        _, paths = _fenced_pair(tmp_path, f"pending{ok}", env, ["Atlas is reviewed.\n", asks[0][1]],
                                [fact, unit("f", 0, "question", asks[0][3])], "f", queries=records,
                                reading_sets=[pending])
        for path in paths:
            if ok:
                assert load_speech_document(path).document.questions[0].query == "q1"
            else:
                with pytest.raises(VEError, match="^QueryMismatch: f$"):
                    load_speech_document(path)
    # A reading question: the set version is the one its derived open term names.
    click = command("require", "click_required", ["check"])
    term = {"name": "intended-reading.r", "arguments": ["rs"], "version": 1, "decided_by": "alice",
            "jurisdiction": "t1", "necessary": [], "sufficient": [], "precedents": [],
            "factors": ["necessary: at least one nomination of a candidate of rs at version 1 by alice",
                        "sufficient: exactly one nomination of a candidate of rs at version 1 by alice"]}
    reading = {"question": {"mode": "reading", "set": "rs", "version": 1}}
    sets = [reading_set("x", 1, "open", "instruction", click)]
    units, (plain, fenced) = _fenced_pair(
        tmp_path, "reading", env, ["Click check.\n", "Which reading did you mean?\n"],
        [unit("x", 0, "instruction", click), unit("r", 0, "question", reading, {"open": ["intended-reading.r"]})],
        "r", open_terms=[term], reading_sets=sets)
    a, b = load_speech_document(plain).document, load_speech_document(fenced).document
    le = elaborate(env, {"units": units, "reading_sets": sets})
    assert a.meaning_ids["r"] == b.meaning_ids["r"] == le["questions"][0]["meaning_id"]
    for other in ({"arguments": ["other"]}, {"version": 2}):  # the open term decides; the document then checks it
        _, (_, fenced) = _fenced_pair(
            tmp_path, "reading-term", env, ["Click check.\n", "Which reading did you mean?\n"],
            [unit("x", 0, "instruction", click), unit("r", 0, "question", reading, {"open": ["intended-reading.r"]})],
            "r", open_terms=[{**term, **other}], reading_sets=sets)
        with pytest.raises(VEError, match="^InvalidInput: invalid question fields for r$"):
            load_speech_document(fenced)
    _, (plain, fenced) = _fenced_pair(tmp_path, "reading-specified", env,
                                      ["Click check.\n", "Which reading did you mean?\n"],
                                      [unit("x", 0, "instruction", click), unit("r", 0, "question", reading)],
                                      "r", reading_sets=sets)
    for path in (plain, fenced):
        with pytest.raises(VEError, match="^InvalidInput: invalid question fields for r$"):
            load_speech_document(path)


def _meaning_id(env, ast):
    from ve.ast import formula_from_data
    from ve.identity import meaning_id
    e = Environment(env)
    return meaning_id(e, formula_from_data(e, ast))


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


def test_presupposition_failure_and_compliance_lines_carry_premise_status(lean, tmp_path):
    # Regression: over contradictory premises Lean's `PRESUPPOSITION-FAILED (certificate for ¬H)` line
    # carried no premise status or vacuity even with inconsistency evidence supplied, and Python's
    # proof-task compliance line dropped the status its certificate check computed.
    from ve.ast import Not
    from ve.entailment import prove_entailment
    env = F0()
    facts = [unit("p", 0, "asserted", {"ast": U("reviewed", "atlas")}),
             unit("n", 1, "asserted", {"ast": ["not", U("reviewed", "atlas")]})]
    for asked in (which("which_one"), polar(U("reviewed", "atlas"))):
        document = {"units": facts + [unit("q", 2, "question", asked)]}
        py = core(env, document)
        q = py.questions[0]
        proof = prove_entailment(py.env, py._caller_premises(), Not(py.presupposition(q)))
        line = py.check_presupposition_failure_certificate(q, proof.certificate)
        assert (line["status"], line["premises"]["status"], line["vacuous"]) == \
            ("PRESUPPOSITION-FAILED", "INCONSISTENT", "yes")
        lean_line = run1({"id": "h", "kind": "speech-answer", "environment": env, "document": document,
                          "question": "q", "evidence": {"presupposition_failed": proof.certificate},
                          "premise_status": {"inconsistent": line["premises"]["certificate"]}})["answer"]
        assert lean_line == \
            "PRESUPPOSITION-FAILED (certificate for ¬H; premises: INCONSISTENT (certificate); vacuous: yes)"
    # A consistent list: ¬H is not certified, never reported as a failed presupposition.
    consistent = core(env, {"units": facts[:1] + [unit("q", 2, "question", which("which_one"))]})
    with pytest.raises(VEError, match="AnswerMismatch: q"):
        consistent.check_presupposition_failure_certificate(consistent.questions[0], proof.certificate)
    # The compliance line of a proof task over contradictory premises is vacuous and says so.
    env["vocabulary"]["predicates"]["cat"]["verbalisation"] = "{0} is a cat"
    lines = ["Tom is a cat.\n", "Tom is not a cat.\n", "Prove that tom is a cat using these premises.\n"]
    positions = [0]
    for text in lines:
        positions.append(positions[-1] + len(text.encode()))
    task = command("require", "submit_required", ["q1"])
    units = [{**unit("p", 0, "asserted", {"ast": U("cat", "tom")}), "span": positions[0:2]},
             {**unit("n", 0, "asserted", {"ast": ["not", U("cat", "tom")]}), "span": positions[1:3]},
             {**unit("t", 0, "instruction", task), "span": positions[2:4]}]
    records = [{"id": "q1", "premises": ["p", "n"], "target": {"ast": U("cat", "tom")}}]
    py = core(env, {"units": units, "queries": records})
    proof = prove_entailment(py.env, py._caller_premises("q1"), py.queries["q1"].target)
    path = tmp_path / "task.ve.md"
    path.write_text("---\n" + json.dumps({"format": "ve-document@2", "environment": env, "units": units,
                                          "queries": records, "compliance": [
                                              {"command": "t", "evidence": {"certificate": proof.certificate}}]}) +
                    "\n---\n" + "".join(lines))
    [line] = load_speech_document(path).compliance_lines
    assert (line["status"], line["premises"]["status"], line["vacuous"]) == ("certificate", "INCONSISTENT", "yes")


def test_document_admission_stays_closed_until_source_wrapper_is_proved(lean):
    case = {"id": "closed", "kind": "admission", "environment": F0(),
            "document": {"units": [unit("u1", 0, "instruction",
                                        command("require", "click_required", ["check"]))]}}
    assert run1(case)["error"] == (
        "UnsupportedProfile: case kind admission is not available on the speech-acts route")


def test_reported_structural_regressions(lean, tmp_path):
    env = F0()
    base = {"units": [unit("u", 0, "question", polar(U("reviewed", "atlas")))]}
    for value in (7, True):
        document = {**base, "queries": value}
        with pytest.raises(VEError, match="^array expected$"):
            core(env, document)
        assert run1({"id": "queries", "kind": "speech-elaborate", "environment": env,
                     "document": document})["error"] == "array expected"
    for phrase in ("the reviewed", "the is"):
        scoped = F0(definites={phrase: "check"})
        assert Environment(scoped)
        assert "error" not in run1({"id": "scope", "kind": "speech-elaborate",
                                    "environment": scoped, "document": {"units": []}})
    versions = [reading_set("u", n, "open", "question", polar(U("reviewed", "atlas")))
                for n in (1, 2, 1)]
    document = {**base, "reading_sets": versions}
    with pytest.raises(VEError, match="invalid or duplicate reading set version"):
        core(env, document)
    assert run1({"id": "versions", "kind": "speech-elaborate", "environment": env,
                 "document": document})["error"] == "invalid or duplicate reading set version"
    bad = reading_set("u", 1, "open", "question", polar(U("reviewed", "atlas")))
    bad["readings"].append({**copy.deepcopy(bad["readings"][0]), "id": []})
    metadata = {"format": "ve-document@2", "environment": env,
                "units": [unit("u", 0, "question", polar(U("reviewed", "atlas")))],
                "reading_sets": [bad]}
    path = tmp_path / "bad-candidate.ve.md"
    path.write_text("---\n" + json.dumps(metadata) + "\n---\nX")
    with pytest.raises(VEError, match="invalid reading"):
        load_speech_document(path)


def test_unit_content_diagnostics_match_lean(lean):
    env = F0()
    body = U("reviewed", "atlas")
    cases = [
        ("asserted", {"ast": body, "extra_wire_field": 7}, "InvalidInput: asserted content"),
        ("asserted", 7, "InvalidInput: asserted content"),
        ("asserted", {}, "InvalidInput: asserted content"),
        ("instruction", 7, "InvalidInput: misplaced speech content"),
        ("question", {"question": {"mode": 7, "body": body}},
         "InvalidInput: invalid question fields for u"),
        ("question", {"question": {"body": body}},
         "InvalidInput: invalid question fields for u"),
        ("question", {"binding": {"you": "alice"}, "question": {"mode": "polar", "body": body}},
         "InvalidInput: binding content requires binding kind"),
    ]
    for index, (kind, content, expected) in enumerate(cases):
        document = {"units": [unit("u", 0, kind, content)]}
        with pytest.raises(VEError) as raised:
            core(env, document)
        assert _diagnostic(raised.value) == expected
        assert run1({"id": str(index), "kind": "speech-elaborate", "environment": env,
                     "document": document})["error"] == expected


def test_duplicate_reading_version_precedes_later_item_error(lean):
    env = F0()
    sets = [reading_set("u", n, status, "question", polar(U("reviewed", "atlas")))
            for n, status in ((1, "open"), (1, "open"), (2, "authored"))]
    sets[2].pop("signature")
    document = {"units": [unit("u", 0, "question", polar(U("reviewed", "atlas")))],
                "reading_sets": sets}
    expected = "invalid or duplicate reading set version"
    with pytest.raises(VEError) as raised:
        core(env, document)
    assert _diagnostic(raised.value) == expected
    assert run1({"id": "duplicate", "kind": "speech-elaborate", "environment": env,
                 "document": document})["error"] == expected


def test_balanced_formula_node_budget_agrees_with_lean(lean):
    body = ["top"]
    for _ in range(13):
        body = ["and", body, copy.deepcopy(body)]
    click = command("require", "click_required", ["check"])
    norm = {"norm": {"name": "n1", "predicate": "click_required", "sign": True,
                     "guard": body, "unless": [], "over": []}}
    documents = [
        {"units": [unit("u", 0, "question", polar(body))]},
        {"units": [unit("u", 0, "asserted", {"ast": body})]},
        {"units": [unit("u", 0, "instruction", {"command": {**click["command"], "guard": body}})]},
        {"units": [unit("u", 0, "norm", norm)]},
        {"units": [unit("u", 0, "question", {"question": {"mode": "follows", "query": "q1"}})],
         "queries": [{"id": "q1", "premises": [], "target": {"ast": body}}]},
        {"units": [unit("u", 0, "asserted")],
         "reading_sets": [reading_set("u", 1, "open", "asserted", body)]},
    ]
    for index, document in enumerate(documents):
        with pytest.raises(VEError) as raised:
            core(F0(), document)
        assert _diagnostic(raised.value) == "ResourceLimit: AST exceeds depth or node budget"
        assert run1({"id": f"nodes-{index}", "kind": "speech-elaborate", "environment": F0(),
                     "document": document})["error"] == _diagnostic(raised.value)


def test_fenced_signed_reading_uses_derived_meaning(lean, tmp_path):
    env = F0()
    click = command("require", "click_required", ["check"])
    sets = [reading_set("x", 1, "open", "instruction", click),
            {**reading_set("r", 1, "authored", "question",
                           {"question": {"mode": "reading", "set": "rs", "version": 1}}), "id": "rr"}]
    sets[0]["id"] = "rs"
    term = {"name": "intended-reading.r", "arguments": ["rs"], "version": 1, "decided_by": "alice",
            "jurisdiction": "t1", "necessary": [], "sufficient": [], "precedents": [],
            "factors": ["necessary: at least one nomination of a candidate of rs at version 1 by alice",
                        "sufficient: exactly one nomination of a candidate of rs at version 1 by alice"]}
    units, (plain, fenced) = _fenced_pair(
        tmp_path, "signed-reading", env, ["Click check.\n", "Which reading did you mean?\n"],
        [unit("x", 0, "instruction", click), unit("r", 0, "question",
             {"question": {"mode": "reading", "set": "rs", "version": 1}})],
        "r", open_terms=[term], reading_sets=sets)
    a, b = load_speech_document(plain).document, load_speech_document(fenced).document
    le = elaborate(env, {"units": units, "reading_sets": sets})
    assert a.meaning_ids["r"] == b.meaning_ids["r"] == le["questions"][0]["meaning_id"]


def test_fence_kind_uses_signed_choice(lean, tmp_path):
    env = F0()
    click = command("require", "click_required", ["check"])
    sets = [reading_set("u", 1, "authored", "instruction", click)]
    units, (plain, fenced) = _fenced_pair(
        tmp_path, "signed-kind", env, ["Click check.\n"],
        [unit("u", 0, "asserted", {"ast": U("reviewed", "atlas")})], "u", reading_sets=sets)
    a, b = load_speech_document(plain).document, load_speech_document(fenced).document
    le = elaborate(env, {"units": units, "reading_sets": sets})
    assert a.meaning_ids == b.meaning_ids
    assert [c.unit for c in a.commands if c.active] == [c.unit for c in b.commands if c.active] == \
        [c["unit"] for c in le["commands"]] == ["u"]


@pytest.mark.parametrize("original_kind,original_content,authored", [
    ("asserted", {"ast": U("reviewed", "beacon")}, True),
    ("question", polar(U("reviewed", "beacon")), True),
    ("asserted", {"ast": U("reviewed", "atlas")}, False),
])
def test_assertion_fence_agrees_with_unfenced_choice(lean, tmp_path, original_kind, original_content, authored):
    # The signed assertion replaces even a different original kind or content.
    env = F0()
    env["vocabulary"]["predicates"]["reviewed"]["verbalisation"] = "{0} is reviewed"
    chosen = {"ast": U("reviewed", "atlas")}
    sets = [reading_set("u", 1, "authored", "asserted", chosen)] if authored else []
    units, (plain, fenced) = _fenced_pair(
        tmp_path, f"asserted-{original_kind}-{authored}", env, ["Atlas is reviewed.\n"],
        [unit("u", 0, original_kind, original_content)], "u", reading_sets=sets)
    a, b = load_speech_document(plain).document, load_speech_document(fenced).document
    le = elaborate(env, {"units": units, "reading_sets": sets})
    assert a.meaning_ids == b.meaning_ids
    assert [_to_data(f) for f in a.premises()] == [_to_data(f) for f in b.premises()] == le["premises"]
    assert [u for u, _ in a.asserted] == [u for u, _ in b.asserted] == ["u"]


@pytest.mark.parametrize("wording,original_kind,original_content,choice_kind,choice_content", [
    ("Is atlas reviewed?", "question", polar(U("reviewed", "atlas")), "asserted",
     {"ast": U("reviewed", "atlas")}),
    ("Click check.", "instruction", command("require", "click_required", ["check"]), "asserted",
     {"ast": U("reviewed", "atlas")}),
    ("Atlas is reviewed.", "asserted", {"ast": U("reviewed", "atlas")}, "question",
     polar(U("reviewed", "atlas"))),
    # The rule holds among all three speech-act kinds, not only the three directions above.
    ("Is atlas reviewed?", "question", polar(U("reviewed", "atlas")), "instruction",
     command("require", "click_required", ["check"])),
    ("Click check.", "instruction", command("require", "click_required", ["check"]), "question",
     polar(U("reviewed", "atlas"))),
    ("Atlas is reviewed.", "asserted", {"ast": U("reviewed", "atlas")}, "instruction",
     command("require", "click_required", ["check"])),
])
def test_signed_choice_kind_matches_surface_in_both_forms(
        lean, tmp_path, wording, original_kind, original_content, choice_kind, choice_content):
    env = F0()
    env["vocabulary"]["predicates"]["reviewed"]["verbalisation"] = "{0} is reviewed"
    chosen = reading_set("u", 1, "authored", choice_kind, choice_content)
    units, (plain, fenced) = _fenced_pair(
        tmp_path, f"choice-surface-{choice_kind}-{original_kind}", env, [wording + "\n"],
        [unit("u", 0, original_kind, original_content)], "u", reading_sets=[chosen])
    for path in (plain, fenced):
        with pytest.raises(VEError, match="^InvalidInput: choice kind$"):
            load_speech_document(path)
    assert run1({"id": "choice-kind", "kind": "speech-elaborate", "environment": env,
                 "document": {"units": [{**units[0], "source": wording}],
                              "reading_sets": [chosen]}})["error"] == "InvalidInput: choice kind"


def _outcome(thunk):
    try:
        thunk()
    except VEError as exc:
        return str(exc)
    return "ok"


def _lean_outcome(result):
    return "ok" if result.get("status") == "ok" else result.get("error")


def _choice_case(env, wording, choice_kind, choice_content, original=None, source=True):
    """A one-unit document whose signed choice replaces `original`, and its Lean case with the wording as `source`."""
    original = original or unit("u", 0, "asserted", {"ast": U("reviewed", "atlas")})
    chosen = reading_set("u", 1, "authored", choice_kind, choice_content)
    document = {"units": [{**original, **({"source": wording} if source else {})}], "reading_sets": [chosen]}
    return document, {"id": "choice", "kind": "speech-elaborate", "environment": env, "document": document}


def _both_forms(tmp_path, name, env, wording, choice_kind, choice_content):
    chosen = reading_set("u", 1, "authored", choice_kind, choice_content)
    _, paths = _fenced_pair(tmp_path, name, env, [wording + "\n"],
                            [unit("u", 0, "asserted", {"ast": U("reviewed", "atlas")})], "u", reading_sets=[chosen])
    return [_outcome(lambda p=p: load_speech_document(p)) for p in paths]


def test_plain_regulated_predicate_never_crashes_the_surface_kind(lean, tmp_path):
    # Regression (speech-acts5 A1): a `plain` regulated predicate has no act, and Python's surface check called
    # `act.split()` on it, raising `AttributeError` for any declarative authored choice, fenced or not; Lean skipped
    # it and accepted.  A plain declaration never classifies a wording, in both cores.
    env = F0()
    env["vocabulary"]["predicates"]["reviewed"]["verbalisation"] = "{0} is reviewed"
    env["vocabulary"]["predicates"]["disabled"]["regulated"] = {"role": "plain", "default": "deny"}
    for wording, kind, content, expected in [
            ("Atlas is reviewed.", "asserted", {"ast": U("reviewed", "atlas")}, "ok"),
            ("Click check.", "instruction", command("require", "click_required", ["check"]), "ok"),
            ("Click check.", "asserted", {"ast": U("reviewed", "atlas")}, "InvalidInput: choice kind")]:
        assert _both_forms(tmp_path, f"plain-{kind}-{len(wording)}", env, wording, kind, content) == [expected] * 2
        document, case = _choice_case(env, wording, kind, content)
        assert _outcome(lambda: core(env, document)) == _lean_outcome(run1(case)) == expected


def test_surface_kind_reads_normalised_acts_in_both_cores(lean, tmp_path):
    # Regression (speech-acts5 A2): with the accepted act "{0}  click {1}", Lean split the raw act and found no
    # verb, so "Click check." under an asserted choice was accepted by Lean and rejected by Python, and an
    # instruction choice the other way.  Both cores read W1's normalised act.
    env = F0()
    env["vocabulary"]["predicates"]["reviewed"]["verbalisation"] = "{0} is reviewed"
    for name in ("click_required", "click_permitted"):
        env["vocabulary"]["predicates"][name]["regulated"]["act"] = "{0}  click\t{1}"
    click = command("require", "click_required", ["check"])
    for kind, content, expected in [("asserted", {"ast": U("reviewed", "atlas")}, "InvalidInput: choice kind"),
                                    ("instruction", click, "ok")]:
        assert _both_forms(tmp_path, f"act-{kind}", env, "Click check.", kind, content) == [expected] * 2
        document, case = _choice_case(env, "Click check.", kind, content)
        assert _outcome(lambda: core(env, document)) == _lean_outcome(run1(case)) == expected


_NON_SPEECH_CHOICES = [
    ("norm", {"norm": {"name": "n1", "predicate": "click_required", "sign": True, "guard": ["top"],
                       "unless": [], "over": []}}),
    # W2's reading sets admit formula content only under `asserted` (or a quoted one).
    *((k, None) for k in ("definition", "example", "exposition", "analogy", "explanation", "meta")),
    ("binding", {"binding": {"you": "alice"}}),
    (["attributed", "bob", "says", "question"], polar(U("reviewed", "atlas"))),
    (["attributed", "bob", "says", "instruction"], command("require", "click_required", ["check"])),
    (["attributed", "bob", "says", "asserted"], {"ast": U("reviewed", "atlas")}),
    (["hedged", "likely", "asserted"], {"ast": U("reviewed", "atlas")}),
    (["hedged", "likely", ["attributed", "bob", "says", "question"]], polar(U("reviewed", "atlas"))),
]


@pytest.mark.parametrize("choice_kind,choice_content", _NON_SPEECH_CHOICES,
                         ids=[json.dumps(k) for k, _ in _NON_SPEECH_CHOICES])
def test_non_speech_choice_kinds_are_unaffected_by_the_surface_rule(lean, tmp_path, choice_kind, choice_content):
    # Regression (speech-acts5 A3, orchestrator correction): the kind rule compared every choice kind with the
    # wording's surface kind, so every norm, definition, example or quoted choice failed whatever its wording.
    # The rule is only among asserted, question and instruction: any other choice is accepted on a question,
    # a declarative, an imperative or a binding wording alike, with the outcome it has without a wording.
    env = F0()
    env["vocabulary"]["predicates"]["reviewed"]["verbalisation"] = "{0} is reviewed"
    cases, expected = [], []
    for i, wording in enumerate(["Is atlas reviewed?", "Atlas is reviewed.", "Click check.", "Do not click check.",
                                 "In this task, you are alice."]):
        assert _both_forms(tmp_path, f"non-speech-{i}", env, wording, choice_kind, choice_content) == ["ok"] * 2
        document, case = _choice_case(env, wording, choice_kind, choice_content)
        bare, bare_case = _choice_case(env, wording, choice_kind, choice_content, source=False)
        assert _outcome(lambda: core(env, document)) == _outcome(lambda: core(env, bare)) == "ok"
        # Lean's frozen JSON boundary carries no `null`, the only content an atomic non-speech choice takes.
        if choice_content is not None:
            cases += [case, bare_case]
            expected += ["ok", "ok"]
    assert [_lean_outcome(r) for r in run(cases)] == expected


def test_speech_choice_on_a_binding_wording_is_unchecked(lean):
    # "Only among the three": a binding-shaped wording has no speech-act surface kind to contradict.
    env = F0()
    for kind, content in [("asserted", {"ast": U("reviewed", "atlas")}), ("question", polar(U("reviewed", "atlas"))),
                          ("instruction", command("require", "click_required", ["check"]))]:
        document, case = _choice_case(env, "In this task, you are alice.", kind, content)
        assert _outcome(lambda: core(env, document)) == _lean_outcome(run1(case)) == "ok"


NON_ASCII = "InvalidInput: non-ASCII speech wording"
_SPACES = [" ", "\t", "\n", "\r", "\x0b", "\x0c"]
_NOT_SPACES = ["\x1c", "\x1d", "\x1e", "\x1f", "\x85", "\xa0", " ", " ", " ", "　", "\x00", "\x7f"]


def _surface_variants():
    bases = ["Is atlas reviewed?", "Atlas is reviewed.", "Atlas is reviewed?", "Click check.", "Do not click check.",
             "Prove that atlas is reviewed.", "In this task, you are alice."]
    variants = set()
    for base in bases:
        variants |= {base, base.upper(), base.lower(), base.swapcase()}
        for c in _SPACES + _NOT_SPACES:
            variants |= {c + base, base + c, base.replace(" ", c, 1), base.replace(" ", c + c)}
    # Non-ASCII letters that Unicode case mapping would fold onto an ASCII prefix or suffix.
    variants |= {"Iſ atlas reviewed.", "İs atlas reviewed.", "ıs atlas reviewed.", "Kick check.",
                 "Atlas is reviewed？", "DO NOT CLICK CHECK.", "dO nOt ClIcK cHeCk.", "CLICK CHECK."}
    return sorted(variants)


def test_surface_normalisation_is_one_ascii_definition_in_both_cores(lean):
    # Regression (speech-acts5 B): Python stripped and casefolded Unicode while Lean trimmed and lowered ASCII, so
    # "Atlas is reviewed?\x0c" was a question in Python and a declarative in Lean.  Both cores now read wordings
    # through one ASCII-only normalisation (3.2).  Differentially over whitespace, case and control characters,
    # each of the three speech-act choices has one outcome in Python and in Lean.
    from ve.speech_acts import surface_kind, surface_words
    env = F0()
    env["vocabulary"]["predicates"]["reviewed"]["verbalisation"] = "{0} is reviewed"
    E = Environment(env)
    assert surface_kind(E, "Atlas is reviewed?\x0c") == "question"
    assert surface_kind(E, "Atlas is reviewed?\x1c") == surface_kind(E, "Atlas is reviewed?\x7f") == "asserted"
    assert surface_kind(E, "Do\x0bnot  click check.") == surface_kind(E, "DO NOT CLICK CHECK.") == "instruction"
    # A non-ASCII wording is rejected before it is classified (3.2).
    for wording in ["Atlas is reviewed?\x85", "Atlas is reviewed?\xa0", "Iſ atlas reviewed.", "İs atlas reviewed."]:
        with pytest.raises(VEError, match=f"^{NON_ASCII}$"):
            surface_kind(E, wording)
    assert surface_words("\x0c A\tB C \n") == "a b c"
    choices = [("asserted", {"ast": U("reviewed", "atlas")}), ("question", polar(U("reviewed", "atlas"))),
               ("instruction", command("require", "click_required", ["check"]))]
    cases, python = [], []
    for wording in _surface_variants():
        for kind, content in choices:
            document, case = _choice_case(env, wording, kind, content)
            cases.append(case)
            python.append(_outcome(lambda: core(env, document)))
            expected = (NON_ASCII if not wording.isascii() else "InvalidInput: choice kind"
                        if surface_kind(E, wording) in ("asserted", "question", "instruction")
                        and surface_kind(E, wording) != kind else "ok")
            assert python[-1] == expected, (wording, kind)
    lean_results = [_lean_outcome(r) for r in run(cases)]
    mismatches = [(c["document"]["units"][0]["source"], c["document"]["reading_sets"][0]["readings"][0]["kind"], p, le)
                  for c, p, le in zip(cases, python, lean_results) if p != le]
    assert mismatches == []


def test_signed_choice_source_null_is_one_diagnostic(lean):
    # Regression (speech-acts5 B): with `"source": null` Python skipped the wording check and Lean raised
    # `InvalidInput: speech wording`.  A present `source` that is not a string is that error in both cores,
    # whatever the choice kind.
    # Lean's decoder raises it for `null` too, but the route's frozen JSON boundary rejects every `null` first.
    from test_speech_acts_lean import LEAN
    env = F0()
    for value in (None, 7, [], {}, True):
        for kind, content in [("asserted", {"ast": U("reviewed", "atlas")}), ("question", polar(U("reviewed", "atlas"))),
                              ("definition", {"ast": U("reviewed", "atlas")})]:
            document, case = _choice_case(env, value, kind, content)
            assert _outcome(lambda: core(env, document)) == "InvalidInput: speech wording"
            if value is None:
                completed = subprocess.run([str(LEAN), "-"], input=json.dumps([case]), capture_output=True,
                                           text=True, timeout=60)
                assert completed.returncode != 0 and "expected restricted JSON value" in completed.stderr
            else:
                assert _lean_outcome(run1(case)) == "InvalidInput: speech wording"


def test_quoted_question_meaning_id_is_its_question_object(lean):
    # Regression (speech-acts5 B): a stated `meaning_id` on a quoted-question unit was expected absent by Python
    # and regenerated by Lean, so each accepted what the other rejected.  A quoted question has its question
    # object's meaning id (3.5) in both cores: the same as a live question with the same content.
    env = F0()
    env["vocabulary"]["predicates"]["reviewed"]["verbalisation"] = "{0} is reviewed"
    source = b"Bob says: is atlas reviewed?\n"
    quoted = {**unit("u", 0, ["attributed", "bob", "says", "question"], polar(U("reviewed", "atlas"))),
              "span": [0, len(source)]}
    live = elaborate(env, {"units": [unit("q", 0, "question", polar(U("reviewed", "atlas")))]})
    expected = live["questions"][0]["meaning_id"]
    assert core(env, {"units": [quoted]}).meaning_ids["u"] == expected
    base = {"format": "ve-document@2", "environment": env}
    for stated, outcome in [(expected, "ok"), ("0" * 64, "unit meaning id does not match content")]:
        stated_unit = {**quoted, "meaning_id": stated}
        assert _outcome(lambda: SpeechSource({**base, "units": [stated_unit]}, source, {})) == outcome
        assert _lean_outcome(run1({"id": "quoted-id", "kind": "speech-elaborate", "environment": env,
                                   "document": {"units": [stated_unit]}})) == outcome


def _unary_click_env():
    """F0 with `click` a unary act ("{0} click"): its command wordings are "Click." and "Click, if ..."."""
    env = F0()
    env["vocabulary"]["predicates"]["reviewed"]["verbalisation"] = "{0} is reviewed"
    for name in ("click_required", "click_permitted"):
        env["vocabulary"]["predicates"][name]["arguments"] = ["user"]
        env["vocabulary"]["predicates"][name]["regulated"]["act"] = "{0} click"
    env["vocabulary"]["predicates"]["done_click"]["arguments"] = ["user"]
    return env


def test_unary_imperative_is_an_instruction_in_both_cores(lean, tmp_path):
    # Regression (speech-acts6 A1): with `click_required` and `click_permitted` over `["user"]` and act
    # "{0} click", the parser reads "Click." as an instruction, but both classifiers required a space after the
    # verb, so both cores accepted an asserted choice on it and rejected the instruction choice it parses as,
    # fenced and inline.  A verb ends at the end of the wording or at a word break (3.2).
    env = _unary_click_env()
    require, forbid = command("require", "click_required", []), command("forbid", "click_permitted", [])
    choices = {"asserted": {"ast": U("reviewed", "atlas")}, "question": polar(U("reviewed", "atlas"))}
    guarded = {"command": {**require["command"], "guard": U("reviewed", "atlas")}}
    # Each wording with the command it parses as, or None where the parser reads none ("Click" lacks its period).
    for wording, instruction in [("Click.", require), ("Click, if atlas is reviewed.", guarded),
                                 ("Do not click.", forbid), ("CLICK.", require), ("Click", None), ("Click!", None),
                                 ("Click\x0c.", None)]:
        for kind, content in [*choices.items(), *([("instruction", instruction)] if instruction else [])]:
            expected = "ok" if kind == "instruction" else "InvalidInput: choice kind"
            assert _both_forms(tmp_path, f"unary-{kind}", env, wording, kind, content) == [expected] * 2, \
                (wording, kind)
            document, case = _choice_case(env, wording, kind, content)
            assert _outcome(lambda: core(env, document)) == _lean_outcome(run1(case)) == expected, (wording, kind)
    # A word that only begins with the verb is no imperative: "clicked", "clicks", "click-through", "click_rate".
    for wording in ["Clicked.", "Clicks.", "Click-through is fine.", "Click_rate is high.", "Click2."]:
        document, case = _choice_case(env, wording, "asserted", choices["asserted"])
        assert _outcome(lambda: core(env, document)) == _lean_outcome(run1(case)) == "ok", wording
    # A non-ASCII letter never continues or ends a verb: the wording is rejected before it is classified.
    document, case = _choice_case(env, "Click\u00e9.", "asserted", choices["asserted"])
    assert _outcome(lambda: core(env, document)) == _lean_outcome(run1(case)) == NON_ASCII


def test_every_parsed_speech_act_has_its_surface_kind(lean):
    # The class behind speech-acts6 A1 and B: a wording the speech parser reads as a command or question has that
    # surface kind, so no signed choice can contradict the reading the parser gives it.  Over unary, binary and
    # multi-word acts, conditions, definites, and whitespace, case and Unicode variants, every parsed wording's
    # kind is its surface kind, in Python and (through the choice check) in Lean.
    from ve.speech_acts import surface_kind
    wordings = ["Click.", "Click, if atlas is reviewed.", "Do not click.", "Click check.", "Do not click check.",
                "Open the desk.", "Open the writing desk.", "Do not share the token.", "Is atlas reviewed?",
                "Is it the case that atlas is reviewed?", "Which one of atlas and beacon is reviewed?",
                "Which of atlas, beacon are reviewed?", "Atlas is reviewed.", "Do check.", "Question check.",
                "How check, if atlas is reviewed.", "Do not do check.", "Check click.", "Does atlas click?"]
    variants = set()
    for base in wordings:
        variants |= {base, base.lower(), base.upper()}
        for c in _SPACES + _NOT_SPACES + ["\u017f", "\u212a"]:
            variants |= {c + base, base + c, base.replace(" ", c, 1), base.replace("s", c, 1),
                         base.replace("k", c, 1)}
    cases, expected = [], []
    for env in (F0(), _unary_click_env(), *(_act_env("{0} " + v + " {1}") for v in ("do", "question", "how")),
                _act_env("{0} {1} click")):
        env["vocabulary"]["predicates"]["reviewed"]["verbalisation"] = "{0} is reviewed"
        E = Environment(env)
        for wording in sorted(variants):
            try:
                _, kind = parse_speech(E, wording, E.speech_acts)
            except VEError:
                continue
            assert surface_kind(E, wording) == kind, wording
            other = "asserted" if kind != "asserted" else "question"
            content = {"ast": U("reviewed", "atlas")} if other == "asserted" else polar(U("reviewed", "atlas"))
            _, case = _choice_case(env, wording, other, content)
            cases.append(case)
            expected.append("InvalidInput: choice kind")
    assert len(cases) > 40
    assert [_lean_outcome(r) for r in run(cases)] == expected


def _act_env(act, unary=False):
    """F0 with `click_required`/`click_permitted` under `act` (over `["user"]` when `unary`)."""
    env = _unary_click_env() if unary else F0()
    env["vocabulary"]["predicates"]["reviewed"]["verbalisation"] = "{0} is reviewed"
    for name in ("click_required", "click_permitted"):
        env["vocabulary"]["predicates"][name]["regulated"]["act"] = act
    return env


# The interrogative first words of 3.2 a W1 act may begin with ("is" and "must" are reserved) and that the parser
# does not refuse outright ("Which ..." and "Can ..." are its `OpenDomainWhich` and `ModalQuestion`).
_ACT_INTERROGATIVES = ["question", "are", "does", "do", "did", "was", "were", "will", "would", "who", "what", "when",
                       "where", "why", "how"]


def test_act_verb_outranks_an_interrogative_word_in_both_cores(lean, tmp_path):
    # Regression (speech-acts6 A1, the class): with the act "{0} do {1}", the parser reads "Do check." as the
    # command to click `check`, but both classifiers took its interrogative first word for a question, so both
    # cores accepted a question choice on it and rejected the instruction choice it parses as.  A final `?`
    # decides first; a declared act's verb then outranks an interrogative first word (3.2).
    asserted, question = {"ast": U("reviewed", "atlas")}, polar(U("reviewed", "atlas"))
    require = command("require", "click_required", ["check"])
    cases, expected = [], []
    for verb in _ACT_INTERROGATIVES:
        env = _act_env("{0} " + verb + " {1}")
        E = Environment(env)
        wording = verb.capitalize() + " check."
        assert parse_speech(E, wording, E.speech_acts)[1] == "instruction", wording
        for kind, content in [("asserted", asserted), ("question", question), ("instruction", require)]:
            outcome = "ok" if kind == "instruction" else "InvalidInput: choice kind"
            document, case = _choice_case(env, wording, kind, content)
            assert _outcome(lambda: core(env, document)) == outcome, (wording, kind)
            cases.append(case)
            expected.append(outcome)
        # A final `?` is still a question, and without the act the interrogative word is.
        for wording, env in [(verb.capitalize() + " check?", env), (verb.capitalize() + " check.", _act_env("{0} click {1}"))]:
            document, case = _choice_case(env, wording, "question", question)
            assert _outcome(lambda: core(env, document)) == "ok", wording
            cases.append(case)
            expected.append("ok")
    assert [_lean_outcome(r) for r in run(cases)] == expected
    # The reproducer, fenced and inline.
    env = _act_env("{0} do {1}")
    assert _both_forms(tmp_path, "do-instruction", env, "Do check.", "instruction", require) == ["ok"] * 2
    assert _both_forms(tmp_path, "do-question", env, "Do check.", "question", question) == \
        ["InvalidInput: choice kind"] * 2
    # The parser refuses "Can ..." and "Which ..." whatever the acts; both cores still agree on their kind.
    for verb, error in [("can", "ModalQuestion"), ("which", "OpenDomainWhich")]:
        env = _act_env("{0} " + verb + " {1}")
        E = Environment(env)
        with pytest.raises(VEError, match=error):
            parse_speech(E, verb.capitalize() + " check.", E.speech_acts)
        document, case = _choice_case(env, verb.capitalize() + " check.", "instruction", require)
        assert _outcome(lambda: core(env, document)) == _lean_outcome(run1(case)) == "ok"


def test_slot_first_act_reads_no_command_in_either_route(lean, tmp_path):
    # Regression (speech-acts6 A1, the class): with the accepted W1 act "{0} {1} click", the parser read
    # "Check click." as the command to click `check`, but no classifier knows a slot's fillers, so both cores took
    # it for a declarative, accepted an asserted choice on it and rejected the instruction choice it parsed as.  An
    # imperative begins with its act's verb (3.2): an act whose first word after `{0}` is a slot has none, so the
    # parser reads no command of it and it classifies no wording, even one spelling its slot.
    env = _act_env("{0} {1} click")
    E = Environment(env)
    asserted = {"ast": U("reviewed", "atlas")}
    for wording in ["Check click.", "Do not check click.", "Check click, if atlas is reviewed."]:
        with pytest.raises(VEError, match="InvalidInput: no single speech-act reading"):
            parse_speech(E, wording, E.speech_acts)
    for wording, kind, content, outcome in [
            ("Check click.", "asserted", asserted, "ok"),
            ("Check click.", "instruction", command("require", "click_required", ["check"]),
             "InvalidInput: choice kind"),
            ("{1} click.", "asserted", asserted, "ok")]:
        document, case = _choice_case(env, wording, kind, content)
        assert _outcome(lambda: core(env, document)) == _lean_outcome(run1(case)) == outcome, (wording, kind)
        assert _both_forms(tmp_path, f"slot-{kind}-{len(wording)}", env, wording, kind, content) == [outcome] * 2
    # A literal verb after a later slot still reads: "{0} click {1}" is F0's act.
    E = Environment(_act_env("{0} click {1}"))
    assert parse_speech(E, "Click check.", E.speech_acts)[1] == "instruction"


def test_speech_parser_folds_and_trims_ascii_only():
    # Regression (speech-acts6 B, the class): the parser upper-cased a command's first letter with Unicode case
    # mapping, so "Do not ßcheck." read as "Do not SScheck." and forbade the act "{0} sscheck", and it
    # Unicode-stripped the alternatives of a which-question, reading "atlas and \u00a0beacon" as beacon.  The
    # parser folds only A-Z and trims only ASCII whitespace (3.2), so no reader sees another sentence.
    env = _act_env("{0} sscheck", unary=True)
    E = Environment(env)
    assert parse_speech(E, "Do not sscheck.", E.speech_acts)[0]["force"] == "forbid"
    assert parse_speech(E, "Do not SSCHECK.", E.speech_acts)[0]["force"] == "forbid"
    for wording in ["Do not ßcheck.", "ßcheck.", "Do not \u017fscheck."]:
        with pytest.raises(VEError):
            parse_speech(E, wording, E.speech_acts)
    E = Environment(_act_env("{0} click {1}"))
    for alternatives in ["atlas and  beacon", "atlas,  beacon", "atlas and beacon\t"]:
        content, kind = parse_speech(E, f"Which one of {alternatives} is reviewed?", E.speech_acts)
        assert (kind, content["domain"]) == ("question", ["atlas", "beacon"]), alternatives
    for alternatives in ["atlas and \u00a0beacon", "atlas\u00a0, beacon", "atlas, beacon\u2003"]:
        with pytest.raises(VEError, match=f"^{NON_ASCII}$"):
            parse_speech(E, f"Which one of {alternatives} is reviewed?", E.speech_acts)


def _source_outcome(env, span, units, fences=None, sets=()):
    meta = {"format": "ve-document@2", "environment": env, "units": units, "reading_sets": list(sets)}
    return _outcome(lambda: SpeechSource(meta, span.encode(), fences or {}))


_ORIGINALS = {"asserted": {"ast": U("reviewed", "atlas")}, "question": polar(U("reviewed", "atlas")),
              "instruction": command("require", "click_required", ["check"])}
_CHOICES = [("asserted", {"ast": U("reviewed", "atlas")}), ("question", polar(U("reviewed", "atlas"))),
            ("instruction", command("require", "click_required", ["check"]))]


def test_fence_never_replaces_the_source_sentence_in_the_choice_check(lean):
    # Regression (speech-acts6 A2): with original kind `asserted`, source "Is atlas reviewed?", fence "Atlas is
    # reviewed." and a signed asserted choice, loading succeeded and supplied an asserted premise, while the
    # inline document was `InvalidInput: choice kind`: the source wrapper checked the fence text in place of the
    # source sentence.  The sentence is the unit's span in both forms; the fence is content the choice replaces.
    env = F0()
    env["vocabulary"]["predicates"]["reviewed"]["verbalisation"] = "{0} is reviewed"
    fence_texts = ["Atlas is reviewed.\n", "Is atlas reviewed?\n", "Click check.\n"]
    for span in ["Is atlas reviewed?\n", "Atlas is reviewed.\n", "Click check.\n"]:
        for original, original_content in _ORIGINALS.items():
            base = {**unit("u", 0, original, original_content), "span": [0, len(span.encode())]}
            for choice_kind, choice_content in _CHOICES:
                sets = [reading_set("u", 1, "authored", choice_kind, choice_content)]
                inline = _source_outcome(env, span, [base], sets=sets)
                document, case = _choice_case(env, span.strip(), choice_kind, choice_content, original=base)
                assert inline == _outcome(lambda: core(env, document)), (span, original, choice_kind)
                assert (inline == "InvalidInput: choice kind") == (_lean_outcome(run1(case)) != "ok")
                for fence in fence_texts:
                    fenced = {**base, "content": {"fence": "u"}, "surface": "english"}
                    assert _source_outcome(env, span, [fenced], {"u": fence}, sets) == inline, \
                        (span, fence, original, choice_kind)
    # The reproducer: no asserted premise from a question-worded source.
    span = "Is atlas reviewed?\n"
    fenced = {**unit("u", 0, "asserted"), "content": {"fence": "u"}, "surface": "english", "span": [0, len(span)]}
    assert _source_outcome(env, span, [fenced], {"u": "Atlas is reviewed.\n"},
                           [reading_set("u", 1, "authored", "asserted", {"ast": U("reviewed", "atlas")})]) == \
        "InvalidInput: choice kind"


def test_fenced_and_inline_agree_without_a_choice(lean):
    # The class behind speech-acts6 A2: no reading of a unit sees its fence where the inline form sees its span.
    # Without a signed choice too, a fenced unit whose fence parses as the inline unit's content has the inline
    # unit's outcome on every span, whatever its kind (a command or question span is re-read by the core).
    env = F0()
    env["vocabulary"]["predicates"]["reviewed"]["verbalisation"] = "{0} is reviewed"
    fences = {"asserted": "Atlas is reviewed.\n", "instruction": "Click check.\n", "question": "Is atlas reviewed?\n"}
    outcomes = set()
    for span in ["Is atlas reviewed?\n", "Atlas is reviewed.\n", "Click check.\n", "Do not click check.\n",
                 "Is beacon reviewed?\n"]:
        for kind, content in _ORIGINALS.items():
            inline = {**unit("u", 0, kind, content), "span": [0, len(span)]}
            fenced = {**unit("u", 0, kind), "content": {"fence": "u"}, "surface": "english", "span": [0, len(span)]}
            outcome = _source_outcome(env, span, [inline])
            assert _source_outcome(env, span, [fenced], {"u": fences[kind]}) == outcome, (span, kind)
            outcomes.add(outcome)
    assert "ok" in outcomes and len(outcomes) > 2


def test_source_wording_is_one_ascii_trim_whatever_the_original_kind(lean, tmp_path):
    # Regression (speech-acts6 B): source "Atlas is reviewed? " with a signed asserted choice passes both
    # cores (U+00A0 is an ordinary character, 3.2), and the source wrapper accepted it for original kind
    # `asserted` but rejected it for `question` or `instruction`, whose wording it had Unicode-stripped before
    # the core's check.  Every reader of a wording trims only ASCII whitespace, and every chosen unit carries its
    # wording to the core, so the outcome is the core's on the raw wording, whatever the original kind or form.
    env = F0()
    env["vocabulary"]["predicates"]["reviewed"]["verbalisation"] = "{0} is reviewed"
    bases = ["Atlas is reviewed?", "Is atlas reviewed?", "Atlas is reviewed.", "Click check.", "Is beacon reviewed?",
             "Click token1."]
    spans = {b + "\n" for b in bases}
    for c in _SPACES + _NOT_SPACES:
        spans |= {c + b + "\n" for b in bases} | {b + c + "\n" for b in bases}
    cases, python = [], []
    for span in sorted(spans):
        for choice_kind, choice_content in _CHOICES:
            sets = [reading_set("u", 1, "authored", choice_kind, choice_content)]
            outcomes = set()
            for original, original_content in _ORIGINALS.items():
                base = {**unit("u", 0, original, original_content), "span": [0, len(span.encode())]}
                outcomes.add(_source_outcome(env, span, [base], sets=sets))
                fenced = {**base, "content": {"fence": "u"}, "surface": "english"}
                outcomes.add(_source_outcome(env, span, [fenced], {"u": span}, sets))
            wording = span.strip(" \t\n\r\x0b\x0c")
            document, case = _choice_case(env, wording, choice_kind, choice_content)
            assert outcomes == {_outcome(lambda: core(env, document))}, (span, choice_kind, outcomes)
            cases.append(case)
            python.append(outcomes.pop())
    # Lean reads no English: it agrees on the choice kind, and Python alone also parses a chosen command or question.
    kind_error = "InvalidInput: choice kind"
    assert [_lean_outcome(r) == kind_error for r in run(cases)] == [p == kind_error for p in python]
    # The reproducer: one outcome whatever the original kind, as by both cores, now the ASCII rule's (3.2).
    span = "Atlas is reviewed?\u00a0\n"
    for original, original_content in _ORIGINALS.items():
        base = {**unit("u", 0, original, original_content), "span": [0, len(span.encode())]}
        assert _source_outcome(env, span, [base], sets=[reading_set("u", 1, "authored", *_CHOICES[0])]) == NON_ASCII


ATTACHED = "InvalidInput: speech template slot must stand apart"


def _env_outcomes(tmp_path, name, env):
    """An environment's outcome in Python, in Lean, and in the inline and fenced source wrapper."""
    document, case = _choice_case(env, "Atlas is reviewed.", "asserted", {"ast": U("reviewed", "atlas")})
    return [_outcome(lambda: Environment(env)), _outcome(lambda: core(env, document)), _lean_outcome(run1(case)),
            *_both_forms(tmp_path, name, env, "Atlas is reviewed.", "asserted", {"ast": U("reviewed", "atlas")})]


def test_attached_template_slots_are_rejected_at_environment_load(lean, tmp_path):
    # Regression (speech-acts6 loop A): with `click_required`/`click_permitted` acts "{0} click{1}", W1 accepted
    # the act, the parser read "Clickcheck." as an instruction and both classifiers read it as a declarative, so both
    # cores and both source forms accepted an asserted choice on it and rejected the instruction choice.
    # "{0} click-{1}", "{0} click'{1}" and "{0} pre{1}post" reproduced too.  Under the speech profile every slot of an
    # act or verbalisation template stands apart from its words (3.1), one diagnostic in every checker.
    for i, act in enumerate(["{0} click{1}", "{0} click-{1}", "{0} click'{1}", "{0} pre{1}post", "{0} click {1}x"]):
        env = _act_env(act)
        assert _env_outcomes(tmp_path, f"act-{i}", env) == [ATTACHED] * 5, act
    for wording, kind, content in [("Clickcheck.", "asserted", {"ast": U("reviewed", "atlas")}),
                                   ("Clickcheck.", "instruction", command("require", "click_required", ["check"]))]:
        env = _act_env("{0} click{1}")
        document, case = _choice_case(env, wording, kind, content)
        assert _outcome(lambda: core(env, document)) == _lean_outcome(run1(case)) == ATTACHED
        assert _both_forms(tmp_path, f"clickcheck-{kind}", env, wording, kind, content) == [ATTACHED] * 2
    # Verbalisations and negative verbalisations: a letter, `'`, `-`, `_`, a digit, a brace or a non-ASCII
    # character (U+00A0 included) next to a slot joins it to a word.
    for i, (field, name, template) in enumerate([
            ("verbalisation", "reviewed", "{0}is reviewed"), ("verbalisation", "done_click", "{0} clicked{1}"),
            ("verbalisation", "done_click", "{0} clicked {1}'s"), ("verbalisation", "done_click", "{0} clicked {1}"),
            ("verbalisation", "done_click", "{0}{1} clicked"), ("verbalisation", "reviewed", "{{0} is reviewed"),
            ("verbalisation", "reviewed", "é{0} is reviewed"), ("verbalisation", "done_click", "{0} clicked {1}_"),
            ("verbalisation", "done_click", "{0} clicked {1}9"), ("verbalisation", "reviewed", "{x}{0} is reviewed"),
            ("negative_verbalisation", "done_click", "{0} did not click-{1}")]):
        env = F0()
        env["vocabulary"]["predicates"][name][field] = template
        assert _env_outcomes(tmp_path, f"verb-{i}", env) == [ATTACHED] * 5, template
    # Whitespace, the template's ends and a word break other than a brace keep a slot apart; W1 normalises an act.
    for i, (field, name, template) in enumerate([
            ("verbalisation", "reviewed", "{0} is reviewed"), ("verbalisation", "done_click", "{0} clicked ({1})"),
            ("verbalisation", "done_click", "{0}: clicked {1}."), ("verbalisation", "done_click", "{0}\tclicked\n{1}"),
            ("negative_verbalisation", "done_click", "{0} did not click {1}")]):
        env = F0()
        env["vocabulary"]["predicates"][name][field] = template
        assert _env_outcomes(tmp_path, f"apart-{i}", env)[:3] == ["ok"] * 3, template
    assert _env_outcomes(tmp_path, "act-normalised", _act_env("{0}  click\t{1}"))[:3] == ["ok"] * 3
    # The template check follows the block's structure checks in both checkers.
    env = _act_env("{0} click{1}")
    env["speech_acts"]["extra"] = 1
    assert _env_outcomes(tmp_path, "block-first", env)[:3] == ["InvalidInput: speech_acts block"] * 3


def _checked_env():
    """F0 with `reviewed` verbalised as "{0} is checked", the speech-acts6 loop B reproducer's environment."""
    env = F0()
    env["vocabulary"]["predicates"]["reviewed"]["verbalisation"] = "{0} is checked"
    return env


def test_non_ascii_wording_is_rejected_before_it_is_read(lean, tmp_path):
    # Regression (speech-acts6 loop B): with `reviewed` verbalised as "{0} is checked", "Is it the case that atlas
    # is checKed?" (U+212A) and "Is it the case that atlas is checked?" were read by P0's English, which
    # folds and splits Unicode, so both loaders accepted them, and command guards reproduced.  Every speech-act
    # wording (a sentence, a fence and the formula it embeds) is ASCII only, rejected before it is classified or
    # read, in both cores and both source forms (3.2).
    env = _checked_env()
    E = Environment(env)
    atlas = U("reviewed", "atlas")
    guarded = {"command": {"force": "require", "act": "click_required", "args": ["check"], "guard": atlas}}
    cases = []
    for text, kind, content in [
            ("Is it the case that atlas is checked?", "question", polar(atlas)),
            ("Is atlas checked?", "question", polar(atlas)),
            ("Click check, if atlas is checked.", "instruction", guarded)]:
        for bad in (text.replace("k", "K", 1), text.replace("atlas ", "atlas ", 1), text + " ",
                    text.replace("atlas", "аtlas", 1)):
            with pytest.raises(VEError, match=f"^{NON_ASCII}$"):
                parse_speech(E, bad, E.speech_acts)
            document = {"units": [{**unit("u", 0, kind, content), "source": bad}]}
            assert _outcome(lambda: core(env, document)) == NON_ASCII, bad
            cases.append({"id": "ascii", "kind": "speech-elaborate", "environment": env, "document": document})
            _, paths = _fenced_pair(tmp_path, f"ascii-{len(cases)}", env, [bad + "\n"], [unit("u", 0, kind, content)],
                                    "u")
            assert [_outcome(lambda p=p: load_speech_document(p)) for p in paths] == [NON_ASCII] * 2, bad
            # Before the choice check: no signed choice of any kind is read against it.
            for choice_kind, choice_content in [("asserted", {"ast": atlas}), (kind, content)]:
                document, case = _choice_case(env, bad, choice_kind, choice_content)
                assert _outcome(lambda: core(env, document)) == NON_ASCII, bad
                cases.append(case)
        # The ASCII wording is read in every checker.
        document = {"units": [{**unit("u", 0, kind, content), "source": text}]}
        assert _outcome(lambda: core(env, document)) == "ok"
        assert _lean_outcome(run1({"id": "ascii-ok", "kind": "speech-elaborate", "environment": env,
                                   "document": document})) == "ok"
    assert [_lean_outcome(r) for r in run(cases)] == [NON_ASCII] * len(cases)
    # The embedded formulas of consequence questions and proof tasks, and an asserted fence.
    for bad in ["Does it follow from these premises that atlas is checKed?",
                "Prove that atlas is checked using these premises."]:
        with pytest.raises(VEError, match=f"^{NON_ASCII}$"):
            parse_speech(E, bad, E.speech_acts, query="q1")
    _, paths = _fenced_pair(tmp_path, "ascii-asserted", env, ["Atlas is checKed.\n"],
                            [unit("u", 0, "asserted", {"ast": atlas})], "u")
    assert [_outcome(lambda p=p: load_speech_document(p)) for p in paths] == [NON_ASCII] * 2
    # A fence is ASCII even under an ASCII span, and even where a signed choice replaces it.
    span = "Is atlas checked?\n"
    fenced = {**unit("u", 0, "question"), "content": {"fence": "u"}, "surface": "english", "span": [0, len(span)]}
    for sets in ([], [reading_set("u", 1, "authored", "question", polar(atlas))]):
        assert _source_outcome(env, span, [fenced], {"u": "Is atlas checKed?\n"}, sets) == NON_ASCII
        assert _source_outcome(env, span, [fenced], {"u": "Is atlas checked?\n"}, sets) == "ok"


def test_answer_metadata_types_and_unit_meaning_id(lean):
    env = F0()
    env["vocabulary"]["predicates"]["reviewed"]["verbalisation"] = "{0} is reviewed"
    source = b"Is atlas reviewed?\n"
    question = {**unit("q", 0, "question", polar(U("reviewed", "atlas"))),
                "span": [0, len(source)]}
    answer = {"question": "q", "by": "checker", "support": "model", "answer": "yes",
              "evidence": {"model": model(reviewed=[["atlas"]])}}
    base = {"format": "ve-document@2", "environment": env, "units": [question]}
    for value in (7, True, [], {}, ""):
        bad = {**answer, "by": value}
        with pytest.raises(VEError, match="^InvalidInput: answer record$"):
            SpeechSource({**base, "answers": [bad]}, source, {})
        assert run1({"id": "answer-by", "kind": "speech-elaborate", "environment": env,
                     "document": {"units": [question], "answers": [bad]}})["error"] == "InvalidInput: answer record"
    with pytest.raises(VEError, match="^InvalidInput: answer record$"):
        SpeechSource({**base, "answers": [{**answer, "by": None}]}, source, {})
    with pytest.raises(VEError, match="^InvalidInput: answers$"):
        SpeechSource({**base, "answers": 7}, source, {})
    assert run1({"id": "answers", "kind": "speech-elaborate", "environment": env,
                 "document": {"units": [question], "answers": 7}})["error"] == "InvalidInput: answers"

    valid_id = core(env, {"units": [question]}).meaning_ids["q"]
    assert SpeechSource({**base, "units": [{**question, "meaning_id": valid_id}]}, source, {}).document.meaning_ids["q"] == valid_id
    assert elaborate(env, {"units": [{**question, "meaning_id": valid_id}]})["questions"][0]["meaning_id"] == valid_id
    with pytest.raises(VEError, match="^unit meaning id does not match content$"):
        SpeechSource({**base, "units": [{**question, "meaning_id": "stale"}]}, source, {})
    assert run1({"id": "meaning-id", "kind": "speech-elaborate", "environment": env,
                 "document": {"units": [{**question, "meaning_id": "stale"}]}})["error"] == \
        "unit meaning id does not match content"


def test_stated_assertion_meaning_id_matches_content(lean):
    env = F0()
    env["vocabulary"]["predicates"]["reviewed"]["verbalisation"] = "{0} is reviewed"
    source = b"Atlas is reviewed.\n"
    fact = {**unit("u", 0, "asserted", {"ast": U("reviewed", "atlas")}),
            "span": [0, len(source)]}
    valid = _meaning_id(env, U("reviewed", "atlas"))
    assert SpeechSource({"format": "ve-document@2", "environment": env,
                         "units": [{**fact, "meaning_id": valid}]}, source, {})
    assert U("reviewed", "atlas") in elaborate(env, {"units": [{**fact, "meaning_id": valid}]})["premises"]
    bad = {**fact, "meaning_id": "stale"}
    with pytest.raises(VEError, match="^unit meaning id does not match content$"):
        SpeechSource({"format": "ve-document@2", "environment": env, "units": [bad]}, source, {})
    assert run1({"id": "meaning-id-asserted", "kind": "speech-elaborate", "environment": env,
                 "document": {"units": [bad]}})["error"] == "unit meaning id does not match content"


def test_answer_metadata_validation_follows_unit_validation(lean):
    env = F0()
    source = b"Click check.\n"
    bad_unit = {**unit("u", 0, "instruction", command("require", "nonesuch", ["check"])),
                "span": [0, len(source)]}
    bad_answer = {"question": "u", "by": "checker", "support": "model", "evidence": {},
                  "conditional": 7}
    with pytest.raises(VEError, match="^UnknownSymbol: regulated predicate nonesuch$"):
        SpeechSource({"format": "ve-document@2", "environment": env, "units": [bad_unit],
                      "answers": [bad_answer]}, source, {})
    assert run1({"id": "answer-order", "kind": "speech-elaborate", "environment": env,
                 "document": {"units": [bad_unit], "answers": [bad_answer]}})["error"] == \
        "UnknownSymbol: regulated predicate nonesuch"


def test_answer_conditional_is_json_boolean_in_both_decoders(lean):
    env = F0()
    env["vocabulary"]["predicates"]["reviewed"]["verbalisation"] = "{0} is reviewed"
    source = b"Is atlas reviewed?\n"
    question = {**unit("q", 0, "question", polar(U("reviewed", "atlas"))), "span": [0, len(source)]}
    record = {"question": "q", "by": "checker", "support": "model", "answer": "yes",
              "evidence": {"model": model(reviewed=[["atlas"]])}}
    meta = {"format": "ve-document@2", "environment": env, "units": [question]}

    for flag in (False, True):
        answer = {**record, "conditional": flag}
        assert SpeechSource({**meta, "answers": [answer]}, source, {}).answer_lines[0]["status"] == "evaluated"
        assert elaborate(env, {"units": [question], "answers": [answer]})["questions"][0]["unit"] == "q"

    for flag in (0, 1, "false", [], {}):
        answer = {**record, "conditional": flag}
        with pytest.raises(VEError, match="^InvalidInput: conditional$"):
            SpeechSource({**meta, "answers": [answer]}, source, {})
        assert run1({"id": "conditional", "kind": "speech-elaborate", "environment": env,
                     "document": {"units": [question], "answers": [answer]}})["error"] == "InvalidInput: conditional"
    with pytest.raises(VEError, match="^InvalidInput: conditional$"):
        SpeechSource({**meta, "answers": [{**record, "conditional": None}]}, source, {})


def test_independent_wire_faults_are_rejected_in_both_decoders(lean):
    # P1 will align the first diagnostic's order. Both routes must reject every
    # document even when a later malformed field is decoded before an earlier one.
    env = F0()
    cases = [
        [unit("c1", 0, "instruction", command("require", "nonesuch", ["check"])),
         unit("c2", 1, "instruction", command("maybe", "click_required", ["check"]))],
        [unit("b", 0, "binding", {"binding": {"you": 7}}),
         unit("c", 1, "instruction", command("maybe", "click_required", ["check"]))],
    ]
    for units in cases:
        document = {"units": units}
        with pytest.raises(VEError):
            core(env, document)
        assert run1({"id": "two-faults", "kind": "speech-elaborate", "environment": env,
                     "document": document})["status"] == "error"


def _wire_mutations(value, prefix=(), *, include_null=False):
    """Replace every nested field and container, then probe required/extra keys."""
    replacements = (7, True, [], {}) + ((None,) if include_null else ())
    if type(value) is dict:
        for key in value:
            path = (*prefix, key)
            for replacement in replacements:
                yield path, replacement
            if key in {"unit", "set", "query", "act", "predicate", "constant", "sort"}:
                yield path, "dangling"
            yield from _wire_mutations(value[key], path, include_null=include_null)
        for key in value:
            yield (*prefix, key), _MISSING
        yield (*prefix, "extra_wire_field"), "unexpected"
    elif type(value) is list:
        for index, item in enumerate(value):
            for replacement in replacements:
                yield (*prefix, index), replacement
            if prefix and prefix[-1] in {"premises", "args", "domain", "arguments"}:
                yield (*prefix, index), "dangling"
            yield from _wire_mutations(item, (*prefix, index), include_null=include_null)


_MISSING = object()


def _replace_wire(value, path, replacement):
    result = copy.deepcopy(value)
    parent = result
    for key in path[:-1]:
        parent = parent[key]
    if replacement is _MISSING:
        del parent[path[-1]]
    else:
        parent[path[-1]] = replacement
    return result


def test_generated_malformed_speech_wire_matches_lean(lean):
    env = F0()
    q = {"id": "q1", "premises": ["a"], "target": {"ast": U("reviewed", "atlas")}}
    set_ = reading_set("a", 1, "open", "asserted", U("reviewed", "atlas"))
    templates = [
        {"units": [unit("a", 0, "asserted", {"ast": U("reviewed", "atlas")}),
                   unit("f", 1, "question", {"question": {"mode": "follows", "query": "q1"}})],
         "queries": [q]},
        {"units": [unit("a", 0, "asserted", {"ast": U("reviewed", "atlas")}),
                   unit("c", 1, "instruction", command("require", "click_required", ["check"]))]},
        {"units": [unit("a", 0, "asserted"), unit("r", 1, "question",
                   {"question": {"mode": "reading", "set": "rs", "version": 1}},
                   {"open": ["intended-reading.r"]})], "reading_sets": [{**set_, "id": "rs"}]},
        {"units": [unit("b", 0, "binding", {"binding": {"phrase": "the knob", "constant": "check"}}),
                   unit("w", 1, "question", which("which_one"))]},
    ]
    cases = []
    for index, document in enumerate(templates):
        for path, replacement in _wire_mutations(document):
            mutated = _replace_wire(document, path, replacement)
            cases.append((f"doc{index}:{path}:{replacement!r}", env, mutated, path))
    for path, replacement in _wire_mutations(env["speech_acts"]):
        changed = copy.deepcopy(env)
        changed["speech_acts"] = _replace_wire(env["speech_acts"], path, replacement)
        cases.append((f"scope:{path}:{replacement!r}", changed, {"units": []}, ("scope", *path)))
    mismatches = []
    for start in range(0, len(cases), 40):
        batch = cases[start:start + 40]
        try:
            results = run([{"id": str(start + i), "kind": "speech-elaborate", "environment": e,
                            "document": d} for i, (_, e, d, _) in enumerate(batch)])
        except Exception as error:
            bad = []
            for name, e, d, _ in batch:
                try:
                    run([{"id": "one", "kind": "speech-elaborate", "environment": e, "document": d}])
                except Exception:
                    bad.append(name)
            raise AssertionError(bad) from error
        for (name, e, d, path), result in zip(batch, results, strict=True):
            try:
                if "units" in d:
                    core(e, d)
                else:
                    raise VEError("missing units")
                py_error = None
            except VEError as error:
                py_error = _diagnostic(error)
            except Exception as error:
                py_error = f"CRASH {type(error).__name__}: {error}"
            le_error = result.get("error")
            # The core is a typed projection. W2 owns envelope fields such as spans,
            # meaning, support and unknown keys; those are checked by SpeechSource.
            # Unit content is decoded by this route too. W2 owns the enclosing
            # span, meaning, support and unknown unit fields.
            route_field = (path[0] in ("scope", "queries", "reading_sets")
                           or len(path) >= 3 and path[0] == "units" and path[2] == "content")
            if py_error and py_error.startswith("CRASH") or route_field and py_error != le_error:
                mismatches.append((name, py_error, le_error))
    assert not mismatches, "\n".join(map(str, mismatches))


def test_generated_fence_equivalence_for_accepted_wordings(lean, tmp_path):
    env = F0()
    env["vocabulary"]["predicates"]["reviewed"]["verbalisation"] = "{0} is reviewed"
    corpus = ["Click check.", "Do not click check.", "Open the desk.",
              "Is atlas reviewed?", "Which one of atlas and beacon is reviewed?",
              "Which of atlas and beacon are reviewed?"]
    for index, wording in enumerate(corpus):
        content, kind = parse_speech(Environment(env), wording, env["speech_acts"])
        tagged = {"command" if kind == "instruction" else "question": content}
        for history in (False, True):
            uid = f"u{index}"
            sets = ([{**reading_set(uid, 1, "authored", kind, tagged), "id": f"rs{index}"}]
                    if history else [])
            unit_ = unit(uid, 0, kind, tagged)
            units, (plain, fenced) = _fenced_pair(
                tmp_path, f"generated-{index}-{history}", env, [wording + "\n"], [unit_], uid,
                reading_sets=sets)
            a, b = load_speech_document(plain).document, load_speech_document(fenced).document
            le = elaborate(env, {"units": units, "reading_sets": sets})
            assert a.scope == b.scope
            assert a.env.environment_id == b.env.environment_id == le["environment_id"]
            assert a.meaning_ids == b.meaning_ids
            assert [_to_data(f) for f in a.premises()] == [_to_data(f) for f in b.premises()] == le["premises"]
            assert [c.unit for c in a.commands if c.active] == [c.unit for c in b.commands if c.active] == \
                [c["unit"] for c in le["commands"]]
            assert [q.unit for q in a.questions] == [q.unit for q in b.questions] == \
                [q["unit"] for q in le["questions"]]


def test_generated_source_wire_never_crashes():
    env = F0()
    env["vocabulary"]["predicates"]["reviewed"]["verbalisation"] = "{0} is reviewed"
    source = b"Is atlas reviewed?\n"
    base = {"format": "ve-document@2", "environment": env,
            "units": [{**unit("q", 0, "question", polar(U("reviewed", "atlas"))),
                       "span": [0, len(source)]}],
            "open_terms": [], "reading_sets": [], "narrowings": [], "weights": [],
            "queries": [], "answers": [], "compliance": []}
    query_source = b"Atlas is reviewed.\nDoes it follow from these premises that atlas is reviewed?\n"
    split = len(b"Atlas is reviewed.\n")
    queried = {**base, "units": [
        {**unit("a", 0, "asserted", {"ast": U("reviewed", "atlas")}), "span": [0, split]},
        {**unit("f", 0, "question", {"question": {"mode": "follows", "query": "q1"}}),
         "span": [split, len(query_source)]}],
        "queries": [{"id": "q1", "premises": ["a"], "target": {"ast": U("reviewed", "atlas")}}]}
    reading_source = b"Click check.\nWhich reading did you mean?\n"
    split = len(b"Click check.\n")
    term = {"name": "intended-reading.r", "arguments": ["rs"], "version": 1, "decided_by": "alice",
            "jurisdiction": "t1", "necessary": [], "sufficient": [], "precedents": [],
            "factors": ["necessary: at least one nomination of a candidate of rs at version 1 by alice",
                        "sufficient: exactly one nomination of a candidate of rs at version 1 by alice"]}
    reading = {**base, "units": [
        {**unit("x", 0, "instruction", command("require", "click_required", ["check"])),
         "span": [0, split]},
        {**unit("r", 0, "question", {"question": {"mode": "reading", "set": "rs", "version": 1}},
                {"open": ["intended-reading.r"]}), "span": [split, len(reading_source)]}],
        "open_terms": [term],
        "reading_sets": [{**reading_set("x", 1, "open", "instruction",
                                       command("require", "click_required", ["check"])), "id": "rs"}]}
    alternate = copy.deepcopy(reading)
    candidates = alternate["reading_sets"][0]["readings"]
    candidates[0]["admission"]["distinguishing_models"] = {"other": "m1"}
    candidates.append({**copy.deepcopy(candidates[0]), "id": "other",
                       "admission": {"who": "author", "why": "other possible reading",
                                     "distinguishing_models": {"r": "m2"}}})
    alternate["reading_sets"][0]["models"] = {"m1": {}, "m2": {}}
    ordinary_source = b"X"
    ordinary = {**base, "units": [{**unit("a", 0, "asserted"), "span": [0, 1]}],
                "reading_sets": [{**reading_set("a", 1, "open", "asserted", None), "id": "rs"}]}
    for metadata, body in ((base, source), (queried, query_source),
                           (reading, reading_source), (alternate, reading_source),
                           (ordinary, ordinary_source)):
        SpeechSource(metadata, body, {})
        paths = [(path, replacement) for path, replacement in _wire_mutations(metadata, include_null=True)
                 if path[0] != "environment" or path[1:2] == ("speech_acts",) or len(path) == 1]
        for path, replacement in paths:
            changed = _replace_wire(metadata, path, replacement)
            try:
                SpeechSource(changed, body, {})
            except VEError:
                pass
            except Exception as error:
                pytest.fail(f"uncaught {type(error).__name__} at {path}: {error}")


def test_answer_records_validate_nested_model_and_list_tokens():
    env = F0()
    env["vocabulary"]["predicates"]["reviewed"]["verbalisation"] = "{0} is reviewed"
    lines = [b"Is atlas reviewed?\n", b"Which of atlas and beacon are reviewed?\n"]
    source = b"".join(lines)
    units = [
        {**unit("p", 0, "question", polar(U("reviewed", "atlas"))), "span": [0, len(lines[0])]},
        {**unit("a", 0, "question", which("which_all")), "span": [len(lines[0]), len(source)]},
    ]
    base_model = model(reviewed=[["atlas"]])
    answers = [
        {"question": "p", "by": "checker", "support": "model", "answer": "yes",
         "evidence": {"model": base_model}},
        {"question": "a", "by": "checker", "support": "model", "answer": {"all": ["atlas"]},
         "evidence": {"model": base_model}},
    ]
    meta = {"format": "ve-document@2", "environment": env, "units": units, "answers": answers}
    assert len(SpeechSource(meta, source, {}).answer_lines) == 2
    for index, field, value, diagnostic in ((0, "evidence", {"model": 7}, "InvalidModel"),
                                            (1, "answer", {"all": [[]]}, "AnswerOutsideDomain")):
        changed = copy.deepcopy(meta)
        changed["answers"][index][field] = value
        with pytest.raises(VEError) as raised:
            SpeechSource(changed, source, {})
        assert _diagnostic(raised.value).startswith(diagnostic)
    for path, replacement in _wire_mutations(answers, ("answers",), include_null=True):
        if len(path) < 2:
            continue
        changed = _replace_wire(meta, path, replacement)
        try:
            SpeechSource(changed, source, {})
        except VEError:
            pass
        except Exception as error:
            pytest.fail(f"uncaught {type(error).__name__} at {path}: {error}")
