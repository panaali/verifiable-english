"""relb-demo-cli: the release B demo (checklist item 5): ask.py, demo/install.sh and DEMO.md.

- ask.py on the demo profile prints exactly the expected-output block of DEMO.md (the block is read from DEMO.md).
- The demo profile given as flags is the same profile as the file; a file's `key` is never read.
- A profile with an unknown field, a bad date, an unknown benefit or a bad amount is refused before anything runs.
- DEMO.md's commands: the HTTPS clone of tag ve-elig-b1, and every repository path they name exists.
- install.sh, run against stub tools: installs only what is missing, then the three build commands in order,
  each step timed; a second run installs nothing; a missing C toolchain with no apt-get stops it.
"""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

import pytest

from tests import lean_routes

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "usecases" / "eligibility"
DEMO = HERE / "DEMO.md"
PROFILE = HERE / "demo" / "b15.json"
INSTALL = HERE / "demo" / "install.sh"
sys.path.insert(0, str(HERE))

import ask as A  # noqa: E402

LEAN = lean_routes.SERVICE.exists()


def demo_block():
    """The fenced block after DEMO.md's expected-output marker."""
    text = DEMO.read_text(encoding="utf-8")
    m = re.search(r"<!-- expected-output:[^>]*-->\n```text\n(.*?)^```$", text, re.S | re.M)
    assert m, "DEMO.md has no expected-output block"
    return m.group(1)


def sh_blocks():
    return re.findall(r"```sh\n(.*?)```", DEMO.read_text(encoding="utf-8"), re.S)


# --- ask.py -----------------------------------------------------------------------------------------

@pytest.mark.skipif(not LEAN, reason="the expected output includes the Lean check: needs the lake build")
def test_demo_output_matches_demo_md():
    cmd = [sys.executable, "usecases/eligibility/ask.py", "usecases/eligibility/demo/b15.json"]
    out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True).stdout
    assert out == demo_block()


def test_demo_block_answers():
    """The block's summary is the plan's expected answer (entitled, £200, not taken back, £200 kept),
    and it names the clauses the plan lists."""
    block = demo_block()
    assert block.startswith("Entitled: YES\nPayment: £200.00\nTaken back by HMRC: NO\nKept: £200.00\n\n")
    for clause in ("regulation 2(a)", "regulation 2(b)", "regulation 3(1)", "regulation 4(4)",
                   "section 7, “If your income is over £35,000”"):
        assert clause in block, clause
    assert block.count("the answer document was admitted.") == 4


def test_summary_without_lean_matches_block():
    """The answers do not depend on the Lean run (without Lean only the Lean lines differ)."""
    out = A.ask(A.build_profile(PROFILE), lean=False)
    block = demo_block()
    strip = lambda t: [line for line in t.splitlines() if not line.startswith("Lean check:")]
    assert strip(out) == strip(block)


def test_flags_give_the_file_profile():
    from_file = A.build_profile(PROFILE)
    from_flags = A.build_profile(birth="1955-03-14", scot_ni_from="2026-09-20", ew_from="2026-09-22")
    assert from_flags["applicant"] == from_file["applicant"]
    assert from_flags["housemate"] is from_file["housemate"] is None


def test_flags_override_file(tmp_path):
    p = A.build_profile(PROFILE, income="40000.00", benefits=["state_pension", "pension_credit"])
    assert p["applicant"]["income"] == "40000.00"
    assert p["applicant"]["benefits"] == ["state_pension", "pension_credit"]
    assert p["applicant"]["birth"] == "1955-03-14"


def test_key_is_never_read(tmp_path):
    case = json.loads(PROFILE.read_text(encoding="utf-8"))
    case["key"] = {"entitled": False, "amount": "300.00", "recovered": True, "kept": "0.00"}
    path = tmp_path / "keyed.json"
    path.write_text(json.dumps(case), encoding="utf-8")
    assert "key" not in A.build_profile(path)
    assert A.ask(A.build_profile(path), lean=False) == A.ask(A.build_profile(PROFILE), lean=False)


