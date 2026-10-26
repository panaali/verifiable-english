"""act-phrases AP-1, the profile part (ap-1b): `acts@0` documents loaded, checked and refused by Lean.

Python loads the `acts` block and a plain declaration's `form` as data and decides nothing: the environment
mode accepts or refuses the environment, the norms route checks the document, and every text below is Lean's,
relayed. Rust refuses every `acts@0` environment (`UnsupportedProfile`). The Lean fixtures of the same
behaviour are `#guard`s in `lean/VE/Service/ActsExamples.lean` and `lean/VE/Compose/Examples.lean`.
"""
from __future__ import annotations

import copy
import json

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


A19 = "{0} comply with the operator’s instructions in {1}"


def test_an_act_with_a_curly_apostrophe_has_leans_identity():
    """ap-1bb (ap-1b deviation 4): Lean's canonical act folds U+2019 (A19), so the environment's identity is the one
    Lean computed from its canonical environment, the same as for the act written with U+0027; Python computes none,
    keeps the act as written, and the norms route checks a document over it."""
    from ve.norms import NormDocument, check_conflict
    from tests.test_norms import rule
    curly = Environment(environment(p=predicate(["person", "case"], {"role": "permission", "default": "allow",
                                                                     "act": A19})))
    straight = Environment(environment(p=predicate(["person", "case"], {"role": "permission", "default": "allow",
                                                                        "act": A19.replace("’", "'")})))
    assert curly.environment_id == straight.environment_id
    assert curly.predicates["p"].regulated.act == A19
    assert check_conflict(NormDocument(curly, [rule("m", "p", True)]), prove=True).status == "CONFLICT-FREE"


UNSORTED = [["norms@0", "acts@0", "relational-fol@0"], ["acts@0", "acts@0", "norms@0", "relational-fol@0"],
            ["relational-fol@0", "acts@0", "norms@0"], ["acts@0", "soft-norms@0", "norms@0", "relational-fol@0"],
            ["norm-defaults@0", "acts@0", "norms@0", "relational-fol@0"]]


@pytest.mark.parametrize("profiles", UNSORTED, ids=["out-of-order", "twice", "reversed", "layer-out-of-order", "sorted-without-norm-defaults"])
def test_an_acts_list_that_is_not_sorted_and_unique_is_refused_as_the_base_refuses_it(profiles):
    """ap-1b review F1: `acts@0` is read only from a sorted unique list, so every route refuses the others with the
    base's text, before any other fault (the norms modes, norm-defaults and the environment mode)."""
    from tests.test_norms import rule
    sorted_refusal = "UnsupportedProfile: profiles must be sorted and unique"
    data = environment(profiles)
    norms = [rule("m", "heard", True).to_dict()]
    for route, case in [("norms", {"kind": "background"}), ("norms", {"kind": "norms-elaborate", "norms": norms}),
                        ("norm-defaults", {"kind": "norm-defaults-report" if "norm-defaults@0" in profiles
                                           else "norms-elaborate", "norms": norms})]:
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


def english_read(data, source):
    from ve import english
    from ve.backends import english_lean, relay
    env = Environment(data)
    [row] = relay.rows("english.read", [english_lean.request(env, source, english.EnglishVocabulary(env), {})])
    return row


SEEK = predicate(["person"], {"role": "permission", "default": "deny", "act": "{0} seek asylum"})


def seek_environment(profiles):
    return {"language": ENV["language"], "spec_revision": ENV["spec_revision"], "profiles": profiles,
            "vocabulary": {"sorts": {"person": {"description": "person"}}, "predicates": {"p": SEEK},
                           "constants": {"alice": {"sort": "person", "description": "alice"}},
                           "acts": {"fixed": []}}}


def test_an_acts_environment_with_norm_defaults_is_read_by_english():
    """ap-1b recheck F3 (its probe): the typing view's `acts@0` stage erased `acts@0` from the submitted list and so
    listed `norm-defaults@0` again, which the earlier stage had erased; English refused what the environment mode
    accepts, naming `norm-defaults@0`."""
    row = english_read(seek_environment(["acts@0", "norm-defaults@0", "norms@0", "relational-fol@0"]),
                       "Alice may seek asylum.")
    assert row.get("status") == "ok" and row["result"]["status"] == "one", row


