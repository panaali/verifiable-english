"""Discourse item 3 (Lean): the `ve_discourse_route` executable on the item-1 fixtures.

docs/spec/discourse.md section 10. Each case is a `ve-document@2` Lean document object
(`format`, `prose`, W2 `units`/`graph`, `discourse`); mention spans are prose byte ranges
computed here from the sentence text. The Lean validator regenerates every binding and
reports the diagnostic texts of section 8 (spans in diagnostics are token ranges of the
unit, lean/DISCOURSE.md).
"""
from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from ve.wire import digest

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean/.lake/build/bin/ve_discourse_route"
PROFILES = ["relational-fol@0", "ve.discourse@1"]


@pytest.fixture(scope="module")
def lean():
    if not LEAN.exists():
        lake = shutil.which("lake")
        if lake is None:
            pytest.skip("lake is required for the discourse Lean route")
        built = subprocess.run([lake, "build"], cwd=ROOT / "lean", capture_output=True, text=True, timeout=1200)
        assert built.returncode == 0, built.stdout + built.stderr
    return LEAN


def run(cases):
    result = subprocess.run([str(LEAN), "-"], input=json.dumps(cases), text=True, capture_output=True, timeout=300)
    assert result.returncode in (0, 1), result.stderr
    rows = json.loads(result.stdout)
    assert len(rows) == len(cases)
    return rows


def vocab(sig=None, constants=None):
    preds = {"reviewed": ["service"], "deployed": ["service"], "safe": ["service"], "eligible": ["service"],
             "ready": ["person"], "owner": ["person"], "manager_of": ["person", "person"],
             "supersedes": ["document", "document"]}
    preds.update(sig or {})
    consts = constants if constants is not None else {"api": "service", "alice": "person", "bob": "person"}
    return {"sorts": {s: {"description": s} for s in ["service", "person", "document"]},
            "predicates": {p: {"arguments": a, "description": p} for p, a in preds.items()},
            "constants": {c: {"sort": s, "description": c} for c, s in consts.items()}}


def env(sig=None, constants=None, profiles=PROFILES):
    return {"language": "ve.core@0.2", "profiles": list(profiles),
            "spec_revision": "ve-v0.2-expand2-2026-09-25", "vocabulary": vocab(sig, constants)}


NAMES = [{"constant": "api", "display": "the API", "scope": "doc"},
         {"constant": "alice", "display": "Alice", "scope": "doc"},
         {"constant": "bob", "display": "Bob", "scope": "doc"}]


OPEN_GRAPH = {"root": "n", "nodes": [{"name": "n", "ast": ["top"], "label": "open:t"}]}


def entity(c):
    return {"kind": "entity", "name": c}


def document(sentences, mentions=(), names=NAMES, kinds=None, contents=None, graph=None, extra=None):
    prose, units = "", []
    for i, s in enumerate(sentences):
        if prose:
            prose += " "
        start = len(prose.encode())
        prose += s
        uid = f"u{i + 1}"
        unit = {"id": uid, "span": [start, len(prose.encode())], "kind": (kinds or {}).get(uid, "asserted")}
        if contents and uid in contents:
            unit["content"] = contents[uid]
        units.append(unit)
    records = []
    for mid, uid, text, form, target, *more in mentions:
        options = dict(more[0]) if more else {}
        occurrence = options.pop("occurrence", 0)
        a0, b0 = units[int(uid[1:]) - 1]["span"]
        segment = prose.encode()[a0:b0].decode()
        index = -1
        for _ in range(occurrence + 1):
            index = segment.lower().find(text.lower(), index + 1)
        assert index >= 0, (text, segment)
        a = a0 + len(segment[:index].encode())
        records.append({"id": mid, "unit": uid, "span": [a, a + len(text.encode())], "form": form,
                        "target": target, **options})
    block = {"version": "ve.discourse@1", "definitions_version": "pending", "document_sort": "document",
             "anchors": [{"id": "doc", "kind": "document", "label": "Policy", "span": [0, len(prose.encode())]}],
             "names": names, "mentions": records}
    block.update(extra or {})
    if graph is None:
        graph = OPEN_GRAPH
    return {"format": "ve-document@2", "prose": prose, "units": units, "graph": graph, "open_terms": ["t"],
            "discourse": block}


