"""jt-2c: the modes that compose with `judgments@0` decide over the environment without the document layers
(`VE.Compose.decidingEnvironment`) and name the list as written (reviews/dri-decisions-20261028-jt-2c.md item 1).

Each case is sent twice: over a `judgments@0` environment and over its profile-free twin. The verdicts are the same,
every identity differs, a certificate or model claimed for the twin does not bind to the layer's environment, and a
profile the layer does not compose with yet is refused by name.
"""
from __future__ import annotations

import json

import pytest

from test_judgments_document import (ALPHA, J1, MODEL, PILOT, PLAIN, PROFILES, STATUS, UPSILON, VOCAB, document,
                                     environment, opened, u, unit)
from ve.backends.lean_service import LeanService

TWIN = [p for p in PROFILES if p != "judgments@0"]


@pytest.fixture(scope="module")
def service():
    with LeanService() as instance:
        yield instance


def both(service, mode, case, profiles=PROFILES, vocabulary=VOCAB):
    """The answers to `case` over `profiles` and over the same list without `judgments@0`."""
    rows = [service.run(mode, [{**case, "environment": environment(vocabulary, ps)}])[0]
            for ps in (profiles, [p for p in profiles if p != "judgments@0"])]
    assert all(r["status"] == "ok" for r in rows), rows
    return rows


def test_the_environment_mode_names_the_list_as_written(service):
    judged, twin = both(service, "environment", {"id": "e"})
    assert (judged["profiles"], twin["profiles"]) == (PROFILES, TWIN)
    assert (judged["family"], judged["acts"]) == (twin["family"], twin["acts"])
    assert judged["environment_id"] != twin["environment_id"]


@pytest.mark.parametrize("ast", [UPSILON, ["forall", "act", u("unlawful_detention")]])
def test_the_check_mode_types_as_the_twin_and_names_the_written_list(service, ast):
    judged, twin = both(service, "check", {"id": "c", "ast": ast})
    assert judged["well_typed"] is twin["well_typed"] is True
    assert judged["meaning_id"] != twin["meaning_id"]


def test_a_formula_the_twin_refuses_is_refused_with_the_same_text(service):
    bad = ["forall", "act", ["unary", "undeclared", ["var", 0]]]
    rows = [service.run("check", [{"id": "c", "environment": environment(profiles=ps), "ast": bad}])[0]
            for ps in (PROFILES, TWIN)]
    assert rows[0]["status"] == "error" and rows[0] == rows[1]


def test_a_model_is_valid_as_for_the_twin_and_the_twin_s_ids_do_not_bind(service):
    judged, twin = both(service, "model", {"id": "m", "model": MODEL})
    assert judged["valid"] is twin["valid"] is True and judged["model_id"] != twin["model_id"]
    ids = {p: service.run("environment", [{"id": "e", "environment": environment(profiles=p)}])[0]["environment_id"]
           for p in (tuple(PROFILES), tuple(TWIN))}
    own = {"environment_id": ids[tuple(PROFILES)], "model_id": judged["model_id"]}
    other = {"environment_id": ids[tuple(TWIN)], "model_id": twin["model_id"]}
    for profiles, claimed, ok in ((PROFILES, own, True), (PROFILES, other, False), (TWIN, other, True),
                                  (TWIN, own, False), (PROFILES, {**own, "model_id": twin["model_id"]}, False)):
        row = service.run("model", [{"id": "m", "environment": environment(profiles=profiles), "model": MODEL,
                                     "claimed": claimed}])[0]
        assert (row["status"] == "ok") is ok, (profiles, claimed, row)


def test_definitions_are_elaborated_as_for_the_twin(service):
    """The `background` case (Python's definitions and Background) on the norms route, which reads the environment
    without the layer (`Norms.Plain.layered`), with and without regulated predicates: no identity, the same answer."""
    plain = {**VOCAB, "predicates": {k: v for k, v in VOCAB["predicates"].items() if "regulated" not in v}}
    for vocabulary in (VOCAB, plain):
        judged, twin = both(service, "norms", {"id": "b", "kind": "background"}, vocabulary=vocabulary)
        assert judged == twin and any(g == "definitions" for g in judged["generators"])


# What `judgments@0` does not compose with yet (`VE.Compose.documentLayersApart`): refused by name by every composing
# mode; the same list without the layer is not refused so, and the layer with the other profiles is answered.
APART = [("soft-norms@0", "soft-norms@0"), ("rights@0", "rights@0"), ("alternatives@0", "alternatives@0"),
         ("risk@0", "risk@0")]


