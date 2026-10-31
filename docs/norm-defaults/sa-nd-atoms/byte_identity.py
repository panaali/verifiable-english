"""sa-nd-atoms evidence: the norm-defaults route cases answer byte-identically before and after.

Runs every `norm-defaults` case of `tests/data/route-cases.jsonl` through two `ve_service`
executables (the merge base's and this branch's) and saves, per case, the SHA-256 of each answer
as the service decoded it (`json.dumps`, key order kept, compact). The saved file is the evidence;
nothing reads git.

    uv run python docs/norm-defaults/sa-nd-atoms/byte_identity.py BASE_SERVICE BRANCH_SERVICE BASE_REV BRANCH_REV
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from tests.lean_service_corpus import recorded  # noqa: E402
from ve.backends.lean_service import LeanService  # noqa: E402

OUT = Path(__file__).with_name("byte-identity.json")


def digests(executable: str, cases: list) -> list[str]:
    with LeanService(executable) as service:
        rows = service.run("norm-defaults", cases)
    return [hashlib.sha256(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
            for row in rows]


def main(base: str, branch: str, base_rev: str, branch_rev: str) -> int:
    cases = recorded("norm-defaults")
    before, after = digests(base, cases), digests(branch, cases)
    rows = [{"id": case.get("id"), "base": b, "branch": a} for case, b, a in zip(cases, before, after)]
    same = sum(row["base"] == row["branch"] for row in rows)
    OUT.write_text(json.dumps({"mode": "norm-defaults", "base": base_rev, "branch": branch_rev, "cases": len(rows),
                               "identical": same, "rows": rows}, indent=1) + "\n")
    print(f"{same} of {len(rows)} answers identical")
    return 0 if cases and same == len(rows) == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:5]))
