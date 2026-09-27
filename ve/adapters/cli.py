"""File based adapter recomputation: ``ve adapter run``."""
import argparse
import json
from pathlib import Path

from ..errors import VEError
from ..wire import loads_json, require_fields
from .records import run, verify


def main(argv=None):
    parser = argparse.ArgumentParser(prog="ve adapter run")
    parser.add_argument("source", help="request JSON, or an existing record with --verify")
    parser.add_argument("--verify", action="store_true", help="recompute and check an existing record")
    args = parser.parse_args(argv)
    try:
        value = loads_json(Path(args.source).read_bytes())
        if args.verify:
            result = verify(value)
        else:
            require_fields(value, {"function", "parameters", "domain"})
            result = run(value["function"], value["parameters"], value["domain"])
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (VEError, OSError) as exc:
        print(json.dumps({"status": "InvalidInput", "error": str(exc)}))
        return 2
