"""A shared, keyed cache of lean-first A/B recordings (speed-abcache; PIPELINE-LIMITS L75).

    tools/lean_first_diff.py record --root DIR --out FILE --cache DIR    # reuse what was recorded, store what is not
    tools/lean_first_diff.py prewarm --commit SHA --cache DIR --workers N

A builder records the base commit of its A/B once per commit, not once per batch: `record --cache` (default
`$VE_AB_CACHE`; unset: off, and `record` runs as before) takes each (corpus, authority) segment from the cache when
it holds one recorded under the same key, records the others as before, writes the same lines in the same order, and
stores each segment it recorded. The key (`root_key` and `segment_key`) names what a segment's records depend on:

- `commit`: the --root checkout's HEAD. A root that `git status --porcelain` shows changed is neither looked up nor
  stored: it is recorded as before.
- `lean_build`: the root's Lean build key (`tools/lean_share.py key`: its `lean/` tree, toolchain, platform, Lake
  manifest, pins).
- `recorder`: the SHA-256 of this checkout's recorder (`RECORDER`: the record code, and `uv.lock`, the packages of the
  interpreter that runs it) and the Python version.
- `corpus`, `authority` and `corpus_sha256`: the segment, and the digest of the inputs its records read (`sources`:
  the corpus files and pilot documents whose digests the records carry, and the files a pilot document names beside it).
- `env`: every `VE_*` variable but the cache and build-store locations and the test runner's own (`UNKEYED`).

An entry `<cache>/v1/<SHA-256 of the key>/` holds `segment.jsonl` and `meta.json` (the key, the segment's SHA-256 and
line count, the checkers it was recorded with, when and where). The recording's scratch path (`<out>` without its
suffix, which a pilot diagnostic may quote) is stored as `SCRATCH` and given back as the reader's own. A segment is
stored only when the root is clean, the recording exited 0, the key is the same after the recording as before, the
checkers it ran are builds the root's lock pins, and it passes every check a hit must pass; it is written to a
temporary directory (files 0644) and renamed into place, and an entry is never rewritten. `prewarm` first removes the
entries not stored or used for `KEEP_DAYS` days.

A hit is used only when `meta.json` names this key and the segment's digest and line count, and the segment, read
back, is complete and checked as `compare` checks it (`check`): every line is one the recorder writes, in its
canonical form, of this corpus and authority, with the source digest of its case, and the segment holds every case
and operation of the corpus (`completeness`). Anything else is a miss, recorded as without a cache; an entry that
fails a check is moved to `<cache>/refused/`, so the segment recorded instead is stored.

Evidence tooling only: `compare` never reads the cache, and the merge train's gate (R2) and the nightlies (R3) never
call `record`.
"""
from __future__ import annotations

import contextlib
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

from tools import lean_first_diff as diff
from tools import lean_share

FORMAT = 1
RECORDER = ("tools/lean_first_diff.py", "tools/lean_first_cache.py", "uv.lock")
# Where caches and stores live, and the test runner's worker settings: no recording reads them.
UNKEYED = ("VE_AB_CACHE", "VE_LEAN_SHARE", "VE_TEST_")
SCRATCH = "<ab-scratch>"
KEEP_DAYS = 3  # `prewarm` removes the entries not stored or used for this long
CHECKERS = (("ve_service", "VE_LEAN_SERVICE", "lean/.lake/build/bin/ve_service"),
            ("rust_jsonl", "VE_RUST_JSONL", "rust/target/release/ve"))


