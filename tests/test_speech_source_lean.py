"""The Lean decoded-source wrapper (`speech-source`, docs/spec/speech-acts.md 8.5) against Python's `SpeechSource`.

Batch 11a of docs/LEAN-FIRST-PLAN.md (on design/lean-first): Lean gains the wrapper, its coverage projection and the
answer, nomination and compliance records; no caller is switched. Every template document must give the same
document id, source id, environment id, coverage tables, record lines and compliance lines in both checkers, and
every single-fault mutant of every template the same verdict. Where both reject with different texts the case must
fall in one of the named wording classes below, and their count is pinned so the baseline cannot grow. The Python
prover is only an untrusted certificate search; Lean replays every certificate.
"""
from __future__ import annotations

import copy
import json

import pytest

from test_speech_acts_conformance import _MISSING, _replace_wire, _wire_mutations, core, reading_set
from test_speech_acts_lean import F0, ROOT, U, command, lean, model, polar, run, unit  # noqa: F401  (lean: fixture)
from ve.ast import And, Not, Top, _to_data, formula_from_data
from ve.entailment import prove_entailment
from ve.environment import Environment
from ve.errors import VEError
from ve.identity import meaning_id
from ve.speech_acts import SpeechDocument
from ve.speech_document import SpeechSource

NON_ASCII = "InvalidInput: non-ASCII speech wording"


def spans(lines):
    positions = [0]
    for line in lines:
        positions.append(positions[-1] + len(line.encode()))
    return [positions[i:i + 2] for i in range(len(lines))]


def placed(lines, units):
    return [{**u, "span": s} for u, s in zip(units, spans(lines))]


def base_env():
    env = F0()
    predicates = env["vocabulary"]["predicates"]
    predicates["reviewed"]["verbalisation"] = "{0} is reviewed"
    predicates["cat"]["verbalisation"] = "{0} is a cat"
    return env


def intended(unit_id, set_id="rs", version=1, by="alice", task="t1"):
    wording = f"a candidate of {set_id} at version {version} by {by}"
    return {"name": f"intended-reading.{unit_id}", "arguments": [set_id], "version": version, "decided_by": by,
            "jurisdiction": task, "necessary": [], "sufficient": [], "precedents": [],
            "factors": [f"necessary: at least one nomination of {wording}",
                        f"sufficient: exactly one nomination of {wording}"]}


def two_commands(unit_id):
    """An open speech set with two command candidates and distinguishing model ids (W2's shape)."""
    first = command("require", "click_required", ["check"])
    second = command("forbid", "share_permitted", ["token1"])
    readings = []
    for rid, content, other, model_id in (("r1", first, "r2", "m1"), ("r2", second, "r1", "m2")):
        readings.append({"id": rid, "kind": "instruction", "meaning_id": "candidate", "content": content,
                         "admission": {"who": "author", "why": "possible reading",
                                       "distinguishing_models": {other: model_id}}})
    return {"id": "rs", "unit": unit_id, "version": 1, "status": "open", "readings": readings,
            "models": {"m1": {}, "m2": {}}}


def certified(env):
    """Asserted facts, a polar answer, a follows judgment and a proof task, each with a found certificate."""
    lines = ["Atlas is reviewed.\n", "Tom is a cat.\n", "Is atlas reviewed?\n",
             "Does it follow from these premises that tom is a cat?\n",
             "Prove that tom is a cat using these premises.\n", "Beacon is reviewed.\n"]
    # The last assertion is in premises(D) but not in the pinned Pi_q of the earlier query (1.4).
    units = placed(lines, [
        unit("a", 0, "asserted", {"ast": U("reviewed", "atlas")}),
        unit("b", 0, "asserted", {"ast": U("cat", "tom")}),
        unit("p", 0, "question", polar(U("reviewed", "atlas"))),
        unit("f", 0, "question", {"question": {"mode": "follows", "query": "q1"}}),
        unit("t", 0, "instruction", command("require", "submit_required", ["q1"])),
        unit("z", 0, "asserted", {"ast": U("reviewed", "beacon")})])
    queries = [{"id": "q1", "premises": ["a", "b"], "target": {"ast": U("cat", "tom")}}]
    py = core(env, {"units": units, "queries": queries})
    question = py.questions[0]
    answer = prove_entailment(py.env, py._caller_premises(), And(py.presupposition(question),
                                                                 py.correct(question, "yes")))
    follows = prove_entailment(py.env, py._caller_premises("q1"), py.queries["q1"].target)
    assert answer.certificate is not None and follows.certificate is not None
    metadata = {"format": "ve-document@2", "environment": env, "units": units, "queries": queries,
                "answers": [{"question": "p", "by": "checker", "support": "certificate", "answer": "yes",
                             "evidence": {"certificate": answer.certificate}},
                            {"question": "f", "by": "checker", "support": "certificate", "judgment": "follows",
                             "evidence": {"certificate": follows.certificate}}],
                "compliance": [{"command": "t", "evidence": {"certificate": follows.certificate}}]}
    return metadata, "".join(lines)


