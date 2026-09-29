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
             format="ve-document@2", sep=" "):
    """A document front matter; `_source` is the body. Units cover every source byte; `sep` follows
    every sentence but the last (a unit boundary with no space after the full stop when empty)."""
    source, units = "", []
    for i, s in enumerate(sentences):
        start = len(source.encode())
        source += s + (sep if i + 1 < len(sentences) and not s.endswith("\n") else "")
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
    # u2 starts at byte 21; the diagnostic prints the surface's prose bytes (the Python text)
    for sentence, span in [("It is deployed.", "[21, 23)"), ("This service is deployed.", "[21, 33)"),
                           ("It is deployed and safe.", "[21, 23)"), ("Its owner is deployed.", "[21, 24)")]:
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
    assert unit_result(resolve(eta(omit_possessive=True), env(PERSON)), "u2") == "UnrecordedSlot: u2: [19, 22)"


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
    # Fable B3: the recorded version pin is carried, not dropped (and checked: looprecheck1 B)
    assert row["mentions"]["m1"]["pin"] == 2
    assert row["well_formed"] == "StaleTarget: m1: eligible@2"
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
            assert admit(doc)["error"] == "UnrecordedSlot: u1: [0, 2)", (status, graph)
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
        # Python does not elaborate descriptions: its abstention is a hint, the verdict Lean's
        python = python_outcome(doc, tmp_path, env(PERSON))
        if graph is None:
            assert python["discourse_hints"] == [
                "UnsupportedProfile: ve.discourse@1 definite, possessive elaboration is not implemented in Python (u2)"]
            assert python["report_id"] == result["report_id"]
        else:
            assert python == result["error"]


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
        assert admit(doc)["error"] == "UnrecordedSlot: u2: [17, 19)", form
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


def test_authored_reading_labels_extend(lean, tmp_path):
    """looprecheck1 B (discourse.py:227, Admission.lean:323): an authored singleton's reading label
    passes @1 and must pass @2 (an authored set is fixed at its one reading in every choice the
    composition gate reads), in both implementations and for `v:all` alike."""
    for label in ("readings:rs1@1:0", "readings:rs1@1:all"):
        outcomes = []
        for fmt in ("ve-document@1", "ve-document@2"):
            environment = env(profiles=["relational-fol@0"]) if fmt.endswith("@1") else env()
            doc = document(["The API is safe."], kinds={"u1": "asserted"}, format=fmt,
                           graph={"root": "n", "nodes": [{"name": "n", "ast": unary("safe", "api"), "label": label}]})
            if fmt.endswith("@2"):
                doc["discourse"] = {}
            doc["reading_sets"] = [reading_set(environment, "rs1", "u1", [("r0", unary("safe", "api"))], "authored")]
            lean_row = admit(doc, environment)
            python = python_outcome(doc, tmp_path, environment)
            assert lean_row.get("admitted") is True, (label, fmt, lean_row)
            assert python["admission"]["admitted"] is True, (label, fmt, python)
            outcomes.append((lean_row["report"], python["admission"]["report"]))
        assert outcomes[0] == outcomes[1], label
    # a recorded reference whose authored reading is the elaboration, cited by its label
    doc = document(["It is deployed."], [("m1", "u1", "It", "pronoun", entity("api"))], names=PY_NAMES,
                   kinds={"u1": "asserted"},
                   graph={"root": "n", "nodes": [{"name": "n", "ast": unary("deployed", "api"), "label": "readings:rs1@1:0"}]})
    doc["reading_sets"] = [reading_set(env(), "rs1", "u1", [("r0", unary("deployed", "api"))], "authored")]
    assert admit(doc)["admitted"] is True
    assert python_outcome(doc, tmp_path)["admission"]["admitted"] is True
    # an open set's label that no compatible choice selects is still rejected
    excluded = joint_doc([{"kind": "excludes", "a": ["rs5", 1, "r0"], "b": ["rs6", 1, "r1"]},
                          {"kind": "excludes", "a": ["rs5", 1, "r1"], "b": ["rs6", 1, "r1"]}])
    excluded["graph"] = {"root": "leaf", "nodes": [{"name": "leaf", "ast": unary("deployed", "api"), "label": "readings:rs6@1:1"}]}
    assert admit(excluded)["error"] == "InvalidCompatibility: report leaf"
    assert python_outcome(excluded, tmp_path) == "InvalidCompatibility: report leaf"


def test_definition_pins_are_checked(lean, tmp_path):
    """looprecheck1 B (Wire.lean:114): a definition pin is regenerated, never carried unchecked.
    No environment the admission accepts declares a definition version, so any pin is stale;
    without a pin the reference resolves as before. A pin on any other target is malformed."""
    def iota(version=None, form="definition_ref"):
        doc = iota_doc()
        mention = doc["discourse"]["mentions"][0]
        mention["form"] = form
        if version is None:
            mention["target"].pop("version")
        else:
            mention["target"]["version"] = version
        doc["units"][1].update(kind="asserted", support="assumption", content={"ast": [
            "forall", "service", ["implies", ["unary", "eligible", ["var", 0]], ["unary", "reviewed", ["var", 0]]]]})
        return doc
    for version in (2, 999):
        assert admit(iota(version))["error"] == f"StaleTarget: m1: eligible@{version}"
        assert python_outcome(iota(version), tmp_path) == f"StaleTarget: m1: eligible@{version}"
    unpinned = admit(iota())
    assert unpinned["status"] == "ok" and unpinned["statuses"]["u2"] == "CHECKED", unpinned
    # Python does not elaborate definition references: its abstention is a hint, the verdict and
    # the statuses Lean's
    python = python_outcome(iota(), tmp_path)
    assert python["discourse_hints"][0].startswith("UnsupportedProfile: ve.discourse@1 definition_ref")
    assert python["coverage"]["bytes_by_status"].get("CHECKED")
    pinned_pronoun = document(["Api is reviewed.", "It is deployed."],
                              [("m1", "u2", "It", "pronoun", {**entity("api"), "version": 1})], names=PY_NAMES,
                              contents={"u1": unary("reviewed", "api"), "u2": unary("deployed", "api")})
    assert admit(pinned_pronoun)["error"] == "InvalidInput: mention m1 target"
    assert python_outcome(pinned_pronoun, tmp_path) == "InvalidInput: mention m1 target"


