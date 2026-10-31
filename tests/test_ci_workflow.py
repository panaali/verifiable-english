"""The security properties of the GitHub Actions workflows (.github/workflows/; gha-wf).

`ve-job.yml` runs VE compute jobs on GitHub (manage-agents reviews/gha-pilot-20261028.md, "Workflow" and
"Security"). Every workflow file, today's and any added later, must keep the trigger and secret rules:
it runs only on a push of a `ci-job/**` branch, its token starts with no permission, and no `run:` block
reads a secret or an event field (template injection). ve-job.yml must also keep its own shape: a
read-only `run` job that keeps no credentials and runs only in this repository, and a `publish` job, the
only one that writes, that pushes nothing but `ci-result/$JOB`, never forced.

gha-wf2: the publish job may also upload the run's branch Lean build to the existing release
`lean-branch-cache`. The token for that (`github.token`) reaches only that one step, which never fails the
result; its `gh` calls are `release view` and `release upload` of that release, never `--clobber`. The step's
own script is run here against a fake `gh`: a pack that is not exactly the head's lean tree, has a member
outside `pins.json` and `lake/build/` or that is not a plain file or directory, is over a cap, carries a
secret or a seal for another tree, platform or toolchain is refused and never uploaded.

actions-gate-x86: a sharded gate builds Lean once. A shard's `run` job may download the artifact `lean-build`
of exactly the run its job.json names (`lean_from`), with a second, read-only token (`actions: read`) that
reaches that one download step only; the download never fails the run. Its check step hands the pack to
job.sh only when it is one regular file named for the head's lean tree with the sha256 job.json names; any
other case is said and the shard builds cold. The build job's job.json says `"lean_publish": false`: its pack
is checked as any other and its sha256 recorded (status `checked`), but nothing reaches gh.

The files are read as text by a small reader of the YAML they use (PyYAML is not in the environment).
It fails closed: tabs, anchors, aliases, tags, merge keys, quoted or duplicate keys and lines it cannot
place are refused, so a rule cannot be dodged by writing the same thing another way.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import io
import json
import os
import re
import shlex
import subprocess
import tarfile
import textwrap

import pytest

from tests.subprocesses import HANG_TIMEOUT

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github/workflows"
VE_JOB = WORKFLOWS / "ve-job.yml"
REPOSITORY = "panaali/verifiable-english"
TOP_KEYS = {"name", "run-name", "on", "permissions", "concurrency", "env", "defaults", "jobs"}
# Events that would run the workflow on someone else's action, on a timer or by hand.
FORBIDDEN_EVENTS = {"pull_request", "pull_request_target", "workflow_run", "workflow_dispatch", "schedule",
                    "issue_comment", "repository_dispatch"}
MAX_TIMEOUT_MINUTES = 120
PINNED = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_./-]+@[0-9a-f]{40}")
EXPRESSION = re.compile(r"\$\{\{(.*?)\}\}", re.S)
# Contexts whose values the pusher of a branch or the author of an event chooses.
UNTRUSTED = re.compile(r"\bgithub\s*\.\s*(event|head_ref)\b")
GIT_PUSH = re.compile(r"\bgit\b(?:\s+-c\s+\S+)*\s+push\b([^;&|\n]*)")
PUBLISH_PUSH = ["origin", "HEAD:refs/heads/ci-result/$JOB"]
ASSET_STEP = "lean-build asset"
ASSET_RELEASE = "lean-branch-cache"
LEAN_FROM_STEP = "lean-from download"
LEAN_FROM_CHECK = "lean-from check"
TOKEN = "${{ github.token }}"
GH_CALL = re.compile(r"(?<![\w-])gh\s+([^\n|;&)]*)")
GH_ALLOWED = re.compile(r'release (view|upload) "\$REL" [^\n]*')
KEY = re.compile(r"([A-Za-z0-9_-]+):(?:\s+(.*))?")
BLOCK_SCALAR = re.compile(r"[|>][-+]?")


class Unsupported(AssertionError):
    """YAML this reader does not take; refused rather than guessed."""


@dataclass
class Line:
    indent: int
    text: str            # the content, comment removed
    number: int
    block: str | None    # the text of a block scalar (`key: |`) that this line opens


def uncomment(line: str) -> str:
    """`line` without a trailing comment (a `#` after a space, outside quotes)."""
    quote = None
    for i, char in enumerate(line):
        if quote:
            quote = None if char == quote else quote
        elif char in "'\"":
            quote = char
        elif char == "#" and (i == 0 or line[i - 1] in " \t"):
            return line[:i].rstrip()
    return line.rstrip()


def indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def lines(text: str) -> list[Line]:
    raw = text.split("\n")
    found, i = [], 0
    while i < len(raw):
        line = raw[i]
        if "\t" in line:
            raise Unsupported(f"line {i + 1}: a tab")
        content = uncomment(line)
        if not content.strip():
            i += 1
            continue
        indent = indent_of(content)
        content = content.strip()
        column = indent
        rest = content
        while rest.startswith("- "):  # a sequence item: its key starts after the dash
            column += 2 + indent_of(rest[2:])
            rest = rest[2:].lstrip(" ")
        key = KEY.fullmatch(rest)
        if key and key.group(2) and BLOCK_SCALAR.fullmatch(key.group(2)):
            number, block, i = i + 1, [], i + 1
            while i < len(raw) and (not raw[i].strip() or indent_of(raw[i]) > column):
                block.append(raw[i])
                i += 1
            found.append(Line(indent, content, number, "\n".join(block)))
            continue
        found.append(Line(indent, content, i + 1, None))
        i += 1
    return found


def scalar(text: str, number: int) -> str:
    if text[:1] in "&*!" or text.startswith("<<"):
        raise Unsupported(f"line {number}: an anchor, alias, tag or merge key")
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "'\"":
        return text[1:-1]
    return text


def parse_value(items: list[Line], pos: int, indent: int):
    """The value whose first line is items[pos], at `indent`; returns (value, next position)."""
    if items[pos].text == "-" or items[pos].text.startswith("- "):
        return parse_sequence(items, pos, indent)
    return parse_mapping(items, pos, indent)


def parse_sequence(items: list[Line], pos: int, indent: int):
    found = []
    while pos < len(items) and items[pos].indent == indent and items[pos].text.startswith("- "):
        line = items[pos]
        rest = line.text[2:]
        column = indent + 2 + indent_of(rest)
        rest = rest.strip()
        if KEY.fullmatch(rest) or rest.startswith("- "):
            items[pos] = Line(column, rest, line.number, line.block)
            value, pos = parse_value(items, pos, column)
        else:
            value, pos = scalar(rest, line.number), pos + 1
        found.append(value)
    return found, pos


def parse_mapping(items: list[Line], pos: int, indent: int):
    found = {}
    while pos < len(items) and items[pos].indent == indent and not items[pos].text.startswith("- "):
        line = items[pos]
        key = KEY.fullmatch(line.text)
        if not key:
            raise Unsupported(f"line {line.number}: not a plain `key: value` ({line.text!r})")
        name, text = key.group(1), key.group(2)
        if name in found:
            raise Unsupported(f"line {line.number}: duplicate key {name!r}")
        pos += 1
        if line.block is not None:
            value = line.block
        elif text:
            value = scalar(text, line.number)
        elif pos < len(items) and (items[pos].indent > indent
                                   or (items[pos].indent == indent and items[pos].text.startswith("- "))):
            value, pos = parse_value(items, pos, items[pos].indent)
        else:
            value = None
        found[name] = value
    return found, pos


def parse(text: str) -> dict:
    items = lines(text)
    if not items or items[0].indent != 0:
        raise Unsupported("the file does not start with a top-level key")
    document, pos = parse_mapping(items, 0, 0)
    if pos != len(items):
        raise Unsupported(f"line {items[pos].number}: cannot place {items[pos].text!r}")
    return document


def walk(value, path=()):
    """Every (path, key, value) of a parsed document, depth first."""
    if isinstance(value, dict):
        for key, child in value.items():
            yield path, key, child
            yield from walk(child, (*path, key))
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from walk(child, (*path, i))


def flow_list(value) -> list[str]:
    """A list written `['a', 'b']` or as a block sequence."""
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str) and value.startswith("[") and value.endswith("]"):
        return [scalar(item.strip(), 0) for item in value[1:-1].split(",") if item.strip()]
    raise AssertionError(f"not a list: {value!r}")


def permissions(value, where: str) -> dict:
    if value is None or value == "{}":
        return {}
    assert isinstance(value, dict), f"{where}: permissions must be a mapping, not {value!r}"
    return value


def steps(job: dict) -> list[dict]:
    found = job.get("steps") or []
    assert isinstance(found, list) and all(isinstance(step, dict) for step in found)
    return found


def run_blocks(document: dict) -> list[tuple[str, str]]:
    return [(job_name, step["run"]) for job_name, job in document["jobs"].items()
            for step in steps(job) if "run" in step]


def check_trigger(document: dict) -> None:
    assert set(document) <= TOP_KEYS, f"unexpected top-level keys {sorted(set(document) - TOP_KEYS)}"
    on = document.get("on")
    # Every key and every word of a value, so a flow form (`on: [push, schedule]`) is seen too.
    keys = {key for _, key, _ in walk(on)} | {word for _, _, value in walk({"on": on}) if isinstance(value, str)
                                             for word in re.findall(r"[A-Za-z_]+", value)}
    assert not keys & FORBIDDEN_EVENTS, f"forbidden triggers {sorted(keys & FORBIDDEN_EVENTS)}"
    assert isinstance(on, dict) and set(on) == {"push"}, f"the only trigger must be push, not {on!r}"
    push = on["push"]
    assert isinstance(push, dict) and set(push) == {"branches"}, f"push must name only branches: {push!r}"
    assert flow_list(push["branches"]) == ["ci-job/**"], push["branches"]


def check_permissions(document: dict, writer: tuple[str, str] | None) -> None:
    """Top-level `permissions: {}`; a job may write only as `writer` (job, scope) allows."""
    assert "permissions" in document and permissions(document["permissions"], "top level") == {}, \
        f"top-level permissions must be {{}}, not {document.get('permissions')!r}"
    for name, job in document["jobs"].items():
        for scope, level in permissions(job.get("permissions"), name).items():
            assert level in ("read", "write", "none"), f"{name}: {scope}: {level!r}"
            assert level != "write" or (name, scope) == writer, f"{name} may not write {scope}"


def check_secrets(document: dict, text: str) -> None:
    assert not [key for _, key, _ in walk(document) if key == "secrets"], "a `secrets:` key"
    assert not [e for e in EXPRESSION.findall(text) if "secrets" in e], "an expression reads secrets"
    for job, block in run_blocks(document):
        assert "secrets." not in block, f"{job}: a run block names secrets."
        injected = [e for e in EXPRESSION.findall(block) if UNTRUSTED.search(e)]
        assert not injected, f"{job}: a run block expands an event field {injected}"


def check_pins(document: dict, text: str) -> None:
    uses = [value for _, key, value in walk(document) if key == "uses"]
    written = re.findall(r"^\s*(?:-\s+)?uses:", text, re.M)
    assert uses and len(uses) == len(written), "a `uses:` the reader did not place"
    for value in uses:
        assert isinstance(value, str) and PINNED.fullmatch(value), f"not pinned by commit: {value!r}"


def check_timeouts(document: dict) -> None:
    jobs = document["jobs"]
    assert isinstance(jobs, dict) and jobs
    for name, job in jobs.items():
        minutes = job.get("timeout-minutes")
        assert minutes is not None and re.fullmatch(r"[0-9]+", minutes), f"{name}: timeout-minutes {minutes!r}"
        assert 1 <= int(minutes) <= MAX_TIMEOUT_MINUTES, f"{name}: timeout-minutes {minutes}"


def check_workflow(text: str) -> None:
    """The rules every workflow file keeps."""
    document = parse(text)
    check_trigger(document)
    check_permissions(document, None)
    check_secrets(document, text)
    check_pins(document, text)
    check_timeouts(document)


def check_ve_job(text: str) -> None:
    """ve-job.yml: the common rules (its `publish` job may write contents), then its own shape."""
    document = parse(text)
    check_trigger(document)
    check_permissions(document, ("publish", "contents"))
    check_secrets(document, text)
    check_pins(document, text)
    check_timeouts(document)
    jobs = document["jobs"]
    assert {"run", "publish"} <= set(jobs), sorted(jobs)
    run, publish = jobs["run"], jobs["publish"]
    assert permissions(run.get("permissions"), "run") == {"contents": "read", "actions": "read"}, run.get("permissions")
    assert permissions(publish.get("permissions"), "publish") == {"contents": "write"}
    assert run.get("if") == f"github.repository == '{REPOSITORY}'", f"run is not guarded: {run.get('if')!r}"
    checkouts = [step for step in steps(run) if step.get("uses", "").startswith("actions/checkout@")]
    assert checkouts, "run has no checkout"
    for step in checkouts:
        assert (step.get("with") or {}).get("persist-credentials") == "false", "run keeps its credentials"
    publish_pushes = []
    for name, block in run_blocks(document):
        pushes = [shlex.split(args) for args in GIT_PUSH.findall(block)]
        if name != "publish":
            assert not pushes, f"{name} pushes"
            assert not GH_CALL.findall(block), f"{name} calls gh"
            continue
        publish_pushes += pushes
        for args in GH_CALL.findall(block):
            assert GH_ALLOWED.fullmatch(args.strip()) and "--clobber" not in args, f"publish calls gh {args.strip()}"
        assert "api.github.com" not in block and "uploads.github.com" not in block, "publish calls the GitHub API"
    assert publish_pushes, "publish pushes nothing"
    for args in publish_pushes:
        assert [arg for arg in args if arg != "-q"] == PUBLISH_PUSH, f"publish pushes {args}"
    check_tokens(text)
    check_asset_step(publish)
    check_lean_from_step(run)


def check_tokens(text: str) -> None:
    """github.token appears twice: the publish job's lean-build upload and the run job's lean-from download."""
    tokens = [e for e in EXPRESSION.findall(text) if "token" in e.lower()]
    assert len(tokens) == 2 and text.count(TOKEN) == 2, f"github.token is used {len(tokens)} times"


def check_lean_from_step(run: dict) -> None:
    """The run job's token (read-only) reaches one step only: the download of the artifact lean-build of the
    run job.json names, in this repository, which never fails the run."""
    holders = [step for step in steps(run) if TOKEN in json.dumps(step)]
    assert len(holders) == 1, f"github.token reaches {len(holders)} steps of run"
    step = holders[0]
    assert step.get("name") == LEAN_FROM_STEP and step.get("uses", "").startswith("actions/download-artifact@"), \
        f"the run job's github.token is not only the {LEAN_FROM_STEP} step's"
    assert step.get("with") == {"name": "lean-build", "path": "${{ runner.temp }}/lean-from",
                                "run-id": "${{ steps.job.outputs.lean_run }}", "github-token": TOKEN}, \
        f"{LEAN_FROM_STEP}: downloads something else: {step.get('with')!r}"
    assert step.get("if") == "steps.job.outputs.lean_run != ''", f"{LEAN_FROM_STEP}: runs without lean_from"
    assert step.get("continue-on-error") == "true", f"{LEAN_FROM_STEP}: may fail the run (no continue-on-error)"
    assert "env" not in step, f"{LEAN_FROM_STEP}: has an env"


def check_asset_step(publish: dict) -> None:
    """The write token reaches one step only: the lean-build upload, which never fails the result and
    writes only to the existing release lean-branch-cache."""
    named = [step for step in steps(publish) if step.get("name") == ASSET_STEP]
    assert len(named) == 1, f"publish has {len(named)} {ASSET_STEP!r} steps"
    step = named[0]
    assert step.get("env") == {"GH_TOKEN": TOKEN, "LEAN_PUBLISH": "${{ needs.run.outputs.lean_publish }}"}, \
        f"github.token is not only the {ASSET_STEP} step's GH_TOKEN"
    for other in steps(publish):
        if "lean-build" in str(other.get("with", {}).get("name", "")) or other is step:
            assert other.get("continue-on-error") == "true", f"{ASSET_STEP}: may fail the result (no continue-on-error)"
    assert f"REL={ASSET_RELEASE};" in step["run"], f"{ASSET_STEP} does not write to {ASSET_RELEASE}"


def workflow_files() -> list[Path]:
    return sorted(path for path in WORKFLOWS.rglob("*") if path.is_file())


def test_ve_job_keeps_its_security_properties():
    check_ve_job(VE_JOB.read_text())


@pytest.mark.parametrize("path", workflow_files(), ids=lambda path: path.relative_to(ROOT).as_posix())
def test_every_workflow_keeps_the_trigger_and_secret_rules(path):
    assert path.suffix in (".yml", ".yaml"), f"{path.name}: not a workflow file"
    if path == VE_JOB:
        check_ve_job(path.read_text())
    else:
        check_workflow(path.read_text())


# One seeded bug per rule, applied to the real file: each must be refused, naming the rule it breaks.
SEEDED = [
    ("pull_request", "    branches: ['ci-job/**']\n", "    branches: ['ci-job/**']\n  pull_request:\n",
     "forbidden triggers"),
    ("dispatch", "on:\n  push:\n", "on:\n  workflow_dispatch:\n  push:\n", "forbidden triggers"),
    ("tags", "    branches: ['ci-job/**']\n", "    branches: ['ci-job/**']\n    tags: ['v*']\n",
     "push must name only branches"),
    ("other branch", "branches: ['ci-job/**']", "branches: ['ci-job/**', 'main']", "ci-job/**"),
    ("quoted on", "\non:\n", "\n'on':\n", "not a plain"),
    ("top write-all", "permissions: {}\nconcurrency", "permissions: write-all\nconcurrency", "permissions must be a mapping"),
    ("actions write", "      actions: read\n", "      actions: write\n", "run may not write actions"),
    ("run writes", "      contents: read\n", "      contents: write\n", "run may not write contents"),
    ("publish packages", "      contents: write\n", "      contents: write\n      packages: write\n",
     "publish may not write packages"),
    ("secret in run", "          set -euo pipefail\n          D=",
     "          set -euo pipefail\n          echo $TOKEN ${{ secrets.TOKEN }}\n          D=", "expression reads secrets"),
    ("event in run", "          set -euo pipefail\n          D=",
     "          set -euo pipefail\n          echo ${{ github.event.head_commit.message }}\n          D=",
     "expands an event field"),
    ("tag pin", "actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5", "actions/checkout@v4", "not pinned"),
    ("timeout", "timeout-minutes: 15", "timeout-minutes: 600", "timeout-minutes 600"),
    ("no timeout", "    timeout-minutes: 15\n", "", "publish: timeout-minutes None"),
    ("credentials", "          persist-credentials: false\n", "", "run keeps its credentials"),
    ("no guard", "    if: github.repository == 'panaali/verifiable-english'\n", "", "run is not guarded"),
    ("force", 'git push -q origin "HEAD:', 'git push -q --force origin "HEAD:', "publish pushes"),
    ("-f", 'git push -q origin "HEAD:', 'git push -f -q origin "HEAD:', "publish pushes"),
    ("+refspec", '"HEAD:refs/heads/ci-result/$JOB" ||', '"+HEAD:refs/heads/ci-result/$JOB" ||', "publish pushes"),
    ("main", '"HEAD:refs/heads/ci-result/$JOB" ||', '"HEAD:refs/heads/main" ||', "publish pushes"),
    ("alias", "\n  run:\n", "\n  run: &job\n", "anchor"),
    ("token in run", "          LEAN_ASSET: ${{ steps.job.outputs.lean_asset }}\n",
     "          LEAN_ASSET: ${{ steps.job.outputs.lean_asset }}\n          T: ${{ github.token }}\n", "github.token is used 3"),
    ("token in a run block", "          set -uo pipefail\n          O=$RUNNER_TEMP/out;",
     "          set -uo pipefail\n          echo ${{ github.token }}\n          O=$RUNNER_TEMP/out;", "github.token is used 3"),
    ("token moved", "          GH_TOKEN: ${{ github.token }}\n", "          TOKEN: ${{ github.token }}\n", "only the lean-build"),
    ("clobber", 'gh release upload "$REL" "$A/$name"', 'gh release upload "$REL" "$A/$name" --clobber', "publish calls gh"),
    ("create", '          up=$(gh release', '          gh release create "$REL" --repo x\n          up=$(gh release', "publish calls gh"),
    ("delete", '          up=$(gh release', '          gh release delete-asset "$REL" "$name" -y\n          up=$(gh release',
     "publish calls gh"),
    ("gh api", '          up=$(gh release', '          gh api -X DELETE repos/x/releases/assets/1\n          up=$(gh release',
     "publish calls gh"),
    ("curl api", '          up=$(gh release', '          curl -X DELETE https://api.github.com/repos/x\n          up=$(gh release',
     "calls the GitHub API"),
    ("gh in run", '          [ "$LEAN_ASSET" != 1 ]', '          gh release list\n          [ "$LEAN_ASSET" != 1 ]', "run calls gh"),
    ("other release", "REL=lean-branch-cache;", "REL=lean-cache;", "does not write to lean-branch-cache"),
    ("may fail", "        continue-on-error: true\n        env:\n", "        env:\n", "may fail the result"),
    ("lean-from repository", "          run-id: ${{ steps.job.outputs.lean_run }}\n",
     "          run-id: ${{ steps.job.outputs.lean_run }}\n          repository: someone/else\n", "downloads something else"),
    ("lean-from another artifact", "          name: lean-build\n          path: ${{ runner.temp }}/lean-from\n",
     "          name: out\n          path: ${{ runner.temp }}/lean-from\n", "downloads something else"),
    ("lean-from may fail", "        continue-on-error: true\n        with:\n          name: lean-build\n          path: ${{ runner.temp }}/lean-from",
     "        with:\n          name: lean-build\n          path: ${{ runner.temp }}/lean-from", "may fail the run"),
    ("lean-from always", "        if: steps.job.outputs.lean_run != ''\n        uses:", "        uses:", "runs without lean_from"),
    ("token moved in run", "          github-token: ${{ github.token }}\n", "",
     "github.token is used 1"),
    ("token to the check step",
     "          github-token: ${{ github.token }}\n      - id: leanfrom\n        name: lean-from check\n"
     "        if: steps.job.outputs.lean_run != ''\n        env:\n",
     "      - id: leanfrom\n        name: lean-from check\n        if: steps.job.outputs.lean_run != ''\n        env:\n"
     "          T: ${{ github.token }}\n", "not only the lean-from download step's"),
    ("download may fail", "        continue-on-error: true\n        uses: actions/download-artifact",
     "        uses: actions/download-artifact", "may fail the result"),
]


@pytest.mark.parametrize("name, old, new, message", SEEDED, ids=[row[0] for row in SEEDED])
def test_each_rule_refuses_its_seeded_bug(name, old, new, message):
    text = VE_JOB.read_text()
    assert text.count(old) >= 1, f"{name}: the seeded edit no longer applies"
    with pytest.raises(AssertionError, match=re.escape(message)):
        check_ve_job(text.replace(old, new, 1))


def test_a_new_workflow_file_keeps_the_common_rules():
    """Any other workflow is held to the trigger, permission, secret, pin and timeout rules, with no
    writer at all; the ve-job shape rules are ve-job.yml's own."""
    text = VE_JOB.read_text()
    with pytest.raises(AssertionError, match="publish may not write contents"):
        check_workflow(text)
    reader = text.replace("      contents: write\n", "      contents: read\n")
    check_workflow(reader)
    with pytest.raises(AssertionError, match="forbidden triggers"):
        check_workflow(reader.replace("on:\n  push:\n", "on:\n  schedule:\n  push:\n"))


