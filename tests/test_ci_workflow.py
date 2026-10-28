"""The security properties of the GitHub Actions workflows (.github/workflows/; gha-wf).

`ve-job.yml` runs VE compute jobs on GitHub (manage-agents reviews/gha-pilot-20261028.md, "Workflow" and
"Security"). Every workflow file, today's and any added later, must keep the trigger and secret rules:
it runs only on a push of a `ci-job/**` branch, its token starts with no permission, and no `run:` block
reads a secret or an event field (template injection). ve-job.yml must also keep its own shape: a
read-only `run` job that keeps no credentials and runs only in this repository, and a `publish` job, the
only one that writes, that pushes nothing but `ci-result/$JOB`, never forced.

The files are read as text by a small reader of the YAML they use (PyYAML is not in the environment).
It fails closed: tabs, anchors, aliases, tags, merge keys, quoted or duplicate keys and lines it cannot
place are refused, so a rule cannot be dodged by writing the same thing another way.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import shlex

import pytest

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
    assert permissions(run.get("permissions"), "run") == {"contents": "read"}, run.get("permissions")
    assert permissions(publish.get("permissions"), "publish") == {"contents": "write"}
    assert run.get("if") == f"github.repository == '{REPOSITORY}'", f"run is not guarded: {run.get('if')!r}"
    checkouts = [step for step in steps(run) if step.get("uses", "").startswith("actions/checkout@")]
    assert checkouts, "run has no checkout"
    for step in checkouts:
        assert (step.get("with") or {}).get("persist-credentials") == "false", "run keeps its credentials"
    for name, block in run_blocks(document):
        pushes = [shlex.split(args) for args in GIT_PUSH.findall(block)]
        if name != "publish":
            assert not pushes, f"{name} pushes"
            continue
        assert pushes, "publish pushes nothing"
        for args in pushes:
            assert [arg for arg in args if arg != "-q"] == PUBLISH_PUSH, f"publish pushes {args}"


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
    ("actions write", "      contents: read\n", "      contents: read\n      actions: write\n", "run may not write actions"),
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