def test_renewal_items_are_counterexamples_to_the_approved_statements(lean, tmp_path):
    """looprecheck1 B (DISCOURSE.md:93): each statement marked (renewal) in lean/DISCOURSE.md is
    false as approved in draft 4. On route outputs, each approved statement's hypotheses hold
    and its conclusion fails; the proved replacement is what the spec reviewers are asked to
    approve (lean/DISCOURSE.md, "Renewal requests")."""
    from ve.english import parse_english
    # R1 ill_typed_target: every slot of eta's two-slot derivation is recorded and accessible,
    # the elaboration is ill typed, and the diagnostic cannot start with both mention ids
    row = resolve(eta(target="api"), env(PERSON))
    assert all(row["mentions"][m]["accessible_recorded"] for m in ("m1", "m2"))
    error = unit_result(row, "u2")
    assert error == "IllTypedTarget: m1: api" and not error.startswith("IllTypedTarget: m2")
    # R2 validity_import: checking an import under the importing document's profiles rejects a
    # valid @1 document, so the approved outcome would refute a true claim
    one = stored_doc(format="ve-document@1")
    assert admit(one, env())["error"] == "UnsupportedProfile: ve.discourse@1 requires ve-document@2"
    assert admit(one, env(profiles=["relational-fol@0"]))["admitted"] is True
    # R3 validity_self: an admission whose joint set hit the budget is UNKNOWN, so its own validity
    # claim cannot be `checked` (covered in test_unknown_admission_is_an_unknown_outcome)
    # R4 validity_independent: a malformed binding rejects j while stripValidity j is admitted
    bound = document(["This document is correct."], kinds={"u1": "meta"},
                     extra={**DOCS, "self_truth": ["u1"], "validity": [{"unit": "u1", "document": "this_policy", "holds": True}]})
    assert admit(bound, env(constants=DOC_CONSTANTS))["error"] == "InvalidInput: u1 is a self-truth sentence"
    del bound["discourse"]["validity"]
    assert admit(bound, env(constants=DOC_CONSTANTS))["admitted"] is True
    # R5 9.5 ParseSound/OneReading on the approved surface: a derivation's yield is the source,
    # which the core parser does not read (it reads the presentation)
    alpha = document(["It is safe."], [("m1", "u1", "It", "pronoun", entity("api"))])
    assert unit_result(resolve(alpha), "u1") == unary("safe", "api")
    with pytest.raises(VEError, match="referent of it is incomplete"):
        parse_english(base_env(env()), "It is safe.")
    # R6 citation/report_extends_joint: the joint set of an authored-only document is the one empty
    # choice, which extends no label; the label is admitted in @1 and (now) in @2
    authored = document(["The API is safe."], kinds={"u1": "asserted"},
                        graph={"root": "n", "nodes": [{"name": "n", "ast": unary("safe", "api"), "label": "readings:rs1@1:0"}]})
    authored["discourse"] = {}
    authored["reading_sets"] = [reading_set(env(), "rs1", "u1", [("r0", unary("safe", "api"))], "authored")]
    result = admit(authored)
    assert result["admitted"] is True and result["joint"] == 1
    assert [leaf["label"] for leaf in result["report"]["assumptions"]] == ["readings:rs1@1:0"]
    # R7 fixture iota (10): `sec2` exports `eligible`, its definition unit lies in `sec2` and m1 pins
    # version 2, yet no admitted environment declares a definition version, so the pinned
    # reference is `StaleTarget` where the fixture expects CHECKED; unpinned, it is CHECKED
    # (looprecheck2 B, WellFormed.lean:190)
    pinned = iota_doc()
    pinned["units"][1].update(kind="asserted", support="assumption", content={"ast": [
        "forall", "service", ["implies", ["unary", "eligible", ["var", 0]], ["unary", "reviewed", ["var", 0]]]]})
    assert pinned["discourse"]["anchors"][1]["exports"] == ["eligible"] and pinned["units"][0]["kind"] == "definition"
    assert pinned["discourse"]["mentions"][0]["target"]["version"] == 2
    assert admit(pinned)["error"] == "StaleTarget: m1: eligible@2"
    del pinned["discourse"]["mentions"][0]["target"]["version"]
    assert admit(pinned)["statuses"]["u2"] == "CHECKED"


# Regressions for the second loop re-check (manage-agents discourse-looprecheck2.final.md).

# every character Python's `\s` (str.isspace) reads as a space, beyond ' ', \t, \n, \r
UNICODE_SPACES = [chr(c) for c in range(0x110000) if chr(c).isspace() and chr(c) not in " \t\n\r"]


def slot_outcomes(sentences, tmp_path, contents, names=PY_NAMES, environment=None):
    """The Lean route's error (None when it admits) and the Python outcome on one document."""
    doc = document(sentences, names=names, contents=contents)
    return admit(doc, environment).get("error"), python_outcome(doc, tmp_path, environment)


def test_unicode_spaces_separate_words(lean, tmp_path):
    """looprecheck2 A (Access.lean:28): a no-break or any other Unicode space separates words in
    Lean as `\\s` does in Python, so "It<space>is safe." has the pronoun slot `It`, and a
    quantifier before one is a competing binder in both implementations."""
    safe = {"u1": unary("safe", "api")}
    for space in UNICODE_SPACES:
        lean_error, python_error = slot_outcomes([f"It{space}is safe."], tmp_path, safe)
        assert lean_error == python_error == "UnrecordedSlot: u1: [0, 2)", (hex(ord(space)), lean_error, python_error)
    # recorded, the unit's wording is not discourse wording (4.1(4)): rejected alike in both; with
    # one ASCII space the pronoun resolves in both
    doc = document(["It is safe."], [("m1", "u1", "It", "pronoun", entity("api"))], names=PY_NAMES,
                   contents=safe)
    assert agree(doc, tmp_path) == "InvalidInput: discourse wording of u1"
    doc = document(["It is safe."], [("m1", "u1", "It", "pronoun", entity("api"))], names=PY_NAMES,
                   contents=safe)
    assert admit(doc)["bound"] == {"u1": unary("safe", "api")}
    assert python_outcome(doc, tmp_path)["references"][0]["status"] == "resolved"
    # a quantifier spelled with a no-break space still competes (fixture beta)
    beta = document(["A service is deployed.", "Api is reviewed.", "It is safe."],
                    [("m1", "u3", "It", "pronoun", entity("api"))], names=PY_NAMES,
                    contents={"u3": unary("safe", "api")})
    assert unit_result(resolve(beta), "u3") == "UnresolvedReference: m1"
    assert admit(beta)["error"] == "UnresolvedReference: m1"
    assert not isinstance(python_outcome(beta, tmp_path), dict)


# characters a word may carry that are not ASCII letters or digits: apostrophes, hyphens, the
# underscore, the modifier letter apostrophe, a non-breaking hyphen, a combining mark, a
# non-ASCII letter, a zero-width space and a word joiner
JOINERS = ["'", "’", "-", "_", "ʼ", "‑", "́", "é", "​", "⁠"]


def test_joined_reference_words_are_slots(lean, tmp_path):
    """looprecheck2 A (Access.lean:28, Grammar.lean:95) and B (discourse.py:272): a reference
    word joined to anything else inside a word is still a slot. With a submitted formula and no
    mention, each unit is `UnrecordedSlot` in both implementations, with the same byte range."""
    safe = {"u1": unary("safe", "api")}
    for sentence in ["It's safe.", "It’s safe.", "He's safe.", "They're safe.", "It-is safe.",
                     "It_ is safe.", "Itʼs safe."]:
        lean_error, python_error = slot_outcomes([sentence], tmp_path, safe)
        width = 4 if sentence.startswith("They") else 2
        assert lean_error == python_error == f"UnrecordedSlot: u1: [0, {width})", (sentence, lean_error, python_error)
    lean_error, python_error = slot_outcomes(["Api is safe; it's deployed."], tmp_path, safe)
    assert lean_error == python_error == "UnrecordedSlot: u1: [13, 15)"
    # the class: every joiner on either side of every reference word, and every other surface
    for word in ("it", "she", "he", "her", "him", "his", "its", "their", "they", "them", "former", "latter", "such"):
        for joiner in JOINERS:
            for sentence in [f"{word.capitalize()}{joiner}x is safe.", f"Api is x{joiner}{word} safe."]:
                lean_error, python_error = slot_outcomes([sentence], tmp_path, safe)
                assert lean_error == python_error, (sentence, lean_error, python_error)
                assert lean_error.startswith("UnrecordedSlot: u1: ["), (sentence, lean_error)
    for sentence in ["This-service is safe.", "By-clause 3, api is safe.", "The-safe is safe.", "Api is the_safe."]:
        lean_error, python_error = slot_outcomes([sentence], tmp_path, safe)
        assert lean_error == python_error, (sentence, lean_error, python_error)
        assert lean_error.startswith("UnrecordedSlot: u1: ["), (sentence, lean_error)
    # a word that merely begins with a reference word's letters is not one
    lean_error, python_error = slot_outcomes(["Itself is safe."], tmp_path, safe)
    assert lean_error is None and isinstance(python_error, dict), (lean_error, python_error)


