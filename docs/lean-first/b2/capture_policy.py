"""Capture the agent-policy harness's actual Rust evaluation calls for rule 3.

Run in the foreground from the repository root. Forked workers inherit the recorder and
write separate files; the parent joins them after the harness has finished.
"""
from __future__ import annotations

import argparse
import importlib
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))


def capture(out: Path) -> None:
    os.environ["VE_AUTHORITY"] = "lean"
    from ve.backends import rust_jsonl
    original = rust_jsonl.run
    with tempfile.TemporaryDirectory(prefix="ve-rule3-policy-") as directory:
        shards = Path(directory)

        def recorded(case, **options):
            result = original(case, **options)
            if case.get("kind") == "evaluate-budgeted":
                line = json.dumps({"case": case, "value": result.get("value"),
                                   "status": result.get("status")}, ensure_ascii=False,
                                  separators=(",", ":")) + "\n"
                with (shards / f"{os.getpid()}.jsonl").open("a") as stream:
                    stream.write(line)
            return result

        rust_jsonl.run = recorded
        sys.path.insert(0, str(ROOT / "usecases/agent-policy"))
        module = importlib.import_module("check")
        module.main(["base"])
        with out.open("w") as stream:
            for shard in sorted(shards.glob("*.jsonl")):
                with shard.open() as source:
                    for line in source:
                        stream.write(line)
    print(f"captured {sum(1 for _ in out.open())} evaluations in {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, required=True)
    capture(parser.parse_args().out)
