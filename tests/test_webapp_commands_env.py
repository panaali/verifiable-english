"""CI-8 (iv): `usecases/webapp-commands/environment.json` is Lean's print of `VE.Commands.Examples.E_web` and its
lexicon, written only by `tools/webapp_commands_env.py` through `tools/regen_generated.py`; no hand copy exists."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from subprocesses import HANG_TIMEOUT
from tools import regen_generated, webapp_commands_env

ROOT = Path(__file__).resolve().parents[1]
COMMITTED = ROOT / "usecases/webapp-commands/environment.json"


def _lean_env() -> dict:
    return {**os.environ, "PATH": os.environ.get("PATH", "") + os.pathsep + str(Path.home() / ".elan/bin")}


def test_the_committed_environment_is_the_lean_generators_output():
    """The committed file is what `VE/Commands/WebEnvMain.lean` prints now: checked by the generator's `--check` and,
    so that a generator holding its own copy cannot pass by agreeing with itself, by running the printer directly."""
    done = subprocess.run([sys.executable, str(ROOT / "tools/webapp_commands_env.py"), "--check"], cwd=ROOT,
                          env=_lean_env(), capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert done.returncode == 0, (done.stdout, done.stderr)
    printed = subprocess.run(["lake", "env", "lean", "--run", "VE/Commands/WebEnvMain.lean"], cwd=ROOT / "lean",
                             env=_lean_env(), capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert printed.returncode == 0, printed.stderr
    assert COMMITTED.read_text() == printed.stdout


def test_the_file_is_the_environment_and_its_lexicon():
    """The two fields an `english.command` request carries besides its wording, each as Lean printed it."""
    data = json.loads(COMMITTED.read_text())
    assert set(data) == {"environment", "lexicon"}
    env, lexicon = data["environment"], data["lexicon"]
    assert set(env["vocabulary"]["sorts"]) == {"user", "control", "ledger", "text", "reading", "token"}
    assert env["speech_acts"]["task"] == "webapp-copy"
    assert env["speech_acts"]["addressee"] == {"sort": "user", "constant": "reader"}
    assert type(lexicon) is dict and type(lexicon["environment_id"]) is str and lexicon["environment_id"]
    assert [letter for _, letter in lexicon["letters"]] == ["A", "B", "C", "D", "E", "F"]


def test_regen_generated_owns_the_file_through_this_generator():
    entry = regen_generated.owner("usecases/webapp-commands/environment.json")
    assert entry is not None and entry.name == "webapp-commands-env"
    assert entry.write == ((regen_generated.PY, "tools/webapp_commands_env.py", "--write"),)
    assert entry.check == ((regen_generated.PY, "tools/webapp_commands_env.py", "--check"),)
    assert entry.fresh == f"tests/test_webapp_commands_env.py::{test_the_committed_environment_is_the_lean_generators_output.__name__}"


@pytest.fixture
def generator(tmp_path, monkeypatch):
    """Runs the generator with `flag` over a target under `tmp_path`, the Lean run replaced by `printed`."""
    target = tmp_path / "webapp-commands/environment.json"
    monkeypatch.setattr(webapp_commands_env, "TARGET", target)

    def run(flag: str, printed: str, returncode: int = 0) -> int:
        result = subprocess.CompletedProcess([], returncode, stdout=printed, stderr="lean failed\n")
        monkeypatch.setattr(webapp_commands_env.subprocess, "run", lambda *args, **kwargs: result)
        monkeypatch.setattr(sys, "argv", ["webapp_commands_env.py", flag])
        return webapp_commands_env.main()
    run.target = target
    return run


def test_write_stores_exactly_what_lean_printed(generator):
    """`--write` stores the printer's output, whatever it is: an `E_web` edit reaches the file with no hand copy."""
    data = json.loads(COMMITTED.read_text())
    data["environment"]["vocabulary"]["sorts"]["robot"] = {"description": "robot"}
    edited = json.dumps(data, indent=2)
    assert generator("--write", edited) == 0
    assert generator.target.read_text() == edited + "\n"
    assert generator("--check", edited) == 0


def test_check_refuses_any_other_file_and_a_failed_printer(generator):
    """`--check` passes only on the printer's output byte for byte: one sort removed, the lexicon dropped or a missing
    file fails it, and a printer failure is never a pass."""
    printed = COMMITTED.read_text().rstrip("\n")
    assert generator("--write", printed) == 0 and generator("--check", printed) == 0
    data = json.loads(printed)
    del data["environment"]["vocabulary"]["sorts"]["token"]
    generator.target.write_text(json.dumps(data, indent=2) + "\n")
    assert generator("--check", printed) == 1
    data = json.loads(printed)
    del data["lexicon"]
    generator.target.write_text(json.dumps(data, indent=2) + "\n")
    assert generator("--check", printed) == 1
    generator.target.unlink()
    assert generator("--check", printed) == 1
    assert generator("--write", printed) == 0
    assert generator("--check", printed, returncode=1) == 1
    assert generator("--write", "", returncode=1) == 1 and generator.target.read_text() == printed + "\n"
