"""Baseline: the previous run's translation (unchanged content) as a readings@1 document, measured."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import s1doc as S  # noqa: E402

PREV = HERE.parent / "prev-run-20261002T1800Z"
meta, source = S.read(PREV / "translation.ve.md")
meta, env = S.to_s1(meta)
named = [s["unit"] for s in meta["reading_sets"]]
(HERE / "scratch").mkdir(exist_ok=True)
res = S.P.measure("udhr-baseline", meta, source, named, [], HERE / "scratch")
print(json.dumps(res, indent=1, ensure_ascii=False, default=str))
