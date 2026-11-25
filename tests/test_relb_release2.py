"""relb-release-2: what a newcomer meets first in release ve-elig-b2 (the Winter Fuel Payment demo).

- The top-level README says what the release is near its top, points to DEMO.md and install.sh, and clones over
  HTTPS (branch ve-elig-b2); no SSH address anywhere.
- DEMO.md: the case count is the real count of cases.json; no "checklist item" opening; it clones ve-elig-b2 and
  says the Lean build prints nothing for about 20 minutes.
- install.sh: rustup's "Cargo's bin directory in your PATH" message is not shown; a line before the Lean build says
  it takes about 20 minutes and prints nothing.
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
    assert re.search(r"prints nothing[^.]*about 20 minutes|about 20 minutes[^.]*prints nothing", text), \
        "DEMO.md must say the Lean build is silent for about 20 minutes"


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
    warn = [i for i, line in enumerate(lines) if "about 20 minutes" in line and "prints nothing" in line]
    assert warn and warn[0] == start + 1, lines  # printed right after the step's heading, before lake runs


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
