"""The pilot's shared reading-set rebuild command after an environment edit."""

import json
from pathlib import Path

import pytest

from tests import lean_routes
from tests.test_document import unit, write_doc
from tests.test_readings_s1_lean import entry, norm, reading, reading_set, situation_id
from tools import readings_s1_pilot as pilot
from ve.ast import formula_from_data
from ve.document import check_document, load_document
from ve.errors import VEError
from ve.identity import meaning_id
from ve.model import FiniteModel
from ve.profiles import LANGUAGE, SPEC_REVISION
from ve.readings import _reading_evaluation, s1_content_meaning_id
from ve.readings_s1 import S1Environment


FIXTURE = Path(__file__).parent / "data/readings_s2/constitution-nd-readings.ve.md"
UDHR = Path(__file__).resolve().parents[1] / "usecases/udhr-pilot/run-20261010T1400Z/translation.ve.md"
TABLE = Path(__file__).resolve().parents[1] / "ve/profile_table.json"
TEXTS = {"u0": "Every agent may help each user.\n", "u1": "Every agent must help each user.\n",
         "u2": "Every agent may help each user who asks.\n"}
SCOPE = {"version": "scope@0", "governors": [{"id": "g1", "unit": "u0", "reach": {"rules": ["may-help-asked"]},
                                              "units": ["u2"], "effect": {"reguard": ["and", "own", ["top"]]}}]}


@pytest.fixture
def lean():
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service has not been built")


ASKS = ["binary", "asks", ["var", 0], ["var", 1]]


def nd_part(tmp_path, *, scoped=False, name="part"):
    """F-ND1 (tests/test_readings_nd_lean.py) as a part document: its reading set under `norm-defaults@0`, whose
    situation's base is over the filled frame (the `unsaid__` tables, no regulated predicate), as the UDHR parts' are,
    between two rules of its own. `scoped` lists `scope@0` with one governor (u0 re-guards u2's rule)."""
    def regulated(role, **extra):
        return {"role": role, "default": "unspecified", "act": "{0} help {1}", **extra}
    raw = {"language": LANGUAGE, "profiles": ["norm-defaults@0", "norms@0", "readings@1", "relational-fol@0"],
           "spec_revision": SPEC_REVISION, "vocabulary": {
               "sorts": {"agent": {"description": "agent"}, "user": {"description": "user"}}, "constants": {},
               "predicates": {
                   "asks": {"arguments": ["user", "agent"], "description": "{0} asks {1}"},
                   "help_required": {"arguments": ["agent", "user"], "description": "obligation",
                                     "regulated": regulated("obligation", permission="help_permitted")},
                   "help_permitted": {"arguments": ["agent", "user"], "description": "permission",
                                      "regulated": regulated("permission")}}}}
    sigma = entry({"domains": {"agent": ["a"], "user": ["u"]}, "constants": {},
                   "relations": {"asks": [], "unsaid__help_permitted": [["a", "u"]], "unsaid__help_required": []}},
                  "every", {"outcome": {"predicate": "help_required", "tuple": ["a", "u"]}}, True)
    sid = situation_id(raw, sigma)
    rs = reading_set("rs_1", "u1", [reading("every", norm("must-help", "help_required", True), {"asks": sid}),
                                    reading("asks", norm("must-help", "help_required", True, guard=ASKS),
                                            {"every": sid})], {sid: sigma})
    env = pilot._environment(raw)
    for r in rs["readings"]:
        r["meaning_id"] = s1_content_meaning_id(env, rs["id"], r)
    contents = {"u0": norm("may-help", "help_permitted", True), "u1": None,
                "u2": norm("may-help-asked", "help_permitted", True, guard=ASKS)}
    units, text = [], b""
    for uid, content in contents.items():
        units.append(unit(uid, len(text), len(text) + len(TEXTS[uid].encode()), "norm", "specified", content))
        text += TEXTS[uid].encode()
    (tmp_path / name).mkdir()
    path = write_doc(tmp_path / name, text, units, environment_json=raw, reading_sets=[rs])
    meta, source = pilot.read(path)
    if scoped:
        meta["environment"]["profiles"] = sorted([*meta["environment"]["profiles"], "scope@0"])
        meta["scope"] = SCOPE
    pilot.write(path, meta, source)
    return path


def rebuilt(path, tmp_path):
    out = tmp_path / f"{path.parent.name}-rebuilt.ve.md"
    assert pilot.main(["--rebuild-reading-ids", str(path), "--out", str(out)]) == 0
    return out


def is_noop(path):
    try:
        return pilot.main(["--rebuild-reading-ids", str(path), "--check-noop"]) == 0
    except SystemExit as exc:
        assert exc.code == 2
        return False


