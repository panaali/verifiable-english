"""relb-privacy-scrub, -hosts and -paths: no private operational detail in the public tree.

Scans every git-tracked text file (and every tracked path, as line 0) for six private-detail kinds and reports each
hit as path:line plus a MASKED value (first 2 characters + "***" + length); no private value is written in this file
or printed by it.

  a  account directory names: per-account Claude/Codex configuration directories, the accounts directory,
     CLAUDE_CONFIG_DIR set to a home-directory path;
  b  owner names and handles (relb-privacy-paths): the worker account handles and their name parts, the login name,
     the ssh user name and the repository owner, as sha256 hex digests of the lowercased names in DIGESTS["b"]. The
     owner is allowed inside the public repository URL (<owner>/verifiable-english), matched by its digest. The tree
     calls them worker-account-1..n, operator, ssh-user and repo-owner;
  c  e-mail addresses (allowed: example.com/.org, .invalid, the public noreply forms, the git@github.com clone form);
  d  host names of our machines (relb-privacy-hosts): the cloud VM names, the Mac runner's name and the build VM's
     hostname, as sha256 hex digests in DIGESTS["d"]. Their IP addresses are not listed: a digest of an IPv4
     address is reversed by trying all 2**32 addresses, and the tree holds none of them;
  e  private paths (relb-privacy-paths): a home directory that starts a path (/home/<user>, /Users/<user>; a /home/
     segment inside another path, such as a test sandbox, is not one), ~/code/<dir>, $HOME/code/<dir>, the inputs
     directory under the home directory and ~/.ve-* files. The tree writes <home>, <repo>, <ops-repo> and <inputs>;
  f  token or key file names: the project's key/token files, private web-app directories, a checkout's .env.

A digest kind matches lowercased word tokens of each line (the same tokenisers as the masked sweep) and of each tracked
path, so the names themselves never appear in the tree. A hyphenated token also yields its runs of 1 to 4 consecutive
hyphen-separated pieces, so a name glued to another word by a hyphen still matches. The digests guard against the
names coming back; they do not hide them (a short role-like name can be guessed from its digest).

ALLOWED lists the files that keep a hit on purpose, each with its exact hit count per kind and its reason: class A of
relb-privacy-held (orchestrator word 2026-11-26), the files whose sha256 is in an outside OpenTimestamps chain (the
T1c preregistration and the three files experiments/T1c/HASHES* pin), kept byte-identical and listed in
docs/REDACTIONS.md. A held file with
more hits than listed fails (a new hit), and one with fewer fails too (update the count), so the list only shrinks;
each is held at its exact sha256. No file may hold a machine name
(kind d). This file holds no hit itself: its fixtures are joined at run time.

Compressed files and archives (relb-privacy-gz-roots, orchestrator word 2026-11-26 item E): a tracked gzip, bzip2,
xz, zip or tar file (found by its magic bytes, nested up to ARCHIVE_DEPTH) is read in memory and each text member is
scanned, its hits reported as <path>!<member>:line; an archive that cannot be read fails the test (never a silent 0).
"""
import bz2
import functools
import gzip
import hashlib
import io
import lzma
import os
import re
import subprocess
import sys
import tarfile
import zipfile
import zlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SELF = "tests/test_public_tree_privacy.py"

