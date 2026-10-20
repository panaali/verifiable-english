"""AR-16a, run once: the binding census's recorded probes (`docs/test-architecture/binding-probes.jsonl.gz`,
`tools/binding_census.py`) name each hand check by its file. The split moved `ve/document.py`'s functions into
`ve/document/`, verbatim, so each probe whose `site` or `caller` names `ve/document.py` names instead the module of
the package that now defines that function (exactly one, or the script fails). Nothing else changes: the function,
the line text, the line at the probe's commit and every other field are as recorded, and the file is rewritten as
`binding_census.collect` writes it (its sort key and `_write_gzip`). Then `tools/binding_census.py --write`.

    python docs/arch/AR-16a/rename_probe_sites.py [--check]
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
OLD = "ve/document.py"
PACKAGE = ROOT / "ve/document"


def owners() -> dict[str, list[str]]:
    """Each function or method name defined at any depth in the package, with the modules defining it."""
    out: dict[str, list[str]] = {}
    for path in sorted(PACKAGE.glob("*.py")):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                where = path.relative_to(ROOT).as_posix()
                if where not in out.setdefault(node.name, []):
                    out[node.name].append(where)
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="report what would change; write nothing")
    args = parser.parse_args(argv)
    defined = owners()

    def module(function: str) -> str:
        found = defined.get(function, [])
        if len(found) != 1:
            raise SystemExit(f"{function}: defined in {found}, not in exactly one module of the package")
        return found[0]

    probes = binding_census.load_probes(PROBES)
    counts = {"sites": 0, "callers": 0}
    for probe in probes:
        site = probe.get("site")
        if isinstance(site, dict) and site.get("file") == OLD:
            site["file"] = module(site["function"])
            counts["sites"] += 1
        caller = probe.get("caller")
        if isinstance(caller, str) and caller.startswith(OLD + ":"):
            probe["caller"] = f"{module(caller.split(':', 1)[1])}:{caller.split(':', 1)[1]}"
            counts["callers"] += 1
    probes.sort(key=lambda p: (p["mode"], p["caller"], p["path"], p["kind"], p["test"]))  # as `collect` sorts
    print(json.dumps({"probes": len(probes), **counts}))
    if not args.check:
        binding_census._write_gzip(PROBES, [json.dumps(p, sort_keys=True, separators=(",", ":")) for p in probes])
    return 0


if __name__ == "__main__":
    sys.exit(main())
