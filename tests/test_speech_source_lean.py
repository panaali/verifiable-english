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
            "compliance": [(c["command"], c["query"]) for c in result["compliance"]],
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


def test_admission_kind_stays_closed(lean):
    name, metadata, source = templates()[0]
    case = {"id": "a", "kind": "admission", "environment": metadata["environment"],
            "document": {"units": metadata["units"]}}
    [result] = run([case])
    assert result["error"] == "UnsupportedProfile: case kind admission is not available on the speech-acts route"


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
