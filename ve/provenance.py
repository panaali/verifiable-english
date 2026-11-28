# ve-layer: 4 (what an answer was made from: hashes of the files, commits and the record of who did what)
"""The provenance block of an answer: what it was made from, and who translated, checked and signed off its text.

`ve ask --json` carries the block as its `provenance` member on every answer (both routes), the staged route
(`ve/staged_ask.py`) prints it after every answer it prints, `ve ask --provenance` prints it after a ve-document's
answer, and `python -m ve provenance PATH` prints it for a text answered by another checkout (tour stop 7 runs its
answers on branch after-release). The block holds
- `source`: the outside text the translation was made from, each file with its SHA-256 (computed from the file when it
  is in the checkout; else the SHA-256 recorded when it was pinned, marked `recorded`); `none: ...` for a text written
  in VE's English (it has no outside source);
- `translation`: the files VE reads (a ve-document, or a staged route's `translation.py`), each with its SHA-256
  computed now, and the commit at which the translation was frozen with whether it has changed since;
- `ve_commit`: the commit of the checkout that answered (`git rev-parse HEAD`), and whether its tracked files differ
  from that commit;
- `checker`: the Lean build that checked the answer (the `ve_service` executable and its SHA-256), `not run` when the
  caller skipped Lean;
- `date`: when the block was made (UTC, to the second);
- the three role lines, `translated_by`, `checked_by`, `signed_off_by`, as the text's record says.
Nothing here is guessed: the per-text facts (source files, freeze commit, roles) are read from the record file
`provenance_records.json` beside this module, keyed by the text's path inside its checkout; a text the record does not
list, or a value that cannot be computed (no git, no such commit, no checker executable), is `unknown`. This module
proves nothing and decides nothing; it reads files and git.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
RECORDS = Path(__file__).resolve().with_name("provenance_records.json")
CHECKER = Path("lean/.lake/build/bin/ve_service")  # the Lean service the answers' certificates go to, in a checkout
UNKNOWN = "unknown"
ROLES = (("translated_by", "Translated by"), ("checked_by", "Checked by"), ("signed_off_by", "Signed off by"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _git(root: Path, *args: str) -> str | None:
    """git's output in `root`, stripped; None when git fails or is missing."""
    try:
        done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return done.stdout.decode("utf-8", "replace").strip() if done.returncode == 0 else None


def checkout_of(path: Path) -> Path | None:
    """The top of the git checkout holding `path`, or None."""
    top = _git(path if path.is_dir() else path.parent, "rev-parse", "--show-toplevel")
    return Path(top) if top else None


