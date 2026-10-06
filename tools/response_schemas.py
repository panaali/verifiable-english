"""Write or check the client's response schemas from their one source, the Lean shapes.

    python tools/response_schemas.py --write [--decoder PATH]
    python tools/response_schemas.py --check [--decoder PATH]

`ve/backends/lean_service_schema/*.json` is generated: `ve_response_decode` renders
`ResponseShape.Schemas` (lean/ResponseShape/Schemas/, one module per file) on the line
`{"check": "schemas"}`, and this tool formats each document. The same Lean shapes decide
responses in `ve_response_decode`, with the runners' decoders and dispatch tests beside them,
so the client's schemas and the Lean side cannot drift apart. `--check` exits 1 when a file
differs from its rendering, a rendered file is missing, or the directory holds a schema file
the Lean source does not render; `--write` rewrites the directory to the rendering. The decoder
defaults to the built `lean/.lake/build/bin/ve_response_decode`.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "ve/backends/lean_service_schema"
DECODER = ROOT / "lean/.lake/build/bin/ve_response_decode"
WIDTH = 112


def rendered(decoder: Path = DECODER) -> dict[str, object]:
    """{file name: document} as the Lean source renders them."""
    done = subprocess.run([str(decoder)], input='{"check": "schemas"}\n', capture_output=True, text=True,
                          check=True)
    documents = json.loads(done.stdout)
    if not isinstance(documents, dict) or not documents:
        raise SystemExit(f"{decoder} rendered no schema: {done.stdout[:200]}")
    return documents


def _compact(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(", ", ": "))


def _format(value: object, indent: int) -> str:
    """JSON with every value that fits in WIDTH columns on one line."""
    flat = _compact(value)
    if indent + len(flat) <= WIDTH or not isinstance(value, (dict, list)) or not value:
        return flat
    inner = " " * (indent + 2)
    if isinstance(value, dict):
        items = [f"{inner}{json.dumps(k, ensure_ascii=False)}: {_format(v, indent + 2)}" for k, v in value.items()]
        return "{\n" + ",\n".join(items) + "\n" + " " * indent + "}"
    items = [inner + _format(v, indent + 2) for v in value]
    return "[\n" + ",\n".join(items) + "\n" + " " * indent + "]"


def text(document: dict) -> str:
    """A schema file: `$id`, `$comment`, the top-level schemas, then `$defs`."""
    order = ["$id", "$comment"] + sorted(k for k in document if k not in ("$id", "$comment", "$defs")) + ["$defs"]
    return _format({k: document[k] for k in order if k in document}, 0) + "\n"


def differences(documents: dict[str, object], directory: Path = DIRECTORY) -> list[str]:
    problems = []
    for name, document in sorted(documents.items()):
        path = directory / name
        if not path.is_file():
            problems.append(f"{name}: not written")
        elif path.read_text() != text(document):
            problems.append(f"{name}: differs from its rendering (edit lean/ResponseShape/Schemas, then --write)")
    problems += [f"{path.name}: not rendered by the Lean source" for path in sorted(directory.glob("*.json"))
                 if path.name not in documents]
    return problems


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true")
    action.add_argument("--check", action="store_true")
    parser.add_argument("--decoder", type=Path, default=DECODER)
    parser.add_argument("--directory", type=Path, default=DIRECTORY)
    args = parser.parse_args(argv)
    documents = rendered(args.decoder)
    if args.write:
        for path in args.directory.glob("*.json"):
            if path.name not in documents:
                path.unlink()
        for name, document in documents.items():
            (args.directory / name).write_text(text(document))
        return 0
    problems = differences(documents, args.directory)
    for problem in problems:
        print(f"response_schemas: {problem}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
