"""Cost of `readings-elaborate` under the unspecified completion before and after RD-2b (RD-2b report).

Usage: python docs/readings-defaults/rd2b/latency.py OUT --before PATH --before-sha256 HEX --after PATH
                                                     [--sizes 10,20,30] [--calls 3]

RD-2b adds the filled document (`fill_premises`, `filled`) to the completion's `readings-elaborate` row, which
`ve document` asks at every load of such a document. The documents are RD-2a's (`../rd2a/latency.py`: F-ND1's open
set beside `n` fixed rules over 20 extra regulated pairs, every completion `unspecified`). Each request is sent to
the two `ve_service` builds `--before` and `--after` names (each pinned by its SHA-256 for `--before`; the build lock
need not list either), in turn, and timed as the service process's CPU after one warm-up call, as RD-2a times it.
The after row must be the before row with the two fields added, and they must be `readings-validate`'s.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from ve.backends.lean_service import LeanService  # noqa: E402
from ve.readings_s1 import wire  # noqa: E402

_spec = importlib.util.spec_from_file_location("rd2a_latency", ROOT / "docs/readings-defaults/rd2a/latency.py")
rd2a = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rd2a)
FILLED = ("fill_premises", "filled")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("out")
    parser.add_argument("--before", required=True)
    parser.add_argument("--before-sha256", required=True)
    parser.add_argument("--after", required=True)
    parser.add_argument("--sizes", default="10,20,30")
    parser.add_argument("--calls", type=int, default=3)
    args = parser.parse_args()
    rows = []
    with LeanService(timeout=3600, executable=args.before, expected_sha256=args.before_sha256,
                     allow_unlisted_build=True) as old, \
            LeanService(timeout=3600, executable=args.after, expected_sha256=rd2a.sha256(Path(args.after)),
                        allow_unlisted_build=True) as new:
        for n in [int(s) for s in args.sizes.split(",")]:
            raw = rd2a.environment("unspecified")
            document = wire(rd2a.document(raw, n, "unspecified"))
            case = {"id": "elaborate", "kind": "readings-elaborate", "environment": wire(raw), "document": document}
            (t_old, [a_old]), (t_new, [a_new]) = rd2a.timed(old, case, args.calls), rd2a.timed(new, case, args.calls)
            [validated] = new.run("readings-route", [{**case, "id": "validate", "kind": "readings-validate"}])
            assert {k: v for k, v in a_new.items() if k not in FILLED} == a_old, n
            assert all(a_new[k] == validated[k] for k in FILLED), n
            rows.append({"fixed_units": n, "elaborate": {"before": t_old, "after": t_new}})
            print(json.dumps(rows[-1]), flush=True)
    Path(args.out).write_text(json.dumps({
        "method": " ".join(__doc__.split("\n\n")[2].split()), "calls": args.calls,
        "before_build": rd2a.sha256(Path(args.before)), "after_build": rd2a.sha256(Path(args.after)),
        "rows": rows}, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
