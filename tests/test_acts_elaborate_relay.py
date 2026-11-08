"""ap-3dc: the `acts-elaborate` relay (act-phrases 6.7) and the norms route under `acts@0` on Lean's elaborated document.

Python asks Lean for the elaborated document of an `acts@0` norms document and the map from each part to its source,
binds it to the request (`ve.norms.bound_elaboration`), and runs its conflict-witness search and prover on it, so that
their witnesses and certificates name the targets Lean has; Lean decides each verdict on the source. A split source
is refused with Lean's D-28 text wherever Python reads a name. The Lean fixtures are in
`lean/VE/Service/ActsExamples.lean` (section Relay).
"""
from __future__ import annotations

import copy

import pytest

from tests import lean_routes
from tests.test_acts_joined_route import NORM_PROFILES, environment
from tests.test_discourse_answer import _nodes, _replaced
from ve import norms as norms_module
from ve.backends import relay
from ve.backends.service_schema import Invalid, check_row
from ve.environment import Environment
from ve.errors import CheckerUnavailable, VEError
from ve.norms import NormDocument, bound_elaboration, check_conflict, check_witness

pytestmark = pytest.mark.skipif(not lean_routes.SERVICE.exists(), reason="ve_service is not built")

D28 = "InvalidInput: name one of its parts: p027 is split into p027__1, p027__2"
A7 = "{0} be held by secret vote or by equivalent free voting procedures"
A14 = ("{0} abandon its core identity or principles, claim to be human, use genuinely deceptive tactics that could "
       "harm users, endanger health or safety, or act against Anthropic's guidelines")
FX14 = ["its core identity or principles", "to be human", "genuinely deceptive tactics that could harm users",
        "health or safety", "Anthropic's guidelines"]
MODEL = {"complete": True, "domains": {"person": ["a"]}, "constants": {}, "relations": {}}


def rule(name, predicate="p027", sign=False, over=()):
    return {"norm": {"name": name, "predicate": predicate, "sign": sign, "guard": ["top"], "unless": [],
                     "over": list(over)}}


def document(data=None, rules=(rule("r027"),)):
    return NormDocument(Environment(data or environment(NORM_PROFILES)), list(rules))


def one(data, name, act, fixed, frames, role="permission"):
    data["vocabulary"]["acts"] = {"fixed": fixed, "frames": frames, "adverbs": []}
    data["vocabulary"]["predicates"] = {name: {"arguments": ["person"], "description": "d", "regulated": {
        "role": role, "default": "deny", "act": act}}}
    return data


def shown(doc):
    """What the relay shows of a document: the relayed declarations and rules, the split texts, Lean's layer labels
    and conflict targets (bound against the relayed document)."""
    relayed = doc.relayed()
    return ({p: (d.arguments, d.regulated) for p, d in relayed.env.predicates.items()},
            [r.to_dict() for r in relayed.rules], dict(doc._split),
            [label for label, _ in doc.premises()], [t[0] for t in doc.conflict_targets()])


def test_a6_gives_two_prohibitions_named_by_their_parts():
    doc = document()
    relayed = doc.relayed()
    assert sorted(relayed.env.predicates) == ["p027__1", "p027__2"]
    assert [d.regulated.act for d in relayed.env.predicates.values()] == [
        "{0} be subjected to torture", "{0} be subjected to cruel, inhuman or degrading treatment or punishment"]
    assert [(r.name, r.predicate, r.sign) for r in relayed.rules] == [("r027-a1", "p027__1", False),
                                                                     ("r027-a2", "p027__2", False)]
    assert [label for label, _ in doc.premises()] == ["layer:norms:p027__1", "layer:norms:p027__2"]
    assert doc._split == {"p027": D28}


def test_a14_gives_five_prohibitions_through_the_route():
    data = one(environment(NORM_PROFILES), "p123", A14, FX14,
               [{"head": h, "markers": [""], "split": [], "modifiers": []}
                for h in ("abandon", "claim", "use", "provide", "endanger")] +
               [{"head": "act", "markers": ["against"], "split": [], "modifiers": []}])
    relayed = document(data, [rule("r123", "p123")]).relayed()
    assert [d.regulated.act for d in relayed.env.predicates.values()] == [
        "{0} abandon its core identity or principles", "{0} claim to be human",
        "{0} use genuinely deceptive tactics that could harm users", "{0} endanger health or safety",
        "{0} act against Anthropic's guidelines"]
    assert [r.name for r in relayed.rules] == [f"r123-a{i}" for i in range(1, 6)]


