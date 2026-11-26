"""Stranger review of the public docs (2026-11-25): what a newcomer reading the README and the docs it links needs.

Findings S1 and S4-S10 of the stranger review: a licence, a runnable `ve document check`, a plain status paragraph,
the roadmap marked historical, no private operations paths in the entry docs, the pinned-source fetch command in the
use cases that need it, and a measured size for the full gate. The roadmap's account-directory and keys-file lines
are row relb-privacy-scrub's (tests/test_public_tree_privacy.py); this file does not test them.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

from subprocesses import HANG_TIMEOUT

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
ROADMAP = ROOT / "ROADMAP.md"
LICENSE = ROOT / "LICENSE"

# The docs the README links a newcomer to first (the stranger review's entry set).
ENTRY_DOCS = ("README.md", "docs/README.md", "ROADMAP.md", "VISION.md", "docs/ARCHITECTURE.md", "AGENTS.md",
              "usecases/agent-policy/README.md", "usecases/eligibility/README.md",
              "usecases/safety-framework/README.md", "usecases/anthropic-rsp/README.md",
              "usecases/openai-preparedness/README.md")
# Private operations paths: the operations repository and personal home directories.
PRIVATE_PATH = re.compile(r"manage-agents|/home/[a-z]|/Users/[A-Za-z]|~/code/")
# Roadmap lines owned by row relb-privacy-scrub (account directories, the keys file): it removes them. The
# "Lead's rules" row sits next to them, so editing it here would conflict with that row's deletion; it is left to
# row relb-privacy-paths (private paths, the next privacy step).
PRIVACY_ROW_LINE = re.compile(r"\.claude-|manage-agents/\.env|^\| Lead's rules \| `~/code/manage-agents/LEAD-PREFERENCES\.md` \|$")
# Use cases whose builder reads a pinned publisher text (usecases/pinned_sources.json).
PINNED = ("anthropic-rsp", "openai-preparedness", "safety-framework")


def readme():
    return README.read_text(encoding="utf-8")


def status_paragraph():
    section = readme().split("\n## Current status and limits\n", 1)[1]
    return section.strip().split("\n\n", 1)[0]


def test_readme_clones_over_https_only():
    assert "git@github.com:" not in readme()


EXAMPLE = "usecases/question-answering/group.ve.md"


def test_readme_shows_a_document_check_command():
    """S5: a runnable command on a small committed document, not only the meaning of its statuses."""
    m = re.search(r"^uv run python -m ve document check (\S+\.ve\.md)$", readme(), re.M)
    assert m, "README.md has no `ve document check` command line"
    assert m.group(1) == EXAMPLE
    assert (ROOT / EXAMPLE).stat().st_size < 5000, "the example should be small"


def test_readme_document_check_output_is_the_real_one():
    """S5: the README's excerpt of the report is what the command prints today."""
    run = subprocess.run([sys.executable, "-m", "ve", "document", "check", EXAMPLE], cwd=ROOT,
                         capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert run.returncode == 0, run.stdout + run.stderr
    coverage = json.loads(run.stdout)["coverage"]
    checked = coverage["bytes_by_status"]["CHECKED"]
    assert coverage["bytes_by_status"] == {"CHECKED": checked} and coverage["source_bytes"] == checked
    excerpt = (f'    "bytes_by_status": {{\n      "CHECKED": {checked}\n    }},\n'
               f'    "coverage_percent": {coverage["coverage_percent"]},\n')
    assert excerpt in readme()
    assert f"all {checked} bytes of its English text" in readme()


def test_try_it_locally_states_the_build_and_that_commands_need_it():
    """S3: the first build's length, and that every command waits for it."""
    section = readme().split("\n## Try it locally\n", 1)[1].split("\n## ", 1)[0]
    assert "can take a while" not in section
    before_commands = section.split("uv run python -m ve render", 1)[0]
    assert "20 to 40 minutes" in before_commands and "CheckerUnavailable" in before_commands


def test_readme_says_pytest_builds_the_native_checkers_first():
    """S4: the headline example's test file starts the native build; say so and how to skip it."""
    text = readme()
    small = text.split("\n## A small example\n", 1)[1].split("\n## ", 1)[0]
    assert "tests/test_natural.py" in small and "VE_NATIVE_PREBUILT=1" in small
    assert re.search(r"first builds the native Lean and Rust checkers.{0,80}20 to 40 minutes", small)
    testing = (ROOT / "docs/TESTING.md").read_text(encoding="utf-8")
    suite = testing.split("\n## The complete suite\n", 1)[1].split("\n```", 1)[0]
    assert "first builds the native" in suite and "VE_NATIVE_PREBUILT=1" in suite
    assert "assisted-formalisation.md" in small  # the same argument through the CLI


def test_status_paragraph_is_plain_and_matches_ownership():
    """S6: three plain sentences; the counts are the ownership table's."""
    para = status_paragraph()
    for word in ("soft-selected", "soft-conflict", "kb-10d", "NormDocument", "refute", "kernel theorem"):
        assert word not in para, word
    visible = re.sub(r"\]\([^)]*\)", "]", para)  # link targets hold dots
    assert len(re.findall(r"[.!?](?:\s|$)", visible)) == 3, visible
    assert "hand-written answer key" in para
    assert "docs/kernel/ownership.md" in para
    table = (ROOT / "docs/kernel/ownership.md").read_text(encoding="utf-8")
    rows = {key: (items, passes) for key, items, passes
            in re.findall(r"^\| ([a-z-]+) \| (\d+) \| \*\*(\d+)\*\* \|", table, re.M)}
    assert rows, "ownership.md has no per-key table"
    quoted = {"anthropic-rsp": "the RSP key's", "openai-preparedness": "Preparedness's",
              "safety-framework": "the safety framework's", "eligibility": "eligibility's",
              "agent-policy": "agent-policy"}
    for key, (items, passes) in rows.items():
        if key == "agent-policy":
            assert f"all {items} agent-policy answers" in para, key
            assert passes == "0"
        else:
            assert f"{passes} of {quoted[key]} {items}" in para, key


def test_roadmap_is_marked_historical():
    """S7: the old roadmap no longer calls itself the current status."""
    head = ROADMAP.read_text(encoding="utf-8").splitlines()[:6]
    visible = [re.sub(r"\[([^]]*)\]\([^)]*\)", r"\1", line) for line in head]
    assert any("Historical (2026-09-22). Current status: README.md." in line for line in visible), head


@pytest.mark.parametrize("name", ENTRY_DOCS)
def test_entry_docs_name_no_private_paths(name):
    """S8: a public doc points at no private operations path or personal home directory."""
    hits = [f"{name}:{i}" for i, line in enumerate((ROOT / name).read_text(encoding="utf-8").splitlines(), 1)
            if PRIVATE_PATH.search(line) and not (name == "ROADMAP.md" and PRIVACY_ROW_LINE.search(line))]
    assert hits == []


@pytest.mark.parametrize("case", PINNED)
def test_pinned_source_cases_name_the_fetch_command(case):
    """S9: the builder reads a publisher text that is not committed; the README says how to get it."""
    text = (ROOT / "usecases" / case / "README.md").read_text(encoding="utf-8")
    assert f"uv run python tools/fetch_pinned_sources.py --doc {case}" in text
    assert "prints that path" in text and "--home DIR" in text


def test_pinned_cases_are_the_pins():
    pins = json.loads((ROOT / "usecases/pinned_sources.json").read_text(encoding="utf-8"))["sources"]
    assert sorted(pins) == sorted(PINNED)


@pytest.mark.parametrize("path", [README, ROOT / "docs/verification-gate.md"], ids=["README.md", "verification-gate"])
def test_gate_size_is_stated(path):
    """S10: the full gate's measured wall time and memory, and the quick route."""
    text = path.read_text(encoding="utf-8")
    assert re.search(r"153 minutes", text) and re.search(r"20\.5 GB", text), path.name
    assert "select_tests.py" in text, path.name


# --- S1: the licence (reviews/dri-decisions-20261125-stranger-triage.md item 5: Apache-2.0) ------------------

def test_license_is_apache_2():
    text = LICENSE.read_text(encoding="utf-8")
    head = [line.strip() for line in text.lstrip().splitlines()[:3]]
    assert head[:3] == ["Apache License", "Version 2.0, January 2004", "http://www.apache.org/licenses/"], head
    assert "TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION" in text
    assert "END OF TERMS AND CONDITIONS" in text
    assert re.search(r"^   Copyright 2026 \S", text, re.M)
    assert "[name of copyright owner]" not in text


def test_license_has_no_email_address():
    assert "@" not in LICENSE.read_text(encoding="utf-8")


def test_pyproject_names_the_licence():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert project["license"] == "Apache-2.0"


def test_readme_names_the_licence():
    assert re.search(r"Licensed under the Apache License 2\.0; see \[LICENSE\]\(LICENSE\)\.", readme())