def test_every_reference_surface_is_recorded(lean, tmp_path):
    """looprecheck2 A, the same class inside an accepted derivation: a registered spelling that
    joins a reference word (`He-api`) derives without a slot, yet its `he` is a reference surface
    no mention records, so the unit is `UnrecordedSlot` in both implementations. A section label
    spelled as a reference word is one too (Python does not elaborate definition references)."""
    names = [{"constant": "api", "display": "He-api", "scope": "doc"}, *NAMES[1:]]
    lean_error, python_error = slot_outcomes(["He-api is safe."], tmp_path, {"u1": unary("safe", "api")}, names)
    assert lean_error == python_error == "UnrecordedSlot: u1: [0, 2)"
    plain = [{"constant": "api", "display": "Web-api", "scope": "doc"}, *NAMES[1:]]
    lean_error, python_error = slot_outcomes(["Web-api is safe."], tmp_path, {"u1": unary("safe", "api")}, plain)
    assert lean_error is None and isinstance(python_error, dict), (lean_error, python_error)
    def section(label):
        doc = document(["Eligible services are reviewed services.",
                        f"Every eligible service is reviewed, where eligible has the meaning defined in section {label}."],
                       [("m1", "u2", "eligible", "definition_ref", {"kind": "predicate", "name": "eligible"})],
                       kinds={"u1": "definition"}, contents={"u2": [
                           "forall", "service", ["implies", ["unary", "eligible", ["var", 0]], ["unary", "reviewed", ["var", 0]]]]})
        doc["discourse"]["anchors"].append({"id": "sec2", "kind": "section", "parent": "doc", "label": label,
                                            "span": [0, doc["units"][1]["span"][1]], "exports": ["eligible"]})
        return admit(doc)
    assert section("2")["statuses"]["u2"] == "CHECKED"
    assert section("its")["error"] == "UnrecordedSlot: u2: [127, 130)"


# Regressions for discourse-loop.final.md and the slots directive (manage-agents
# discourse-slots-directive.md): slot discovery is per unit, byte-exact and longest-first, with the
# same case fold, in Lean and Python; both print the same `UnrecordedSlot` text.

SELF = {"documents": [{"name": "this_policy", "display": ["It is safe"], "refers": "self", "version": 1}]}
SELF_CONSTANTS = {"api": "service", "alice": "person", "bob": "person", "this_policy": "document"}


def test_units_are_lexed_on_their_own(lean, tmp_path):
    """A (Wire.lean:234): `Api is reviewed.It is safe.` as units [0, 16) and [16, 27). Lexing the
    whole prose joined `reviewed.It` into one token that lay in neither unit, so u2 lost `It` and
    was admitted with nothing bound. Each unit is now lexed from its own bytes."""
    contents = {"u1": unary("reviewed", "api"), "u2": unary("safe", "api")}
    doc = document(["Api is reviewed.", "It is safe."], names=PY_NAMES, contents=contents, sep="")
    assert [u["span"] for u in doc["units"]] == [[0, 16], [16, 27]]
    assert admit(doc)["error"] == python_outcome(doc, tmp_path) == "UnrecordedSlot: u2: [16, 18)"
    recorded = document(["Api is reviewed.", "It is safe."], [("m1", "u2", "It", "pronoun", entity("api"))],
                        names=PY_NAMES, contents=contents, sep="")
    lean_row, python = admit(recorded), python_outcome(recorded, tmp_path)
    assert lean_row["bound"] == {"u2": unary("safe", "api")}
    assert lean_row["report_id"] == python["report_id"]
    # the class: every unit boundary, with or without a space, and a unit that begins inside a word
    for sep in ("", " ", "\n", "\u00a0"):
        doc = document(["Api is reviewed.", "Its owner is ready."], names=PY_NAMES, sep=sep,
                       contents={"u1": unary("reviewed", "api"), "u2": unary("ready", "alice")})
        start = doc["units"][1]["span"][0]
        assert admit(doc)["error"] == python_outcome(doc, tmp_path) == f"UnrecordedSlot: u2: [{start}, {start + 3})"
    # a boundary inside `Apiit`: u1 ends after `Api`, so u2's `it` is a word of its own
    doc = document(["Api", "it is safe."], names=PY_NAMES, sep="", contents={"u2": unary("safe", "api")})
    assert admit(doc)["error"] == python_outcome(doc, tmp_path) == "UnrecordedSlot: u2: [3, 5)"


def test_coverage_is_exact_and_longest_first(lean, tmp_path):
    """A (WellFormed.lean:271): the self-document display `It is safe` is one surface of
    `It is safe.`; a pronoun recorded on `It` overlaps it but does not record it, so the unit is
    `UnrecordedSlot: u1: [0, 10)` in both (Lean admitted it CHECKED)."""
    environment = env(constants=SELF_CONSTANTS)
    it = ("m1", "u1", "It", "pronoun", entity("api"))
    doc = document(["It is safe."], [it], names=PY_NAMES, contents={"u1": unary("safe", "api")}, extra=SELF)
    assert admit(doc, environment)["error"] == python_outcome(doc, tmp_path, environment) == \
        "UnrecordedSlot: u1: [0, 10)"
    # without the display the pronoun alone is the surface and resolves in both
    plain = document(["It is safe."], [it], names=PY_NAMES, contents={"u1": unary("safe", "api")},
                     extra={"documents": [{**SELF["documents"][0], "display": ["this document"]}]})
    lean_row, python = admit(plain, environment), python_outcome(plain, tmp_path, environment)
    assert lean_row["bound"] == {"u1": unary("safe", "api")} and lean_row["report_id"] == python["report_id"]
    # a mention that contains a surface without being it is not enough either
    wide = document(["It is safe."], [("m1", "u1", "It is", "pronoun", entity("api"))], names=PY_NAMES,
                    contents={"u1": unary("safe", "api")})
    assert admit(wide)["error"] == python_outcome(wide, tmp_path) == "UnrecordedSlot: u1: [0, 2)"
    # `the former` is one surface, recorded whole; its `former` alone is not
    pair = {"kind": "entity", "name": "api", "pair": ["api", "alice"]}
    for text, error in [("The former", None), ("former", "UnrecordedSlot: u2: [28, 38)")]:
        doc = document(["Api and Alice are reviewed.", "The former is deployed."],
                       [("m1", "u2", text, "ordinal_pair", pair)], names=PY_NAMES,
                       contents={"u2": unary("deployed", "api")})
        lean_row, python = admit(doc), python_outcome(doc, tmp_path)
        if error is None:
            assert lean_row["bound"] == {"u2": unary("deployed", "api")} and lean_row["report_id"] == python["report_id"]
        else:
            assert lean_row["error"] == python == error


def test_unicode_case_variants_are_folded(lean, tmp_path):
    """B (Grammar.lean:115): `İt`, `ıt` and `ſuch` read `it` and `such` in Python's case-insensitive
    patterns; Lean's segments were ASCII-only and admitted them. Both now fold exactly the four
    characters `re.I` equates with ASCII letters (İ, ı, ſ, the Kelvin sign)."""
    safe = {"u1": unary("safe", "api")}
    for sentence in ["İt is safe.", "ıt is safe.", "ſuch service is safe.", "Iſ it safe.", "Api is ſafe; ıts owner is ready.",
                     "Tḣe api is safe; ſhe is ready.", "Api is safe; the formeꝛ is. It is.", "Api is reviewed by ſection."]:
        lean_error, python_error = slot_outcomes([sentence], tmp_path, safe)
        assert lean_error == python_error and python_error.startswith("UnrecordedSlot: u1: ["), \
            (sentence, lean_error, python_error)
    lean_error, python_error = slot_outcomes(["İt is safe."], tmp_path, safe)
    assert lean_error == "UnrecordedSlot: u1: [0, 3)"
    # recorded, a folded pronoun is not discourse wording (4.1(4)): rejected alike in both
    doc = document(["İt is safe."], [("m1", "u1", "İt", "pronoun", entity("api"))], names=PY_NAMES, contents=safe)
    assert agree(doc, tmp_path) == "InvalidInput: discourse wording of u1"
    # a quantifier spelled with ſ is still a competing binder in both (fixture beta)
    beta = document(["ſome service is deployed.", "Api is reviewed.", "It is safe."],
                    [("m1", "u3", "It", "pronoun", entity("api"))], names=PY_NAMES,
                    contents={"u3": unary("safe", "api")})
    assert admit(beta)["error"] == "UnresolvedReference: m1"
    assert not isinstance(python_outcome(beta, tmp_path), dict)
    # a character outside the fold is not a letter of a reference word, in either checker
    lean_error, python_error = slot_outcomes(["Іt is safe."], tmp_path, safe)  # Cyrillic І
    assert lean_error is None and isinstance(python_error, dict)


