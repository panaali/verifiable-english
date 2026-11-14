"""Fetch each publisher document of usecases/pinned_sources.json at its sha256 pin and write its extracted text.

Usage: uv run python tools/fetch_pinned_sources.py [--home DIR] [--doc NAME ...] [--check]

For each document: download its URL, refuse bytes whose sha256 or size is not the pin, run the case's committed
extract step (pinned pypdf), refuse text whose sha256 or size is not the pin, then write the text at
<home>/<path>, where build_document.DEFAULT_SOURCE (Path.home() / path) looks. A text already stored there is
checked and kept; a stored text that differs from its pin is refused, never overwritten. --check downloads
nothing. Every document is tried; each one that cannot be pinned is named on a FAILED line and the exit status
is 1 (fail closed: no pin is changed and nothing falls back to another copy). Only hashes, sizes and URLs are
committed; the publisher's text exists only on the machine that fetched it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINS = ROOT / "usecases/pinned_sources.json"
REQUIRE = "VE_REQUIRE_PINNED_SOURCES"
SKIP_REASON = "the pinned source is not stored on this machine"
USER_AGENT = "ve-fetch-pinned-sources/1"
MAX_BYTES = 32_000_000
EXTRACT_TIMEOUT = 1800
KEYS = {"url": str, "pdf_sha256": str, "pdf_bytes": int, "extract": list, "path": str, "text_sha256": str,
        "text_bytes": int}


class FetchError(Exception):
    """A document that cannot be had at its pin."""


def load(pins: Path = PINS) -> dict[str, dict]:
    """The pinned documents by name, each entry exactly KEYS with their types; anything else is refused."""
    data = json.loads(pins.read_text(encoding="utf-8"))
    if data.get("version") != 1 or not isinstance(data.get("sources"), dict) or not data["sources"]:
        raise ValueError(f"{pins}: not a version 1 pins file with sources")
    for doc, entry in data["sources"].items():
        if not isinstance(entry, dict) or set(entry) != set(KEYS) or any(
                type(entry[k]) is not t for k, t in KEYS.items()):
            raise ValueError(f"{pins}: {doc}: the entry is not exactly {sorted(KEYS)} with their types")
        if Path(entry["path"]).is_absolute() or ".." in Path(entry["path"]).parts:
            raise ValueError(f"{pins}: {doc}: path must be relative to the home directory")
        if not all(isinstance(a, str) for a in entry["extract"]) or "{pdf}" not in entry["extract"] \
                or "{text}" not in entry["extract"]:
            raise ValueError(f"{pins}: {doc}: extract must be strings naming {{pdf}} and {{text}}")
    return data["sources"]


def required() -> bool:
    """True when VE_REQUIRE_PINNED_SOURCES=1: an absent pinned source is then a failure, not a skip."""
    return os.environ.get(REQUIRE) == "1"


def _identity(data: bytes) -> tuple[str, int]:
    return hashlib.sha256(data).hexdigest(), len(data)


def problem(doc: str, entry: dict, path: Path) -> str | None:
    """Why the text at `path` is not the pinned text of `doc`, or None when it is."""
    if not path.is_file():
        return f"the pinned source {doc} is not stored at {path}"
    got = _identity(path.read_bytes())
    if got != (entry["text_sha256"], entry["text_bytes"]):
        return (f"the pinned source {doc} at {path} has sha256 {got[0]} ({got[1]} bytes), not the pin "
                f"{entry['text_sha256']} ({entry['text_bytes']} bytes)")
    return None


def download(url: str, *, attempts: int = 3) -> bytes:
    """The bytes at `url` (https or, in tests, file), at most MAX_BYTES."""
    last = None
    for _ in range(attempts):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=120) as response:
                data = response.read(MAX_BYTES + 1)
            if len(data) > MAX_BYTES:
                raise FetchError(f"{url} serves more than {MAX_BYTES} bytes")
            return data
        except OSError as exc:  # URLError and timeouts; a wrong hash is never retried
            last = exc
    raise FetchError(f"{url} could not be downloaded: {last}")


def fetch(doc: str, entry: dict, home: Path, *, root: Path = ROOT) -> str:
    """Make <home>/<path> the pinned text of `doc`; the line to print. Raises FetchError naming the reason."""
    dest = home / entry["path"]
    if dest.exists() or dest.is_symlink():
        reason = problem(doc, entry, dest)
        if reason is not None:
            raise FetchError(f"{reason}; it is not overwritten")
        return f"ok {doc}: already stored at {dest}"
    data = download(entry["url"])
    got = _identity(data)
    if got != (entry["pdf_sha256"], entry["pdf_bytes"]):
        raise FetchError(f"{entry['url']} served sha256 {got[0]} ({got[1]} bytes), not the pin "
                         f"{entry['pdf_sha256']} ({entry['pdf_bytes']} bytes)")
    with tempfile.TemporaryDirectory(prefix="ve-pinned-") as directory:
        pdf, text = Path(directory) / "source.pdf", Path(directory) / "source.txt"
        pdf.write_bytes(data)
        argv = [{"{pdf}": str(pdf), "{text}": str(text)}.get(a, a) for a in entry["extract"]]
        done = subprocess.run(argv, cwd=root, capture_output=True, text=True, timeout=EXTRACT_TIMEOUT)
        if done.returncode != 0:
            raise FetchError(f"the extract step exited {done.returncode}: {(done.stderr or done.stdout)[-400:]}")
        reason = problem(doc, entry, text)
        if reason is not None:
            raise FetchError(f"the extract step does not reproduce the pin: {reason}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        part = dest.with_name(dest.name + ".part")
        part.write_bytes(text.read_bytes())
        os.replace(part, dest)
    return f"ok {doc}: {entry['url']} -> {dest} (sha256 {entry['text_sha256'][:12]}, {entry['text_bytes']} bytes)"


def main(argv: list[str] | None = None, *, pins: Path = PINS, root: Path = ROOT) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--doc", action="append", default=None)
    parser.add_argument("--check", action="store_true", help="download nothing; check the stored texts")
    args = parser.parse_args(argv)
    sources = load(pins)
    docs = args.doc or sorted(sources)
    failed = 0
    for doc in docs:
        try:
            if doc not in sources:
                raise FetchError(f"no pin named {doc} in {pins}")
            if args.check:
                reason = problem(doc, sources[doc], args.home / sources[doc]["path"])
                if reason is not None:
                    raise FetchError(reason)
                print(f"ok {doc}: stored at its pin", flush=True)
            else:
                print(fetch(doc, sources[doc], args.home, root=root), flush=True)
        except (FetchError, OSError, subprocess.SubprocessError) as exc:
            failed += 1
            print(f"FAILED {doc}: {exc}", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
