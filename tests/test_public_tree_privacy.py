"""relb-privacy-scrub step 1: no private operational detail in the public tree.

Scans every git-tracked text file for private-detail kinds and reports each hit as path:line plus a MASKED value
(first 2 characters + "***" + length); no private value is written in this file or printed by it.

Kinds checked now (step 1):
  a  account directory names: per-account Claude/Codex configuration directories, the accounts directory,
     CLAUDE_CONFIG_DIR set to a home-directory path;
  c  e-mail addresses (allowed: example.com/.org, .invalid, the public noreply forms, the git@github.com clone form);
  f  token or key file names: the project's key/token files, the Claude CLI credentials file, private web-app
     directories, a checkout's .env.

Later rows add kinds here:
  relb-privacy-hosts  (d) host names: add sha256 hex digests of the lowercased names to DIGESTS["d"];
  relb-privacy-paths  (b) owner names / login name: digests in DIGESTS["b"]; (e) private paths: a regex in GENERIC.
A digest kind matches lowercased word tokens of each line (the same tokenisers as the masked sweep), so the names
themselves never appear in the tree.

ALLOWED lists the files that keep a hit on purpose, each with its exact hit count per kind and its reason (a pinned
digest, or a code change that needs its own row). A held file with more hits than listed fails (a new hit), and one with
fewer fails too (update the count), so the list only shrinks. This file holds no hit itself: its fixtures are joined at
run time.
"""
import functools
import hashlib
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SELF = "tests/test_public_tree_privacy.py"

GENERIC = {
    "a": re.compile(r"\.claude-[A-Za-z0-9][\w.-]*|\.codex-[A-Za-z0-9][\w.-]*|\.[a-z]+-accounts\b"
                    r"|CLAUDE_CONFIG_DIR=[\"']?(?:[~/]|\$HOME|\$\{HOME)[^\s\"'`;)]*"),
    "c": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.(?:com|org|net|io|dev|edu|gov|ai|co|uk|de"
                    r"|me|app|ca|us|info|biz|xyz|invalid|local|test)\b"),
    "f": re.compile(r"\.ve-[\w.-]*(?:key|token)\b(?:\.json)?|\.credentials\.json\b|\.[a-z]+-private\b"
                    r"|\b[\w-]+/\.env\b"),
}
# value filters per kind: a match for which the filter is true is not a hit
EXEMPT = {
    "c": re.compile(r"@(?:[\w-]+\.)*(?:example\.com|example\.org|invalid)$|^noreply@anthropic\.com$"
                    r"|@users\.noreply\.github\.com$|^noreply@github\.com$|^git@github\.com$", re.I),
}
# sha256 hex digests of lowercased private names, matched against lowercased word tokens (rows above fill these)
DIGESTS = {
    "b": frozenset(),
    "d": frozenset(),
}
TOKENIZERS = [re.compile(p) for p in (r"[a-z0-9]+", r"[a-z0-9-]+", r"[a-z0-9.]+", r"[a-z0-9._-]+")]

_T1C = "pinned: its sha256 is in experiments/T1c/HASHES, HASHES-A1 and HASHES-A2 (the T1c preregistration)"
_RWP = "pinned: its sha256 is in {}/MANIFEST.sha256 (the sealed risk wording probe)"
_RUNNER = ("needs a code row (relb-privacy-code-3): the runner checks the account picker's output against the "
           "accounts directory; removing the name changes what it accepts")
ALLOWED = {
    "experiments/T1c/PREREG-T1c.md": ({"a": 1}, _T1C),
    "ve_experiments/t1c/transport.py": ({"f": 1}, _T1C + "; also code: reads the Claude CLI credentials file"),
    "experiments/authoring-gates/risk-wording-probe/seal.py":
        ({"a": 1}, _RWP.format("experiments/authoring-gates/risk-wording-probe")),
    "experiments/authoring-gates/risk-wording-probe/readers.json":
        ({"a": 1}, _RWP.format("experiments/authoring-gates/risk-wording-probe") + " and risk-wording-probe-2's"),
    "experiments/authoring-gates/risk-wording-probe-2/seal.py":
        ({"a": 1}, _RWP.format("experiments/authoring-gates/risk-wording-probe-2")),
    "experiments/authoring-gates/risk-wording-probe-2/readers.json":
        ({"a": 1}, _RWP.format("experiments/authoring-gates/risk-wording-probe-2")),
    "tools/hooks/precommit.py": ({"f": 2}, "needs a code row (relb-privacy-code-1): the hook refuses files under the "
                                      "private web-app directory by its name"),
    "tests/test_precommit_hook.py": ({"f": 6}, "needs a code row (relb-privacy-code-1): fixtures of that hook rule and "
                                          "of a checkout's .env"),
    "ve_experiments/claude_cli.py": ({"f": 1}, "needs a code row (relb-privacy-code-2): reads the Claude CLI "
                                          "credentials file by its name"),
    "docs/act-phrases/ap-7/runner.py": ({"a": 1}, _RUNNER),
    "docs/judgment-terms/jt-e1r/runner.py": ({"a": 1}, _RUNNER),
    "docs/judgment-terms/jt-e3/runner.py": ({"a": 1}, _RUNNER),
    "docs/presupposition/ps-e1/e1_runner.py": ({"a": 1}, _RUNNER),
    "experiments/authoring-gates/risk-wording-probe/run.py": ({"a": 1}, _RUNNER + " (its Codex home constant)"),
    "experiments/authoring-gates/risk-wording-probe-2/run.py": ({"a": 1}, _RUNNER + " (its Codex home constant)"),
}