def templates():
    """(name, metadata, source) documents both checkers accept, one per wrapper feature."""
    env = base_env()
    out = []
    polar_source = "Is atlas reviewed?\n"
    out.append(("polar", {"format": "ve-document@2", "environment": env,
                          "units": placed([polar_source], [unit("q", 0, "question", polar(U("reviewed", "atlas")))]),
                          "open_terms": [], "reading_sets": [], "narrowings": [], "weights": [],
                          "queries": [], "answers": [], "compliance": []}, polar_source))
    lines = ["Click check.\n", "Which reading did you mean?\n"]
    out.append(("reading", {"format": "ve-document@2", "environment": env, "units": placed(lines, [
        unit("x", 0, "instruction", command("require", "click_required", ["check"])),
        unit("r", 0, "question", {"question": {"mode": "reading", "set": "rs", "version": 1}},
             {"open": ["intended-reading.r"]})]),
        "open_terms": [intended("r")], "reading_sets": [two_commands("x")],
        "narrowings": [{"id": "n1", "set": "rs", "version": 1, "keeps": ["r1"], "by": "alice",
                        "reason_spans": ["r"]}]}, "".join(lines)))
    lines = ["In this task, you are alice.\n", "Click check.\n", "Is atlas reviewed?\n"]
    unbound = copy.deepcopy(env)
    unbound["speech_acts"].pop("addressee")
    out.append(("answered", {"format": "ve-document@2", "environment": unbound, "units": placed(lines, [
        unit("u0", 0, "binding", {"binding": {"you": "alice"}}),
        unit("u1", 0, "instruction", command("require", "click_required", ["check"])),
        unit("u2", 0, "question", polar(U("reviewed", "atlas")))]),
        "answers": [{"question": "u2", "by": "checker", "support": "model", "answer": "yes",
                     "evidence": {"model": model(reviewed=[["atlas"]])}}]}, "".join(lines)))
    lines = ["Click check.\n"]
    out.append(("chosen", {"format": "ve-document@2", "environment": env, "units": placed(lines, [
        unit("c", 0, "asserted", {"ast": U("reviewed", "atlas")})]),
        "reading_sets": [{**reading_set("c", 1, "authored", "instruction",
                                        command("require", "click_required", ["check"]))}]}, "".join(lines)))
    formula = U("reviewed", "atlas")
    mid = meaning_id(Environment(env), formula_from_data(Environment(env), formula))
    ordinary = reading_set("a", 1, "open", "asserted", formula)
    ordinary["readings"][0]["meaning_id"] = mid
    lines = ["Atlas is reviewed.\n", "It depends.\n", "The desk is fine.\n", "Atlas is clear.\n", "Heading\n"]
    clear = {"name": "clear", "arguments": [], "decided_by": "alice", "jurisdiction": "t1", "version": 1,
             "necessary": [], "sufficient": [], "factors": ["plain words"], "precedents": []}
    out.append(("meanings", {"format": "ve-document@2", "environment": env, "units": placed(lines, [
        unit("a", 0, "asserted"),
        unit("d", 0, "exposition", meaning={"unformalised": "vague"}),
        unit("k", 0, "asserted", {"ast": U("reviewed", "beacon")}, meaning={"contextual": "desk state"}),
        unit("o", 0, "exposition", meaning={"open": ["clear"]}),
        unit("h", 0, "exposition", meaning={"contextual": "a heading"})]),
        "open_terms": [clear], "reading_sets": [ordinary], "weights": []}, "".join(lines)))
    lines = ["Atlas is reviewed. ", "Beacon is reviewed.\n"]
    mixed = {"id": "m", "span": [0, len("".join(lines).encode())], "status": "MIXED", "parts": [
        {**unit("m1", 0, "asserted", {"ast": U("reviewed", "atlas")}), "span": spans(lines)[0], "status": "CHECKED"},
        {**unit("m2", 0, "exposition", meaning={"contextual": "aside"}), "span": spans(lines)[1],
         "status": "LABELLED"}]}
    out.append(("mixed", {"format": "ve-document@2", "environment": env, "units": [mixed]}, "".join(lines)))
    metadata, source = certified(env)
    out.append(("certified", metadata, source))
    return out


def py_outcome(metadata, source, fences=None):
    try:
        s = SpeechSource(metadata, source.encode(), fences or {})
        return {"ok": True, "document_id": s.document_id, "source_id": s.source_id,
                "environment_id": s.document.env.environment_id, "coverage": s.coverage(),
                "answers": [(a["question"], a["status"]) for a in s.answer_lines],
                "compliance": [(c["command"], c["query"]) for c in s.compliance_lines],
                "meaning_ids": dict(sorted(s.document.meaning_ids.items()))}
    except VEError as exc:
        return {"ok": False, "error": str(exc)}
    except Exception as exc:  # a Python bug; only VEError may escape (build checklist 5)
        return {"ok": False, "error": f"CRASH {type(exc).__name__}"}


def lean_outcome(result):
    if result.get("status") != "ok":
        return {"ok": False, "error": result.get("error")}
    meaning_ids = {c["unit"]: c["meaning_id"] for c in result["commands"]}
    meaning_ids.update({q["unit"]: q["meaning_id"] for q in result["questions"]})
    return {"ok": True, "document_id": result["document_id"], "source_id": result["source_id"],
            "environment_id": result["environment_id"], "coverage": result["coverage"],
            "answers": [(a["question"], a.get("status", "follows")) for a in result["answers"]],
            "compliance": [(c["command"], c.get("query", c.get("unit"))) for c in result["compliance"]],
            "meaning_ids": dict(sorted(meaning_ids.items()))}


def source_case(index, metadata, source, fences=None, **extra):
    return {"id": str(index), "kind": "speech-source",
            "document": {"metadata": metadata, "source": source, "fences": fences or {}}, **extra}


def run_source(metadata, source, fences=None, **extra):
    [result] = run([source_case(0, metadata, source, fences, **extra)])
    return result


def comparable(py, le):
    """Python's meaning ids include binding, norm and formula units the Lean report does not list."""
    if py.get("ok") and le.get("ok"):
        py = {**py, "meaning_ids": {k: v for k, v in py["meaning_ids"].items() if k in le["meaning_ids"]}}
    return py, le


def test_templates_agree_with_python(lean):
    for name, metadata, source in templates():
        py, le = comparable(py_outcome(metadata, source), lean_outcome(run_source(metadata, source)))
        assert py["ok"], (name, py)
        assert py == le, name


def test_template_reports_cover_every_class_and_record(lean):
    by_name = {name: run_source(metadata, source) for name, metadata, source in templates()}
    classes = set()
    for result in by_name.values():
        assert result["status"] == "ok", result
        classes |= set(result["coverage"]["bytes_by_class"])
        total = sum(u["bytes"] for u in result["units"])
        assert sum(result["coverage"]["bytes_by_class"].values()) == total
        assert sum(result["coverage"]["bytes_by_status"].values()) == total
    assert classes == {"C", "L", "O", "R", "U"}
    meanings = {u["id"]: (u["status"], u["class"]) for u in by_name["meanings"]["units"]}
    assert meanings == {"a": ("OPEN", "R"), "d": ("UNFORMALISED", "U"), "k": ("LABELLED", "L"),
                        "o": ("OPEN", "O"), "h": ("LABELLED", "L")}
    assert {u["id"]: u.get("parent") for u in by_name["mixed"]["units"]} == {"m1": "m", "m2": "m"}
    certified = by_name["certified"]
    assert [a["line"] for a in certified["answers"]] == [
        "supported yes (certificate; premises: UNKNOWN (no premise-status evidence); vacuous: unknown)",
        "follows (certificate; premises: UNKNOWN (no premise-status evidence); vacuous: unknown)"]
    assert certified["compliance"] == [{"command": "t", "query": "q1", "line":
        "certificate: query q1 (premises: UNKNOWN (no premise-status evidence); vacuous: unknown)"}]
    assert certified["status_text"][2:] == [
        "questions: 2 answered (2 by certificate, 0 in a model), 0 presupposition failures, 0 unknown, 0 unanswered",
        "compliance: 1 of 1 commands with evidence (0 external, 1 certificates)"]
    assert by_name["reading"]["coverage"]["residual"] == {"open_terms": 1, "unresolved_sets": 1}