def test_income_over_limit_is_taken_back():
    out = A.ask(A.build_profile(PROFILE, income="40000.00"), lean=False)
    assert out.startswith("Entitled: YES\nPayment: £200.00\nTaken back by HMRC: YES\nKept: £0.00\n")


def test_not_entitled_summary():
    out = A.ask(A.build_profile(birth="1970-08-19"), lean=False)
    assert out.startswith("Entitled: NO\nPayment: not applicable (not entitled)\n"
                          "Taken back by HMRC: not applicable (not entitled)\nKept: not applicable (not entitled)\n")


@pytest.mark.parametrize("applicant, message", [
    ({"birth": "1955-03-14", "ew_frm": "2020-01-01"}, "unknown field(s) ew_frm"),
    ({"birth": "1955-3-14"}, "is not a date written YYYY-MM-DD"),
    ({"birth": "1955-02-30"}, "is not a date written YYYY-MM-DD"),
    ({"birth": "1955-03-14", "benefits": ["pension_credt"]}, "unknown benefits ['pension_credt']"),
    ({"birth": "1955-03-14", "income": "£40,000"}, "is not an amount in GBP"),
    ({"birth": "1955-03-14", "care": {"from": "2025-01-10", "to": "2026-12-01"}}, "applicant.care: fields"),
    ({"ew_from": "2020-01-01"}, "a birth date ('birth') is required"),
])
def test_bad_profile_refused(tmp_path, capsys, applicant, message):
    path = tmp_path / "bad.json"
    path.write_text(json.dumps({"applicant": applicant}), encoding="utf-8")
    assert A.main([str(path), "--no-lean"]) == 2
    err = capsys.readouterr()
    assert message in err.err and err.out == ""


def test_unknown_profile_field_and_bad_json(tmp_path, capsys):
    path = tmp_path / "bad.json"
    path.write_text(json.dumps({"applicant": {"birth": "1955-03-14"}, "partner": True}), encoding="utf-8")
    assert A.main([str(path), "--no-lean"]) == 2
    assert "unknown profile field(s) partner" in capsys.readouterr().err
    path.write_text("{", encoding="utf-8")
    assert A.main([str(path), "--no-lean"]) == 2
    assert "not valid JSON" in capsys.readouterr().err


def test_no_profile_is_a_usage_error():
    with pytest.raises(SystemExit) as exc:
        A.main([])
    assert exc.value.code == 2


# --- DEMO.md commands ---------------------------------------------------------------------------------

def test_demo_commands():
    blocks = sh_blocks()
    commands = "\n".join(blocks)
    assert "git clone --branch ve-elig-b1 https://github.com/panaali/verifiable-english.git ve && cd ve" in commands
    assert "git@" not in commands  # HTTPS only: a clean machine has no SSH key
    assert "sh usecases/eligibility/demo/install.sh" in commands
    assert "uv run python usecases/eligibility/ask.py usecases/eligibility/demo/b15.json" in commands
    for path in re.findall(r"usecases/eligibility/\S+\.(?:py|sh|json)", commands):
        assert (ROOT / path).is_file(), path


# --- install.sh against stub tools ---------------------------------------------------------------------

BASICS = ("sh", "env", "date", "dirname", "tail", "id", "mkdir", "cp")


def _stub(path, calls):
    path.write_text(f'#!/bin/sh\necho "{path.name} $*" >> "{calls}"\n', encoding="utf-8")
    path.chmod(0o755)


def _sandbox(tmp_path, tools):
    """A PATH with only the shell basics and stubs for `tools`; HOME and TMPDIR in tmp_path."""
    bindir, home, calls = tmp_path / "bin", tmp_path / "home", tmp_path / "calls"
    bindir.mkdir()
    home.mkdir()
    calls.write_text("", encoding="utf-8")
    for name in BASICS:
        found = shutil.which(name)
        assert found, name
        (bindir / name).symlink_to(found)
    for name in tools:
        _stub(bindir / name, calls)
    env = {"PATH": str(bindir), "HOME": str(home), "TMPDIR": str(tmp_path)}
    return env, calls


