"""`right-clauses@0` on the service (docs/spec/right-clauses.md 8.1, 9.1, 9.3; cmp-s3-cfr-1): the registered profile's
`clauses-elaborate` mode reads 9.1's documents in the head's order (4.1, 7), and with the profile off nothing changes
(K10, the saved 9.3 regression). Lean is the authority; the relay and the Python differential are cmp-s3-cfr-1b's."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest

from tests.lean_build import lean_build
from tests.lean_service_corpus import recorded
from tests.subprocesses import HANG_TIMEOUT
from ve.backends.lean_service import LeanService, case_digest, case_texts
from ve.backends.service_schema import Invalid, check_response

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/composition/cmp-s3-cfr-1/profile-off.json"
ENVIRONMENT = ROOT / "tests/data/right-clauses-environment.json"
OFF = ["norms@0", "relational-fol@0", "rights@0", "soft-norms@0"]
ON = ["norms@0", "relational-fol@0", "right-clauses@0", "rights@0", "soft-norms@0"]


def environment(profiles=ON):
    """9.1's environment (tests/data/right-clauses-environment.json): rights' state Texas and persons Ann, Bob, with
    the base predicates `country_of` and `charged`, and the regulated `public_service_access_required`."""
    return {**json.loads(ENVIRONMENT.read_text()), "profiles": profiles}


def document(**keys):
    """Right `r21` (holder person, guard top) with the claim line `equal-access`, unit span [0, 100); `keys` are the
    line's head keys (`elided: []` unless given; None drops a key)."""
    line = {"kind": "claim", "norm": {"name": "equal-access", "predicate": "public_service_access_required",
                                      "sign": True, "guard": ["top"], "unless": [], "over": []},
            **{"elided": []}, **keys}
    line = {k: v for k, v in line.items() if v is not None}
    return [{"right": {"name": "r21", "holder": "person", "lines": [line]}, "span": [0, 100]}]


# `total: null` is written by omission on the service's restricted JSON (rights' `_wire`)
DEEP = ["top"]
for _ in range(65):
    DEEP = ["not", DEEP]
RELATION = {"predicate": "country_of", "slots": [0, 1], "cites": []}
CHARGED = {"role": "trigger", "formula": ["unary", "charged", ["var", 0]], "span": [10, 20]}


@pytest.fixture(scope="module")
def service():
    with LeanService(lean_build("ve_service") / "ve_service", timeout=HANG_TIMEOUT) as running:
        yield running


def exchange(service, mode, cases):
    text = json.dumps(cases, ensure_ascii=False)
    _, response = service.exchange(mode, text, len(cases), timeout=HANG_TIMEOUT)
    request = {"id": response["id"], "mode": mode, "cases": cases,
               "digests": [case_digest(t) for t in case_texts(text)], "bytes": len(text.encode())}
    check_response(mode, response, request)
    return [bound["result"] for bound in response["results"]]


def elaborate(service, *documents, profiles=ON):
    return exchange(service, "clauses-elaborate",
                    [{"id": str(i), "environment": environment(profiles), "document": d}
                     for i, d in enumerate(documents)])


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def without_head_keys(doc):
    """The profile-off document: no unit span, no line keys of the head."""
    out = deepcopy(doc)
    for unit in out:
        unit.pop("span", None)
        for body in (unit.get("right"), unit.get("right_lines")):
            for line in (body or {}).get("lines", []):
                for key in ("elided", "clauses", "relation"):
                    line.pop(key, None)
    return out


def guard(result):
    return json.loads(result["result"]["plained"])[0]["right"]["lines"][0]["norm"]["guard"]