@pytest.mark.parametrize("extra, named", APART)
@pytest.mark.parametrize("mode, field", [("check", {"ast": UPSILON}), ("model", {"model": MODEL}),
                                         ("norms", {"kind": "background"})])
def test_a_composed_profile_is_refused_by_name(service, extra, named, mode, field):
    """The model mode validates the environment as written first (`validatedComposedEnvironment`), whose decoders
    refuse these lists over this vocabulary before the model's environment is read."""
    refusal = f"CheckerUnavailable: judgments@0 with {named} needs its composed Lean route"
    rows = [service.run(mode, [{"id": "x", "environment": environment(profiles=sorted(ps + [extra])), **field}])[0]
            for ps in (PROFILES, TWIN)]
    assert rows[0]["status"] == "error" and rows[1].get("error") != refusal
    if mode != "model":
        assert rows[0] == {"id": "x", "status": "error", "error": refusal}


@pytest.mark.parametrize("extra", ["readings@1", "norm-defaults@0", "data@0", "time@0"])
def test_a_profile_the_layer_composes_with_is_answered(service, extra):
    profiles = sorted(PROFILES + [extra])
    row = service.run("check", [{"id": "c", "environment": environment(profiles=profiles), "ast": UPSILON}])[0]
    assert row["status"] == "ok" and row["well_typed"] is True, row


# The layer's own requirement over the list as written (jt-2c review F1, `VE.Compose.layerGate`): every composing mode
# refuses a list with `judgments@0` and without `documents@1` with the environment mode's text, answers it with
# `documents@1`, and answers the list without the layer.
REQUIRES = "UnsupportedProfile: judgments@0 requires documents@1"
WITHOUT_DOCUMENTS = [p for p in PROFILES if p != "documents@1"]
COMPOSING = [("environment", {}, []), ("check", {"ast": UPSILON}, []),
             ("metered", {"kind": "evaluate-budgeted", "model": MODEL, "ast": [UPSILON], "max_evaluations": 1000}, []),
             ("model", {"model": MODEL}, []), ("norms", {"kind": "background"}, []),
             ("norms", {"kind": "norms-elaborate", "norms": []}, []),
             ("norm-defaults", {"kind": "norm-defaults-elaborate", "norms": []}, ["norm-defaults@0"])]


@pytest.mark.parametrize("mode, field, extra", COMPOSING,
                         ids=[f"{m}-{f.get('kind', 'case')}" for m, f, _ in COMPOSING])
def test_the_layer_s_own_requirement_is_checked_by_every_composing_mode(service, mode, field, extra):
    """PROBE F1: the check mode answered `ok` over `WITHOUT_DOCUMENTS`, which the environment mode refuses."""
    def row(profiles):
        return service.run(mode, [{"id": "x", "environment": environment(profiles=sorted(profiles + extra)),
                                   **field}])[0]
    assert row(WITHOUT_DOCUMENTS) == {"id": "x", "status": "error", "error": REQUIRES}
    assert row(PROFILES)["status"] == "ok", row(PROFILES)
    assert row([p for p in WITHOUT_DOCUMENTS if p != "judgments@0"])["status"] == "ok"


def test_the_english_route_checks_the_layer_s_own_requirement(service):
    """The English reader's block branch (`EnglishGrammar.Run.environmentId` under `norm-defaults@0`) over a
    `judgments@0` environment Python builds: read with `documents@1`, refused without it by the environment mode's
    text, before the lexicon's binding."""
    from test_acts_profile import seek_environment
    from ve import english
    from ve.backends import english_lean
    from ve.environment import Environment
    written = ["acts@0", "documents@1", "judgments@0", "norm-defaults@0", "norms@0", "relational-fol@0"]
    env = Environment(seek_environment(written))
    case = english_lean.request(env, "Alice may seek asylum.", english.EnglishVocabulary(env), {})
    [read] = service.run("english.read", [case])
    assert read["status"] == "ok" and read["result"]["status"] == "one", read
    case["environment"]["profiles"] = [p for p in written if p != "documents@1"]
    assert service.run("english.read", [case])[0] == {"id": case["id"], "status": "error", "error": REQUIRES}


# `ve document` on a `judgments@0` document (DELTA row 1, the DRI's item 2) and on its twin.

FOL = ["definitions@0", "documents@1", "judgments@0", "relational-fol@0"]
NO_NORMS = {**VOCAB, "predicates": {k: v for k, v in VOCAB["predicates"].items() if "regulated" not in v}}
DOCUMENTS = {
    "J-alpha": (STATUS["J-alpha"], VOCAB, PROFILES),
    "J-chi": (STATUS["J-chi"], VOCAB, PROFILES),
    "J-xi-prime": (STATUS["J-xi-prime"], VOCAB, PROFILES),
    "fol": ((J1, [unit("u1", opened("arbitrary"), {"ast": UPSILON}),
                  unit("u2", content={"ast": ["forall", "act", ["implies", u("unlawful_detention"), u("detention")]]})],
             (), ["OPEN", "CHECKED"], None), NO_NORMS, FOL),
    "pilot": (STATUS["J-alpha"], PLAIN, PILOT),
}


