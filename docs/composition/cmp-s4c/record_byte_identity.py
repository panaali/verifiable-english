"""Record the saved byte-identity comparison of cmp-s4c (docs/spec/discourse.md 14.8: S4-2's share, S4-3, S4-25,
S4-28): each case of `tests/test_discourse_composed_route.py` `identity_cases`, with the compact answer of the
`ve_service` named on the command line (main's, at the merge base the REPORT names), to `byte-identity.json`.

Usage (repo root): uv run python docs/composition/cmp-s4c/record_byte_identity.py <ve_service of main>
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tests.test_discourse_composed_route import EVIDENCE, compact, identity_cases  # noqa: E402
from ve.backends.lean_service import LeanService  # noqa: E402


def main(executable: str) -> None:
    service = LeanService(executable)
    try:
        cases = identity_cases()
        rows = service.run("discourse", [c for _, c in cases])
    finally:
        service.close()
    EVIDENCE.write_text(json.dumps([[name, c, compact(row)] for (name, c), row in zip(cases, rows)], indent=1,
                                   ensure_ascii=False) + "\n")
    print(f"wrote {EVIDENCE.relative_to(ROOT)}: {len(cases)} cases")


if __name__ == "__main__":
    main(sys.argv[1])