def pin(case):
    """Fill `definitions_version` with the environment id under the base pair."""
    probe = copy.deepcopy(case)
    probe["kind"] = "discourse-resolve"
    row = run([probe])[0]
    assert row["status"] == "ok", row
    case["document"]["discourse"]["definitions_version"] = row["environment_id"]
    return case


def resolve(doc, environment=None):
    row = run([{"id": "r", "kind": "discourse-resolve", "environment": environment or env(), "document": doc}])[0]
    assert row["status"] == "ok", row
    return row


def unit_result(row, uid):
    value = row["units"][uid]
    return value["formula"] if value["status"] == "resolved" else value["error"]


def admit_raw(doc, environment=None):
    return run([{"id": "a", "kind": "admission", "environment": environment or env(), "document": doc}])[0]


def admit(doc, environment=None):
    case = pin({"id": "a", "kind": "admission", "environment": environment or env(), "document": doc})
    return run([case])[0]


def unary(p, c):
    return ["unary", p, ["const", c]]


def unique(sort, restriction):
    return ["exists", sort, ["and", restriction,
                             ["forall", sort, ["implies", restriction, ["eq", ["var", 0], ["var", 1]]]]]]


MANAGER = ["binary", "manager_of", ["var", 0], ["const", "alice"]]
PERSON = {"reviewed": ["person"]}


# (α) Named antecedent

def test_alpha_named_antecedent(lean):
    doc = document(["The API is reviewed.", "It is safe."], [("m1", "u2", "It", "pronoun", entity("api"))],
                   contents={"u1": unary("reviewed", "api")},
                   graph={"root": "n2", "nodes": [{"name": "n2", "ast": unary("safe", "api"), "unit": "u2"}]})
    row = resolve(doc)
    assert unit_result(row, "u2") == unary("safe", "api")
    assert {t["name"] for t in row["mentions"]["m1"]["accessible"]} == {"api", "alice", "bob"}
    result = admit(doc)
    assert result["status"] == "ok", result
    assert result["bound"] == {"u2": unary("safe", "api")}
    assert result["statuses"] == {"u1": "CHECKED", "u2": "CHECKED"}
    assert result["report"]["root"]["ast"] == unary("safe", "api")


def test_alpha_ill_typed_target(lean):
    doc = document(["The API is reviewed.", "It is safe."], [("m1", "u2", "It", "pronoun", entity("alice"))])
    assert unit_result(resolve(doc), "u2") == "IllTypedTarget: m1: alice"
    assert admit(doc)["error"] == "IllTypedTarget: m1: alice"


# (α′) Natural view versus manifest

def test_alpha_prime_differences(lean):
    doc = document(["The API is reviewed.", "Alice is ready.", "It is safe."], [("m1", "u3", "It", "pronoun", entity("api"))])
    assert unit_result(resolve(doc, env(PERSON)), "u3") == unary("safe", "api")
    beta_names = [{"constant": "api", "display": "the API", "scope": "doc"},
                  {"constant": "beta", "display": "Beta", "scope": "doc"}]
    with_beta = env(constants={"api": "service", "beta": "service", "alice": "person", "bob": "person"})
    unmentioned = document(["The API is reviewed.", "It is safe."], [("m1", "u2", "It", "pronoun", entity("api"))],
                           names=beta_names)
    assert unit_result(resolve(unmentioned, with_beta), "u2") == "AmbiguousReference: m1: api, beta"
    earlier_anchor = document(["A service is deployed.", "The API is reviewed.", "It is safe."],
                              [("m1", "u3", "It", "pronoun", entity("api"))])
    spans = [u["span"] for u in earlier_anchor["units"]]
    earlier_anchor["discourse"]["anchors"] += [
        {"id": "sec1", "kind": "section", "parent": "doc", "label": "1", "span": spans[0]},
        {"id": "sec2", "kind": "section", "parent": "doc", "label": "2", "span": [spans[1][0], spans[2][1]]}]
    assert unit_result(resolve(earlier_anchor), "u3") == unary("safe", "api")


# (β) Competing quantifier

