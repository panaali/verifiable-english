"""tools/binding_census.py: ADR 0001's census of every response-shape leaf, and the probe of the hand binders.

* The committed census is the one the tool generates from the shapes and the recorded evidence, it covers every
  mode and every leaf of the generic checker's static census, and a stale copy fails `--check`.
* rd-9's 47 fields are each placed in the census.
* A probe refusal is attributed to the hand check that made it (the exception it converted, else its first
  frame that is not an error-building helper), never to the service client; a later Lean request's rejection
  counts as the transport's. A hand check is retirable later only if the generic checker refuses every probed
  mutant it refuses.
* The probe itself, live on one consumer test, records mutants with the generic verdict and the hand check that
  refused them.
"""
from __future__ import annotations

import gzip
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import binding_census as C  # noqa: E402
from ve.backends import shape_binding  # noqa: E402
from ve.backends.service_schema import MODES  # noqa: E402

CENSUS = json.loads(C.CENSUS.read_text())


def test_the_census_is_current():
    assert C.main(["--check"]) == 0


def test_a_stale_census_fails_the_check(tmp_path, monkeypatch, capsys):
    stale = tmp_path / "census.json"
    stale.write_text(C.CENSUS.read_text().replace('"class": "bound"', '"class": "none"', 1))
    view = tmp_path / "census.md"
    view.write_text(C.VIEW.read_text())
    monkeypatch.setattr(C, "CENSUS", stale)
    monkeypatch.setattr(C, "VIEW", view)
    assert C.main(["--check"]) == 1
    assert "census.json is stale" in capsys.readouterr().err


def test_the_census_covers_every_mode_and_every_leaf():
    assert list(CENSUS["modes"]) == list(MODES)
    for mode, data in CENSUS["modes"].items():
        static = {(leaf.path, leaf.kind, leaf.binding.cls) for leaf in shape_binding.leaves(mode)
                  if "/~" not in leaf.path}
        listed = {(row["path"], row["kind"], row["class"]) for row in data["leaves"]}
        assert listed == static, mode
        assert {row["class"] for row in data["leaves"]} <= set(shape_binding.CLASSES)
        assert all(row["today"]["status"] == "shape" for row in data["leaves"] if row["class"] != "none"), mode


def test_rd9s_47_fields_are_each_placed():
    rows = CENSUS["rd9"]
    assert [row["row"] for row in rows] == list(range(1, 48))
    for row in rows:
        if "note" not in row:
            assert row["places"] and all(place["class"] != "missing" for place in row["places"]), row


def _line(**overrides):
    line = {"mode": "discourse", "test": "t", "kind": "flip", "path": "/x", "expect": "accept", "why": "",
            "generic": "accept", "outcome": "CheckerUnavailable", "caller": ["ve/discourse.py", "lean_admission"],
            "refusals": []}
    return {**line, **overrides}


def test_a_refusal_is_attributed_to_the_check_that_made_it():
    converted = _line(refusals=[{"transport": False, "frames": [["ve/document.py", 450, "unavailable"]],
                                 "cause": {"transport": False, "frames": [["ve/document.py", 531, "require"]]}}])
    assert C._attributed(converted)["site"]["function"] == "require"
    helper = _line(refusals=[{"transport": False, "cause": None,
                              "frames": [["ve/document.py", 450, "unavailable"], ["ve/document.py", 470,
                                                                                   "_lean_document"]]}])
    assert C._attributed(helper)["site"]["function"] == "_lean_document"
    direct = _line(refusals=[{"transport": False, "cause": None, "frames": [["ve/discourse.py", 191,
                                                                             "lean_admission"]]}])
    assert (C._attributed(direct)["refused"], C._attributed(direct)["site"]["line"]) == ("hand", 191)
    later = _line(refusals=[{"transport": True, "cause": None, "frames": [["ve/rights.py", 231, "_soft"]]}])
    assert (C._attributed(later)["refused"], C._attributed(later)["site"]) == ("transport", None)
    rejected = _line(refusals=[{"transport": False, "frames": [["ve/rights.py", 231, "_soft"]],
                                "cause": {"transport": True, "frames": [["ve/rights.py", 229, "_soft"]]}}])
    assert C._attributed(rejected)["refused"] == "transport"
    assert C._attributed(_line(outcome="passed"))["refused"] is None


def test_a_hand_check_is_retirable_only_if_the_generic_checker_refuses_all_it_refuses():
    site = {"file": "ve/x.py", "function": "bind", "line": 3, "text": "raise CheckerUnavailable('x')"}
    probe = {"mode": "m", "kind": "flip", "path": "/a", "refused": "hand", "site": site, "generic": "refuse"}
    [covered] = C.hand_binders([probe, {**probe, "path": "/b"}])
    assert covered["retirable_later"] and not covered["refused_only_by_hand"]
    [carrying] = C.hand_binders([probe, {**probe, "path": "/b", "generic": "accept"}])
    assert not carrying["retirable_later"] and carrying["refused_only_by_hand"] == ["m flip /b"]
    assert C.hand_binders([{**probe, "refused": "transport", "site": None}]) == []


def test_the_census_names_the_hand_binders_the_probe_found():
    binders = {binder["binder"]: binder for binder in CENSUS["hand_binders"]}
    # The discourse joint-choices binder carries the SOME-to-ALL binding the shapes do not state
    # (tests/test_discourse_answer.py::test_duplicate_and_out_of_range_choices_are_no_answer).
    joint = binders["ve/discourse.py:_bind_joint"]
    assert not joint["retirable_later"]
    assert any("joint_choices" in item for item in joint["refused_only_by_hand"]), joint


def test_the_probe_finds_the_hand_check_of_a_consumer_test(tmp_path):
    """Live: the probe over one consumer test of `words` records mutants with the generic checker's verdict, and
    attributes a refusal to `ve.words.read_answer`, the hand binder of that route."""
    import nested_pytest
    test = "tests/test_words.py::test_lean_words_as_the_pre_q24_producers_did[0]"
    done = subprocess.run(nested_pytest.command(["-q", "-p", "tests.binding_probe", test]), cwd=ROOT,
                          env=nested_pytest.environment(os.environ, VE_BINDING_PROBE=str(tmp_path)),
                          capture_output=True, text=True)
    assert done.returncode == 0, done.stdout[-2000:] + done.stderr[-2000:]
    lines = [json.loads(line) for path in tmp_path.glob("probe-*.jsonl") for line in path.read_text().splitlines()]
    probes = [C._attributed(line) for line in lines if "genuine" not in line and "error" not in line]
    assert any("genuine" in line for line in lines)
    assert probes and all(p["generic"] in ("accept", "refuse") for p in probes)
    assert any(p["refused"] == "hand" and p["site"]["file"] == "ve/words.py" and p["site"]["function"] ==
               "read_answer" for p in probes), probes


def test_the_recorded_evidence_is_gzip_without_a_timestamp():
    for path in (C.ANSWERS, C.PROBES):
        data = path.read_bytes()
        assert data[4:8] == b"\0\0\0\0", path  # mtime 0: the same lines give the same bytes
        assert gzip.decompress(data)
