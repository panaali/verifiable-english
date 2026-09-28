"""Discourse item 3 (Lean): the `ve_discourse_route` executable on the item-1 fixtures.

docs/spec/discourse.md section 10. Each case's document is a `ve-document@2` text, the bytes
the Python loader reads: JSON front matter (units with their meaning and support, reading
sets with ids, the 3.1 `discourse` block) and the source. Mention spans are source byte ranges
computed here from the sentence text; sibling files an import names travel as the case's
`files`. The Lean validator regenerates every binding and reports the diagnostic texts of
section 8 (spans in diagnostics are token ranges of the unit, lean/DISCOURSE.md).
"""
from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from ve.ast import formula_from_data
from ve.document import check_document, load_document, stored_identities
from ve.environment import Environment
from ve.errors import VEError
from ve.identity import meaning_id
from ve.model import FiniteModel
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


def base_env(environment):
    return Environment({**environment, "profiles": [p for p in environment["profiles"] if p != "ve.discourse@1"]})


NAMES = [{"constant": "api", "display": "the API", "scope": "doc"},
         {"constant": "alice", "display": "Alice", "scope": "doc"},
         {"constant": "bob", "display": "Bob", "scope": "doc"}]

OPEN_TERM = {"name": "t", "arguments": [], "decided_by": "reviewer", "necessary": [], "sufficient": [],
             "factors": [], "precedents": [], "jurisdiction": "policy", "version": 1}
OPEN_GRAPH = {"root": "n", "nodes": [{"name": "n", "ast": ["top"], "label": "open:t"}]}


def entity(c):
    return {"kind": "entity", "name": c}


def unit_record(uid, span, kind, content):
    meaning = ({"unformalised": kind[1]} if type(kind) is list and kind[0] == "unformalised" else "specified")
    unit = {"id": uid, "span": span, "kind": kind, "meaning": meaning,
            "support": "assumption" if content is not None else "none"}
    if content is not None:
        unit["content"] = {"ast": content}
    return unit


def document(sentences, mentions=(), names=NAMES, kinds=None, contents=None, graph=None, extra=None,
             format="ve-document@2"):
    """A document front matter; `_source` is the body. Units cover every source byte."""
    source, units = "", []
    for i, s in enumerate(sentences):
        start = len(source.encode())
        source += s + (" " if i + 1 < len(sentences) and not s.endswith("\n") else "")
        uid = f"u{i + 1}"
        content = (contents or {}).get(uid)
        kind = (kinds or {}).get(uid, "asserted" if content is not None else "exposition")
        units.append(unit_record(uid, [start, len(source.encode())], kind, content))
    records = []
    for mid, uid, text, form, target, *more in mentions:
        options = dict(more[0]) if more else {}
        occurrence = options.pop("occurrence", 0)
        a0, b0 = units[int(uid[1:]) - 1]["span"]
        segment = source.encode()[a0:b0].decode()
        index = -1
        for _ in range(occurrence + 1):
            index = segment.lower().find(text.lower(), index + 1)
        assert index >= 0, (text, segment)
        a = a0 + len(segment[:index].encode())
        records.append({"id": mid, "unit": uid, "span": [a, a + len(text.encode())], "form": form,
                        "target": target, **options})
    front = {"format": format, "units": units, "graph": graph or OPEN_GRAPH, "open_terms": [OPEN_TERM],
             "_source": source}
    if format == "ve-document@2":
        block = {"version": "ve.discourse@1", "document_sort": "document",
                 "anchors": [{"id": "doc", "kind": "document", "label": "Policy", "span": [0, len(source.encode())]}],
                 "names": names, "mentions": records}
        block.update(extra or {})
        front["discourse"] = block
    return front


def text(doc, environment=None):
    front = {k: v for k, v in doc.items() if k != "_source"}
    front["environment"] = environment or env()
    return "---\n" + json.dumps(front) + "\n---\n" + doc["_source"]


def case(kind, doc, environment=None, files=None):
    c = {"id": kind, "kind": kind, "document": text(doc, environment)}
    if files is not None:
        c["files"] = files
    return c


def resolve(doc, environment=None):
    row = run([case("discourse-resolve", doc, environment)])[0]
    assert row["status"] == "ok", row
    return row


def unit_result(row, uid):
    value = row["units"][uid]
    return value["formula"] if value["status"] == "resolved" else value["error"]


def admit(doc, environment=None, files=None):
    return run([case("admission", doc, environment, files)])[0]


def python_ids(doc, environment, tmp_path, name="doc.ve.md"):
    path = tmp_path / name
    path.write_text(text(doc, environment))
    loaded = load_document(path)
    return loaded["source_id"], loaded["document_id"]


def unary(p, c):
    return ["unary", p, ["const", c]]


def unique(sort, restriction):
    return ["exists", sort, ["and", restriction,
                             ["forall", sort, ["implies", restriction, ["eq", ["var", 0], ["var", 1]]]]]]


def model(environment, true_atoms):
    """One entity per sort; the listed unary atoms of `api` true, everything else false."""
    E = base_env(environment)
    data = {"complete": True, "domains": {s: [f"e_{s}"] for s in E.model_sorts},
            "constants": {c: f"e_{d.sort}" for c, d in E.constants.items()},
            "relations": {p: ([["e_service"]] if p in true_atoms else []) for p in E.predicates}}
    return FiniteModel.from_dict(E, data).model_id, data