# The differential property (slots directive 3): generated documents, Lean admits iff Python
# admits, with the same report, and otherwise the same diagnostic text. Python abstains
# (`UnsupportedProfile`) on the forms it does not elaborate (a document name in a unit with meaning).

PAIR = {"kind": "entity", "name": "alice", "pair": ["alice", "bob"]}
DIFF_SENTENCES = [
    ("Api is reviewed.", unary("reviewed", "api"), []),
    ("It is safe.", unary("safe", "api"), [("It", "pronoun", entity("api"))]),
    ("It is deployed.", unary("deployed", "api"), [("It", "pronoun", entity("api"))]),
    ("This service is safe.", unary("safe", "api"), [("This service", "demonstrative", entity("api")),
                                                      ("This", "pronoun", entity("api"))]),
    ("Alice is ready.", unary("ready", "alice"), []),
    ("She is ready.", unary("ready", "alice"), [("She", "pronoun", entity("alice"))]),
    ("Alice and Bob are ready.", ["and", unary("ready", "alice"), unary("ready", "bob")], []),
    ("The former is ready.", unary("ready", "alice"), [("The former", "ordinal_pair", PAIR),
                                                       ("former", "ordinal_pair", PAIR)]),
    ("A service is deployed.", ["exists", "service", ["unary", "deployed", ["var", 0]]], []),
    ("İt is safe.", unary("safe", "api"), [("İt", "pronoun", entity("api"))]),
]
DIFF_DISPLAYS = ["It is safe", "this document", "Api is reviewed", "she"]
DIFF_SEPARATORS = ["", " ", "\n", " "]


def diff_document(rng):
    """A random document: two to four sentences, a random separator after each (a unit boundary
    with no space after the full stop included), random contents, a random subset of the candidate
    mentions (the display surfaces among them) and random displays for the document itself."""
    picks = [rng.choice(DIFF_SENTENCES) for _ in range(rng.randint(2, 4))]
    displays = rng.sample(DIFF_DISPLAYS, rng.randint(0, 2))
    sep = rng.choice(DIFF_SEPARATORS)
    contents = {f"u{i + 1}": ast for i, (_, ast, _) in enumerate(picks) if rng.random() < 0.75}
    mentions = []
    for i, (sentence, _, candidates) in enumerate(picks):
        found = [(text, form, target) for text, form, target in candidates]
        found += [(d, "document_name", {"kind": "document", "name": "this_policy"}) for d in displays
                  if d.lower() in sentence.lower()]
        chosen = [c for c in found if rng.random() < 0.6]
        for text, form, target in chosen[:1]:  # recorded mentions of one unit never overlap
            mentions.append((f"m{len(mentions) + 1}", f"u{i + 1}", text, form, target))
    extra = {"documents": [{"name": "this_policy", "display": displays or ["this document"], "refers": "self",
                            "version": 1}]}
    return document([p[0] for p in picks], mentions, names=PY_NAMES, contents=contents, extra=extra, sep=sep)


def diff_cases():
    """The two loop reproducers first, then generated documents."""
    contents = {"u1": unary("reviewed", "api"), "u2": unary("safe", "api")}
    other = {"documents": [{**SELF["documents"][0], "display": ["this document"]}]}
    yield document(["Api is reviewed.", "It is safe."], names=PY_NAMES, contents=contents, sep="", extra=other)
    yield document(["It is safe."], [("m1", "u1", "It", "pronoun", entity("api"))], names=PY_NAMES,
                   contents={"u1": unary("safe", "api")}, extra=SELF)
    rng = __import__("random").Random(20260929)
    for _ in range(300):
        yield diff_document(rng)


def test_lean_and_python_discover_the_same_slots(lean, tmp_path):
    environment = env(constants=SELF_CONSTANTS)
    docs = list(diff_cases())
    rows = run([case("admission", doc, environment) for doc in docs])
    compared = admitted = 0
    for doc, row in zip(docs, rows):
        python = python_outcome(doc, tmp_path, environment)
        where = (doc["_source"], doc["discourse"]["mentions"], doc["discourse"]["documents"][0]["display"],
                 sorted(u["id"] for u in doc["units"] if "content" in u))
        if isinstance(python, str) and python.startswith("UnsupportedProfile"):
            continue
        compared += 1
        if isinstance(python, dict):
            admitted += 1
            assert row.get("status") == "ok", (where, row.get("error"))
            assert (row["report_id"], row["references"]) == (python["report_id"], python["references"]), where
        else:
            assert row.get("error") == python, (where, row.get("error"), python)
    assert rows[0]["error"] == "UnrecordedSlot: u2: [16, 18)"
    assert rows[1]["error"] == "UnrecordedSlot: u1: [0, 10)"
    assert compared > 200 and 20 < admitted < compared, (compared, admitted)


# Regressions for the discourse loop re-check (manage-agents discourse2-looprecheck1.final.md): the
# text inputs of `Acc` are read as segments and mention surfaces by the shared lexer, in both.

IT_API = ("m1", "u2", "It", "pronoun", entity("api"))
SAFE_U2 = {"u2": unary("safe", "api")}


def agree(doc, tmp_path, environment=None):
    """Lean's and Python's outcomes on one document: the shared diagnostic, or `admitted` when both
    admit it with the same report."""
    row, python = admit(doc, environment), python_outcome(doc, tmp_path, environment)
    if isinstance(python, dict):
        assert row.get("status") == "ok", (doc["_source"], row.get("error"))
        assert (row["report_id"], row["references"]) == (python["report_id"], python["references"]), doc["_source"]
        return "admitted"
    assert row.get("error") == python, (doc["_source"], row.get("error"), python)
    return python


def noun_env(noun="system"):
    environment = env()
    environment["vocabulary"]["sorts"]["service"]["verbalisation"] = {"singular": noun, "plural": noun + "s"}
    return environment


def test_joined_words_never_hide_a_competing_quantifier(lean, tmp_path):
    """A (Access.lean:183): `A service's owner is ready.` quantifies a service, so a later `It` has a
    competing binder of its target's sort. Lean read `service's` as one word and admitted u2
    CHECKED; Python rejected. Both now read the binders as segments."""
    for opening in ["A service's owner is ready.", "A service’s owner is ready."]:
        doc = document([opening, "It is safe."], [IT_API], names=PY_NAMES, contents=SAFE_U2)
        assert agree(doc, tmp_path) == "UnresolvedReference: m1", opening
    # the class: a joiner on either side of the quantifier or the sort word, and modifiers between
    openings = [f"A service{j}s owner is ready." for j in JOINERS] + [f"Some{j}service is ready." for j in JOINERS]
    openings += ["A big red service is ready.", "A well-known service is ready.", "Some v2.1 service is ready.",
                 "Every service_owner is ready.", "An (old) service is ready.", "Alice owns a service-account.",
                 "A person's service is ready."]
    for opening in openings:
        doc = document([opening, "It is safe."], [IT_API], names=PY_NAMES, contents=SAFE_U2)
        assert agree(doc, tmp_path) == "UnresolvedReference: m1", opening
    # a declared noun of the sort quantifies it too, joined or not
    for opening in ["A system is deployed.", "A system's owner is ready.", "Some big system is ready."]:
        doc = document([opening, "It is safe."], [IT_API], names=PY_NAMES, contents=SAFE_U2)
        assert agree(doc, tmp_path, noun_env()) == "UnresolvedReference: m1", opening
    # no quantifier of the target's sort: resolved in both (the rule stays scoped by sort)
    for opening in ["Api's owner is ready.", "Alice is a person.", "Every person is ready.", "Api is reviewed."]:
        doc = document([opening, "It is safe."], [IT_API], names=PY_NAMES, contents=SAFE_U2)
        assert agree(doc, tmp_path) == "admitted", opening


