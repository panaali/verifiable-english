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


def joined(act, fixed):
    data = environment(p=predicate(["person"], {"role": "plain", "default": "deny", "act": act,
                                                "form": "has the right"}))
    data["vocabulary"]["acts"]["fixed"] = fixed
    del data["vocabulary"]["predicates"]["heard"], data["vocabulary"]["predicates"]["protected"]
    if not fixed:
        del data["vocabulary"]["predicates"]["paid"]
    return data


@pytest.mark.parametrize("act, fixed", [(A5, []), (A6, FIXED)], ids=["A5", "A6"])
def test_a_joined_act_is_refused_with_leans_text(act, fixed):
    """ap-3dc (DRI 2026-11-02 ap-3db item 5): the environment row reads a joined act with the act check, so one the
    declared frames do not read is refused with D-16, where AP-1 gave D-4."""
    assert refusal(joined(act, fixed)) == "InvalidInput: act phrase for p has no reading under the declared frames"


def test_a_joined_act_the_frames_read_loads():
    data = joined(A6, FIXED)
    data["vocabulary"]["acts"]["frames"] = [{"head": "subjected", "markers": ["to"], "split": ["to"], "modifiers": []}]
    assert Environment(data).predicates["p"].regulated.act == A6


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
    Lean computed from its canonical environment, the same as for the act written with U+0027. Python stores the
    canonical act the environment row gives (F1), so the two are one environment, and the norms route checks a
    document over it."""
    from ve.norms import NormDocument, check_conflict
    from tests.test_norms import rule
    curly = Environment(environment(p=predicate(["person", "case"], {"role": "permission", "default": "allow",
                                                                     "act": A19})))
    straight = Environment(environment(p=predicate(["person", "case"], {"role": "permission", "default": "allow",
                                                                        "act": A19.replace("’", "'")})))
    assert curly.environment_id == straight.environment_id
    assert curly.to_dict() == straight.to_dict()
    assert curly.predicates["p"].regulated.act == A19.replace("’", "'")
    assert check_conflict(NormDocument(curly, [rule("m", "p", True)]), prove=True).status == "CONFLICT-FREE"


def _spelled(act, fresh):
    """An `acts@0` environment with the permission `p` of `act` and a predicate named `fresh`, so that no cache of
    this process has seen its identity yet."""
    return environment(p=predicate(["person", "case"], {"role": "permission", "default": "allow", "act": act}),
                       **{fresh: {"arguments": ["person"], "description": "d"}})


@pytest.mark.parametrize("first", ["curly", "straight"])
def test_one_identity_is_one_environment_whichever_loads_first(first):
    """ap-1bb review F1 (its probe, in both orders): every cache keyed by an environment's identity (the lexicon,
    the encoded request, the definitions, the accepted rows) answers for the environment that has it. Two spellings
    Lean reads as one act have one identity, so Python builds one environment of them: the same `to_dict()`, the
    same request bytes and the same lexicon and legend, whichever was loaded first in the process."""
    from ve import words
    from ve.environment_wire import encoded_environment
    from ve.norm_defaults_english import legend
    spellings = {"curly": A19, "straight": A19.replace("’", "'")}
    order = [first] + [k for k in spellings if k != first]
    envs = {k: Environment(_spelled(spellings[k], f"fresh_{first}")) for k in order}
    lexicons = {k: words.lexicon(envs[k]) for k in order}
    legends = {k: legend(envs[k]) for k in order}
    encoded = {k: encoded_environment(envs[k], "lean-norms", envs[k].to_dict).text for k in order}
    assert envs["curly"].environment_id == envs["straight"].environment_id
    assert envs["curly"].to_dict() == envs["straight"].to_dict()
    assert lexicons["curly"] == lexicons["straight"] and "’" not in json.dumps(lexicons, ensure_ascii=False)
    assert legends["curly"] == legends["straight"]
    assert encoded["curly"] == encoded["straight"]


def _environment_row(data):
    from ve.backends.relay import decide
    return decide("environment", [{"id": "environment", "environment": data}])[0]


def _acts_mutants(acts):
    """One-fault mutants of a genuine row's `acts`: a name dropped, undeclared, a declared predicate without an
    act, renamed, the map emptied, an act changed (another canonical act, the act as written) and the member
    deleted."""
    yield "dropped", {k: v for k, v in acts.items() if k != "p"}
    yield "undeclared", {**acts, "absent": acts["p"]}
    yield "no-act", {**acts, "plain_fact": acts["p"]}
    yield "renamed", {("p2" if k == "p" else k): v for k, v in acts.items()}
    yield "empty", {}
    yield "changed", {**acts, "p": acts["protected"]}
    yield "as-written", {**acts, "p": A19}
    yield "deleted", None


@pytest.mark.parametrize("mutant", ["dropped", "undeclared", "no-act", "renamed", "empty", "changed", "as-written",
                                    "deleted"])
def test_acts_not_bound_to_the_request_are_unavailable(monkeypatch, mutant):
    """ap-1bb F1, R8: the environment row's `acts` name exactly the request's regulated acts, and the environment
    Python builds with them must have the row's identity; every one-fault mutant of a genuine row is
    `CheckerUnavailable`, never an environment that another identity names."""
    from ve.backends import relay, validation
    from ve.errors import CheckerUnavailable
    data = _spelled(A19, "plain_fact")
    row = _environment_row(data)
    assert set(row["acts"]) == {"heard", "paid", "protected", "p"}
    acts = dict(_acts_mutants(row["acts"]))[mutant]
    mutated = {k: v for k, v in row.items() if k != "acts"} | ({} if acts is None else {"acts": acts})
    monkeypatch.setattr(validation, "_ACCEPTED", {})
    monkeypatch.setattr(relay, "decide", lambda mode, cases, **kw: [mutated])
    with pytest.raises(CheckerUnavailable):
        Environment(data)


@pytest.mark.parametrize("value", [None, True, 7, "7", [], ["x"], {"p": 7}, {"p": None}, {"p": []}, {"p": {}},
                                   {"p": "\ud800"}, "deep", "deleted"])
def test_a_retyped_acts_field_fails_the_schema(value):
    """The environment row's `acts` is typed by the generated schema (`string_map`): the genuine exchange passes,
    and every retype, sent as bytes through the service's decoder, is refused before Python builds anything."""
    from tests.lean_build import lean_build
    from tests.subprocesses import HANG_TIMEOUT
    from ve.backends.lean_service import LeanService, _decode_json, case_digest, case_texts
    from ve.backends.service_schema import Invalid, check_response
    cases = [{"id": "environment", "environment": _spelled(A19, "plain_fact")}]
    text = json.dumps(cases, ensure_ascii=False, separators=(",", ":"))
    with LeanService(lean_build("ve_service") / "ve_service", timeout=HANG_TIMEOUT) as service:
        _, response = service.exchange("environment", text, 1, timeout=HANG_TIMEOUT)
    request = {"id": response["id"], "mode": "environment", "cases": cases,
               "digests": [case_digest(t) for t in case_texts(text)], "bytes": len(text.encode())}
    check_response("environment", _decode_json(json.dumps(response).encode()), request)
    assert response["results"][0]["result"]["acts"]["p"] == A19.replace("’", "'")
    mutant = copy.deepcopy(response)
    if value == "deleted":
        del mutant["results"][0]["result"]["acts"]
    else:
        mutant["results"][0]["result"]["acts"] = "DEEP" if value == "deep" else value
    line = json.dumps(mutant).replace('"DEEP"', "[" * 10_000 + "]" * 10_000).encode()
    with pytest.raises((Invalid, ValueError)):
        check_response("environment", _decode_json(line), request)


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
    predicate that is no plain act added, a name renamed, and the map emptied; and (review F2) the slots of a
    wording, which name the predicate's argument positions: one pushed past the arity, one left out, one written
    `{01}`, one with a format spec, a stray brace, and a slot `{1}` in a unary predicate's wording."""
    yield "dropped", {k: v for k, v in wordings.items() if k != "paid"}
    yield "undeclared", {**wordings, "absent": A2_WORDING}
    yield "extra-row", {**wordings, "protected": A2_WORDING}
    yield "renamed", {("heard2" if k == "heard" else k): v for k, v in wordings.items()}
    yield "empty", {}
    yield "slot-past-arity", {**wordings, "heard": wordings["heard"].replace("{1}", "{2}")}
    yield "slot-left-out", {**wordings, "heard": wordings["heard"].replace(" in {1}", "")}
    yield "slot-zero-padded", {**wordings, "heard": wordings["heard"].replace("{1}", "{01}")}
    yield "slot-format-spec", {**wordings, "heard": wordings["heard"].replace("{1}", "{1:x}")}
    yield "stray-brace", {**wordings, "paid": wordings["paid"] + " {"}
    yield "slot-in-unary", {**wordings, "paid": wordings["paid"] + " in {1}"}