def reading_set(environment, set_id, unit, readings, status="open"):
    E = base_env(environment)
    ids = [rid for rid, _ in readings]
    models = {}
    if len(readings) > 1:
        mid, data = model(environment, {readings[0][1][1]})
        models[mid] = data
    item = {"id": set_id, "unit": unit, "version": 1, "status": status, "readings": [
        {"id": rid, "kind": "asserted", "content": ast, "meaning_id": meaning_id(E, formula_from_data(E, ast)),
         "admission": {"who": "author", "why": "fixture",
                       "distinguishing_models": {o: next(iter(models)) for o in ids if o != rid}}}
        for rid, ast in readings]}
    if models:
        item["models"] = models
    if status == "authored":
        item["signature"] = "author"
    return item


MANAGER = ["binary", "manager_of", ["var", 0], ["const", "alice"]]
PERSON = {"reviewed": ["person"]}


# (α) Named antecedent

def test_alpha_named_antecedent(lean):
    doc = document(["The API is reviewed.", "It is safe."], [("m1", "u2", "It", "pronoun", entity("api"))],
                   contents={"u1": unary("reviewed", "api"), "u2": unary("safe", "api")},
                   graph={"root": "n2", "nodes": [{"name": "n2", "ast": unary("safe", "api"), "unit": "u2"}]})
    row = resolve(doc)
    assert unit_result(row, "u2") == unary("safe", "api")
    assert {t["name"] for t in row["mentions"]["m1"]["accessible"]} == {"api", "alice", "bob"}
    result = admit(doc)
    assert result["status"] == "ok", result
    assert result["admitted"] is True
    assert result["bound"] == {"u2": unary("safe", "api")}
    assert result["statuses"] == {"u1": "CHECKED", "u2": "CHECKED"}
    assert result["report"]["root"]["ast"] == unary("safe", "api")


def test_alpha_ill_typed_target(lean):
    doc = document(["The API is reviewed.", "It is safe."], [("m1", "u2", "It", "pronoun", entity("alice"))])
    assert unit_result(resolve(doc), "u2") == "IllTypedTarget: m1: alice"
    assert admit(doc)["error"] == "IllTypedTarget: m1: alice"


def test_unrecorded_reference_is_a_slot(lean):
    """Astra A1: a reference surface with no recorded mention is discovered from the source."""
    graph = {"root": "n2", "nodes": [{"name": "n2", "ast": unary("deployed", "api"), "unit": "u2"}]}
    for sentence, span in [("It is deployed.", "[0, 1)"), ("This service is deployed.", "[0, 2)"),
                           ("It is deployed and safe.", "[0, 1)"), ("Its owner is deployed.", "[0, 1)")]:
        doc = document(["The API is reviewed.", sentence],
                       contents={"u1": unary("reviewed", "api"), "u2": unary("deployed", "api")}, graph=graph)
        assert admit(doc)["error"] == f"UnrecordedSlot: u2: {span}", sentence
    # without content the unit claims nothing, so nothing is checked
    plain = document(["The API is reviewed.", "It is deployed."], contents={"u1": unary("reviewed", "api")})
    result = admit(plain)
    assert result["status"] == "ok", result
    assert result["statuses"]["u2"] == "LABELLED"


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
    # Astra B: a recorded pair with no coordination before it is not a candidate
    uncoordinated = document(["Alice is reviewed.", "The latter is ready."],
                             [("m1", "u2", "The latter", "ordinal_pair", {**pair, "name": "bob"})])
    assert unit_result(resolve(uncoordinated, env(PERSON)), "u2") == "UnresolvedReference: m1"


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
    # Fable B1: the diagnostic names the slot whose target does not fit, not the enclosing one
    assert unit_result(resolve(eta(target="api"), env(PERSON)), "u2") == "IllTypedTarget: m1: api"
    ready_service = env({"reviewed": ["person"], "ready": ["service"]})
    assert unit_result(resolve(eta(), ready_service), "u2") == "IllTypedTarget: m2: binder:0"
    assert unit_result(resolve(eta(omit_possessive=True), env(PERSON)), "u2") == "UnrecordedSlot: u2: [0, 1)"


def test_eta_presupposition_carriers(lean):
    claim = ["forall", "person", ["implies", MANAGER, ["unary", "ready", ["var", 0]]]]
    graph = {"root": "claim", "nodes": [{"name": "claim", "ast": claim, "unit": "u2"}]}
    assumed = eta("presuppositional", extra_units=["Alice has exactly one manager."], presupposition_unit="u3",
                  graph=graph, contents={"u2": claim, "u3": unique("person", MANAGER)})
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
    # Fable B1: pending is not a status; the unit is OPEN (13.12)
    assert result["statuses"]["u2"] == "OPEN"
    assert result["presuppositions"] == {"m2": "discourse:presupposition:m2: unresolved"}
    assert [r["status"] for r in result["references"]] == ["pending", "resolved"]


def test_eta_pending_content_is_never_a_premise(lean):
    """Astra A3: submitting the presuppositional claim as content does not make it a premise."""
    claim = ["forall", "person", ["implies", MANAGER, ["unary", "ready", ["var", 0]]]]
    used = eta("presuppositional", contents={"u2": claim},
               graph={"root": "claim", "nodes": [{"name": "claim", "ast": claim, "unit": "u2"}]})
    assert admit(used, env(PERSON))["error"] == "AdmissionError: node claim is not admitted under label asserted"
    unused = eta("presuppositional", contents={"u2": claim})
    result = admit(unused, env(PERSON))
    assert result["status"] == "ok", result
    assert result["pending"] == [["u2", "PresuppositionUnresolved: m2"]]
    assert result["bound"] == {} and result["statuses"]["u2"] == "OPEN"


