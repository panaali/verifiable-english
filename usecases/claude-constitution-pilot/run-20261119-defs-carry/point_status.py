#!/usr/bin/env python3
"""`measure.py --only point-status-c9` of run-20261104T0716Z on this run's probe: its after and strict steps only.

    uv run python usecases/claude-constitution-pilot/run-20261119-defs-carry/point_status.py

The old run's `measure.py` runs unchanged. Its answers and `measurements.json` are written to this run's `answers/`.
"""
from __future__ import annotations

import json

import carry_definitions
import measure  # the old run's (carry_definitions puts it on the path); it reads `migrate_soft.PROBE`

if __name__ == "__main__":
    carry_definitions.here()
    measure.ANSWERS = carry_definitions.RUN / "answers"
    record = measure.ANSWERS / "measurements.json"
    if not record.exists():
        record.write_text(json.dumps({"steps": []}) + "\n")
    measure.main(("point-status-c9",))