def wording_class(name, path, py_error, lean_error):
    """The named wording classes where both checkers reject with different texts (none is a verdict change)."""
    if py_error.startswith("CRASH "):
        return "python-crash"  # ve/document.py `_parts` raises TypeError on an unhashable part status
    if "evidence" in path and "model" in path:
        return "model-decoder"  # the shared finite-model decoder's texts (Bridge vs ve/model.py), batch 12
    if path == ("environment",):
        return "environment-decoder"  # the environment envelope's texts, batch 12
    if py_error.startswith("AnswerOutsideDomain: ") and lean_error.startswith("AnswerOutsideDomain: "):
        return "answer-repr"  # Python's repr of the stated answer; Lean writes its JSON (DRI answer 3)
    if path[:2] == ("environment", "speech_acts") and lean_error == "reading meaning id does not match content":
        # Order: the block edit both breaks the block and moves the environment id a W2 set's meaning id binds;
        # Python's environment decoder reports the first, Lean's W2 set check the second (spec 7's limitation).
        return "identity-order"
    if "parts" in path and lean_error == "MIXED parts must partition their parent span":
        # Order: Python's `_parts` is a generator and checks a part's span against the source before the next
        # part's start; `Loader.partsOf` checks the parent's partition first.
        return "mixed-part-order"
    if py_error.startswith("UnknownSymbol: ") and lean_error.startswith("QueryMismatch: "):
        # Order: a dangling proof-task argument also leaves its query record unasked; Python resolves the
        # argument at the unit, the Lean core regenerates the queries first (the core's own order).
        return "query-order"
    return None


# Pinned per class: a new wording difference, or a grown class, fails the test (the baseline must not grow).
WORDING_BASELINE = {"model-decoder": 171, "environment-decoder": 7, "answer-repr": 2, "identity-order": 2,
                    "mixed-part-order": 7, "python-crash": 4, "query-order": 1}


def mutants():
    for name, metadata, source in templates():
        for path, replacement in _wire_mutations(metadata):
            if path[0] == "environment" and not (path[1:2] == ("speech_acts",) or len(path) == 1):
                continue  # the environment's own decoders are batch 12's; its speech block is this route's
            if path[:2] in (("answers", 0), ("answers", 1), ("compliance", 0)) and "certificate" in path[3:4]:
                continue  # certificate internals are the certificate checker's own corpus
            yield name, path, _replace_wire(metadata, path, replacement), source


def test_single_fault_mutants_agree_with_python(lean):
    cases = list(mutants())
    results = run([source_case(i, m, s) for i, (_, _, m, s) in enumerate(cases)])
    assert len(results) == len(cases)
    classes, unexplained = {}, []
    for (name, path, metadata, source), result in zip(cases, results):
        py, le = comparable(py_outcome(metadata, source), lean_outcome(result))
        if py == le:
            continue
        assert py["ok"] == le["ok"], (name, path, py, le)  # never a verdict difference
        assert not py["ok"], (name, path, py, le)  # accepted documents agree on every reported field
        label = wording_class(name, path, py["error"], le["error"])
        if label is None:
            unexplained.append((name, path, py["error"], le["error"]))
        else:
            classes[label] = classes.get(label, 0) + 1
    assert unexplained == []
    assert all(classes.get(k, 0) <= v for k, v in WORDING_BASELINE.items()), classes
    assert set(classes) <= set(WORDING_BASELINE), classes


def test_two_fault_mutants_agree_on_the_verdict(lean):
    """Pairs of faults: both checkers reject (the first fault may differ, spec 7's known limitation)."""
    name, metadata, source = templates()[1]
    singles = [(p, r) for p, r in _wire_mutations(metadata)
               if p[0] not in ("environment",) and r is not _MISSING][:60]
    cases = []
    for (p1, r1), (p2, r2) in zip(singles, singles[1:]):
        try:
            changed = _replace_wire(_replace_wire(metadata, p1, r1), p2, r2)
        except (KeyError, IndexError, TypeError):
            continue
        cases.append(changed)
    results = run([source_case(i, m, source) for i, m in enumerate(cases)])
    for changed, result in zip(cases, results):
        assert py_outcome(changed, source)["ok"] == lean_outcome(result)["ok"]


@pytest.mark.parametrize("character", [" ", "’", "K", "İ", "\x85", "　"])
def test_non_ascii_wordings_are_rejected_in_both(lean, character):
    env = base_env()
    for text in (f"Is atlas{character}reviewed?\n", f"Is atlas reviewed?{character}\n"):
        metadata = {"format": "ve-document@2", "environment": env,
                    "units": placed([text], [unit("q", 0, "question", polar(U("reviewed", "atlas")))])}
        assert py_outcome(metadata, text) == lean_outcome(run_source(metadata, text)) == \
            {"ok": False, "error": NON_ASCII}


# Python's speech parser reads every instruction and question wording against its content (`_check_wordings`); that
# is the English layer (plan track E3), which Lean does not have, so a wording its parser cannot read is Python's
# rejection alone. Both agree on everything else.
@pytest.mark.parametrize("space", [" ", "\t", "\r", "\x0b", "\x0c", "  ", "\x1f", "\x7f"])
def test_ascii_spacing_and_controls_agree(lean, space, monkeypatch):
    env = base_env()
    text = f"Is atlas{space}reviewed?{space}\n"
    metadata = {"format": "ve-document@2", "environment": env,
                "units": placed([text], [unit("q", 0, "question", polar(U("reviewed", "atlas")))])}
    py, le = comparable(py_outcome(metadata, text), lean_outcome(run_source(metadata, text)))
    if le["ok"] and not py["ok"]:
        # Python's rejection is its English layer's: without the wording check it accepts, as Lean does.
        monkeypatch.setattr(SpeechDocument, "_check_wordings", lambda self: None)
        py = comparable(py_outcome(metadata, text), le)[0]
    assert py == le


