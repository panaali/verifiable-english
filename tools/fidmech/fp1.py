"""fp-1, the fingerprint of a case's semantic inputs and of each rule block (item 44/45), ported from manage-agents
tools-local/uc-audit.py fingerprints_of (:1246) and its helpers, so VE needs no file of that bundle.

`fingerprints_of(files)` is `{"_doc": fingerprint of every semantic input, <rule block id>: its own fingerprint}`. A
block's fingerprint covers its block text, the vocabulary entry and legend lines of every predicate it uses, and the
inputs every block shares whole: facts.d1.ve, build_document.py and the translation module. The values equal
uc-audit's (tests/test_fidmech_mutants.py checks them against a copy of the inputs seat's fp1.json values).
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from tools.fidmech.wording import _used as used_predicates


def semantic(name):
    """An audited semantic input of a case (fp-1, item 45)."""
    return (name in ("rules.d1.ve", "facts.d1.ve", "build_document.py", "cases.json", "stage0.py")
            or name.endswith("vocabulary.py") or name.endswith("translation.py")
            or re.fullmatch(r"environment\.d\d+\.json", name) is not None)


def unit_shared(name):
    """The inputs every rule block's fingerprint includes whole: facts and the translation module."""
    return name == "facts.d1.ve" or name == "build_document.py" or name.endswith("translation.py")


def semantic_files_tree(case_dir):
    """{file name: bytes} of a case directory's semantic inputs."""
    d = Path(case_dir)
    return {f.name: f.read_bytes() for f in sorted(d.iterdir()) if f.is_file() and semantic(f.name)} if d.is_dir() else {}


def rule_blocks(text):
    """{block id: (block text incl. header, body text)} of a rules.d1.ve ('## <id> | ...' headers)."""
    lines = text.splitlines()
    heads = [(i, m.group(1)) for i, line in enumerate(lines) for m in [re.match(r"^## (\S+) \|", line)] if m]
    out = {}
    for j, (i, uid) in enumerate(heads):
        e = heads[j + 1][0] if j + 1 < len(heads) else len(lines)
        out[uid] = ("\n".join(lines[i:e]).rstrip(), "\n".join(lines[i + 1:e]))
    return out


def legend_raw(key, vlines):
    """The vocabulary-file lines of a predicate's entry (at most 41)."""
    start = next((i for i, line in enumerate(vlines) if re.match(r'\s*"' + re.escape(key) + r'"\s*:', line)), None)
    if start is None:
        return []
    out, depth, j = [vlines[start]], vlines[start].count("(") - vlines[start].count(")"), start + 1
    while j < len(vlines) and (depth > 0 or vlines[j].lstrip().startswith('"')
                               and not re.match(r'\s*"[a-z0-9_]+"\s*:', vlines[j])):
        out.append(vlines[j])
        depth += vlines[j].count("(") - vlines[j].count(")")
        j += 1
        if len(out) > 40:
            break
    return out


def fp(parts):
    h = hashlib.sha256()
    for k, v in parts:
        h.update(k.encode() + b"\0" + v + b"\0")
    return "fp1:" + h.hexdigest()[:16]


def fingerprints_of(files):
    """fp-1 of a case's semantic files ({name: bytes}): {"_doc": ..., <rule block id>: ...}; {} for no files."""
    if not files:
        return {}
    out = {"_doc": fp(sorted(files.items()))}
    try:
        env = json.loads(files.get("environment.d1.json") or b"{}")
    except ValueError:
        env = {}
    preds = (env.get("vocabulary") or {}).get("predicates") or {}
    vf = sorted(n for n in files if n.endswith("vocabulary.py"))
    vlines = files[vf[0]].decode("utf-8", "replace").splitlines() if vf else []
    shared = [(n, files[n]) for n in sorted(files) if unit_shared(n)]
    for uid, (block, body) in rule_blocks(files.get("rules.d1.ve", b"").decode("utf-8", "replace")).items():
        parts = [("block", block.encode())]
        for key in used_predicates(body, env):
            parts.append(("pred:" + key, json.dumps(preds.get(key), sort_keys=True).encode()))
            parts.append(("legend:" + key, "\n".join(legend_raw(key, vlines)).encode()))
        out[uid] = fp(parts + shared)
    return out
