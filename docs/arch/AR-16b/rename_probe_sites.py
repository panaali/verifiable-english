"""AR-16b, run once: the binding census's recorded probes (`docs/test-architecture/binding-probes.jsonl.gz`,
`tools/binding_census.py`) name each hand check by its file. The split moved `ve/readings_verdicts.py`'s code into
`ve/readings_verdicts/`, verbatim, so each probe whose `site` names `ve/readings_verdicts.py` names instead the module
of the package that holds the site's recorded line text (exactly one, or the script fails: a function name such as
`conflict` is defined by three route classes in three modules, so the text decides, not the name). A probe whose
`caller` names the old file names the module defining that function (exactly one, or the script fails). Nothing else
changes: the function, the line text, the line at the probe's commit and every other field are as recorded, and the
file is rewritten as `binding_census.collect` writes it (its sort key and `_write_gzip`). Then
`tools/binding_census.py --write`.

    python docs/arch/AR-16b/rename_probe_sites.py [--check]
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools import binding_census  # noqa: E402  (the recording's owner: its path, reader and writer)

PROBES = binding_census.PROBES
OLD = "ve/readings_verdicts.py"
PACKAGE = ROOT / "ve/readings_verdicts"


def holding(text: str) -> list[str]:
    """The package's modules holding the line `text` (stripped), each once at most."""
    out = []
    for path in sorted(PACKAGE.glob("*.py")):
        count = sum(1 for line in path.read_text().splitlines() if line.strip() == text.strip())
        if count > 1:
            raise SystemExit(f"{text!r}: {count} times in {path}")
        if count:
            out.append(path.relative_to(ROOT).as_posix())
    return out


def defining(function: str) -> list[str]:
    out = []
    for path in sorted(PACKAGE.glob("*.py")):
        if any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function
               for node in ast.walk(ast.parse(path.read_text()))):
            out.append(path.relative_to(ROOT).as_posix())
    return out


def one(found: list[str], what: str) -> str:
    if len(found) != 1:
        raise SystemExit(f"{what}: in {found}, not in exactly one module of the package")
    return found[0]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="report what would change; write nothing")
    args = parser.parse_args(argv)
    probes = binding_census.load_probes(PROBES)
    counts = {"sites": 0, "callers": 0}
    for probe in probes:
        site = probe.get("site")
        if isinstance(site, dict) and site.get("file") == OLD:
            site["file"] = one(holding(site["text"]), site["text"])
            counts["sites"] += 1
        caller = probe.get("caller")
        if isinstance(caller, str) and caller.startswith(OLD + ":"):
            function = caller.split(":", 1)[1]
            probe["caller"] = f"{one(defining(function), function)}:{function}"
            counts["callers"] += 1
    probes.sort(key=lambda p: (p["mode"], p["caller"], p["path"], p["kind"], p["test"]))  # as `collect` sorts
    print(json.dumps({"probes": len(probes), **counts}))
    if not args.check:
        binding_census._write_gzip(PROBES, [json.dumps(p, sort_keys=True, separators=(",", ":")) for p in probes])
    return 0


if __name__ == "__main__":
    sys.exit(main())