def test_a7_is_one_obligation_kept_whole():
    data = one(environment(NORM_PROFILES), "p079", A7, ["equivalent free voting procedures"],
               [{"head": "held", "markers": ["by"], "split": [], "modifiers": []}], role="obligation")
    doc = document(data, [rule("r079", "p079", sign=True)])
    assert doc.relayed() is doc and doc._split == {}
    assert [t[0] for t in doc.conflict_targets()] == ["p079"]


def test_precedence_splits_pairwise():
    relayed = document(rules=(rule("r027"), rule("s027", sign=True, over=["r027"]))).relayed()
    assert [(r.name, r.over) for r in relayed.rules] == [("r027-a1", ()), ("r027-a2", ()),
                                                        ("s027-a1", ("r027-a1",)), ("s027-a2", ("r027-a2",))]


def test_differing_act_lists_are_refused_through_the_route():
    """D-24: *must* keeps the act whole and *may not* splits it, so the obligation and its dual read it differently."""
    act = "{0} use the tool or provide the data"
    data = environment(NORM_PROFILES)
    data["vocabulary"]["acts"] = {"fixed": ["the tool", "the data"], "adverbs": [], "frames": [
        {"head": h, "markers": [""], "split": [], "modifiers": []} for h in ("use", "provide")]}
    data["vocabulary"]["predicates"] = {
        "q": {"arguments": ["person"], "description": "d",
              "regulated": {"role": "obligation", "default": "deny", "act": act, "permission": "qm"}},
        "qm": {"arguments": ["person"], "description": "d",
               "regulated": {"role": "permission", "default": "deny", "act": act}}}
    doc = document(data, [rule("rq", "q", sign=True), rule("rqm", "qm")])
    with pytest.raises(VEError) as caught:
        doc.relayed()
    assert str(caught.value) == ("InvalidInput: the rules on q and its dual read its act differently; write the parts "
                                 "as separate predicates")


def test_a_joined_act_with_no_rule_is_refused_with_the_rows_diagnostic():
    with pytest.raises(VEError) as caught:
        document(rules=()).relayed()
    assert str(caught.value) == "InvalidInput: the joined act of p027 has no rule to read it by"


def test_the_conflict_search_and_prover_run_on_the_parts():
    conflicting = (rule("r027"), rule("s027", sign=True))
    found = check_conflict(document(rules=conflicting), model=MODEL)
    assert (found.status, found.target) == ("CONFLICT", "p027__1")
    assert "rule r027-a1 forbids" in found.situation and "rule s027-a1 permits" in found.situation
    resolved = (rule("r027"), rule("s027", sign=True, over=["r027"]))
    assert check_conflict(document(rules=resolved), prove=True).status == "CONFLICT-FREE"
    assert check_witness(document(rules=conflicting), "p027__2", MODEL, ["a"]) is True


@pytest.mark.parametrize("read", [
    lambda doc: doc.elaborate("p027"),
    lambda doc: doc.selection("p027"),
    lambda doc: check_witness(doc, "p027", MODEL, ["a"]),
    lambda doc: check_conflict(doc, model={**MODEL, "relations": {"p027": []}}),
], ids=["elaborate", "selection", "witness-target", "model-relation"])
def test_a_split_source_is_refused_with_leans_text(read):
    with pytest.raises(VEError) as caught:
        read(document())
    assert str(caught.value) == D28


@pytest.mark.parametrize("retained", [
    lambda doc: doc._premises_python(),
    lambda doc: norms_module._check_conflict_python(doc, model=None, certificates=None, max_evaluations=1,
                                                    prove=False, tableau_steps=1),
    lambda doc: norms_module._norm_certificate_python(doc, (), None, {}),
], ids=["premises", "conflict", "certificate"])
def test_the_retained_python_path_refuses_an_acts_document(retained):
    doc = document()
    assert norms_module._lean_route(doc)
    with pytest.raises(CheckerUnavailable, match="acts@0 is decided on Lean's norms route only"):
        retained(doc)


