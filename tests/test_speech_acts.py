"""Deterministic experimental speech-act core fixtures (no trusted route)."""
from copy import deepcopy
import json

import pytest

from ve.ast import Binary, Const, Eq, Not, Unary, Var, _to_data
from ve.environment import Environment
from ve.errors import VEError
from ve.profiles import LANGUAGE, SPEC_REVISION
from ve.speech_acts import SpeechDocument, combine
from ve.speech_english import parse_speech
from ve.speech_document import load_speech_document
from ve.entailment import prove_entailment


def environment(*, task="t1", addressee="alice", definite=True):
    scope = {"task": task}
    if addressee:
        scope["addressee"] = {"sort": "user", "constant": addressee}
    if definite:
        scope["definites"] = {"the token": "token1", "the desk": "desk1"}
    return Environment({
        "language": LANGUAGE, "spec_revision": SPEC_REVISION,
        "profiles": ["norms@0", "relational-fol@0", "speech-acts@0"],
        "speech_acts": scope,
        "vocabulary": {
            "sorts": {s: {"description": s, "verbalisation": {"singular": s, "plural": s + "s"}}
                      for s in ("user", "token", "desk", "service", "query")},
            "predicates": {
                "share_permitted": {"arguments": ["user", "token"], "description": "share",
                                    "regulated": {"role": "permission", "default": "allow", "act": "{0} share {1}"}},
                "open_required": {"arguments": ["user", "desk"], "description": "open",
                                  "regulated": {"role": "obligation", "default": "deny", "act": "{0} open {1}",
                                                "permission": "open_permitted"}},
                "open_permitted": {"arguments": ["user", "desk"], "description": "open",
                                   "regulated": {"role": "permission", "default": "allow", "act": "{0} open {1}"}},
                "reviewed": {"arguments": ["service"], "description": "reviewed",
                             "verbalisation": "{0} is reviewed"},
            },
            "constants": {name: {"sort": sort, "description": name} for name, sort in {
                "alice": "user", "bob": "user", "token1": "token", "desk1": "desk",
                "atlas": "service", "beacon": "service", "q1": "query"}.items()},
        },
    })


def unit(uid, kind, content, source=None):
    return {"id": uid, "kind": kind, "meaning": "specified", "support": "none",
            "content": content, **({"source": source} if source else {})}


def command(uid, force, act, arg, source=None):
    return unit(uid, "instruction", {"command": {"force": force, "act": act,
                                     "args": [arg], "guard": ["top"]}}, source)


def question(uid, mode, body, domain=(), source=None):
    content = {"mode": mode, "body": body}
    if domain:
        content.update({"sort": "service", "domain": list(domain)})
    return unit(uid, "question", {"question": content}, source)


def test_scope_identity_and_profile_gate():
    a = environment()
    assert Environment(a.to_dict()).environment_id == a.environment_id
    assert environment(task="t2").environment_id != a.environment_id
    assert environment(addressee="bob").environment_id != a.environment_id
    assert environment(definite=False).environment_id != a.environment_id
    raw = a.to_dict()
    raw["profiles"].remove("norms@0")
    with pytest.raises(VEError, match="speech-acts@0 requires norms@0"):
        Environment(raw)
    raw = a.to_dict()
    raw["profiles"].insert(0, "closure@0")
    with pytest.raises(VEError, match="speech-acts@0 with closure@0"):
        Environment(raw)


def test_prohibition_is_permission_negative_and_quoted_is_dormant():
    env = environment()
    active = command("u1", "forbid", "share_permitted", "token1", "Do not share the token.")
    quoted = deepcopy(active)
    quoted["id"] = "u2"
    quoted["kind"] = ["attributed", "manual", "says", "instruction"]
    quoted.pop("source")
    doc = SpeechDocument(env, [active, quoted])
    assert len(doc.policy.rules) == 1
    rule = doc.policy.rules[0]
    assert rule.name == "cmd-u1" and rule.sign is False and rule.predicate == "share_permitted"
    assert rule.guard.left.left == Eq(Var(1), Const("alice"))
    assert rule.guard.left.right == Eq(Var(0), Const("token1"))
    assert doc.premises() == SpeechDocument(env, [active]).premises()
    bad = command("u1", "forbid", "open_required", "desk1")
    with pytest.raises(VEError, match="MissingPermissionRole"):
        SpeechDocument(env, [bad])
    bad["content"]["command"]["force"] = "permit"
    with pytest.raises(VEError, match="InvalidInput: force"):
        SpeechDocument(env, [bad])