def test_beta_competing_quantifier(lean):
    doc = document(["A service is deployed.", "The API is reviewed.", "It is safe."],
                   [("m1", "u3", "It", "pronoun", entity("api"))])
    assert unit_result(resolve(doc), "u3") == "UnresolvedReference: m1"


# (γ) Gender never selects

def test_gamma_gender_never_selects(lean):
    doc = document(["Alice is reviewed.", "Bob is reviewed.", "She is ready."],
                   [("m1", "u3", "She", "pronoun", entity("alice"))])
    assert unit_result(resolve(doc, env(PERSON)), "u3") == "AmbiguousReference: m1: alice, bob"


# (δ) Demonstrative

def test_delta_demonstrative(lean):
    doc = document(["This service is safe."], [("m1", "u1", "This service", "demonstrative", entity("api"))])
    assert unit_result(resolve(doc), "u1") == unary("safe", "api")
    claim = document(["This claim is disputed."], [("m1", "u1", "This claim", "demonstrative", {"kind": "claim", "name": "l1"})],
                     kinds={"u1": ["unformalised", "claims"]})
    assert admit(claim)["error"] == "UnsupportedTarget: m1: claim"


# (ε) such

def test_epsilon_such(lean):
    doc = document(["Every reviewed service is deployed.", "Every such service is safe."],
                   [("m1", "u2", "such", "such", {"kind": "predicate", "name": "reviewed"})])
    assert unit_result(resolve(doc), "u2") == ["forall", "service", ["implies", ["unary", "reviewed", ["var", 0]],
                                                                    ["unary", "safe", ["var", 0]]]]
    unbound = document(["Every service is deployed.", "Every such service is safe."],
                       [("m1", "u2", "such", "such", {"kind": "predicate", "name": "reviewed"})])
    assert unit_result(resolve(unbound), "u2") == "UnresolvedReference: m1"


# (ζ) Ordinal pair

def test_zeta_ordinal_pair(lean):
    pair = {"kind": "entity", "name": "alice", "pair": ["alice", "bob"]}
    doc = document(["Alice and Bob are reviewed.", "The former is ready."], [("m1", "u2", "The former", "ordinal_pair", pair)])
    assert unit_result(resolve(doc, env(PERSON)), "u2") == unary("ready", "alice")
    latter = document(["Alice and Bob are reviewed.", "The latter is ready."],
                      [("m1", "u2", "The latter", "ordinal_pair", {**pair, "name": "bob"})])
    assert unit_result(resolve(latter, env(PERSON)), "u2") == unary("ready", "bob")
    carol_env = env(PERSON, {"api": "service", "alice": "person", "bob": "person", "carol": "person"})
    two = document(["Alice and Bob are reviewed.", "Bob and Carol are reviewed.", "The former is ready."],
                   [("m1", "u3", "The former", "ordinal_pair", pair)],
                   names=NAMES + [{"constant": "carol", "display": "Carol", "scope": "doc"}])
    assert unit_result(resolve(two, carol_env), "u3").startswith("AmbiguousReference: m1")
    bad = document(["Alice and Bob are reviewed.", "The former is ready."],
                   [("m1", "u2", "The former", "ordinal_pair", {**pair, "name": "api"})])
    assert admit(bad, env(PERSON))["error"] == "InvalidInput: mention m1 target"


# (η) Possessive description, nested mentions

ETA_NAMES = NAMES[:2]


def eta(reading="assertive", restriction=MANAGER, target="alice", extra_units=(), presupposition_unit=None,
        omit_possessive=False, names=ETA_NAMES, graph=None, contents=None):
    options = {"reading": reading, "restriction": restriction}
    if presupposition_unit:
        options["presupposition_unit"] = presupposition_unit
    mentions = [("m2", "u2", "Her manager", "definite", entity("binder:0"), options)]
    if not omit_possessive:
        mentions.append(("m1", "u2", "Her", "possessive", entity(target)))
    return document(["Alice is reviewed.", "Her manager is ready.", *extra_units], mentions, names=names,
                    graph=graph, contents=contents)


