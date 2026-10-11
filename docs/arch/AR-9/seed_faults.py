"""Plant each AR-9 split fault, prove its named tests fail, then restore the source.

    VE_NATIVE_PREBUILT=1 uv run python docs/arch/AR-9/seed_faults.py > docs/arch/AR-9/evidence/mutants.json

One fault per claim of the split (names still importable, moved code reaches the facade's
names only through the seams, one owner per member), each with the new test that pins the
claim and, where one exists, an older test of the behaviour the fault breaks.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools import nested_pytest  # noqa: E402  (the one builder of a nested pytest command)
SPLIT = "tests/test_assist_split.py::"
CASES = [
    ("recovery stops re-exporting nearest_wordings", "names",
     [("ve/assist/recovery.py", "GlossaryAdapter, ProposerAdapter, _Commands, nearest_wordings)",
       "GlossaryAdapter, ProposerAdapter, _Commands)")],
     [SPLIT + "test_every_name_the_module_defined_is_still_importable_from_it[ve.assist.recovery-nearest_wordings]",
      "tests/test_assist_recovery.py::test_ledger_json_restore_and_revision_guard"]),
    ("session stops re-exporting config_digest", "names",
     [("ve/assist/session.py", "_symbols_of, config_digest)", "_symbols_of)")],
     [SPLIT + "test_every_name_the_module_defined_is_still_importable_from_it[ve.assist.session-config_digest]",
      "tests/test_assist.py::test_astra6_deleted_propose_event_detected_after_metadata_edit"]),
    ("replay calls its own evaluate, bypassing the seam", "seams",
     [("ve/assist/recovery_replay.py", "from ..errors import VEError\n",
       "from ..errors import VEError\nfrom ..evaluate import evaluate\n"),
      ("ve/assist/recovery_replay.py", "        checked = self._evaluate(self.env, formula, model, trace=False)",
       "        checked = evaluate(self.env, formula, model, trace=False)")],
     [SPLIT + "test_moved_code_does_not_bind_the_names_the_facade_owns[ve.assist.recovery_replay]",
      "tests/test_assist_deadline.py::test_situation_evaluation_is_inside_approval_deadline[evaluate]"]),
    ("the deadline seam binds the value at import", "seams",
     [("ve/assist/recovery.py", "    @staticmethod\n    def _operation_seconds():\n        return OPERATION_SECONDS\n",
       "    _operation_seconds = staticmethod(lambda seconds=OPERATION_SECONDS: seconds)\n")],
     [SPLIT + "test_each_recovery_seam_reads_the_facade_name_when_called[OPERATION_SECONDS-_operation_seconds]"]),
    ("the facade shadows a journal method", "one owner",
     [("ve/assist/recovery.py", "    # -- seams ---",
       "    def _expect(self, expected_revision):\n        return None\n\n    # -- seams ---")],
     [SPLIT + "test_every_member_has_one_owner[RecoveryService]",
      "tests/test_assist_recovery.py::test_ledger_json_restore_and_revision_guard"]),
]


def run(test: str) -> dict:
    done = subprocess.run(nested_pytest.command(["-q", "-x", "-p", "no:cacheprovider", test]), cwd=ROOT,
                          env=nested_pytest.environment(os.environ, VE_NATIVE_PREBUILT="1"),
                          capture_output=True, text=True)
    return {"test": test, "exit_code": done.returncode, "failure_excerpt": done.stdout[-1500:]}


def main() -> int:
    records = []
    for bug, claim, edits, tests in CASES:
        originals = {path: (ROOT / path).read_text() for path, _, _ in edits}
        try:
            for path, before, after in edits:
                text = (ROOT / path).read_text()
                if text.count(before) != 1:
                    raise RuntimeError(f"expected one mutation site for {bug} in {path}")
                (ROOT / path).write_text(text.replace(before, after, 1))
            records.append({"bug": bug, "claim": claim, "files": sorted(originals),
                            "runs": [run(test) for test in tests]})
        finally:
            for path, text in originals.items():
                (ROOT / path).write_text(text)
    restored = [run(test) for _, _, _, tests in CASES for test in tests]
    print(json.dumps({"mutants": records, "restored": [{"test": r["test"], "exit_code": r["exit_code"]}
                                                      for r in restored]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