# --- the lean-build asset step's own script, run against a fake `gh` (gha-wf2)
LEAN_VERSION = "Lean (version 4.24.0, x86_64-unknown-linux-gnu, commit 0123abcd, Release)"
FAKE_GH = """#!/bin/bash
printf '%s\\n' "$*" >> "$FAKE_GH_LOG"
case $1-$2 in
  release-view) [ "${FAKE_GH_VIEW:-ok}" = ok ] || { echo "$FAKE_GH_VIEW" >&2; exit 1; }; printf '%s\\n' $FAKE_GH_ASSETS;;
  release-upload) [ "${FAKE_GH_UPLOAD:-ok}" = ok ] || { echo "$FAKE_GH_UPLOAD" >&2; exit 1; };;
  *) exit 2;;
esac
"""


def asset_script() -> str:
    publish = parse(VE_JOB.read_text())["jobs"]["publish"]
    # The reader keeps a block scalar's indentation; bash needs the heredoc's PY at column 0, as YAML gives it.
    return textwrap.dedent(next(step["run"] for step in steps(publish) if step.get("name") == ASSET_STEP))


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd, check=True,
                          capture_output=True, text=True, timeout=HANG_TIMEOUT).stdout.strip()


def head_checkout(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "head"
    (repo / "lean").mkdir(parents=True)
    (repo / "lean/lean-toolchain").write_text("leanprover/lean4:v4.24.0\n")
    (repo / "lean/VE.lean").write_text("def x := 1\n")
    git(repo, "init", "-q")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "head")
    return repo, git(repo, "rev-parse", "HEAD:lean")