REBOUND = ["dropped", "undeclared", "extra-row", "renamed", "empty", "slot-past-arity", "slot-left-out",
           "slot-zero-padded", "slot-format-spec", "stray-brace", "slot-in-unary"]


@pytest.mark.parametrize("mutant", REBOUND + ["field-dropped"])
def test_wordings_not_bound_to_the_request_are_unavailable(monkeypatch, mutant):
    """R8: the names of `wordings` are exactly the request's plain acts, and the slots of each wording exactly its
    predicate's argument positions (`relay.slots_bound`), on both readers (the display's `plain_wordings` and the
    document's `norms-elaborate` row)."""
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
    real = relay.decide  # the document's `acts-elaborate` case (ap-3dc) is Lean's own
    monkeypatch.setattr(relay, "decide", lambda mode, cases, **kw: [row] if cases[0].get("kind") != "acts-elaborate"
                        else real(mode, cases, **kw))
    with pytest.raises(CheckerUnavailable, match="wordings are not bound"):
        plain_wordings(env)
    with pytest.raises(CheckerUnavailable, match="wordings are not bound"):
        document._lean_regenerated()


RETYPED = [None, True, 7, 7.5, "7", [], [A1_WORDING], {"heard": 7}, {"heard": None}, {"heard": [A1_WORDING]},
           {"heard": {}}, {"heard": "\ud800"}, "deep", "deleted"]


@pytest.mark.parametrize("value", RETYPED)
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


# ap-1be (1): a `norm-defaults@0` environment, which the norms route does not read, gets the same wordings from the
# norm-defaults route's `norm-defaults-elaborate` row (`Norms.Wire.plainWordings` of the decoded source), typed by its
# schema and bound by `_bind_wordings` on both of its readers.

ND_PROFILES = ["acts@0", "norm-defaults@0", "norms@0", "relational-fol@0"]


def _nd_case(env):
    return {"id": "norm-defaults-elaborate", "kind": "norm-defaults-elaborate", "environment": env.to_dict(),
            "norms": []}


def test_a_norm_defaults_environment_reads_with_the_wording_lean_selected(monkeypatch):
    """R3: under `norm-defaults@0` the display asks the norm-defaults route only, and shows its row's `wordings`,
    Lean's text: the norms route's for the same acts (A1 109 B, A2); a permission keeps its modal form. The base
    showed Python's fallback display."""
    from ve.backends import relay
    from ve.english import EnglishVocabulary
    from ve.norms import plain_wordings
    env = Environment(environment(ND_PROFILES))
    row = relay.decide("norm-defaults", [_nd_case(env)])[0]
    assert row["wordings"] == _genuine_row(Environment(environment()))["wordings"] == {
        "heard": A1_WORDING, "paid": A2_WORDING}
    asked = []
    monkeypatch.setattr(relay, "decide_once", lambda mode, case: asked.append((mode, case)) or row)
    assert plain_wordings(env) == {"heard": A1_WORDING, "paid": A2_WORDING}
    words = EnglishVocabulary(env)
    assert (words.predicates["heard"], words.predicates["paid"]) == (A1_WORDING, A2_WORDING)
    assert words.predicates["protected"] == A3.replace("{0} ", "{0} may ", 1)
    assert {(mode, json.dumps(case, sort_keys=True)) for mode, case in asked} == {
        ("norm-defaults", json.dumps(_nd_case(env), sort_keys=True))}