GENERIC = {
    "a": re.compile(r"\.claude-[A-Za-z0-9][\w.-]*|\.codex-[A-Za-z0-9][\w.-]*|\.[a-z]+-accounts\b"
                    r"|CLAUDE_CONFIG_DIR=[\"']?(?:[~/]|\$HOME|\$\{HOME)[^\s\"'`;)]*"),
    "c": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.(?:com|org|net|io|dev|edu|gov|ai|co|uk|de"
                    r"|me|app|ca|us|info|biz|xyz|invalid|local|test)\b"),
    # a home directory starting a path (not a /home/ segment inside another path), code and inputs directories under
    # the home directory, and ~/.ve-* files ("[s]" keeps this file's own text from matching)
    "e": re.compile(r"(?<![\w.$}/])(?:/home|/Users)/[A-Za-z0-9_][\w.-]*|(?:~|\$HOME|\$\{HOME\})/code/[\w.-]+"
                    r"|(?:~|\$HOME)/ve-input[s]\b|(?:~|\$HOME)/\.ve-[\w.-]+"),
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
    # relb-privacy-paths (2026-11-26): the worker account handles (14, 13, 13 and 8 characters) and two name parts (6
    # each), the login name (6), the ssh user name (8) and the repository owner (7; allowed in the public URL).
    "b": frozenset({
        "1083ffafcdbd45c1cfca5e3703437d68b302805dd35be082c16974748c451a73",
        "14fbd8f96d602fbd59230decbef094d52943a12b7164b30d3b05f3cf6d8f9f65",
        "31fabf8de2d5fe5609b50a9d48154d4361101d5609c92fee0bc900daa8a96e0f",
        "380547094aa5e274f9ad6e016586a34d44810c40017cbe762d9099adc0184322",
        "72b6df644dae8dc31eb2bd7859295e92b8823bf9b23ba57b845c25afdace5b96",
        "b39466e305abda45366903f3565f3fad695a44765855e421691768f1164ef318",
        "b6614267a8f6464375addbb8af5fcba42951df7482b05a5da575879bfa38ea9f",
        "dce0d39921b78cbe795e647254e60b2df2be4af024df4f03e111059d325386cf",
        "f16f3103c0dc5e0c4ed458e6480434b19cc2f6c0b02a26f8c21e9e64b179e86d",
    }),
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
# the public repository URL (or its owner/name slug): allowed when the owner part is the owner's digest
OWNER_DIGEST = "b39466e305abda45366903f3565f3fad695a44765855e421691768f1164ef318"
PUBLIC_URL = re.compile(r"(?:github\.com[/:])?([\w.-]+)/verifiable-english", re.I)

# A standard file name (the Claude CLI's credentials file) or a generic prefix alone is not a hit (orchestrator word
# 2026-11-25 on relb-privacy-s1b): it carries no private value. A path that names a private account directory still
# hits kind a, and the project's own key/token file names still hit kind f.
_PREREG = ("held, the one documented exception (docs/REDACTIONS.md; orchestrator word 2026-11-25): the timestamped T1c "
           "preregistration; its sha256 is OpenTimestamped and the counted T1c results depend on it")
_CLASS_A = ("class A (relb-privacy-held 2026-11-26; orchestrator word 2026-11-26, docs/REDACTIONS.md): held byte-identical, "
            "a documented exception: its sha256 is in an outside OpenTimestamps chain; ")
ALLOWED = {
    "experiments/T1c/PREREG-T1c.md": ({'a': 1, 'b': 3}, _PREREG),
    "design/crypto-inspired-oversight.md": ({'b': 1}, _CLASS_A + "sha256 in experiments/T1c/HASHES, HASHES-A1 and HASHES-A2"),
    "experiments/T1c/README.md": ({'b': 3, 'e': 1}, _CLASS_A + "sha256 in experiments/T1c/HASHES-A2"),
    "ve_experiments/t1c/run.py": ({'b': 1}, _CLASS_A + "sha256 in experiments/T1c/HASHES-A2"),
}
# A held file is held at exactly these bytes: any change to it must come back to review.
HELD_SHA256 = {
    "design/crypto-inspired-oversight.md": "17bd3eb8c8f43f6762c9b10accbcc7e683d37d8ec07f1a992cfa6367fa8dfda8",
    "experiments/T1c/PREREG-T1c.md": "56c3f7f08699369b26cd9c48c584d8fcefa9fa600723f27fffda74abf8cb4bb7",
    "experiments/T1c/README.md": "5b351679fbffd75d3f0df508afcbb64cf13ad6b92172ccec589019d4f612d5a1",
    "ve_experiments/t1c/run.py": "fd3c47a8fb2245d53d331fda5ae913b91ed18cd28df0f4eb983140d8311d62cc",
}


def _digest(value):
    return hashlib.sha256(value.lower().encode()).hexdigest()


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


@functools.lru_cache(maxsize=1 << 20)
def _token_digest(token):
    return hashlib.sha256(token.encode()).hexdigest()


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
        line = PUBLIC_URL.sub(lambda m: " " if _digest(m.group(1)) == OWNER_DIGEST else m.group(0), line)
        for t in _tokens(line.lower()):
            d = _token_digest(t)
            hits.extend((k, t) for k, v in active.items() if d in v)
    return hits


ARCHIVE_DEPTH = 8


def _sniff(data):
    if data[:2] == b"\x1f\x8b":
        return "gz"
    if data[:3] == b"BZh" and data[3:4].isdigit():
        return "bz2"
    if data[:6] == b"\xfd7zXZ\x00":
        return "xz"
    if data[:4] in (b"PK\x03\x04", b"PK\x05\x06"):
        return "zip"
    if len(data) >= 262 and data[257:262] == b"ustar":
        return "tar"
    return None


def blob_members(data, label, depth=0):
    """[(label, text bytes)] of one blob: itself when it is text, each text member (recursively) when it is a
    compressed file or an archive; [] for another binary. An unreadable archive raises ValueError."""
    kind = _sniff(data)
    if kind is None:
        return [] if b"\0" in data[:8000] else [(label, data)]
    if depth >= ARCHIVE_DEPTH:
        raise ValueError(f"{label}: nested deeper than {ARCHIVE_DEPTH}")
    out = []
    try:
        if kind in ("gz", "bz2", "xz"):
            inner = {"gz": gzip.decompress, "bz2": bz2.decompress, "xz": lzma.decompress}[kind](data)
            name = os.path.basename(label.split("!")[-1])
            stem, ext = os.path.splitext(name)
            if _sniff(inner) == "tar":
                return blob_members(inner, label, depth)
            out += blob_members(inner, f"{label}!{stem if ext else name + '.out'}", depth + 1)
        elif kind == "zip":
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                for info in z.infolist():
                    if not info.is_dir():
                        out += blob_members(z.read(info), f"{label}!{info.filename}", depth + 1)
        else:
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:") as t:
                for m in t.getmembers():
                    if m.isfile():
                        out += blob_members(t.extractfile(m).read(), f"{label}!{m.name}", depth + 1)
    except (OSError, EOFError, zlib.error, zipfile.BadZipFile, tarfile.TarError, lzma.LZMAError) as e:
        raise ValueError(f"{label}: unreadable {kind} ({type(e).__name__})") from e
    return out


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
        for label, data in blob_members(p.read_bytes(), rel):
            if label != rel:  # a member name is scanned like a tracked path
                for kind, v in scan_line(label.split("!", 1)[1]):
                    hits.setdefault(kind, []).append((label, 0, mask(v)))
            for i, line in enumerate(data.decode("utf-8", "replace").splitlines(), 1):
                for kind, v in scan_line(line):
                    hits.setdefault(kind, []).append((label, i, mask(v)))
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
    (_j("cd /ho", "me/someone/x"), "e"),
    (_j("ls /Us", "ers/someone"), "e"),
    (_j('"/ho', 'me/runner/work/x"'), "e"),
    (_j("C=${X:-/ho", "me/someone/.local/bin/claude}"), "e"),
    (_j("cd ~/co", "de/some-repo/tools"), "e"),
    (_j("cd $HOME/co", "de/x"), "e"),
    (_j("cd ${HOME}/co", "de/x"), "e"),
    (_j("ls ~/ve-in", "puts/a"), "e"),
    (_j("cat ~/.ve", "-notes"), "e"),
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
    _j("/tmp/sandbox-x/ho", "me/fake/killed"),
    _j("zsh $T/ho", "me/tm-nightly.sh --once"),
    "see <home>/.local/bin/claude, <repo>/tools/x.py, <ops-repo>/reviews/a.md, <inputs>/b, <home>/code/other-repo",
    "pytest-of-operator, worker-account-2 and ssh-user, repo-owner",
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


def test_the_name_digest_set_is_nine_sha256_hex_digests_and_holds_the_owner():
    for d in DIGESTS["b"]:
        assert re.fullmatch(r"[0-9a-f]{64}", d)
    assert len(DIGESTS["b"]) == 9
    assert OWNER_DIGEST in DIGESTS["b"]


@pytest.mark.parametrize("line", ["tmp/pytest-of-someone-zz/pytest-0", '"account": "claude-someone-zz"',
                                  "test_gets_someone_zz_over_44", "Someone-ZZ said", "x/someone-zz/verifiable-englis"])
def test_a_name_digest_matches_names_in_paths_and_words(monkeypatch, line):
    monkeypatch.setitem(DIGESTS, "b", frozenset({hashlib.sha256(b"someone-zz").hexdigest()}))
    assert any(k == "b" for k, _ in scan_line(line.replace("someone_zz", "someone-zz")))


def test_the_owner_is_allowed_only_inside_the_public_repo_url(monkeypatch):
    monkeypatch.setitem(DIGESTS, "b", frozenset({hashlib.sha256(b"owner-zz").hexdigest()}))
    monkeypatch.setattr(sys.modules[__name__], "OWNER_DIGEST", hashlib.sha256(b"owner-zz").hexdigest())
    assert scan_line("git clone https://github.com/Owner-ZZ/verifiable-english.git") == []
    assert scan_line("see owner-zz/verifiable-english#12") == []
    assert ("b", "owner-zz") in scan_line("asked owner-zz about it")
    assert ("b", "owner-zz") in scan_line("https://github.com/owner-zz/other-repo")


def test_another_owner_in_a_repo_url_is_not_allowed(monkeypatch):
    monkeypatch.setitem(DIGESTS, "b", frozenset({hashlib.sha256(b"someone-zz").hexdigest()}))
    assert ("b", "someone-zz") in scan_line("github.com/someone-zz/verifiable-english")


def test_every_held_file_names_its_reason():
    for path, (counts, reason) in ALLOWED.items():
        assert counts and reason, path
        assert not set(counts) - set("abcdef"), path


def _fake_home_path():
    return "/" + "home" + "/zzfake" + "user/data"  # joined at run time: this file holds no hit


def _tar(name, data):
    bio = io.BytesIO()
    with tarfile.open(fileobj=bio, mode="w") as t:
        info = tarfile.TarInfo(name)
        info.size = len(data)
        t.addfile(info, io.BytesIO(data))
    return bio.getvalue()


def _zip(name, data):
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, "w") as z:
        z.writestr(name, data)
    return bio.getvalue()