def seal(tree: str, **changes) -> bytes:
    key = {"git_lean_tree": tree, "platform": {"system": "Linux", "machine": "x86_64"},
           "toolchain": {"lean": LEAN_VERSION}}
    key.update(changes)
    return json.dumps({"format": 1, "key": key}).encode()


def pack(path: Path, members: list[tuple[str, object]]) -> None:
    """members: (name, bytes) a file, (name, "dir"), (name, "symlink"), (name, "hardlink")."""
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as tar:
        for name, body in members:
            info = tarfile.TarInfo(name)
            if body == "dir":
                info.type = tarfile.DIRTYPE
                tar.addfile(info)
            elif body in ("symlink", "hardlink"):
                info.type = tarfile.SYMTYPE if body == "symlink" else tarfile.LNKTYPE
                info.linkname = "lake/build/lib/a.olean"
                tar.addfile(info)
            else:
                info.size = len(body)
                tar.addfile(info, io.BytesIO(body))
    subprocess.run(["zstd", "-q", "-o", str(path)], input=raw.getvalue(), check=True, timeout=HANG_TIMEOUT)


def good_members(tree: str) -> list[tuple[str, object]]:
    return [("pins.json", seal(tree)), ("lake", "dir"), ("lake/build", "dir"), ("lake/build/lib", "dir"),
            ("lake/build/lib/a.olean", b"olean" * 100), ("lake/build/bin/ve_service", b"\x7fELF" + b"0" * 64)]


