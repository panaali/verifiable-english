"""Run the three keyed harnesses under the path recorder and save `docs/usecases/keyed-answers.json`.

`usecases/keyed_paths.py` holds the recorder, the evidence path and the harness files; this script runs each
harness's `run()` under it, each in a fresh interpreter, because the harnesses share sibling module names
(`stage0`). `uv run python usecases/measure_keyed_paths.py --write` regenerates the evidence.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_SPEC = importlib.util.spec_from_file_location("keyed_paths", HERE / "keyed_paths.py")
keyed_paths = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(keyed_paths)
_MARK = "KEYED-PATHS "


def measure(harness: str) -> dict:
    """The paths one harness's `run()` takes, sorted by name."""
    path = keyed_paths.HARNESSES[harness]
    sys.path.insert(0, str(path.parent))
    try:
        spec = importlib.util.spec_from_file_location(f"keyed_paths_{harness.replace('-', '_')}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with keyed_paths.recording() as counts:
            module.run()
    finally:
        sys.path.remove(str(path.parent))
    return dict(sorted(counts.items()))


def measured(harness: str) -> dict:
    """`measure(harness)` in a fresh interpreter: the harnesses share sibling module names (`stage0`)."""
    done = subprocess.run([sys.executable, __file__, "--harness", harness], cwd=HERE.parent,
                          check=True, capture_output=True, text=True)
    return json.loads(done.stdout.rsplit(_MARK, 1)[1])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true", help=f"write {keyed_paths.EVIDENCE.name}")
    parser.add_argument("--harness", choices=keyed_paths.HARNESSES, help="measure one harness and print its paths")
    args = parser.parse_args(argv)
    if args.harness:
        print(_MARK + json.dumps(measure(args.harness)))
        return 0
    evidence = {name: measured(name) for name in keyed_paths.HARNESSES}
    text = json.dumps(evidence, indent=1, sort_keys=True) + "\n"
    if args.write:
        keyed_paths.EVIDENCE.write_text(text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
