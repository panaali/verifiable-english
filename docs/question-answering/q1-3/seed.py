"""Plant each seeded bug of `mutants.json` alone, run the test it names, restore the file, and save the outcome.

    uv run python docs/question-answering/q1-3/seed.py

Run it on a clean tree with nothing else reading it: the planted bug is in the checkout while its test runs.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import nested_pytest  # noqa: E402

SAVED = Path(__file__).with_name("mutants.json")


def main() -> int:
    saved = json.loads(SAVED.read_text())
    env = nested_pytest.environment(os.environ, VE_NATIVE_PREBUILT="1")
    for mutant in saved["mutants"]:
        path, old, new = ROOT / mutant["file"], mutant["mutation"]["from"], mutant["mutation"]["to"]
        original = path.read_text()
        assert original.count(old) == 1, (mutant["behaviour"], original.count(old))
        try:
            path.write_text(original.replace(old, new))
            run = subprocess.run(nested_pytest.command(["-q", "-x", "-p", "no:cacheprovider", mutant["test"]]),
                                 cwd=ROOT, env=env, capture_output=True, text=True)
        finally:
            path.write_text(original)
        mutant["killed"] = nested_pytest.failed_test_run(run)
        mutant["result"] = [line for line in run.stdout.splitlines() if line.strip()][-1]
        print(mutant["killed"], mutant["behaviour"], "|", mutant["result"], flush=True)
    SAVED.write_text(json.dumps(saved, indent=1) + "\n")
    return 0 if all(m["killed"] for m in saved["mutants"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
