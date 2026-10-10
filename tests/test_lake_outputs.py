"""tools/lake_outputs.py: an executable whose Lake trace does not record the file beside it is stale (rd-6b review
B2: an older `ve_conformance` under a trace copied from another checkout, reported up to date by Lake)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools import lake_outputs

ROOT = Path(__file__).resolve().parents[1]


def project(tmp_path, binaries):
    """A Lake build directory holding `binaries` (name -> bytes), each traced as Lake traces it."""
    directory = tmp_path / ".lake/build/bin"
    directory.mkdir(parents=True)
    paths = []
    for name, content in binaries.items():
        path = directory / name
        path.write_bytes(content)
        paths.append(path)
    hashes = lake_outputs.output_hashes(paths)
    for path in paths:
        path.with_name(path.name + ".trace").write_text(json.dumps({"outputs": hashes[path], "log": []}))
        path.with_name(path.name + ".hash").write_text(hashes[path])
    return directory


def test_traced_binaries_are_fresh_and_a_replaced_binary_is_stale(tmp_path):
    directory = project(tmp_path, {"ve_a": b"one build", "ve_b": b"another build"})
    assert lake_outputs.stale(tmp_path) == []
    # The review's case: the file is an older build, the trace a newer one's.
    (directory / "ve_a").write_bytes(b"an older build")
    assert lake_outputs.stale(tmp_path) == [directory / "ve_a"]
    assert lake_outputs.drop_stale(tmp_path) == [directory / "ve_a"]
    assert not (directory / "ve_a.trace").exists() and not (directory / "ve_a.hash").exists()
    assert (directory / "ve_a").is_file() and (directory / "ve_b.trace").is_file()
    assert lake_outputs.stale(tmp_path) == []


@pytest.mark.parametrize("trace", ["", "{", "[]", '{"log": []}', '{"outputs": null}', '{"outputs": true}',
                                   '{"outputs": "0"}'])
def test_an_unreadable_or_wrong_trace_is_stale(tmp_path, trace):
    directory = project(tmp_path, {"ve_a": b"build"})
    (directory / "ve_a.trace").write_text(trace)
    assert lake_outputs.stale(tmp_path) == [directory / "ve_a"]
    assert lake_outputs.main(["--lean", str(tmp_path)]) == 1


def test_the_oracle_is_lakes_hash():
    """Known answer: Lake's own `.hash` of an executable it built is the oracle's hash of that file."""
    binary = ROOT / "lean/.lake/build/bin/ve_conformance"
    assert lake_outputs.output_hashes([binary])[binary] == binary.with_name("ve_conformance.hash").read_text().strip()


def test_every_build_entry_point_drops_stale_traces_first():
    """The gate fails when its build leaves a stale executable; the map recorder and the CI fuzz test check too."""
    gate = (ROOT / "tools/gate.py").read_text()
    # in the gate's own allowlisted environment, as its build runs (an ambient LD_PRELOAD never reaches it)
    assert gate.index("lake_outputs.drop_stale(env=env)") < gate.index('command(["lake", "build"]') < \
        gate.index("lake_outputs.stale(env=env)")
    recorder = (ROOT / "tools/test_map.py").read_text()
    assert recorder.index("lake_outputs.drop_stale()") < recorder.index('(["lake", "build"]')
    assert "lake_outputs.stale() == []" in (ROOT / "tests/test_difffuzz.py").read_text()