def test_span_cutting_a_character_and_partition(lean):
    env = base_env()
    text = "Is atlas reviewed?\n"
    metadata = {"format": "ve-document@2", "environment": env,
                "units": [{**unit("q", 0, "question", polar(U("reviewed", "atlas"))), "span": [0, len(text) - 1]}]}
    assert lean_outcome(run_source(metadata, text)) == py_outcome(metadata, text) == \
        {"ok": False, "error": "unit spans do not partition all source bytes"}
    wide = "Is atlas reviewed?é"
    metadata["units"][0]["span"] = [0, len(wide.encode()) - 1]
    assert lean_outcome(run_source(metadata, wide)) == py_outcome(metadata, wide) == \
        {"ok": False, "error": "unit span cuts a UTF-8 character"}


def test_fenced_english_is_not_implemented_and_never_accepted(lean):
    env = base_env()
    text = "Is atlas reviewed?\n"
    metadata = {"format": "ve-document@2", "environment": env,
                "units": [{**unit("q", 0, "question", {"fence": "q"}), "span": [0, len(text)], "surface": "english"}]}
    fences = {"q": "Is atlas reviewed?\n"}
    assert py_outcome(metadata, text, fences)["ok"]
    assert run_source(metadata, text, fences)["error"] == "NotImplemented: fenced English content"
    fences = {"q": "Is atlas reviewed ?\n"}
    assert run_source(metadata, text, fences)["error"] == NON_ASCII


def test_answer_records_replay_their_evidence(lean):
    env = base_env()
    metadata, source = certified(env)
    wrong = copy.deepcopy(metadata)
    wrong["answers"][0]["answer"] = "no"
    assert run_source(wrong, source)["error"] == py_outcome(wrong, source)["error"] == "AnswerMismatch: p"
    stale = copy.deepcopy(metadata)
    stale["compliance"][0]["evidence"]["certificate"]["conclusion_meaning_id"] = "0" * 64
    assert run_source(stale, source)["error"] == py_outcome(stale, source)["error"] == "QueryMismatch: q1"
    judged = copy.deepcopy(metadata)
    judged["answers"][1]["judgment"] = "gap"
    assert run_source(judged, source)["error"] == py_outcome(judged, source)["error"] == "InvalidInput: judgment"
    # A model refuting the stated answer is a mismatch; one refuting the presupposition is reported.
    answered = templates()[2][1:]
    refuted = copy.deepcopy(answered[0])
    refuted["answers"][0]["evidence"]["model"] = model()
    assert run_source(refuted, answered[1])["error"] == py_outcome(refuted, answered[1])["error"] == \
        "AnswerMismatch: u2"


def judged(env):
    """A follows question whose query does not follow (Pi_q is `reviewed(atlas)` only) and a polar question, the
    judgment record first: records keep the document's order (review 11a C1)."""
    lines = ["Atlas is reviewed.\n", "Does it follow from these premises that tom is a cat?\n", "Is atlas reviewed?\n"]
    units = placed(lines, [unit("a", 0, "asserted", {"ast": U("reviewed", "atlas")}),
                           unit("f", 0, "question", {"question": {"mode": "follows", "query": "q1"}}),
                           unit("p", 0, "question", polar(U("reviewed", "atlas")))])
    queries = [{"id": "q1", "premises": ["a"], "target": {"ast": U("cat", "tom")}}]
    gap = {"question": "f", "by": "checker", "support": "model", "judgment": "gap",
           "evidence": {"model": model(reviewed=[["atlas"]])}}
    answer = {"question": "p", "by": "checker", "support": "model", "answer": "yes",
              "evidence": {"model": model(reviewed=[["atlas"]])}}
    metadata = {"format": "ve-document@2", "environment": env, "units": units, "queries": queries,
                "answers": [gap, answer]}
    return metadata, "".join(lines)


def test_gap_judgment_records_replay_their_model(lean):
    """Review 11a B3: a model-backed `gap` record (3.3) is replayed as `speech-consequence` replays it, and the two
    entry points give the same judgment for the same document and model."""
    env = base_env()
    metadata, source = judged(env)
    result = run_source(metadata, source)
    assert result["status"] == "ok", result
    [gap, answer] = result["answers"]
    assert gap["question"] == "f" and gap["status"] == "gap" and gap["line"].startswith("gap (model ")
    assert answer["question"] == "p" and answer["line"].startswith("evaluated yes in model ")
    document = {"units": [{k: v for k, v in u.items() if k != "span"} | {"span": [i, i + 1]}
                          for i, u in enumerate(metadata["units"])], "queries": metadata["queries"]}
    [consequence] = run([{"id": "c", "kind": "speech-consequence", "environment": env, "document": document,
                          "query": "q1", "model": metadata["answers"][0]["evidence"]["model"],
                          "model_id": gap["line"][len("gap (model "):-1]}])
    assert consequence["judgment"] == gap["line"]
    assert result["status_text"][2] == \
        "questions: 2 answered (0 by certificate, 2 in a model), 0 presupposition failures, 0 unknown, 0 unanswered"
    # The model must satisfy Pi_q and falsify the target; the judgment must be the one its evidence supports.
    holds = copy.deepcopy(metadata)
    holds["answers"][0]["evidence"]["model"] = model(reviewed=[["atlas"]], cat=[["tom"]])
    assert run_source(holds, source)["error"] == "AnswerMismatch: f"
    unsatisfied = copy.deepcopy(metadata)
    unsatisfied["answers"][0]["evidence"]["model"] = model()
    assert run_source(unsatisfied, source)["error"].startswith("InvalidModel(premises)")
    for field, value in (("support", "certificate"), ("judgment", "refuted"), ("judgment", 7),
                         ("evidence", {"certificate": {}})):
        bad = copy.deepcopy(metadata)
        bad["answers"][0][field] = value
        assert run_source(bad, source)["error"] == "InvalidInput: judgment", (field, value)
    # Python does not replay gap records yet (it rejects them); Lean's answer is the specified one (3.3, 5.3).
    assert py_outcome(metadata, source)["error"] == "InvalidInput: judgment"