def test_a_scope_part_with_a_reading_set_rebuilds_as_a_noop_lean_admits(lean, tmp_path):
    path = nd_part(tmp_path, scoped=True)
    assert is_noop(path)
    assert rebuilt(path, tmp_path).read_bytes() == path.read_bytes()
    report = check_document(path)
    assert [s["set"] for s in report["readings"]["sets"]] == ["rs_1"]
    # The ids are those of the environment the chain reads, without `scope@0`: the part's own without it.
    plain, _ = pilot.read(nd_part(tmp_path, name="plain"))
    assert pilot.read(path)[0]["reading_sets"] == plain["reading_sets"]


def test_an_edited_scope_part_rebuilds_to_the_ids_lean_accepts(lean, tmp_path):
    edited = []
    for scoped, name in ((True, "scoped"), (False, "plain")):
        path = nd_part(tmp_path, scoped=scoped, name=name)
        meta, source = pilot.read(path)
        meta["environment"]["vocabulary"]["sorts"]["agent"]["description"] += " after edit"
        pilot.write(path, meta, source)
        assert not is_noop(path)
        out = rebuilt(path, tmp_path)
        assert is_noop(out)
        assert [s["set"] for s in check_document(out)["readings"]["sets"]] == ["rs_1"]
        edited.append(pilot.read(out)[0]["reading_sets"])
    assert edited[0] == edited[1] and edited[0] != pilot.read(nd_part(tmp_path, name="base"))[0]["reading_sets"]


@pytest.mark.parametrize("profiles", [
    ["readings@1", "relational-fol@0", "scope@0"],
    ["alternatives@0", "norms@0", "readings@1", "relational-fol@0", "risk@0", "scope@0"],
    ["norm-defaults@0", "norms@0", "readings@1", "relational-fol@0", "scope@0", "ve.discourse@1"]],
    ids=["without-norms", "with-risk", "with-discourse"])
def test_a_scope_list_the_document_mode_refuses_is_refused_with_leans_text(lean, tmp_path, profiles):
    path = nd_part(tmp_path, scoped=True)
    meta, source = pilot.read(path)
    meta["environment"]["profiles"] = profiles
    pilot.write(path, meta, source)
    with pytest.raises(VEError) as document_mode:
        load_document(path)
    with pytest.raises(VEError) as rebuild:
        pilot.rebuild_reading_ids(meta, source)
    assert str(rebuild.value) == str(document_mode.value)
    assert str(rebuild.value).startswith("UnsupportedProfile: ")
    if "ve.discourse@1" in profiles:
        # scope@0's own row of Lean's profile table (`ve/profile_table.json`, generated from `VE.Compose.profileTable`).
        [row] = [r for r in json.loads(TABLE.read_text())["rows"] if r["profile"] == "scope@0"]
        assert str(rebuild.value) == "UnsupportedProfile: " + dict(row["refuses"])["ve.discourse@1"]


def test_rebuild_is_a_noop_on_a_situation_over_the_filled_frame(lean, tmp_path):
    path = nd_part(tmp_path)
    assert is_noop(path)
    out = rebuilt(path, tmp_path)
    assert out.read_bytes() == path.read_bytes()
    assert check_document(out) == check_document(path)


def test_rebuild_adds_a_new_base_predicate_and_no_regulated_one(lean, tmp_path):
    path = nd_part(tmp_path)
    meta, source = pilot.read(path)
    meta["environment"]["vocabulary"]["predicates"]["trusts"] = {"arguments": ["user", "agent"],
                                                                 "description": "{0} trusts {1}"}
    pilot.write(path, meta, source)
    with pytest.raises(VEError):
        check_document(path)
    out = rebuilt(path, tmp_path)
    [entry] = pilot.read(out)[0]["reading_sets"][0]["situations"].values()
    assert list(entry["base"]["relations"]) == ["asks", "unsaid__help_permitted", "unsaid__help_required", "trusts"]
    assert entry["base"]["relations"]["trusts"] == []
    assert [s["set"] for s in check_document(out)["readings"]["sets"]] == ["rs_1"]


def test_rebuild_command_is_noop_on_unchanged_environment(tmp_path, capsys):
    assert pilot.main(["--rebuild-reading-ids", str(FIXTURE), "--check-noop"]) == 0
    assert '"no_op": true' in capsys.readouterr().out
    original, source = pilot.read(FIXTURE)
    changed = pilot.rebuild_reading_ids(original, source)
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
    assert pilot.rebuild_reading_ids(meta, source)["reading_sets"] == meta["reading_sets"]
    out = tmp_path / "same.ve.md"
    assert pilot.main(["--rebuild-reading-ids", str(UDHR), "--check-noop", "--out", str(out)]) == 0
    assert pilot.read(out) == (meta, source)
