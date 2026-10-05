"""Capture the discourse corpus of the lean-first gate (docs/LEAN-FIRST-PLAN.md 5.1 item 2, batch 4).

No `ve-document@2` file is stored in the repository or on a pilot branch: every discourse document
is written by a test. This module is a pytest plugin that records, for every text `load_document`
sends to the Lean discourse route, the text and the sibling files its imports name, and a writer
that merges the records into one corpus file, deduplicated by content::

    cd BASE; LF4_CAPTURE=/tmp/capture.jsonl PYTHONPATH=BASE:HEAD/docs/lean-first/b4 \\
        HEAD/.venv/bin/python -m pytest -p capture_discourse -n 8 tests/test_discourse*.py ...
    python docs/lean-first/b4/capture_discourse.py write /tmp/capture.jsonl docs/lean-first/discourse-corpus.json

Run the plugin in the base checkout, so the corpus holds the documents the tests wrote before the
batch (the head's tests may write fewer). Each process appends to `$LF4_CAPTURE.<pid>`. `tools/lean_first_diff.py --corpus discourse` reads the
corpus file from the tool's own checkout, writes each document and its files to a scratch
directory, and records `load_document`, `check_document` and `render_document` of it.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import sys
from pathlib import Path


def _record(raw: bytes, directory: Path) -> None:
    from ve.discourse import _import_names, _sibling
    from ve.document import _split
    files = {}
    try:
        meta = _split(raw)[0]
    except Exception:  # noqa: BLE001  (a front matter that does not decode names no file)
        meta = {}
    for name in _import_names(meta) if type(meta) is dict else []:
        try:
            data = _sibling(directory, name)
        except Exception:  # noqa: BLE001
            data = None
        if data is not None:
            files[name] = base64.b64encode(data).decode()
    # one level of imports is what the discourse tests write; deeper chains name files of files
    for data in list(files.values()):
        try:
            child = _split(base64.b64decode(data))[0]
        except Exception:  # noqa: BLE001
            continue
        for name in _import_names(child) if type(child) is dict else []:
            try:
                nested = _sibling(directory, name)
            except Exception:  # noqa: BLE001
                nested = None
            if nested is not None and name not in files:
                files[name] = base64.b64encode(nested).decode()
    line = json.dumps({"document": base64.b64encode(raw).decode(), "files": files}, sort_keys=True)
    # one file per process, so xdist workers never interleave a line
    with open(f"{os.environ['LF4_CAPTURE']}.{os.getpid()}", "a") as out:
        out.write(line + "\n")


def pytest_configure(config):
    import ve.discourse as discourse
    original = discourse.lean_admission

    def recording(raw, directory):
        try:
            _record(raw, Path(directory))
        except Exception as exc:  # noqa: BLE001  (capture never changes a test's outcome)
            print(f"capture failed: {exc}", file=sys.stderr)
        return original(raw, directory)

    discourse.lean_admission = recording


def write(capture: Path, out: Path) -> int:
    seen = {}
    for path in sorted(capture.parent.glob(capture.name + ".*")):
        for line in path.read_text().splitlines():
            row = json.loads(line)
            key = hashlib.sha256(json.dumps(row, sort_keys=True).encode()).hexdigest()
            seen.setdefault(key, row)
    corpus = [{"id": key[:16], **row} for key, row in sorted(seen.items())]
    out.write_text(json.dumps(corpus, indent=0, sort_keys=True) + "\n")
    print(f"{len(corpus)} documents")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[1] != "write":
        raise SystemExit("usage: capture_discourse.py write CAPTURE.jsonl CORPUS.json")
    raise SystemExit(write(Path(sys.argv[2]), Path(sys.argv[3])))
