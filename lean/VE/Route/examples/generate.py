"""Generate the Lean `route` subcommand's shipped cases (P0-Lean seed cases).

Usage (repo root): uv run python lean/VE/Route/examples/generate.py
Writes lean/VE/Route/examples/route-cases.json. Each case carries the Lean
verdict it is expected to produce under "expected" (Lean ignores the field).

Certificates come from the unchanged Python tableau prover, run on a v0 copy of
the environment in which the built-in `$string` sort is renamed to an ordinary
sort; the trace is independent of that name. The binding (environment id and
meaning ids) is recomputed with the `ve.core@0.2` identity domains, and the
checked premise list is Background (literal distinctness, sorted pairs) then
the case's premises, as the Lean route regenerates it.
"""
from __future__ import annotations

import copy
import itertools
import json
from pathlib import Path

from ve import Environment
from ve.ast import formula_from_data
from ve.entailment import prove_entailment
from ve.wire import digest

OUT = Path(__file__).with_name("route-cases.json")
LANGUAGE = "ve.core@0.2"
REVISION = "ve-v0.2-expand2-2026-09-25"
STRING = "$string"


def envelope(vocabulary, profiles=("relational-fol@0",)):
    return {"language": LANGUAGE, "profiles": list(profiles), "spec_revision": REVISION,
            "vocabulary": vocabulary}


VOCAB = {
    "sorts": {"person": {"description": "a person"}},
    "predicates": {"dept": {"arguments": ["person", STRING], "description": "the department of a person"},
                   "senior": {"arguments": ["person"], "description": "is senior"}},
    "constants": {"alice": {"sort": "person", "description": "Alice"},
                  "bob": {"sort": "person", "description": "Bob"},
                  "finance": {"sort": STRING, "description": "the string finance"},
                  "legal": {"sort": STRING, "description": "the string legal"}},
}
EMPTY = {"sorts": {}, "predicates": {}, "constants": {}}


def literals(vocabulary):
    return sorted(c for c, d in vocabulary["constants"].items() if d["sort"] == STRING)


def background(vocabulary):
    lits = literals(vocabulary)
    return [["not", ["eq", ["const", a], ["const", b]]] for a, b in itertools.combinations(lits, 2)]


def v0_env(vocabulary):
    text = json.dumps(vocabulary).replace(json.dumps(STRING), json.dumps("zstring"))
    vocab = json.loads(text)
    if any(d["sort"] == "zstring" for d in vocab["constants"].values()) or any(
            "zstring" in d["arguments"] for d in vocab["predicates"].values()):
        vocab["sorts"]["zstring"] = {"description": "strings (proof copy)"}
    return Environment.from_dict({"language": "ve.core@0", "profile": "relational-fol@0",
                                  "spec_revision": "ve-v0-draft-2026-09-20", "vocabulary": vocab})


def identity(profiles):
    return "v0.2:" + ",".join(profiles)


def environment_id(env_json):
    return digest(f"ve-environment-{identity(env_json['profiles'])}\n", env_json)


def meaning_id(env_json, ast):
    return digest(f"ve-meaning-{identity(env_json['profiles'])}\n",
                  {"environment_id": environment_id(env_json), "ast": ast})


def certificate(env_json, premises, conclusion):
    env = v0_env(env_json["vocabulary"])
    result = prove_entailment(env, [formula_from_data(env, p) for p in premises],
                              formula_from_data(env, conclusion))
    assert result.certificate is not None, (premises, conclusion, result)
    return {"checker_version": result.certificate["checker_version"],
            "environment_id": environment_id(env_json),
            "premise_meaning_ids": [meaning_id(env_json, p) for p in premises],
            "conclusion_meaning_id": meaning_id(env_json, conclusion),
            "trace": result.certificate["trace"]}


MODEL = {"complete": True, "domains": {"person": ["a", "b"], STRING: ["f", "l"]},
         "constants": {"alice": "a", "bob": "b", "finance": "f", "legal": "l"},
         "relations": {"dept": [["a", "f"]], "senior": [["a"]]}}
ALIAS = copy.deepcopy(MODEL)
ALIAS["constants"]["legal"] = "f"

DEPT_AF = ["binary", "dept", ["const", "alice"], ["const", "finance"]]
DEPT_AL = ["binary", "dept", ["const", "alice"], ["const", "legal"]]
SAME = ["eq", ["const", "finance"], ["const", "legal"]]
SENIOR_A = ["unary", "senior", ["const", "alice"]]