# (θ) Plural

def test_theta_plural(lean):
    target = {"kind": "entity", "members": ["alice", "bob"]}
    doc = document(["Alice and Bob are reviewed.", "They are ready."],
                   [("m1", "u2", "They", "plural", target, {"reading": "distributive"})])
    assert unit_result(resolve(doc, env(PERSON)), "u2") == ["and", unary("ready", "alice"), unary("ready", "bob")]
    reversed_members = document(["Alice and Bob are reviewed.", "They are ready."],
                                [("m1", "u2", "They", "plural", {"kind": "entity", "members": ["bob", "alice"]},
                                  {"reading": "distributive"})])
    # Astra B: members are the coordination's, in its order; a permutation is another target
    assert unit_result(resolve(reversed_members, env(PERSON)), "u2") == "InaccessibleTarget: m1: bob, alice"
    unlisted = document(["Alice is reviewed.", "Bob is reviewed.", "They are ready."],
                        [("m1", "u3", "They", "plural", target, {"reading": "distributive"})])
    assert unit_result(resolve(unlisted, env(PERSON)), "u3") == "UnresolvedReference: m1"
    collective = document(["Alice and Bob are reviewed.", "They are ready."],
                          [("m1", "u2", "They", "plural", target, {"reading": "collective"})])
    assert admit(collective, env(PERSON))["error"] == "InvalidInput: reading collective"
    single = document(["Alice and Bob are reviewed.", "They are ready."],
                      [("m1", "u2", "They", "plural", {"kind": "entity", "members": ["alice"]}, {"reading": "distributive"})])
    assert admit(single, env(PERSON))["error"] == "InvalidInput: mention m1 target"


# (μ) Same-witness fusion and the J5 negatives

FUSED = ["exists", "service", ["and", ["unary", "deployed", ["var", 0]], ["unary", "reviewed", ["var", 0]]]]


def fusion(content=None, extra_sets=(), reading=None, opening="A service is deployed.", status="open"):
    doc = document([opening, "It is reviewed."], contents=content,
                   extra={"groups": [{"set": "rs1", "version": 1, "reading": "same-witness", "spans": ["u1", "u2"]}]},
                   kinds={"u1": "asserted"})
    doc["reading_sets"] = [reading_set(env(), "rs1", "u1", [("same-witness", reading or FUSED)], status),
                           *extra_sets]
    return doc


def test_mu_group_single_assertion(lean):
    result = admit(fusion())
    assert result["status"] == "ok", result
    # Fable B1: an open owning set is OPEN on every span (W2's rule); an authored one is CHECKED
    assert result["statuses"]["u1"] == result["statuses"]["u2"] == "OPEN"
    authored = admit(fusion(status="authored"))
    assert authored["statuses"]["u1"] == authored["statuses"]["u2"] == "CHECKED"
    assert admit(fusion({"u2": ["exists", "service", ["unary", "reviewed", ["var", 0]]]}))["error"] == \
        "IndependentFragment: u2"
    own_set = fusion(extra_sets=[reading_set(env(), "rs2", "u2", [("r", unary("reviewed", "api"))])])
    assert admit(own_set)["error"] == "IndependentFragment: u2"
    split = ["and", ["exists", "service", ["unary", "deployed", ["var", 0]]],
             ["exists", "service", ["unary", "reviewed", ["var", 0]]]]
    assert admit(fusion(reading=split))["error"] == "WitnessSplit: rs1@1:same-witness"
    fused_id = fusion()
    fused_id["discourse"]["groups"][0]["reading"] = "fused"
    assert admit(fused_id)["error"] == "InvalidInput: reading fused not in rs1@1"


def test_mu_group_reading_is_regenerated(lean):
    """Astra A2: a shared-witness reading that is not the spans' English is a manifest mismatch."""
    def fused(p, q):
        return ["exists", "service", ["and", ["unary", p, ["var", 0]], ["unary", q, ["var", 0]]]]
    for reading in (fused("safe", "safe"), fused("reviewed", "deployed"), fused("deployed", "safe")):
        assert admit(fusion(reading=reading))["error"] == "ManifestMismatch: groups.rs1@1:same-witness", reading
    universal = fusion(opening="Every service is deployed.")
    assert admit(universal)["error"] == \
        "InvalidInput: group rs1@1:same-witness spans are outside the supported fragment"


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
    doc = document(["The API is reviewed."] + ["The API is safe."] * sets,
                   contents={"u1": unary("reviewed", "api")},
                   kinds={f"u{k + 2}": "asserted" for k in range(sets)}, extra={"constraints": constraints})
    choices = [("r0", unary("safe", "api")), ("r1", unary("deployed", "api"))][:readings]
    doc["reading_sets"] = [reading_set(env(), f"rs{5 + k}", f"u{k + 2}", choices) for k in range(sets)]
    return doc


def joint(doc):
    row = run([case("discourse-joint", doc)])[0]
    assert row["status"] == "ok", row
    return row