@pytest.mark.parametrize("pack, label", [
    (lambda b: gzip.compress(b), "x.txt.gz!x.txt"),
    (lambda b: bz2.compress(b), "x.txt.bz2!x.txt"),
    (lambda b: lzma.compress(b), "x.txt.xz!x.txt"),
    (lambda b: _zip("in/x.txt", b), "x.zip!in/x.txt"),
    (lambda b: gzip.compress(_tar("in/x.txt", b)), "x.tar.gz!in/x.txt"),
    (lambda b: _zip("in/y.txt.gz", gzip.compress(b)), "x.zip!in/y.txt.gz!y.txt"),
])
def test_a_value_inside_a_compressed_file_or_archive_is_found(pack, label):
    text = ("before\n" + "x" * 30000 + " " + _fake_home_path() + "\n").encode()
    name = label.split("!")[0]
    members = blob_members(pack(text), name)
    assert [m[0] for m in members] == [label]
    assert [k for m in members for line in m[1].decode().splitlines() for k, _v in scan_line(line)] == ["e"]


def test_a_clean_archive_and_a_plain_binary_give_nothing_and_a_broken_one_fails():
    assert [k for _l, d in blob_members(gzip.compress(_tar("c.txt", b"clean words\n")), "c.tar.gz")
            for line in d.decode().splitlines() for k, _v in scan_line(line)] == []
    assert blob_members(bytes(range(256)) * 4, "x.bin") == []
    with pytest.raises(ValueError, match="unreadable gz"):
        blob_members(b"\x1f\x8b\x08\x00" + b"\xff" * 40, "bad.gz")