def _acts_lists():
    from ve.profiles import BY_NAME
    base = ["acts@0", "norms@0", "relational-fol@0"]
    extras = [p for p in BY_NAME if p not in base]
    for k in (1, 2):
        for i, p in enumerate(extras):
            for more in ([[]] if k == 1 else [[q] for q in extras[i + 1:]]):
                yield sorted(base + [p] + more)


def test_every_acts_list_the_environment_mode_accepts_is_read_by_english():
    """ap-1b recheck F3, the class: for every list of `acts@0`, `norms@0`, `relational-fol@0` and one or two more
    environment profiles, English reads what the environment mode accepts (the two are one Lean decision about
    the profiles; the Lean side is `admittedWithActs` in `lean/VE/Service/ActsExamples.lean`)."""
    accepted = []
    for profiles in _acts_lists():
        data = seek_environment(profiles)
        try:
            Environment(data)
        except VEError:
            continue
        accepted.append(profiles)
        row = english_read(data, "Alice may seek asylum.")
        assert row.get("status") == "ok" and row["result"]["status"] == "one", (profiles, row)
    assert ["acts@0", "norm-defaults@0", "norms@0", "relational-fol@0"] in accepted
    assert any("norm-defaults@0" in ps and len(ps) == 5 for ps in accepted), accepted


# ap-1bb (2): Lean's wording of a plain act, relayed by the norms route's `norms-elaborate` row (`wordings`), typed
# by its schema and bound to the request's plain acts; English displays it and Python computes none.

A1_WORDING = "{0} is entitled in full equality to a fair and public hearing by an independent and impartial tribunal in {1}"
A2_WORDING = "{0} has the right to equal pay for equal work without any discrimination"
A21 = "{0}" + " ab" * 131 + " a" * 2


def test_a_plain_act_reads_with_the_wording_lean_selected():
    """Spec 2.1 and 11.1: A1's 109-byte wording and A21's 414-byte one (a 400-byte plain act), past the template
    lint's lengths; never "classified as" or "has the recorded relation"; a permission keeps its modal form."""
    from ve.english import EnglishVocabulary
    from ve.norms import plain_wordings
    env = Environment(environment())
    words = EnglishVocabulary(env)
    assert plain_wordings(env) == {"heard": A1_WORDING, "paid": A2_WORDING}
    assert (words.predicates["heard"], words.predicates["paid"]) == (A1_WORDING, A2_WORDING)
    assert [len(w.encode()) for w in (A1_WORDING, A2_WORDING)] == [109, 72]
    assert words.atom("heard", ("Alice", "the trial")).startswith("Alice is entitled in full equality")
    assert words.predicates["protected"] == A3.replace("{0} ", "{0} may ", 1)
    long = EnglishVocabulary(Environment(environment(heard=predicate(["person"], {
        "role": "plain", "default": "deny", "act": A21, "form": "has the right"})))).predicates["heard"]
    assert long == "{0} has the right " + A21[4:] and len(long.encode()) == 414


def _genuine_row(env):
    from ve.backends.relay import decide
    return decide("norms", [{"id": "norms-elaborate", "kind": "norms-elaborate", "environment": env.to_dict(),
                             "norms": []}])[0]


def test_the_wording_is_the_one_lean_relays(monkeypatch):
    """Python computes no wording: the one shown is the relayed one, whatever it says (R8: its text is Lean's)."""
    from ve.backends import relay
    from ve.english import EnglishVocabulary
    env = Environment(environment())
    row = _genuine_row(env)
    row["wordings"] = {**row["wordings"], "paid": "{0} is owed equal pay"}
    monkeypatch.setattr(relay, "decide_once", lambda mode, case: row)
    assert EnglishVocabulary(env).predicates["paid"] == "{0} is owed equal pay"