def test_omicron_joint_set(lean):
    correlated = [{"kind": "requires", "a": ["rs5", 1, "r0"], "b": ["rs6", 1, "r0"]},
                  {"kind": "requires", "a": ["rs5", 1, "r1"], "b": ["rs6", 1, "r1"]}]
    row = joint(joint_doc(correlated))
    assert row["verdict"] == "COMPLETE"
    assert row["choices"] == [[["rs5", 1, 0], ["rs6", 1, 0]], [["rs5", 1, 1], ["rs6", 1, 1]]]
    excludes = [{"kind": "excludes", "a": ["rs5", 1, i], "b": ["rs6", 1, k]} for i in ("r0", "r1") for k in ("r0", "r1")]
    row = joint(joint_doc(excludes))
    assert row["verdict"] == "INVALID" and row["diagnostic"] == "InvalidCompatibility: rs5, rs6"
    row = joint(joint_doc([], sets=7))
    assert row["verdict"] == "UNKNOWN" and row["diagnostic"] == "ResourceLimit: joint choices"
    zero = joint(joint_doc([], sets=0))
    assert zero["choices"] == [[]] and zero["joint"] == ["top"]
    unknown_id = joint_doc([{"kind": "requires", "a": ["rs5", 1, "pattern-z"], "b": ["rs6", 1, "r0"]}])
    assert run([case("discourse-joint", unknown_id)])[0]["error"] == "InvalidInput: reading pattern-z not in rs5@1"


# (λ) The composition gate at report level

def test_lambda_report_extension(lean):
    excluded = [{"kind": "excludes", "a": ["rs5", 1, i], "b": ["rs6", 1, "r1"]} for i in ("r0", "r1")]
    graph = {"root": "leaf", "nodes": [{"name": "leaf", "ast": unary("deployed", "api"), "label": "readings:rs6@1:1"}]}
    doc = joint_doc(excluded)
    doc["graph"] = graph
    assert admit(doc)["error"] == "InvalidCompatibility: report leaf"
    unknown = joint_doc([], sets=7)
    unknown["graph"] = graph
    result = admit(unknown)
    assert result["status"] == "ok", result
    assert result["joint"] == "ResourceLimit: joint choices"
    # Fable B2: an unfinished joint set is UNKNOWN in the answer, never admitted
    assert result["admitted"] == "UNKNOWN"
    assert result["reading_verdicts"] == {"report leaf": "UNKNOWN (joint choices)"}


def test_recorded_choices_are_the_lemma_labels(lean):
    """Astra B (manifest_choices_are_labels): a recorded choice must be the lemmas' label."""
    lemma = {"name": "policy/l1", "conclusion": unary("safe", "api"),
             "leaves": [{"ast": unary("safe", "api"), "label": "readings:rs5@1:0"}]}
    doc = joint_doc([])
    doc["lemmas"] = [lemma]
    doc["discourse"]["choices"] = [["rs5", 1, "r0"]]
    assert admit(doc)["status"] == "ok"
    doc["discourse"]["choices"] = [["rs5", 1, "r1"]]
    assert admit(doc)["error"] == "ManifestMismatch: choices.policy/l1"


# (π) Document names

DOCS = {"documents": [{"name": "this_policy", "display": ["this document", "this policy"], "refers": "self", "version": 3},
                      {"name": "policy2", "display": ["policy 2"], "refers": {"import": "policy2"}, "version": 2,
                       "source_id": "x", "document_id": "y"}],
        "imports": {"policy2": {"source_id": "x", "document_id": "y", "bytes": "policy2.ve.md"}}}
DOC_CONSTANTS = {"api": "service", "alice": "person", "bob": "person", "this_policy": "document", "policy2": "document"}


def test_pi_document_names(lean):
    doc = document(["This policy supersedes policy 2."],
                   [("m1", "u1", "This policy", "document_name", {"kind": "document", "name": "this_policy"}),
                    ("m2", "u1", "policy 2", "document_name", {"kind": "document", "name": "policy2"})], extra=DOCS)
    assert unit_result(resolve(doc, env(constants=DOC_CONSTANTS)), "u1") == \
        ["binary", "supersedes", ["const", "this_policy"], ["const", "policy2"]]
    other = env(constants={**DOC_CONSTANTS, "policy9": "document"})
    assert admit(doc, other)["error"] == "InvalidInput: document sort document has other constants"


# (ρ, σ, τ, υ) Validity and the truth boundary

def validity_doc(sentence, document_name, holds, extra_docs=None, before=()):
    extra = copy.deepcopy(extra_docs or DOCS)
    uid = f"u{len(before) + 1}"
    extra["validity"] = [{"unit": uid, "document": document_name, "holds": holds}]
    return document([*before, sentence], kinds={f"u{i + 1}": "meta" for i in range(len(before) + 1)}, extra=extra)


def test_rho_validity_self(lean):
    positive = admit(validity_doc("This document is a valid VE document.", "this_policy", True), env(constants=DOC_CONSTANTS))
    assert positive["status"] == "ok", positive
    assert positive["validity"] == {"u1": "checked"} and positive["statuses"]["u1"] == "CHECKED"
    negative = admit(validity_doc("This document is not a valid VE document.", "this_policy", False),
                     env(constants=DOC_CONSTANTS))
    assert negative["validity"] == {"u1": "refuted"} and negative["statuses"]["u1"] == "LABELLED"


def stored_doc(sentence="The API is reviewed.", graph=None, format="ve-document@1", contents=None):
    return document([sentence], contents=contents if contents is not None else {"u1": unary("reviewed", "api")},
                    graph=graph or {"root": "n", "nodes": [{"name": "n", "ast": unary("reviewed", "api"), "unit": "u1"}]},
                    format=format)


def stored(tmp_path, doc=None, environment=None):
    """A sibling document's text and its pins, computed by the Python loader."""
    doc = doc or stored_doc()
    environment = environment or (env(profiles=["relational-fol@0"]) if doc["format"] == "ve-document@1" else env())
    source_id, document_id = python_ids(doc, environment, tmp_path, "stored.ve.md")
    return text(doc, environment), source_id, document_id