class Miss(Exception):
    """No cached segment is used or stored; the message says why."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json_sha256(value) -> str:
    return _sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())


def say(text: str) -> None:
    print(f"[ab-cache] {text}", file=sys.stderr, flush=True)


def root_key(root: Path) -> dict:
    """The key parts every segment recorded in `root` shares (module docstring); Miss when `root` is not cached."""
    def git(*args):
        done = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
        if done.returncode:
            raise Miss(f"git {' '.join(args)}: {done.stderr.strip()[-300:]}")
        return done.stdout
    if git("status", "--porcelain"):
        raise Miss(f"{root} has uncommitted changes")
    try:
        lean = lean_share.key(root / "lean")
    except lean_share.Refused as exc:
        raise Miss(f"no Lean build key: {exc}") from None
    recorder = {name: _sha256((diff.ROOT / name).read_bytes()) if (diff.ROOT / name).is_file() else None
                for name in RECORDER}
    env = {name: value for name, value in sorted(os.environ.items())
           if name.startswith("VE_") and not name.startswith(UNKEYED)}
    return {"format": FORMAT, "commit": git("rev-parse", "HEAD").strip(), "lean_build": lean,
            "recorder": recorder, "python": sys.version, "env": env}


def segment_key(shared: dict, corpus: str, authority: str, corpus_sha256: str) -> dict:
    return json.loads(json.dumps({**shared, "corpus": corpus, "authority": authority,
                                  "corpus_sha256": corpus_sha256}))


def sources(corpus: str, root: Path, out: Path):
    """(the digest of the inputs `corpus`'s records read, the source digest the records of a case carry): the files
    the recorder reads them from, in the recorded root or in this checkout (`tools/lean_first_diff.py`)."""
    if corpus == "probe":
        digest = diff.digest(root / "tests/probe_matrix.py")
        return digest, lambda case: digest
    if corpus == "conformance":
        files = {name: diff.digest(root / f"conformance/{name}.json") for name in diff.CONFORMANCE}
        return _json_sha256(files), lambda case: files.get(case.split("/")[0])
    if corpus in ("readings", "rights", "norm_defaults", "document"):
        digest = diff.digest(out.with_suffix(f".{corpus}.json"))
        return digest, lambda case: digest
    if corpus in ("discourse", "quantity"):
        entries, source, path = ((diff.discourse_corpus(diff.ROOT), diff.discourse_source, diff.DISCOURSE)
                                 if corpus == "discourse" else
                                 (diff.quantity_corpus(diff.ROOT), diff.quantity_source, diff.QUANTITY))
        by_case = {entry["id"]: source(entry) for entry in entries}
        return diff.digest(diff.ROOT / path), by_case.get
    assert corpus == "pilots", corpus
    documents = diff.pilot_documents(diff.ROOT)
    blobs = {name: blob for name, blob, _ in documents}
    beside = {name: {target: _sha256(data) for target, data in diff.pilot_companions(diff.ROOT, name, text).items()}
              for name, _, text in documents}
    return _json_sha256([blobs, beside]), blobs.get


def _stem(out: Path) -> str:
    stem = str(out.with_suffix(""))
    if json.dumps(stem, ensure_ascii=False)[1:-1] != stem or SCRATCH in stem:
        raise Miss(f"the output path {stem!r} is quoted differently in JSON")
    return stem + "."


def check(text: str, corpus: str, authority: str, source_of) -> None:
    """Miss unless `text` is a complete segment `record` writes for `corpus` and `authority` (module docstring)."""
    name = f"the cached {corpus}/{authority} segment"
    try:
        records = diff.load_text(text, name)
        if not text.endswith("\n"):
            raise Miss(f"{name} does not end with a whole line")
        for line in text.split("\n")[:-1]:
            row = json.loads(line)
            if diff.line(row) != line + "\n":
                raise Miss(f"{name} holds a line the recorder does not write: {line[:120]}")
            if (row["corpus"], row["authority"]) != (corpus, authority):
                raise Miss(f"{name} holds a record of {row['corpus']}/{row['authority']}")
            if row["source_sha256"] != source_of(row["case"]):
                raise Miss(f"{name} holds a record of {row['case']} read from another source")
        diff.completeness(name, records, diff.expected_cases(diff.ROOT, [corpus], [authority]))
    except diff.Unusable as exc:
        raise Miss(str(exc)) from None


def lookup(cache: Path, key: dict, source_of, out: Path) -> str:
    """The text of the segment stored under `key`, as a recording into `out` writes it; Miss on any doubt."""
    entry = cache / "v1" / _json_sha256(key)
    if not entry.is_dir():
        raise Miss(f"no entry {entry.name[:16]}")
    try:
        text = _read(entry, key, source_of, out)
    except Miss:
        # a damaged entry is set aside, so that the segment recorded now is stored in its place
        refused = cache / "refused" / f"{entry.name}-{os.getpid()}-{datetime.datetime.now():%Y%m%dT%H%M%S%f}"
        refused.parent.mkdir(parents=True, exist_ok=True)
        with contextlib.suppress(OSError):  # another reader may have set it aside first
            os.rename(entry, refused)
        raise
    with contextlib.suppress(OSError):
        os.utime(entry)  # used now: `prune` keeps it
    return text


def _read(entry: Path, key: dict, source_of, out: Path) -> str:
    try:
        meta = json.loads((entry / "meta.json").read_text())
        data = (entry / "segment.jsonl").read_bytes()
        text = data.decode()
    except (OSError, ValueError) as exc:
        raise Miss(f"no readable entry {entry.name[:16]}: {exc}") from None
    if type(meta) is not dict or not diff.same(meta.get("key"), key):
        raise Miss(f"the entry {entry.name[:16]} names another key")
    if meta.get("sha256") != _sha256(data) or meta.get("records") != data.count(b"\n"):
        raise Miss(f"the entry {entry.name[:16]} is not the segment stored")
    text = text.replace(SCRATCH + ".", _stem(out))
    check(text, key["corpus"], key["authority"], source_of)
    return text


def pinned_checkers(root: Path) -> dict:
    """The digests of the checkers a recording in `root` runs; Miss unless `root`'s lock pins each."""
    try:
        lock = json.loads((root / "lean/checkers.lock").read_text())
    except (OSError, ValueError) as exc:
        raise Miss(f"no readable lock in {root}: {exc}") from None
    found = {}
    for name, variable, default in CHECKERS:
        path = Path(os.environ.get(variable) or root / default)
        found[name] = _sha256(path.read_bytes()) if path.is_file() else None
        if found[name] is None or found[name] not in lock.get(name, ()):
            raise Miss(f"{path} is not a {name} build {root}'s lock pins")
    return found


def store(cache: Path, key: dict, text: str, out: Path, checkers: dict) -> Path:
    """Store a checked segment under `key` (module docstring); the entry. An entry is never rewritten."""
    entry = cache / "v1" / _json_sha256(key)
    if entry.is_dir():
        return entry
    if SCRATCH in text:
        raise Miss(f"the segment holds {SCRATCH}")
    data = text.replace(_stem(out), SCRATCH + ".").encode()
    entry.parent.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix="tmp-", dir=entry.parent))
    try:
        (scratch / "segment.jsonl").write_bytes(data)
        meta = {"format": FORMAT, "key": key, "sha256": _sha256(data), "records": data.count(b"\n"),
                "unavailable": sum(diff._unavailable(json.loads(line)["outcome"]) for line in text.split("\n")[:-1]),
                "checkers": checkers, "stored": {"at": datetime.datetime.now(datetime.timezone.utc).isoformat(
                    timespec="seconds"), "host": platform.node(), "load": list(os.getloadavg())}}
        (scratch / "meta.json").write_text(json.dumps(meta, indent=1, sort_keys=True) + "\n")
        for path in (scratch / "segment.jsonl", scratch / "meta.json"):
            os.chmod(path, 0o644)
        os.chmod(scratch, 0o755)
        try:
            os.rename(scratch, entry)
        except OSError:
            if not entry.is_dir():
                raise
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    return entry


