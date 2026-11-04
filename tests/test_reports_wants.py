"""The `wants` test's one owner (docs/spec/attitudes.md section 10 item 6, RC-4; AT-1w): Lean's
`reports-wants` kind (`VE.Reports.wantsPhrase?`, `lean/VE/Attribution/Words.lean`) answers the
parity table recorded from the deleted Python `_infinitive` and `_finite`, its rows are typed and
bound to the phrases sent (R8), and `reports@0`'s English reads both forms from it.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ve.backends.service_schema import Compiler, Context, Invalid
from ve.environment import Environment
from ve.errors import CheckerUnavailable, ResourceLimit, VEError
from ve.limits import MAX_SOURCE_BYTES
import ve.reports as reports
from ve.report_english import parse_rendered_report, render_report_unit
from ve.reports_route import wants_forms

from test_report_english import B, assess, document, environment, report
from test_reports_lean import lean, run1  # noqa: F401

TABLE = json.loads((Path(__file__).parent / "data/reports_wants_parity.json").read_text(encoding="utf-8"))
C_E = ('is classified as "mass_casualty_weapon_uplift"', 'be classified as "mass_casualty_weapon_uplift"')


def case(phrases, infinitives):
    return {"id": "wants", "kind": "reports-wants", "phrases": phrases, "infinitives": infinitives}


def test_the_kind_answers_the_parity_table_on_every_row(lean):
    infinitive = TABLE["infinitive"] + TABLE["infinitive_probes"]
    finite = TABLE["finite"] + TABLE["finite_probes"]
    assert TABLE["checkout"] == "94580b39b" and len(TABLE["infinitive"]) == 3 and len(TABLE["finite"]) == 3
    answer = wants_forms([p for p, _ in infinitive], [p for p, _ in finite])
    assert [[r["phrase"], r["infinitive"]] for r in answer["phrases"]] == infinitive
    assert [[r["infinitive"], r["finite"]] for r in answer["infinitives"]] == finite


def test_c_e_phrase_gives_its_infinitive_and_back_through_the_kind(lean):
    """Fixture C-e's part "c0 wants s1 to be classified as ..." (spec 7.1, at-rev AT-R1)."""
    doc = document(report("anthropic", "believes", "c1", B("audits", "anthropic", "service")))
    assert doc.infinitive(C_E[0]) == C_E[1]
    assert doc.finite(C_E[1]) == C_E[0]
    assert doc.infinitive("is not " + C_E[0][3:]) is None


def genuine():
    sent = case(["is safe", "is not safe", "audits service"], ["be safe", "audit service"])
    answer = run1(sent)
    assert answer["phrases"][1] == {"phrase": "is not safe", "infinitive": None}, answer
    return sent, answer


def mutations(answer):
    """Each row's members dropped, emptied and retyped; each row list dropped, emptied, given a
    duplicate, reordered, shifted and given a row for a phrase not sent. The flag marks a binding
    mutation, which the document refuses too; the schema refuses every one."""
    for field, key in (("phrases", "phrase"), ("infinitives", "infinitive")):
        rows = answer[field]
        for i, row in enumerate(rows):
            for member in row:
                bad = copy.deepcopy(answer)
                del bad[field][i][member]
                yield f"{field}[{i}] without {member}", bad, True
                for value in ("", 7, True, [], {}, 1.5, [[[]]], *(() if member == "infinitive" else (None,))):
                    if value == "" and member != key:
                        continue
                    bad = copy.deepcopy(answer)
                    bad[field][i][member] = value
                    yield f"{field}[{i}].{member} = {value!r}", bad, member == key
        for label, changed in (("dropped", rows[1:]), ("empty", []), ("duplicated", rows + rows[-1:]),
                               ("reordered", rows[::-1]), ("not sent", rows + [{**rows[0], key: "flies"}]),
                               ("shifted", [{**rows[0], key: rows[1][key]}] + rows[1:])):
            bad = copy.deepcopy(answer)
            bad[field] = changed
            yield f"{field} {label}", bad, True
        bad = copy.deepcopy(answer)
        del bad[field]
        yield f"without {field}", bad, True


def test_every_retyped_or_rebound_row_is_refused_by_the_schema(lean):
    sent, answer = genuine()
    validator = Compiler().ref("reports.json", "#/row")[0]
    validator(answer, Context(sent), {})
    for label, bad, _ in mutations(answer):
        with pytest.raises(Invalid):
            validator(bad, Context(sent), {})
            pytest.fail(label)