def import_docs(source_id, document_id):
    docs = copy.deepcopy(DOCS)
    docs["documents"][1].update({"source_id": source_id, "document_id": document_id})
    docs["imports"] = {"policy2": {"source_id": source_id, "document_id": document_id, "bytes": "policy2.ve.md"}}
    return docs


def claim(holds, docs, files, sentence=None):
    sentence = sentence or ("Policy 2 is a valid VE document." if holds else "Policy 2 is not a valid VE document.")
    return admit(validity_doc(sentence, "policy2", holds, docs), env(constants=DOC_CONSTANTS), files)


def test_tau_validity_import(lean, tmp_path):
    """Fable A2: an import is checked under its own environment, and a completed rejection is not
    a resource limit; Astra A5: pins are enforced."""
    body, source_id, document_id = stored(tmp_path)
    files = {"policy2.ve.md": body}
    docs = import_docs(source_id, document_id)
    checked = claim(True, docs, files)
    assert checked["status"] == "ok", checked
    assert checked["validity"] == {"u1": "checked"} and checked["statuses"]["u1"] == "CHECKED"
    assert claim(False, docs, files)["validity"] == {"u1": "refuted"}
    absent = claim(True, docs, {})
    assert absent["validity"] == {"u1": "unconfirmed (import bytes absent)"} and absent["statuses"]["u1"] == "LABELLED"
    assert claim(True, import_docs("0" * 64, document_id), files)["error"] == "StaleTarget: policy2"
    # Astra A5: the document id pin, and the declaration agreeing with the import table
    assert claim(True, import_docs(source_id, "0" * 64), files)["error"] == "StaleTarget: policy2"
    disagreeing = import_docs(source_id, document_id)
    disagreeing["documents"][1]["document_id"] = "1" * 64
    assert claim(True, disagreeing, files)["error"] == "ManifestMismatch: documents.policy2"
    # a completed rejection (an asserted node on a unit without content)
    rejected = stored_doc(contents={}, graph={"root": "n", "nodes": [{"name": "n", "ast": unary("reviewed", "api"),
                                                                       "unit": "u1"}]})
    rejected["units"][0]["kind"] = "exposition"
    body, source_id, document_id = stored(tmp_path, rejected)
    files, docs = {"policy2.ve.md": body}, import_docs(source_id, document_id)
    assert claim(False, docs, files)["validity"] == {"u1": "checked"}
    assert claim(True, docs, files)["validity"] == {"u1": "refuted"}
    # a check that hits a resource limit is unconfirmed for either polarity
    many = {"root": "n0", "nodes": [{"name": f"n{i}", "ast": ["top"], "label": "open:t"} for i in range(1001)]}
    body, source_id, document_id = stored(tmp_path, stored_doc(graph=many, contents={}))
    files, docs = {"policy2.ve.md": body}, import_docs(source_id, document_id)
    for holds in (True, False):
        assert claim(holds, docs, files)["validity"] == {"u1": "unconfirmed (ResourceLimit: graph node count)"}
    # a sibling that does not decode is an error of the importing document (4.1(10)), not an outcome
    bad = body.replace('"format"', '"extra": 1, "format"', 1)
    assert claim(True, import_docs(hashlib.sha256(bad.encode()).hexdigest(), document_id), {"policy2.ve.md": bad})[
        "error"] == "InvalidInput: document policy2: unknown document metadata"


def test_tau_import_under_its_own_profiles(lean, tmp_path):
    """Fable A2: a @2 import and a @1 import both check under their own declarations."""
    body, source_id, document_id = stored(tmp_path, stored_doc(format="ve-document@2"))
    assert claim(True, import_docs(source_id, document_id), {"policy2.ve.md": body})["validity"] == {"u1": "checked"}
    body, source_id, document_id = stored(tmp_path, stored_doc(format="ve-document@1"))
    assert claim(True, import_docs(source_id, document_id), {"policy2.ve.md": body})["validity"] == {"u1": "checked"}


def test_sigma_validity_embedded(lean, tmp_path):
    """Fable A2: an embedded unit's bytes are a document text, checked at depth 1."""
    inner = stored_doc(sentence="The API is reviewed.\n")
    inner_env = env(profiles=["relational-fol@0"])
    embedded = text(inner, inner_env)
    _, document_id = python_ids(inner, inner_env, tmp_path, "inner.ve.md")
    docs = {"documents": [{"name": "above", "display": ["the above document"], "refers": {"embedded": "u1"},
                           "version": 1, "document_id": document_id}]}
    doc = validity_doc("The above document is a valid VE document.", "above", True, docs, before=[embedded])
    constants = {"api": "service", "alice": "person", "bob": "person", "above": "document"}
    result = admit(doc, env(constants=constants))
    assert result["status"] == "ok", result
    assert result["validity"] == {"u2": "checked"}
    tampered = copy.deepcopy(doc)
    tampered["_source"] = tampered["_source"].replace("The API is reviewed.", "The API is reviewes.")
    assert admit(tampered, env(constants=constants))["error"] == "StaleTarget: above"


