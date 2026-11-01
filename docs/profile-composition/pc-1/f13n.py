"""F1.3n's saved evidence: every document-mode request of tests/data without `judgments@0`
(`tests/test_judgments_chain.py::plain_documents`) answered by the merge base's service and by PC-1's, compared
byte for byte. Writes f13n.json beside this file.

    uv run python docs/profile-composition/pc-1/f13n.py BASE_SERVICE HEAD_SERVICE
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]

from test_judgments_chain import plain_documents  # noqa: E402
from ve.backends.lean_service import LeanService  # noqa: E402


def answers(executable, cases):
    with LeanService(executable, allow_unlisted_build=True) as service:
        return [json.dumps(row, sort_keys=True) for row in service.run("document", cases)]


def main(base, head):
    named = plain_documents()
    cases = [c for _, c in named]
    before, after = answers(base, cases), answers(head, cases)
    out = {"requests": len(cases), "identical": sum(a == b for a, b in zip(before, after)),
           "differing": [n for (n, _), a, b in zip(named, before, after) if a != b],
           "services": {k: hashlib.sha256(Path(p).read_bytes()).hexdigest() for k, p in (("base", base), ("head", head))},
           "answers_sha256": hashlib.sha256("\n".join(after).encode()).hexdigest()}
    (Path(__file__).parent / "f13n.json").write_text(json.dumps(out, indent=1) + "\n")
    return 0 if not out["differing"] else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
