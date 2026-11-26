"""relb-privacy-scrub step 1: no private operational detail in the public tree.

Scans every git-tracked text file for private-detail kinds and reports each hit as path:line plus a MASKED value
(first 2 characters + "***" + length); no private value is written in this file or printed by it.

Kinds checked now (steps 1 and 2):
  a  account directory names: per-account Claude/Codex configuration directories, the accounts directory,
     CLAUDE_CONFIG_DIR set to a home-directory path;
  c  e-mail addresses (allowed: example.com/.org, .invalid, the public noreply forms, the git@github.com clone form);
  f  token or key file names: the project's key/token files, private web-app
     directories, a checkout's .env;
  d  host names of our machines (relb-privacy-hosts): the cloud VM names, the Mac runner's name and the build VM's
     hostname, as sha256 hex digests of the lowercased names in DIGESTS["d"]. Their IP addresses are not listed: a
     digest of an IPv4 address is reversed by trying all 2**32 addresses, and the tree holds none of them.

Later rows add kinds here:
  relb-privacy-paths  (b) owner names / login name: digests in DIGESTS["b"]; (e) private paths: a regex in GENERIC.
A digest kind matches lowercased word tokens of each line (the same tokenisers as the masked sweep) and of each tracked
path (reported as line 0), so the names themselves never appear in the tree. A hyphenated token also yields its runs of
1 to 4 consecutive hyphen-separated pieces, so a name glued to another word by a hyphen still matches. The digests
guard against the names coming back; they do not hide them (a short role-like name can be guessed from its digest).

ALLOWED lists the files that keep a hit on purpose, each with its exact hit count per kind and its reason (a digest
that a counted result or a timestamp depends on; relb-privacy-s1b redacted the rest, docs/REDACTIONS.md). A held file
with more hits than listed fails (a new hit), and one with fewer fails too (update the count), so the list only
shrinks. No file may hold a machine name (kind d): relb-privacy-hosts-code-1 redacted the last four. This file holds no
hit itself: its fixtures are joined at run time.
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
    "f": re.compile(r"\.ve-[\w.-]*(?:key|token)\b(?:\.json)?|\.[a-z]+-private\b"
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
    # relb-privacy-hosts (2026-11-26): the build VM's hostname (15 characters), two cloud VM names (10 each) and the
    # Mac runner's name (8); the tree calls them build-vm, cloud-vm-2, cloud-vm-3 and mac-runner.
    "d": frozenset({
        "51961b9ef6b3fe38bca2fcc7472851174c866924d26ec36bc57517f116e22d4f",
        "a443a8d2a896752b0c83381f1564b01f35ee19749b5e0a9cc933f46e208cd3fd",
        "714b7fcf7e868b59876edbb2e79910f1048d285463f0755f7155250a5cd17e83",
        "a266b6064223b5a33b9f328c8a4e9aab50d3167379ecbb8371fb7c5af48238a6",
    }),
}
TOKENIZERS = [re.compile(p) for p in (r"[a-z0-9]+", r"[a-z0-9-]+", r"[a-z0-9.]+", r"[a-z0-9._-]+")]

# A standard file name (the Claude CLI's credentials file) or a generic prefix alone is not a hit (orchestrator word
# 2026-11-25 on relb-privacy-s1b): it carries no private value. A path that names a private account directory still
# hits kind a, and the project's own key/token file names still hit kind f.
_PREREG = ("held, the one documented exception (docs/REDACTIONS.md; orchestrator word 2026-11-25): the timestamped T1c "
           "preregistration; its sha256 is OpenTimestamped and the counted T1c results depend on it")
ALLOWED = {
    "experiments/T1c/PREREG-T1c.md": ({"a": 1}, _PREREG),
}
# A held file is held at exactly these bytes: any change to it must come back to review.
HELD_SHA256 = {
    "experiments/T1c/PREREG-T1c.md": "56c3f7f08699369b26cd9c48c584d8fcefa9fa600723f27fffda74abf8cb4bb7",
}


def mask(value):
    return f"{value[:2]}***({len(value)})"


def kinds():
    return sorted(GENERIC) + sorted(k for k, v in DIGESTS.items() if v)


def _tokens(low):
    out = set()
    for t in TOKENIZERS:
        out.update(m.group(0).strip(".-_") for m in t.finditer(low))
    for tok in [t for t in out if "-" in t]:
        parts = [p for p in tok.split("-") if p]
        out.update("-".join(parts[i:j]) for i in range(len(parts)) for j in range(i + 1, min(i + 4, len(parts)) + 1))
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


def path_hits(rel):
    """[(kind, (path, 0, masked value))] for a tracked path itself (a file named after a host is a hit too)."""
    return [(kind, (rel, 0, mask(v))) for kind, v in scan_line(rel)]


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
        if not rel:
            continue
        for kind, h in path_hits(rel):
            hits.setdefault(kind, []).append(h)
        if p.is_symlink() or not p.is_file():
            continue
        data = p.read_bytes()
        if b"\0" in data[:8000]:
            continue
        for i, line in enumerate(data.decode("utf-8", "replace").splitlines(), 1):
            for kind, v in scan_line(line):
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


def test_every_held_file_is_held_at_its_exact_bytes():
    assert set(HELD_SHA256) == set(ALLOWED)
    for path, digest in HELD_SHA256.items():
        got = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        assert got == digest, f"{path} changed (sha256 {got[:12]}...): a held file comes back to review before its entry moves"


def test_no_file_is_allowed_a_machine_name():
    assert not [path for path, (counts, _reason) in ALLOWED.items() if "d" in counts]


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
    (_j("cat ~/.team", "-accounts/claude-x/.credentials.json"), "a"),  # a private dir with the standard name
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
    "path = (config or Path.home() / '.claude') / '.credentials.json'",
    "the CLI keeps its login in .credentials.json",
])
def test_public_forms_are_not_hits(line):
    assert scan_line(line) == []


def test_a_digest_kind_matches_tokens_without_the_name_in_the_tree(monkeypatch):
    monkeypatch.setitem(DIGESTS, "d", frozenset({hashlib.sha256(b"build-host-zz").hexdigest()}))
    assert ("d", "build-host-zz") in scan_line("ssh Build-Host-ZZ uptime")
    assert scan_line("ssh build-host-zy uptime") == []


def test_the_host_digest_set_is_four_sha256_hex_digests():
    for d in DIGESTS["d"]:
        assert re.fullmatch(r"[0-9a-f]{64}", d)
    assert len(DIGESTS["d"]) == 4


def test_long_lines_are_scanned_to_their_end(monkeypatch):
    monkeypatch.setitem(DIGESTS, "d", frozenset({hashlib.sha256(b"build-host-zz").hexdigest()}))
    assert ("d", "build-host-zz") in scan_line("x" * 30000 + ' "where": "build-host-zz"')


@pytest.mark.parametrize("line", ["old build-host-zz-old box", "logs/ssh-build-host-zz.txt", "x_build-host-zz_y"])
def test_a_host_name_glued_by_a_hyphen_still_matches(monkeypatch, line):
    monkeypatch.setitem(DIGESTS, "d", frozenset({hashlib.sha256(b"build-host-zz").hexdigest()}))
    assert ("d", "build-host-zz") in scan_line(line)


def test_tracked_paths_are_scanned(monkeypatch):
    monkeypatch.setitem(DIGESTS, "d", frozenset({hashlib.sha256(b"build-host-zz").hexdigest()}))
    assert path_hits("docs/x/sar/build-host-zz.txt") == [("d", ("docs/x/sar/build-host-zz.txt", 0, "bu***(13)"))]
    assert path_hits("docs/x/sar/build-host-zy.txt") == []