def test_scope_combination_and_conflict_policy_shape():
    yes = command("u1", "require", "open_required", "desk1", "Open the desk.")
    no = command("u2", "forbid", "open_permitted", "desk1", "Do not open the desk.")
    a = SpeechDocument(environment(task="ta"), [yes])
    b = SpeechDocument(environment(task="tb"), [no])
    with pytest.raises(VEError, match="ScopeMismatch: ta, tb"):
        combine(a, b)
    both = SpeechDocument(environment(), [yes, no])
    assert [r.name for r in both.policy.rules] == ["cmd-u1", "cmd-u2"]
    assert [r.sign for r in both.policy.rules] == [True, False]


def test_questions_presuppositions_and_complete_lists():
    env = environment()
    body = ["unary", "reviewed", ["var", 0]]
    one = question("u1", "which_one", body, ("atlas", "beacon"),
                   "Which one of atlas and beacon is reviewed?")
    all_ = question("u2", "which_all", body, ("atlas", "beacon"),
                    "Which of atlas and beacon are reviewed?")
    polar = question("u3", "polar", ["unary", "reviewed", ["const", "atlas"]],
                     source="Is atlas reviewed?")
    doc = SpeechDocument(env, [one, all_, polar])
    assert doc.presupposition(doc.questions[0]) != doc.presupposition(doc.questions[1])
    assert "reviewed" in repr(doc.correct(doc.questions[1], ()))
    assert doc.correct(doc.questions[2], "no") == Not(Unary("reviewed", Const("atlas")))
    assert doc.premises() == SpeechDocument(env, []).premises()
    wrong = deepcopy(one)
    wrong["content"]["question"]["mode"] = "which_all"
    with pytest.raises(VEError, match="ModeMismatch: u1"):
        SpeechDocument(env, [wrong])


def test_english_rejects_unscoped_modes_and_coordination():
    env = environment()
    assert parse_speech(env, "Open the desk.", env.speech_acts)[0]["act"] == "open_required"
    assert parse_speech(env, "Do not open the desk.", env.speech_acts)[0]["act"] == "open_permitted"
    with pytest.raises(VEError, match="ModalQuestion"):
        parse_speech(env, "Must alice open the desk?", env.speech_acts)
    with pytest.raises(VEError, match="OpenDomainWhich"):
        parse_speech(env, "Which services are reviewed?", env.speech_acts)
    with pytest.raises(VEError, match="PermissionNotCommand"):
        parse_speech(env, "You may open the desk.", env.speech_acts)


def test_answer_certificate_replay_and_dormant_question():
    env = environment()
    fact = unit("u1", "asserted", {"ast": ["unary", "reviewed", ["const", "atlas"]]})
    asked = question("u2", "polar", ["unary", "reviewed", ["const", "atlas"]],
                     source="Is atlas reviewed?")
    doc = SpeechDocument(env, [fact, asked])
    q = doc.questions[0]
    target = doc.correct(q, "yes")
    from ve.ast import And
    proof = prove_entailment(env, doc._caller_premises(), And(doc.presupposition(q), target))
    assert proof.status == "Found"
    assert doc.check_answer_certificate(q, "yes", proof.certificate)["status"] == "supported"
    with pytest.raises(VEError, match="AnswerMismatch: u2"):
        doc.check_answer_certificate(q, "no", proof.certificate)
    assert doc.premises() == SpeechDocument(env, [fact]).premises()