def test_coordinations_are_read_as_segments(lean, tmp_path):
    """The same class for the other text input of `Acc` Python elaborates: a coordination whose
    second name is joined (`Bob's`) is a coordination in both; one whose first name is joined
    (`Alice's and`) is none in either."""
    ready = {"u2": unary("ready", "alice")}
    former = [("m1", "u2", "The former", "ordinal_pair", PAIR)]
    for opening in ["Alice and Bob's manager is ready.", "Alice and Bob’s manager is ready.", "Alice and Bob-x is ready."]:
        doc = document([opening, "The former is ready."], former, names=PY_NAMES, contents=ready)
        assert agree(doc, tmp_path) == "admitted", opening
    for opening in ["Alice's and Bob's managers are ready.", "Alice and Bobby are ready."]:
        doc = document([opening, "The former is ready."], former, names=PY_NAMES, contents=ready)
        assert agree(doc, tmp_path) == "UnresolvedReference: m1", opening


def test_mention_surfaces_are_read_by_the_lexer(lean, tmp_path):
    """B (discourse.py:429): `The\\u00a0former` (or two spaces) is the ordinal surface in Lean, whose
    lexer separates words at every `str.isspace` character; Python required one literal space and
    reported `MentionNotSlot`. Python now reads a recorded surface as the lexer's words too. Any
    spacing but one ASCII space is not discourse wording (4.1(4)): rejected alike in both."""
    ready = {"u2": unary("ready", "alice")}
    for space in [" ", "  ", "\t", *UNICODE_SPACES]:
        expected = "admitted" if space == " " else "InvalidInput: discourse wording of u2"
        doc = document(["Alice and Bob are ready.", f"The{space}former is ready."],
                       [("m1", "u2", f"The{space}former", "ordinal_pair", PAIR)], names=PY_NAMES, contents=ready)
        assert agree(doc, tmp_path) == expected, hex(ord(space[-1]))
        doc = document(["Api is reviewed.", f"This{space}service is safe."],
                       [("m1", "u2", f"This{space}service", "demonstrative", entity("api"))], names=PY_NAMES,
                       contents=SAFE_U2)
        assert agree(doc, tmp_path) == expected, hex(ord(space[-1]))
    # a demonstrative before the sort's declared noun is a slot in both (slot discovery reads it)
    doc = document(["Api is reviewed.", "This system is safe."],
                   [("m1", "u2", "This system", "demonstrative", entity("api"))], names=PY_NAMES, contents=SAFE_U2)
    assert agree(doc, tmp_path, noun_env()) == "admitted"
    # a surface that is not the form's words is no slot in either
    for text, form, target in [("The", "ordinal_pair", PAIR), ("This", "demonstrative", entity("api"))]:
        sentence = "The former is ready." if form == "ordinal_pair" else "This service is safe."
        opening = "Alice and Bob are ready." if form == "ordinal_pair" else "Api is reviewed."
        contents = ready if form == "ordinal_pair" else SAFE_U2
        doc = document([opening, sentence], [("m1", "u2", text, form, target)], names=PY_NAMES, contents=contents)
        assert agree(doc, tmp_path).startswith("UnrecordedSlot: u2: ["), text


def test_mention_spans_start_and_end_on_tokens(lean, tmp_path):
    """B (discourse.py:957): Lean maps a mention's byte range to a token range of its unit and
    rejects one that does not start and end on tokens (`InvalidInput: mention m1 span`) before any
    other check of the block; Python reported `UnrecordedSlot`. Every byte range of the unit now
    has the same outcome in both."""
    doc = document(["It is safe."], [("m1", "u1", "It ", "pronoun", entity("api"))], names=PY_NAMES,
                   contents={"u1": unary("safe", "api")})
    assert agree(doc, tmp_path) == "InvalidInput: mention m1 span"
    for sentence in ["It is safe.", "İt is  safe."]:
        base = document(["Api is reviewed.", sentence], [("m1", "u2", sentence[:2], "pronoun", entity("api"))],
                        names=PY_NAMES, contents=SAFE_U2)
        a0, b0 = base["units"][1]["span"]
        docs = []
        for a in range(0, b0 + 2):
            for b in range(a + 1, b0 + 2):
                doc = copy.deepcopy(base)
                doc["discourse"]["mentions"][0]["span"] = [a, b]
                docs.append(doc)
        rows = run([case("admission", doc) for doc in docs])
        aligned = 0
        for doc, row in zip(docs, rows):
            python = python_outcome(doc, tmp_path)
            span = doc["discourse"]["mentions"][0]["span"]
            if isinstance(python, dict):
                assert row.get("status") == "ok" and row["report_id"] == python["report_id"], (sentence, span)
            else:
                assert row.get("error") == python, (sentence, span, row.get("error"), python)
            aligned += python != "InvalidInput: mention m1 span"
        assert 0 < aligned < len(docs) // 4, (sentence, aligned)
    # a mention naming no unit is the same error in both
    doc = document(["It is safe."], [("m1", "u1", "It", "pronoun", entity("api"))], names=PY_NAMES,
                   contents={"u1": unary("safe", "api")})
    doc["discourse"]["mentions"][0]["unit"] = "u9"
    assert agree(doc, tmp_path) == "InvalidInput: mention m1 names an unknown unit"


# The differential property over these classes: generated documents with joined, hyphenated and
# Unicode-spaced binders, coordinations and surfaces, and mention ranges off and on token boundaries.

JOIN_OPENINGS = ["A service{j}s owner is ready.", "Api{j}s owner is ready.", "Some{j}service is ready.",
                 "Alice and Bob{j}s manager is ready.", "Alice{j}s and Bob is ready.", "A big{j}red service is ready.",
                 "Alice and Bob are ready.", "Api is reviewed."]
JOIN_LATER = [
    ("It is safe.", SAFE_U2["u2"], [("It", "pronoun", entity("api")), ("It ", "pronoun", entity("api")),
                                    ("t", "pronoun", entity("api"))]),
    ("The{s}former is ready.", unary("ready", "alice"), [("The{s}former", "ordinal_pair", PAIR),
                                                         ("The{s}", "ordinal_pair", PAIR)]),
    ("This{s}service is safe.", SAFE_U2["u2"], [("This{s}service", "demonstrative", entity("api")),
                                                ("This{s}service is", "demonstrative", entity("api"))]),
]


def join_document(rng):
    j = rng.choice(JOINERS + [" ", " "])
    s = rng.choice([" ", "  ", " ", " ", "\t"])
    opening = rng.choice(JOIN_OPENINGS).format(j=j)
    later, ast, candidates = rng.choice(JOIN_LATER)
    text, form, target = rng.choice(candidates)
    return document([opening, later.format(s=s)], [("m1", "u2", text.format(s=s), form, target)], names=PY_NAMES,
                    contents={"u2": ast} if rng.random() < 0.85 else {})


def test_lean_and_python_agree_on_joined_words_and_spans(lean, tmp_path):
    rng = __import__("random").Random(20260930)
    docs = [join_document(rng) for _ in range(300)]
    rows = run([case("admission", doc) for doc in docs])
    outcomes = set()
    for doc, row in zip(docs, rows):
        python = python_outcome(doc, tmp_path)
        where = (doc["_source"], doc["discourse"]["mentions"])
        if isinstance(python, dict):
            assert row.get("status") == "ok", (where, row.get("error"))
            assert (row["report_id"], row["references"]) == (python["report_id"], python["references"]), where
            outcomes.add("admitted")
        else:
            assert row.get("error") == python, (where, row.get("error"), python)
            outcomes.add(python.split(":")[0] + (": span" if python.endswith(" span") else ""))
    assert {"admitted", "UnresolvedReference", "InvalidInput: span"} <= outcomes, outcomes