def test_right_clauses_k1_service_identity(service):
    """K1 through the registered profile: Python models the environment (`right-clauses@0` is in the profile table's
    environment list, so Lean's environment mode gates it by the whole table), `clauses-elaborate` accepts the
    unstructured line, its plained bytes are the profile-off document's, the slot is `Lim_D = []`, and the rights
    mode answers the plained document as it answers the profile-off one."""
    from ve import Environment
    from ve.profiles import BY_NAME
    assert "right-clauses@0" in BY_NAME
    assert Environment(environment()).to_dict()["profiles"] == ON
    [k1] = elaborate(service, document())
    assert k1["status"] == "ok", k1
    off = without_head_keys(document())
    assert k1["result"] == {"plained": canonical(off), "clause_slot": []}
    plained, written = (exchange(service, "rights", [{"id": "k1", "kind": "rights-elaborate", "environment":
                                                      environment(OFF), "document": d}])[0]
                        for d in (json.loads(k1["result"]["plained"]), off))
    assert plained == written and plained["status"] == "ok", plained


# 9.1 on the service, in the head's order (4.1, 7): each document's answer, the error text or the plain guard and slot.
TOTAL = {**RELATION, "total": 1}
K_FIXTURES = {
    "K2": (document(relation=RELATION), ["and", ["top"], ["binary", "country_of", ["var", 1], ["var", 0]]], []),
    "K3": (document(relation=TOTAL), ["and", ["top"], ["binary", "country_of", ["var", 1], ["var", 0]]],
           [{"label": "rights:relation:equal-access:total",
             "ast": ["forall", "person", ["implies", ["top"], ["exists", "state",
                                                               ["binary", "country_of", ["var", 0], ["var", 1]]]]]}]),
    "K4": (document(clauses=[CHARGED], elided=[[30, 40]]), ["and", ["top"], ["unary", "charged", ["var", 0]]], []),
    "K5": (document(clauses=[{**CHARGED, "span": [90, 110]}], elided=[[30, 40]]), "ClauseSpan: equal-access: [90, 110)"),
    "K6": (document(clauses=[CHARGED], elided=[[15, 25]]), "ClauseSpan: equal-access: [15, 25)"),
    "K7": (document(clauses=[{**CHARGED, "formula": ["unary", "charged", ["var", 1]]}]),
           "InvalidInput: ill-typed clause 0 of rule equal-access"),
    "K8a": (document(relation={**RELATION, "slots": [1, 1]}), "RelationShape: equal-access"),
    "K8b": (document(relation={**RELATION, "total": 0}), "RelationShape: equal-access"),
    "K9": (document(elided=None), "InvalidInput: elided missing on rule equal-access"),
    "K15": (document(elided=None, clauses=[]), "InvalidInput: elided missing on rule equal-access"),
    "two-relations": (document(relation=[RELATION, TOTAL]), "InvalidInput: invalid relation of rule equal-access"),
    "relation-key": (document(relation={**RELATION, "extra": 1}), "InvalidInput: invalid relation of rule equal-access"),
    "elided-shape": (document(elided=[[1, 2, 3]]), "InvalidInput: invalid elided of rule equal-access"),
    "clauses-empty": (document(clauses=[]), "InvalidInput: invalid clauses of rule equal-access"),
    "clause-role": (document(clauses=[{**CHARGED, "role": "reason"}]),
                    "InvalidInput: invalid clause 0 of rule equal-access"),
    "unit-span": ([{**document()[0], "span": [0]}], "InvalidInput: invalid unit span"),
    "roles": (document(clauses=[{**CHARGED, "role": "scope"}, {**CHARGED, "role": "object", "span": [20, 30]}]),
              ["and", ["and", ["top"], ["unary", "charged", ["var", 0]]], ["unary", "charged", ["var", 0]]], []),
    "deep-clause": (document(clauses=[{**CHARGED, "formula": DEEP}]), "ResourceLimit: formula depth exceeds 64"),
    "relation-cites": (document(relation={**RELATION, "cites": [1]}), "InvalidInput: invalid relation of rule equal-access"),
    "elided-scalar": (document(elided=5), "InvalidInput: invalid elided of rule equal-access"),
    "clauses-scalar": (document(clauses=5), "InvalidInput: invalid clauses of rule equal-access"),
    "no-unit-span": ([{"right": document(clauses=[CHARGED])[0]["right"]}], "ClauseSpan: equal-access: [10, 20)"),
}


