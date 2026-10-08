"""Admission cost of a readings document under the unspecified completion (RD-2a report; review B2).

Usage: python docs/readings-defaults/rd2a/latency.py OUT --before PATH --before-sha256 HEX [--sizes 30,44,60]
                                                     [--calls 2]

The document is F-ND1's open set (`tests/test_readings_nd_lean.py`) beside `n` fixed rules spread over 20 extra
regulated pairs. Three requests per size: `readings-validate` with every completion `deny` (still the completion's
route, whose checks are then trivial, so the author's admission is most of the cost), and `readings-validate` and
`readings-elaborate` with unspecified completions. Before review B2 both validates admitted the author's document
twice. Each request is sent to two `ve_service` builds, this tree's and the
one `--before` names (pinned by its SHA-256; the build lock of this tree need not list it), in turn, and timed as the
service process's CPU (every thread's user and system time, `/proc/<pid>/stat`) after one warm-up call; the two
builds' answers must be the same.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from tests import test_readings_nd_lean as nd  # noqa: E402
from tests.test_readings_s1_lean import norm  # noqa: E402
from ve.backends.lean_service import LeanService  # noqa: E402
from ve.readings_s1 import wire  # noqa: E402

VERBS = ["assist", "call", "greet", "inform", "warn", "thank", "visit", "notify", "contact", "answer",
         "teach", "guide", "serve", "protect", "support", "advise", "remind", "invite", "welcome", "train"]


def environment(completion: str) -> dict:
    raw = nd.env1(completion=completion)
    predicates = raw["vocabulary"]["predicates"]
    for i, verb in enumerate(VERBS):
        predicates[f"p{i}_required"] = {"arguments": ["agent", "user"], "description": "obligation",
                                        "regulated": nd.regulated("obligation", completion, "{0} %s {1}" % verb,
                                                                  permission=f"p{i}_permitted")}
        predicates[f"p{i}_permitted"] = {"arguments": ["agent", "user"], "description": "permission",
                                         "regulated": nd.regulated("permission", completion, "{0} %s {1}" % verb)}
    return raw


def document(raw: dict, n: int, completion: str) -> dict:
    if completion == "unspecified":
        base = nd.base1([["a", "u"]])
        for i in range(len(VERBS)):
            base["relations"][f"unsaid__p{i}_permitted"] = [["a", "u"]]
            base["relations"][f"unsaid__p{i}_required"] = []
    else:
        base = {"domains": {"agent": ["a"], "user": ["u"]}, "constants": {}, "relations": {"asks": []}}
    doc, _ = nd.doc1(raw, nd.entry(base, "every", nd.PROBE1, True))
    doc["units"] += [{"id": f"f{i}", "kind": "norm", "content": norm(f"rule{i}", f"p{i % len(VERBS)}_required", True)}
                     for i in range(n)]
    return doc


def cpu_seconds(pid: int) -> float:
    """User and system time of every thread of the process (fields 14 and 15 of `/proc/<pid>/stat`)."""
    fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
    return (int(fields[11]) + int(fields[12])) / os.sysconf("SC_CLK_TCK")


def timed(service: LeanService, case: dict, calls: int) -> tuple[float, list]:
    rows = service.run("readings-route", [case])
    assert rows[0].get("status") == "ok", rows
    before = cpu_seconds(service.pid)
    for _ in range(calls):
        service.run("readings-route", [case])
    return round((cpu_seconds(service.pid) - before) / calls, 2), rows


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("out")
    parser.add_argument("--before", required=True)
    parser.add_argument("--before-sha256", required=True)
    parser.add_argument("--sizes", default="30,44,60")
    parser.add_argument("--calls", type=int, default=2)
    args = parser.parse_args()
    sizes = [int(s) for s in args.sizes.split(",")]
    after = ROOT / "lean/.lake/build/bin/ve_service"
    rows = []
    with LeanService(timeout=3600, executable=args.before, expected_sha256=args.before_sha256,
                     allow_unlisted_build=True) as old, LeanService(timeout=3600) as new:
        for n in sizes:
            row = {"fixed_units": n}
            for label, completion, kind in (("s1_only", "deny", "readings-validate"),
                                            ("validate", "unspecified", "readings-validate"),
                                            ("elaborate", "unspecified", "readings-elaborate")):
                raw = environment(completion)
                case = {"id": label, "kind": kind, "environment": wire(raw),
                        "document": wire(document(raw, n, completion))}
                (t_old, a_old), (t_new, a_new) = timed(old, case, args.calls), timed(new, case, args.calls)
                assert a_old == a_new, (n, label)
                row[label] = {"before": t_old, "after": t_new}
            rows.append(row)
            print(json.dumps(row), flush=True)
    Path(args.out).write_text(json.dumps({
        "method": " ".join(__doc__.split("\n\n")[2].split()), "calls": args.calls,
        "before_build": sha256(Path(args.before)), "after_build": sha256(after), "rows": rows}, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