def records(file: Path | None = None) -> dict:
    """The record file's texts (path inside the checkout -> record); {} when it cannot be read."""
    try:
        data = json.loads((file or RECORDS).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    texts = data.get("texts") if type(data) is dict else None
    return texts if type(texts) is dict else {}


def _file(root: Path, name: str) -> dict:
    path = root / name
    return {"file": name, "sha256": sha256(path) if path.is_file() else UNKNOWN}


def _source(root: Path, record: dict | None):
    if record is None or "source" not in record:
        return UNKNOWN
    source = record["source"]
    if type(source) is str:
        return source
    out = []
    for item in source:
        path = root / item["file"]
        if path.is_file():
            out.append({"file": item["file"], "sha256": sha256(path)})
        elif type(item.get("sha256")) is str:
            out.append({"file": item["file"], "sha256": item["sha256"], "recorded": item.get("kept", "yes")})
        else:
            out.append({"file": item["file"], "sha256": UNKNOWN})
    return out


def _freeze(root: Path, record: dict | None, files: list[dict]) -> dict:
    commit = record.get("freeze_commit") if record else None
    if type(commit) is not str:
        return {"freeze_commit": UNKNOWN, "changed_since_freeze": UNKNOWN}
    changed = UNKNOWN
    frozen = []
    for item in files:
        try:
            done = subprocess.run(["git", "-C", str(root), "show", f"{commit}:{item['file']}"], capture_output=True,
                                  timeout=30)
        except (OSError, subprocess.SubprocessError):
            break
        if done.returncode != 0:
            break
        frozen.append(hashlib.sha256(done.stdout).hexdigest())
    else:
        if files and all(item["sha256"] != UNKNOWN for item in files):
            changed = "no" if frozen == [item["sha256"] for item in files] else "yes"
    return {"freeze_commit": commit, "changed_since_freeze": changed}


def _commit(root: Path | None) -> dict:
    # only the top of a checkout has a commit of its own (an installed copy of `ve` inside another repository has not)
    head = _git(root, "rev-parse", "HEAD") if root and checkout_of(root) == root else None
    if head is None:
        return {"ve_commit": UNKNOWN, "ve_tree_changed": UNKNOWN}
    status = _git(root, "status", "--porcelain", "--untracked-files=no")
    return {"ve_commit": head, "ve_tree_changed": UNKNOWN if status is None else ("yes" if status else "no")}


def _checker(root: Path | None, lean: bool):
    if not lean:
        return "not run"
    if root is None or checkout_of(root) != root:
        return UNKNOWN
    configured = os.environ.get("VE_LEAN_SERVICE") if root.resolve() == ROOT else None
    path = Path(configured) if configured else root / CHECKER
    if not path.is_file():
        return UNKNOWN
    from .backends.lean_service import executable_sha256
    shown = str(CHECKER) if not configured else str(path)
    return {"file": shown, "sha256": executable_sha256(path)}


def block(text: Path, *, root: Path | None = None, lean: bool = True, now: datetime.datetime | None = None,
          record_file: Path | None = None) -> dict:
    """The provenance block of an answer made from `text` (a ve-document file or a staged-route directory) by the
    checkout `root` (default: the checkout holding `text`); `lean` False when the caller skipped Lean. The
    translation's files are the record's, else `text` itself for a file and its `translation.py` for a directory."""
    text = Path(text).resolve()
    top = checkout_of(text)
    key = text.relative_to(top).as_posix() if top and text.is_relative_to(top) else None
    record = records(record_file).get(key) if key else None
    if type(record) is not dict:
        record = None
    base = top if key else text.parent
    if record and type(record.get("translation")) is list:
        names = [str(name) for name in record["translation"]]
    else:
        names = [p.relative_to(base).as_posix() for p in ([text / "translation.py"] if text.is_dir() else [text])]
    files = [_file(base, name) for name in names]
    answered_by = Path(root).resolve() if root is not None else top
    stamp = (now or datetime.datetime.now(datetime.timezone.utc)).astimezone(datetime.timezone.utc)
    roles = record.get("roles") if record else None
    return {"source": _source(base, record),
            "translation": {"files": files, **_freeze(base, record, files)},
            **_commit(answered_by),
            "checker": _checker(answered_by, lean),
            "date": stamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
            **{key: (roles.get(key) if type(roles) is dict and type(roles.get(key)) is str else UNKNOWN)
               for key, _ in ROLES}}


def _hashed(item) -> str:
    if type(item) is not dict:
        return str(item)
    text = f"{item['file']} sha256 {item['sha256']}"
    if "recorded" in item:
        text += f" (recorded; {item['recorded']})"
    return text


def lines(provenance: dict, heading: str = "Provenance of this answer:") -> list[str]:
    """The block as printed text."""
    out = [heading]
    source = provenance["source"]
    for item in (source if type(source) is list else [source]):
        out.append(f"  Source: {_hashed(item)}")
    translation = provenance["translation"]
    for item in translation["files"]:
        out.append(f"  Translation: {_hashed(item)}")
    out.append(f"  Translation frozen at commit: {translation['freeze_commit']}; changed since: "
               f"{translation['changed_since_freeze']}")
    out.append(f"  VE commit: {provenance['ve_commit']}; tracked files changed since: {provenance['ve_tree_changed']}")
    out.append(f"  Checker (Lean build): {_hashed(provenance['checker'])}")
    out.append(f"  Date: {provenance['date']}")
    out.extend(f"  {label}: {provenance[key]}" for key, label in ROLES)
    return out


def main(argv=None) -> int:
    import argparse
    parser = argparse.ArgumentParser(
        prog="python -m ve provenance",
        description="Print the provenance block of answers made from a text (a ve-document file or a staged-route "
                    "directory) by the checkout that holds it: its source and translation hashes, the checkout's "
                    "commit and Lean build, the date and who translated, checked and signed off the text.")
    parser.add_argument("text", help="the ve-document file or staged-route directory the answers were read from")
    parser.add_argument("--json", action="store_true", help="print the block as JSON")
    options = parser.parse_args(argv)
    text = Path(options.text)
    if not text.exists():
        print(f"no such file or directory: {options.text}", file=sys.stderr)
        return 2
    provenance = block(text)
    if options.json:
        print(json.dumps({"provenance": provenance}, ensure_ascii=False, indent=2))
    else:
        print("\n".join(lines(provenance, "Provenance of the answers above (their text, and the checkout that "
                                          "answered them):")))
    return 0