@pytest.fixture(scope="module")
def texts(service, tmp_path_factory):
    """Each document and its twin, written once."""
    directory = tmp_path_factory.mktemp("judged")
    out = {}
    for name, ((records, units, sets, *_), vocabulary, profiles) in DOCUMENTS.items():
        for tag, ps in (("judged", profiles), ("twin", [p for p in profiles if p != "judgments@0"])):
            path = directory / f"{name}-{tag}.ve.md"
            path.write_text(document(service, units, records, sets=sets, vocabulary=vocabulary, profiles=ps))
            out[name, tag] = path
    return out


@pytest.mark.parametrize("name", DOCUMENTS)
def test_ve_document_loads_as_the_twin_with_identities_of_its_own(texts, name):
    from ve.document import load_document
    judged, twin = (load_document(texts[name, tag]) for tag in ("judged", "twin"))
    assert [u["status"] for u in judged["units"]] == [u["status"] for u in twin["units"]]
    assert [u["status"] for u in judged["units"]] == DOCUMENTS[name][0][3]
    assert judged["environment"].profiles == tuple(DOCUMENTS[name][2])
    for identity in ("source_id", "document_id"):
        assert judged[identity] != twin[identity]
    assert judged["environment"].environment_id != twin["environment"].environment_id
    meanings = [(a.get("meaning_id"), b.get("meaning_id")) for a, b in zip(judged["units"], twin["units"])]
    assert all(a != b for a, b in meanings if a or b)


IDENTITIES = {"source_id", "document_id", "model_id", "environment_id", "meaning_id"}


def without_identities(value, seen):
    """`value` with every identity field's value recorded in `seen` and replaced by its key."""
    if type(value) is dict:
        return {k: (seen.append(v) or k) if k in IDENTITIES else without_identities(v, seen) for k, v in value.items()}
    if type(value) is list:
        return [without_identities(v, seen) for v in value]
    return value


@pytest.mark.parametrize("name", ["J-alpha", "J-chi", "fol"])
def test_ve_document_check_and_coverage_answer_as_the_twin(texts, name):
    from ve.document import load_document
    from ve.document.report import check_document, coverage
    for run, named in ((check_document, True), (lambda path: coverage(load_document(path)), False)):
        ids = {}
        answers = {tag: without_identities(run(texts[name, tag]), ids.setdefault(tag, [])) for tag in ("judged", "twin")}
        assert answers["judged"] == answers["twin"]
        assert bool(ids["judged"]) is named and not set(ids["judged"]) & set(ids["twin"])


@pytest.mark.parametrize("name", ["J-alpha", "J-xi-prime", "pilot"])
def test_ve_document_render_is_the_twin_s(texts, name):
    from ve.document.render import render_document
    assert render_document(texts[name, "judged"]) == render_document(texts[name, "twin"])


def test_the_pilot_list_s_replay_kinds_are_refused_by_name_until_jt_2d(texts):
    """norm-defaults' replay kinds bind their certificates to the environment they decode (jt-2d): refused by name
    under the layer, answered for the twin."""
    from ve.document.report import check_document
    from ve.errors import CheckerUnavailable
    with pytest.raises(CheckerUnavailable, match="judgments@0 with norm-defaults-gaps needs its composed Lean route"):
        check_document(texts["pilot", "judged"])
    assert json.dumps(check_document(texts["pilot", "twin"]))


def test_the_document_mode_keeps_jt_2_s_fault_order(service):
    """The document mode refuses by name only (`VE.Compose.layersApart`); the layer's requirement is its gate's over
    the list as written, after its envelope checks: a key outside the envelope is named first, with or without
    `documents@1`, as at jt-2."""
    from test_judgments_document import answer, document, outcome

    def refusal(profiles):
        head, front, body = document(service, [unit("u1", kind="meta")], J1, profiles=profiles).split("\n", 2)
        front = json.loads(front)
        front["environment"]["zzz"] = 1
        return outcome(answer(service, "\n".join([head, json.dumps(front), body])))
    keyed = refusal(PROFILES)
    assert keyed[1] is None and "zzz" in keyed[0], keyed
    assert refusal(WITHOUT_DOCUMENTS) == keyed
