"""Replay stored `ve_service` answers against a build.

* `store-replay --store DIR [--executable PATH]` (the answer store's nightly check, tests/answer_store.py):
  every entry the store holds for the build at PATH (default: the lake build), its exact request line sent
  to that build and the answer compared with the stored response byte for byte. Exit 1 on any difference or
  unreadable entry; the JSON result goes to stdout (or `--output`). It runs after the nightly's
  `tools/gate.py --no-quarantine`, never in place of it: the gate never reads the store.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


# The answer store's byte replay

def store_replay(arguments: list[str]) -> int:
    from tests import answer_store
    from ve.backends.lean_service import DEFAULT_EXECUTABLE
    parser = argparse.ArgumentParser(prog="answer_replay.py store-replay",
                                     description="replay the answer store against its build, byte for byte")
    parser.add_argument("--store", required=True, type=Path, help="the store's directory")
    parser.add_argument("--executable", type=Path, default=DEFAULT_EXECUTABLE, help="the build to replay against")
    parser.add_argument("--allow-unlisted-build", action="store_true",
                        help="replay a build lean/checkers.lock does not pin (tests)")
    parser.add_argument("--jobs", type=int, default=4, help="service processes in parallel")
    parser.add_argument("--output", type=Path, help="write the JSON result here")
    options = parser.parse_args(arguments)
    result = answer_store.replay(options.store, options.executable,
                                 allow_unlisted_build=options.allow_unlisted_build, jobs=options.jobs)
    text = json.dumps(result, indent=1, sort_keys=True) + "\n"
    if options.output:
        options.output.write_text(text)
    else:
        sys.stdout.write(text)
    print(f"store-replay: build {result['build'][:12]}: {result['same']} of {result['entries']} entries the same, "
          f"{len(result['different'])} different, {len(result['unreadable'])} unreadable; "
          f"{len(result['other_builds'])} other builds not replayed", file=sys.stderr)
    return 0 if result["ok"] else 1


COMMANDS = {"store-replay": store_replay}


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] not in COMMANDS:
        print(f"usage: answer_replay.py {{{','.join(COMMANDS)}}} ...", file=sys.stderr)
        return 2
    return COMMANDS[argv[0]](argv[1:])


if __name__ == "__main__":
    sys.exit(main())