def record(args, cache: Path) -> int:
    """`tools/lean_first_diff.py record --cache`: the recording `record` writes, its segments taken from `cache` where
    it holds them under their key, the others recorded and stored."""
    root, out, cache = Path(args.root).resolve(), Path(args.out).resolve(), cache.resolve()
    segments = [(corpus, authority) for corpus in args.corpus
                for authority in diff.authorities_of(corpus, args.authority)]
    out.write_text("")
    texts, keys = {}, {}
    try:
        shared = root_key(root)
        _stem(out)
    except Miss as exc:
        say(f"off: {exc}")
        shared = None
    for corpus in dict.fromkeys(corpus for corpus, _ in segments) if shared else ():
        corpus_sha256, source_of = sources(corpus, root, out)
        for authority in diff.authorities_of(corpus, args.authority):
            key = keys[corpus, authority] = (segment_key(shared, corpus, authority, corpus_sha256), source_of)
            try:
                texts[corpus, authority] = lookup(cache, key[0], source_of, out)
                say(f"hit {corpus}/{authority}")
            except Miss as exc:
                say(f"miss {corpus}/{authority}: {exc}")
    missed = [segment for segment in segments if segment not in texts]
    groups: dict[tuple, list] = {}
    for corpus, authority in missed:
        authorities = tuple(args.authority) if authority == "default" else tuple(
            name for name in args.authority if (corpus, name) in missed)
        groups.setdefault(authorities, [])
        if corpus not in groups[authorities]:
            groups[authorities].append(corpus)
    for number, (authorities, corpora) in enumerate(groups.items()):
        part = out.with_name(f"{out.name}.part{number}")
        code = diff.run_child(root, part, corpora, authorities, args.workers, scratch=out)
        if code:
            return code
        text = part.read_text()
        if text and not text.endswith("\n"):
            return 2
        lines: dict[tuple, list] = {}
        for line in text.split("\n")[:-1]:  # not `splitlines`: a record's strings may hold U+2028, U+0085, ...
            row = json.loads(line)
            if (row["corpus"], row["authority"]) not in missed:
                say(f"the recording holds a record of {row['corpus']}/{row['authority']}, which was not recorded")
                return 2
            lines.setdefault((row["corpus"], row["authority"]), []).append(line + "\n")
        texts.update((segment, "".join(found)) for segment, found in lines.items())
        part.unlink()
    out.write_text("".join(texts.get(segment, "") for segment in segments))
    if shared and missed:
        try:
            if root_key(root) != shared:
                raise Miss(f"{root}, its Lean build, the recorder or the environment changed while recording")
            checkers = pinned_checkers(root)
        except Miss as exc:
            say(f"nothing stored: {exc}")
            return 0
        for segment in missed:
            try:
                check(texts.get(segment, ""), *segment, keys[segment][1])
                say(f"stored {'/'.join(segment)} in {store(cache, keys[segment][0], texts[segment], out, checkers)}")
            except Miss as exc:
                say(f"not stored {'/'.join(segment)}: {exc}")
    return 0


