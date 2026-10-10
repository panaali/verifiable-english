"""The tracked quarantine of tests that fail under machine load: tools/test-quarantine.json.

Each entry names one test (a node ID), the saved evidence that it fails under load and passes alone (a
JSON file in the repository whose `test` is that node ID), an owner, the day it was added and the day
it expires, at most `MAX_DAYS` later. An expired entry no longer applies: the test blocks again.

A quarantined test still runs everywhere. What the quarantine changes:

* the gate (`tools/gate.py`): a quarantined test that failed runs once more, alone and serially. If it
  passes there it no longer fails the gate, and the record keeps both outcomes (`quarantine`); if it
  fails again it fails the gate as before;
* an agent's selected run (`tools/select_tests.py --run`): its failure is reported as quarantined and
  does not count towards `--maxfail` or the exit status;
* the nightly runs with the quarantine off (`tools/gate.py --no-quarantine`): every failure blocks.

`python3 tools/quarantine.py` checks the file and lists the active and expired entries.
"""
from __future__ import annotations

import datetime
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools/test-quarantine.json"
VERSION = 1
MAX_DAYS = 7
FIELDS = ("test", "evidence", "owner", "added", "expires", "reason")


class QuarantineError(ValueError):
    """The quarantine file is malformed: nothing in it applies."""


def today() -> datetime.date:
    """The UTC day the quarantine is read on (tests pass their own day instead)."""
    return datetime.datetime.now(datetime.timezone.utc).date()


def _day(entry: dict, field: str, where: str) -> datetime.date:
    try:
        return datetime.date.fromisoformat(entry[field])
    except ValueError:
        raise QuarantineError(f"{where}: {field} {entry[field]!r} is not a YYYY-MM-DD day") from None


def load(path: Path | None = None, root: Path | None = None) -> list[dict]:
    """The entries of the quarantine file at `path` (default PATH), each checked, with evidence paths under
    `root` (default ROOT); any fault raises QuarantineError."""
    path, root = path or PATH, root or ROOT
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        raise QuarantineError(f"{path}: {exc}") from None
    if not isinstance(data, dict) or set(data) != {"version", "entries"}:
        raise QuarantineError(f"{path}: an object with exactly 'version' and 'entries'")
    if type(data["version"]) is not int or data["version"] != VERSION:
        raise QuarantineError(f"{path}: version {data['version']!r}, not {VERSION}")
    if not isinstance(data["entries"], list):
        raise QuarantineError(f"{path}: 'entries' is not a list")
    seen = set()
    for index, entry in enumerate(data["entries"]):
        where = f"{path.name} entry {index}"
        if not isinstance(entry, dict) or set(entry) != set(FIELDS):
            raise QuarantineError(f"{where}: an object with exactly the fields {', '.join(FIELDS)}")
        for field in FIELDS:
            if not isinstance(entry[field], str) or not entry[field].strip():
                raise QuarantineError(f"{where}: {field} is not a non-empty string")
        test = entry["test"]
        if not test.startswith("tests/") or "::" not in test or not test.split("::", 1)[0].endswith(".py"):
            raise QuarantineError(f"{where}: test {test!r} is not a test node ID (tests/<file>.py::<name>)")
        if test in seen:
            raise QuarantineError(f"{where}: {test} is quarantined twice")
        seen.add(test)
        added, expires = _day(entry, "added", where), _day(entry, "expires", where)
        if not added <= expires <= added + datetime.timedelta(days=MAX_DAYS):
            raise QuarantineError(f"{where}: expires {expires} is not within {MAX_DAYS} days after added {added}")
        evidence = Path(entry["evidence"])
        if evidence.is_absolute() or ".." in evidence.parts:
            raise QuarantineError(f"{where}: evidence {entry['evidence']!r} is not a path in the repository")
        try:
            saved = json.loads((root / evidence).read_text())
        except (OSError, ValueError) as exc:
            raise QuarantineError(f"{where}: evidence {entry['evidence']}: {exc}") from None
        if not isinstance(saved, dict) or saved.get("test") != test:
            raise QuarantineError(f"{where}: evidence {entry['evidence']} is not about {test}")
    return data["entries"]


def active(entries: list[dict], day: datetime.date) -> dict[str, dict]:
    """The entries that apply on `day` (added on or before it, expiring on or after it), by test."""
    return {entry["test"]: entry for entry in entries
            if datetime.date.fromisoformat(entry["added"]) <= day <= datetime.date.fromisoformat(entry["expires"])}


def expired(entries: list[dict], day: datetime.date) -> list[str]:
    return sorted(entry["test"] for entry in entries if datetime.date.fromisoformat(entry["expires"]) < day)


def main() -> int:
    try:
        entries = load()
    except QuarantineError as exc:
        print(f"invalid quarantine: {exc}", file=sys.stderr)
        return 1
    day = today()
    for test, entry in sorted(active(entries, day).items()):
        print(f"active until {entry['expires']}: {test} (owner {entry['owner']}; evidence {entry['evidence']})")
    for test in expired(entries, day):
        print(f"expired, blocks again: {test}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