def test_right_clauses_k_fixtures_service(service):
    """K2 to K9, K15 and the decoder's refusals: structured lines plain into the guard (1.2), a total relation adds
    its premise to the slot after `Lim_D` (1.3), and each refusal is section 7's text, in 4.1's order."""
    results = elaborate(service, *(fixture[0] for fixture in K_FIXTURES.values()))
    for name, fixture, result in zip(K_FIXTURES, K_FIXTURES.values(), results):
        if isinstance(fixture[1], str):
            assert result == {"id": result["id"], "status": "error", "error": fixture[1]}, name
        else:
            assert result["status"] == "ok", (name, result)
            assert guard(result) == fixture[1] and result["result"]["clause_slot"] == fixture[2], name
            [unit] = json.loads(result["result"]["plained"])
            assert set(unit) == {"right"} and [set(line) for line in unit["right"]["lines"]] == [{"kind", "norm"}], name


def test_right_clauses_k10_profile_off(service):
    """K10: with the profile off, K2's line is refused by the rights decoder with today's text, and the
    `clauses-elaborate` mode refuses the list (its head is not listed)."""
    [rights] = exchange(service, "rights", [{"id": "k10", "kind": "rights-elaborate", "environment": environment(OFF),
                                             "document": [{"right": document(relation=RELATION)[0]["right"]}]}])
    assert rights["error"] == "fields do not match: expected [kind, norm], got [elided, kind, norm, relation]", rights
    [head] = elaborate(service, document(), profiles=OFF)
    assert head["error"] == "UnsupportedProfile: clauses-elaborate requires right-clauses@0", head


def _answer_digest(row) -> str:
    return hashlib.sha256(canonical({k: v for k, v in row.items() if k != "id"}).encode()).hexdigest()


def test_right_clauses_profile_off_evidence():
    """9.3, profile off, as saved evidence (docs/composition/cmp-s3-cfr-1/profile-off.json): the rights mode's answers
    to the recorded rights route cases have the same digests on this item's build as on the base build."""
    saved = json.loads(EVIDENCE.read_text())
    assert saved["head_answers"] == saved["answers"] and saved["head_cases"] == saved["cases"]
    assert len(saved["answers"]) == len(saved["cases"]) > 0 and saved["commit"] != saved["head_commit"]


def test_right_clauses_profile_on_regression(service):
    """9.3, profile on: each recorded rights case's array document, with `elided: []` on every line, elaborates to
    itself (`plain_identity`) and the rights mode answers the plained document as the written one, verdicts and
    statuses included; or the head refuses it with the profile-off answer's own text."""
    cases = [c for c in recorded("rights") if type(c.get("document")) is list and
             "rights@0" in c.get("environment", {}).get("profiles", [])]
    on = []
    for case in cases:
        doc = deepcopy(case["document"])
        for unit in doc:
            for body in (unit.get("right"), unit.get("right_lines")):
                for line in body.get("lines", []) if type(body) is dict else []:
                    line["elided"] = []
        profiles = sorted({*case["environment"]["profiles"], "right-clauses@0"})
        on.append({"id": case["id"], "environment": {**case["environment"], "profiles": profiles}, "document": doc})
    heads = exchange(service, "clauses-elaborate", on)
    answers = exchange(service, "rights", cases)
    assert cases and any(head["status"] == "ok" for head in heads)
    plained = [(case, head, answer) for case, head, answer in zip(cases, heads, answers) if head["status"] == "ok"]
    again = exchange(service, "rights", [{**case, "document": json.loads(head["result"]["plained"])}
                                         for case, head, _ in plained])
    for (case, head, answer), rerun in zip(plained, again):
        assert json.loads(head["result"]["plained"]) == case["document"] and rerun == answer, case["id"]
    for case, head, answer in zip(cases, heads, answers):
        if head["status"] != "ok":
            assert head["error"] == answer["error"], (case["id"], head, answer)


