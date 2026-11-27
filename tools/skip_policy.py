"""The one list of skipped tests a gate may pass, and the one check every gate applies to it.

The list is `optional_tests` in tools/gate-optional.json. Each row names a test (a node ID, or a pattern with
`*`), the text its skip message must contain (`reason`), who answers for it (`owner`) and the last UTC day it
applies (`expires`, YYYY-MM-DD). A skipped test passes only while a row matches its node ID and skip message and
that row has not expired; any other skip fails the run, as a failed test does, and so does an expired row's skip.

Every gate runs this check at the commit under test:

* the full gate (`tools/gate.py`: the train's candidate gates on Actions, the Mac and the VM, the nightlies) reads
  each skip from its pytest events (`permitted`);
* a selected run (`tools/select_tests.py --run`: the runner's selected shards, the Mac's and the VM's selected
  runs, the chain's selected route, the after-release light gate) reads each skip from its units' JUnit reports
  (`junit_skips`, `violations`).

`python3 tools/skip_policy.py` checks the file and lists the rows that expire within 7 days;
`python3 tools/skip_policy.py junit <report.xml>...` checks the skips of JUnit reports (exit 1 on any refused skip).
"""
from __future__ import annotations

import datetime
import fnmatch
import json
from pathlib import Path
import sys
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools/gate-optional.json"
FIELDS = ("nodeid", "reason", "owner", "expires")


class SkipPolicyError(ValueError):
    """The list is malformed: a gate that reads it refuses every skip."""


def today() -> datetime.date:
    """The UTC day the list is read on (tests pass their own day instead)."""
    return datetime.datetime.now(datetime.timezone.utc).date()


def expiry(entry: dict) -> datetime.date:
    try:
        return datetime.date.fromisoformat(entry["expires"])
    except (KeyError, TypeError, ValueError) as exc:
        raise SkipPolicyError(f"row {entry.get('nodeid')!r}: expires must be a YYYY-MM-DD day") from exc


def validate(policy: dict) -> list[dict]:
    """The rows of `policy` (the parsed file), each checked: every field a non-empty string, a valid expiry day."""
    rows = policy.get("optional_tests", []) if isinstance(policy, dict) else None  # no key: no skip allowed
    if not isinstance(rows, list):
        raise SkipPolicyError("optional_tests must be a list")
    for entry in rows:
        if not isinstance(entry, dict) or any(not isinstance(entry.get(field), str) or not entry[field].strip()
                                              for field in FIELDS):
            raise SkipPolicyError(f"row {entry!r}: needs non-empty {', '.join(FIELDS)}")
        expiry(entry)
    return rows


def load(path: Path = PATH) -> list[dict]:
    try:
        policy = json.loads(Path(path).read_text())
    except (OSError, ValueError) as exc:
        raise SkipPolicyError(f"cannot read {path}: {exc}") from exc
    return validate(policy)


def matches(nodeid: str, reason: str, entry: dict) -> bool:
    return ((fnmatch.fnmatchcase(nodeid, entry["nodeid"]) if "*" in entry["nodeid"] else nodeid == entry["nodeid"])
            and entry["reason"] in reason)


def verdict(nodeid: str, reason: str, entries: list[dict], day: datetime.date | None = None) -> str:
    """"allowed", "expired" (only expired rows match) or "unlisted" (no row matches)."""
    day = day or today()
    found = [entry for entry in entries if matches(nodeid, reason, entry)]
    if not found:
        return "unlisted"
    # A row without `expires` is only legal in callers' own lists (the gate's deselection rows): it never expires.
    return "allowed" if any("expires" not in entry or expiry(entry) >= day for entry in found) else "expired"


def permitted(nodeid: str, reason: str, entries: list[dict], day: datetime.date | None = None) -> bool:
    return verdict(nodeid, reason, entries, day) == "allowed"


def junit_skips(report: Path, unit: str | None = None) -> list[tuple[str, str]] | None:
    """(node ID, skip message) of every skipped case of a JUnit (xunit1) report; None when it is unreadable.

    The node ID is rebuilt from the case's class name, as tools/run_order.py `junit_cases` does: for a report of the
    test file `unit`, `<unit>::<class>::<name>`; without `unit` (or a case of another file), the class name's module
    path. A case of a module skipped whole names the module file."""
    try:
        tree = ElementTree.parse(report)
    except (OSError, ElementTree.ParseError):
        return None
    module = unit.removesuffix(".py").replace("/", ".") if unit else None
    found = []
    for case in tree.iter("testcase"):
        skipped = case.find("skipped")
        if skipped is None:
            continue
        name, classname = case.get("name") or "", case.get("classname") or ""
        if module and not classname and name == module:
            nodeid = unit
        elif module and classname == module:
            nodeid = f"{unit}::{name}"
        elif module and classname.startswith(module + "."):
            nodeid = "::".join([unit, *classname.removeprefix(module + ".").split("."), name])
        else:
            nodeid = file_nodeid(classname, name, case.get("file"))
        found.append((nodeid, " ".join(filter(None, [skipped.get("message"), skipped.text or ""]))))
    return found


def file_nodeid(classname: str, name: str, file: str | None) -> str:
    """The node ID of a case from its class name alone: the longest dotted prefix that is the test file's module."""
    if not classname:  # a module skipped whole: its case is named by the module's dotted path
        return name.replace(".", "/") + ".py"
    parts = classname.split(".")
    if file and file.endswith(".py"):
        module = file.removesuffix(".py").split("/")
        if parts[:len(module)] == module:
            return "::".join([file, *parts[len(module):], name])
    for cut in range(len(parts), 0, -1):
        candidate = "/".join(parts[:cut]) + ".py"
        if (ROOT / candidate).is_file():
            return "::".join([candidate, *parts[cut:], name])
    return f"{classname}::{name}"


def violations(skips: list[tuple[str, str]], entries: list[dict],
               day: datetime.date | None = None) -> list[tuple[str, str, str]]:
    """(node ID, verdict, message) of every skip in `skips` the list does not allow."""
    day = day or today()
    return [(nodeid, found, message) for nodeid, message in skips
            if (found := verdict(nodeid, message, entries, day)) != "allowed"]


def describe(refused: list[tuple[str, str, str]]) -> str:
    return "; ".join(f"{nodeid} ({'expired row' if found == 'expired' else 'not on tools/gate-optional.json'}: "
                     f"{' '.join(message.split())[:160]})" for nodeid, found, message in refused)


def main(argv: list[str]) -> int:
    try:
        entries = load()
    except SkipPolicyError as exc:
        print(f"skip policy: {exc}", file=sys.stderr)
        return 2
    if argv[:1] == ["junit"]:
        refused = []
        for report in argv[1:]:
            skips = junit_skips(Path(report))
            if skips is None:
                print(f"skip policy: no readable JUnit report {report}", file=sys.stderr)
                return 2
            refused += violations(skips, entries)
        for nodeid, found, message in refused:
            print(f"REFUSED SKIP ({found}): {nodeid}: {' '.join(message.split())[:200]}")
        print(f"skip policy: {len(refused)} refused skip(s)")
        return 1 if refused else 0
    if argv:
        print(__doc__, file=sys.stderr)
        return 2
    day = today()
    for entry in entries:
        left = (expiry(entry) - day).days
        if left < 7:
            print(f"{'EXPIRED' if left < 0 else f'expires in {left} d'}: {entry['nodeid']} "
                  f"(owner {entry['owner']}, {entry['expires']})")
    print(f"skip policy: {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