@pytest.mark.parametrize("mutant", REBOUND + ["field-dropped"])
def test_norm_defaults_wordings_not_bound_to_the_request_are_unavailable(monkeypatch, mutant):
    """R8 on the norm-defaults row, on both readers (the display's `plain_wordings` and the document's own row,
    `UnspecifiedDocument`): the genuine row is accepted by each, and each binding mutant of `_rebound` is refused."""
    from ve import norm_defaults_route
    from ve.backends import relay
    from ve.errors import CheckerUnavailable
    from ve.norm_defaults import UnspecifiedDocument
    from ve.norms import plain_wordings
    env = Environment(environment(ND_PROFILES))
    row = relay.decide("norm-defaults", [_nd_case(env)])[0]
    monkeypatch.setattr(relay, "decide_once", lambda mode, case: row)
    monkeypatch.setattr(norm_defaults_route, "run_case", lambda case: row)
    assert plain_wordings(env) == {"heard": A1_WORDING, "paid": A2_WORDING}
    assert UnspecifiedDocument(env, []).elaboration is row
    row = copy.deepcopy(row)
    if mutant == "field-dropped":
        del row["wordings"]
    else:
        row["wordings"] = dict(_rebound(row["wordings"]))[mutant]
    with pytest.raises(CheckerUnavailable, match="norm-defaults-elaborate wordings are not bound"):
        plain_wordings(env)
    with pytest.raises(CheckerUnavailable, match="norm-defaults-elaborate wordings are not bound"):
        UnspecifiedDocument(env, [])


def test_a_retyped_norm_defaults_wordings_field_fails_the_schema():
    """`norm-defaults-elaborate`'s `wordings` is typed by the generated schema (`string_map`): the genuine exchange
    passes, and each retype of `RETYPED`, sent as bytes through the service's decoder, is refused."""
    from tests.lean_build import lean_build
    from tests.subprocesses import HANG_TIMEOUT
    from ve.backends.lean_service import LeanService, _decode_json, case_digest, case_texts
    from ve.backends.service_schema import Invalid, check_response
    cases = [_nd_case(Environment(environment(ND_PROFILES)))]
    text = json.dumps(cases, ensure_ascii=False, separators=(",", ":"))
    with LeanService(lean_build("ve_service") / "ve_service", timeout=HANG_TIMEOUT) as service:
        _, response = service.exchange("norm-defaults", text, 1, timeout=HANG_TIMEOUT)
    request = {"id": response["id"], "mode": "norm-defaults", "cases": cases,
               "digests": [case_digest(t) for t in case_texts(text)], "bytes": len(text.encode())}
    check_response("norm-defaults", _decode_json(json.dumps(response).encode()), request)
    assert response["results"][0]["result"]["wordings"] == {"heard": A1_WORDING, "paid": A2_WORDING}
    for value in RETYPED:
        mutant = copy.deepcopy(response)
        if value == "deleted":
            del mutant["results"][0]["result"]["wordings"]
        else:
            mutant["results"][0]["result"]["wordings"] = "DEEP" if value == "deep" else value
        line = json.dumps(mutant).replace('"DEEP"', "[" * 10_000 + "]" * 10_000).encode()
        with pytest.raises((Invalid, ValueError)):
            check_response("norm-defaults", _decode_json(line), request)


def test_an_environment_without_a_plain_act_asks_lean_nothing_to_display(monkeypatch):
    """The display's cost is unchanged where no plain act is declared (every environment before `acts@0`): no
    call to the norms route, nor (ap-1be) to the norm-defaults route under `norm-defaults@0`, so the UDHR and
    constitution pilots' displays make none."""
    from ve.backends import relay
    from ve.english import EnglishVocabulary
    for profiles in (None, ND_PROFILES):
        data = environment(profiles)
        for name in ("heard", "paid"):
            del data["vocabulary"]["predicates"][name]
        env = Environment(data)
        monkeypatch.setattr(relay, "decide_once", lambda mode, case: pytest.fail("asked"))
        monkeypatch.setattr(relay, "decide", lambda mode, cases, **kw: pytest.fail("asked"))
        assert EnglishVocabulary(env).predicates["protected"] == A3.replace("{0} ", "{0} may ", 1)
        monkeypatch.undo()


@pytest.mark.parametrize("template, arity, bound", [
    ("{0} sees {1}", 2, True), ("{1} is seen by {0}", 2, True), ("{0} is", 1, True), ("it rains", 0, True),
    ("{0} sees {2}", 2, False), ("{0} sees", 2, False), ("{0} sees {01}", 2, False), ("{0} sees {1:x}", 2, False),
    ("{0} sees {1!r}", 2, False), ("{0} sees { 1}", 2, False), ("{0} sees {1} }", 2, False),
    ("{0} sees {{1}}", 2, False), ("{0} sees {١}", 2, False), ("{0} sees {-1}", 2, False),
    ("{0} sees {" + "9" * 5000 + "}", 2, False), (None, 1, False), (7, 1, False)])
def test_slots_bound_is_the_one_slot_binding_of_every_relayed_wording(template, arity, bound):
    """review F2: `relay.slots_bound` (used by the norms and rights relays) admits a template exactly when its braces
    are slots `{i}` as `EnglishVocabulary.atom` replaces them and those slots are the arity's positions."""
    from ve.backends.relay import slots_bound
    assert slots_bound(template, arity) is bound