def done_document(env, done=("binary", "done_click", ["const", "alice"], ["const", "check"]), support="observation"):
    lines = ["Click check.\n", "Alice clicked check.\n"]
    units = placed(lines, [unit("u1", 0, "instruction", command("require", "click_required", ["check"])),
                           {**unit("d", 0, "asserted", {"ast": list(done)}), "support": support}])
    return {"format": "ve-document@2", "environment": env, "units": units,
            "compliance": [{"command": "u1", "evidence": {"unit": "d"}}]}, "".join(lines)


def test_external_compliance_names_an_asserted_done_unit(lean):
    """Review 11a B3: external compliance evidence (3.3, 5.4) is an asserted unit whose content is exactly the act's
    `done` fact at the command's bound constants, reported with that unit's own support kind."""
    env = base_env()
    metadata, source = done_document(env)
    result = run_source(metadata, source)
    assert result["status"] == "ok", result
    assert result["compliance"] == [{"command": "u1", "unit": "d", "line": "external: unit d (observation)"}]
    assert result["status_text"][3] == "compliance: 1 of 1 commands with evidence (1 external, 0 certificates)"
    for done in (("not", ["binary", "done_click", ["const", "alice"], ["const", "check"]]),  # not the fact
                 ("binary", "done_open", ["const", "alice"], ["const", "desk1"]),  # another act
                 ("unary", "reviewed", ["const", "atlas"])):
        changed, text = done_document(env, done)
        assert run_source(changed, text)["error"] == "InvalidInput: compliance record", done
    for evidence in ({"unit": "u1"}, {"unit": "nowhere"}, {"unit": 7}, {"unit": "d", "certificate": {}}):
        changed = copy.deepcopy(metadata)
        changed["compliance"][0]["evidence"] = evidence
        error = run_source(changed, source)["error"]
        assert error in ("InvalidInput: compliance record", "QueryMismatch: u1"), (evidence, error)
    # Python does not read external evidence yet (it rejects the record); Lean's answer is the specified one.
    assert py_outcome(metadata, source)["error"] == "QueryMismatch: u1"


def conditional(env):
    """The certified document with its polar answer recorded conditionally (3.3's `conditional: true`)."""
    metadata, source = certified(env)
    py = core(env, {"units": metadata["units"], "queries": metadata["queries"]})
    question = py.questions[0]
    found = prove_entailment(py.env, [*py._caller_premises(), py.presupposition(question)],
                             py.correct(question, "yes"))
    assert found.certificate is not None
    metadata = copy.deepcopy(metadata)
    metadata["answers"][0] = {**metadata["answers"][0], "conditional": True,
                              "evidence": {"certificate": found.certificate}}
    return metadata, source


# Every record kind of section 3.3 (and the two compliance kinds of 5.4), with a document whose record of that kind
# is valid and the report line it must give: an unimplemented branch fails here (review 11a B3's class).
RECORD_KINDS = {
    "answer certificate": (lambda env: certified(env), "answers", 0, "supported yes (certificate; "),
    "answer conditional": (conditional, "answers", 0, "supported yes given the presupposition (certificate; "),
    "answer model": (lambda env: templates()[2][1:], "answers", 0, "evaluated yes in model "),
    "judgment follows": (lambda env: certified(env), "answers", 1, "follows (certificate; "),
    "judgment gap": (judged, "answers", 0, "gap (model "),
    "nomination": (lambda env: nominated([{"question": "r", "by": "alice", "support": "testimony", "nominate": 0}]),
                   "nominations", 0, "0 by alice (testimony)"),
    "compliance certificate": (lambda env: certified(env), "compliance", 0, "certificate: query q1 ("),
    "compliance external": (done_document, "compliance", 0, "external: unit d (observation)"),
}


@pytest.mark.parametrize("kind", sorted(RECORD_KINDS))
def test_every_record_kind_is_replayed(lean, kind):
    build, key, index, line = RECORD_KINDS[kind]
    metadata, source = build(base_env())
    result = run_source(metadata, source)
    assert result["status"] == "ok", (kind, result)
    assert result[key][index]["line"].startswith(line), (kind, result[key])


def test_premise_status_evidence_comes_from_the_case(lean):
    env = base_env()
    metadata, source = certified(env)
    py = core(env, {"units": metadata["units"], "queries": metadata["queries"]})
    status = {"model": model(reviewed=[["atlas"], ["beacon"]], cat=[["tom"]])}
    result = run_source(metadata, source, premise_status={"answers": {"0": status, "1": status},
                                                          "compliance": {"0": status}})
    assert result["status"] == "ok", result
    assert [a["line"] for a in result["answers"]] == [
        "supported yes (certificate; premises: model m; vacuous: no)",
        "follows (certificate; premises: model m; vacuous: no)"]
    assert result["compliance"][0]["line"] == "certificate: query q1 (premises: model m; vacuous: no)"
    # Evidence that is no model of the checked list is rejected, never read as UNKNOWN.
    bad = {"model": model()}
    assert run_source(metadata, source, premise_status={"answers": {"0": bad}})["error"].startswith("InvalidModel")
    assert py.premises()  # the regenerated list the evidence is checked against is not empty


def nominated(nominations):
    name, metadata, source = templates()[1]
    metadata = copy.deepcopy(metadata)
    metadata["answers"] = nominations
    return metadata, source


def test_nominations_name_a_candidate_of_the_bound_set(lean):
    metadata, source = nominated([])
    [line] = run_source(metadata, source)["nominations"]
    assert line == {"question": "r", "line": "CLARIFICATION-OPEN (none)"}
    record = {"question": "r", "by": "alice", "support": "testimony", "nominate": 1}
    metadata, source = nominated([record])
    [line] = run_source(metadata, source)["nominations"]
    assert line == {"question": "r", "line": "1 by alice (testimony)",
                    "narrowing": {"set": "rs", "version": 1, "keeps": ["r2"], "by": "alice",
                                  "reason_spans": ["r"], "support": "testimony"}}
    metadata, source = nominated([record, {**record, "nominate": 0}])
    assert run_source(metadata, source)["nominations"][0]["line"] == "CLARIFICATION-OPEN (multiple)"
    metadata, source = nominated([record, record])
    assert run_source(metadata, source)["nominations"][0]["line"] == "1 by alice (testimony)"
    for index in (2, 64, "0", True, [0]):  # the restricted JSON input reads no negative or fractional number
        metadata, source = nominated([{**record, "nominate": index}])
        assert run_source(metadata, source)["error"] == "NominationOutsideSet: r"
    for bad in ({**record, "support": "certificate"}, {**record, "by": "Not a token"}, {**record, "extra": 1}):
        metadata, source = nominated([bad])
        assert run_source(metadata, source)["error"] == "InvalidInput: answer record"
    metadata, source = nominated([{**record, "question": "x"}])
    assert run_source(metadata, source)["error"] == "AnswerMismatch: x"
    # Python does not record nominations yet (it rejects the record); Lean's answer is the specified one.
    assert py_outcome(*nominated([record]))["error"] == "InvalidInput: answer record"


