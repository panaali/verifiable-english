"""kb-2a-b part (4): each unit's status as `ve document check` answers it, for the fixtures whose documents reached the
two routed refusals of `Service/Document.lean` before this item.

    uv run python docs/kernel/kb-2a-b/status_compare.py --probes   # writes probes/JT-a.ve.md and probes/SC-a.ve.md
    uv run python docs/kernel/kb-2a-b/status_compare.py --phase before|after

`--probes` cuts the two fsf-r2 probe documents (JT-a, SC-a) from the pinned DeepMind source exactly as
usecases/safety-framework/measure_r2.py builds them, and saves them here so the comparison and its tests read files.
`--phase` runs `ve document check` (Python's CLI path: `load_document` then `check_document`) on the four fixtures and
records, per fixture, each unit's status or the refusal, under that phase in status-compare.json. It records what it
sees; it never adjusts either side."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / "status-compare.json"
FIXTURES = {
    "rd9-docroute": ROOT / "tests/data/rd9-docroute.ve.md",
    "JT-a": HERE / "probes/JT-a.ve.md",
    "SC-a": HERE / "probes/SC-a.ve.md",
    "probe-translation": ROOT / "usecases/claude-constitution-pilot/run-20261104T0716Z/probe-translation.probe.md",
}


def probes(source: Path) -> None:
    sys.path.insert(0, str(ROOT / "usecases/safety-framework"))
    import measure_r2 as R
    texts = {}

    def capture(text):
        texts[len(texts)] = text
        return {}

    R.lean_document = capture
    data = source.read_bytes()
    R.judgments_probes(data)
    (HERE / "probes/JT-a.ve.md").write_bytes(texts[0])  # JT-a is the first document judgments_probes builds
    texts.clear()
    R.scope_probes(data)
    (HERE / "probes/SC-a.ve.md").write_bytes(texts[0])  # SC-a is the first document scope_probes builds


def statuses(path: Path) -> dict:
    from ve.document import check_document, load_document
    from ve.errors import CheckerUnavailable, VEError
    try:
        units = load_document(path)["units"]
        check_document(path)
    except (VEError, CheckerUnavailable) as exc:
        return {"admitted": False, "diagnostic": f"{type(exc).__name__}: {exc}"}
    return {"admitted": True, "units": {u["id"]: u["status"] for u in units}}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--probes", action="store_true")
    parser.add_argument("--source", type=Path,
                        default=Path.home() / "code/manage-agents/pilots/safety-framework/source/fsf-3.1.txt")
    parser.add_argument("--phase", choices=["before", "after"])
    parser.add_argument("--commit", default="")
    args = parser.parse_args(argv)
    if args.probes:
        probes(args.source)
    if args.phase:
        saved = json.loads(OUT.read_text()) if OUT.exists() else {}
        saved[args.phase] = {"commit": args.commit, "fixtures": {k: statuses(p) for k, p in FIXTURES.items()}}
        OUT.write_text(json.dumps(saved, indent=1, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