# Regressions for the discourse2 loop (manage-agents discourse2-loop.final.md) under the spacing
# directive (discourse-spacing-directive.md): a unit that records a reference has discourse wording
# (4.1(4)), printable ASCII with canonical spacing once the layout around it is removed, or it is
# `InvalidInput: discourse wording of <unit>` in both checkers, before parsing, for pronouns,
# demonstratives and ordinals alike.

WORDING_FORMS = [
    # (opening, later unit with {s} between its words and {p} before its full stop, recorded
    # surface, form, target, content of the later unit)
    ("Api is reviewed.", "It{s}is{s}safe{p}.", "It", "pronoun", entity("api"), SAFE_U2["u2"]),
    ("Api is reviewed.", "This{s}service{s}is{s}safe{p}.", "This{s}service", "demonstrative", entity("api"),
     SAFE_U2["u2"]),
    ("Alice and Bob are ready.", "The{s}former{s}is{s}ready{p}.", "The{s}former", "ordinal_pair", PAIR,
     unary("ready", "alice")),
]


def wording_doc(opening, later, surface, form, target, content, s=" ", p="", sep=" "):
    return document([opening, later.format(s=s, p=p)], [("m1", "u2", surface.format(s=s), form, target)],
                    names=PY_NAMES, contents={"u2": content}, sep=sep)


def test_discourse_wording_is_canonical_ascii(lean, tmp_path):
    """A (discourse.py:527): `It is safe .` with `It` recorded at [0, 2) was CHECKED in Lean and
    `IllTypedTarget: m1: api` in Python, whose expansion parser does not read the space before the
    full stop. Tabs, newlines and Unicode spaces did the same, for demonstratives and ordinals too.
    Both checkers now reject every such unit before parsing, with one code."""
    doc = document(["It is safe ."], [("m1", "u1", "It", "pronoun", entity("api"))], names=PY_NAMES,
                   contents={"u1": unary("safe", "api")})
    assert agree(doc, tmp_path) == "InvalidInput: discourse wording of u1"
    wording = "InvalidInput: discourse wording of u2"
    for row in WORDING_FORMS:
        assert agree(wording_doc(*row), tmp_path) == "admitted", row[1]
        # any space before the full stop, and any spacing but one ASCII space between words
        for p in [" ", "\t", "\n", "\r", "  ", *UNICODE_SPACES]:
            assert agree(wording_doc(*row, p=p), tmp_path) == wording, (row[1], hex(ord(p[0])))
        for s in ["  ", "\t", "\n", "\r", " \t", *UNICODE_SPACES]:
            assert agree(wording_doc(*row, s=s), tmp_path) == wording, (row[1], hex(ord(s[0])))
    # a space before any closing punctuation or after an opening parenthesis, a control or a
    # non-ASCII character anywhere inside the sentence
    safe = {"u1": unary("safe", "api")}
    for sentence in ["It is safe , and it is.", "It is safe ; it is.", "It is safe : yes.", "It is safe !",
                     "It is safe ?", "It is safe (v2 ).", "It is safe ( v2).", "It is\x00safe.", "It is safe\x7f.",
                     "It is safe\x0b.", "It is safé.", "It is safe\u200b.", "It is safe\u2024", "It is “safe”.",
                     "It\u00a0is safe.", "It is safe\u3002"]:
        doc = document([sentence], [("m1", "u1", "It", "pronoun", entity("api"))], names=PY_NAMES, contents=safe)
        assert agree(doc, tmp_path) == "InvalidInput: discourse wording of u1", repr(sentence)
    # the layout around a unit's sentences is not inside one: trailing and leading layout is admitted
    # with the same report in both (Python parses the sentences alone)
    for row in WORDING_FORMS:
        for sep in ["\n", "\n\n", "\t", "\r\n"]:
            assert agree(wording_doc(*row, sep=sep), tmp_path) == "admitted", (row[1], sep)
    for sentence in [" It is safe.", "\n\tIt is safe.", "It is safe. \n"]:
        at = sentence.index("It")
        doc = document([sentence], [("m1", "u1", "It", "pronoun", entity("api"))], names=PY_NAMES, contents=safe)
        assert doc["discourse"]["mentions"][0]["span"] == [at, at + 2]
        assert agree(doc, tmp_path) == "admitted", repr(sentence)
    # the rule is on units that record a reference: a unit without one keeps its own wording (its
    # binder still competes, fixture beta), and the error names the recording unit
    doc = wording_doc("A  service’s owner is ready .", *WORDING_FORMS[0][1:])
    assert agree(doc, tmp_path) == "UnresolvedReference: m1"
    doc = wording_doc("Api  is reviewed .", *WORDING_FORMS[0][1:], p=" ")
    assert agree(doc, tmp_path) == wording


def test_unparseable_recorded_reference_wording(lean, tmp_path):
    """B (discourse.py:562): `İt is safe (v2.1).` with `İt` recorded at [0, 3) was `InvalidInput:
    unit u1 is outside the supported discourse fragment` in Lean and `IllTypedTarget: m1: api` in
    Python. Its non-ASCII letter is not discourse wording: the same code in both, before parsing.
    Every folded character (4.1(6)) in a recorded unit is rejected alike."""
    safe = {"u1": unary("safe", "api")}
    for sentence, surface in [("İt is safe (v2.1).", "İt"), ("ıt is safe.", "ıt"), ("It is ſafe.", "It"),
                              ("It is safe; İt is.", "It"), ("It is \u212aey.", "It")]:
        doc = document([sentence], [("m1", "u1", surface, "pronoun", entity("api"))], names=PY_NAMES, contents=safe)
        assert agree(doc, tmp_path) == "InvalidInput: discourse wording of u1", sentence
    for opening, later, surface, form, target, content in WORDING_FORMS:
        folded = later.replace("i", "ı", 1) if form != "pronoun" else "İt{s}is{s}safe{p}."
        doc = wording_doc(opening, folded, surface.replace("i", "ı", 1) if form != "pronoun" else "İt",
                          form, target, content)
        assert agree(doc, tmp_path) == "InvalidInput: discourse wording of u2", folded
    # the known limitation (docs/spec/discourse.md 8): in discourse wording, a unit outside both
    # grammars is rejected by both, with different codes (Lean: outside the fragment; Python: the
    # recorded expansion does not parse)
    doc = document(["It is safe (v2.1)."], [("m1", "u1", "It", "pronoun", entity("api"))], names=PY_NAMES,
                   contents=safe)
    row, python = admit(doc), python_outcome(doc, tmp_path)
    assert row["error"] == "InvalidInput: unit u1 is outside the supported discourse fragment"
    assert python == "IllTypedTarget: m1: api"


