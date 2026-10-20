"""act-phrases AP-1, the profile part (ap-1b): `acts@0` documents loaded, checked and refused by Lean.

Python loads the `acts` block and a plain declaration's `form` as data and decides nothing: the environment
mode accepts or refuses the environment, the norms route checks the document, and every text below is Lean's,
relayed. Rust refuses every `acts@0` environment (`UnsupportedProfile`). The Lean fixtures of the same
behaviour are `#guard`s in `lean/VE/Service/ActsExamples.lean` and `lean/VE/Compose/Examples.lean`.
"""
from __future__ import annotations

import copy

import pytest

from tests import lean_routes
from ve.environment import Environment
from ve.errors import VEError

pytestmark = pytest.mark.skipif(not lean_routes.SERVICE.exists(), reason="ve_service is not built")

A1 = "{0} in full equality to a fair and public hearing by an independent and impartial tribunal in {1}"
A2 = "{0} to equal pay for equal work without any discrimination"
A3 = "{0} to the protection of the moral and material interests resulting from {1}"
A5 = "{0} to seek and to enjoy in other countries asylum from persecution"
A6 = "{0} be subjected to torture or to cruel, inhuman or degrading treatment or punishment"
FIXED = ["a fair and public hearing by an independent and impartial tribunal", "equal pay for equal work",
         "the moral and material interests", "cruel, inhuman or degrading treatment or punishment"]


def predicate(arguments, regulated):
    return {"arguments": arguments, "description": "d", "regulated": regulated}


ENV = {
    "language": "ve.core@0.2", "profiles": ["acts@0", "norms@0", "relational-fol@0"],
    "spec_revision": "ve-v0.2-expand2-2026-09-25",
    "vocabulary": {
        "sorts": {"person": {"description": "person"}, "case": {"description": "case"}},
        "predicates": {
            "heard": predicate(["person", "case"], {"role": "plain", "default": "deny", "act": A1,
                                                    "form": "is entitled"}),
            "paid": predicate(["person"], {"role": "plain", "default": "deny", "act": A2, "form": "has the right"}),
            "protected": predicate(["person", "case"], {"role": "permission", "default": "allow", "act": A3}),
        },
        "constants": {},
        "acts": {"fixed": FIXED},
    },
}


def environment(profiles=None, **predicates):
    data = copy.deepcopy(ENV)
    if profiles is not None:
        data["profiles"] = profiles
    data["vocabulary"]["predicates"].update(predicates)
    return data


def refusal(data) -> str:
    with pytest.raises(VEError) as caught:
        Environment(data)
    return str(caught.value)


def test_an_acts_environment_loads_with_its_block_and_forms_as_data():
    env = Environment(environment())
    stored = env.to_dict()
    assert stored["vocabulary"]["acts"] == {"fixed": FIXED}
    assert stored["vocabulary"]["predicates"]["heard"]["regulated"] == {
        "role": "plain", "default": "deny", "act": A1, "form": "is entitled"}
    assert env.predicates["paid"].regulated.form == "has the right"
    from ve.background import background
    assert type(background(env)) in (list, tuple)  # Lean's plain route reads the profile (it refused it before)
    # the identity Python stores is the one Lean computed over the same bytes (the constructor binds it)
    assert env.environment_id.startswith("sha256:") or len(env.environment_id) > 16


@pytest.mark.parametrize("act, fixed, word", [(A5, [], "and"), (A6, FIXED, "or")], ids=["A5", "A6"])
def test_a_joined_act_is_refused_with_leans_text(act, fixed, word):
    data = environment(p=predicate(["person"], {"role": "plain", "default": "deny", "act": act,
                                                "form": "has the right"}))
    data["vocabulary"]["acts"]["fixed"] = fixed
    del data["vocabulary"]["predicates"]["heard"], data["vocabulary"]["predicates"]["protected"]
    if not fixed:
        del data["vocabulary"]["predicates"]["paid"]
    assert refusal(data) == f"InvalidInput: act phrase for p joins acts with '{word}' outside a fixed phrase"


@pytest.mark.parametrize("profiles, text", [
    (["acts@0", "norms@0", "relational-fol@0", "soft-norms@0"], "acts@0 with soft-norms@0 is not implemented"),
    (["acts@0", "closure@0", "norms@0", "relational-fol@0"], "acts@0 on the closure family is not implemented"),
    (["acts@0", "relational-fol@0"], "acts@0 requires norms@0"),
], ids=["soft-norms", "closure", "no-norms"])
def test_the_rows_refusals_come_first(profiles, text):
    assert refusal(environment(profiles)) == f"UnsupportedProfile: {text}"
    # the plain route gates the submitted list too, before it sets the statement layers aside (ap-1b review C1)
    [row] = lean_routes.rows("norms", [{"id": "b", "kind": "background", "environment": environment(profiles)}])
    assert row.get("error") == f"UnsupportedProfile: {text}", row