def test_narrowing_references_are_typed_before_resolution(lean):
    """A narrowing's set and version are a set id and a version number before they are looked up (3.2)."""
    name, metadata, source = templates()[1]
    for field, value in (("set", "not a token"), ("set", ""), ("version", 0), ("version", "1"), ("version", True)):
        changed = copy.deepcopy(metadata)
        changed["narrowings"][0][field] = value
        assert run_source(changed, source)["error"] == py_outcome(changed, source)["error"] == "invalid narrowing"
    for field, value, text in (("set", "other", "narrowing cites unknown reading set version"),
                               ("version", 2, "narrowing cites unknown reading set version"),
                               ("keeps", ["r9"], "narrowing must keep named readings"),
                               ("keeps", [], "narrowing must keep named readings"),
                               ("reason_spans", ["nowhere"], "narrowing needs cited source units"),
                               ("by", "Not a token", "invalid narrowing id or author")):
        changed = copy.deepcopy(metadata)
        changed["narrowings"][0][field] = value
        assert run_source(changed, source)["error"] == py_outcome(changed, source)["error"] == text


@pytest.mark.parametrize("condition", [["unary", "nonexistent", ["const", "atlas"]],
                                       ["unary", "reviewed", ["const", "nobody"]], ["unary", "reviewed", ["var", 0]],
                                       ["binary", "reviewed", ["const", "atlas"], ["const", "atlas"]]])
def test_open_term_conditions_are_typed(lean, condition):
    """An open term's conditions are closed formulas over the environment (document.md), in both checkers."""
    name, metadata, source = templates()[1]
    changed = copy.deepcopy(metadata)
    changed["open_terms"].append({"name": "extra", "arguments": [], "decided_by": "alice", "jurisdiction": "t1",
                                  "version": 1, "necessary": [condition], "sufficient": [], "factors": [],
                                  "precedents": []})
    py, le = py_outcome(changed, source), lean_outcome(run_source(changed, source))
    assert not py["ok"] and py == le


def test_reading_question_needs_its_derived_open_term(lean):
    name, metadata, source = templates()[1]
    for field, value in (("decided_by", "bob"), ("version", 2), ("factors", ["other"]), ("jurisdiction", "t2")):
        changed = copy.deepcopy(metadata)
        changed["open_terms"][0][field] = value
        assert run_source(changed, source)["error"] == py_outcome(changed, source)["error"] == \
            "InvalidInput: invalid question fields for r"
    unbound = copy.deepcopy(metadata)
    unbound["environment"]["speech_acts"].pop("addressee")
    assert run_source(unbound, source)["error"] == py_outcome(unbound, source)["error"] == "UnboundSlot: you"


def test_document_id_excludes_removable_weights_only(lean):
    name, metadata, source = templates()[0]
    weighted = {**metadata, "weights": [{"set": "rs", "by": "alice", "values": [1]}]}
    first, second = run_source(metadata, source), run_source(weighted, source)
    assert first["document_id"] == second["document_id"] == SpeechSource(weighted, source.encode(), {}).document_id
    moved = {**metadata, "narrowings": [], "lemmas": []}
    assert run_source(moved, source)["document_id"] != first["document_id"]


REVIEWED, CAT = U("reviewed", "atlas"), U("cat", "tom")
ANSWER_LEAF = {"name": "ans", "ast": ["and", ["top"], REVIEWED], "label": "speech:answer:p:yes"}


def admission_case(metadata, source, graph, **extra):
    return {"id": "a", "kind": "admission",
            "document": {"metadata": {**metadata, "graph": graph}, "source": source, "fences": {}}, **extra}


def admit(metadata, source, graph, **extra):
    [result] = run([admission_case(metadata, source, graph, **extra)])
    return result


def certified_graph(env):
    """The certified document's claim graph: the answer leaf of `p` and the asserted unit `b` entail the root."""
    metadata, source = certified(env)
    py = core(env, {"units": metadata["units"], "queries": metadata["queries"]})
    from ve.background import background as generated_background
    answer = formula_from_data(py.env, ANSWER_LEAF["ast"])
    cat = formula_from_data(py.env, CAT)
    root = And(answer, cat)
    # The prover checks Background first; in a graph those premises are explicit `background:<generator>` leaves.
    found = prove_entailment(py.env, [answer, cat], root)
    assert found.certificate is not None
    background = [{"name": f"bg{i}", "ast": _to_data(p.formula), "label": f"background:{p.generator}"}
                  for i, p in enumerate(generated_background(py.env))]
    assert background and {n["label"] for n in background} == {"background:profile"}
    graph = {"root": "root", "nodes": [
        *background, ANSWER_LEAF, {"name": "b", "ast": CAT, "unit": "b"},
        {"name": "root", "ast": _to_data(root), "premises": [*(n["name"] for n in background), "ans", "b"],
         "certificate": found.certificate}]}
    return metadata, source, graph


