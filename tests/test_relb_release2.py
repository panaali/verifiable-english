"""relb-release-2: what a newcomer meets first in release ve-elig-b2 (the Winter Fuel Payment demo).

- The top-level README says what the release is near its top, points to DEMO.md and install.sh, and clones over
  HTTPS (branch ve-elig-b2); no SSH address anywhere.
- DEMO.md: the case count is the real count of cases.json; no "checklist item" opening; it clones ve-elig-b2 and
  says the Lean build takes 20 to 40 minutes, with a progress line every minute (tour revision 1126; it was silent).
- install.sh: rustup's "Cargo's bin directory in your PATH" message is not shown; a line before the Lean build says
  it takes 20 to 40 minutes and prints a line every minute.
- Build time: README, DEMO.md and install.sh say 20 to 40 minutes, never "about 20 minutes"; DEMO.md cites the
  measured range 1,259 to 2,376 seconds (the slowest first build seen was 2,376 s on GitHub's free machines).
- README "Try it locally": after the release's install.sh, Lean and Rust are in ~/.elan/bin and ~/.cargo/bin, so the
  section says to put those on PATH before its `lake build` and `rust_build.py` lines.
- install.sh's logs get a fresh name per run (mktemp), so a log another user left in the same temporary directory
  is never in the way; a failure still prints the log's path.
- No project-internal words (work-item names, review labels, "certificates", "document was admitted") in the printed
  output of both demo forms, in DEMO.md, or in the two READMEs.
- The printout's assumption about the rules' English wording gives the count results.json records.
"""
import json
from pathlib import Path
import re
import subprocess
import sys

import pytest

from tests.test_relb_demo_cli import INSTALL, _run_install, _sandbox, _stub, demo_block

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "usecases" / "eligibility"
README = ROOT / "README.md"
ELIG_README = HERE / "README.md"
DEMO = HERE / "DEMO.md"
PROFILE = HERE / "demo" / "b15.json"
sys.path.insert(0, str(HERE))

import ask as A  # noqa: E402

CLONE = "git clone --branch ve-elig-b2 https://github.com/panaali/verifiable-english.git ve && cd ve"

# Words a newcomer cannot know: work-item and review labels, and checker jargon (case-insensitive).
INSIDER = [r"w6a", r"relb", r"r7 recheck", r"finding c\b", r"mutant", r"certificat",
           r"documents? (?:was|were) admitted", r"answer documents? admitted", r"lean-admitted",
           r"admitted by lean", r"checklist item"]


def visible(markdown):
    """The text a reader sees: Markdown link targets and HTML comments dropped (file names stay out of it). The
    verbatim quote of `ve document check --help`'s CHECKED wording is dropped too: tests/test_kernel_closure.py
    requires the top-level README to quote it word for word (DRI 2026-11-11), and it names certificate verdicts."""
    from ve.document.cli import CHECKED_MEANS
    text = re.sub(r"<!--.*?-->", "", markdown.replace(CHECKED_MEANS, ""), flags=re.S)
    return re.sub(r"\]\([^)]*\)", "]", text)


def insider_hits(text):
    return sorted({m.group(0) for pat in INSIDER for m in re.finditer(pat, text, re.I)})


# --- top-level README ---------------------------------------------------------------------------------