def test_eta_nested_mentions(lean):
    assertive = ["exists", "person", ["and", MANAGER, ["and", ["forall", "person", ["implies", MANAGER,
                 ["eq", ["var", 0], ["var", 1]]]], ["unary", "ready", ["var", 0]]]]]
    assert unit_result(resolve(eta(), env(PERSON)), "u2") == assertive
    assert unit_result(resolve(eta(names=NAMES), env(PERSON)), "u2") == "AmbiguousReference: m1: alice, bob"
    mismatch = eta(restriction=["binary", "manager_of", ["var", 0], ["const", "bob"]], names=NAMES)
    mismatch["discourse"]["names"] = ETA_NAMES
    assert unit_result(resolve(mismatch, env(PERSON)), "u2") == "ManifestMismatch: mentions.m2.restriction"
    assert unit_result(resolve(eta(target="api"), env(PERSON)), "u2") == "IllTypedTarget: m2: binder:0"
    assert unit_result(resolve(eta(omit_possessive=True), env(PERSON)), "u2") == "UnrecordedSlot: u2: [0, 1)"


def test_eta_presupposition_carriers(lean):
    claim = ["forall", "person", ["implies", MANAGER, ["unary", "ready", ["var", 0]]]]
    graph = {"root": "claim", "nodes": [{"name": "claim", "ast": claim, "unit": "u2"}]}
    assumed = eta("presuppositional", extra_units=["Alice has exactly one manager."], presupposition_unit="u3",
                  graph=graph, contents={"u3": unique("person", MANAGER)})
    result = admit(assumed, env(PERSON))
    assert result["status"] == "ok", result
    assert result["presuppositions"] == {"m2": "discourse:presupposition:m2: assumed (u3)"}
    assert result["bound"] == {"u2": claim}
    assert result["pending"] == []
    assert all(not leaf.get("label", "").startswith("discourse:") for leaf in result["report"]["assumptions"])
    neither = eta("presuppositional")
    result = admit(neither, env(PERSON))
    assert result["status"] == "ok", result
    assert result["pending"] == [["u2", "PresuppositionUnresolved: m2"]]
    assert result["bound"] == {}
    assert result["statuses"]["u2"] == "PENDING"
    assert result["presuppositions"] == {"m2": "discourse:presupposition:m2: unresolved"}


# (θ) Plural

def test_theta_plural(lean):
    target = {"kind": "entity", "members": ["alice", "bob"]}
    doc = document(["Alice and Bob are reviewed.", "They are ready."],
                   [("m1", "u2", "They", "plural", target, {"reading": "distributive"})])
    assert unit_result(resolve(doc, env(PERSON)), "u2") == ["and", unary("ready", "alice"), unary("ready", "bob")]
    reversed_members = document(["Alice and Bob are reviewed.", "They are ready."],
                                [("m1", "u2", "They", "plural", {"kind": "entity", "members": ["bob", "alice"]},
                                  {"reading": "distributive"})])
    assert unit_result(resolve(reversed_members, env(PERSON)), "u2") == ["and", unary("ready", "alice"),
                                                                         unary("ready", "bob")]
    collective = document(["Alice and Bob are reviewed.", "They are ready."],
                          [("m1", "u2", "They", "plural", target, {"reading": "collective"})])
    assert admit_raw(collective, env(PERSON))["error"] == "InvalidInput: reading collective"
    single = document(["Alice and Bob are reviewed.", "They are ready."],
                      [("m1", "u2", "They", "plural", {"kind": "entity", "members": ["alice"]}, {"reading": "distributive"})])
    assert admit(single, env(PERSON))["error"] == "InvalidInput: mention m1 target"


# (μ) Same-witness fusion and the J5 negatives

def fusion(content=None, extra_sets=(), reading=None):
    fused = ["exists", "service", ["and", ["unary", "deployed", ["var", 0]], ["unary", "reviewed", ["var", 0]]]]
    doc = document(["A service is deployed.", "It is reviewed."], contents=content,
                   extra={"groups": [{"set": "rs1", "version": 1, "reading": 0, "spans": ["u1", "u2"]}]})
    doc["reading_sets"] = [{"id": "rs1", "version": 1, "readings": [reading or fused]}, *extra_sets]
    return doc


