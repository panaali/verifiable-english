"""English authoring of definitions, glossaries of synonyms and citations (W3,
VISION 'Synonyms and varied wording')."""
from subprocesses import HANG_TIMEOUT
from copy import deepcopy
import json
from pathlib import Path

import pytest

from conformance.p0 import definitions_envelope
from ve import Environment
from ve.ast import Const, Unary, formula_from_data
from ve.bundle import check_bundle
from ve.definitions import compile_definitions
from ve.english import parse_english, render_english
from ve.entailment import prove_entailment
from ve.errors import VEError
from ve.profiles import SPEC_REVISION
from ve.surface.definitions import (adopt, parse_citation, parse_definition, parse_glossary,
                                    render_citation, render_definition, wordings)

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean/.lake/build/bin/ve_conformance"


def staff_env(profiles=("relational-fol@0",)):
    words = {"staff": "{0} is staff", "personnel": "{0} is personnel", "trusted": "{0} is trusted",
             "badge": "{0} is badged"}
    predicates = {name: {"arguments": ["person"], "description": name, "verbalisation": text}
                  for name, text in words.items()}
    predicates["employee"] = {"arguments": ["person"], "description": "is an employee"}
    predicates["manages"] = {"arguments": ["person", "person"], "description": "manages"}
    return {"language": "ve.core@0.2", "profiles": list(profiles), "spec_revision": SPEC_REVISION,
            "vocabulary": {"sorts": {"person": {"description": "a person"}}, "predicates": predicates,
                           "constants": {"ann": {"sort": "person", "description": "Ann"}}}}


GLOSSARY = "In this document, staff, employees and personnel mean the same thing.\n"
TRUSTED = ('By definition, for every person, that person is trusted exactly when both that person '
           'is staff and that person is badged.\n')


@pytest.mark.parametrize("path", [
    None,
    "usecases/claude-constitution-excerpt/definitions-environment.json",
])
def test_every_definition_renders_as_one_reading_sentence(path):
    raw = definitions_envelope() if path is None else json.loads((ROOT / path).read_text())
    env = Environment(raw)
    rows = wordings(env)
    assert len(rows) == len(env.definition_entries)
    for definition in compile_definitions(env, env.definition_entries, version=env.environment_id):
        sentence = render_definition(env, definition)
        assert sentence.startswith("By definition, for every ")
        assert parse_definition(env, sentence) == definition


def test_math_bundle_definitions_read_back():
    data = json.loads((ROOT / "usecases/math-mini-paper/t7-definitions-bundle.json").read_text())
    env = Environment(data["environment"])
    for definition in compile_definitions(env, env.definition_entries, version=env.environment_id):
        assert parse_definition(env, render_definition(env, definition)) == definition


def test_glossary_adopts_alias_definitions_and_keeps_word_choice():
    raw = adopt(staff_env(), GLOSSARY + TRUSTED)
    env = Environment(raw)
    assert env.environment_id != Environment(staff_env()).environment_id
    assert raw["profiles"] == ["definitions@0", "relational-fol@0"]
    entries = env.definition_entries
    assert entries["employee"]["body"] == ["unary", "staff", ["var", 0]]
    assert entries["personnel"]["body"] == ["unary", "staff", ["var", 0]]
    assert "staff" not in entries
    # The author's word stays in the document; meaning goes through the alias.
    personnel = Unary("personnel", Const("ann"))
    assert "personnel" in render_english(personnel, env)
    staff = Unary("staff", Const("ann"))
    assert prove_entailment(env, (staff,), personnel).status == "Found"
    assert prove_entailment(env, (Unary("employee", Const("ann")),), personnel).status == "Found"


def test_glossary_certificate_is_accepted_by_lean():
    if not LEAN.exists():
        pytest.skip("lean route runner is not built (lake build)")
    import subprocess
    raw = adopt(staff_env(), GLOSSARY)
    env = Environment(raw)
    premise, conclusion = Unary("employee", Const("ann")), Unary("personnel", Const("ann"))
    certificate = prove_entailment(env, (premise,), conclusion).certificate
    case = [{"id": "glossary", "kind": "certificate", "environment": raw,
             "premises": [["unary", "employee", ["const", "ann"]]],
             "conclusion": ["unary", "personnel", ["const", "ann"]], "certificate": certificate}]
    run = subprocess.run([str(LEAN), "route", "-"], input=json.dumps(case), capture_output=True,
                         text=True, timeout=HANG_TIMEOUT)
    assert json.loads(run.stdout)[0]["valid"] is True


@pytest.mark.parametrize("sentence, message", [
    ("In this document, staff and managers mean the same thing.", "no declared predicate"),
    ("In this document, staff and manages mean the same thing.", "same argument sorts"),
    ("In this document, staff and staff mean the same thing.", "two different words"),
    ("In this document, staff mean the same thing.", "two different words"),
    ("Staff and personnel mean the same thing.", "In this document"),
])
def test_glossary_rejections(sentence, message):
    with pytest.raises(VEError, match=message):
        parse_glossary(Environment(staff_env()), sentence)


def test_glossary_rejects_redefinition_and_cycles():
    with pytest.raises(VEError, match="already defined"):
        adopt(staff_env(), GLOSSARY + "In this document, trusted and personnel mean the same thing.\n")
    with pytest.raises(VEError, match="DependencyCycle"):
        adopt(staff_env(), "In this document, staff and personnel mean the same thing.\n"
                           "In this document, personnel and trusted mean the same thing.\n"
                           "In this document, trusted and staff mean the same thing.\n")