def run_asset_step(tmp_path: Path, members=None, *, name=None, extra=(), script=None, raw=None, publish="", **gh) -> dict:
    repo, tree = head_checkout(tmp_path)
    rt = tmp_path / "rt"
    (rt / "out").mkdir(parents=True)
    (rt / "lean-build").mkdir()
    target = rt / "lean-build" / (name or f"lean-build-{tree[:12]}.tar.zst")
    if raw is not None:
        target.write_bytes(raw)
    else:
        pack(target, good_members(tree) if members is None else members(tree))
    for extra_name in extra:
        (rt / "lean-build" / extra_name).write_bytes(b"x")
    fake = tmp_path / "bin"
    fake.mkdir()
    (fake / "gh").write_text(FAKE_GH)
    (fake / "gh").chmod(0o755)
    log = tmp_path / "gh.log"
    env = {**{k: v for k, v in os.environ.items() if not k.startswith(("GH_", "GITHUB_", "FAKE_GH"))},
           "PATH": f"{fake}{os.pathsep}{os.environ['PATH']}", "RUNNER_TEMP": str(rt), "GH_TOKEN": "not-a-token",
           "GITHUB_REPOSITORY": REPOSITORY, "FAKE_GH_LOG": str(log), "LEAN_PUBLISH": publish,
           **{f"FAKE_GH_{k.upper()}": v for k, v in gh.items()}}
    done = subprocess.run(["bash", "-c", script or asset_script()], cwd=repo, env=env, capture_output=True, text=True,
                          timeout=HANG_TIMEOUT)
    assert done.returncode == 0, f"the step failed the result: {done.stdout}{done.stderr}"
    record = json.loads((rt / "out/lean-build-asset.json").read_text())
    record["calls"] = log.read_text().splitlines() if log.exists() else []
    record["pack"] = target
    record["tree"] = tree
    return record