def cases():
    env = envelope(VOCAB)
    out = []

    def case(id_, expected, **fields):
        out.append({"id": id_, "environment": fields.pop("environment", env), **fields, "expected": expected})

    # Evaluation and model validity (invalid-background-model: aliasing literals).
    case("eval-literals", {"status": "ok", "values": [True, False]}, model=MODEL, ast=[DEPT_AF, SAME])
    case("eval-alias-invalid", {"status": "error", "generator": "literals"}, model=ALIAS, ast=[["top"]])
    case("countermodel-refutes", {"status": "ok", "refutes": True}, kind="countermodel", model=MODEL,
         premises=[DEPT_AF], conclusion=DEPT_AL)
    case("countermodel-alias-invalid", {"status": "error", "generator": "literals"}, kind="countermodel",
         model=ALIAS, premises=[DEPT_AF], conclusion=DEPT_AL)
    case("string-quantifier-rejected", {"status": "error"}, model=MODEL, ast=[["forall", STRING, ["top"]]])

    # Certificates: the checked list is Background ++ premises.
    gamma = [["or", SAME, DEPT_AF]]
    checked = background(VOCAB) + gamma
    cert = certificate(env, checked, DEPT_AF)
    case("certificate-uses-background", {"status": "ok", "valid": True, "background": 1}, kind="certificate",
         premises=gamma, conclusion=DEPT_AF, certificate=cert)
    unbound = dict(cert, premise_meaning_ids=[meaning_id(env, p) for p in gamma])
    case("certificate-without-background-binding", {"status": "error"}, kind="certificate",
         premises=gamma, conclusion=DEPT_AF, certificate=unbound)
    case("certificate-stale-environment", {"status": "error"}, kind="certificate",
         premises=gamma, conclusion=DEPT_AF, certificate=dict(cert, environment_id="0" * 64))

    # Envelopes (UnsupportedProfile names the profile or the pair).
    for id_, profiles in [("profile-unknown", ["relational-fol@0", "zzz@0"]),
                          ("profile-unsorted", ["relational-fol@0", "closure@0"]),
                          ("profile-duplicate", ["relational-fol@0", "relational-fol@0"]),
                          ("profile-missing-base", ["definitions@0"]),
                          ("profile-closure-order", ["closure@0", "order@0", "relational-fol@0"]),
                          ("profile-nary-order", ["nary@0", "order@0", "relational-fol@0"]),
                          ("profile-nary-without-closure", ["nary@0", "relational-fol@0"]),
                          ("profile-closure-nary-gated", ["closure@0", "nary@0", "relational-fol@0"])]:
        case(id_, {"status": "error"}, environment=envelope(EMPTY, profiles), ast=[["top"]],
             model={"complete": True, "domains": {}, "constants": {}, "relations": {}})
    for id_, profiles in [("family-fol", ["definitions@0", "documents@1", "relational-fol@0"]),
                          ("family-closure", ["closure@0", "relational-fol@0"]),
                          ("family-order", ["order@0", "relational-fol@0"])]:
        case(id_, {"status": "ok", "values": [True]}, environment=envelope(EMPTY, profiles), ast=[["top"]],
             model={"complete": True, "domains": {}, "constants": {}, "relations": {}})
    case("revision-unsupported", {"status": "error"},
         environment=dict(envelope(EMPTY), spec_revision="ve-v0.2-other"), ast=[["top"]],
         model={"complete": True, "domains": {}, "constants": {}, "relations": {}})

    # One dependency DAG (definitions above and below norms; cycles rejected).
    graph_env = envelope(EMPTY, ["definitions@0", "norms@0", "relational-fol@0"])
    case("dag-definition-above-norm", {"status": "ok", "order": ["safe", "required", "violation"]},
         environment=graph_env, kind="dependency-order",
         nodes=[{"name": "violation", "mentions": ["required", "done"]},
                {"name": "required", "mentions": ["safe"]},
                {"name": "safe", "mentions": ["base"]}])
    case("dag-cycle-definition-norm", {"status": "error", "error": "DependencyCycle: a, b, c"},
         environment=graph_env, kind="dependency-order",
         nodes=[{"name": "a", "mentions": ["b"]}, {"name": "b", "mentions": ["a"]},
                {"name": "c", "mentions": ["a"]}, {"name": "d", "mentions": []}])
    case("dag-self-loop", {"status": "error", "error": "DependencyCycle: p"},
         environment=graph_env, kind="dependency-order", nodes=[{"name": "p", "mentions": ["p"]}])

    # Admission: labels, bridge leaves, background leaves, nested kinds.
    units = [{"id": "u1", "span": [0, 20], "kind": "asserted", "content": SENIOR_A},
             {"id": "u2", "span": [21, 60], "kind": ["attributed", "bob", "says", "asserted"],
              "content": ["or", SAME, DEPT_AF]},
             {"id": "u3", "span": [61, 120],
              "kind": ["attributed", "alice", "believes",
                       ["hedged", "likely", ["causal", "because", "asserted", "asserted"]]]}]
    bg = background(VOCAB)[0]
    premises = [["or", SAME, DEPT_AF], bg]
    edge = certificate(env, premises, DEPT_AF)
    nodes = [{"name": "claim-u2", "ast": ["or", SAME, DEPT_AF], "label": "bridge:accepts(bob,u2)", "unit": "u2"},
             {"name": "distinct", "ast": bg, "label": "background:literals"},
             {"name": "senior", "ast": SENIOR_A, "unit": "u1"},
             {"name": "root", "ast": DEPT_AF, "premises": ["claim-u2", "distinct"], "certificate": edge}]
    document = {"units": units, "graph": {"root": "root", "nodes": nodes}}
    case("admit-bridge-background", {"status": "ok", "admitted": True}, kind="admission", document=document)

    def mutate(id_, expected, change):
        doc = copy.deepcopy(document)
        change(doc)
        case(id_, expected, kind="admission", document=doc)

    def strip_bridge(doc):
        del doc["graph"]["nodes"][0]["label"]
    mutate("admit-quoted-without-bridge",
           {"status": "error", "error": "AdmissionError: quoted content of unit u2 is used without a bridge leaf"},
           strip_bridge)

    def strip_background(doc):
        del doc["graph"]["nodes"][1]["label"]
    mutate("admit-background-label-stripped", {"status": "error"}, strip_background)

    def wrong_agent(doc):
        doc["graph"]["nodes"][0]["label"] = "bridge:accepts(alice,u2)"
    mutate("admit-bridge-wrong-agent", {"status": "error"}, wrong_agent)

    def explicit_default(doc):
        doc["graph"]["nodes"][2]["label"] = "asserted"
    mutate("admit-explicit-default-label", {"status": "error"}, explicit_default)

    def overlapping(doc):
        doc["units"][1]["span"] = [10, 60]
    mutate("admit-overlapping-spans", {"status": "error"}, overlapping)

    # Citation and reading choices.
    cited = copy.deepcopy(document)
    cited["lemmas"] = [{"name": "b1/t1", "conclusion": DEPT_AF,
                        "leaves": [{"ast": ["or", SAME, DEPT_AF], "label": "bridge:accepts(bob,u2)"}]}]
    # The citing report carries the lemma's leaves: they are premises of the citing step.
    via = certificate(env, [DEPT_AF, ["or", SAME, DEPT_AF]], DEPT_AF)
    cited["graph"] = {"root": "uses", "nodes": [
        nodes[0], {"name": "cited", "ast": DEPT_AF, "label": "cite:b1/t1"},
        {"name": "uses", "ast": DEPT_AF, "premises": ["cited", "claim-u2"], "certificate": via}]}
    case("admit-citation-with-leaves", {"status": "ok", "admitted": True}, kind="admission", document=cited)
    missing = copy.deepcopy(cited)
    missing["graph"] = {"root": "cited", "nodes": [missing["graph"]["nodes"][1]]}
    case("admit-citation-missing-leaf", {"status": "error"}, kind="admission", document=missing)

    readings = copy.deepcopy(document)
    readings["reading_sets"] = [{"id": "s1", "version": 1, "readings": [DEPT_AF, DEPT_AL]}]
    both = certificate(env, [DEPT_AF, DEPT_AL], DEPT_AF)
    readings["graph"] = {"root": "r", "nodes": [
        {"name": "r0", "ast": DEPT_AF, "label": "readings:s1@1:0"},
        {"name": "r1", "ast": DEPT_AL, "label": "readings:s1@1:1"},
        {"name": "r", "ast": DEPT_AF, "premises": ["r0", "r1"], "certificate": both}]}
    case("admit-incompatible-choices", {"status": "error", "error": "AdmissionError: incompatible reading choices"},
         kind="admission", document=readings)
    one = copy.deepcopy(readings)
    one_cert = certificate(env, [DEPT_AF], DEPT_AF)
    one["graph"] = {"root": "r", "nodes": [
        {"name": "r0", "ast": DEPT_AF, "label": "readings:s1@1:0"},
        {"name": "r", "ast": DEPT_AF, "premises": ["r0"], "certificate": one_cert}]}
    case("admit-one-choice", {"status": "ok", "admitted": True}, kind="admission", document=one)
    return out


def main():
    OUT.write_text(json.dumps(cases(), indent=1, ensure_ascii=False) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
