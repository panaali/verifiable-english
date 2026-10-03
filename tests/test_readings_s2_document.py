"""S2a through the document path (docs/spec/composition-s2.md 1.1, 4, 6, 9): the route, the refusals before any
verdict, the verdicts across readings and the report, on documents written to disk.

`data/readings_s2/constitution-nd-readings.ve.md` is the constitution pilot's case of DRI ruling 4 (run
20261003T0600Z, `probes/s1-probe.json` (a)): the pilot's own environment (`norm-defaults@0`, with `readings@1` added),
its claim graph, the force set `force-u0036-s05` with its two `content: null` candidates re-identified under the new
environment, and five of its units (the set's sentence, three rules, the graph's claim). The pilot reported it
refused with `UnsupportedProfile: readings@1 requires norms@0`, which is false of the document.
"""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

from ve.document import _environment, check_document
from ve.errors import VEError

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "tests/data/readings_s2/constitution-nd-readings.ve.md"
ABSTENTION = "UnsupportedProfile: readings@1 content with norm-defaults@0 is not implemented"


def _split(path):
    data = Path(path).read_bytes()
    end = data.index(b"\n---\n", 4)
    return json.loads(data[4:end]), data[end + 5:]


def _write(tmp_path, name, meta, rest):
    path = tmp_path / name
    path.write_bytes(b"---\n" + json.dumps(meta, ensure_ascii=False).encode() + b"\n---\n" + rest)
    return path


def _reidentified(env, item):
    spec = importlib.util.spec_from_file_location("readings_s1_pilot", ROOT / "tools/readings_s1_pilot.py")
    pilot = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pilot)
    return pilot._reidentified(env, item)


def test_ruling4_pilot_document_with_readings_and_norm_defaults_loads():
    """No set is content-bearing, so the document is W2's (1.1 row 1) and validates as without `readings@1`."""
    report = check_document(PILOT)
    assert report["admission"]["admitted"] is True
    assert report["premises"] == {"status": "UNKNOWN", "reason": "non-assertion reading elaboration pending"}
    assert "readings" not in report  # no content-bearing set: S1's and S2's blocks are not reached


def test_ruling4_pilot_document_answers_as_without_readings(tmp_path):
    meta, rest = _split(PILOT)
    plain = copy.deepcopy(meta)
    plain["environment"]["profiles"] = [p for p in plain["environment"]["profiles"] if p != "readings@1"]
    env = _environment(plain["environment"])
    plain["reading_sets"] = [_reidentified(env, item) for item in plain["reading_sets"]]
    without = check_document(_write(tmp_path, "plain.ve.md", plain, rest))
    with_readings = check_document(PILOT)
    for key in ("premises", "reading_plan", "stale_reading_labels"):
        assert with_readings[key] == without[key], key
    assert with_readings["admission"]["report"] == without["admission"]["report"]


def test_ruling4_rule_candidate_beside_norm_defaults_is_the_named_abstention(tmp_path):
    """The pilot's probe (b): a strict rule as one candidate's content. Lean and Python now both reach S1's
    abstention (before: Lean `invalid regulated role or default`, Python `unspecified completion requires
    norm-defaults@0`, so `CheckerUnavailable`)."""
    meta, rest = _split(PILOT)
    reading_set = meta["reading_sets"][0]
    reading_set.pop("models", None)
    env = _environment(meta["environment"])
    from ve.readings import s1_content_meaning_id
    rule = {"norm": {"name": "clarify-ambiguity", "predicate": "clarification_required", "sign": True,
                     "guard": ["unary", "genuine_ambiguity", ["var", 0]], "unless": [], "over": []}}
    strict = next(r for r in reading_set["readings"] if r["id"] == "strict")
    strict["content"] = rule
    strict["meaning_id"] = s1_content_meaning_id(env, reading_set["id"], strict)
    for r in reading_set["readings"]:
        r["admission"]["distinguishing_models"] = {o: "pending" for o in r["admission"]["distinguishing_models"]}
    with pytest.raises(VEError) as caught:
        check_document(_write(tmp_path, "rule.ve.md", meta, rest))
    assert caught.value.message == ABSTENTION


def test_ruling4_lean_frame_reads_unspecified_as_deny(lean_route):
    """Lean's decoder and Python's S1 environment agree on a `norm-defaults@0` frame: `unspecified` is the
    placeholder `deny` there (E‴), so readings-validate answers instead of failing to decode."""
    from ve.readings_route import document_wire, run_lean
    from ve.readings_s1 import S1Environment
    meta, _ = _split(PILOT)
    senv = S1Environment(meta["environment"])
    assert senv.frame.predicates["clarification_required"].regulated.default == "deny"
    units = [{"id": u["id"], "kind": u["kind"], "content": None} for u in meta["units"]]
    [row] = run_lean([{"id": "v", "kind": "readings-validate", "environment": meta["environment"],
                       "document": document_wire(units, meta["reading_sets"])}], executable=lean_route)
    assert row["status"] == "ok" and row["content_bearing"] is False, row


@pytest.fixture
def lean_route():
    from ve.readings_route import LEAN_ROUTE
    if not LEAN_ROUTE.exists():
        pytest.skip("ve_readings_route is not built")
    return LEAN_ROUTE