def test_upsilon_self_truth(lean):
    doc = document(["Everything in this document is true."], kinds={"u1": "meta"}, extra={"self_truth": ["u1"]})
    result = admit(doc)
    assert result["status"] == "ok", result
    assert result["self_truth"] == ["u1"] and result["statuses"]["u1"] == "LABELLED"
    bound_as_validity = document(["This document is correct."], kinds={"u1": "meta"},
                                 extra={**DOCS, "self_truth": ["u1"],
                                        "validity": [{"unit": "u1", "document": "this_policy", "holds": True}]})
    assert admit(bound_as_validity, env(constants=DOC_CONSTANTS))["error"] == "InvalidInput: u1 is a self-truth sentence"


def test_validity_binding_is_regenerated_from_wording(lean):
    """Astra A4, Fable A1: the manifest cannot turn a truth wording into a checked validity claim."""
    environment = env(constants=DOC_CONSTANTS)
    for sentence in ("Everything in this document is true.", "This document is correct.", "Policy 2 is correct."):
        assert admit(validity_doc(sentence, "this_policy", True), environment)["error"] == \
            "InvalidInput: validity unit u1 is not a validity wording", sentence
    assert admit(validity_doc("This document is not a valid VE document.", "this_policy", True), environment)[
        "error"] == "ManifestMismatch: validity.u1.holds"
    assert admit(validity_doc("This document is a valid VE document.", "this_policy", False), environment)[
        "error"] == "ManifestMismatch: validity.u1.holds"
    assert admit(validity_doc("Policy 2 is a valid VE document.", "this_policy", True), environment)[
        "error"] == "ManifestMismatch: validity.u1.document"


# (φ) Identity, tampering and the profile adapter

def phi_base():
    return document(["The API is reviewed.", "It is safe."], [("m1", "u2", "It", "pronoun", entity("api"))],
                    contents={"u2": unary("safe", "api")},
                    graph={"root": "n2", "nodes": [{"name": "n2", "ast": unary("safe", "api"), "unit": "u2"}]})


def test_phi_tampering_and_identity(lean, tmp_path):
    base = phi_base()
    tampered = copy.deepcopy(base)
    tampered["units"][1]["content"] = {"ast": unary("deployed", "api")}
    assert admit(tampered)["error"] == "ManifestMismatch: bound.u2"
    stale = copy.deepcopy(base)
    stale["discourse"]["definitions_version"] = "0" * 64
    assert admit(stale)["error"] == "StaleTarget: definitions@" + "0" * 64
    first = admit(copy.deepcopy(base))
    relabelled = copy.deepcopy(base)
    relabelled["discourse"]["anchors"][0]["label"] = "Renamed"
    second = admit(relabelled)
    assert first["document_id"] != second["document_id"]
    assert first["report"] == second["report"]
    resolved = resolve(copy.deepcopy(base))
    ast = unary("safe", "api")
    meaning = digest("ve-meaning-v0.2:relational-fol@0\n", {"environment_id": resolved["environment_id"], "ast": ast})
    assert resolved["units"]["u2"]["meaning_id"] == meaning == first["meaning_ids"]["u2"]
    plain_env = env(profiles=["relational-fol@0"])
    plain_id = digest("ve-environment-v0.2:relational-fol@0\n", plain_env)
    assert resolved["environment_id"] == plain_id
    moved = copy.deepcopy(base)
    moved["weights"] = []
    assert admit(moved)["document_id"] == first["document_id"]
    # Fable B3: the identities are the Python loader's on the same bytes
    same = stored_doc(format="ve-document@2")
    source_id, document_id = python_ids(same, env(), tmp_path)
    row = admit(same)
    assert (row["source_id"], row["document_id"]) == (source_id, document_id)


def test_phi_format1(lean, tmp_path):
    cases = json.loads((ROOT / "lean/VE/Route/examples/route-cases.json").read_text())
    admission = next(c for c in cases if c.get("kind") == "admission" and c["expected"].get("status") == "ok")
    delegated = {k: v for k, v in admission.items() if k != "expected"}
    row = run([delegated])[0]
    for key, value in admission["expected"].items():
        assert row[key] == value
    with_profile = copy.deepcopy(delegated)
    with_profile["environment"]["profiles"] = sorted(with_profile["environment"]["profiles"] + ["ve.discourse@1"])
    assert run([with_profile])[0]["error"] == "UnsupportedProfile: ve.discourse@1 requires ve-document@2"
    one = stored_doc()
    assert admit(one, env(profiles=["relational-fol@0"]))["admitted"] is True
    assert admit(one, env())["error"] == "UnsupportedProfile: ve.discourse@1 requires ve-document@2"


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
    row = resolve(iota_doc())
    assert unit_result(row, "u2") == ["forall", "service", ["implies", ["unary", "eligible", ["var", 0]],
                                                            ["unary", "reviewed", ["var", 0]]]]
    # Fable B3: the recorded version pin is carried, not dropped
    assert row["mentions"]["m1"]["pin"] == 2
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


# Regressions for the loop re-check (manage-agents discourse-looprecheck1.final.md). Each
# reproducer runs through the Lean route and, where Python implements the form, through the
# Python loader on the same document text.

# display strings the Python English parser reads back after expansion ("Api is deployed.")
PY_NAMES = [{"constant": "api", "display": "Api", "scope": "doc"}, *NAMES[1:]]


def python_outcome(doc, tmp_path, environment=None, files=None):
    """The Python loader's verdict on the same document text: its result, or the diagnostic."""
    for name, body in (files or {}).items():
        (tmp_path / name).write_text(body)
    path = tmp_path / "doc.ve.md"
    path.write_text(text(doc, environment))
    try:
        return check_document(path)
    except VEError as exc:
        return str(exc)