# ap-1bc (1): the words route (`VE.Words.regulatedOf`) decodes a clause's declaration as Lean's English does, so an
# `acts@0` plain act, a long act and an act with a fixed phrase each have Lean's clause; Python relays them.

AB81 = "{0}" + " ab" * 26
DUAL = {"must_hear": predicate(["person", "case"], {"role": "obligation", "default": "deny", "act": A1,
                                                    "permission": "may_hear"}),
        "may_hear": predicate(["person", "case"], {"role": "permission", "default": "deny", "act": A1}),
        "long": predicate(["person"], {"role": "permission", "default": "allow", "act": AB81}),
        "late": {"arguments": ["person"], "description": "d"}}


def test_the_words_route_words_acts_clauses_by_leans_decoder():
    """ap-1bb review F3: the words route answered `the predicate heard is not regulated` for a plain act; a plain
    act's clause is its wording at either value, a permission's has its modal (A3: `and` inside a fixed phrase; an
    81-character act, past today's 80), and an obligation whose act holds a fixed phrase has its pair sentence."""
    from ve import words
    env = Environment(environment(**DUAL))
    found = words.lines(env, [
        words.point_item({}, "heard", ["e0", "e1"], True), words.point_item({}, "heard", ["e0", "e1"], False),
        words.point_item({}, "paid", ["e0"], False, kind="filling"),
        words.point_item({}, "protected", ["e0", "e1"], True), words.point_item({}, "protected", ["e0", "e1"], False),
        words.point_item({}, "long", ["e0"], True), words.pair_item("must_hear")])
    heard = A1_WORDING.replace("{0}", "e0").replace("{1}", "e1")
    tail = A1[4:].replace("{1}", "")
    assert found == [
        heard, heard,
        "Here the text does not say whether e0 has the right to equal pay for equal work without any discrimination;"
        " this situation answers 'no'.",
        A3.replace("{0} ", "e0 may ").replace("{1}", "e1"), A3.replace("{0} ", "e0 must not ").replace("{1}", "e1"),
        "e0 may" + " ab" * 26,
        f'Whenever a person must {tail}an entity of sort "case", it may {tail}that entity of sort "case".']


@pytest.mark.parametrize("item, message", [
    ({"kind": "point", "constants": {}, "predicate": "late", "tuple": ["e0"], "value": True}, "late is not regulated"),
    ({"kind": "filling", "constants": {}, "predicate": "late", "tuple": ["e0"], "value": True}, "late is not regulated"),
    ({"kind": "pair", "required": "heard"}, "heard is no obligation"),
    ({"kind": "pair", "required": "protected"}, "protected is no obligation")])
def test_the_words_route_still_refuses_what_is_not_a_regulated_clause(item, message):
    """The refusing side: under `acts@0` a base predicate has no clause, and a plain act or a permission no pair."""
    from ve import words
    with pytest.raises(VEError, match=message):
        words.lines(Environment(environment(**DUAL)), [item])


# ap-1bd: typing, the model path, the readings route and `ve document` read `acts@0` (Lean's answers, relayed)

PLAIN = {"paid": ENV["vocabulary"]["predicates"]["paid"]}  # every regulated declaration plain


def plain_environment(profiles=None):
    data = environment(profiles)
    data["vocabulary"]["predicates"] = copy.deepcopy(PLAIN)
    return data


def test_an_acts_formula_is_typed_and_its_models_checked_by_lean():
    from ve.ast import Forall, Unary, Var, check_formula
    from ve.model import FiniteModel
    env = Environment(environment(**DUAL))
    check_formula(env, Forall("person", Unary("paid", Var(0))))
    with pytest.raises(VEError, match="TypeMismatch: Predicate 'paid' expects"):
        check_formula(env, Forall("case", Unary("paid", Var(0))))
    def model(may):
        return {"complete": True, "domains": {"person": ["p"], "case": ["c"]}, "constants": {},
                "relations": {**{p: [] for p in env.predicates}, "must_hear": [["p", "c"]], "may_hear": may}}
    FiniteModel.from_dict(env, model([["p", "c"]]))
    with pytest.raises(VEError, match="required relation must_hear exceeds permission may_hear"):
        FiniteModel.from_dict(env, model([]))


def test_rust_searches_leans_model_view_of_an_acts_environment():
    """ap-1bg (b): Rust's search reads Lean's model view of an `acts@0` environment (`profiles.model_view`): without
    the profile, its block and each plain act's wording, each permission and obligation act Lean's placeholder, one
    per distinct act, so a dual pair keeps one act. A permission's act no longer stops the search; Lean checks every
    witness, and a model breaking the pair is still refused. Without `acts@0` the environment is Rust's as before."""
    from ve.ast import Binary, Exists, Unary, Var
    from ve.profiles import model_environment, model_view
    from ve.search import find_countermodel
    view = model_view(model_environment(environment(**DUAL)))
    assert view["profiles"] == ["norms@0", "relational-fol@0"] and "acts" not in view["vocabulary"]
    regulated = {p: d["regulated"] for p, d in view["vocabulary"]["predicates"].items() if "regulated" in d}
    assert regulated["paid"] == {"role": "plain", "default": "deny"}
    assert [regulated[p]["act"] for p in ("long", "may_hear", "must_hear", "protected")] == \
        ["{0} acta", "{0} actb {1}", "{0} actb {1}", "{0} actc {1}"]
    for env in (environment(), environment(**DUAL), plain_environment()):
        found = find_countermodel(Environment(env), (), Exists("person", Unary("paid", Var(0))))
        assert found.status == "Found" and found.model.relations["paid"] == frozenset()
    found = find_countermodel(Environment(environment(**DUAL)), (), Exists("person", Exists("case", Binary(
        "must_hear", Var(1), Var(0)))))
    assert found.status == "Found" and found.model.relations["must_hear"] <= found.model.relations["may_hear"]
    bare = {"profiles": ["norms@0", "relational-fol@0"], "vocabulary": {}}
    assert model_view(bare) is bare


