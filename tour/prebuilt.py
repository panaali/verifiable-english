"""The tour's prebuilt checkers: the two programs VE runs to check answers, built once and fetched by the install.

The tour runs two checker programs: Lean's `ve_service` (lean/.lake/build/bin/) and the Rust `ve`
(rust/target/release/). Building them from source takes most of an hour. This script packs the built programs of both
checkouts the tour uses (this one, "main", and the after-release checkout in .tour-after-release/) into one archive,
and unpacks such an archive into place, so that `sh tour/install.sh` can skip the builds.

    python tour/prebuilt.py make DIR        pack the built programs into DIR/ARCHIVE and write tour/prebuilt.json
    python tour/prebuilt.py install SOURCE  fetch SOURCE (an https:// or file:// URL, or a path), check it, unpack it
    python tour/prebuilt.py scan ARCHIVE    list any private detail in the archive's programs (exit 1 if any)
    python tour/prebuilt.py url             print the archive's published URL

tour/prebuilt.json (committed) records, for each checkout, the commit of its Lean and Rust sources (git tree ids) and
the SHA-256 of every program, plus the SHA-256 of the archive itself. `install` refuses an archive whose SHA-256 is not
the recorded one, a program whose SHA-256 is not the recorded one, and a checkout whose sources differ from the ones
the programs were built from (then the install builds from source instead). VE itself also refuses a Lean checker
whose SHA-256 is not listed in lean/checkers.lock.

The archive is made the same way everywhere (sorted members, fixed times and owners, gzip without a time stamp), so
the same programs always give the same archive bytes. The GitHub Actions workflow .github/workflows/tour-prebuilt.yml
builds the programs from source on a free runner, runs `make`, checks that the result equals tour/prebuilt.json and
holds no private detail, and keeps the archive as the run's artifact; a maintainer then uploads those same bytes as
the release asset `url` names (the workflow's token cannot write, by this repository's workflow rules).
"""
from __future__ import annotations

import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.request

TOUR = Path(__file__).resolve().parent
ROOT = TOUR.parent
SIDE = ROOT / ".tour-after-release"
MANIFEST = TOUR / "prebuilt.json"
ARCHIVE = "ve-tour-prebuilt-linux-x86_64.tar.gz"
FORMAT = "ve-tour-prebuilt@1"
# The programs, relative to a checkout. Rust's `ve` is packed for "main" only: the after-release checkout uses the
# same one when its Rust sources are the same (the install checks that), and its stops never run it otherwise.
PROGRAMS = {"main": ("lean/.lake/build/bin/ve_service", "rust/target/release/ve"),
            "after-release": ("lean/.lake/build/bin/ve_service",)}
# The public home-directory paths a program may name: Lean's own release builds of Lean and of its LLVM (GitHub's
# runner), compiled into Lean's runtime library. Any other home-directory path in a program is a private detail.
PUBLIC_HOME_PATH = re.compile(rb"/ho" + rb"me/runner/work/(?:lean4/lean4|lean-llvm/lean-llvm)/")
HOME_PATH = re.compile(rb"/(?:home|Users)/[A-Za-z0-9._-]+")
STRING = re.compile(rb"[\x20-\x7e]{6,}")


def checkout(side: str) -> Path:
    return ROOT if side == "main" else SIDE


def tree(path: Path, sub: str) -> str:
    """The git tree id of SUB at the checkout's HEAD: the commit of those sources."""
    return subprocess.run(["git", "-C", str(path), "rev-parse", f"HEAD:{sub}"], check=True, capture_output=True,
                          text=True).stdout.strip()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def archive_bytes(files: dict[str, bytes]) -> bytes:
    """A gzip'd tar of FILES (name -> bytes), the same bytes for the same files on any machine."""
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.USTAR_FORMAT) as tar:
        for name in sorted(files):
            info = tarfile.TarInfo(name)
            info.size, info.mode, info.mtime = len(files[name]), 0o755, 0
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            tar.addfile(info, io.BytesIO(files[name]))
    out = io.BytesIO()
    with gzip.GzipFile(fileobj=out, mode="wb", compresslevel=6, mtime=0, filename="") as gz:
        gz.write(raw.getvalue())
    return out.getvalue()


def make(outdir: str) -> int:
    files, sides = {}, {}
    for side, programs in PROGRAMS.items():
        path = checkout(side)
        commit = subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"], check=True, capture_output=True,
                                text=True).stdout.strip()
        record = {"lean_tree": tree(path, "lean"), "rust_tree": tree(path, "rust"), "files": {}}
        if side == "after-release":
            record["commit"] = commit
        for rel in programs:
            data = (path / rel).read_bytes()
            files[f"{side}/{rel}"] = data
            record["files"][rel] = sha256(data)
        sides[side] = record
    data = archive_bytes(files)
    hits = scan_files(files)
    if hits:
        for hit in hits:
            print("private detail:", hit, file=sys.stderr)
        return 1
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    (out / ARCHIVE).write_bytes(data)
    (out / f"{ARCHIVE}.sha256").write_text(f"{sha256(data)}  {ARCHIVE}\n")
    old = manifest() if MANIFEST.exists() else {}
    new = {"format": FORMAT, "platform": "linux-x86_64", "archive": ARCHIVE, "archive_sha256": sha256(data),
           "archive_bytes": len(data), "release_tag": f"tour-prebuilt-{sides['main']['lean_tree'][:10]}",
           "repository": old.get("repository", "https://github.com/panaali/verifiable-english"), "sides": sides}
    MANIFEST.write_text(json.dumps(new, indent=1) + "\n", encoding="utf-8")
    print(f"{out / ARCHIVE}: {len(data)} bytes, sha256 {sha256(data)}")
    return 0


