"""tools/lake_outputs.py: an executable whose Lake trace does not record the file beside it is stale (rd-6b review
B2: an older `ve_conformance` under a trace copied from another checkout, reported up to date by Lake)."""
from __future__ import annotations

import json
import os
from pathlib import Path
import pwd
from types import SimpleNamespace

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


def test_lean_is_found_in_the_accounts_elan_when_home_is_replaced(tmp_path, monkeypatch):
    """The gate replaces HOME with its scratch home; a stage whose PATH lacks the toolchain (the gate's own tests
    fake its toolchain check) still finds the account's elan `lean`, and only a missing one is an error."""
    account = Path(pwd.getpwuid(os.getuid()).pw_dir)
    if not (account / ".elan/bin/lean").is_file():
        pytest.skip("no elan in this account")
    monkeypatch.setenv("HOME", str(tmp_path))
    assert lake_outputs.lean_executable({"PATH": "/usr/bin:/bin"}) == str(account / ".elan/bin/lean")
    monkeypatch.setattr(lake_outputs.pwd, "getpwuid", lambda uid: SimpleNamespace(pw_dir=str(tmp_path)))
    with pytest.raises(RuntimeError, match="lean is required"):
        lake_outputs.lean_executable({"PATH": "/usr/bin:/bin"})


def test_every_build_entry_point_drops_stale_traces_first():
    """The gate fails when its build leaves a stale executable; the map recorder and the CI fuzz test check too."""
    gate = (ROOT / "tools/gate.py").read_text()
    # in the gate's own allowlisted environment, as its build runs (an ambient LD_PRELOAD never reaches it)
    assert gate.index('lake_outputs.drop_stale(ROOT / "lean", env=env)') < \
        gate.index('command(["lake", "build"]') < \
        gate.index('lake_outputs.stale(ROOT / "lean", env=env)')
    recorder = (ROOT / "tools/test_map.py").read_text()
    assert recorder.index("lake_outputs.drop_stale()") < recorder.index('(["lake", "build"]')
    assert "lake_outputs.stale() == []" in (ROOT / "tests/test_difffuzz.py").read_text()


def lakefile(lean, *targets):
    """A lakefile.toml with these `lean_exe` tables (each a dict of its keys)."""
    lean.mkdir(parents=True, exist_ok=True)
    tables = "".join("\n[[lean_exe]]\n" + "".join(f'{key} = "{value}"\n' for key, value in target.items())
                     for target in targets)
    (lean / "lakefile.toml").write_text(f'name = "p"\n\n[[lean_lib]]\nname = "P"\n{tables}')


def test_a_removed_targets_binary_is_obsolete_and_a_live_ones_files_are_kept(tmp_path):
    """Plan 3.8 "Obsolete executables": Lake never touches the binary of a target the lakefile dropped."""
    lakefile(tmp_path, {"name": "ve_service", "root": "Serve"}, {"name": "ve_bench", "root": "Bench"},
             {"name": "ve_named", "root": "Named", "exeName": "ve_file"})
    directory = tmp_path / ".lake/build/bin"
    directory.mkdir(parents=True)
    live = ["ve_service", "ve_service.trace", "ve_service.hash", "ve_service.sha256-cache", "ve_bench", "ve_file",
            "ve_file.trace"]
    gone = ["ve_diagnose", "ve_diagnose.trace", "ve_diagnose.hash", "ve_named", "ve_service.tmp1e62a1a",
            "ve_service.sha256-cachexyz", "ve_servicex"]
    for name in live + gone:
        (directory / name).write_bytes(b"x")
    (directory / "ve_rights_route.dSYM").mkdir()
    (directory / "ve_rights_route.dSYM/ve_rights_route").write_bytes(b"x")
    expected = sorted(directory / name for name in [*gone, "ve_rights_route.dSYM"])
    assert lake_outputs.obsolete(tmp_path) == expected
    assert lake_outputs.main(["--obsolete", "--lean", str(tmp_path)]) == 1
    assert lake_outputs.main(["--drop-obsolete", "--lean", str(tmp_path)]) == 0
    assert sorted(path.name for path in directory.iterdir()) == sorted(live)
    assert lake_outputs.obsolete(tmp_path) == [] and lake_outputs.main(["--obsolete", "--lean", str(tmp_path)]) == 0


def test_the_repositorys_executables_are_its_lakefiles():
    """Known answer: the file names of every lean_exe of lean/lakefile.toml, default target or not."""
    assert lake_outputs.executables() == [
        "ve_conformance", "ve_metered", "ve_service", "ve_english_run", "ve_response_decode", "ve_english_lean_bench",
        "ve_english_route", "ve_speech_acts_route", "ve_senses_route"]


@pytest.mark.parametrize("text", ['name = "p"\n[[lean_exe]]\nroot = "Main"\n',
                                  'name = "p"\n[[lean_exe]]\nname = "Ve.Service"\n',
                                  'name = "p"\n[[lean_exe]]\nname = "../ve"\n',
                                  'name = "p"\nlean_exe = "ve"\n',
                                  'name = "p"\n[[lean_exe\n'])
def test_targets_it_cannot_name_remove_nothing(tmp_path, text):
    (tmp_path / "lakefile.toml").write_text(text)
    (tmp_path / ".lake/build/bin").mkdir(parents=True)
    (tmp_path / ".lake/build/bin/ve").write_bytes(b"x")
    with pytest.raises(RuntimeError):
        lake_outputs.drop_obsolete(tmp_path)
    assert (tmp_path / ".lake/build/bin/ve").exists()


def test_a_lakefile_only_lake_can_evaluate_removes_nothing(tmp_path):
    lakefile(tmp_path, {"name": "ve_service", "root": "Serve"})
    (tmp_path / "lakefile.lean").write_text("import Lake\n")
    (tmp_path / ".lake/build/bin").mkdir(parents=True)
    (tmp_path / ".lake/build/bin/ve_old").write_bytes(b"x")
    with pytest.raises(RuntimeError, match="only Lake can read its targets"):
        lake_outputs.drop_obsolete(tmp_path)
    assert (tmp_path / ".lake/build/bin/ve_old").exists()