def test_right_clauses_environment_texts_kept():
    """Registration changes an environment answer only where the profile is listed with every rights profile, and
    there the answer is the same list's without `right-clauses@0`. Saved (environment-texts.json, the probe at the base
    build and at this item's): no text of the 154 lists without rights@0 moves, and the 37 rights lists that move each
    answer as without the profile. Live: beside `acts@0` or without `rights@0` the text is the base's; every rights
    list with up to two more profiles answers as without the profile, or refuses the profile by name as the base did."""
    from itertools import combinations
    from ve import Environment
    from ve.errors import UnsupportedProfile
    saved = json.loads((EVIDENCE.parent / "environment-texts.json").read_text())
    assert saved["differ"] == [] and len(saved["texts"]) == 154 and len(saved["rights"]) == 106
    moved = sorted(k for k, v in saved["rights"].items() if v["base"] != v["head"])
    assert moved == saved["rights_differ"] and len(moved) == 37
    assert all(saved["rights"][k]["head"] == saved["rights"][k]["off"] for k in moved)
    acts = environment(["acts@0", "norms@0", "relational-fol@0", "right-clauses@0"])
    acts["vocabulary"]["acts"] = {"fixed": []}
    del acts["vocabulary"]["rights"]
    soft = environment(["norms@0", "relational-fol@0", "right-clauses@0", "soft-norms@0"])
    del soft["vocabulary"]["rights"]
    for env in (acts, soft):
        with pytest.raises(UnsupportedProfile, match="^UnsupportedProfile: Unsupported profile right-clauses@0$"):
            Environment(env)
    assert Environment(environment()).to_dict()["profiles"] == ON

    def text(profiles):
        env = environment(profiles)
        if "acts@0" in profiles:
            env["vocabulary"]["acts"] = {"fixed": []}
        try:
            return Environment(env) and "ok"
        except UnsupportedProfile as refusal:
            return str(refusal)
    by_name = {"UnsupportedProfile: Unsupported profile right-clauses@0",
               "UnsupportedProfile: speech-acts@0 with right-clauses@0",
               "UnsupportedProfile: readings@1 is not the head of this profile list"}
    others = sorted({p for k in saved["texts"] for p in k.split(",")} - set(ON))
    # a document layer: the composed gate after the layer's own (`validatedComposedEnvironment`)
    layered = sorted({*ON, "documents@1", "judgments@0"})
    assert text(layered) == text([p for p in layered if p != "right-clauses@0"]) == "ok"
    for k in (0, 1, 2):
        for extra in combinations(others, k):
            on = sorted({*ON, *extra})
            answer, off = text(on), text([p for p in on if p != "right-clauses@0"])
            assert answer == off or answer in by_name, (on, answer, off)
            assert answer == saved["rights"][",".join(on)]["head"] or answer == off, on