def mask(value):
    return f"{value[:2]}***({len(value)})"


def kinds():
    return sorted(GENERIC) + sorted(k for k, v in DIGESTS.items() if v)


def _tokens(low):
    out = set()
    for t in TOKENIZERS:
        out.update(m.group(0).strip(".-_") for m in t.finditer(low))
    return out


def scan_line(line):
    """[(kind, value)] for one line."""
    hits = []
    for kind, rx in GENERIC.items():
        for m in rx.finditer(line):
            v = m.group(0)
            if kind in EXEMPT and EXEMPT[kind].search(v):
                continue
            hits.append((kind, v))
    active = {k: v for k, v in DIGESTS.items() if v}
    if active:
        for t in _tokens(line.lower()):
            d = hashlib.sha256(t.encode()).hexdigest()
            hits.extend((k, t) for k, v in active.items() if d in v)
    return hits


@functools.lru_cache(maxsize=1)
def tree_hits():
    """{kind: [(path, line, masked value)]} over every tracked text file."""
    try:
        out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"], capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("not a git checkout")
    hits = {}
    for rel in out.decode("utf-8", "replace").split("\0"):
        p = ROOT / rel
        if not rel or p.is_symlink() or not p.is_file():
            continue
        data = p.read_bytes()
        if b"\0" in data[:8000]:
            continue
        for i, line in enumerate(data.decode("utf-8", "replace").splitlines(), 1):
            for kind, v in scan_line(line[:20000]):
                hits.setdefault(kind, []).append((rel, i, mask(v)))
    return hits


@pytest.mark.parametrize("kind", kinds())
def test_no_private_detail_of_kind_in_the_tracked_tree(kind):
    bad = [h for h in tree_hits().get(kind, []) if kind not in ALLOWED.get(h[0], ({}, ""))[0]]
    assert not bad, f"{len(bad)} kind-({kind}) hits (masked): " + "; ".join(f"{p}:{n} {v}" for p, n, v in bad[:40])


def test_every_held_file_has_exactly_its_listed_hits():
    off = []
    for path, (counts, _reason) in ALLOWED.items():
        for k, want in counts.items():
            got = [h for h in tree_hits().get(k, []) if h[0] == path]
            if len(got) != want:
                off.append(f"{path} ({k}): {len(got)} hits, ALLOWED says {want}: "
                           + "; ".join(f":{n} {v}" for _p, n, v in got[:5]))
    assert not off, "held files off their counts (a new hit, or update/remove the entry): " + " | ".join(off)


def test_this_file_holds_no_hit():
    assert SELF not in ALLOWED
    assert not [h for hs in tree_hits().values() for h in hs if h[0] == SELF]


def _j(*parts):
    """Join fixture pieces at run time, so no fixture is itself a hit in this file."""
    return "".join(parts)


@pytest.mark.parametrize("line, kind", [
    (_j("cfg=~/.claude", "-someone"), "a"),
    (_j("export CODEX_HOME=$HOME/.codex", "-two"), "a"),
    (_j("ls ~/.my", "-accounts/x"), "a"),
    (_j("CLAUDE_CONFIG_DIR", "=~/x claude -p"), "a"),
    (_j("Author: A <someone", "@mail.test>"), "c"),
    (_j("token in ~/.ve", "-some-token"), "f"),
    (_j("key at ~/.ve", "-thing-key.json"), "f"),
    (_j("cat x/.credentials", ".json"), "f"),
    (_j("under .site", "-private/"), "f"),
    (_j("source ops-repo/", ".env"), "f"),
])
def test_the_patterns_find_each_kind(line, kind):
    assert kind in {k for k, _ in scan_line(line)}


@pytest.mark.parametrize("line", [
    "mail a@example.com or b@x.example.org or c@host.invalid",
    "Co-Authored-By: X <noreply@anthropic.com>; 1+x@users.noreply.github.com; git@github.com:o/r.git",
    _j("CLAUDE_CONFIG_DIR", "=$cfg claude -p"),
    "Path.home() / f'.claude-{label}'",
])
def test_public_forms_are_not_hits(line):
    assert scan_line(line) == []


def test_a_digest_kind_matches_tokens_without_the_name_in_the_tree(monkeypatch):
    monkeypatch.setitem(DIGESTS, "d", frozenset({hashlib.sha256(b"build-host-zz").hexdigest()}))
    assert ("d", "build-host-zz") in scan_line("ssh Build-Host-ZZ uptime")
    assert scan_line("ssh build-host-zy uptime") == []