def readings_row(env, units, sets=()):
    from ve.readings_route import document_wire
    [row] = lean_routes.rows("readings-route", [{"id": "v", "kind": "readings-validate", "environment": env,
                                                 "document": document_wire(units, list(sets))}])
    return row


def test_the_readings_route_reads_single_acts_and_refuses_a_joined_act():
    rule = {"norm": {"name": "m", "predicate": "paid", "sign": True, "guard": ["top"], "unless": [], "over": []}}
    readings = ["acts@0", "norms@0", "readings@1", "relational-fol@0"]
    assert readings_row(plain_environment(readings), [{"id": "u1", "kind": "norm", "content": rule}]).get("error") is None
    # a reading set over `acts@0` is read as without the profile (ap-1bg; ap-1bd kept the base's refusal)
    sets = [{"id": "rs1", "unit": "u1", "version": 1, "status": "open", "situations": {}, "readings": [
        {"id": r, "kind": "norm", "content": {"norm": {**rule["norm"], "sign": r == "a"}}} for r in "ab"]}]
    bare = plain_environment(readings[1:])
    bare["vocabulary"].pop("acts")
    bare["vocabulary"]["predicates"]["paid"]["regulated"] = {"role": "plain", "default": "deny"}
    assert readings_row(plain_environment(readings), [{"id": "u1"}], sets)["error"] == \
        readings_row(bare, [{"id": "u1"}], sets)["error"] == "each other reading needs a distinguishing model id"
    joined = plain_environment(readings)
    joined["vocabulary"]["predicates"]["paid"]["regulated"]["act"] = A5
    assert readings_row(joined, [])["error"] == ("UnsupportedProfile: acts@0 on the readings route admits single acts "
                                                 "only; the act of paid joins acts")
    joined["profiles"].remove("readings@1")
    # without `readings@1` the environment row reads it with the act check (ap-3dc, DRI 2026-11-02 ap-3db item 5)
    assert refusal(joined) == "InvalidInput: act phrase for paid has no reading under the declared frames"


U076 = "1. Everyone has the right to take part in the government of his country, directly or through freely chosen " \
       "representatives."


def u076(tmp_path, profiles):
    """The UDHR pilot's act-phrase probe (u076): one plain act with one fixed phrase, a part document (L70)."""
    from tests.test_document import write_doc
    act = "{0} to take part in the government of his country directly or through freely chosen representatives"
    env = {"language": "ve.core@0.2", "profiles": profiles, "spec_revision": ENV["spec_revision"], "vocabulary": {
        "constants": {}, "sorts": {"person": {"description": "a human person"}},
        "predicates": {"take_part": predicate(["person"], {"role": "plain", "default": "unspecified", "act": act,
                                                           "form": "has the right"})},
        "acts": {"fixed": ["directly or through freely chosen representatives"]}}}
    norm = {"norm": {"guard": ["top"], "name": "u076", "over": [], "predicate": "take_part", "sign": True,
                     "unless": []}}
    return write_doc(tmp_path, U076.encode(), [{"id": "u076", "kind": "norm", "meaning": "specified", "support": "none",
                                                "span": [0, len(U076.encode())], "content": norm}],
                     environment_json=env, open_terms=[])


def test_a_udhr_act_phrase_unit_is_checked_end_to_end(tmp_path):
    from ve.document import check_document, render_document
    path = u076(tmp_path, ["acts@0", "documents@1", "norm-defaults@0", "norms@0", "relational-fol@0"])
    report = check_document(path)
    assert report["coverage"]["bytes_by_status"] == {"CHECKED": len(U076.encode())}
    assert report["premises"]["status"] == "model"
    assert render_document(path).rstrip().endswith("Checked reading: Every person has the right to take part in the government "
                                          "of his country directly or through freely chosen representatives.")
    with pytest.raises(VEError, match=r"fields do not match: expected \[sorts, predicates, constants\], got \[acts"):
        check_document(u076(tmp_path, ["documents@1", "norm-defaults@0", "norms@0", "relational-fol@0"]))


# ap-1bd review F1: an `acts@0` environment with `readings@1` loads, so the wording of its plain acts is asked of the
# readings route, which runs the elaborate case on the lower route without the head profile (Lean's
# `Readings.Run.runLower`); before, the norms and norm-defaults routes refused `readings@1` and every English entry
# point (`EnglishVocabulary`) failed.

def test_a_readings_environment_has_leans_wordings():
    """PROBE F1."""
    from ve.norms import plain_wordings
    env = Environment(plain_environment(["acts@0", "norms@0", "readings@1", "relational-fol@0"]))
    assert plain_wordings(env) == {"paid": A2_WORDING}


def test_every_acts_list_the_environment_mode_accepts_has_leans_wordings():
    """F1, the class: every list of `acts@0`, `norms@0`, `relational-fol@0` and one or two more profiles that the
    environment mode accepts with a plain act gives the wording Lean gives without the extra profiles, through
    `EnglishVocabulary`, which every English entry point builds."""
    from ve.english import EnglishVocabulary
    accepted = []
    for profiles in _acts_lists():
        try:
            env = Environment(plain_environment(profiles))
        except VEError:
            continue
        accepted.append(profiles)
        assert EnglishVocabulary(env).predicates["paid"] == A2_WORDING, profiles
    assert {"readings@1", "norm-defaults@0"} <= {p for ps in accepted for p in ps if "readings@1" in ps}, accepted