def test_reading_sets_regenerate_their_slots(lean, tmp_path):
    """looprecheck1 A (WellFormed.lean:224): a reading set is a unit's meaning, so the unit's
    source slots are discovered and every reading must be the elaboration."""
    labelled = {"root": "n", "nodes": [{"name": "n", "ast": unary("safe", "api"), "label": "readings:rs1@1:0"}]}
    for status in ("authored", "open"):
        for graph in (None, labelled):
            doc = document(["It is deployed."], names=PY_NAMES, kinds={"u1": "asserted"}, graph=graph)
            doc["reading_sets"] = [reading_set(env(), "rs1", "u1", [("r0", unary("safe", "api"))], status)]
            assert admit(doc)["error"] == "UnrecordedSlot: u1: [0, 1)", (status, graph)
            assert python_outcome(doc, tmp_path) == "UnrecordedSlot: u1: [0, 2)", (status, graph)
    # a recorded mention: the readings are compared with the elaboration, never trusted
    it = [("m1", "u1", "It", "pronoun", entity("api"))]
    for readings in ([("r0", unary("safe", "api"))], [("r0", unary("deployed", "api")), ("r1", unary("safe", "api"))]):
        doc = document(["It is deployed."], it, names=PY_NAMES, kinds={"u1": "asserted"})
        doc["reading_sets"] = [reading_set(env(), "rs1", "u1", readings, "authored" if len(readings) == 1 else "open")]
        assert admit(doc)["error"] == "ManifestMismatch: bound.u1", readings
        assert python_outcome(doc, tmp_path) == "ManifestMismatch: bound.u1", readings
    doc = document(["It is deployed."], it, names=PY_NAMES, kinds={"u1": "asserted"})
    doc["reading_sets"] = [reading_set(env(), "rs1", "u1", [("r0", unary("deployed", "api"))], "authored")]
    result = admit(doc)
    assert result["status"] == "ok", result
    assert result["statuses"] == {"u1": "CHECKED"} and result["bound"] == {"u1": unary("deployed", "api")}
    assert python_outcome(doc, tmp_path)["coverage"]["bytes_by_status"] == {"CHECKED": len("It is deployed.")}


def test_pending_unit_readings_never_reach_w2(lean, tmp_path):
    """looprecheck1 A (Admission.lean:304): a pending presupposition's reading set is withheld
    like its content, so it is never a report assumption."""
    claim = ["forall", "person", ["implies", MANAGER, ["unary", "ready", ["var", 0]]]]
    labelled = {"root": "n", "nodes": [{"name": "n", "ast": claim, "label": "readings:rs1@1:0"}]}
    for graph in (labelled, None):
        doc = eta("presuppositional", graph=graph)
        doc["units"][1]["kind"] = "asserted"
        doc["reading_sets"] = [reading_set(env(PERSON), "rs1", "u2", [("r0", claim)])]
        result = admit(doc, env(PERSON))
        if graph is None:
            assert result["status"] == "ok", result
            assert result["pending"] == [["u2", "PresuppositionUnresolved: m2"]] and result["bound"] == {}
            assert all(leaf["ast"] != claim for leaf in result["report"]["assumptions"])
        else:
            assert result["error"] == "AdmissionError: node n is not admitted under label readings:rs1@1:0"
        # Python does not elaborate descriptions: a unit with meaning using one is unsupported
        assert python_outcome(doc, tmp_path, env(PERSON)).startswith(
            "UnsupportedProfile: ve.discourse@1 definite, possessive elaboration is not implemented in Python (u2)")


def test_unknown_admission_is_an_unknown_outcome(lean, tmp_path):
    """looprecheck1 A (Admission.lean:98): a document whose own admission answers `admitted:
    UNKNOWN` (seven binary sets, 128 joint choices) is an unknown outcome, so a validity claim
    about it is unconfirmed for either polarity; the same holds for a claim about this document."""
    inner = joint_doc([], sets=7)
    assert admit(inner)["admitted"] == "UNKNOWN"
    body, source_id, document_id = stored(tmp_path, inner, env())
    for holds in (True, False):
        result = claim(holds, import_docs(source_id, document_id), {"policy2.ve.md": body})
        assert result["validity"] == {"u1": "unconfirmed (ResourceLimit: joint choices)"}, result
        assert result["statuses"]["u1"] == "LABELLED"
    sentences = ["The API is reviewed."] + ["The API is safe."] * 7 + ["This document is a valid VE document."]
    extra = {**copy.deepcopy(DOCS), "validity": [{"unit": "u9", "document": "this_policy", "holds": True}]}
    own = document(sentences, contents={"u1": unary("reviewed", "api")}, extra=extra,
                   kinds={**{f"u{k}": "asserted" for k in range(2, 9)}, "u9": "meta"})
    own["reading_sets"] = [reading_set(env(constants=DOC_CONSTANTS), f"rs{k}", f"u{k}", [("r0", unary("safe", "api")),
                                                                  ("r1", unary("deployed", "api"))])
                           for k in range(2, 9)]
    result = admit(own, env(constants=DOC_CONSTANTS))
    assert result["admitted"] == "UNKNOWN", result
    assert result["validity"] == {"u9": "unconfirmed (ResourceLimit: joint choices)"}
    assert result["statuses"]["u9"] == "LABELLED"