def test_the_publish_job_uploads_a_checked_branch_build(tmp_path):
    record = run_asset_step(tmp_path)
    assert record["status"] == "uploaded", record
    assert record["key"] == record["tree"] and record["name"] == f"lean-build-{record['tree'][:12]}.tar.zst"
    assert record["sha256"] == hashlib.sha256(record["pack"].read_bytes()).hexdigest()
    assert record["bytes"] == str(record["pack"].stat().st_size) and record["release"] == ASSET_RELEASE
    assert [call.split()[:3] for call in record["calls"]] == [["release", "view", ASSET_RELEASE],
                                                              ["release", "upload", ASSET_RELEASE]]
    assert record["calls"][1].split()[3] == str(record["pack"]) and "--clobber" not in record["calls"][1]


def test_an_asset_already_on_the_release_is_kept(tmp_path):
    record = run_asset_step(tmp_path, assets=f"other.tar.zst lean-build-{head_checkout(tmp_path / 'x')[1][:12]}.tar.zst")
    assert record["status"] == "exists", record
    assert [call.split()[1] for call in record["calls"]] == ["view"], "an existing asset was uploaded again"


@pytest.mark.parametrize("view, upload, status", [
    ("release not found", "ok", "no-release"),
    ("HTTP 502: Bad Gateway", "ok", "failed"),
    ("ok", "HTTP 422: already_exists", "failed"),
])
def test_a_github_failure_is_recorded_and_never_fails_the_result(tmp_path, view, upload, status):
    record = run_asset_step(tmp_path, view=view, upload=upload)
    assert record["status"] == status, record
    assert all(call.split()[1] in ("view", "upload") for call in record["calls"])