def test_right_clauses_environment_and_model_answer_as_without_the_profile(service):
    """DRI condition (dri-decisions-20261109-cmp-s3-cfr-1 item 4): the profile carries nothing into the environment and
    model modes. The environment mode answers an environment listing `right-clauses@0` as the same environment without
    it, but for the profile list it echoes and the identity, which binds that list (spec 3). The model mode decides no model under the profile.
    Lean checks the environment, then the model's tables, then the profile list: a well-formed model is refused by the
    name, as on main, and the same model without it is valid; a faulty model gets the answer it gets without the profile
    (cmp-s3-cfr-1 review F2: main refused it by the name). Python's model view drops the profile (`MODEL_REDUCTIONS`),
    so no relay asks it."""
    on, off = (exchange(service, "environment", [{"id": "e", "environment": environment(ps)}])[0] for ps in (ON, OFF))
    assert on["environment_id"] != off["environment_id"] and on["profiles"] == ON and off["profiles"] == OFF
    bound = ("environment_id", "profiles")
    assert {k: v for k, v in on.items() if k not in bound} == {k: v for k, v in off.items() if k not in bound}
    # one of the 37 moved lists that the norms route refuses (dri-decisions-20261110-cmp-s3-cfr-1-env item 1)
    refused = [exchange(service, "environment", [{"id": "e", "environment": environment(sorted({*ps, "closure@0"}))}])[0]
               for ps in (ON, OFF)]
    assert refused[0] == refused[1] == {"id": "e", "status": "error",
                                        "error": "UnsupportedProfile: the norms route admits FOL documents only"}
    model = {"complete": True, "domains": {"state": ["texas"], "person": ["ann", "bob"]},
             "constants": {"texas": "texas", "ann": "ann", "bob": "bob"},
             "relations": {"charged": [["ann"]], "country_of": [["texas", "ann"]], "public_service_access_required": []}}
    on, off = (exchange(service, "model", [{"id": "m", "environment": environment(ps), "model": model}])[0]
               for ps in (ON, OFF))
    assert on == {"id": "m", "status": "error", "error": "UnsupportedProfile: Unsupported profile right-clauses@0"}
    assert off["status"] == "ok" and off["valid"] is True
    # review F2's two faulty models: the same InvalidModel answer, text and path, with and without the profile
    for faulty, error, path in ((_replaced(model, ("relations", "charged", 0, 0), "zed"),
                                 "InvalidModel: relation tuple contains a dangling or wrong-sort entity",
                                 "/relations/charged/0/0"),
                                (_replaced(model, ("relations", "charged"), 5),
                                 "InvalidModel: relation must be an array", None)):
        on, off = (exchange(service, "model", [{"id": "m", "environment": environment(ps), "model": faulty}])[0]
                   for ps in (ON, OFF))
        assert on == off and off["status"] == "error" and off["error"] == error
        assert path is None or off["path"] == path
    # the path a model request takes: Python's model view of the environment, then Lean's model mode
    from ve.profiles import model_environment
    viewed = [model_environment(environment(ps)) for ps in (ON, OFF)]
    assert viewed[0] == viewed[1] and "right-clauses@0" not in viewed[0]["profiles"]
    on = exchange(service, "model", [{"id": "m", "environment": viewed[0], "model": model}])[0]
    assert on == exchange(service, "model", [{"id": "m", "environment": viewed[1], "model": model}])[0]
    assert on["status"] == "ok" and on["valid"] is True


def _replaced(value, path, new):
    """`value` with the node at `path` replaced by `new` (a copy)."""
    if not path:
        return new
    out = deepcopy(value)
    node = out
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = new
    return out


def _node_paths(value, path=()):
    yield path
    items = value.items() if isinstance(value, dict) else enumerate(value) if isinstance(value, list) else ()
    for key, child in items:
        yield from _node_paths(child, (*path, key))


def test_right_clauses_model_mode_faulty_models_answer_as_without_the_profile(service):
    """Review F2 as a class: every one-node mutation of a valid 9.1 model (each node replaced by 7, true, null, [], {}
    or a dangling entity, and each object key dropped) gets, with `right-clauses@0` listed, exactly the answer it gets
    without the profile when that answer is a fault; a model that holds without the profile is refused by the name.
    So the model mode decides no model under the profile, and adds no answer of its own (DELTA row 1)."""
    model = {"complete": True, "domains": {"state": ["texas"], "person": ["ann", "bob"]},
             "constants": {"texas": "texas", "ann": "ann", "bob": "bob"},
             "relations": {"charged": [["ann"]], "country_of": [["texas", "ann"]], "public_service_access_required": []}}
    mutants = []
    for path in _node_paths(model):
        mutants += [_replaced(model, path, new) for new in (7, True, None, [], {}, "zed")]
        if path:
            parent = model
            for key in path[:-1]:
                parent = parent[key]
            if isinstance(parent, dict):
                dropped = deepcopy(model)
                node = dropped
                for key in path[:-1]:
                    node = node[key]
                del node[path[-1]]
                mutants.append(dropped)
    on, off = ([{"id": f"m{i}", "environment": environment(ps), "model": m} for i, m in enumerate(mutants)]
               for ps in (ON, OFF))
    on, off = exchange(service, "model", on), exchange(service, "model", off)
    refused = {"status": "error", "error": "UnsupportedProfile: Unsupported profile right-clauses@0"}
    faulty = [i for i, answer in enumerate(off) if answer["status"] == "error"]
    for a, b in zip(on, off):
        assert a == (b if b["status"] == "error" else {"id": b["id"], **refused}), (a, b)
    # the sweep reaches both sides: faulty models of several kinds, and models that hold without the profile
    assert len(faulty) >= 40 and len(mutants) - len(faulty) >= 1
    assert len({off[i]["error"] for i in faulty}) >= 4 and any("path" in off[i] for i in faulty)