def test_admission_admits_the_claim_graph_over_the_projection(lean):
    """Review 11a B1: the `admission` kind admits a speech-act payload's claim graph (8.5, 8.6): P0 provenance over
    W2's projection plus the two route-local leaves, and P0's report identity over the 3.5 document id."""
    env = base_env()
    metadata, source, graph = certified_graph(env)
    result = admit(metadata, source, graph)
    assert result["status"] == "ok", result
    assert result["admitted"] is True
    assumptions = result["report"]["assumptions"]
    assert [leaf.get("label", "asserted") for leaf in assumptions[:4]] == \
        ["background:profile"] * 3 + ["speech:answer:p:yes"]
    # The answer certificate is bound to the complete regenerated premise list. Its
    # provenance remains visible even when the graph uses the answer as one leaf.
    assert [leaf["ast"] for leaf in assumptions[4:-1]] == run_source(metadata, source)["premises"]
    assert [(leaf["name"], leaf.get("label", "asserted")) for leaf in assumptions[-4:]] == \
        [("a", "asserted"), ("b", "asserted"), ("z", "asserted"), ("b", "asserted")]
    assert result["report"]["root"]["name"] == "root"
    assert result["document_id"] == run_source({**metadata, "graph": graph}, source)["document_id"]
    assert result["kinds"] == ["asserted", "asserted", "question", "question", "instruction", "asserted"]
    assert result["classes"] == [{"id": u["id"], "class": "C"} for u in metadata["units"]]
    assert result["status_text"] == run_source(metadata, source)["status_text"]
    # Identity (checklist 15): removable weights move nothing; the source, the report and the document do.
    weighted = {**metadata, "weights": [{"set": "rs", "by": "alice", "values": [1]}]}
    assert admit(weighted, source, graph)["report_id"] == result["report_id"]
    assert admit(metadata, source.replace("Beacon", "Becon"), graph)["status"] == "error"  # spans
    smaller = {"root": "ans", "nodes": [ANSWER_LEAF]}
    assert admit(metadata, source, smaller)["report_id"] != result["report_id"]
    renamed = copy.deepcopy(metadata)
    renamed["units"][1]["support"] = "observation"
    assert admit(renamed, source, graph)["report_id"] != result["report_id"]


def test_answer_only_graph_retains_certificate_premises(lean):
    """A graph with only an answer leaf still reports every input of that answer certificate."""
    metadata, source = certified(base_env())
    result = admit(metadata, source, {"root": "ans", "nodes": [ANSWER_LEAF]})
    assert result["status"] == "ok", result
    assumptions = result["report"]["assumptions"]
    assert assumptions[0] == ANSWER_LEAF
    assert [leaf["ast"] for leaf in assumptions[1:]] == run_source(metadata, source)["premises"]
    assert [leaf["name"] for leaf in assumptions[-3:]] == ["a", "b", "z"]


def test_admission_presupposition_leaves_stay_assumptions(lean):
    env = base_env()
    metadata, source = certified(env)
    graph = {"root": "h", "nodes": [{"name": "h", "ast": ["top"], "label": "speech:presupposition:p"}]}
    result = admit(metadata, source, graph)
    assert result["status"] == "ok", result
    assert result["report"]["assumptions"] == [{"name": "h", "ast": ["top"], "label": "speech:presupposition:p"}]


@pytest.mark.parametrize("status,label", [("open", "readings:rs@1:all"),
                                         ("authored", "readings:rs@1:0")])
def test_admission_projects_structured_assertion_readings(lean, status, label):
    """An asserted speech reading has `{"ast": ...}` content; P0 reads the enclosed formula.
    Both an open disjunction and a signed choice retain their reading provenance.
    """
    env = base_env()
    source = "Atlas is reviewed.\n"
    ast = U("reviewed", "atlas")
    metadata = {"format": "ve-document@2", "environment": env,
                "units": placed([source], [unit("a", 0, "asserted", {"ast": ast})]),
                "reading_sets": [reading_set("a", 1, status, "asserted", {"ast": ast})]}
    node = {"name": "r", "ast": ast, "label": label}
    assert py_outcome(metadata, source)["ok"]
    assert run_source(metadata, source)["status"] == "ok"
    result = admit(metadata, source, {"root": "r", "nodes": [node]})
    assert result["status"] == "ok", result
    assert result["report"]["assumptions"] == [node]


@pytest.mark.parametrize("node, error", [
    # an answer leaf whose formula is not H and F of a certificate-supported record
    ({"name": "n", "ast": ["and", ["top"], ["not", REVIEWED]], "label": "speech:answer:p:no"},
     "AdmissionError: node n is not admitted under label speech:answer:p:no"),
    ({"name": "n", "ast": REVIEWED, "label": "speech:answer:p:yes"},
     "AdmissionError: node n is not admitted under label speech:answer:p:yes"),
    # the follows question's judgment is no answer leaf, and a presupposition leaf must be the regenerated formula
    ({"name": "n", "ast": CAT, "label": "speech:answer:f:yes"},
     "AdmissionError: node n is not admitted under label speech:answer:f:yes"),
    ({"name": "n", "ast": REVIEWED, "label": "speech:presupposition:p"},
     "AdmissionError: node n is not admitted under label speech:presupposition:p"),
    # no compliance leaf and no checker-generated done fact (4.6, 8.5)
    ({"name": "n", "ast": ["binary", "done_submit", ["const", "alice"], ["const", "q1"]],
      "label": "speech:compliance:t"}, "AdmissionError: node n is not admitted under label speech:compliance:t"),
    ({"name": "n", "ast": ["binary", "done_submit", ["const", "alice"], ["const", "q1"]]},
     "AdmissionError: node n is not admitted under label asserted"),
    ({"name": "n", "ast": ["binary", "done_submit", ["const", "alice"], ["const", "q1"]], "unit": "t"},
     "AdmissionError: node n is not admitted under label asserted"),
    # an asserted leaf is the unit's own formula
    ({"name": "n", "ast": CAT, "unit": "a"}, "AdmissionError: node n is not admitted under label asserted"),
])
def test_admission_rejects_leaves_without_provenance(lean, node, error):
    env = base_env()
    metadata, source = certified(env)
    assert admit(metadata, source, {"root": "n", "nodes": [node]})["error"] == error


def test_binding_units_are_withheld_from_p0_and_classed(lean):
    """8.5 `bindings_withheld`: a binding unit never reaches P0 (its kind decoder has no `binding`), is classed by the
    coverage projection and stays in the identity payload."""
    name, metadata, source = templates()[2]
    graph = {"root": "h", "nodes": [{"name": "h", "ast": ["top"], "label": "speech:presupposition:u2"}]}
    result = admit(metadata, source, graph)
    assert result["status"] == "ok", result
    assert result["kinds"] == ["instruction", "question"]
    assert [c["id"] for c in result["classes"]] == ["u0", "u1", "u2"]
    pointed = {"root": "h", "nodes": [{"name": "h", "ast": ["top"], "unit": "u0"}]}
    assert admit(metadata, source, pointed)["error"] == "AdmissionError: node h is not admitted under label asserted"
    rebound = copy.deepcopy(metadata)
    rebound["units"][0]["support"] = "testimony"
    assert admit(rebound, source, graph)["report_id"] != result["report_id"]