def replace_member(tree, name, body):
    return [(n, body if n == name else b) for n, b in good_members(tree)]


REFUSED = {
    "another tree's name": (dict(name="lean-build-0123456789ab.tar.zst"), "not exactly one file"),
    "a second file": (dict(extra=["notes.txt"]), "not exactly one file"),
    "a symlink": (dict(members=lambda t: good_members(t) + [("lake/build/lib/l.olean", "symlink")]),
                  "not a regular file or directory"),
    "a hardlink": (dict(members=lambda t: good_members(t) + [("lake/build/lib/h.olean", "hardlink")]),
                   "not a regular file or directory"),
    "a .. member": (dict(members=lambda t: good_members(t) + [("lake/build/../../x", b"x")]), "outside pins.json"),
    "an absolute member": (dict(members=lambda t: good_members(t) + [("/etc/x", b"x")]), "outside pins.json"),
    "a member outside lake/build": (dict(members=lambda t: good_members(t) + [("lake/packages/x", b"x")]),
                                    "outside pins.json"),
    "a secret": (dict(members=lambda t: good_members(t) + [("lake/build/lib/s.olean", b"a ghp_" + b"A1" * 18 + b" z")]),
                 "matches a secret pattern"),
    "a private key": (dict(members=lambda t: good_members(t) + [("lake/build/k", b"-----BEGIN RSA PRIVATE KEY-----")]),
                      "matches a secret pattern"),
    "another tree's seal": (dict(members=lambda t: replace_member(t, "pins.json", seal("f" * 40))), "this lean tree"),
    "another platform": (dict(members=lambda t: replace_member(
        t, "pins.json", seal(t, platform={"system": "Linux", "machine": "aarch64"}))), "Linux-x86_64"),
    "another lean": (dict(members=lambda t: replace_member(
        t, "pins.json", seal(t, toolchain={"lean": LEAN_VERSION.replace("4.24.0", "4.25.0")}))), "seal's lean"),
    "no seal": (dict(members=lambda t: [m for m in good_members(t) if m[0] != "pins.json"]), "no pins.json"),
    "no build": (dict(members=lambda t: [("pins.json", seal(t))]), "nothing under lake/build"),
    "not zstd": (dict(raw=b"plain bytes, not a zstd frame"), "not a readable tar.zst"),
    "over the size cap": (dict(script="cap"), "over the cap 100"),
    "over the uncompressed cap": (dict(script="ucap"), "over 600 bytes uncompressed"),
}


@pytest.mark.parametrize("case", REFUSED, ids=list(REFUSED))
def test_a_bad_pack_is_refused_and_never_uploaded(tmp_path, case):
    kwargs, reason = REFUSED[case]
    if kwargs.get("script") == "cap":
        kwargs = {**kwargs, "script": asset_script().replace("CAP=2000000000;", "CAP=100;", 1)}
    elif kwargs.get("script") == "ucap":
        kwargs = {**kwargs, "script": asset_script().replace("UCAP=8000000000", "UCAP=600", 1)}
    record = run_asset_step(tmp_path, **kwargs)
    assert record["status"] == "refused" and reason in record["reason"], record
    assert not record["calls"], f"a refused pack reached gh: {record['calls']}"
    assert "A1A1A1" not in json.dumps(record, default=str), "the record repeats the secret"