# cmp-s3-cfr-1b: the relay (ve/right_clauses.py) against Lean's mode on 9.1 and 9.2's documents (9.3's differential)
def _env(sorts=(), predicates=None, profiles=ON):
    env = environment(profiles)
    env["vocabulary"]["sorts"].update({s: {"description": s} for s in sorts})
    env["vocabulary"]["predicates"].update(predicates or {})
    return env


def _spanned(doc, a, b):
    doc[0]["span"] = [a, b]
    return doc


def _base(*names, sorts=("person",)):
    return {n: {"arguments": list(sorts), "description": "base"} for n in names}


NORM = document()[0]["right"]["lines"][0]["norm"]
POWER = {"kind": "power", "liberty": {**NORM, "name": "may-access"}, "recognition": {**NORM, "name": "recognise-access"},
         "elided": [], "relation": RELATION}
L29 = {"limitation": {"name": "l29", "scope": "all", "kinds": "all", "decided_by": "unstated", "factors": [],
                      "conditions": [{"name": "determined_by_law", "role": "necessary", "verbalisation": "by law"}]}}
F11_TRIGGER = {"role": "trigger", "span": [3541, 3635], "formula": ["exists", "act", ["and", ["binary",
               "violates_right_of", ["var", 0], ["var", 1]], ["unary", "right_granted_by_law", ["var", 0]]]]}
VULNERABLE = {"vulnerable": {"arguments": ["person"], "description": "plain", "regulated": {"role": "plain", "default": "deny"}}}
DIFFERENTIAL = {
    "K1": (environment(), document()),
    **{name: (environment(), fixture[0]) for name, fixture in K_FIXTURES.items()},
    "K10": (environment(OFF), document(relation=RELATION)),
    "K11": (environment(), [{"right": {"name": "r21", "holder": "person", "lines": [POWER]}, "span": [0, 100]}]),
    "K12": (environment(sorted([*ON, "readings@1"])), document(relation=TOTAL)),
    "K13": (environment(), document(relation=TOTAL) + [L29]),
    "K14": (_env(predicates=VULNERABLE), [{**document(relation=TOTAL)[0], "right": {
        **document(relation=TOTAL)[0]["right"], "guard": ["unary", "vulnerable", ["var", 0]]}}]),
    "F11": (_env(["act"], {**_base("right_granted_by_law", sorts=["act"]), **_base("violates_right_of", sorts=["act", "person"]),
                           **_base("has_tribunals_competent_for", sorts=["state", "person"])}),
            _spanned(document(clauses=[F11_TRIGGER], relation={**TOTAL, "predicate": "has_tribunals_competent_for",
                                                                "cites": ["u035"]}), 3469, 3637) + [{"source_units": ["u035"]}]),
    "F12": (_env(predicates=_base("rights_and_charges_determined", "full_equality")), _spanned(document(clauses=[
        {"role": "scope", "span": [3838, 3934], "formula": ["unary", "rights_and_charges_determined", ["var", 0]]},
        {"role": "scope", "span": [3755, 3771], "formula": ["unary", "full_equality", ["var", 0]]}]), 3734, 3935)),
    "F14": (environment(), _spanned(document(relation=RELATION), 6861, 6938)),
}
PINNED = {"K10": "UnsupportedProfile: clauses-elaborate requires right-clauses@0", "K11": "ClauseLineShape: may-access",
          "K12": "UnsupportedProfile: right-clauses@0 with readings@1 is not implemented",
          "K14": "RelationShape: equal-access"}


