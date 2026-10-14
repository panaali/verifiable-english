"""Shared inputs for the defeasible phase-1 measurements (docs/research/defeasible-phase1.md section 1).

Pilot runs are read-only; their paths are the ones the plan pins (run 20261012T1800Z of both pilots).
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PILOTS = Path.home() / "code/manage-agents/pilots"
CONSTITUTION = PILOTS / "claude-constitution"
CONSTITUTION_RUN = CONSTITUTION / "run-20261012T1800Z"
UDHR = PILOTS / "udhr"
UDHR_RUN = UDHR / "run-20261012T1800Z"
EVIDENCE = ROOT / "docs/research/evidence/defeasible"

# Research 2.3's screen, as stated there: case-insensitive whole words or phrases.
MARKERS = ("generally", "typically", "usually", "normally", "in most cases", "by default", "absent", "unless",
           "in general", "as a rule", "tend to", "ordinarily", "default", "otherwise")
MARKER_RE = re.compile(r"\b(?:" + "|".join(re.escape(m).replace(r"\ ", r"\s+") for m in MARKERS) + r")\b",
                       re.IGNORECASE)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def units(run: Path):
    data = json.loads((run / "units.json").read_text())
    return data["units"] if isinstance(data, dict) else data


def unit_text(source: bytes, unit) -> str:
    start, end = unit["span"]
    return source[start:end].decode("utf-8")


def unit_bytes(unit) -> int:
    return unit["span"][1] - unit["span"][0]


def front_matter(path: Path):
    text = path.read_text()
    head = text.split("\n---\n", 1)[0]
    return json.loads(head.lstrip("-\n"))


def write_json(name: str, data) -> Path:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    path = EVIDENCE / name
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
    return path
