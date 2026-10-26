"""AR-10: Python reads the profile table Lean generates (`ve/profile_table.json`) and holds no row of its own."""
import os
from pathlib import Path
import subprocess
import sys

from subprocesses import HANG_TIMEOUT
from tools import profile_table
from ve import profiles

ROOT = Path(__file__).resolve().parents[1]


def test_the_committed_table_is_the_lean_generators_output():
    """The committed file is what `VE/Compose/ProfilesMain.lean` prints now, checked by the generator itself, so an
    edit of `profileTable` without `--write` fails the suite."""
    env = {**os.environ, "PATH": os.environ.get("PATH", "") + os.pathsep + str(Path.home() / ".elan/bin")}
    done = subprocess.run([sys.executable, str(ROOT / "tools/profile_table.py"), "--check"], cwd=ROOT, env=env,
                          capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert done.returncode == 0, (done.stdout, done.stderr)


def test_python_reads_the_rows_and_the_environment_profiles():
    """`BY_NAME` is the table's environment list, each with its rows; every row is typed as Lean writes it."""
    assert list(profiles.BY_NAME) == profiles._TABLE["environment"]
    assert len(profiles.BY_NAME) == 18 and profiles.BASE in profiles.BY_NAME and "readings@1" in profiles.BY_NAME
    assert profiles.BY_NAME["risk@0"] == tuple(r for r in profiles.ROWS if r["profile"] == "risk@0")
    assert len(profiles.BY_NAME["risk@0"]) == 2
    for row in profiles.ROWS:
        assert set(row) == {"profile", "requires", "refuses", "slot"}
        assert type(row["profile"]) is str and type(row["slot"]) is str
        assert all(type(q) is str for q in row["requires"])
        assert all(type(pair) is list and len(pair) == 2 and all(type(x) is str for x in pair)
                   for pair in row["refuses"])
    # rows that are no environment profile of their own: discourse's, the rights clauses' and scope@0, a wrapper
    # the Lean document mode runs before the chain (sc-1b)
    assert {r["profile"] for r in profiles.ROWS} - set(profiles.BY_NAME) == {"ve.discourse@1", "right-clauses@0",
                                                                             "scope@0"}


def test_no_python_gate_remains():
    """The Python mirror of the gate is gone: Lean's `gateOf` is the one owner (R6)."""
    for name in ("REGISTRY", "ProfileRecord", "checker_family", "route_gate", "require_checker", "GATED"):
        assert not hasattr(profiles, name), name


def test_generator_writes_lean_output_and_check_refuses_any_other_file(tmp_path, monkeypatch):
    """`--write` stores exactly what the Lean printer printed; `--check` passes only on that file, and a printer
    failure is never a pass. The Lean run is replaced by its recorded output."""
    target = tmp_path / "profile_table.json"
    printed = (ROOT / "ve/profile_table.json").read_text()
    result = subprocess.CompletedProcess([], 0, stdout=printed.rstrip("\n"), stderr="")
    monkeypatch.setattr(profile_table, "TARGET", target)
    monkeypatch.setattr(profile_table.subprocess, "run", lambda *args, **kwargs: result)

    def run(flag):
        monkeypatch.setattr(sys, "argv", ["profile_table.py", flag])
        return profile_table.main()

    assert run("--check") == 1  # no file yet
    assert run("--write") == 0 and target.read_text() == printed
    assert run("--check") == 0
    target.write_text(printed.replace('"slot": "risk"', '"slot": "norms"', 1))
    assert run("--check") == 1
    failed = subprocess.CompletedProcess([], 2, stdout="", stderr="lake failed")
    monkeypatch.setattr(profile_table.subprocess, "run", lambda *args, **kwargs: failed)
    target.write_text(printed)
    assert run("--check") == 2 and run("--write") == 2 and target.read_text() == printed