def url() -> str:
    m = manifest()
    return f"{m['repository']}/releases/download/{m['release_tag']}/{m['archive']}"


def fetch(source: str) -> bytes:
    """The archive's bytes from SOURCE (an https://, http:// or file:// URL, or a path), with a progress line every
    few seconds while it downloads."""
    if "://" not in source:
        return Path(source).read_bytes()
    with urllib.request.urlopen(source, timeout=60) as response:
        total = int(response.headers.get("Content-Length") or 0)
        chunks, got, shown = [], 0, time.monotonic()
        while chunk := response.read(1 << 20):
            chunks.append(chunk)
            got += len(chunk)
            if time.monotonic() - shown >= 5:
                shown = time.monotonic()
                print(f"  downloaded {got >> 20} of {total >> 20 or '?'} MB", flush=True)
    return b"".join(chunks)


def install(source: str) -> int:
    """Fetch, check and unpack the archive into both checkouts. Exit 0 installed; 3 this commit has no prebuilt
    programs (its sources differ from the ones recorded: build from source); 1 a check failed."""
    m = manifest()
    for side, record in m["sides"].items():
        path = checkout(side)
        if not path.is_dir():
            print(f"prebuilt: the {side} checkout {path} is missing", file=sys.stderr)
            return 1
        for sub in ("lean", "rust"):
            if tree(path, sub) != record[f"{sub}_tree"]:
                print(f"prebuilt: the {side} checkout's {sub}/ sources are not the ones the prebuilt programs were "
                      f"built from, so they cannot be used here", file=sys.stderr)
                return 3
    print(f"prebuilt: fetching {source}", flush=True)
    data = fetch(source)
    if sha256(data) != m["archive_sha256"]:
        print(f"prebuilt: the archive's SHA-256 is {sha256(data)}, not the recorded {m['archive_sha256']}: refused",
              file=sys.stderr)
        return 1
    print(f"prebuilt: archive checked ({len(data) >> 20} MB, SHA-256 as recorded in tour/prebuilt.json)", flush=True)
    wanted = {f"{side}/{rel}": digest for side, record in m["sides"].items() for rel, digest in record["files"].items()}
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        members = tar.getmembers()
        if sorted(x.name for x in members) != sorted(wanted) or not all(x.isfile() for x in members):
            print("prebuilt: the archive does not hold exactly the recorded programs: refused", file=sys.stderr)
            return 1
        files = {x.name: tar.extractfile(x).read() for x in members}
    for name, body in files.items():
        if sha256(body) != wanted[name]:
            print(f"prebuilt: {name} is not the recorded program: refused", file=sys.stderr)
            return 1
    for name, body in sorted(files.items()):
        side, rel = name.split("/", 1)
        target = checkout(side) / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as tmp:
            tmp.write(body)
        os.chmod(tmp.name, 0o755)
        os.replace(tmp.name, target)
        print(f"prebuilt: installed {side} {rel}", flush=True)
    return 0


def scan_files(files: dict[str, bytes]) -> list[str]:
    """Every private detail in the printable strings of FILES: the public tree's own patterns
    (tests/test_public_tree_privacy.py's scan_line: account directories, e-mail addresses, key files, host names), and
    any home-directory path other than Lean's public build path."""
    sys.path.insert(0, str(ROOT / "tests"))
    try:
        from test_public_tree_privacy import mask, scan_line
    finally:
        sys.path.remove(str(ROOT / "tests"))
    where = {}  # each distinct string once (the programs share most of theirs), with the first program holding it
    for name, body in sorted(files.items()):
        for text in STRING.findall(body):
            where.setdefault(text, name)
    hits = []
    for text, name in sorted(where.items()):
        # Absolute home paths are checked below, with the narrow Lean build-path exemption. Counting them here too
        # would duplicate a private path and flag the public Lean paths before that exemption can apply.
        hits.extend(f"{name}: kind {kind} {mask(value)}" for kind, value in scan_line(text.decode("ascii"))
                    if kind != "e" or not value.startswith(("/ho" + "me/", "/Us" + "ers/")))
        for home in HOME_PATH.finditer(text):
            if not PUBLIC_HOME_PATH.match(text, home.start()):
                hits.append(f"{name}: home path {mask(home.group(0).decode('ascii'))}")
    return hits


def scan(archive: str) -> int:
    with tarfile.open(archive, mode="r:gz") as tar:
        files = {x.name: tar.extractfile(x).read() for x in tar.getmembers() if x.isfile()}
    hits = scan_files(files)
    for hit in hits:
        print(hit)
    print(f"{len(files)} programs scanned, {len(hits)} private details")
    return 1 if hits else 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["make"] and len(argv) == 2:
        return make(argv[1])
    if argv[:1] == ["install"] and len(argv) == 2:
        return install(argv[1])
    if argv[:1] == ["scan"] and len(argv) == 2:
        return scan(argv[1])
    if argv == ["url"]:
        print(url())
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