def test_right_clauses_differential(service):
    """9.3: the relay's answer is Lean's, byte for byte, on K1 to K15, F11, F12 and F14: the plained bytes and the slot
    when Lean reads the document, Lean's text (raised as its class) when it refuses it. K13's slot lists `Lim_D`'s
    premise before `Rel_D`'s; F11's totality premise names its rule."""
    from ve import right_clauses
    from ve.errors import VEError
    lean = exchange(service, "clauses-elaborate", [{"id": k, "environment": e, "document": d}
                                                   for k, (e, d) in DIFFERENTIAL.items()])
    for (name, (env, doc)), row in zip(DIFFERENTIAL.items(), lean):
        if row["status"] == "error":
            with pytest.raises(VEError) as refusal:
                right_clauses.elaborate(env, doc)
            assert str(refusal.value) == row["error"] == PINNED.get(name, row["error"]), name
            continue
        relayed = right_clauses.elaborate(env, doc)
        assert relayed.plained == row["result"]["plained"] and name not in PINNED, name
        assert [{"label": label, "ast": ast} for label, ast in relayed.clause_slot] == row["result"]["clause_slot"], name
    labels = {row["id"]: [r["label"] for r in row["result"]["clause_slot"]] for row in lean if row["status"] == "ok"}
    assert labels["K13"] == ["rights:limitation:l29:public_service_access_required:necessary:determined_by_law",
                             "rights:relation:equal-access:total"]
    assert labels["F11"] == ["rights:relation:equal-access:total"] and labels["F12"] == labels["F14"] == []


def _bound(result, doc):
    from ve.backends.lean_service import CheckerUnavailable
    from ve.right_clauses import bind
    try:
        return bind(result, doc)
    except CheckerUnavailable:
        return None


def test_right_clauses_relay_binds_every_field(service):
    """R8: every unit, line and label of the answer is the request's. Each field of a genuine answer retyped fails the
    schema; each rebound (a unit, line or premise dropped, added or renamed) is `CheckerUnavailable`."""
    names = ["K3", "K13", "F11"]
    rows = exchange(service, "clauses-elaborate", [{"id": k, "environment": DIFFERENTIAL[k][0], "document":
                                                   DIFFERENTIAL[k][1]} for k in names])
    for name, row in zip(names, rows):
        doc, result = DIFFERENTIAL[name][1], row["result"]
        assert _bound(result, doc) is not None, name
        units = json.loads(result["plained"])
        renamed = deepcopy(units)
        renamed[0]["right"]["lines"][0]["norm"]["name"] = "other"
        plained = [units[:-1], units + [units[0]], renamed, [{"bar": units[0]}] + units[1:], units[0]]
        slots = [result["clause_slot"][:-1], result["clause_slot"] + result["clause_slot"][-1:],
                 [{**r, "label": r["label"].replace("equal-access", "other")} for r in result["clause_slot"]],
                 [{**r, "label": r["label"].replace("determined_by_law", "other")} for r in result["clause_slot"]],
                 [{**r, "label": r["label"].replace("l29", "l30")} for r in result["clause_slot"]]]
        for mutant in [{**result, "plained": canonical(p)} for p in plained] + [{**result, "plained": "["}] + [
                {**result, "clause_slot": s} for s in slots if s != result["clause_slot"]]:
            assert _bound(mutant, doc) is None, (name, mutant)
        case = [{"id": "0", "environment": DIFFERENTIAL[name][0], "document": doc}]
        text = json.dumps(case, ensure_ascii=False)
        _, response = service.exchange("clauses-elaborate", text, 1, timeout=HANG_TIMEOUT)
        request = {"id": response["id"], "mode": "clauses-elaborate", "cases": case,
                   "digests": [case_digest(t) for t in case_texts(text)], "bytes": len(text.encode())}
        check_response("clauses-elaborate", response, request)
        for path, value in [(("plained",), 1), (("plained",), None), (("clause_slot",), {}),
                            (("clause_slot", 0, "label"), 7), (("clause_slot", 0, "ast"), "top"), (("clause_slot", 0), [])]:
            bad = deepcopy(response)
            target = bad["results"][0]["result"]["result"]
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            with pytest.raises(Invalid):
                check_response("clauses-elaborate", bad, request)


