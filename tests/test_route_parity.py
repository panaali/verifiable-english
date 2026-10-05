"""docs/lean-first/b1/route_parity.py, the Gate-1 byte parity of lean-first batch 1, passes only on evidence.

lf-1 review B: given a recording directory and a one-shot bin directory that did not exist, the tool
compared nothing and exited 0. Missing, empty or partial inputs now exit 2 before anything runs, and a
run whose accounting does not cover every case sent, or every requested mode, exits 1.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("route_parity", ROOT / "docs/lean-first/b1/route_parity.py")
route_parity = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(route_parity)

CASE = json.dumps({"id": "c", "kind": "evaluate"})


def record(directory: Path, pairs) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "main-1.jsonl").write_text("".join(json.dumps(list(p)) + "\n" for p in pairs))
    return directory


def bin_dir(directory: Path, modes) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    for mode in modes:
        (directory / route_parity.EXECUTABLES[mode]).write_text("")
    return directory


def run(*argv):
    return route_parity.main([str(a) for a in argv])


def test_nonexistent_recording_and_binaries_fail(tmp_path, capsys):
    """The reviewer's reproduction: it exited 0, reporting zero cases and no modes."""
    assert run(tmp_path / "no-recording", tmp_path / "no-bin") == 2
    assert run(tmp_path / "no-recording", bin_dir(tmp_path / "bin", route_parity.EXECUTABLES)) == 2
    assert "no recording directory" in capsys.readouterr().err


@pytest.mark.parametrize("contents", [None, []])
def test_empty_recordings_fail(tmp_path, capsys, contents):
    recorded = tmp_path / "rec"
    recorded.mkdir()
    if contents is not None:
        record(recorded, contents)
    assert run(recorded, bin_dir(tmp_path / "bin", ["soft-norms"]), "--modes", "soft-norms") == 2
    assert "no " in capsys.readouterr().err


def test_a_requested_mode_without_cases_fails(tmp_path, capsys):
    recorded = record(tmp_path / "rec", [("soft-norms", CASE)])
    assert run(recorded, bin_dir(tmp_path / "bin", ["soft-norms", "rights"]), "--modes", "soft-norms,rights") == 2
    assert "no recorded case for modes rights" in capsys.readouterr().err
    # The default is every mode, so a recording of one mode is not parity for all.
    assert run(recorded, bin_dir(tmp_path / "bin", route_parity.EXECUTABLES)) == 2


def test_missing_one_shot_executable_and_unknown_modes_fail(tmp_path, capsys):
    recorded = record(tmp_path / "rec", [("soft-norms", CASE)])
    assert run(recorded, tmp_path / "bin-empty", "--modes", "soft-norms") == 2
    assert "ve_soft_norms_route" in capsys.readouterr().err
    assert run(recorded, bin_dir(tmp_path / "bin", ["soft-norms"]), "--modes", "soft-norms,not-a-mode") == 2


def _fake(monkeypatch, old, new):
    monkeypatch.setattr(route_parity, "one_shot", lambda base, mode, unit, texts: (old(texts), 0.0, 0.0))
    monkeypatch.setattr(route_parity, "service_rows", lambda mode, texts: (new(texts), 0.0, 0.0))


def _rows(texts):
    return [{"id": json.loads(t)["id"], "status": "ok"} for t in texts]


@pytest.fixture
def inputs(tmp_path):
    cases = [json.dumps({"id": f"c{i}"}) for i in range(70)]
    recorded = record(tmp_path / "rec", [("soft-norms", t) for t in cases] + [("rights", cases[0])])
    return recorded, bin_dir(tmp_path / "bin", ["soft-norms", "rights"])


def test_identical_rows_pass_with_every_case_accounted(monkeypatch, inputs, tmp_path):
    _fake(monkeypatch, _rows, _rows)
    out = tmp_path / "out.json"
    assert run(*inputs, "--modes", "soft-norms,rights", "--out", out) == 0
    report = json.loads(out.read_text())
    assert report["total"]["cases"] == report["total"]["same"] == 71
    assert report["requested_modes"] == ["rights", "soft-norms"] and report["problems"] == []


@pytest.mark.parametrize("new", [
    lambda texts: [{**row, "status": "error"} for row in _rows(texts)],  # a row differs
    lambda texts: _rows(texts)[:-1],  # a row is missing
    lambda texts: None,  # the service refuses a batch the one-shot answered
])
def test_differences_fail(monkeypatch, inputs, new):
    _fake(monkeypatch, _rows, new)
    assert run(*inputs, "--modes", "soft-norms,rights") == 1


def test_a_batch_difference_counts_every_case_of_the_batch(monkeypatch, inputs, tmp_path):
    _fake(monkeypatch, _rows, lambda texts: _rows(texts)[:-1])
    out = tmp_path / "out.json"
    run(*inputs, "--modes", "soft-norms", "--out", out)
    entry = json.loads(out.read_text())["modes"]["soft-norms"]
    assert entry["different"] == entry["cases"] == 70 and entry["same"] == 0


def test_lost_cases_and_missing_modes_are_problems():
    """A comparison that drops cases or modes (a mutant of `compare`) is no evidence either."""
    entry = {"cases": 3, "same": 2, "by_design": 0, "different": 0}
    assert route_parity.verdict_problems({"rights"}, 3, {"rights": entry}, {**entry}) != []
    full = {**entry, "same": 3}
    assert route_parity.verdict_problems({"rights"}, 3, {"rights": full}, full) == []
    assert route_parity.verdict_problems({"rights", "risk"}, 3, {"rights": full}, full) != []
    assert route_parity.verdict_problems({"rights"}, 4, {"rights": full}, full) != []
    zero = {"cases": 0, "same": 0, "by_design": 0, "different": 0}
    assert route_parity.verdict_problems({"rights"}, 0, {"rights": zero}, zero) != []