def test_expansions_never_read_a_display(lean, tmp_path):
    """The expansion half of the same class: Python expanded a recorded reference into its target's
    registered display and parsed that, so a display its parser does not read back (`the API`,
    `API`, `Ápi`, a doubled space) made Python `IllTypedTarget` where Lean, which never parses a
    display, was CHECKED. Python now parses the expansion with the parser's own spelling of the
    constant and keeps the display for the reviewed presentation only."""
    safe = {"u1": unary("safe", "api")}
    for display in ["the API", "API", "Ápi", "Api  x", "Api ", "api\u00a0v2", "The  API"]:
        names = [{"constant": "api", "display": display, "scope": "doc"}, *NAMES[1:]]
        doc = document(["It is safe."], [("m1", "u1", "It", "pronoun", entity("api"))], names=names, contents=safe)
        assert agree(doc, tmp_path) == "admitted", display
        assert python_outcome(doc, tmp_path)["reviewed_presentations"]["u1"] == display + " is safe."
    # an ill-typed target is still ill-typed in both, whatever its display
    for display in ["Alice", "the owner"]:
        names = [NAMES[0], {"constant": "alice", "display": display, "scope": "doc"}, NAMES[2]]
        doc = document(["Api is reviewed.", "It is safe."], [("m1", "u2", "It", "pronoun", entity("alice"))],
                       names=names, contents=SAFE_U2)
        assert agree(doc, tmp_path) == "IllTypedTarget: m1: alice", display
    # a constant the parser spells quoted (`web_api`) expands and resolves in both
    environment = env(constants={"web_api": "service", "alice": "person", "bob": "person"})
    names = [{"constant": "web_api", "display": "the web API", "scope": "doc"}, *NAMES[1:]]
    doc = document(["It is safe."], [("m1", "u1", "It", "pronoun", entity("web_api"))], names=names,
                   contents={"u1": unary("safe", "web_api")})
    assert agree(doc, tmp_path, environment) == "admitted"


# The differential property over the class: generated documents whose recorded units carry random
# spacing, punctuation spacing, layout and folded or non-ASCII characters, with random displays.

WORDING_SPACES = [" "] * 8 + ["  ", "\t", "\n", "\u00a0", "\u2003", "\u3000", " \t"]
WORDING_BEFORE = [""] * 8 + [" ", "\t", "\u00a0", "\n"]
WORDING_DISPLAYS = ["Api", "the API", "API", "Ápi", "Api  x"]


def wording_document(rng):
    opening, later, surface, form, target, content = rng.choice(WORDING_FORMS)
    s, p = rng.choice(WORDING_SPACES), rng.choice(WORDING_BEFORE)
    if rng.random() < 0.2:
        later = later.replace("{s}is{s}", "{s}i" + rng.choice(["ſ", "s", "é"]) + "{s}", 1)
    names = [{"constant": "api", "display": rng.choice(WORDING_DISPLAYS), "scope": "doc"}, *NAMES[1:]]
    sep = rng.choice([" ", "\n", "\n\n", "", "\t"])
    lead = rng.choice(["", "", " ", "\n"])
    doc = document([opening, lead + later.format(s=s, p=p)], [("m1", "u2", surface.format(s=s), form, target)],
                   names=names, contents={"u2": content} if rng.random() < 0.85 else {}, sep=sep)
    return doc


def test_lean_and_python_agree_on_discourse_wording(lean, tmp_path):
    rng = __import__("random").Random(20261001)
    docs = [wording_document(rng) for _ in range(400)]
    rows = run([case("admission", doc) for doc in docs])
    outcomes = {}
    for doc, row in zip(docs, rows):
        python = python_outcome(doc, tmp_path)
        where = (doc["_source"], doc["discourse"]["mentions"], doc["discourse"]["names"][0]["display"])
        if isinstance(python, dict):
            assert row.get("status") == "ok", (where, row.get("error"))
            assert (row["report_id"], row["references"]) == (python["report_id"], python["references"]), where
            key = "admitted"
        else:
            assert row.get("error") == python, (where, row.get("error"), python)
            key = python.split(" of ")[0] if "wording" in python else python.split(":")[0]
        outcomes[key] = outcomes.get(key, 0) + 1
    assert outcomes.get("admitted", 0) > 60 and outcomes.get("InvalidInput: discourse wording", 0) > 60, outcomes


# Regressions for the discourse3 loop (manage-agents discourse3-loop.final.md) under the authority
# directive (discourse-authority-directive.md): Python's expansion parser and Lean's lexer and
# grammar kept disagreeing on edge-case wording (quotes, displays, agreement), with Lean admitting
# what Python rejected. The admission is now Lean's by construction: Python's API relays the Lean
# route's verdict, statuses, references and report id, and Python's own check only gives hints and
# the diagnostic text of a document Lean rejects too.

QUOTED_ENV = {"owns": ["person", "service"]}
QUOTED_CONSTANTS = {"web_api": "service", "alice": "person", "bob": "person"}
QUOTED_NAMES = [{"constant": "web_api", "display": '"web_api"', "scope": "doc"},
                {"constant": "alice", "display": "Alice", "scope": "doc"}]
OWNS = ["binary", "owns", ["const", "alice"], ["const", "web_api"]]
FORMER = {"kind": "entity", "name": "alice", "pair": ["alice", "bob"]}


def lean_verdict(doc, tmp_path, environment=None):
    """Lean's and Python's outcomes on one document, which must be the same verdict: `admitted`
    with Lean's report id, references and statuses in Python's result, or both rejecting (with
    Python's diagnostic, which may differ in code only, docs/spec/discourse.md 8). Returns
    (`admitted` or Lean's diagnostic, Python's hints or diagnostic)."""
    row, python = admit(doc, environment), python_outcome(doc, tmp_path, environment)
    if row["status"] == "ok":
        assert isinstance(python, dict), (doc["_source"], python)
        assert (python["report_id"], python["references"]) == (row["report_id"], row["references"])
        loaded = load_document(tmp_path / "doc.ve.md")
        assert {u["id"]: u["status"] for u in loaded["units"]} == row["statuses"]
        return "admitted", python.get("discourse_hints", [])
    assert isinstance(python, str) and not python.startswith("CheckerUnavailable"), (doc["_source"], python)
    return row["error"], python


def test_absent_spaces_beside_quotes_follow_lean(lean, tmp_path):
    """A (discourse.py:359): `She owns"web_api".` with `She` recorded at [0, 3) for `alice` and
    `web_api` displayed `"web_api"` passes discourse wording and is CHECKED in Lean, but Python's
    parser rejected the expansion (`IllTypedTarget: m1: alice`). Demonstratives and ordinals did the
    same. Python now admits it as Lean does; its parser's rejection is a hint."""
    environment = env(QUOTED_ENV, QUOTED_CONSTANTS)
    names_bob = [*QUOTED_NAMES, {"constant": "bob", "display": "Bob", "scope": "doc"}]
    for sentences, surface, form, target, names in [
            (['She owns"web_api".'], "She", "pronoun", entity("alice"), QUOTED_NAMES),
            (['This person owns"web_api".'], "This person", "demonstrative", entity("alice"), QUOTED_NAMES),
            (["Alice and Bob are here.", 'The former owns"web_api".'], "The former", "ordinal_pair", FORMER,
             names_bob)]:
        uid = f"u{len(sentences)}"
        doc = document(sentences, [("m1", uid, surface, form, target)], names=names, contents={uid: OWNS})
        assert lean_verdict(doc, tmp_path, environment) == ("admitted", ["IllTypedTarget: m1: alice"]), sentences
        # with the space, Python's parser agrees and gives no hint
        spaced = document([s.replace('owns"', 'owns "') for s in sentences], [("m1", uid, surface, form, target)],
                          names=names, contents={uid: OWNS})
        assert lean_verdict(spaced, tmp_path, environment) == ("admitted", []), sentences
        # a wrong recorded content is still Lean's rejection, whatever Python's parser reads
        wrong = document(sentences, [("m1", uid, surface, form, target)], names=names,
                         contents={uid: ["binary", "owns", ["const", "bob"], ["const", "web_api"]]})
        assert lean_verdict(wrong, tmp_path, environment)[0] == f"ManifestMismatch: bound.{uid}", sentences