def test_mu_group_single_assertion(lean):
    result = admit(fusion())
    assert result["status"] == "ok", result
    assert result["statuses"]["u1"] == result["statuses"]["u2"] == "CHECKED"
    assert admit(fusion({"u2": ["exists", "service", ["unary", "reviewed", ["var", 0]]]}))["error"] == \
        "IndependentFragment: u2"
    split = ["and", ["exists", "service", ["unary", "deployed", ["var", 0]]],
             ["exists", "service", ["unary", "reviewed", ["var", 0]]]]
    assert admit(fusion(reading=split))["error"] == "WitnessSplit: rs1@1:0"


# (ν) Universal plus it

def test_nu_universal_it(lean):
    doc = document(["Every service is deployed.", "It is reviewed."], [("m1", "u2", "It", "pronoun", entity("api"))])
    assert unit_result(resolve(doc), "u2") == "UnresolvedReference: m1"


# (ξ) Description without a possessor

def test_xi_description(lean):
    options = {"reading": "presuppositional", "restriction": ["unary", "owner", ["var", 0]]}
    doc = document(["The owner is ready."], [("m1", "u1", "The owner", "definite", entity("binder:0"), options)])
    assert unit_result(resolve(doc), "u1") == ["forall", "person", ["implies", ["unary", "owner", ["var", 0]],
                                                                    ["unary", "ready", ["var", 0]]]]


# (ο) Correlated readings

def joint_doc(constraints, sets=2, readings=2):
    doc = document(["The API is reviewed."], contents={"u1": unary("reviewed", "api")},
                   extra={"constraints": constraints})
    doc["reading_sets"] = [{"id": f"rs{k}", "version": 1,
                            "readings": [unary("safe", "api") if i == 0 else unary("deployed", "api")
                                         for i in range(readings)]} for k in range(5, 5 + sets)]
    return doc


def joint(doc):
    row = run([{"id": "j", "kind": "discourse-joint", "environment": env(), "document": doc}])[0]
    assert row["status"] == "ok", row
    return row


def test_omicron_joint_set(lean):
    correlated = [{"kind": "requires", "a": ["rs5", 1, 0], "b": ["rs6", 1, 0]},
                  {"kind": "requires", "a": ["rs5", 1, 1], "b": ["rs6", 1, 1]}]
    row = joint(joint_doc(correlated))
    assert row["verdict"] == "COMPLETE"
    assert row["choices"] == [[["rs5", 1, 0], ["rs6", 1, 0]], [["rs5", 1, 1], ["rs6", 1, 1]]]
    excludes = [{"kind": "excludes", "a": ["rs5", 1, i], "b": ["rs6", 1, k]} for i in range(2) for k in range(2)]
    row = joint(joint_doc(excludes))
    assert row["verdict"] == "INVALID" and row["diagnostic"] == "InvalidCompatibility: rs5, rs6"
    row = joint(joint_doc([], sets=7))
    assert row["verdict"] == "UNKNOWN" and row["diagnostic"] == "ResourceLimit: joint choices"
    zero = joint(joint_doc([], sets=0))
    assert zero["choices"] == [[]] and zero["joint"] == ["top"]


# (λ) The composition gate at report level

def test_lambda_report_extension(lean):
    excluded = [{"kind": "excludes", "a": ["rs5", 1, i], "b": ["rs6", 1, 1]} for i in range(2)]
    graph = {"root": "leaf", "nodes": [{"name": "leaf", "ast": unary("deployed", "api"), "label": "readings:rs6@1:1"}]}
    doc = joint_doc(excluded)
    doc["graph"] = graph
    assert admit(doc)["error"] == "InvalidCompatibility: report leaf"
    unknown = joint_doc([], sets=7)
    unknown["graph"] = graph
    result = admit(unknown)
    assert result["status"] == "ok", result
    assert result["joint"] == "ResourceLimit: joint choices"


# (π) Document names

DOCS = {"documents": [{"name": "this_policy", "display": ["this document", "this policy"], "refers": "self", "version": 3},
                      {"name": "policy2", "display": ["policy 2"], "refers": {"import": "policy2"}, "version": 2,
                       "source_id": "x", "document_id": "y"}],
        "imports": {"policy2": {"source_id": "x", "document_id": "y"}}}
DOC_CONSTANTS = {"api": "service", "alice": "person", "bob": "person", "this_policy": "document", "policy2": "document"}


