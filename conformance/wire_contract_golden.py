"""Materialize the hand-derived spec fixture records for review and drift checks."""

import argparse
import json
from pathlib import Path

from tests.test_wire_contract_lean import DEFER, DEMO
from tests.test_wire_contract_soft_lean import FIXTURES, record

ROOT = Path(__file__).resolve().parents[1] / "conformance/wire-contract"


def _decode(expected):
    return expected if expected == "clean" else json.loads(expected)


def reports():
    engine = {
        "source": "docs/spec/wire-contract.md 8.1",
        "demo@0": {name: _decode(expected) for name, (_, expected) in sorted(DEMO.items())},
        "defer@0": {name: _decode(expected) for name, (_, expected) in sorted(DEFER.items())},
        "python_deferred": {"E34": "d2", "E35": "d2", "E36": "d2"},
    }
    pilot = {name: expected for name, (_, expected) in sorted(FIXTURES.items())}
    pilot.update({
        "P1a": "clean",
        "P1b": "clean",
        "P7": record("4.14b", "rule-fields", "SOFT_INVALID_FACTORS", "InvalidInput",
                     "/norms/0/norm/exception/factors/0", "InvalidInput: invalid factors of rule a",
                     {"name": "a"}),
        "P17": {"check": "2.3", "phase": "declarations", "code": "SOFT_INVALID_INPUT",
                "class": "InvalidInput", "path": "/environment",
                "inherited_text": "language-specific"},
    })
    return {"engine-golden.json": engine,
            "soft-norms@0-golden.json": {"source": "docs/spec/wire-contract.md 8.3",
                                         "contract": "soft-norms@0", "revision": 1,
                                         "fixtures": dict(sorted(pilot.items()))}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    different = []
    for filename, body in reports().items():
        path = ROOT / filename
        rendered = json.dumps(body, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        if args.check:
            if not path.exists() or path.read_text() != rendered:
                different.append(filename)
        else:
            path.write_text(rendered)
    if different:
        print("golden reports differ: " + ", ".join(different))
    return bool(different)


if __name__ == "__main__":
    raise SystemExit(main())