def test_a_pack_not_to_publish_is_checked_and_never_reaches_gh(tmp_path):
    record = run_asset_step(tmp_path / "a", publish="false")
    assert record["status"] == "checked" and not record["calls"], record
    assert record["sha256"] == hashlib.sha256(record["pack"].read_bytes()).hexdigest() and record["key"] == record["tree"]
    refused = run_asset_step(tmp_path / "b", members=lambda t: replace_member(t, "pins.json", seal("f" * 40)), publish="false")
    assert refused["status"] == "refused" and "this lean tree" in refused["reason"], refused


def test_lean_publish_false_comes_only_from_job_json(tmp_path):
    outputs, _ = run_job_commit_step(tmp_path / "a", {"lean_asset": True, "lean_publish": False})
    assert outputs["lean_publish"] == "false", outputs
    for value in ("false", 0, None):
        outputs, _ = run_job_commit_step(tmp_path / f"b{value}", {"lean_asset": True, "lean_publish": value})
        assert outputs["lean_publish"] == "", (value, outputs)


def test_the_caps_the_refusal_tests_lower_are_the_real_ones():
    script = asset_script()
    assert "; CAP=2000000000; UCAP=8000000000\n" in script, "the size caps moved: update the cap tests"


def test_the_run_job_packs_only_when_job_json_asks():
    """job.json's "lean_asset" must be the JSON value true; only then is VE_LEAN_ASSET_DIR set for job.sh,
    and only one file there is sent, as the separate short-lived artifact lean-build."""
    run = parse(VE_JOB.read_text())["jobs"]["run"]
    blocks = "\n".join(step.get("run", "") for step in steps(run))
    assert '.get("lean_asset") is True' in blocks
    assert '[ "$LEAN_ASSET" != 1 ] || export VE_LEAN_ASSET_DIR="$RUNNER_TEMP/lean-build"' in blocks
    sent = [step for step in steps(run) if (step.get("with") or {}).get("name") == "lean-build"
            and step.get("uses", "").startswith("actions/upload-artifact@")]
    assert len(sent) == 1 and sent[0]["if"] == "always() && steps.pack.outputs.ready == 'true'"
    assert int(sent[0]["with"]["retention-days"]) <= 3 and run["outputs"]["lean_asset"] == "${{ steps.pack.outputs.ready }}"


# --- the lean-from steps (actions-gate-x86): a gate shard takes a Lean build only from the run its job.json names
def run_step_script(name: str) -> str:
    run = parse(VE_JOB.read_text())["jobs"]["run"]
    return textwrap.dedent(next(step["run"] for step in steps(run) if step.get("name") == name))


def clean_env(**extra: str) -> dict:
    dropped = ("VE_LEAN_FROM", "VE_LEAN_FROM_SHA256", "VE_LEAN_ASSET_DIR")
    return {**{k: v for k, v in os.environ.items() if not k.startswith(("GH_", "GITHUB_", "LEAN_")) and k not in dropped},
            **extra}


def run_lean_from_check(tmp_path: Path, files=None, *, sha=None) -> tuple[str, str, Path]:
    """files: (name, bytes | "symlink") in the downloaded artifact dir; None = the right pack; "none" = no dir."""
    repo, tree = head_checkout(tmp_path)
    rt = tmp_path / "rt"
    (rt / "out").mkdir(parents=True)
    body = b"the pack of this lean tree"
    good = f"lean-build-{tree[:12]}.tar.zst"
    if files != "none":
        (rt / "lean-from").mkdir()
        for name, content in ([(good, body)] if files is None else files(good)):
            if content == "symlink":
                (rt / "lean-from" / name).symlink_to(tmp_path / "elsewhere")
            else:
                (rt / "lean-from" / name).write_bytes(content)
    output = tmp_path / "github-output"
    output.touch()
    env = clean_env(RUNNER_TEMP=str(rt), GITHUB_OUTPUT=str(output), LEAN_RUN="4242",
                    LEAN_SHA=sha or hashlib.sha256(body).hexdigest())
    done = subprocess.run(["bash", "-c", run_step_script(LEAN_FROM_CHECK)], cwd=repo, env=env, capture_output=True,
                          text=True, timeout=HANG_TIMEOUT)
    assert done.returncode == 0, f"the check failed the run: {done.stdout}{done.stderr}"
    return output.read_text(), (rt / "out/lean-from.txt").read_text(), rt / "lean-from" / good


def test_the_lean_from_check_hands_over_the_named_pack(tmp_path):
    output, said, pack_path = run_lean_from_check(tmp_path)
    assert output == f"file={pack_path}\n", output
    assert said.startswith(f"lean-from: run 4242: {pack_path.name} sha256 ") and said.rstrip().endswith(" ok"), said


LEAN_FROM_REFUSED = {
    "another sha256": (dict(sha="0" * 64), "sha256 "),
    "another tree's name": (dict(files=lambda good: [("lean-build-0123456789ab.tar.zst", b"x")]), "not lean-build-"),
    "a second file": (dict(files=lambda good: [(good, b"x"), ("notes.txt", b"y")]), "2 files"),
    "a hidden second file": (dict(files=lambda good: [(good, b"x"), (".x", b"y")]), "2 files"),
    "an empty artifact": (dict(files=lambda good: []), "0 files"),
    "no download": (dict(files="none"), "0 files"),
    "a symlink": (dict(files=lambda good: [(good, "symlink")]), "not a regular file"),
}