def _tree(n):
    return ["unary", "charged", ["var", 0]] if n == 1 else ["and", _tree(n // 2), _tree(n - n // 2)]


def _sized(sizes):
    """One line per entry of `sizes`, each on its own obligation, with one clause of that many atoms."""
    env = environment()
    regulated = env["vocabulary"]["predicates"]["public_service_access_required"]
    acts = ["food", "water", "housing", "schooling", "care", "work"]
    lines = []
    for i, n in enumerate(sizes):
        env["vocabulary"]["predicates"][f"p{i}_required"] = {**regulated, "regulated": {
            **regulated["regulated"], "act": "{0} give {1} access to " + acts[i]}}
        lines.append({**document()[0]["right"]["lines"][0], "norm": {**NORM, "name": f"a{i}", "predicate": f"p{i}_required"},
                      "clauses": [{"role": "scope", "formula": _tree(n), "span": [1, 2]}]})
    return {"environment": env, "document": [{"right": {"name": "r21", "holder": "person", "lines": lines}, "span": [0, 100]}]}


def test_right_clauses_w1_budget(service):
    """W1's 10,000-node budget on `plain D` (spec 10) and the evaluator rule of 2026-10-27: a large well-formed
    document (four lines, 400-atom clauses) is read; four 833-atom clauses pass the node budget (the generated layers'
    budget then refuses them) and one atom more does not. The head charges what it reads before the quadratic or deep
    work: 257 line objects, a line of 64 conjuncts, and long span and cite lists end within the deadline."""
    spans = document(elided=[[2 * i, 2 * i + 1] for i in range(30000)])
    spans[0]["span"] = [0, 60002]
    ids = [f"u{i}" for i in range(20000)]
    deep = document(clauses=[{**CHARGED, "role": "scope", "span": [i, i + 1]} for i in range(64)])
    many = [{"right": {**document()[0]["right"], "lines": [document()[0]["right"]["lines"][0]] * 257}}]
    cases = [_sized([400] * 4), _sized([833] * 4), _sized([833] * 3 + [834]),
             {"environment": environment(), "document": many}, {"environment": environment(), "document": deep},
             {"environment": environment(), "document": spans},
             {"environment": environment(), "document": document(relation={**RELATION, "cites": ids[::-1]}) +
              [{"source_units": ids}]}]
    rows = exchange(service, "clauses-elaborate", [{"id": str(i), **c} for i, c in enumerate(cases)])
    assert [r.get("error") for r in rows] == [
        None, "ResourceLimit: generated norm layers", "ResourceLimit: AST exceeds 10,000 nodes", "ResourceLimit: rules",
        "ResourceLimit: formula depth exceeds 64", None, None]
    assert len(json.loads(rows[0]["result"]["plained"])[0]["right"]["lines"]) == 4


def test_right_clauses_rights_environment_reads_the_profile():
    """Python's rights environment reads `right-clauses@0` (its soft frame drops it, as Lean's `withoutClauses`): the
    environment is the one without the profile but for the list it binds (DELTA row 1), and a faulty one is refused
    with the same text. Without rights@0 the profile is still refused by name."""
    from ve.errors import VEError
    from ve.profiles import model_environment
    from ve.rights import RightsEnvironment
    on, off = RightsEnvironment(environment()), RightsEnvironment(environment(OFF))
    assert on.to_dict() == {**off.to_dict(), "profiles": ON} and on.environment_id != off.environment_id
    assert model_environment(environment()) == model_environment(environment(OFF))
    for profiles in (ON, OFF):
        bad = environment(profiles)
        bad["vocabulary"]["rights"]["holders"] = ["citizen"]
        with pytest.raises(VEError) as refusal:
            RightsEnvironment(bad)
        assert str(refusal.value) == "UnknownSymbol: sort citizen"
    with pytest.raises(VEError, match="^UnsupportedProfile: rights@0 is required$"):
        RightsEnvironment(environment([p for p in ON if p != "rights@0"]))