def _run_install(env):
    return subprocess.run(["sh", str(INSTALL)], env=env, capture_output=True, text=True)


def test_install_syntax():
    assert subprocess.run(["sh", "-n", str(INSTALL)]).returncode == 0


def test_install_all_present_runs_builds_only(tmp_path):
    env, calls = _sandbox(tmp_path, ["cc", "curl", "git", "uv", "elan", "rustup", "lake"])
    for attempt in (1, 2):  # a second run does the same: nothing installed, the builds run again
        calls.write_text("", encoding="utf-8")
        r = _run_install(env)
        assert r.returncode == 0, r.stderr
        lines = calls.read_text(encoding="utf-8").splitlines()
        assert not any(line.startswith(("curl", "apt-get", "sudo")) for line in lines), lines
        builds = [line for line in lines if line.startswith(("uv sync", "uv run", "lake"))]
        assert builds == ["uv sync --locked --inexact", "lake build", "uv run python tools/rust_build.py"]
        assert "rustup toolchain install" in lines
        timed = re.findall(r"^==> (.*): done in \d+ s$", r.stdout, re.M)
        assert len(timed) == 8, r.stdout
        assert re.search(r"^==> all steps done in \d+ s$", r.stdout, re.M)


def test_install_missing_uv_installs_it(tmp_path):
    env, calls = _sandbox(tmp_path, ["cc", "git", "elan", "rustup", "lake"])
    # curl stub: prints an installer that puts a uv stub in ~/.local/bin (where the real one goes)
    made = tmp_path / "uv-made"
    made.mkdir()
    _stub(made / "uv", calls)
    curl = Path(env["PATH"]) / "curl"
    curl.write_text(f'#!/bin/sh\necho "curl $*" >> "{calls}"\n'
                    f"echo 'mkdir -p \"$HOME/.local/bin\" && cp \"{made / 'uv'}\" \"$HOME/.local/bin/uv\"'\n",
                    encoding="utf-8")
    curl.chmod(0o755)
    r = _run_install(env)
    assert r.returncode == 0, r.stdout + r.stderr
    lines = calls.read_text(encoding="utf-8").splitlines()
    assert [line for line in lines if line.startswith("curl")] == ["curl -LsSf https://astral.sh/uv/install.sh"]
    assert "uv sync --locked --inexact" in lines and "uv run python tools/rust_build.py" in lines


def test_install_missing_compiler_without_apt_stops(tmp_path):
    env, calls = _sandbox(tmp_path, ["curl", "git", "uv", "elan", "rustup", "lake"])
    r = _run_install(env)
    assert r.returncode == 1
    assert "missing build-essential and no apt-get" in r.stderr
    assert calls.read_text(encoding="utf-8") == ""  # nothing built


def test_install_lake_failure_stops(tmp_path):
    env, calls = _sandbox(tmp_path, ["cc", "curl", "git", "uv", "elan", "rustup"])
    lake = Path(env["PATH"]) / "lake"
    lake.write_text('#!/bin/sh\necho "error: build failed"\nexit 1\n', encoding="utf-8")
    lake.chmod(0o755)
    r = _run_install(env)
    assert r.returncode == 1
    assert "lake build failed" in r.stderr
    assert "uv run python tools/rust_build.py" not in calls.read_text(encoding="utf-8")


def test_install_is_run_from_anywhere(tmp_path):
    """install.sh finds the repository root from its own path, so the cwd does not matter."""
    env, calls = _sandbox(tmp_path, ["cc", "curl", "git", "uv", "elan", "rustup", "lake"])
    r = subprocess.run(["sh", str(INSTALL)], env=env, cwd=tmp_path, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert os.path.isdir(ROOT / "lean")