def test_admission_layer_leaves_are_the_regenerated_policy(lean):
    env = base_env()
    metadata, source = certified(env)
    layers = {p["label"]: p["ast"] for p in run_source(metadata, source)["policy"]["premises"]}
    label = "layer:norms:submit_required"
    assert admit(metadata, source, {"root": "l", "nodes": [{"name": "l", "ast": layers[label], "label": label}]}) \
        ["status"] == "ok"
    wrong = layers["layer:norms:click_required"]
    assert admit(metadata, source, {"root": "l", "nodes": [{"name": "l", "ast": wrong, "label": label}]})["error"] \
        == f"AdmissionError: node l is not admitted under label {label}"


def test_admission_entry_points(lean):
    """The P0-form admission case on the speech route names the payload it needs; a payload without a graph is
    W2's abstention, never an admission; a malformed source is the speech-source rejection."""
    name, metadata, source = templates()[0]
    case = {"id": "a", "kind": "admission", "environment": metadata["environment"],
            "document": {"units": metadata["units"]}}
    [result] = run([case])
    assert result["error"] == ('InvalidInput: speech-act admission reads the ve-document@2 payload '
                               '{"metadata", "source", "fences"}')
    [result] = run([{"id": "a", "kind": "admission",
                     "document": {"metadata": metadata, "source": source, "fences": {}}}])
    assert result["error"] == "NotImplemented: a document without a claim graph"
    bad = {**metadata, "units": []}
    assert admit(bad, source, {"root": "n", "nodes": []})["error"] == run_source(bad, source)["error"]


def test_admission_graph_type_confusion_is_a_bounded_rejection(lean):
    """Every single-fault mutant of the claim graph (checklist 5) is an answer row: admitted, or rejected with a
    diagnostic; nothing crashes or goes unanswered."""
    env = base_env()
    metadata, source, graph = certified_graph(env)
    mutants = [_replace_wire({"graph": graph}, path, replacement)["graph"]
               for path, replacement in _wire_mutations({"graph": graph}) if path != ("graph",)]
    results = run([{**admission_case(metadata, source, g), "id": str(i)} for i, g in enumerate(mutants)])
    assert len(results) == len(mutants) > 100
    for g, result in zip(mutants, results):
        assert result["status"] in ("ok", "error") and "case_index" not in result, (g, result)
        if result["status"] == "error":
            assert type(result["error"]) is str and result["error"], (g, result)
    assert sum(r["status"] == "ok" for r in results) < len(results) // 2


def test_every_record_line_is_regenerated_not_copied(lean):
    """The record lines come from Lean's replay: a record's own text fields never reach the report."""
    env = base_env()
    metadata, source = certified(env)
    result = run_source(metadata, source)
    assert json.dumps(result).count("supported yes") == 1
    noted = copy.deepcopy(metadata)
    noted["answers"][0]["answer"] = {"one": "atlas"}
    assert run_source(noted, source)["error"].startswith("AnswerOutsideDomain: p, ")
    assert [_to_data(f) for f in core(env, {"units": metadata["units"], "queries": metadata["queries"]})
            .premises()] == result["premises"]
    assert _to_data(And(Top(), Not(Top()))) != result["premises"]


@pytest.mark.parametrize("depth", [300, 10_000])
def test_deep_input_is_a_bounded_rejection(lean, depth):
    """A 10,000-deep JSON value in the front matter is the restricted reader's ResourceLimit, never a crash."""
    import subprocess

    from subprocesses import HANG_TIMEOUT
    name, metadata, source = templates()[0]
    case = json.dumps([source_case(0, {**metadata, "weights": "DEEP"}, source)])
    case = case.replace('"DEEP"', "[" * depth + "]" * depth)
    completed = subprocess.run([str(lean), "-"], input=case, capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert completed.returncode == 1
    assert json.loads(completed.stdout) == [{"case_index": 0, "error": "ResourceLimit: JSON depth exceeds 256",
                                             "status": "error"}]


# Spec 8.5 names whose Lean owner has another name or shape, each with the declaration that stands in for it (and
# lean/SPEECH-ACTS.md says how it differs). Every other 8.5 name must be declared under VE.SpeechActs as written.
SPEC_8_5_STAND_INS = {
    "SpeechUnit": "VE.SpeechActs.Source.SourceUnit",
    "OpenTerm": "VE.SpeechActs.Source.SpeechSource.openTerms",  # validated W2 JSON (`Loader.openTermNames`)
    "SpeechReading": "VE.SpeechActs.Source.SetInfo.readings",  # validated W2 JSON, checked as candidates by the core
    "SpeechReadingSet": "VE.SpeechActs.Source.SetInfo",
    "Narrowing": "VE.SpeechActs.Source.Nomination",  # recorded nominations; W2 narrowings by `Loader.narrowingIds`
    "SpeechSource.toDoc": "VE.SpeechActs.Wire.Decoded.D",  # the projection is `src.dec.D`
}


def test_every_spec_8_5_name_has_a_lean_owner():
    """Review 11a B1's class: a required 8.5 item (wrapper, admission, theorem) is never silently left out."""
    import re
    spec = (ROOT / "docs/spec/speech-acts.md").read_text()
    section = spec[spec.index("### 8.5 Theorems: wire and report"):spec.index("### 8.6 ")]
    names = re.findall(r"^(?:theorem|structure|def) ([A-Za-z_.]+)", section, re.M)
    assert {"SpeechAdmitted", "bindings_withheld", "speech_wire_acceptance", "active_commands"} <= set(names)
    declared = (ROOT / "lean/declarations.txt").read_text()
    missing = []
    for name in names:
        owner = SPEC_8_5_STAND_INS.get(name)
        pattern = re.escape(owner) + "@" if owner else r" VE\.SpeechActs\.[\w.]*\b" + re.escape(name) + "@"
        if not re.search(pattern, declared):
            missing.append(name)
    assert missing == []
