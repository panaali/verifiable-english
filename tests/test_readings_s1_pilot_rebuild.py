"""The pilot's shared reading-set rebuild command after an environment edit."""

from pathlib import Path

import pytest

from tools import readings_s1_pilot as pilot
from ve.ast import formula_from_data
from ve.identity import meaning_id
from ve.model import FiniteModel
from ve.readings import _reading_evaluation
from ve.readings_s1 import S1Environment


FIXTURE = Path(__file__).parent / "data/readings_s2/constitution-nd-readings.ve.md"
UDHR = Path(__file__).resolve().parents[1] / "usecases/udhr-pilot/run-20261010T1400Z/translation.ve.md"


def test_rebuild_command_is_noop_on_unchanged_environment(tmp_path, capsys):
    assert pilot.main(["--rebuild-reading-ids", str(FIXTURE), "--check-noop"]) == 0
    assert '"no_op": true' in capsys.readouterr().out
    original, source = pilot.read(FIXTURE)
    changed = pilot.rebuild_reading_ids(original)
    assert changed["reading_sets"] == original["reading_sets"]
    destination = tmp_path / "same.ve.md"
    assert pilot.main(["--rebuild-reading-ids", str(FIXTURE), "--out", str(destination)]) == 0
    assert pilot.read(destination) == (original, source)


def test_rebuild_command_updates_every_set_after_environment_edit(tmp_path):
    meta, source = pilot.read(FIXTURE)
    first_sort = next(iter(meta["environment"]["vocabulary"]["sorts"].values()))
    first_sort["description"] += " after edit"
    edited = tmp_path / "edited.ve.md"
    pilot.write(edited, meta, source)
    with pytest.raises(SystemExit) as exc:
        pilot.main(["--rebuild-reading-ids", str(edited), "--check-noop"])
    assert exc.value.code == 2
    rebuilt = tmp_path / "rebuilt.ve.md"
    assert pilot.main(["--rebuild-reading-ids", str(edited), "--out", str(rebuilt)]) == 0
    refreshed, rest = pilot.read(rebuilt)
    assert rest == source
    assert refreshed["reading_sets"] != meta["reading_sets"]
    env = pilot._environment(refreshed["environment"])
    model_env, _ = _reading_evaluation(env)
    for item in refreshed["reading_sets"]:
        assert all(key == FiniteModel.from_dict(model_env, data).model_id
                   for key, data in item.get("models", {}).items())
    assert pilot.main(["--rebuild-reading-ids", str(rebuilt), "--check-noop"]) == 0


def test_rebuild_updates_formula_candidate_meanings():
    meta, _ = pilot.read(FIXTURE)
    item = meta["reading_sets"][0]
    item["readings"][0]["content"] = ["top"]
    item["readings"][1]["content"] = ["not", ["top"]]
    env = pilot._environment(meta["environment"])
    changed = pilot._reidentified(env, item)
    for reading in changed["readings"]:
        assert reading["meaning_id"] == meaning_id(env, formula_from_data(env, reading["content"]))


def test_rebuild_updates_situation_keys_and_admission_references():
    meta, _ = pilot.read(UDHR)
    original = next(item for item in meta["reading_sets"] if item.get("situations"))
    # A synthetic main-environment set exercises the rekeying branch. The
    # recorded UDHR set itself belongs to a companion environment.
    original = {**original, "readings": [{k: v for k, v in r.items() if k != "companion"}
                                          for r in original["readings"]]}
    changed = pilot._reidentified(pilot._environment(meta["environment"]), original)
    env = pilot._environment(meta["environment"])
    assert len(changed["situations"]) == len(original["situations"])
    assert all(key == S1Environment.situation_id_for(env, entry)
               for key, entry in changed["situations"].items())
    for reading in changed["readings"]:
        assert set(reading["admission"]["distinguishing_models"].values()) <= (
            set(changed["situations"]) | {"pending"})


def test_rebuild_preserves_companion_identities_on_unchanged_udhr(tmp_path):
    meta, source = pilot.read(UDHR)
    assert pilot.rebuild_reading_ids(meta)["reading_sets"] == meta["reading_sets"]
    out = tmp_path / "same.ve.md"
    assert pilot.main(["--rebuild-reading-ids", str(UDHR), "--check-noop", "--out", str(out)]) == 0
    assert pilot.read(out) == (meta, source)
