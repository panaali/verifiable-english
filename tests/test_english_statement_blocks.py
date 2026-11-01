"""The 120 pinned rule blocks and Python's recorded node for each (en-e3-norm EN-0; spec english-lean-s6 f22).

`tests/data/norm-blocks/rsp.jsonl` (76) and `fsf.jsonl` (44) hold each block's id and text, the commit it was read
at and Python's `norm` object (`docs/english-lean/en-s6/capture_blocks.py`). Every block is present, still the
text of its use case's `rules.d1.ve`, and its node's W1 fields decode with Lean's one decoder,
`VE.Norms.Wire.decodeNorm`. Lean reads none of the blocks yet: en-s6 adds the values and their assembly, and
the node path and the reader are en-s6b (DRI decision reviews/dri-decisions-20261101-en-s6.md). Each block is listed with
that reason, and the baseline is 0 of 120; en-s6b replaces it by the comparison of Lean's node with Python's.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import subprocess

import pytest

from tests.lean_build import lean_build
from tests.subprocesses import HANG_TIMEOUT

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "tests/data/norm-blocks"
CASES = {"rsp": ("anthropic-rsp", 76), "fsf": ("safety-framework", 44)}
W1 = {"name", "predicate", "sign", "guard", "unless", "over"}
SOFT = W1 | {"mode", "exception"}
READER = ROOT / "lean/VE/EnglishGrammar/Norm/Read.lean"
NOT_READ = "en-s6b: Lean has no reader of block texts yet (Norm/Read.lean)"


def blocks(name: str) -> list[dict]:
    return [json.loads(line) for line in (DATA / f"{name}.jsonl").read_text().splitlines()]


def source_blocks(case: str) -> list[tuple[str, str]]:
    lines = (ROOT / "usecases" / case / "rules.d1.ve").read_text().splitlines()
    return [(re.match(r"## ([a-z0-9-]+) \|", h)[1], t) for h, t in zip(lines[::2], lines[1::2])]


def lean_reading(row: dict) -> tuple[str, dict | None]:
    """Lean's node for a block, or the reason it has none."""
    return NOT_READ, None


@pytest.mark.parametrize("name", CASES)
def test_every_pinned_block_has_its_python_node(name):
    case, count = CASES[name]
    rows = blocks(name)
    assert len(rows) == count
    assert [(r["id"], r["text"]) for r in rows] == source_blocks(case)
    assert len({r["commit"] for r in rows}) == 1
    for r in rows:
        assert set(r) == {"commit", "id", "text", "node"}, r["id"]
        [node] = r["node"]
        soft = " should " in r["text"]
        assert set(node) == (SOFT if soft else W1), r["id"]
        assert node["name"] == "rule-1" and node["over"] == [] and type(node["sign"]) is bool, r["id"]
        assert node.get("mode", "strict") == ("default" if soft else "strict"), r["id"]


def test_pinned_counts_and_baseline():
    rows = [r for name in CASES for r in blocks(name)]
    assert len(rows) == 120
    assert sum(" should " in r["text"] for r in rows) == 17
    readings = [lean_reading(r) for r in rows]
    assert [why for why, _ in readings] == [NOT_READ] * 120
    assert not READER.exists(), "the reader has landed: compare Lean's node with Python's here (en-s6b)"


@pytest.fixture(scope="module")
def lake():
    found = shutil.which("lake")
    if found is None:
        pytest.skip("lake is not available")
    lean_build("VE")
    return found


def decodes(lake: str, tmp_path: Path, cores: list[tuple[str, dict]]) -> subprocess.CompletedProcess:
    """Lean's `decodeNorm` on each node, one `#guard` per node."""
    lines = ["import VE.Norms.Wire", "open Lean"]
    for name, core in cores:
        text = json.dumps(json.dumps({"norm": core}))
        lines.append(f"#guard (do VE.Norms.Wire.decodeNorm (← Json.parse {text})).toBool -- {name}")
    source = tmp_path / "Blocks.lean"
    source.write_text("\n".join(lines) + "\n")
    return subprocess.run([lake, "env", "lean", str(source)], cwd=ROOT / "lean", capture_output=True, text=True,
                          timeout=HANG_TIMEOUT)


def test_every_recorded_node_decodes_in_lean(lake, tmp_path):
    cores = [(r["id"], {k: v for k, v in r["node"][0].items() if k in W1}) for name in CASES for r in blocks(name)]
    run = decodes(lake, tmp_path, cores)
    assert run.returncode == 0, run.stdout + run.stderr
    retyped = [(cores[0][0], {**cores[0][1], "sign": 1})] + cores[1:]
    assert decodes(lake, tmp_path, retyped).returncode != 0