def test_readme_names_the_release_near_the_top():
    text = README.read_text(encoding="utf-8")
    top = text[: len(text) // 4]
    assert "Winter Fuel Payment" in top and "ve-elig-b2" in top
    assert "usecases/eligibility/DEMO.md" in top and "usecases/eligibility/demo/install.sh" in top
    assert CLONE in top


def test_readme_clones_over_https_only():
    text = README.read_text(encoding="utf-8")
    assert "git@" not in text and "ssh://" not in text
    clones = re.findall(r"^git clone .*$", text, re.M)
    assert clones and all("https://github.com/panaali/verifiable-english.git" in c for c in clones), clones


# --- DEMO.md ------------------------------------------------------------------------------------------

def test_demo_case_count_is_cases_json():
    n = len(json.loads((HERE / "cases.json").read_text(encoding="utf-8"))["cases"])
    text = DEMO.read_text(encoding="utf-8")
    counts = re.findall(r"its (\d+) cases", text)
    assert counts == [str(n)], (counts, n)


def test_demo_opening_and_clone():
    text = DEMO.read_text(encoding="utf-8")
    assert "checklist item" not in text.lower()
    assert CLONE in "\n".join(re.findall(r"```sh\n(.*?)```", text, re.S))
    assert "ve-elig-b1" not in "\n".join(re.findall(r"```sh\n(.*?)```", text, re.S))
    assert re.search(r"20 to 40 minutes[^.]*progress line every minute", text), \
        "DEMO.md must say the Lean build takes 20 to 40 minutes, with a progress line every minute"


# --- install.sh -----------------------------------------------------------------------------------------

def test_install_hides_rustups_path_message(tmp_path):
    env, calls = _sandbox(tmp_path, ["cc", "git", "uv", "elan", "lake"])
    made = tmp_path / "rustup-made"
    made.mkdir()
    _stub(made / "rustup", calls)
    # curl stub: prints an installer that says what rustup-init says at its end, and puts a rustup stub in ~/.cargo/bin
    curl = Path(env["PATH"]) / "curl"
    curl.write_text(f'#!/bin/sh\necho "curl $*" >> "{calls}"\n'
                    "echo 'echo \"To get started you need Cargo'\"'\"'s bin directory ($HOME/.cargo/bin) in your PATH\"'\n"
                    f"echo 'mkdir -p \"$HOME/.cargo/bin\" && cp \"{made / 'rustup'}\" \"$HOME/.cargo/bin/rustup\"'\n",
                    encoding="utf-8")
    curl.chmod(0o755)
    r = _run_install(env)
    assert r.returncode == 0, r.stdout + r.stderr
    assert [line for line in calls.read_text(encoding="utf-8").splitlines() if line.startswith("curl")] \
        == ["curl -sSf https://sh.rustup.rs"]
    assert "Cargo's bin directory" not in r.stdout + r.stderr
    assert "rustup toolchain install" in calls.read_text(encoding="utf-8")


def test_install_failed_rustup_download_stops(tmp_path):
    """A failed download gives sh an empty script (exit 0): install.sh must still stop, saying rustup failed."""
    env, calls = _sandbox(tmp_path, ["cc", "git", "uv", "elan", "lake"])
    curl = Path(env["PATH"]) / "curl"
    curl.write_text('#!/bin/sh\necho "curl: (6) Could not resolve host: sh.rustup.rs" >&2\nexit 6\n', encoding="utf-8")
    curl.chmod(0o755)
    r = _run_install(env)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "rustup installed" not in r.stdout
    assert "rustup install failed" in r.stderr
    assert not any(line.startswith(("uv sync", "lake")) for line in calls.read_text(encoding="utf-8").splitlines())


def test_install_says_the_lean_build_is_long_and_silent(tmp_path):
    env, calls = _sandbox(tmp_path, ["cc", "curl", "git", "uv", "elan", "rustup", "lake"])
    r = _run_install(env)
    assert r.returncode == 0, r.stderr
    lines = r.stdout.splitlines()
    start = lines.index("==> lake build (Lean; the first build is the long one)")
    # tour revision 1126: the build is no longer silent; it prints a line every minute (test_relb_demo_cli.py)
    warn = [i for i, line in enumerate(lines) if "20 to 40 minutes" in line and "a line every minute" in line]
    assert warn and warn[0] == start + 1, lines  # printed right after the step's heading, before lake runs


# --- build time, Try it locally, install.sh log names (re-judge of ve-elig-b2) ----------------------------

def test_build_time_is_20_to_40_minutes():
    """The first Lean build was measured at 1,259 to 2,376 s; "about 20 minutes" made a healthy build look hung."""
    texts = {p.name: p.read_text(encoding="utf-8") for p in (README, DEMO, INSTALL)}
    for name, text in texts.items():
        assert "about 20 minutes" not in text, name
        assert "20 to 40 minutes" in text, name
    assert "measured 1,259 to 2,376 seconds" in texts["DEMO.md"]


def test_try_it_locally_puts_elan_and_cargo_on_path():
    text = README.read_text(encoding="utf-8")
    section = text.split("\n## Try it locally\n", 1)[1].split("\n## ", 1)[0]
    exports = [m for m in re.findall(r"export PATH=\"([^\"]*)\"", section)]
    assert any("$HOME/.elan/bin" in e and "$HOME/.cargo/bin" in e for e in exports), exports
    first_export = section.index("export PATH=")
    assert first_export < section.index("lake build") and first_export < section.index("rust_build.py")
    assert "install.sh" in section[:section.index("lake build")]


def _install_with_rustup_missing(env, calls, tmp_path):
    """Give the sandbox a curl whose installer puts a rustup stub in ~/.cargo/bin."""
    made = tmp_path / "rustup-made"
    made.mkdir(exist_ok=True)
    _stub(made / "rustup", calls)
    curl = Path(env["PATH"]) / "curl"
    curl.write_text(f'#!/bin/sh\necho "curl $*" >> "{calls}"\n'
                    f"echo 'mkdir -p \"$HOME/.cargo/bin\" && cp \"{made / 'rustup'}\" \"$HOME/.cargo/bin/rustup\"'\n",
                    encoding="utf-8")
    curl.chmod(0o755)


def test_install_logs_ignore_another_users_files(tmp_path):
    """The old fixed names are taken (a directory stands for a file another user owns): the install still runs,
    and a successful run leaves no log behind."""
    env, calls = _sandbox(tmp_path, ["cc", "git", "uv", "elan", "lake"])
    _install_with_rustup_missing(env, calls, tmp_path)
    for name in ("ve-demo-rustup-install.log", "ve-demo-lake-build.log"):
        (tmp_path / name).mkdir()
    r = _run_install(env)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "rustup installed" in r.stdout
    assert "uv run python tools/rust_build.py" in calls.read_text(encoding="utf-8")
    assert sorted(p.name for p in tmp_path.glob("ve-demo-*")) == ["ve-demo-lake-build.log", "ve-demo-rustup-install.log"]


def test_install_failed_lake_logs_are_new_files(tmp_path):
    """Two failing runs write two different logs, each in TMPDIR, each named in the error and holding lake's output."""
    env, calls = _sandbox(tmp_path, ["cc", "curl", "git", "uv", "elan", "rustup"])
    lake = Path(env["PATH"]) / "lake"
    lake.write_text('#!/bin/sh\necho "error: build failed"\nexit 1\n', encoding="utf-8")
    lake.chmod(0o755)
    logs = []
    for attempt in (1, 2):
        r = _run_install(env)
        assert r.returncode == 1, r.stdout + r.stderr
        m = re.search(r"lake build failed; full log: (\S+)$", r.stderr, re.M)
        assert m, r.stderr
        logs.append(Path(m.group(1)))
    assert logs[0] != logs[1]
    for log in logs:
        assert log.parent == tmp_path and log.name.startswith("ve-demo-lake-build")
        assert "error: build failed" in log.read_text(encoding="utf-8")
        assert log.stat().st_mode & 0o777 == 0o600  # made by mktemp, not a guessable shell name


# --- insider words --------------------------------------------------------------------------------------

def test_printed_demo_output_has_no_insider_words():
    """Both demo forms (the file and the flags), without Lean here; with Lean, the DEMO.md block (the expected
    output test_relb_demo_cli.py compares with the real run)."""
    by_file = A.ask(A.build_profile(PROFILE), lean=False)
    by_flags = A.ask(A.build_profile(birth="1955-03-14", scot_ni_from="2026-09-20", ew_from="2026-09-22"), lean=False)
    for name, text in (("file form", by_file), ("flag form", by_flags), ("DEMO.md block", demo_block())):
        assert insider_hits(text) == [], name


@pytest.mark.parametrize("path", [README, ELIG_README, DEMO], ids=["README.md", "eligibility README.md", "DEMO.md"])
def test_readmes_have_no_insider_words(path):
    assert insider_hits(visible(path.read_text(encoding="utf-8"))) == []


# --- the printout's count of checked English wordings ----------------------------------------------------

def test_printout_gives_the_english_count_results_json_records():
    english = json.loads((HERE / "results.json").read_text(encoding="utf-8"))["english"]
    line = f"In all, {english['rules_round_trip']} of the published translation's {english['rules']} rules have a checked English wording."
    out = A.ask(A.build_profile(PROFILE), lean=False)
    assert " ".join(out.split()).count(line) == 1
    assert line in " ".join(demo_block().split())
    assert "have no checked English wording" not in out  # every rule used here has one (results.json)
