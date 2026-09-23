"""Build the P3 item set from pinned public artefacts.

Each item directory receives the exact source text, its provenance (repository,
commit, path, SHA-256), and a neutral JSON *world*: the finite data (entity store,
cluster objects, requests, Alloy instance) on which both the VE formalisation and
the independent reference evaluator are run. Nothing here reads or writes VE.

Sources are read from local pinned clones (see data/README.md at the repo root)
and from files fetched into /private/tmp/p3src at pinned commits/URLs (see
README.md in this directory). Run once; the committed items/ are the record.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ITEMS = HERE / "items"
DATA = Path("/Users/seyran/code/ve-claude/data")
FETCHED = Path("/private/tmp/p3src")

CEDAR_EX = ("cedar-policy/cedar-examples", "c251f7d1ad171bd12dee5d1d7a1cceaec994518f", "Apache-2.0")
CEDAR_IT = ("cedar-policy/cedar-integration-tests", "1999ea249229e26cabb398a279fea721854a471d", "Apache-2.0")
ALLOY = ("AlloyTools/models", "886447d3369a9036aa4c3b49a82d7c557ab2e5f9", "Apache-2.0")
K8S = ("kubernetes/website", "218c4cee69d6f06f24645b4e7abc37c2f59eb913", "CC-BY-4.0")
AWS = ("docs.aws.amazon.com IAM User Guide", "fetched 2026-09-22", "AWS documentation (example policy excerpt)")


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def write_item(item_id: str, item: dict, sources: dict[str, str]) -> None:
    d = ITEMS / item_id
    d.mkdir(parents=True, exist_ok=True)
    for name, text in sources.items():
        (d / name).write_text(text)
    item["id"] = item_id
    item["source_files"] = {name: sha(text) for name, text in sources.items()}
    (d / "item.json").write_text(json.dumps(item, indent=1, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------- Cedar helpers

def uid_str(v) -> str:
    if isinstance(v, str):
        return v
    if "__entity" in v:
        v = v["__entity"]
    return f'{v["type"]}::{json.dumps(v["id"])}'


def norm_value(v):
    """Normalise Cedar entity-JSON values: entity refs become {"__entity": "T::\"id\""}.

    A dict with exactly the keys type/id is an implicit (schema-typed) entity
    reference in these fixtures; the schema confirms every such occurrence.
    """
    if isinstance(v, dict):
        if set(v) == {"__entity"}:
            return {"__entity": uid_str(v)}
        if set(v) == {"type", "id"}:
            return {"__entity": uid_str(v)}
        if set(v) == {"__extn"}:
            return v
        if set(v) == {"fn", "arg"}:  # schema-typed extension value without the __extn wrapper
            return {"__extn": v}
        return {k: norm_value(x) for k, x in v.items()}
    if isinstance(v, list):
        return [norm_value(x) for x in v]
    return v


def norm_entities(raw: list) -> list:
    out = []
    for e in raw:
        out.append({"uid": uid_str(e["uid"]),
                    "attrs": norm_value(e.get("attrs", {})),
                    "parents": [uid_str(p) for p in e.get("parents", [])]})
    return out


def schema_actions(schema_text: str) -> list:
    """Action entities and their memberOf parents, from a .cedarschema file."""
    namespace = ""
    m = re.search(r"namespace\s+(\w+)\s*\{", schema_text)
    if m:
        namespace = m.group(1) + "::"
    text = re.sub(r"//[^\n]*", "", schema_text)
    acts = []
    for m in re.finditer(r"\baction\s+(.*?)(?=appliesTo|;|\{)", text, re.S):
        body = m.group(1)
        names_part, _, in_part = body.partition(" in ")
        if "\n" in names_part and " in" not in body and "in [" in body:
            names_part, _, in_part = body.partition("in [")
            in_part = "[" + in_part
        names = [n.strip().strip('"') for n in names_part.replace("\n", " ").split(",") if n.strip()]
        parents = []
        in_part = in_part.strip()
        if in_part:
            parents = [p.strip().strip('"') for p in in_part.strip("[] \n").split(",") if p.strip()]
        for n in names:
            acts.append({"uid": f'{namespace}Action::{json.dumps(n)}', "attrs": {},
                         "parents": [f'{namespace}Action::{json.dumps(p)}' for p in parents]})
    return acts


def norm_request(r: dict) -> dict:
    return {"principal": uid_str(r["principal"]), "action": uid_str(r["action"]),
            "resource": uid_str(r["resource"]), "context": norm_value(r.get("context", {}))}


def cedar_integration(item_id: str, scenario: str) -> None:
    root = DATA / "cedar-integration-tests"
    spec = json.loads((root / f"tests/example_use_cases/{scenario}.json").read_text())
    policy_path = spec["policies"]
    policy = (root / policy_path).read_text()
    entities = norm_entities(json.loads((root / spec["entities"]).read_text()))
    schema = (root / spec["schema"]).read_text()
    have = {e["uid"] for e in entities}
    entities += [a for a in schema_actions(schema) if a["uid"] not in have]  # harness loads entities with the schema
    questions = [{"description": r["description"], "request": norm_request(r),
                  "recorded_decision": r["decision"]} for r in spec["requests"]]
    write_item(item_id, {
        "family": "cedar", "synthetic": False,
        "provenance": {"repository": CEDAR_IT[0], "commit": CEDAR_IT[1], "licence": CEDAR_IT[2],
                       "policy_path": policy_path, "entities_path": spec["entities"],
                       "schema_path": spec["schema"], "test_path": f"tests/example_use_cases/{scenario}.json"},
        "question": "Does the Cedar authorizer allow each request under this policy set and entity store?",
        "world": {"entities": entities, "linked": []},
        "questions": questions,
    }, {"source.cedar": policy})


SCHEMA_COERCE = {"cedar-example-use-cases/streaming_service": {"Show": {"releaseDate": "datetime"}}}


def cedar_usecase(item_id: str, rel: str, policy_name="policies.cedar", entities_name="entities.json",
                  schema_name="policies.cedarschema", with_schema=True) -> None:
    root = DATA / "cedar-examples"
    base = root / rel
    policy = (base / policy_name).read_text()
    entities = norm_entities(json.loads((base / entities_name).read_text()))
    # Schema-declared extension types for attributes stored as bare strings
    # (streaming_service schema: Show.releaseDate is a datetime).
    for e in entities:
        for attr, fn in SCHEMA_COERCE.get(rel, {}).get(e["uid"].rsplit("::", 1)[0], {}).items():
            if isinstance(e["attrs"].get(attr), str):
                e["attrs"][attr] = {"__extn": {"fn": fn, "arg": e["attrs"][attr]}}
    if with_schema:
        have = {e["uid"] for e in entities}
        entities += [a for a in schema_actions((base / schema_name).read_text()) if a["uid"] not in have]
    linked = json.loads((base / "linked").read_text()) if (base / "linked").exists() else []
    questions = []
    for decision in ("ALLOW", "DENY"):
        for f in sorted((base / decision).glob("*.json")):
            questions.append({"description": f"{decision}/{f.name}",
                              "request": norm_request(json.loads(f.read_text())),
                              "recorded_decision": decision.lower()})
    sources = {"source.cedar": policy}
    if linked:
        sources["linked.json"] = (base / "linked").read_text()
    write_item(item_id, {
        "family": "cedar", "synthetic": False,
        "provenance": {"repository": CEDAR_EX[0], "commit": CEDAR_EX[1], "licence": CEDAR_EX[2],
                       "policy_path": f"{rel}/{policy_name}", "entities_path": f"{rel}/{entities_name}",
                       "schema_path": f"{rel}/{schema_name}" if with_schema else None,
                       "requests": f"{rel}/ALLOW, {rel}/DENY",
                       "schema_used_for_action_hierarchy": with_schema},
        "question": "Does the Cedar authorizer allow each request under this policy set and entity store?",
        "world": {"entities": entities, "linked": linked},
        "questions": questions,
    }, sources)


def build_cedar() -> None:
    # 3c (principal ==, any action, resource in album) is omitted to keep the set at 40 items;
    # its constructs are covered by 2b and 3a.
    for i, s in enumerate(["1a", "2a", "2b", "2c", "3a", "3b", "3c", "4a", "4d", "4e", "4f", "5b"], 1):
        if s != "3c":
            cedar_integration(f"c{i:02d}_cit_{s}", s)
    uc = "cedar-example-use-cases"
    cedar_usecase("c13_document_cloud", f"{uc}/document_cloud")
    cedar_usecase("c14_github", f"{uc}/github_example")
    cedar_usecase("c15_hotel_static", f"{uc}/hotel_chains/static")
    cedar_usecase("c16_hotel_templated", f"{uc}/hotel_chains/templated")
    cedar_usecase("c17_sales_static", f"{uc}/sales_orgs/static")
    cedar_usecase("c18_sales_templated", f"{uc}/sales_orgs/templated")
    cedar_usecase("c19_streaming", f"{uc}/streaming_service")
    cedar_usecase("c20_tags_n_roles", f"{uc}/tags_n_roles")
    cedar_usecase("c21_tax_preparer", f"{uc}/tax_preparer")
    # language-in-action run.sh authorizes without a schema: no schema action hierarchy.
    cedar_usecase("c22_photoapp", "cedar-policy-language-in-action/PhotoApp", "photoapp.cedar",
                  "photoapp.cedarentities.json", "photoapp.cedarschema", with_schema=False)
    cedar_usecase("c23_gitapp", "cedar-policy-language-in-action/GitApp", "gitapp.cedar",
                  "gitapp.cedarentities.json", "gitapp.cedarschema", with_schema=False)


if __name__ == "__main__":
    which = sys.argv[1:] or ["cedar", "k8s", "aws", "alloy"]
    if "cedar" in which:
        build_cedar()
    if {"k8s", "aws", "alloy"} & set(which):
        import build_items_extra
        build_items_extra.build(which, write_item, sha)