def test_displays_outside_replaced_mentions_follow_lean(lean, tmp_path):
    """A (discourse.py:550): `She owns the API.` with `She` recorded for `alice` and `api`
    registered with display `the API` is CHECKED in Lean (its grammar reads a registered display);
    Python's parser read the unchanged suffix as display text and rejected it. Python now admits it
    as Lean does."""
    environment = env(QUOTED_ENV, {"api": "service", "alice": "person"})
    names = [{"constant": "api", "display": "the API", "scope": "doc"},
             {"constant": "alice", "display": "Alice", "scope": "doc"}]
    content = {"u1": ["binary", "owns", ["const", "alice"], ["const", "api"]]}
    doc = document(["She owns the API."], [("m1", "u1", "She", "pronoun", entity("alice"))], names=names,
                   contents=content)
    assert lean_verdict(doc, tmp_path, environment) == ("admitted", ["IllTypedTarget: m1: alice"])
    for display in ["The API", "the  API", "API", "Api"]:
        other = [{**names[0], "display": display}, names[1]]
        variant = document([f"She owns {display}."], [("m1", "u1", "She", "pronoun", entity("alice"))],
                           names=other, contents=content)
        verdict, _ = lean_verdict(variant, tmp_path, environment)
        assert verdict == "admitted" or verdict.startswith("InvalidInput"), (display, verdict)


def test_agreement_follows_lean(lean, tmp_path):
    """A (discourse.py:552): `It are safe.` with `It` recorded at [0, 2) for `api` is CHECKED in
    Lean (its grammar does not check agreement) and was `IllTypedTarget: m1: api` in Python, as were
    `This service are safe.` and `The former are ready.`. Python now admits them as Lean does."""
    for opening, sentence, surface, form, target, content in [
            ("Api is reviewed.", "It are safe.", "It", "pronoun", entity("api"), unary("safe", "api")),
            ("Api is reviewed.", "This service are safe.", "This service", "demonstrative", entity("api"),
             unary("safe", "api")),
            ("Alice and Bob are ready.", "The former are ready.", "The former", "ordinal_pair", FORMER,
             unary("ready", "alice"))]:
        doc = document([opening, sentence], [("m1", "u2", surface, form, target)], names=PY_NAMES,
                       contents={"u2": content})
        assert lean_verdict(doc, tmp_path) == ("admitted", [f"IllTypedTarget: m1: {target['name']}"]), sentence


def test_python_never_adds_an_admission(lean, tmp_path):
    """The other direction of the class: what Python's parser reads but Lean's discourse fragment
    does not is Lean's rejection, never a Python-only admission. `It is safe (v2.1).` (the recorded
    known limitation) keeps Python's diagnostic, since both reject."""
    doc = document(["It is safe (v2.1)."], [("m1", "u1", "It", "pronoun", entity("api"))], names=PY_NAMES,
                   contents={"u1": unary("safe", "api")})
    assert lean_verdict(doc, tmp_path) == ("InvalidInput: unit u1 is outside the supported discourse fragment",
                                           "IllTypedTarget: m1: api")
    # a predicate verbalisation Python's parser reads (`is active` for `deployed`): Lean's fragment
    # reads predicates by name
    environment = env({"deployed": ["service"]})
    environment["vocabulary"]["predicates"]["deployed"]["verbalisation"] = "{0} is active"
    doc = document(["Api is reviewed.", "It is active."], [("m1", "u2", "It", "pronoun", entity("api"))],
                   names=PY_NAMES, contents={"u2": unary("deployed", "api")})
    assert lean_verdict(doc, tmp_path, environment)[0] == "InvalidInput: unit u2 is outside the supported discourse fragment"
    assert isinstance(python_outcome(doc, tmp_path, environment), str)


def test_graphless_document_is_an_abstention(lean, tmp_path):
    """A `@2` document without a claim graph is loaded but never admitted by Python (document.md),
    and the Lean route's admission needs a graph: Lean abstains (`NotImplemented`), and so does
    Python (`UnsupportedProfile`), never a Python-only CHECKED."""
    doc = document(["Api is reviewed.", "It is safe."], [IT_API], names=PY_NAMES,
                   contents={"u1": unary("reviewed", "api"), **SAFE_U2})
    doc.pop("graph")
    doc.pop("open_terms")
    assert admit(doc)["error"] == "NotImplemented: a document without a claim graph"
    assert python_outcome(doc, tmp_path) == ("UnsupportedProfile: the Lean discourse route abstains "
                                             "(NotImplemented: a document without a claim graph)")


def test_validity_verdicts_are_lean_verdicts(lean, tmp_path):
    """A validity claim, which Python never evaluated (its abstention), is admitted with Lean's
    verdict and status."""
    environment = env(constants=DOC_CONSTANTS)
    for sentence, holds, verdict, status in [("This document is a valid VE document.", True, "checked", "CHECKED"),
                                             ("This document is not a valid VE document.", False, "refuted",
                                              "LABELLED")]:
        doc = validity_doc(sentence, "this_policy", holds)
        assert lean_verdict(doc, tmp_path, environment)[0] == "admitted"
        python = python_outcome(doc, tmp_path, environment)
        assert python["validity"] == {"u1": verdict}
        assert python["coverage"]["bytes_by_status"] == {status: len(sentence)}


# The differential property over the class: generated wording variants (quotes and the spaces
# beside them, spacing, display names, pronouns, demonstratives, ordinals, agreement), each with a
# recorded content that is the elaboration or not. The Python API's verdict is Lean's on every one.

AUTHORITY_TARGETS = [("She", "pronoun", entity("alice")), ("This person", "demonstrative", entity("alice")),
                     ("The former", "ordinal_pair", FORMER), ("It", "pronoun", entity("web_api")),
                     ("This service", "demonstrative", entity("web_api"))]
AUTHORITY_DISPLAYS = ['"web_api"'] * 3 + ["the web API", "Web", "API", "the  API", "Ápi"]
AUTHORITY_SPACES = [" "] * 6 + ["  "]


def authority_document(rng):
    surface, form, target = rng.choice(AUTHORITY_TARGETS)
    display = rng.choice(AUTHORITY_DISPLAYS)
    person = target["name"] == "alice"
    before, after = rng.choice([(" ", "")] * 3 + [("", "")] * 3 + [(" ", " "), ("", " "), ("  ", "")])
    verb = rng.choice(["owns", "own"]) if person else rng.choice(["is", "are"])
    rest = f"{verb}{before}{display}{after}." if person else f"{verb}{rng.choice(AUTHORITY_SPACES)}safe."
    sentence = f"{surface}{rng.choice(AUTHORITY_SPACES)}{rest}"
    opening = "Alice and Bob are here." if form == "ordinal_pair" else rng.choice(["Web is ready.", "Bob is here."])
    right = OWNS if person else unary("safe", "web_api")
    wrong = ["binary", "owns", ["const", "bob"], ["const", "web_api"]] if person else ["top"]
    names = [{"constant": "web_api", "display": display, "scope": "doc"},
             {"constant": "alice", "display": "Alice", "scope": "doc"}]
    if form == "ordinal_pair":
        names.append({"constant": "bob", "display": "Bob", "scope": "doc"})
    return document([opening, sentence], [("m1", "u2", surface, form, target)], names=names,
                    contents={"u2": right if rng.random() < 0.8 else wrong})


def test_python_verdict_is_lean_verdict_on_wording_variants(lean, tmp_path):
    environment = env({"owns": ["person", "service"], "safe": ["service"]}, QUOTED_CONSTANTS)
    rng = __import__("random").Random(20261002)
    docs = [authority_document(rng) for _ in range(300)]
    rows = run([case("admission", doc, environment) for doc in docs])
    outcomes = {"admitted": 0, "admitted over Python's parser": 0, "rejected": 0}
    for doc, row in zip(docs, rows):
        python = python_outcome(doc, tmp_path, environment)
        where = (doc["_source"], doc["discourse"]["names"][0]["display"], row.get("error"), python)
        if row["status"] == "ok":
            assert isinstance(python, dict), where
            assert (python["report_id"], python["references"]) == (row["report_id"], row["references"]), where
            outcomes["admitted over Python's parser" if python.get("discourse_hints") else "admitted"] += 1
        else:
            assert isinstance(python, str) and not python.startswith("CheckerUnavailable"), where
            outcomes["rejected"] += 1
    assert all(n > 20 for n in outcomes.values()), outcomes