def test_query_pinning_and_stale_proof_task_identity():
    env = environment()
    fact = unit("u1", "asserted", {"ast": ["unary", "reviewed", ["const", "atlas"]]})
    task = command("u2", "require", "open_required", "desk1")
    # A consequence question pins exactly the earlier asserted premise.
    question_unit = unit("u3", "question", {"question": {"mode": "follows", "query": "q1"}})
    query = {"id": "q1", "premises": ["u1"],
             "target": {"ast": ["unary", "reviewed", ["const", "atlas"]]}}
    doc = SpeechDocument(env, [fact, task, question_unit], [query])
    assert "TrivialQuery: u3" in doc.warnings
    proof = prove_entailment(env, doc._caller_premises("q1"), doc.queries["q1"].target)
    assert proof.status == "Found"
    assert doc.check_consequence_certificate("q1", proof.certificate)["status"] == "follows"
    changed = deepcopy(query)
    changed["target"] = {"ast": ["unary", "reviewed", ["const", "beacon"]]}
    retargeted = SpeechDocument(env, [fact, task, question_unit], [changed])
    with pytest.raises(VEError, match="QueryMismatch: q1"):
        retargeted.check_consequence_certificate("q1", proof.certificate)
    changed = deepcopy(query)
    changed["premises"] = ["u1", "u3"]
    with pytest.raises(VEError, match="QueryMismatch: u3"):
        SpeechDocument(env, [fact, task, question_unit], [changed])


def test_v2_source_identity_partition_and_coverage(tmp_path):
    env = environment()
    source = "Open the desk.\nHeading\n"
    end = len("Open the desk.\n".encode())
    meta = {"format": "ve-document@2", "environment": env.to_dict(),
            "units": [
                {**command("u1", "require", "open_required", "desk1"), "span": [0, end]},
                {"id": "u2", "span": [end, len(source.encode())], "kind": "meta",
                 "meaning": {"unformalised": "heading"}, "support": "none"}],
            "queries": [], "reading_sets": []}
    path = tmp_path / "speech.ve.md"
    def save(metadata):
        path.write_text("---\n" + json.dumps(metadata) + "\n---\n" + source)
        return load_speech_document(path)
    first = save(meta)
    assert first.document_id == save(deepcopy(meta)).document_id
    assert first.coverage()["bytes_by_class"] == {"C": end, "U": len(source.encode()) - end}
    assert [r.name for r in first.document.policy.rules] == ["cmd-u1"]
    weighted = deepcopy(meta)
    weighted["weights"] = []
    assert save(weighted).document_id == first.document_id
    changed = deepcopy(meta)
    changed["environment"]["speech_acts"]["task"] = "t2"
    assert save(changed).document_id != first.document_id
    malformed = deepcopy(meta)
    malformed["reading_sets"] = [1]
    with pytest.raises(VEError, match="invalid reading set"):
        save(malformed)
    reading = {"id": "r1", "kind": "instruction", "meaning_id": "candidate",
               "content": {"command": {"force": "require", "act": "open_required",
                                       "args": ["desk1"]}},
               "admission": {"who": "author", "why": "This is the intended command.",
                             "distinguishing_models": {}}}
    wrong_owner = deepcopy(meta)
    wrong_owner["reading_sets"] = [
        {"id": "rs1", "unit": "u1", "version": 1, "status": "open", "readings": [reading]},
        {"id": "rs1", "unit": "u2", "version": 2, "status": "open", "readings": [reading]},
    ]
    with pytest.raises(VEError, match="versions must keep their unit"):
        save(wrong_owner)
    path.write_text('---\n{"format":"ve-document@2","format":"ve-document@2"}\n---\n' + source)
    with pytest.raises(VEError, match="invalid JSON front matter"):
        load_speech_document(path)


def test_model_answer_scope_and_presupposition_failure():
    env = environment()
    polar = question("u1", "polar", ["unary", "reviewed", ["const", "atlas"]],
                     source="Is atlas reviewed?")
    one = question("u2", "which_one", ["unary", "reviewed", ["var", 0]],
                   ("atlas", "beacon"), "Which one of atlas and beacon is reviewed?")
    doc = SpeechDocument(env, [polar, one])
    base = doc.policy.base_environment()
    wire = {"complete": True,
            "domains": {s: [s + "0"] for s in base.sorts},
            "constants": {name: sort + "0" for name, entry in base.constants.items()
                          if (sort := entry.sort)},
            "relations": {name: [] for name in base.predicates}}
    wire["relations"]["reviewed"] = [["service0"]]
    evaluated = doc.evaluate_answer_model(doc.questions[0], "yes", wire)
    assert evaluated["status"] == "evaluated" and evaluated["scope"] == "this model only"
    # atlas and beacon alias the same service entity in this model, so the
    # single-choice presupposition fails, regardless of the nominated token.
    assert doc.evaluate_answer_model(doc.questions[1], "atlas", wire)["status"] == "PRESUPPOSITION-FAILED"
    wire["relations"]["open_required"] = []  # A supplied regulated table is never accepted.
    with pytest.raises(VEError):
        doc.complete_model(wire)