def prune(cache: Path, days: float = KEEP_DAYS) -> None:
    """Remove the entries not stored or used for `days` days, the entries set aside, and stores left unfinished."""
    old = datetime.datetime.now().timestamp() - days * 86400
    for path in [*(cache / "v1").glob("*"), *(cache / "refused").glob("*")]:
        if path.parent.name == "refused" or path.stat().st_mtime < old:
            shutil.rmtree(path, ignore_errors=True)


def prewarm(commit: str, cache: Path, workers: int, repo: Path = diff.ROOT) -> int:
    """Record every corpus of `commit` into `cache`: a worktree of it, its Lean build restored from the shared store
    (`tools/lean_share.py restore`; else `lake build`), its Rust checker built, then that commit's own
    `record --cache`. Segments already stored are hits, so a second run records nothing."""
    cache = cache.resolve()
    cache.mkdir(parents=True, exist_ok=True)
    prune(cache)
    work = Path(tempfile.mkdtemp(prefix="prewarm-", dir=cache))
    tree = work / "root"
    env = {**os.environ, "PATH": f"{Path.home() / '.elan/bin'}{os.pathsep}{os.environ.get('PATH', '')}"}
    try:
        subprocess.run(["git", "worktree", "add", "--detach", str(tree), commit], cwd=repo, check=True)
        if not (tree / "tools/lean_first_cache.py").is_file():
            say(f"{commit} has no base-record cache: nothing recorded")
            return 2
        if subprocess.run([sys.executable, "tools/lean_share.py", "restore"], cwd=tree, env=env).returncode:
            subprocess.run(["lake", "build"], cwd=tree / "lean", env=env, check=True)
        subprocess.run([sys.executable, "tools/rust_build.py"], cwd=tree, env=env, check=True)
        return subprocess.run([sys.executable, "tools/lean_first_diff.py", "record", "--root", str(tree),
                               "--out", str(work / "base.jsonl"), "--cache", str(cache), "--workers", str(workers)],
                              cwd=tree, env=env).returncode
    except subprocess.CalledProcessError as exc:
        say(f"prewarm of {commit} failed: {exc}")
        return 2
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(tree)], cwd=repo, capture_output=True)
        shutil.rmtree(work, ignore_errors=True)