def test_without_acts_the_block_and_a_plain_act_are_refused_as_today():
    data = environment(["norms@0", "relational-fol@0"])
    assert refusal(data).startswith("InvalidInput: invalid regulated fields for heard")
    del data["vocabulary"]["predicates"]["heard"], data["vocabulary"]["predicates"]["paid"]
    data["vocabulary"]["predicates"]["protected"]["regulated"]["act"] = "{0} be protected in {1}"
    assert "fields do not match" in refusal(data)


def test_the_norms_route_checks_rules_on_acts():
    """Lean replays the certificates of a document with a plain act and a long permission act; a contradicting
    pair of rules on the plain act is not certified free of conflict."""
    from ve.norms import NormDocument, check_conflict

    def report(*rules):
        units = [{"norm": {"name": name, "predicate": p, "sign": sign, "guard": ["top"], "unless": [], "over": []}}
                 for name, p, sign in rules]
        return check_conflict(NormDocument(Environment(environment()), units), prove=True)
    assert report(("m", "heard", True), ("n", "protected", True)).status == "CONFLICT-FREE"
    assert report(("m", "heard", True), ("n", "heard", False)).status != "CONFLICT-FREE"


def test_rust_refuses_an_acts_environment():
    from ve.backends import rust_jsonl
    from ve.errors import UnsupportedProfile
    case = {"id": "acts", "kind": "check", "ast": ["top"], "environment": environment()}
    with pytest.raises(UnsupportedProfile) as caught:
        rust_jsonl.run(case)
    assert "acts@0" in str(caught.value)


def test_an_act_python_stores_differently_is_unavailable_never_answered():
    """Lean's canonical act folds U+2019 (A19); Python's stored act does not, so the identities differ and the load is
    CheckerUnavailable until Python reads the canonical environment from Lean (ap-1bb)."""
    from ve.errors import CheckerUnavailable
    data = environment(p=predicate(["person", "case"], {"role": "permission", "default": "allow",
                                                        "act": "{0} comply with the operator’s instructions in {1}"}))
    with pytest.raises(CheckerUnavailable, match="identities differ"):
        Environment(data)


UNSORTED = [["norms@0", "acts@0", "relational-fol@0"], ["acts@0", "acts@0", "norms@0", "relational-fol@0"],
            ["relational-fol@0", "acts@0", "norms@0"], ["acts@0", "soft-norms@0", "norms@0", "relational-fol@0"]]


@pytest.mark.parametrize("profiles", UNSORTED, ids=["out-of-order", "twice", "reversed", "layer-out-of-order"])
def test_an_acts_list_that_is_not_sorted_and_unique_is_refused_as_the_base_refuses_it(profiles):
    """ap-1b review F1: `acts@0` is read only from a sorted unique list, so every route refuses the others with the
    base's text, before any other fault (the norms modes, norm-defaults and the environment mode)."""
    from tests.test_norms import rule
    sorted_refusal = "UnsupportedProfile: profiles must be sorted and unique"
    data = environment(profiles)
    norms = [rule("m", "heard", True).to_dict()]
    for route, case in [("norms", {"kind": "background"}), ("norms", {"kind": "norms-elaborate", "norms": norms}),
                        ("norm-defaults", {"kind": "norms-elaborate", "norms": norms})]:
        [row] = lean_routes.rows(route, [{"id": "b", "environment": data, **case}])
        assert row.get("status") == "error" and row["error"] == sorted_refusal, (route, case["kind"], row)
    assert refusal(data) == sorted_refusal


def test_without_acts_an_invalid_block_is_not_read():
    """ap-1b review F2: without `acts@0` the block's phrases are not checked; the vocabulary decoder refuses the
    block as a field, whatever it holds."""
    data = environment(["norms@0", "relational-fol@0"])
    del data["vocabulary"]["predicates"]["heard"], data["vocabulary"]["predicates"]["paid"]
    data["vocabulary"]["predicates"]["protected"]["regulated"]["act"] = "{0} be protected in {1}"
    data["vocabulary"]["acts"] = {"fixed": ["the court that is competent"]}
    assert "fields do not match" in refusal(data)
    [row] = lean_routes.rows("norms", [{"id": "b", "kind": "background", "environment": data}])
    assert "fields do not match" in row.get("error", ""), row