def test_a_udhr_act_phrase_unit_with_readings_is_checked_and_rendered(tmp_path):
    """F1's measured case: u076 with `readings@1` (the UDHR pilot's environment lists it and `norm-defaults@0`)."""
    from ve.document import check_document, render_document
    path = u076(tmp_path, ["acts@0", "documents@1", "norm-defaults@0", "norms@0", "readings@1", "relational-fol@0"])
    assert check_document(path)["coverage"]["bytes_by_status"] == {"CHECKED": len(U076.encode())}
    assert render_document(path).rstrip().endswith("Checked reading: Every person has the right to take part in the "
                                                   "government of his country directly or through freely chosen "
                                                   "representatives.")


READINGS_PROFILES = ["acts@0", "norms@0", "readings@1", "relational-fol@0"]


@pytest.mark.parametrize("mutant", REBOUND + ["field-dropped"])
def test_readings_wordings_not_bound_to_the_request_are_unavailable(monkeypatch, mutant):
    """F1, R8: the readings route's elaborate row (the one `plain_wordings` asks for a `readings@1` environment) is
    bound by the same `_bind_wordings`."""
    from ve.backends import relay
    from ve.errors import CheckerUnavailable
    from ve.norms import plain_wordings
    data = environment(READINGS_PROFILES)
    env = Environment(data)
    [row] = relay.decide("readings-route", [{"id": "norms-elaborate", "kind": "norms-elaborate", "environment": data,
                                             "norms": []}])
    assert row["wordings"] == {"heard": A1_WORDING, "paid": A2_WORDING}
    if mutant == "field-dropped":
        del row["wordings"]
    else:
        row["wordings"] = dict(_rebound(row["wordings"]))[mutant]
    asked = []
    monkeypatch.setattr(relay, "decide_once", lambda mode, case: asked.append(mode) or row)
    with pytest.raises(CheckerUnavailable, match="wordings are not bound"):
        plain_wordings(env)
    assert asked == ["readings-route"]


@pytest.mark.parametrize("profiles", [READINGS_PROFILES, sorted(READINGS_PROFILES + ["norm-defaults@0"])])
@pytest.mark.parametrize("value", RETYPED)
def test_a_retyped_readings_wordings_field_fails_the_schema(profiles, value):
    """F1: the readings route's row for a lower route's elaborate case is that route's row, so its `wordings` member
    is typed by the same generated schema; every retype is refused before a reader sees it."""
    from tests.lean_build import lean_build
    from tests.subprocesses import HANG_TIMEOUT
    from ve.backends.lean_service import LeanService, _decode_json, case_digest, case_texts
    from ve.backends.service_schema import Invalid, check_response
    kind = "norm-defaults-elaborate" if "norm-defaults@0" in profiles else "norms-elaborate"
    cases = [{"id": "w", "kind": kind, "environment": Environment(environment(profiles)).to_dict(), "norms": []}]
    text = json.dumps(cases, ensure_ascii=False, separators=(",", ":"))
    with LeanService(lean_build("ve_service") / "ve_service", timeout=HANG_TIMEOUT) as service:
        _, response = service.exchange("readings-route", text, 1, timeout=HANG_TIMEOUT)
    request = {"id": response["id"], "mode": "readings-route", "cases": cases,
               "digests": [case_digest(t) for t in case_texts(text)], "bytes": len(text.encode())}
    check_response("readings-route", _decode_json(json.dumps(response).encode()), request)
    assert response["results"][0]["result"]["wordings"] == {"heard": A1_WORDING, "paid": A2_WORDING}
    mutant = copy.deepcopy(response)
    if value == "deleted":
        del mutant["results"][0]["result"]["wordings"]
    else:
        mutant["results"][0]["result"]["wordings"] = "DEEP" if value == "deep" else value
    line = json.dumps(mutant).replace('"DEEP"', "[" * 10_000 + "]" * 10_000).encode()
    with pytest.raises((Invalid, ValueError)):
        check_response("readings-route", _decode_json(line), request)


# ap-1bg (a): a reading set over `acts@0` takes the superposed and enumerated routes. Under the completion the
# filled environment carries the request's `acts` block, acts and forms, typed by the schema and bound to the request;
# every genuine answer is mutated one and two faults at a time.

LONG = "{0} help {1} with the moral and material interests"


def completion_case(profiles=("acts@0", "norm-defaults@0", "norms@0", "readings@1", "relational-fol@0")):
    """F-ND1 (readings under the unspecified completion) under `acts@0`: the dual pair's act holds a fixed phrase and a
    plain act is beside it; its environment and document (with meaning ids) as the readings route reads them."""
    from tests.test_readings_nd_lean import doc1, env1
    from ve.document import _environment
    from ve.readings import s1_content_meaning_id
    raw = env1(sorted(profiles))
    if "acts@0" in profiles:
        for p in ("help_permitted", "help_required"):
            raw["vocabulary"]["predicates"][p]["regulated"]["act"] = LONG
        raw["vocabulary"]["predicates"]["paid"] = predicate(["user"], {"role": "plain", "default": "deny", "act": A2,
                                                                       "form": "has the right"})
        raw["vocabulary"]["acts"] = {"fixed": FIXED}
    document, _ = doc1(raw)
    env = _environment(raw)
    for reading_set in document["reading_sets"]:
        for r in reading_set["readings"]:
            r["meaning_id"] = s1_content_meaning_id(env, reading_set["id"], r)
    return raw, document