@pytest.mark.parametrize("case", LEAN_FROM_REFUSED, ids=list(LEAN_FROM_REFUSED))
def test_the_lean_from_check_refuses_anything_else_and_the_shard_builds_cold(tmp_path, case):
    kwargs, reason = LEAN_FROM_REFUSED[case]
    output, said, _ = run_lean_from_check(tmp_path, **kwargs)
    assert "file=" not in output, f"{case}: handed over: {output}"
    assert said.startswith("lean-from: run 4242: ") and reason in said and said.rstrip().endswith("cold build"), said


def run_job_commit_step(tmp_path: Path, job_json: dict) -> tuple[dict, str | None]:
    """The run job's `job commit` step on a job commit whose job.json is `job_json` (+ job, head)."""
    repo, _ = head_checkout(tmp_path)
    head = git(repo, "rev-parse", "HEAD")
    (repo / "ci-job").mkdir()
    (repo / "ci-job/job.json").write_text(json.dumps({"job": "j1", "head": head, "argv": [], **job_json}))
    (repo / "ci-job/job.sh").write_text("exit 0\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "ci-job j1")
    rt = tmp_path / "rt"
    rt.mkdir()
    output = tmp_path / "github-output"
    output.touch()
    done = subprocess.run(["bash", "-c", run_step_script("job commit")], cwd=repo, capture_output=True, text=True,
                          env=clean_env(RUNNER_TEMP=str(rt), GITHUB_OUTPUT=str(output), GITHUB_REF_NAME="ci-job/j1"),
                          timeout=HANG_TIMEOUT)
    assert done.returncode == 0, f"{done.stdout}{done.stderr}"
    said = rt / "out/lean-from.txt"
    return dict(line.split("=", 1) for line in output.read_text().splitlines()), \
        said.read_text() if said.exists() else None


SHA = "ab" * 32


def test_job_json_names_the_build_run_and_its_sha256(tmp_path):
    outputs, said = run_job_commit_step(tmp_path, {"lean_from": {"run_id": "4242", "sha256": SHA}})
    assert (outputs["lean_run"], outputs["lean_sha"]) == ("4242", SHA) and said is None, (outputs, said)


def test_no_lean_from_downloads_nothing(tmp_path):
    outputs, said = run_job_commit_step(tmp_path / "a", {})
    assert (outputs["lean_run"], outputs["lean_sha"], said) == ("", "", None), outputs
    outputs, said = run_job_commit_step(tmp_path / "b", {"lean_from": None})
    assert (outputs["lean_run"], outputs["lean_sha"], said) == ("", "", None), outputs


@pytest.mark.parametrize("lean_from", [
    {"run_id": 4242, "sha256": SHA},
    {"run_id": "42 42", "sha256": SHA},
    {"run_id": "4242; x", "sha256": SHA},
    {"run_id": "4242", "sha256": SHA.upper()},
    {"run_id": "4242", "sha256": SHA[:-1]},
    {"run_id": "4242", "sha256": SHA, "repository": "someone/else"},
    {"run_id": "4242"},
    ["4242", SHA],
    "4242",
], ids=["int run", "space", "injection", "upper sha", "short sha", "extra key", "no sha", "a list", "a string"])
def test_a_malformed_lean_from_is_said_and_downloads_nothing(tmp_path, lean_from):
    outputs, said = run_job_commit_step(tmp_path, {"lean_from": lean_from})
    assert (outputs["lean_run"], outputs["lean_sha"]) == ("", ""), outputs
    assert said == "lean-from: job.json's lean_from is malformed: cold build\n", said


def run_job_step(tmp_path: Path, **env: str) -> dict:
    """The run job's `job` step with a job.sh that prints the lean variables it was given."""
    rt = tmp_path / "rt"
    (rt / "ci-job").mkdir(parents=True)
    (rt / "ci-job/job.json").write_text(json.dumps({"argv": []}))
    (rt / "ci-job/job.sh").write_text('for v in VE_LEAN_FROM VE_LEAN_FROM_SHA256 VE_LEAN_ASSET_DIR; do '
                                      'echo "$v=${!v-unset}"; done > "$3/env.txt"\n')
    (rt / "out").mkdir()
    done = subprocess.run(["bash", "-c", run_step_script("job")], cwd=tmp_path, capture_output=True, text=True,
                          env=clean_env(RUNNER_TEMP=str(rt), GITHUB_WORKSPACE=str(tmp_path), LEAN_ASSET="", **env),
                          timeout=HANG_TIMEOUT)
    assert done.returncode == 0, f"{done.stdout}{done.stderr}"
    return dict(line.split("=", 1) for line in (rt / "out/env.txt").read_text().splitlines())


def test_job_sh_gets_the_pack_only_when_the_check_passed(tmp_path):
    given = run_job_step(tmp_path / "a", LEAN_FROM="/rt/lean-from/p.tar.zst", LEAN_SHA=SHA)
    assert (given["VE_LEAN_FROM"], given["VE_LEAN_FROM_SHA256"]) == ("/rt/lean-from/p.tar.zst", SHA), given
    refused = run_job_step(tmp_path / "b", LEAN_FROM="", LEAN_SHA=SHA)
    assert (refused["VE_LEAN_FROM"], refused["VE_LEAN_FROM_SHA256"]) == ("unset", "unset"), refused
    job = next(step for step in steps(parse(VE_JOB.read_text())["jobs"]["run"]) if step.get("name") == "job")
    assert job["env"]["LEAN_FROM"] == "${{ steps.leanfrom.outputs.file }}", "job.sh's pack is not the check's output"