def test_pi_document_names(lean):
    doc = document(["This policy supersedes policy 2."],
                   [("m1", "u1", "This policy", "document_name", {"kind": "document", "name": "this_policy"}),
                    ("m2", "u1", "policy 2", "document_name", {"kind": "document", "name": "policy2"})], extra=DOCS)
    assert unit_result(resolve(doc, env(constants=DOC_CONSTANTS)), "u1") == \
        ["binary", "supersedes", ["const", "this_policy"], ["const", "policy2"]]
    other = env(constants={**DOC_CONSTANTS, "policy9": "document"})
    assert admit(doc, other)["error"] == "InvalidInput: document sort document has other constants"


# (ρ, τ, υ) Validity and the truth boundary

def validity_doc(sentence, document_name, holds, extra_docs=None):
    extra = copy.deepcopy(extra_docs or DOCS)
    extra["validity"] = [{"unit": "u1", "document": document_name, "holds": holds}]
    return document([sentence], kinds={"u1": "meta"}, extra=extra)


def test_rho_validity_self(lean):
    positive = admit(validity_doc("This document is a valid VE document.", "this_policy", True), env(constants=DOC_CONSTANTS))
    assert positive["status"] == "ok", positive
    assert positive["validity"] == {"u1": "checked"} and positive["statuses"]["u1"] == "CHECKED"
    negative = admit(validity_doc("This document is not a valid VE document.", "this_policy", False),
                     env(constants=DOC_CONSTANTS))
    assert negative["validity"] == {"u1": "refuted"} and negative["statuses"]["u1"] == "LABELLED"


def stored(sentence="The API is reviewed."):
    inner = document([sentence], contents={"u1": unary("reviewed", "api")},
                     graph={"root": "n", "nodes": [{"name": "n", "ast": unary("reviewed", "api"), "unit": "u1"}]})
    case = pin({"id": "s", "kind": "admission", "environment": env(), "document": inner})
    assert run([case])[0]["status"] == "ok"
    inner = case["document"]
    text = json.dumps({"environment": env(), "document": inner})
    source_id = hashlib.sha256(("ve-source-v0.2\n" + inner["prose"]).encode()).hexdigest()
    return text, source_id


def import_docs(content, source_id):
    docs = copy.deepcopy(DOCS)
    docs["documents"][1]["source_id"] = source_id
    docs["imports"] = {"policy2": {"source_id": source_id, "document_id": "y",
                                   **({"content": content} if content is not None else {})}}
    return docs


def test_tau_validity_import(lean):
    text, source_id = stored()
    checked = admit(validity_doc("Policy 2 is a valid VE document.", "policy2", True, import_docs(text, source_id)),
                    env(constants=DOC_CONSTANTS))
    assert checked["status"] == "ok", checked
    assert checked["validity"] == {"u1": "checked"}
    absent = admit(validity_doc("Policy 2 is a valid VE document.", "policy2", True, import_docs(None, source_id)),
                   env(constants=DOC_CONSTANTS))
    assert absent["validity"] == {"u1": "unconfirmed (import bytes absent)"}
    stale = admit(validity_doc("Policy 2 is a valid VE document.", "policy2", True, import_docs(text, "0" * 64)),
                  env(constants=DOC_CONSTANTS))
    assert stale["error"] == "StaleTarget: policy2"
    rejected_text = json.dumps({"environment": env(constants=DOC_CONSTANTS), "document": {"format": "ve-document@2"}})
    bad_id = hashlib.sha256(b"ve-source-v0.2\n").hexdigest()
    negative = admit(validity_doc("Policy 2 is not a valid VE document.", "policy2", False,
                                  import_docs(rejected_text, bad_id)), env(constants=DOC_CONSTANTS))
    assert negative["status"] == "ok", negative
    assert negative["validity"] == {"u1": "checked"}


def test_upsilon_self_truth(lean):
    doc = document(["Everything in this document is true."], kinds={"u1": "meta"}, extra={"self_truth": ["u1"]})
    result = admit(doc)
    assert result["status"] == "ok", result
    assert result["self_truth"] == ["u1"] and result["statuses"]["u1"] == "LABELLED"
    bound_as_validity = document(["This document is correct."], kinds={"u1": "meta"},
                                 extra={**DOCS, "self_truth": ["u1"],
                                        "validity": [{"unit": "u1", "document": "this_policy", "holds": True}]})
    assert admit(bound_as_validity, env(constants=DOC_CONSTANTS))["error"] == "InvalidInput: u1 is a self-truth sentence"


