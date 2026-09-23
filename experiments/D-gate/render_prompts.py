"""Render the raw-arm prompts for the D gate (no model calls).

    UV_CACHE_DIR=/private/tmp/ve-uv-cache-dgate uv run --project solvers --locked python render_prompts.py

Writes prompts.jsonl: one row per item with the exact user prompt and its SHA-256. The prompt shows
the artefact as a reviewer would see it (policy text, schema and template links for Cedar; the RBAC
YAML for Kubernetes, with experiment filler objects appended), the domain, the assumptions and the
question. It never shows the verifier encoding, the property policy or the answer.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
PROMPT_VERSION = "dgate-raw-v1"

TEMPLATE = """You are reviewing an access-control configuration. Decide whether a universal property holds.

{artefact}

Domain of the question: {domain}

Assumptions: {assumptions}

Question: {question}

Reason as carefully as you need. Then end your reply with exactly one final line, either
ANSWER: YES
or
ANSWER: NO"""


def cedar_artefact(it):
    s = it["shown_to_model"]
    parts = [f"Cedar policies:\n```cedar\n{(HERE / s['policy']).read_text().strip()}\n```",
             f"Cedar schema:\n```cedarschema\n{(HERE / s['schema']).read_text().strip()}\n```"]
    if s.get("template_links"):
        parts.append("Template links (exactly these exist):\n```json\n"
                     + json.dumps(s["template_links"], indent=1) + "\n```")
    return "\n\n".join(parts)


def k8s_artefact(it, arts):
    base = HERE / "artefacts" / it["artefact"]
    src = (base / "source.yaml").read_text().strip()
    edit = it.get("_edit") or {}
    for old, new in edit.get("yaml_replace", []):
        assert src.count(old) == 1, (it["id"], old)
        src = src.replace(old, new)
    world = json.loads((base / "world.json").read_text())
    extra = [o for o in world["objects"] if o.get("synthetic")] + list(edit.get("add_objects", []))
    docs = [src]
    for o in extra:
        o = {k: v for k, v in o.items() if k != "synthetic"}
        o = {"apiVersion": "rbac.authorization.k8s.io/v1", **o}
        docs.append(yaml.safe_dump(o, sort_keys=False).strip())
    return "Kubernetes RBAC objects (these are all the RBAC objects in the cluster):\n```yaml\n" + "\n---\n".join(docs) + "\n```"


def main():
    import importlib.util
    spec = importlib.util.spec_from_file_location("build_items", HERE / "build_items.py")
    b = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(b)
    edits = {k["id"]: k["edit"] for k in b.K}
    items = json.loads((HERE / "items.json").read_text())
    rows = []
    for it in items:
        if it["family"] == "cedar":
            art = cedar_artefact(it)
        else:
            it = dict(it, _edit=edits.get(it["id"]))
            art = k8s_artefact(it, None)
        prompt = TEMPLATE.format(artefact=art, domain=it["domain"], assumptions=it["assumptions"],
                                 question=it["question"])
        rows.append(dict(id=it["id"], artefact=it["artefact"], prompt_version=PROMPT_VERSION,
                         sha256=hashlib.sha256(prompt.encode()).hexdigest(), prompt=prompt))
    with open(HERE / "prompts.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(len(rows), "prompts;", "max chars", max(len(r["prompt"]) for r in rows))


if __name__ == "__main__":
    main()