def test_v2_answer_record_replays_certificate_without_new_premise(tmp_path):
    env = environment()
    source = "atlas is reviewed.\nIs atlas reviewed?\n"
    boundary = len("atlas is reviewed.\n".encode())
    fact = {**unit("u1", "asserted", {"ast": ["unary", "reviewed", ["const", "atlas"]]}),
            "span": [0, boundary]}
    asked = {**question("u2", "polar", ["unary", "reviewed", ["const", "atlas"]]),
             "span": [boundary, len(source.encode())]}
    core = SpeechDocument(env, [fact, {**asked, "source": "Is atlas reviewed?"}])
    q = core.questions[0]
    from ve.ast import And
    proof = prove_entailment(env, core._caller_premises(),
                             And(core.presupposition(q), core.correct(q, "yes")))
    assert proof.status == "Found"
    meta = {"format": "ve-document@2", "environment": env.to_dict(), "units": [fact, asked],
            "answers": [{"question": "u2", "by": "checker", "support": "certificate",
                         "answer": "yes", "evidence": {"certificate": proof.certificate}}]}
    path = tmp_path / "answered.ve.md"
    def save(metadata):
        path.write_text("---\n" + json.dumps(metadata) + "\n---\n" + source)
        return load_speech_document(path)
    loaded = save(meta)
    assert loaded.answer_lines[0]["status"] == "supported"
    assert loaded.document.premises() == core.premises()
    forged = deepcopy(meta)
    forged["answers"][0]["answer"] = "no"
    with pytest.raises(VEError, match="AnswerMismatch: u2"):
        save(forged)


def test_proof_task_identity_binds_query_target_and_certificate():
    raw = environment().to_dict()
    raw["vocabulary"]["predicates"].update({
        "submit_required": {"arguments": ["user", "query"], "description": "submit",
                            "regulated": {"role": "obligation", "default": "deny",
                                          "act": "{0} submit a proof of {1}",
                                          "permission": "submit_permitted"}},
        "submit_permitted": {"arguments": ["user", "query"], "description": "submit",
                             "regulated": {"role": "permission", "default": "allow",
                                           "act": "{0} submit a proof of {1}"}},
        "done_submit": {"arguments": ["user", "query"], "description": "submitted"},
    })
    env = Environment(raw)
    fact = unit("u1", "asserted", {"ast": ["unary", "reviewed", ["const", "atlas"]]})
    task = command("u2", "require", "submit_required", "q1",
                   "Prove that atlas is reviewed using these premises.")
    query = {"id": "q1", "premises": ["u1"],
             "target": {"ast": ["unary", "reviewed", ["const", "atlas"]]}}
    doc = SpeechDocument(env, [fact, task], [query])
    proof = prove_entailment(env, doc._caller_premises("q1"), doc.queries["q1"].target)
    assert proof.status == "Found"
    before = doc.premises()
    assert doc.check_consequence_certificate("q1", proof.certificate)["status"] == "follows"
    assert doc.premises() == before
    changed = deepcopy(query)
    changed["target"] = {"ast": ["unary", "reviewed", ["const", "beacon"]]}
    task_without_wording = deepcopy(task)
    task_without_wording.pop("source")
    retargeted = SpeechDocument(env, [fact, task_without_wording], [changed])
    assert doc.meaning_ids["u2"] != retargeted.meaning_ids["u2"]
    with pytest.raises(VEError, match="QueryMismatch: q1"):
        retargeted.check_consequence_certificate("q1", proof.certificate)
