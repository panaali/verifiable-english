"""Plant each seeded bug of this batch's `mutants.json` alone, run the test it names, restore the file, and save the
outcome: q1-3's `seed.py` loop, pointed at this file's `mutants.json`.

    uv run python docs/question-answering/q1-3b/seed.py
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("q1_3_seed", Path(__file__).parents[1] / "q1-3/seed.py")
seed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(seed)
seed.SAVED = Path(__file__).with_name("mutants.json")

if __name__ == "__main__":
    raise SystemExit(seed.main())