def test_every_rebound_row_is_unavailable_to_the_document(lean, monkeypatch):
    sent, answer = genuine()
    doc = document(report("anthropic", "believes", "c1", B("audits", "anthropic", "service")))
    monkeypatch.setattr(reports, "wants_forms", lambda *a: answer)
    assert doc.wants_forms(sent["phrases"], sent["infinitives"]) == (
        ["be safe", None, "audit service"], ["is safe", "audits service"])
    bound = [(label, bad) for label, bad, binding in mutations(answer) if binding]
    for label, bad in bound + [("not an object", [])]:
        monkeypatch.setattr(reports, "wants_forms", lambda *a, bad=bad: bad)
        with pytest.raises(CheckerUnavailable):
            doc.wants_forms(sent["phrases"], sent["infinitives"])
            pytest.fail(label)


def test_the_english_reads_both_forms_from_the_kind_and_refuses_a_dropped_row(lean, monkeypatch):
    content = report("anthropic", "wants", "c1", B("publishes", "anthropic", "service"))
    doc = document(content)
    rendered = render_report_unit(doc, "u1")
    assert rendered["text"] == "Anthropic wants to publish service."
    assert doc.meaning_id(parse_rendered_report(doc, rendered)) == doc.meaning_id(content)
    for field in ("phrases", "infinitives"):
        def dropped(phrases, infinitives, field=field):
            answer = wants_forms(phrases, infinitives)
            return {**answer, field: answer[field][1:]}
        monkeypatch.setattr(reports, "wants_forms", dropped)
        with pytest.raises(CheckerUnavailable):
            render_report_unit(doc, "u1") if field == "phrases" else parse_rendered_report(doc, rendered)
    monkeypatch.undo()


@pytest.mark.parametrize("content, text, phrase, infinitive", [
    (report("anthropic", "wants", "c1", B("publishes", "anthropic", "service")), "Anthropic wants to publish service.",
     "publishes service", "publish service"),
    (report("article", "wants", "c1", B("audits", "anthropic", "service")),
     "The article wants anthropic to audit service.", "audits service", "audit service")])
def test_one_wants_sentence_asks_lean_three_times(lean, monkeypatch, content, text, phrase, infinitive):
    """A step count, not a time: printing asks for the phrase's infinitive and, through the
    printer's one-reading check, for its finite form; parsing asks for the finite form once."""
    doc, calls = document(content), []
    monkeypatch.setattr(reports, "wants_forms", lambda p, i: calls.append((list(p), list(i))) or wants_forms(p, i))
    rendered = render_report_unit(doc, "u1")
    parse_rendered_report(doc, rendered)
    assert rendered["text"] == text
    assert calls == [([phrase], []), ([], [infinitive]), ([], [infinitive])]


def test_a_phrase_the_test_refuses_has_no_wants_wording(lean):
    """The opposite direction: `trys service` has no infinitive (`try`'s finite form is `tries`,
    not the phrase), so a `wants` of it has no reviewed wording and its assessment keeps the long form."""
    env = environment().to_dict()
    env["vocabulary"]["predicates"]["trys"] = {"arguments": ["organisation", "system"], "description": "trys",
                                               "verbalisation": "{0} trys {1}"}
    content = B("trys", "anthropic", "service")
    doc = document(report("article", "wants", "c1", content), assess("probably", content),
                   env=Environment(env))
    assert doc.infinitive("trys service") is None
    with pytest.raises(VEError, match="No reviewed wording: wants needs a sentence"):
        render_report_unit(doc, "u1")
    assert render_report_unit(doc, "u2")["text"] == (
        "According to the stated assessment, it is probably the case that anthropic trys service.")


def test_the_request_is_charged_against_max_source_bytes(lean):
    # One byte more per phrase: a request of exactly the limit is answered, one byte more is not.
    many = ["runs x"] * ((MAX_SOURCE_BYTES - len("run x") - 1) // len("runs x "))
    answer = wants_forms(many, ["run x"])
    assert len(answer["phrases"]) == len(many)
    assert answer["infinitives"] == [{"infinitive": "run x", "finite": "runs x"}]
    assert wants_forms(["a" * (MAX_SOURCE_BYTES - 1)], [])["phrases"][0]["infinitive"] is None
    for phrases, infinitives in ((["a" * MAX_SOURCE_BYTES], []), (["a" * (MAX_SOURCE_BYTES - 2)], ["b"])):
        with pytest.raises(ResourceLimit, match="reports-wants phrases exceed max_source_bytes"):
            wants_forms(phrases, infinitives)


@pytest.mark.parametrize("field", ["phrases", "infinitives"])
@pytest.mark.parametrize("value", [7, True, "is safe", {}, [7], [["is safe"]], [{}], "absent"])
def test_a_malformed_request_is_invalid_input(lean, field, value):
    sent = case(["is safe"], ["be safe"])
    if value == "absent":
        del sent[field]
    else:
        sent[field] = value
    answer = run1(sent)
    assert answer == {"id": "wants", "status": "error",
                      "error": f"InvalidInput: reports-wants {field} must be a list of strings"}
    if type(value) is list:
        with pytest.raises(VEError, match="must be a list of strings"):
            wants_forms(sent["phrases"], sent["infinitives"])
