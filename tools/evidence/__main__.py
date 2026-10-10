"""python -m tools.evidence {scope,latency,ab,fuzz_ab,report} ...  (see tools/evidence/__init__.py)."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.evidence import ROOT, EvidenceError, dump, scope  # noqa: E402
from tools.evidence import ab, fuzz_ab, latency, report  # noqa: E402

COMMANDS = {"latency": latency.main, "ab": ab.main, "fuzz_ab": fuzz_ab.main, "report": report.main}


def scope_main(argv) -> int:
    parser = argparse.ArgumentParser(prog="python -m tools.evidence scope",
                                     description="Save the batch's scope: base..head --no-merges.")
    parser.add_argument("--base", default="main")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        saved = scope(args.base, args.head, ROOT)
    except EvidenceError as exc:
        print(exc)
        return 1
    dump(args.out, saved)
    print(f"scope {saved['base'][:8]}..{saved['head'][:8]}: {len(saved['commits'])} commit(s), "
          f"{len(saved['changes'])} path(s); {args.out}")
    return 0


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    commands = {"scope": scope_main, **COMMANDS}
    if not argv or argv[0] not in commands:
        print(f"usage: python -m tools.evidence {{{','.join(commands)}}} ...", file=sys.stderr)
        return 2
    return commands[argv[0]](argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
