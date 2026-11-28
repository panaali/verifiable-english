"""relb-demo-cli: the release B demo (checklist item 5): ask.py, demo/install.sh and DEMO.md.

- ask.py on the demo profile prints exactly the expected-output block of DEMO.md (the block is read from DEMO.md).
- The demo profile given as flags is the same profile as the file; a file's `key` is never read.
- A profile with an unknown field, a bad date, an unknown benefit or a bad amount is refused before anything runs.
- DEMO.md's commands: the HTTPS clone of release ve-elig-b2, and every repository path they name exists.
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
from subprocesses import HANG_TIMEOUT

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


GUIDANCE_LEGEND = ("(basis: guidance): the answer uses a clause of the GOV.UK guide “Winter Fuel Payment”, which is\n"
                   "  guidance on the law, not law.\n")


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
    assert block.startswith("Entitled: YES\nPayment: £200.00\nTaken back by HMRC: NO (basis: guidance)\n"
                            "Kept: £200.00 (basis: guidance)\n" + GUIDANCE_LEGEND + "\n")
    for clause in ("regulation 2(a)", "regulation 2(b)", "regulation 3(1)", "regulation 4(4)",
                   "section 7, “If your income is over £35,000”"):
        assert clause in block, clause
    assert block.count("; the answer was checked by Lean and accepted.") == 4


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
    assert out.startswith("Entitled: YES\nPayment: £200.00\nTaken back by HMRC: YES (basis: guidance)\n"
                          "Kept: £0.00 (basis: guidance)\n" + GUIDANCE_LEGEND + "\n")


def test_not_entitled_summary():
    out = A.ask(A.build_profile(birth="1970-08-19"), lean=False)
    assert out.startswith("Entitled: NO\nPayment: not applicable (not entitled)\n"
                          "Taken back by HMRC: not applicable (not entitled)\nKept: not applicable (not entitled)\n\n")
    assert "basis: guidance" not in out.lower()  # no answer, so no basis to mark (row tour-basis-guidance)


# --- the "basis: guidance" mark on the summary lines (row tour-basis-guidance, 2026-11-28) ---------------------------

def test_the_summary_marks_the_answers_that_use_the_guide_and_says_what_the_mark_means():
    """The HMRC lines (questions 3 and 4) use the GOV.UK guide's £35,000 test, so they carry the mark and the line under
    the summary says the guide is guidance, not law; the entitlement and the amount rest on the Regulations only."""
    lines = A.ask(A.build_profile(PROFILE), lean=False).split("\n")
    assert lines[:4] == ["Entitled: YES", "Payment: £200.00", "Taken back by HMRC: NO (basis: guidance)",
                         "Kept: £200.00 (basis: guidance)"]
    assert "\n".join(lines[4:7]) + "\n" == GUIDANCE_LEGEND + "\n"


def test_the_summary_mark_comes_from_the_sources_of_the_clauses(monkeypatch):
    """The mark is read from the data (which source each clause used comes from, and what that source is), not
    written per answer: were the guide law, no line would be marked and no legend printed; were the Regulations
    guidance, every answered line would be."""
    import explain as X
    monkeypatch.setitem(X.BASIS, "S2", "law")
    head = A.ask(A.build_profile(PROFILE), lean=False).split("\n\n")[0]
    assert head == "Entitled: YES\nPayment: £200.00\nTaken back by HMRC: NO\nKept: £200.00"
    monkeypatch.setitem(X.BASIS, "S1", "guidance")
    head = A.ask(A.build_profile(PROFILE), lean=False).split("\n\n")[0].split("\n")
    assert all(line.endswith(" (basis: guidance)") for line in head[:4])
    legend = " ".join(" ".join(head[4:]).split())
    assert legend == ("(basis: guidance): the answer uses a clause of the Social Fund Winter Fuel Payment Regulations "
                      "2025 (SI 2025/969), which is guidance on the law, not law.")  # the guide is still "law" here


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
    assert "git clone --branch ve-elig-b2 https://github.com/panaali/verifiable-english.git ve && cd ve" in commands
    assert "git@" not in commands  # HTTPS only: a clean machine has no SSH key
    assert "sh usecases/eligibility/demo/install.sh" in commands
    assert "uv run python usecases/eligibility/ask.py usecases/eligibility/demo/b15.json" in commands
    for path in re.findall(r"usecases/eligibility/\S+\.(?:py|sh|json)", commands):
        assert (ROOT / path).is_file(), path


# --- install.sh against stub tools ---------------------------------------------------------------------

BASICS = ("sh", "env", "date", "dirname", "tail", "id", "mkdir", "cp", "mktemp", "rm", "sleep", "grep")


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


def test_install_prints_a_line_every_minute_during_a_build(tmp_path):
    """tour revision 1126: a build prints a progress line every VE_PROGRESS_INTERVAL (60 by default) while it runs.
    No real time passes: `date` reads a clock file, and `sleep` moves that clock one second only while the stub
    `lake` is blocked on a FIFO; the second such sleep releases it, so exactly two progress lines are due."""
    env, calls = _sandbox(tmp_path, ["cc", "curl", "git", "uv", "elan", "rustup"])
    bindir, clock, waiting, fifo = tmp_path / "bin", tmp_path / "clock", tmp_path / "waiting", tmp_path / "fifo"
    clock.write_text("1000\n", encoding="utf-8")
    os.mkfifo(fifo)
    stubs = {
        "date": f'#!/bin/sh\nread t < "{clock}"; echo "$t"\n',
        "sleep": (f'#!/bin/sh\n[ -f "{waiting}" ] || exit 0\n'
                  f'read t < "{clock}"; n=$(( t + 1 )); echo "$n" > "{clock}"\n'
                  f'if [ "$n" -eq 1002 ]; then rm -f "{waiting}"; echo go > "{fifo}"; fi\n'),
        "lake": (f'#!/bin/sh\necho "lake $*" >> "{calls}"\necho "[3/7] Built X"\n'
                 f': > "{waiting}"\nread _ < "{fifo}"\n'),
    }
    for name, text in stubs.items():
        (bindir / name).unlink(missing_ok=True)
        (bindir / name).write_text(text, encoding="utf-8")
        (bindir / name).chmod(0o755)
    r = subprocess.run(["sh", str(INSTALL)], env={**env, "VE_PROGRESS_INTERVAL": "1"}, capture_output=True, text=True,
                       timeout=HANG_TIMEOUT)
    assert r.returncode == 0, r.stderr
    ticks = re.findall(r"^    lake build: still running, \d+ min so far, \[3/7\] files$", r.stdout, re.M)
    assert ticks == ["    lake build: still running, 0 min so far, [3/7] files"] * 2, r.stdout
    assert "still running" not in r.stdout.replace("    lake build: still running", ""), r.stdout


def test_install_without_sudo_prints_the_apt_line(tmp_path):
    """VE_NO_SUDO=1 (tour/install.sh sets it): a missing package stops the install with the command, no sudo run."""
    env, calls = _sandbox(tmp_path, ["curl", "git", "uv", "elan", "rustup", "lake", "apt-get", "sudo"])
    r = subprocess.run(["sh", str(INSTALL)], env={**env, "VE_NO_SUDO": "1"}, capture_output=True, text=True)
    assert r.returncode == 1
    assert "sudo apt-get update && sudo apt-get install -y build-essential ca-certificates" in r.stderr
    assert not [line for line in calls.read_text(encoding="utf-8").splitlines() if line.startswith(("sudo", "apt-get"))]


def test_the_wording_option_reads_each_clause_as_its_checked_wordings():
    """ask.py --wording prints the same summary and answers, with each rule's checked English wording in place of its
    hand-written gloss (tour stop 6 runs it so)."""
    import explain as X
    profile = A.build_profile(PROFILE)
    plain, worded = A.ask(profile, lean=False), A.ask(profile, lean=False, wording=True)
    data = X.explanation(profile, lean=False)
    assert worded == A.summary(data) + "\n" + X.render(data, wording=True, gloss=False)
    assert worded.split("\n\n", 1)[0] == plain.split("\n\n", 1)[0]
    assert "Read as:" in plain and "Read as:" not in worded
    assert "Read as (each rule's checked English wording, generated from the rule):" in worded
    out = subprocess.run([sys.executable, str(HERE / "ask.py"), "--no-lean", "--wording", str(PROFILE)],
                         capture_output=True, text=True, check=True, timeout=HANG_TIMEOUT).stdout
    assert out == worded