def test_glossary_rejects_an_ambiguous_word():
    raw = staff_env()
    raw["vocabulary"]["predicates"]["employees"] = {"arguments": ["person"], "description": "x"}
    with pytest.raises(VEError, match="more than one"):
        parse_glossary(Environment(raw), GLOSSARY)


@pytest.mark.parametrize("sentence, message", [
    (TRUSTED.replace("By definition, ", ""), "starts with"),
    (TRUSTED.replace(" exactly when ", " when "), "exactly once"),
    (TRUSTED.replace("both that person", "that person is staff exactly when both that person"),
     "exactly once"),
    ("By definition, that person is trusted exactly when that person is staff.", "for every"),
    ("By definition, for every person, that person is staff exactly when that person is trusted.",
     None),
    ("By definition, for every first person, for every second person, the second person has the "
     'recorded relation "manages" to the first person exactly when this holds in all cases.',
     "arguments in order"),
])
def test_definition_sentence_rejections(sentence, message):
    env = Environment(staff_env(("definitions@0", "relational-fol@0")))
    if message is None:  # well formed; the body is checked on adoption
        assert parse_definition(env, sentence).name == "staff"
        return
    with pytest.raises(VEError, match=message):
        parse_definition(env, sentence)


def test_definition_sentence_parts_are_read_by_python_with_lean_shadow(monkeypatch):
    """A definition's head and body use Python admission and still reach Lean's shadow reader."""
    from ve import english
    from ve.backends import english_lean
    seen = []
    original = english_lean.read
    monkeypatch.setattr(english_lean, "read",
                        lambda env, source, words, options: seen.append(source) or original(env, source, words, options))
    python_seen = []
    original_python = english._python_reading
    monkeypatch.setattr(english, "_python_reading",
                        lambda *args: python_seen.append(args[1]) or original_python(*args))
    parse_definition(Environment(staff_env(("definitions@0", "relational-fol@0"))), TRUSTED)
    assert seen == ["for every person, that person is trusted.",
                    "for every person, both that person is staff and that person is badged."]
    assert python_seen == seen


def test_citation_and_definition_renderings_are_checked_by_lean(monkeypatch):
    """Recheck 1 of E2, B: the citation's conclusion and a definition's biconditional are formula sentences,
    so Lean's `english.check` reads each rendering back (LEDGER), not Python's statement-layer reader."""
    from ve import english
    from ve.backends import english_lean
    seen = []
    original = english_lean.check
    monkeypatch.setattr(english_lean, "check", lambda *args: seen.append(args[-1]) or original(*args))
    env = Environment(adopt(staff_env(), TRUSTED))
    [row] = wordings(env)
    conclusion = formula_from_data(env, ["unary", "trusted", ["const", "ann"]])
    citation = render_citation(env, ["T1"], conclusion)
    assert citation == "By T1, ann is trusted.\n"
    assert [row["biconditional"]] in seen and any(c.startswith("Ann is trusted") for cs in seen for c in cs)


def test_a_citation_over_an_nary_environment_with_a_layer_renders():
    """The failure the statement-layer flag hid (`tests/test_stage2_bundle.py` family4): Lean's typed check
    refused every sentence of an `nary@0` environment beside `data@0`, so no citation passed its check."""
    from tests import probe_matrix as pm
    env = Environment(pm.raw_environment(("closure@0", "nary@0", "data@0")))
    conclusion = pm.semantic_formula(env)
    assert parse_citation(env, render_citation(env, ["first"], conclusion), ["first"]) == (("first",), conclusion)


@pytest.mark.parametrize("sentence", [
    "By definition, for every person, that person is trusted exactly when that person is staff. Ann is badged.",
    "By definition, for every person, that person is trusted exactly when that person is staff. This is impossible.",
])
def test_definition_rejects_extra_english_statement(sentence):
    env = Environment(staff_env(("definitions@0", "relational-fol@0")))
    with pytest.raises(VEError):
        parse_definition(env, sentence)
    with pytest.raises(VEError):
        adopt(staff_env(), sentence)


def test_no_keyword_cannot_be_a_constant_in_definition_profile():
    raw = staff_env(("definitions@0", "relational-fol@0"))
    raw["vocabulary"]["constants"]["no"] = {"sort": "person", "description": "No"}
    with pytest.raises(VEError, match="Reserved|reserved"):
        Environment(raw)


def test_citation_sentences_round_trip():
    data = json.loads((ROOT / "usecases/math-mini-paper/t7-definitions-bundle.json").read_text())
    env = Environment(data["environment"])
    report = check_bundle(data)
    names = [lemma["name"] for lemma in data["lemmas"]]
    for lemma, row in zip(data["lemmas"], report["lemmas"], strict=True):
        cited = [names[[l["meaning_id"] for l in data["lemmas"]].index(m)] for m in lemma["cites"]]
        conclusion = formula_from_data(env, lemma["conclusion"])
        assert row["english"] == render_citation(env, cited, conclusion)
        assert parse_citation(env, row["english"], names) == (tuple(cited), conclusion)
    assert report["lemmas"][-1]["english"].startswith("By T7a and T7b, for every point")
    with pytest.raises(VEError, match="unknown lemma"):
        parse_citation(env, report["lemmas"][-1]["english"].replace("T7b", "T9"), names)
    three = render_citation(env, ["T7a", "T7b", "T7"], conclusion)
    assert parse_citation(env, three, names) == (("T7a", "T7b", "T7"), conclusion)