def test_the_route_case_relays_the_row_on_both_modes():
    """The recorded route cases (`tests/data/route-cases.jsonl`): A6 on the norms mode and, unspecified, on the
    norm-defaults mode, each answered ELABORATED with the same parts."""
    data = environment(["acts@0", "norm-defaults@0", "norms@0", "relational-fol@0"], default="unspecified")
    for mode, env in (("norms", environment(NORM_PROFILES)), ("norm-defaults", data)):
        [row] = relay.decide(mode, [{"id": "acts-elaborate", "kind": "acts-elaborate", "environment": env,
                                     "norms": [rule("r027")]}])
        assert row["verdict"] == "ELABORATED" and [p["name"] for p in row["predicates"]] == ["p027__1", "p027__2"]
        assert {p["default"] for p in row["predicates"]} == {"unspecified" if mode == "norm-defaults" else "deny"}


# Fuzz (6.7 step 5): genuine rows mutated one fault at a time; every mutant is no answer or shows nothing new.
RETYPED = (7, True, None, [], {}, "x", -1, 999, 1.5)
TEXTS = {"act", "text", "name"}  # Lean's texts and generated names, relayed verbatim (SR12): retyped, never rewritten


def _mutants(row):
    for path, value in _nodes(row):
        if not path:
            continue
        for other in RETYPED:
            if type(other) is not type(value) or (other != value and path[-1] not in TEXTS):
                yield f"{path} := {other!r}", _replaced(row, path, other)
        if type(value) is int and type(value) is not bool:
            for other in (value + 1, value - 1):
                yield f"{path} := {other}", _replaced(row, path, other)
        if type(value) is str:
            yield f"{path} := ''", _replaced(row, path, "")
            if path[-1] == "source":
                for other in ("p027", "r027", "s027", "p027__1"):
                    if other != value:
                        yield f"{path} renamed {other}", _replaced(row, path, other)
        if type(value) is list and value:
            for name, other in {"duplicated first": [value[0], *value], "reversed": value[::-1],
                                "first dropped": value[1:], "last replaced by first": [*value[:-1], value[0]]}.items():
                if other != value:
                    yield f"{path} {name}", _replaced(row, path, other)
        if type(value) is dict:
            for key in value:
                yield f"{path} without {key}", _replaced(row, path, {k: v for k, v in value.items() if k != key})
    for key in row:
        yield f"without {key}", {k: v for k, v in row.items() if k != key}


def _answered(monkeypatch, mutant):
    """Lean's `acts-elaborate` answers `mutant`, checked against the mode's schema as the client checks every row;
    every other case runs."""
    real = relay.decide

    def decide(mode, cases, **options):
        if cases[0].get("kind") != "acts-elaborate":
            return real(mode, cases, **options)
        try:
            check_row(mode, mutant, cases[0], 0)
        except Invalid as exc:
            raise CheckerUnavailable(f"CheckerUnavailable: {exc}") from exc
        return [copy.deepcopy(mutant)]
    monkeypatch.setattr(relay, "decide", decide)


@pytest.mark.parametrize("rules", [(rule("r027"), rule("s027", sign=True, over=["r027"]))], ids=["precedence"])
def test_genuine_row_mutants_never_pass_as_answers(monkeypatch, rules):
    [genuine] = relay.decide("norms", [{"id": "acts-elaborate", "kind": "acts-elaborate",
                                        "environment": environment(NORM_PROFILES), "norms": [r for r in rules]}])
    expected = shown(document(rules=rules))
    _answered(monkeypatch, genuine)
    assert shown(document(rules=rules)) == expected  # the stub replays the genuine row
    accepted = []
    for label, mutant in _mutants(genuine):
        _answered(monkeypatch, mutant)
        try:
            if shown(document(rules=rules)) != expected:
                accepted.append(label)
        except CheckerUnavailable:
            pass
    assert not accepted, accepted


def test_a_refused_row_with_a_part_or_no_text_is_no_answer():
    doc = document()
    refused = {"id": "acts-elaborate", "status": "ok", "environment_id": doc.env.environment_id, "verdict": "REFUSED",
               "diagnostic": "InvalidInput: x", "predicates": [], "rules": [], "kept": [], "split": []}
    with pytest.raises(VEError, match="InvalidInput: x"):
        bound_elaboration(doc, refused)
    for mutant in ({**refused, "kept": ["p027"]}, {k: v for k, v in refused.items() if k != "diagnostic"}):
        with pytest.raises(CheckerUnavailable):
            bound_elaboration(doc, mutant)