def malformed_blocks():
    """Stored `@2` documents whose discourse block does not decode (3.1), one per table shape."""
    def with_block(**changes):
        doc = stored_doc(format="ve-document@2")
        doc["discourse"].update(changes)
        return doc
    pronoun = {"id": "m1", "unit": "u1", "span": [0, 3], "form": "pronoun", "target": entity("api")}
    yield "mentions", with_block(mentions="not an array")
    yield "extra field", with_block(names=[{"constant": "api", "display": "Api", "scope": "doc", "extra": 1}])
    yield "group reading", with_block(groups=[{"set": "rs9", "version": 1, "reading": "r0", "spans": ["u1"]}])
    yield "version", with_block(version="ve.discourse@9")
    yield "reading", with_block(mentions=[{**pronoun, "reading": "collective"}])
    yield "document version", with_block(documents=[{"name": "x", "display": ["x"], "refers": "self"}])
    anchor = stored_doc(format="ve-document@2")
    anchor["discourse"]["anchors"][0]["kind"] = "chapter"
    yield "anchor kind", anchor


def test_stored_block_decodes_or_rejects_the_importer(lean, tmp_path):
    """looprecheck1 A (Admission.lean:192): a stored document must decode its whole discourse
    block (4.1(10)), not only its document and import tables; one that does not is an error of
    the importing document, never a completed rejection that checks a negative validity claim.
    Python rejects the same importer."""
    for name, inner in malformed_blocks():
        body = text(inner, env())
        _, source_id, document_id = stored_identities(body.encode())
        files = {"policy2.ve.md": body}
        negative = claim(False, import_docs(source_id, document_id), files)
        assert negative["status"] == "error", (name, negative)
        assert negative["error"].startswith("InvalidInput: document policy2: "), (name, negative)
        importer = document(["The API is reviewed."], contents={"u1": unary("reviewed", "api")},
                            extra=import_docs(source_id, document_id))
        environment = env(constants=DOC_CONSTANTS)
        lean_error = admit(importer, environment, files)["error"]
        python_error = python_outcome(importer, tmp_path, environment, files)
        assert lean_error == negative["error"], name
        assert python_error.startswith("InvalidInput: document policy2: "), (name, python_error)
    # a well-formed @2 import still decodes and is checked
    body, source_id, document_id = stored(tmp_path, stored_doc(format="ve-document@2"))
    assert claim(False, import_docs(source_id, document_id), {"policy2.ve.md": body})["validity"] == {"u1": "refuted"}


def test_own_block_decodes_as_strictly_in_python(lean, tmp_path):
    """The same class on the importing document: Python decodes its own block with the stored
    decoder, so a field Lean's strict decoder rejects is rejected in Python too."""
    doc = document(["Api is reviewed.", "It is deployed."], [("m1", "u2", "It", "pronoun", entity("api"))],
                   names=PY_NAMES, contents={"u1": unary("reviewed", "api"), "u2": unary("deployed", "api")})
    assert isinstance(python_outcome(doc, tmp_path), dict)
    doc["discourse"]["mentions"][0]["note"] = "free text"
    assert admit(doc)["error"].startswith("fields do not match")
    assert python_outcome(doc, tmp_path) == "InvalidInput: discourse fields"


def test_location_binding_never_covers_a_slot(lean, tmp_path):
    """looprecheck1 A (discourse.py:582): relabelling `It` as a navigation (or section_ref)
    mention does not account for its slot; both implementations report it unrecorded."""
    for form in ("navigation", "section_ref"):
        doc = document(["Api is reviewed.", "It is deployed."],
                       [("m1", "u2", "It", form, {"kind": "anchor", "name": "doc"})], names=PY_NAMES,
                       contents={"u1": unary("reviewed", "api"), "u2": unary("deployed", "api")})
        assert admit(doc)["error"] == "UnrecordedSlot: u2: [0, 1)", form
        assert python_outcome(doc, tmp_path) == "UnrecordedSlot: u2: [17, 19)", form


def test_ordinal_competitors_are_their_pairs(lean, tmp_path):
    """looprecheck1 B (discourse.py:406): two coordinations `[api, alice]` and `[api, bob]` are two
    candidates of "the former" although both select `api`; both implementations reject."""
    doc = document(["Api and Alice are reviewed.", "Api and Bob are reviewed.", "The former is deployed."],
                   [("m1", "u3", "The former", "ordinal_pair", {"kind": "entity", "name": "api", "pair": ["api", "alice"]})],
                   names=PY_NAMES, contents={"u3": unary("deployed", "api")})
    assert admit(doc)["error"] == "AmbiguousReference: m1: api"
    assert python_outcome(doc, tmp_path) == "AmbiguousReference: m1: api"
    # one coordination: resolved in both
    single = document(["Api and Alice are reviewed.", "The former is deployed."],
                      [("m1", "u2", "The former", "ordinal_pair", {"kind": "entity", "name": "api", "pair": ["api", "alice"]})],
                      names=PY_NAMES, contents={"u2": unary("deployed", "api")})
    assert admit(single)["bound"] == {"u2": unary("deployed", "api")}
    assert python_outcome(single, tmp_path)["references"][0]["status"] == "resolved"
    # a constant registered twice is one declaration error in both, not two candidates
    twice = document(["Api is reviewed.", "It is deployed."], [("m1", "u2", "It", "pronoun", entity("api"))],
                     names=[*PY_NAMES, {"constant": "api", "display": "The service", "scope": "doc"}],
                     contents={"u1": unary("reviewed", "api"), "u2": unary("deployed", "api")})
    assert admit(twice)["error"] == "DuplicateDeclaration: name api"
    assert python_outcome(twice, tmp_path) == "DuplicateDeclaration: name api"