def test_a_reading_set_over_acts_takes_the_superposed_and_enumerated_routes(tmp_path):
    """Both routes answer an `acts@0` document as they answer it without the profile (ap-1bd refused it): F-ND1 is
    superposed and conflict-free, review M8's document enumerated with its conflict under one reading."""
    from tests.test_document import unit, write_doc
    from tests.test_readings_s1_lean import env_k, norm
    from tests.test_readings_s2_document import ASKS, s2_document
    from ve.document import check_document
    text = b"Every agent must help each user.\n"
    answers = []
    for profiles in (("acts@0", "norm-defaults@0", "norms@0", "readings@1", "relational-fol@0"),
                     ("norm-defaults@0", "norms@0", "readings@1", "relational-fol@0")):
        raw, document = completion_case(profiles)
        (tmp_path / profiles[0]).mkdir()
        path = write_doc(tmp_path / profiles[0], text, [unit("u1", 0, len(text), "norm", "specified")],
                         environment_json=raw, reading_sets=document["reading_sets"])
        readings = check_document(path)["readings"]
        answers.append((readings["route"], readings["conflict"]["status"]))
    assert answers == [("superposed", "CONFLICT-FREE")] * 2
    waive = lambda over: norm("waive-x", "avoid_required", False, over=over, guard=ASKS)  # noqa: E731
    answers = []
    for acts in (True, False):
        raw = env_k(("acts@0", "norms@0", "readings@1", "relational-fol@0")[0 if acts else 1:])
        if acts:
            raw["vocabulary"]["acts"] = {"fixed": FIXED}
            raw["vocabulary"]["predicates"]["avoid_required"]["regulated"]["act"] = \
                "{0} avoid deceiving {1} about the moral and material interests"
        path = s2_document(tmp_path, [("fixed", "u0", norm("base-x", "avoid_required", True)),
                                      ("set", "rs1", "u1", [("a", waive(()), "norm", None),
                                                            ("b", waive(("base-x",)), "norm", None)]),
                                      ("fixed", "u3", norm("stop-x", "avoid_required", False, over=("waive-x",)))],
                           raw=raw, name=f"m8-{acts}.ve.md")
        readings = check_document(path)["readings"]
        answers.append((readings["route"], readings["conflict"]["status"]))
    assert answers == [("enumerated", "CONFLICT")] * 2


@pytest.fixture(scope="module")
def filled_exchange():
    """The genuine `readings-validate` exchange of `completion_case`, once: its cases, request and response."""
    from tests.lean_build import lean_build
    from tests.subprocesses import HANG_TIMEOUT
    from ve.backends.lean_service import LeanService, case_digest, case_texts
    from ve.readings_route import document_wire, wire
    raw, document = completion_case()
    cases = [{"id": "v", "kind": "readings-validate", "environment": wire(raw),
              "document": wire(document_wire(document["units"], document["reading_sets"]))}]
    text = json.dumps(cases, ensure_ascii=False, separators=(",", ":"))
    with LeanService(lean_build("ve_service") / "ve_service", timeout=HANG_TIMEOUT) as service:
        _, response = service.exchange("readings-route", text, 1, timeout=HANG_TIMEOUT)
    request = {"id": response["id"], "mode": "readings-route", "cases": cases,
               "digests": [case_digest(t) for t in case_texts(text)], "bytes": len(text.encode())}
    return raw, document, request, response


def test_the_readings_route_fills_acts_under_the_completion(filled_exchange):
    from ve.readings_route import validate
    raw, document, _, _ = filled_exchange
    vocabulary = validate(raw, document["units"], document["reading_sets"])["filled"]["environment"]["vocabulary"]
    assert vocabulary["acts"] == {"fixed": FIXED} and vocabulary["predicates"]["paid"]["regulated"] == {
        "role": "plain", "default": "deny", "act": A2, "form": "has the right"}
    assert vocabulary["predicates"]["help_required"]["regulated"]["act"] == LONG


FILLED_RETYPED = [("form", 7), ("form", None), ("form", ["has the right"]), ("form", "has a right"), ("acts", 7),
                  ("acts", {"fixed": 7}), ("acts", {"fixed": [7]}), ("acts", {"fixed": FIXED, "frames": []}),
                  ("acts", {})]


def one_and_two(faults):
    """Every fault alone and every pair of faults on different targets."""
    return [(f,) for f in faults] + [(f, g) for i, f in enumerate(faults) for g in faults[i + 1:] if f[0] != g[0]]


@pytest.mark.parametrize("faults", one_and_two(FILLED_RETYPED),
                         ids=lambda fs: "+".join(f"{f[0]}{FILLED_RETYPED.index(f)}" for f in fs))
def test_a_retyped_filled_act_field_fails_the_schema(filled_exchange, faults):
    """The filled environment's `form` (one of Lean's two forms) and `acts` block are typed by the generated schema
    (`readings-route.json`): the genuine exchange passes and every retype, alone or with another, is refused."""
    from ve.backends.lean_service import _decode_json
    from ve.backends.service_schema import Invalid, check_response
    _, _, request, response = filled_exchange
    check_response("readings-route", _decode_json(json.dumps(response).encode()), request)
    mutant = copy.deepcopy(response)
    vocabulary = mutant["results"][0]["result"]["filled"]["environment"]["vocabulary"]
    for field, value in faults:
        (vocabulary["predicates"]["paid"]["regulated"] if field == "form" else vocabulary)[field] = value
    with pytest.raises(Invalid):
        check_response("readings-route", _decode_json(json.dumps(mutant).encode()), request)


FILLED_REBOUND = [("paid", "form-changed"), ("paid", "form-dropped"), ("help_required", "act-changed"),
                  ("acts", "acts-dropped"), ("phrase", "phrase-dropped")]