# (φ) Identity, tampering and the profile adapter

def test_phi_tampering_and_identity(lean):
    base = document(["The API is reviewed.", "It is safe."], [("m1", "u2", "It", "pronoun", entity("api"))],
                    graph={"root": "n2", "nodes": [{"name": "n2", "ast": unary("safe", "api"), "unit": "u2"}]})
    tampered = copy.deepcopy(base)
    tampered["units"][1]["content"] = unary("deployed", "api")
    assert admit(tampered)["error"] == "ManifestMismatch: bound.u2"
    stale = pin({"id": "s", "kind": "admission", "environment": env(), "document": copy.deepcopy(base)})
    stale["document"]["discourse"]["definitions_version"] = "0" * 64
    assert run([stale])[0]["error"] == "StaleTarget: definitions@" + "0" * 64
    first = admit(copy.deepcopy(base))
    relabelled = copy.deepcopy(base)
    relabelled["discourse"]["anchors"][0]["label"] = "Renamed"
    second = admit(relabelled)
    assert first["document_id"] != second["document_id"]
    assert first["report"] == second["report"]
    resolved = resolve(copy.deepcopy(base))
    ast = unary("safe", "api")
    meaning = digest("ve-meaning-v0.2:relational-fol@0\n", {"environment_id": resolved["environment_id"], "ast": ast})
    assert resolved["units"]["u2"]["meaning_id"] == meaning
    plain_env = env(profiles=["relational-fol@0"])
    plain_id = digest("ve-environment-v0.2:relational-fol@0\n", plain_env)
    assert resolved["environment_id"] == plain_id


def test_phi_format1(lean):
    cases = json.loads((ROOT / "lean/VE/Route/examples/route-cases.json").read_text())
    admission = next(c for c in cases if c.get("kind") == "admission" and c["expected"].get("status") == "ok")
    delegated = {k: v for k, v in admission.items() if k != "expected"}
    row = run([delegated])[0]
    for key, value in admission["expected"].items():
        assert row[key] == value
    with_profile = copy.deepcopy(delegated)
    with_profile["environment"]["profiles"] = sorted(with_profile["environment"]["profiles"] + ["ve.discourse@1"])
    assert run([with_profile])[0]["error"] == "UnsupportedProfile: ve.discourse@1 requires ve-document@2"


# (ι) Definition reference and (κ) anchors

def iota_doc():
    doc = document(["Eligible services are reviewed services.",
                    "Every eligible service is reviewed, where eligible has the meaning defined in section 2."],
                   [("m1", "u2", "eligible", "definition_ref", {"kind": "predicate", "name": "eligible", "version": 2})],
                   kinds={"u1": "definition"})
    end = doc["units"][1]["span"][1]
    doc["discourse"]["anchors"].append({"id": "sec2", "kind": "section", "parent": "doc", "label": "2",
                                        "span": [0, end], "exports": ["eligible"]})
    return doc


def test_iota_definition_reference(lean):
    assert unit_result(resolve(iota_doc()), "u2") == ["forall", "service", ["implies", ["unary", "eligible", ["var", 0]],
                                                                            ["unary", "reviewed", ["var", 0]]]]
    unexported = iota_doc()
    unexported["discourse"]["anchors"][1]["exports"] = []
    assert unit_result(resolve(unexported), "u2") == "UnresolvedReference: m1"


def test_kappa_anchor_tables(lean):
    duplicate = iota_doc()
    duplicate["discourse"]["anchors"].append({"id": "sec2b", "kind": "section", "parent": "doc", "label": "2",
                                              "span": [0, 5]})
    assert admit(duplicate)["error"] == "DuplicateAnchor: 2"
    dangling = iota_doc()
    dangling["discourse"]["names"] = [dict(NAMES[0], scope="sec9")]
    assert admit(dangling)["error"] == "DanglingAnchor: sec9"
