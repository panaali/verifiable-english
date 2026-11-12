"""sc-admit-cpu, DRI amendment 2026-11-11 (reviews/dri-decisions-20261111-adv1118.md item 2): the answers of the three
keyed corpora and of every soft-default readings document under data/ and usecases/, in one tree, for the main-vs-HEAD
answer list of docs/rd-9/sc-admit-cpu/cpu.md ("Keyed corpora and soft-default documents at the final limit").

  <python> corpora_answers.py corpus <tree> <out-dir> <corpus>   # <out-dir>/<corpus>.results.json: what run.py writes
  <python> corpora_answers.py documents <tree> <out-dir>         # <out-dir>/documents.json: each document's answers
  python3 corpora_answers.py compare <main-dir> <head-dir>       # every changed answer and every ResourceLimit

`corpus` runs `usecases/<corpus>/run.py`'s own `main` with its `RESULTS` path pointed at <out-dir>, so the tree is not
written. `documents` finds each document whose environment lists `readings@1`, `soft-norms@0` and `norm-defaults@0`
(the soft completion, SoftWire.lean `underSoftCompletion`; Lean decides it, this only picks the files to send) and
records its load (admission) and `ve document check` answers. Run with the tree's own Python environment and
`PYTHONPATH=<tree>`, so that `ve` is the tree's; the Lean service is the tree's `lean/.lake/build/bin/ve_service`.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

CORPORA = ("anthropic-rsp", "openai-preparedness", "safety-framework")
REFUSAL = "ResourceLimit: the per-reading checks"
SOFT = {"readings@1", "soft-norms@0", "norm-defaults@0"}
# Beside data/ and usecases/: the one test document on the soft completion that is a readable document file.
EXTRA = ("tests/data/rd9-docroute.ve.md",)


def corpus(tree: Path, out: Path, name: str) -> None:
    sys.path.insert(0, str(tree))
    spec = importlib.util.spec_from_file_location("run", tree / "usecases" / name / "run.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["run"] = module
    spec.loader.exec_module(module)
    module.RESULTS = out / f"{name}.results.json"
    module.main([])


def soft_documents(tree: Path) -> list[str]:
    found = []
    for top in ("data", "usecases"):
        for path in sorted((tree / top).rglob("*")):
            if not path.is_file() or path.suffix not in (".md", ".json", ".txt", ".ve"):
                continue
            head = path.read_bytes()[:200]
            if b'"format": "ve-document@1"' not in head:
                continue
            text = path.read_text()
            for match in re.finditer(r'"profiles"\s*:\s*(\[[^\]]*\])', text):
                try:
                    profiles = set(json.loads(match.group(1)))
                except ValueError:
                    continue
                if SOFT <= profiles and "rights@0" not in profiles:
                    found.append(str(path.relative_to(tree)))
                    break
    return found + list(EXTRA)


LOAD = ("import json, sys; from ve.document import load_document; d = load_document(sys.argv[1]); "
        "s2 = d.get('readings_s2') or {}; print(json.dumps({'admitted': True, 'route': s2.get('route'), "
        "'finding': s2.get('finding'), 'choices': len(s2.get('choices', []))}, sort_keys=True))")


def documents(tree: Path, out: Path) -> None:
    env = {**os.environ, "PYTHONPATH": str(tree)}
    rows = {}
    for doc in soft_documents(tree):
        row = {}
        for step, argv in (("load", ["-c", LOAD, doc]), ("check", ["-m", "ve", "document", "check", doc])):
            proc = subprocess.run([sys.executable, *argv], cwd=tree, env=env, capture_output=True, text=True)
            text = proc.stdout + proc.stderr
            row[step] = {"returncode": proc.returncode, "sha256": hashlib.sha256(proc.stdout.encode()).hexdigest(),
                         "refusals": text.count(REFUSAL), "head": proc.stdout[:400], "error": proc.stderr[-400:]}
        rows[doc] = row
    (out / "documents.json").write_text(json.dumps(rows, indent=1, sort_keys=True) + "\n")


def differences(a, b, path="$"):
    if type(a) is not type(b):
        yield path
    elif isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                yield f"{path}.{k}"
            else:
                yield from differences(a[k], b[k], f"{path}.{k}")
    elif isinstance(a, list):
        if len(a) != len(b):
            yield f"{path}[len {len(a)} != {len(b)}]"
        for i, (x, y) in enumerate(zip(a, b)):
            yield from differences(x, y, f"{path}[{i}]")
    elif a != b:
        yield path


def compare(main: Path, head: Path) -> int:
    changed = 0
    for name in [*(f"{c}.results.json" for c in CORPORA), "documents.json"]:
        texts = [(d / name).read_text() for d in (main, head)]
        diffs = list(differences(*(json.loads(t) for t in texts)))
        changed += len(diffs)
        print(f"{name}: main {REFUSAL!r} x{texts[0].count(REFUSAL)}, HEAD x{texts[1].count(REFUSAL)}; "
              f"{len(diffs)} changed answers{': ' if diffs else ''}{', '.join(diffs[:20])}")
    return 1 if changed else 0


if __name__ == "__main__":
    command, *args = sys.argv[1:]
    if command == "corpus":
        corpus(Path(args[0]).resolve(), Path(args[1]).resolve(), args[2])
    elif command == "documents":
        documents(Path(args[0]).resolve(), Path(args[1]).resolve())
    else:
        sys.exit(compare(Path(args[0]), Path(args[1])))