@pytest.mark.parametrize("faults", one_and_two(FILLED_REBOUND), ids=lambda fs: "+".join(f[1] for f in fs))
def test_a_filled_act_not_bound_to_the_request_is_unavailable(monkeypatch, filled_exchange, faults):
    """The filled environment's `acts` block and every act and form are the request's: each rebinding of a genuine
    answer, alone or with another, is `CheckerUnavailable`, never an answer."""
    from ve import readings_route
    from ve.errors import CheckerUnavailable
    raw, document, _, _ = filled_exchange
    genuine = readings_route.run_lean

    def rebound(cases, **kwargs):
        rows = copy.deepcopy(genuine(cases, **kwargs))
        vocabulary = rows[0]["filled"]["environment"]["vocabulary"]
        predicates = vocabulary["predicates"]
        for _, mutant in faults:
            if mutant == "form-changed":
                predicates["paid"]["regulated"]["form"] = "is entitled"
            elif mutant == "form-dropped":
                del predicates["paid"]["regulated"]["form"], predicates["paid"]["regulated"]["act"]
            elif mutant == "act-changed":
                predicates["help_required"]["regulated"]["act"] = predicates["help_permitted"]["regulated"]["act"] = \
                    "{0} help {1}"
            elif mutant == "acts-dropped":
                vocabulary.pop("acts", None)
            elif "acts" in vocabulary:
                vocabulary["acts"]["fixed"] = FIXED[1:]
        return rows
    monkeypatch.setattr(readings_route, "run_lean", rebound)
    with pytest.raises(CheckerUnavailable):
        readings_route.validate(raw, document["units"], document["reading_sets"])


# ap-1bg (b): the environment row's `model_acts` (Lean's `Standalone.modelActs`) are typed and bound to the request.

MODEL_RETYPED = [None, 7, [], ["x"], {"may_hear": 7}, {"may_hear": None}, {"may_hear": []}, "deleted"]


@pytest.mark.parametrize("value", MODEL_RETYPED, ids=str)
def test_a_retyped_model_acts_field_fails_the_schema(value):
    """`model_acts` is a `string_map` in the generated schema (`environment.json`); with `acts` retyped too, still."""
    from tests.lean_build import lean_build
    from tests.subprocesses import HANG_TIMEOUT
    from ve.backends.lean_service import LeanService, _decode_json, case_digest, case_texts
    from ve.backends.service_schema import Invalid, check_response
    cases = [{"id": "environment", "environment": environment(**DUAL)}]
    text = json.dumps(cases, ensure_ascii=False, separators=(",", ":"))
    with LeanService(lean_build("ve_service") / "ve_service", timeout=HANG_TIMEOUT) as service:
        _, response = service.exchange("environment", text, 1, timeout=HANG_TIMEOUT)
    request = {"id": response["id"], "mode": "environment", "cases": cases,
               "digests": [case_digest(t) for t in case_texts(text)], "bytes": len(text.encode())}
    check_response("environment", _decode_json(json.dumps(response).encode()), request)
    for second in (False, True):
        mutant = copy.deepcopy(response)
        result = mutant["results"][0]["result"]
        if value == "deleted":
            del result["model_acts"]
        else:
            result["model_acts"] = value
        if second:
            result["acts"] = {"may_hear": 7}
        with pytest.raises(Invalid):
            check_response("environment", _decode_json(json.dumps(mutant).encode()), request)


MODEL_REBOUND = [("dropped", lambda m: m.pop("long")), ("undeclared", lambda m: m.update(absent="{0} actz")),
                 ("plain", lambda m: m.update(paid="{0} actz")), ("split", lambda m: m.update(may_hear="{0} actz {1}")),
                 ("merged", lambda m: m.update(long=m["protected"])), ("emptied", lambda m: m.clear())]


@pytest.mark.parametrize("faults", one_and_two(MODEL_REBOUND), ids=lambda fs: "+".join(f[0] for f in fs))
def test_model_acts_not_bound_to_the_request_are_unavailable(monkeypatch, faults):
    """Each one- and two-fault rebinding of a genuine row's `model_acts` (a permission dropped, an undeclared or a
    plain predicate named, a dual pair split, two distinct acts merged, the map emptied) is `CheckerUnavailable`, both
    where Python builds the environment and where Rust's model view reads it."""
    from ve.backends import relay, validation
    from ve.errors import CheckerUnavailable
    from ve.profiles import model_environment, model_view
    data = model_environment(environment(**DUAL))
    row = _environment_row(data)
    assert set(row["model_acts"]) == {"long", "may_hear", "must_hear", "protected"}
    for _, fault in faults:
        fault(row["model_acts"])
    monkeypatch.setattr(validation, "_ACCEPTED", {})
    monkeypatch.setattr(relay, "decide", lambda mode, cases, **kw: [row])
    with pytest.raises(CheckerUnavailable):
        Environment(data)
    with pytest.raises(CheckerUnavailable):
        model_view(data)


@pytest.mark.parametrize("mutant", ["changed", "dropped", "added"])
def test_a_soft_views_prime_acts_block_not_bound_to_the_request_is_unavailable(monkeypatch, mutant):
    """ap-1bg: `soft-elaborate` on the soft view of an `acts@0` norms frame echoes the request's `acts` block in
    `environment_prime` (`bind_prime_environment` compares it with the request); a changed, dropped or added block is
    `CheckerUnavailable`. The rights route's prime is bound by the same binder."""
    from ve import softnorms
    from ve.backends import soft_relay
    from ve.errors import CheckerUnavailable
    view = plain_environment(["acts@0", "norms@0", "relational-fol@0", "soft-norms@0"])
    view["vocabulary"]["soft"] = {"parties": [], "ranks": [], "outranks": [], "ties": [], "outranking": {"mode": "strict"}}
    assert softnorms.check_soft_source(view, generated=True)["environment_prime"]["vocabulary"]["acts"] == {"fixed": FIXED}
    genuine = soft_relay.run

    def rebound(case):
        row = copy.deepcopy(genuine(case))
        vocabulary = row["environment_prime"]["vocabulary"]
        if mutant == "changed":
            vocabulary["acts"] = {"fixed": FIXED[1:]}
        elif mutant == "dropped":
            del vocabulary["acts"]
        else:
            vocabulary["rights"] = {"holders": []}
        return row
    monkeypatch.setattr(soft_relay, "run", rebound)
    with pytest.raises(CheckerUnavailable):
        softnorms.check_soft_source(view, generated=True)