def _rebound(wordings):
    """Binding mutants of a genuine `wordings` map: each name dropped, an undeclared name and a declared
    predicate that is no plain act added, a name renamed, and the map emptied."""
    yield "dropped", {k: v for k, v in wordings.items() if k != "paid"}
    yield "undeclared", {**wordings, "absent": A2_WORDING}
    yield "extra-row", {**wordings, "protected": A2_WORDING}
    yield "renamed", {("heard2" if k == "heard" else k): v for k, v in wordings.items()}
    yield "empty", {}


@pytest.mark.parametrize("mutant", ["dropped", "undeclared", "extra-row", "renamed", "empty", "field-dropped"])
def test_wordings_not_bound_to_the_request_are_unavailable(monkeypatch, mutant):
    """R8: the names of `wordings` are exactly the request's plain acts, on both readers (the display's
    `plain_wordings` and the document's `norms-elaborate` row)."""
    from ve.backends import relay
    from ve.errors import CheckerUnavailable
    from ve.norms import NormDocument, plain_wordings
    env = Environment(environment())
    document = NormDocument(env, [])
    row = _genuine_row(env)
    if mutant == "field-dropped":
        del row["wordings"]
    else:
        row["wordings"] = dict(_rebound(row["wordings"]))[mutant]
    monkeypatch.setattr(relay, "decide_once", lambda mode, case: row)
    monkeypatch.setattr(relay, "decide", lambda mode, cases, **kw: [row])
    with pytest.raises(CheckerUnavailable, match="wordings are not bound"):
        plain_wordings(env)
    with pytest.raises(CheckerUnavailable, match="wordings are not bound"):
        document._lean_regenerated()


@pytest.mark.parametrize("value", [None, True, 7, 7.5, "7", [], [A1_WORDING], {"heard": 7}, {"heard": None},
                                   {"heard": [A1_WORDING]}, {"heard": {}}, {"heard": "\ud800"}, "deep", "deleted"])
def test_a_retyped_wordings_field_fails_the_schema(value):
    """The `wordings` member is typed by the generated schema (`common.json` `string_map`): the genuine exchange
    passes, and every retype of the map or of one wording, sent as bytes through the service's decoder, is
    refused before a reader sees it (a lone surrogate or a 10,000-deep list by the decoder)."""
    from tests.lean_build import lean_build
    from tests.subprocesses import HANG_TIMEOUT
    from ve.backends.lean_service import LeanService, _decode_json, case_digest, case_texts
    from ve.backends.service_schema import Invalid, check_response
    env = Environment(environment())
    cases = [{"id": "w", "kind": "norms-elaborate", "environment": env.to_dict(), "norms": []}]
    text = json.dumps(cases, ensure_ascii=False, separators=(",", ":"))
    with LeanService(lean_build("ve_service") / "ve_service", timeout=HANG_TIMEOUT) as service:
        _, response = service.exchange("norms", text, 1, timeout=HANG_TIMEOUT)
    request = {"id": response["id"], "mode": "norms", "cases": cases,
               "digests": [case_digest(t) for t in case_texts(text)], "bytes": len(text.encode())}
    check_response("norms", _decode_json(json.dumps(response).encode()), request)
    assert response["results"][0]["result"]["wordings"] == {"heard": A1_WORDING, "paid": A2_WORDING}
    mutant = copy.deepcopy(response)
    if value == "deleted":
        del mutant["results"][0]["result"]["wordings"]
    else:
        mutant["results"][0]["result"]["wordings"] = "DEEP" if value == "deep" else value
    line = json.dumps(mutant).replace('"DEEP"', "[" * 10_000 + "]" * 10_000).encode()
    with pytest.raises((Invalid, ValueError)):
        check_response("norms", _decode_json(line), request)


def test_norm_defaults_keeps_todays_display_without_asking(monkeypatch):
    """The norms route does not read `norm-defaults@0`; such an environment asks for no wording (next item)."""
    from ve.backends import relay
    from ve.norms import plain_wordings
    env = Environment(environment(["acts@0", "norm-defaults@0", "norms@0", "relational-fol@0"]))
    monkeypatch.setattr(relay, "decide_once", lambda mode, case: pytest.fail("asked"))
    assert plain_wordings(env) == {}
