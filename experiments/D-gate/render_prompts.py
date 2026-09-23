"""Render the raw-arm prompts for the D gate (no model calls).

    UV_CACHE_DIR=/private/tmp/ve-uv-cache-dgate uv run --project solvers --locked python render_prompts.py

Writes prompts.jsonl: one row per item with the exact user prompt and its SHA-256. The prompt shows
the artefact (policy text, schema and template links for Cedar; the RBAC objects for Kubernetes,
with the experiment filler objects), the domain, the assumptions and the question. It never shows the
verifier encoding, the property policy or the answer.

Presentation is normalised uniformly, for every artefact (review finding: comments and formatting
were cues):
* Cedar policies and schemas: every `//` comment is removed (string literals are respected) and
  comment-only lines are dropped; nothing else changes. With CEDAR set, each stripped text is checked
  to parse to the same JSON form as the original (`cedar translate-policy` / `translate-schema`).
* Kubernetes: every object (upstream, filler and planted edit alike) is rendered from the JSON objects
  the verifier checks, by one YAML dumper in the upstream style (flow lists of scalars, double-quoted
  strings where quoting is needed), in a fixed kind order (ClusterRole, Role, ClusterRoleBinding,
  RoleBinding; stable within a kind). YAML comments are therefore gone, and a planted object is not
  distinguishable by style or by being last. The rendered YAML is checked to load back to the objects.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
PROMPT_VERSION = "dgate-raw-v2"

TEMPLATE = """You are reviewing an access-control configuration. Decide whether a universal property holds.

{artefact}

Domain of the question: {domain}

Assumptions: {assumptions}

Question: {question}

Reason as carefully as you need. Then end your reply with exactly one final line, either
ANSWER: YES
or
ANSWER: NO"""


def strip_cedar_comments(text):
    """Remove `//` comments outside string literals; drop lines that held only a comment; strip
    trailing whitespace; collapse runs of blank lines. Cedar has no block comments."""
    out_lines = []
    for line in text.split("\n"):
        buf, i, in_str = [], 0, False
        while i < len(line):
            ch = line[i]
            if in_str:
                buf.append(ch)
                if ch == "\\" and i + 1 < len(line):
                    buf.append(line[i + 1])
                    i += 1
                elif ch == '"':
                    in_str = False
            elif ch == '"':
                in_str = True
                buf.append(ch)
            elif line.startswith("//", i):
                break
            else:
                buf.append(ch)
            i += 1
        kept = "".join(buf).rstrip()
        if kept or not line.strip():  # a line that held only a comment disappears
            out_lines.append(kept)
    text = "\n".join(out_lines)
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    return text.strip()


def _cedar_json(args, text):
    return json.loads(subprocess.run([os.environ["CEDAR"], *args], input=text, capture_output=True,
                                     text=True, check=True).stdout)


def check_cedar_equivalent(kind, original, stripped):
    """With CEDAR set: the stripped text parses to the same JSON as the original."""
    if not os.environ.get("CEDAR"):
        return False
    if kind == "policy":
        args = ["translate-policy", "--direction", "cedar-to-json"]
        assert _cedar_json(args, original) == _cedar_json(args, stripped), "comment stripping changed a policy"
    else:
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d) / "a.cedarschema", Path(d) / "b.cedarschema"
            a.write_text(original)
            b.write_text(stripped)
            args = ["translate-schema", "--direction", "cedar-to-json", "-s"]
            assert _cedar_json(args + [str(a)], "") == _cedar_json(args + [str(b)], ""), "comment stripping changed a schema"
    return True


CHECKED = []


def cedar_text(path, kind):
    original = (HERE / path).read_text()
    stripped = strip_cedar_comments(original)
    CHECKED.append(check_cedar_equivalent(kind, original, stripped))
    return stripped


def cedar_artefact(it):
    s = it["shown_to_model"]
    parts = [f"Cedar policies:\n```cedar\n{cedar_text(s['policy'], 'policy')}\n```",
             f"Cedar schema:\n```cedarschema\n{cedar_text(s['schema'], 'schema')}\n```"]
    if s.get("template_links"):
        parts.append("Template links (exactly these exist):\n```json\n"
                     + json.dumps(s["template_links"], indent=1) + "\n```")
    return "\n\n".join(parts)


KIND_ORDER = ("ClusterRole", "Role", "ClusterRoleBinding", "RoleBinding")


class _Dumper(yaml.SafeDumper):
    pass


def _str(dumper, value):
    try:
        plain_ok = value != "" and yaml.safe_load(value) == value and value.strip() == value
    except yaml.YAMLError:
        plain_ok = False
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style=None if plain_ok else '"')


def _list(dumper, value):
    if value and all(isinstance(v, str) for v in value):  # upstream style: ["get", "list"]
        return yaml.SequenceNode("tag:yaml.org,2002:seq",
                                 [dumper.represent_scalar("tag:yaml.org,2002:str", v, style='"') for v in value],
                                 flow_style=True)
    return dumper.represent_sequence("tag:yaml.org,2002:seq", value, flow_style=False)


_Dumper.add_representer(str, _str)
_Dumper.add_representer(list, _list)


def k8s_objects(it):
    """The objects the verifier checks (world.json or the edit's world), synthetic flags removed,
    apiVersion first, in the fixed kind order."""
    objs = json.loads((HERE / it["verifier"]["policies"]).read_text())["objects"]
    out = []
    for o in objs:
        o = {k: v for k, v in o.items() if k != "synthetic"}
        o = {"apiVersion": "rbac.authorization.k8s.io/v1", "kind": o["kind"],
             **{k: v for k, v in o.items() if k not in ("apiVersion", "kind")}}
        out.append(o)
    return sorted(out, key=lambda o: KIND_ORDER.index(o["kind"]))


def k8s_artefact(it):
    objs = k8s_objects(it)
    docs = [yaml.dump(o, Dumper=_Dumper, sort_keys=False, default_flow_style=False, width=120).strip() for o in objs]
    text = "\n---\n".join(docs)
    assert list(yaml.safe_load_all(text)) == objs, it["id"]
    return "Kubernetes RBAC objects (these are all the RBAC objects in the cluster):\n```yaml\n" + text + "\n```"


def main():
    items = json.loads((HERE / "items.json").read_text())
    rows = []
    for it in items:
        art = cedar_artefact(it) if it["family"] == "cedar" else k8s_artefact(it)
        prompt = TEMPLATE.format(artefact=art, domain=it["domain"], assumptions=it["assumptions"],
                                 question=it["question"])
        rows.append(dict(id=it["id"], artefact=it["artefact"], prompt_version=PROMPT_VERSION,
                         sha256=hashlib.sha256(prompt.encode()).hexdigest(), prompt=prompt))
    with open(HERE / "prompts.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(len(rows), "prompts;", "max chars", max(len(r["prompt"]) for r in rows),
          f"; Cedar texts checked equivalent after comment stripping: {sum(CHECKED)}/{len(CHECKED)}")


if __name__ == "__main__":
    main()
